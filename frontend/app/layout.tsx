import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "IsometricMTO — AI-Powered Material Take-Off Generator",
  description:
    "Upload a piping isometric drawing and let Gemini AI extract a complete, engineer-validated Material Take-Off (MTO) in seconds. Export to CSV for ERP import.",
  keywords: ["piping", "isometric", "MTO", "material take-off", "AI", "Gemini"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
