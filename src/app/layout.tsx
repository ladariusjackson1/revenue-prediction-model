import type { Metadata } from "next";
import { DM_Sans, Fraunces } from "next/font/google";
import "./globals.css";

const sans = DM_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
});

const display = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Top 500 Revenue Model",
  description:
    "Dashboard for U.S. top 500 company revenues (Fortune 500 2025 / FY2024).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${sans.variable} ${display.variable} font-[family-name:var(--font-sans)] antialiased`}>
        {children}
      </body>
    </html>
  );
}
