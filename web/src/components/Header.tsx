"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";

export function Header() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    } else {
      // Si no estamos en home, redirigir a home con el hash
      window.location.href = `/#${id}`;
    }
  };

  return (
    <header className="sticky top-0 z-50 border-b border-brand-gray/50 bg-white/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2 text-2xl font-bold tracking-tight" onClick={() => window.location.href='/'}>
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-blue text-white shadow-lg shadow-brand-blue/20">
            <span className="text-xl">Y</span>
          </div>
          <span className="text-brand-slate">Yachachiy<span className="text-brand-blue">.ai</span></span>
        </Link>
        <nav className="hidden md:flex gap-10 items-center">
          <button onClick={() => scrollToSection('programas')} className="text-sm font-semibold text-slate-600 hover:text-brand-blue transition">Programas</button>
          <button onClick={() => scrollToSection('como-funciona')} className="text-sm font-semibold text-slate-600 hover:text-brand-blue transition">Cómo Funciona</button>
          <button onClick={() => scrollToSection('nosotros')} className="text-sm font-semibold text-slate-600 hover:text-brand-blue transition">Nosotros</button>
        </nav>
      </div>
    </header>
  );
}
