"""
Baseline Experiments Module

This module implements baseline experiments for comparing different approaches.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import logging
from app.evaluation.metrics import EvaluationResult, GroundTruthAnnotation, RiskPoint, EvaluationMetrics

logger = logging.getLogger(__name__)


class BaselineType(Enum):
    """Types of baseline experiments"""
    NO_RAG = "no_rag"  # Direct LLM analysis
    SIMPLE_RAG = "simple_rag"  # Vector-only RAG
    MULTI_AGENT_RAG = "multi_agent_rag"  # Full multi-agent system


@dataclass
class ExperimentConfig:
    """Configuration for a baseline experiment"""
    baseline_type: BaselineType
    model_name: str
    temperature: float
    max_tokens: int
    top_p: float
    retrieval_config: Optional[Dict[str, Any]] = None


@dataclass
class ExperimentResult:
    """Result of a single experiment run"""
    baseline_type: BaselineType
    contract_id: str
    model_name: str
    duration: float
    token_usage: int
    cost: float
    prediction: Dict[str, Any]
    metrics: Dict[str, float]
    error: Optional[str] = None


class BaselineExperiments:
    """Run baseline experiments for contract analysis"""

    def __init__(self, llm_client, vector_store=None):
        """
        Initialize baseline experiments.

        Args:
            llm_client: LLM client for making predictions
            vector_store: Optional vector store for RAG baselines
        """
        self.llm_client = llm_client
        self.vector_store = vector_store

    async def run_no_rag_baseline(
        self,
        contract_text: str,
        user_query: str,
        config: ExperimentConfig
    ) -> ExperimentResult:
        """
        Run baseline v1: Direct LLM analysis without RAG

        Args:
            contract_text: Contract text to analyze
            user_query: User query/question
            config: Experiment configuration

        Returns:
            Experiment result
        """
        start_time = time.time()
        contract_id = f"baseline-no-rag-{int(start_time)}"

        try:
            # Construct prompt for direct analysis
            prompt = self._construct_no_rag_prompt(contract_text, user_query)

            # Call LLM
            response = await self.llm_client.generate(
                prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

            duration = time.time() - start_time

            # Parse response (simplified)
            prediction = self._parse_llm_response(response)

            # Calculate metrics (placeholder)
            metrics = {
                'duration': duration,
                'token_usage': getattr(response, 'usage', {}).get('total_tokens', 0),
                'cost': self._estimate_cost(getattr(response, 'usage', {}))
            }

            return ExperimentResult(
                baseline_type=config.baseline_type,
                contract_id=contract_id,
                model_name=config.model_name,
                duration=duration,
                token_usage=metrics['token_usage'],
                cost=metrics['cost'],
                prediction=prediction,
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"No RAG baseline failed: {e}", exc_info=True)
            return ExperimentResult(
                baseline_type=config.baseline_type,
                contract_id=contract_id,
                model_name=config.model_name,
                duration=time.time() - start_time,
                token_usage=0,
                cost=0.0,
                prediction={},
                metrics={},
                error=str(e)
            )

    async def run_simple_rag_baseline(
        self,
        contract_text: str,
        user_query: str,
        config: ExperimentConfig
    ) -> ExperimentResult:
        """
        Run baseline v2: Vector-only RAG (no hybrid retrieval, no multi-agent)

        Args:
            contract_text: Contract text to analyze
            user_query: User query/question
            config: Experiment configuration

        Returns:
            Experiment result
        """
        start_time = time.time()
        contract_id = f"baseline-simple-rag-{int(start_time)}"

        try:
            # Retrieve relevant context using vector search only
            retrieved_docs = []
            if self.vector_store:
                # Simple vector search (no BM25, no reranking)
                retrieved_docs = await self._simple_vector_search(contract_text, user_query)

            # Construct prompt with retrieved context
            prompt = self._construct_simple_rag_prompt(contract_text, user_query, retrieved_docs)

            # Call LLM
            response = await self.llm_client.generate(
                prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )

            duration = time.time() - start_time

            # Parse response
            prediction = self._parse_llm_response(response)
            prediction['retrieved_context'] = retrieved_docs

            # Calculate metrics
            metrics = {
                'duration': duration,
                'retrieval_count': len(retrieved_docs),
                'token_usage': getattr(response, 'usage', {}).get('total_tokens', 0),
                'cost': self._estimate_cost(getattr(response, 'usage', {}))
            }

            return ExperimentResult(
                baseline_type=config.baseline_type,
                contract_id=contract_id,
                model_name=config.model_name,
                duration=duration,
                token_usage=metrics['token_usage'],
                cost=metrics['cost'],
                prediction=prediction,
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Simple RAG baseline failed: {e}", exc_info=True)
            return ExperimentResult(
                baseline_type=config.baseline_type,
                contract_id=contract_id,
                model_name=config.model_name,
                duration=time.time() - start_time,
                token_usage=0,
                cost=0.0,
                prediction={},
                metrics={},
                error=str(e)
            )

    async def run_multi_agent_baseline(
        self,
        contract_text: str,
        contract_type: str,
        user_query: str,
        config: ExperimentConfig
    ) -> ExperimentResult:
        """
        Run full multi-agent RAG baseline (current system)

        Args:
            contract_text: Contract text to analyze
            contract_type: Type of contract
            user_query: User query/question
            config: Experiment configuration

        Returns:
            Experiment result
        """
        start_time = time.time()
        contract_id = f"baseline-multi-agent-{int(start_time)}"

        try:
            # Import the actual contract analysis workflow
            from app.agents import create_contract_analysis_graph, create_initial_state, ContractType
            from app.api.v1.contracts import generate_task_id

            # Create workflow graph
            graph = create_contract_analysis_graph()

            # Initialize state
            state = create_initial_state(
                contract_id=contract_id,
                contract_text=contract_text,
                contract_type=ContractType(contract_type),
                user_query=user_query
            )

            # Execute workflow
            result = await graph.ainvoke(state)

            duration = time.time() - start_time

            # Extract prediction from result
            prediction = {
                'final_answer': result.get('final_answer', ''),
                'agent_history': [str(agent) for agent in result.get('agent_history', [])],
                'analysis_confidence': result.get('analysis_confidence', 0.0),
                'validation_confidence': result.get('validation_result', {}).get('overall_confidence', 0.0),
                'report': result.get('report'),
                'findings': result.get('report', {}).get('findings', []),
            }

            # Calculate metrics
            metrics = {
                'duration': duration,
                'agent_count': len(result.get('agent_history', [])),
                'token_usage': result.get('token_usage', 0),
                'cost': result.get('cost', 0.0),
                'analysis_confidence': prediction['analysis_confidence'],
                'validation_confidence': prediction['validation_confidence'],
            }

            return ExperimentResult(
                baseline_type=config.baseline_type,
                contract_id=contract_id,
                model_name=config.model_name,
                duration=duration,
                token_usage=metrics['token_usage'],
                cost=metrics['cost'],
                prediction=prediction,
                metrics=metrics
            )

        except Exception as e:
            logger.error(f"Multi-agent baseline failed: {e}", exc_info=True)
            return ExperimentResult(
                baseline_type=config.baseline_type,
                contract_id=contract_id,
                model_name=config.model_name,
                duration=time.time() - start_time,
                token_usage=0,
                cost=0.0,
                prediction={},
                metrics={},
                error=str(e)
            )

    def _construct_no_rag_prompt(self, contract_text: str, user_query: str) -> str:
        """Construct prompt for no-RAG baseline"""
        return f"""You are a legal contract analyst. Please analyze the following contract.

