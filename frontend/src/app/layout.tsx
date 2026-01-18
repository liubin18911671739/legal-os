import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Layout as AppLayout } from "@/components/layout";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LegalOS - Enterprise Legal Intelligence",
  description: "Multi-agent RAG system for contract analysis and legal review",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppLayout>{children}</AppLayout>
      </body>
    </html>
  );
}
