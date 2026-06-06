import type { Metadata } from "next";
import Link from "next/link";

import { Providers } from "@/components/providers";
import { ThemeToggle } from "@/components/theme-toggle";

import "./globals.css";

export const metadata: Metadata = {
  title: "VPE-1.0 Try-on Studio",
  description: "Frontend-only virtual try-on studio for VPE-1.0",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-background focus:px-3 focus:py-2 focus:text-sm focus:ring-2 focus:ring-ring"
          >
            Skip to content
          </a>
          <header className="border-b bg-background/95">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
              <Link href="/" className="text-lg font-semibold tracking-normal">
                VPE-1.0
              </Link>
              <div className="flex items-center gap-2">
                <nav aria-label="Main navigation" className="flex items-center gap-3 text-sm sm:gap-4">
                  <Link
                    className="rounded-sm text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    href="/"
                  >
                    Studio
                  </Link>
                  <Link
                    className="rounded-sm text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    href="/history"
                  >
                    History
                  </Link>
                  <Link
                    className="rounded-sm text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    href="/health"
                  >
                    Health
                  </Link>
                </nav>
                <ThemeToggle />
              </div>
            </div>
          </header>
          <main id="main-content" className="mx-auto min-h-[calc(100vh-4rem)] max-w-7xl px-4 py-6 sm:px-6">
            {children}
          </main>
        </Providers>
      </body>
    </html>
  );
}
