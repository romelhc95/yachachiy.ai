"use client";

import Link from "next/link";

export function Footer() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    } else {
      window.location.href = `/#${id}`;
    }
  };

  return (
    <footer className="border-t border-brand-gray/50 py-20 mt-12">
      <div className="mx-auto max-w-6xl px-6">
        <div className="flex flex-col md:flex-row justify-between items-start gap-12">
          <div className="max-w-xs space-y-6">
            <div className="text-2xl font-bold flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-brand-blue flex items-center justify-center text-white text-sm">Y</div>
              <span className="text-brand-slate">Yachachiy<span className="text-brand-blue">.ai</span></span>
            </div>
            <p className="text-slate-500 font-medium leading-relaxed">Decisiones educativas inteligentes basadas en datos reales para los profesionales del futuro en el Perú.</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-16">
            <div className="space-y-6">
              <p className="text-xs font-black uppercase tracking-[0.2em] text-slate-400">Plataforma</p>
              <ul className="space-y-4 font-bold text-sm text-slate-600">
                <li><button onClick={() => scrollToSection('programas')} className="hover:text-brand-blue transition">Explorar</button></li>
                <li><button onClick={() => scrollToSection('como-funciona')} className="hover:text-brand-blue transition">Cómo Funciona</button></li>
                <li><button onClick={() => scrollToSection('nosotros')} className="hover:text-brand-blue transition">Sobre nosotros</button></li>
              </ul>
            </div>
            <div className="space-y-6">
              <p className="text-xs font-black uppercase tracking-[0.2em] text-slate-400">Legal</p>
              <ul className="space-y-4 font-bold text-sm text-slate-600">
                <li><Link href="#" className="hover:text-brand-blue transition">Privacidad</Link></li>
                <li><Link href="#" className="hover:text-brand-blue transition">Términos</Link></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-20 pt-8 border-t border-brand-gray/30 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-bold text-slate-400 uppercase tracking-widest">
          <span>© 2026 Yachachiy.ai · Data-driven education</span>
          <div className="flex gap-6">
            <Link href="#" className="hover:text-brand-blue transition">LinkedIn</Link>
            <Link href="#" className="hover:text-brand-blue transition">Twitter</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
