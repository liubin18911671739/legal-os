import type { Metadata } from "next";
import "./globals.css";
import { Layout as AppLayout } from "@/components/layout";

export const metadata: Metadata = {
  title: "LegalOS - 企业法律智能分析系统",
  description: "基于多智能体 RAG 的合同审查与法律合规分析平台",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body className="font-sans antialiased">
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
