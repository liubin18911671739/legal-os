"""
Load testing script for LegalOS API using Locust

Run with:
    locust -f load_test.py --host=http://localhost:8000
"""
import json
import time
import random
from typing import Dict, Any
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner


SAMPLE_CONTRACT = """
劳动合同

甲方：北京科技有限公司
乙方：张三

第一条 合同期限
本合同期限为三年，自2024年1月1日起至2027年1月1日止。

第二条 工作内容
乙方担任软件工程师岗位，负责系统开发和维护工作。

第三条 劳动报酬
乙方的月工资为10000元，甲方于每月15日支付上月工资。

第四条 保密义务
乙方应当保守甲方的商业秘密和技术秘密，不得泄露给第三方。

第五条 违约责任
任何一方违反本合同约定，应向对方支付5000元违约金。
"""


class LegalOSUser(HttpUser):
    """User that simulates interactions with LegalOS API"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.username = f"user_{random.randint(1000, 9999)}"
        self.contract_id = None
        self.task_id = None
    
    @task(3)
    def health_check(self):
        """Check API health"""
        self.client.get("/health")
    
    @task(2)
    def get_documents(self):
        """Get list of documents"""
        self.client.get("/api/v1/documents/")
    
    @task(1)
    def upload_document(self):
        """Upload a new document"""
        response = self.client.post(
            "/api/v1/documents/",
            json={
                "title": f"Contract {random.randint(1, 1000)}",
                "file_name": f"contract_{random.randint(1, 1000)}.pdf",
                "file_type": "pdf",
                "file_size": "1.5 MB"
            }
        )
        if response.status_code == 201:
            data = response.json()
            self.contract_id = data.get("id")
    
    @task(5)
    def analyze_contract(self):
        """Analyze a contract"""
        if not self.contract_id:
            # Create a document first
            self.upload_document()
        
        if self.contract_id:
            response = self.client.post(
                "/api/v1/contracts/analyze",
                json={
                    "contract_id": self.contract_id,
                    "contract_text": SAMPLE_CONTRACT,
                    "contract_type": random.choice([
                        "employment", "sales", "lease", "service", "purchase"
                    ]),
                    "user_query": "Analyze this contract for risks"
                }
            )
            if response.status_code == 202:
                data = response.json()
                self.task_id = data.get("task_id")
    
    @task(3)
    def get_task_status(self):
        """Get task status"""
        if self.task_id:
            self.client.get(f"/api/v1/contracts/tasks/{self.task_id}")
    
    @task(2)
    def get_analysis_result(self):
        """Get analysis result"""
        if self.task_id:
            self.client.get(f"/api/v1/contracts/analysis/{self.task_id}")
    
    @task(2)
    def search_knowledge(self):
        """Search knowledge base"""
        self.client.get(
            "/api/v1/knowledge/search",
            params={
                "query": random.choice([
                    "employment contract",
                    "sales agreement",
                    "lease terms",
                    "service level agreement"
                ]),
                "top_k": 5
            }
        )
    
    @task(1)
    def get_evaluation_info(self):
        """Get evaluation dataset info"""
        self.client.get("/api/v1/evaluation/dataset/info")
    
    @task(1)
    def get_evaluation_contracts(self):
        """Get evaluation contracts"""
        self.client.get("/api/v1/evaluation/dataset/contracts")


class PerformanceMetrics:
    """Custom performance metrics tracking"""
    
    def __init__(self):
        self.requests = 0
        self.failures = 0
        self.response_times = []
        self.start_time = time.time()
    
    def record_request(self, response_time: float, success: bool):
        """Record a request"""
        self.requests += 1
        if not success:
            self.failures += 1
        self.response_times.append(response_time)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.response_times:
            return {}
        
        sorted_times = sorted(self.response_times)
        total_time = time.time() - self.start_time
        rps = self.requests / total_time if total_time > 0 else 0
        
        return {
            "total_requests": self.requests,
            "requests_per_second": rps,
            "failures": self.failures,
            "failure_rate": self.failures / self.requests if self.requests > 0 else 0,
            "avg_response_time": sum(self.response_times) / len(self.response_times),
            "median_response_time": sorted_times[len(sorted_times) // 2],
            "p95_response_time": sorted_times[int(len(sorted_times) * 0.95)],
            "p99_response_time": sorted_times[int(len(sorted_times) * 0.99)],
        }


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops"""
    if isinstance(environment.runner, MasterRunner):
        return
    
    print("\n" + "="*50)
    print("Load Test Results")
    print("="*50)
    
    stats = {
        "total_requests": environment.stats.total.num_requests,
        "failures": environment.stats.total.num_failures,
        "rps": environment.stats.total.current_rps,
        "avg_response_time": environment.stats.total.avg_response_time,
        "median_response_time": environment.stats.total.median_response_time,
    }
    
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Failures: {stats['failures']}")
    print(f"Requests/Second: {stats['rps']:.2f}")
    print(f"Avg Response Time: {stats['avg_response_time']:.2f}ms")
    print(f"Median Response Time: {stats['median_response_time']:.2f}ms")
    print("="*50 + "\n")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python load_test.py <number_of_users> <spawn_rate>")
        print("Example: python load_test.py 50 5")
        sys.exit(1)
    
    num_users = int(sys.argv[1])
    spawn_rate = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"Starting load test with {num_users} users at {spawn_rate} users/second")
    print("Press Ctrl+C to stop the test")
    
    import subprocess
    subprocess.run([
        "locust",
        "-f", __file__,
        "--host", "http://localhost:8000",
        "--users", str(num_users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", "5m",
        "--headless",
        "--html", "load_test_report.html"
    ])
