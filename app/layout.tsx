import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "VPE-1.0 Try-on Studio",
  description: "Frontend-only virtual try-on studio for VPE-1.0",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <header className="border-b bg-background/95">
          <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
            <Link href="/" className="text-lg font-semibold tracking-normal">
              VPE-1.0
            </Link>
            <nav aria-label="Main navigation" className="flex items-center gap-4 text-sm">
              <Link className="text-muted-foreground hover:text-foreground" href="/">
                Studio
              </Link>
              <Link className="text-muted-foreground hover:text-foreground" href="/history">
                History
              </Link>
              <Link className="text-muted-foreground hover:text-foreground" href="/health">
                Health
              </Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto min-h-[calc(100vh-4rem)] max-w-7xl px-4 py-6 sm:px-6">
          {children}
        </main>
      </body>
    </html>
  );
}
