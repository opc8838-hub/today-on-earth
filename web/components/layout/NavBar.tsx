"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Globe } from "lucide-react";
import { SITE, NAV_LINKS } from "@/lib/constants";

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-nav border-b border-earth-700">
      <div className="max-w-8xl mx-auto px-6 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <Globe className="w-5 h-5 text-earth-blue transition-colors group-hover:text-earth-100" />
          <span className="text-sm font-medium tracking-widest text-earth-100 uppercase">
            {SITE.name}
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-8">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`text-xs tracking-widest uppercase transition-colors ${
                  isActive
                    ? "text-earth-blue"
                    : "text-earth-300 hover:text-earth-100"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
