import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "TrueValue.ae — Dubai Property Due Diligence",
  description:
    "Institutional-grade property due diligence for Dubai real estate. AI-powered analysis covering 15+ zones, 12 tools, and scored verdicts — delivered via Telegram.",
  keywords: [
    "Dubai real estate",
    "property due diligence",
    "AI property analysis",
    "Dubai investment",
    "TrueValue.ae",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
