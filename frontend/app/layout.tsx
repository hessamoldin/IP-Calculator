import "./globals.css";
import type { ReactNode } from "react";
import type { Viewport } from "next";
import Nav from "@/components/Nav";

export const viewport: Viewport = { width: "device-width", initialScale: 1, viewportFit: "cover", themeColor: "#002b64" };

export const metadata = { title: "IP Calculator", description: "Subnet, VLSM and IP tools" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Nav />
        <main>{children}</main>
      </body>
    </html>
  );
}