Contract Text:
{contract_text}

{user_query}

Please provide:
1. Overall risk assessment (low/medium/high)
2. Key issues or concerns
3. Compliance issues
4. Suggestions for improvement

Format your response in JSON structure with 'overall_risk', 'findings', and 'suggestions' fields.
"""

    def _construct_simple_rag_prompt(
        self,
        contract_text: str,
        user_query: str,
        retrieved_docs: List[str]
    ) -> str:
        """Construct prompt for simple RAG baseline"""
        context = "\n\n".join(retrieved_docs[:5]) if retrieved_docs else "No relevant context found."

        return f"""You are a legal contract analyst. Please analyze the following contract using the provided context.

Contract Text:
{contract_text}

Relevant Context:
{context}

{user_query}

Please provide:
1. Overall risk assessment (low/medium/high)
2. Key issues or concerns
3. Compliance issues
4. Suggestions for improvement

Format your response in JSON structure with 'overall_risk', 'findings', and 'suggestions' fields.
"""

    async def _simple_vector_search(
        self,
        contract_text: str,
        query: str
    ) -> List[str]:
        """Simple vector search without BM25 or reranking"""
        # This is a placeholder - actual implementation would use vector store
        # For now, return empty list
        return []

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response (simplified)"""
        # Try to parse as JSON
        import json
        try:
            # Extract JSON from response if embedded in text
            if '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return {'final_answer': response}
        except json.JSONDecodeError:
            return {'final_answer': response}

    def _estimate_cost(self, usage: Dict[str, int]) -> float:
        """Estimate cost based on token usage"""
        # Simplified cost calculation
        total_tokens = usage.get('total_tokens', 0)
        return total_tokens * 0.00002  # $0.02 per 1K tokens

    async def run_all_baselines(
        self,
        contract_text: str,
        contract_type: str,
        user_query: str,
        configs: List[ExperimentConfig]
    ) -> List[ExperimentResult]:
        """
        Run all baseline experiments

        Args:
            contract_text: Contract text to analyze
            contract_type: Type of contract
            user_query: User query/question
            configs: List of experiment configurations

        Returns:
            List of experiment results
        """
        results = []

        for config in configs:
            if config.baseline_type == BaselineType.NO_RAG:
                result = await self.run_no_rag_baseline(contract_text, user_query, config)
            elif config.baseline_type == BaselineType.SIMPLE_RAG:
                result = await self.run_simple_rag_baseline(contract_text, user_query, config)
            elif config.baseline_type == BaselineType.MULTI_AGENT_RAG:
                result = await self.run_multi_agent_baseline(contract_text, contract_type, user_query, config)
            else:
                logger.warning(f"Unknown baseline type: {config.baseline_type}")
                continue

            results.append(result)

        return results
