"use client";

import { useEffect, useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Clock, TrendingUp, ChevronDown, X, GraduationCap, ArrowRight } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { SUPABASE_URL, SUPABASE_ANON_KEY, cleanSlug, parseDurationToMonths, type Course, type Institution } from "@/lib/supabase";

/**
 * Yachachiy.ai - Home Page
 * 
 * Plataforma para comparar programas educativos en el Perú usando datos reales.
 * Utiliza una arquitectura Serverless con Supabase y Cloudflare Pages.
 */
export default function Home() {
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const [activeFilters, setActiveFilters] = useState({
    priceMin: "",
    priceMax: "",
    modes: [] as string[],
    durations: [] as string[],
    types: [] as string[],
    includeConsultar: true
  });

  // Carga inicial de datos desde Supabase PostgREST
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const headers = {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        };

        // Fetch Courses
        const courseRes = await fetch(`${SUPABASE_URL}/rest/v1/courses?select=*&order=created_at.desc`, { headers });
        const courseData = await courseRes.json();
        
        // Fetch Institutions
        const instRes = await fetch(`${SUPABASE_URL}/rest/v1/institutions?select=*`, { headers });
        const instData = await instRes.json();

        if (Array.isArray(courseData)) setAllCourses(courseData);
        if (Array.isArray(instData)) setInstitutions(instData);
      } catch (error) {
        console.error("Error cargando datos de Yachachiy:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Filtrado reactivo en el cliente para mayor velocidad
  const filteredCourses = useMemo(() => {
    let result = [...allCourses];

    // Búsqueda por texto
    if (searchTerm) {
      result = result.filter(c => 
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
        c.institution_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filtros activos
    return result.filter((course) => {
      if (activeFilters.modes.length > 0 && !activeFilters.modes.includes(course.mode)) return false;
      if (activeFilters.types.length > 0 && !activeFilters.types.includes(course.category)) return false;
      
      if (activeFilters.durations.length > 0) {
        const months = parseDurationToMonths(course.duration);
        const matches = activeFilters.durations.some(range => {
          if (range === "<6") return months > 0 && months < 6;
          if (range === "6-12") return months >= 6 && months <= 12;
          if (range === ">12") return months > 12;
          return false;
        });
        if (!matches) return false;
      }

      const price = course.price_pen;
      if (price === null) {
        if ((activeFilters.priceMin || activeFilters.priceMax) && !activeFilters.includeConsultar) return false;
      } else {
        if (activeFilters.priceMin && price < parseFloat(activeFilters.priceMin)) return false;
        if (activeFilters.priceMax && price > parseFloat(activeFilters.priceMax)) return false;
      }
      return true;
    });
  }, [allCourses, activeFilters, searchTerm]);

  return (
    <div className="min-h-screen bg-white dark:bg-brand-slate text-brand-slate dark:text-white font-sans selection:bg-brand-mint/30">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-brand-gray/50 bg-white/95 dark:bg-brand-slate/95 backdrop-blur shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2 text-2xl font-bold tracking-tight text-brand-slate dark:text-white">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-blue text-white font-bold">Y</div>
            <span>Yachachiy<span className="text-brand-blue">.ai</span></span>
          </Link>
          <nav className="hidden md:flex gap-8 items-center">
            <Link href="/" className="text-sm font-medium text-brand-blue">Inicio</Link>
            <button onClick={() => document.getElementById('como-funciona')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Cómo Funciona</button>
            <button onClick={() => document.getElementById('programas')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Programas</button>
            <Button onClick={() => setIsModalOpen(true)} size="sm" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-semibold rounded-xl px-5 h-9 border-0">Asesoría Gratis</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-brand-slate to-brand-blue p-10 md:p-16 text-white shadow-premium">
          <div className="relative z-10">
            <p className="mb-4 text-sm font-bold uppercase tracking-[0.24em] text-brand-mint">Yachachiy · Democratizando la Educación</p>
            <h1 className="max-w-3xl text-4xl font-bold leading-tight md:text-6xl">Tu futuro profesional, <span className="text-brand-mint">decidido con datos.</span></h1>
            <p className="mt-6 max-w-2xl text-lg text-blue-100/90 leading-relaxed">
              Consolidamos la oferta educativa tech del Perú. Compara ROI, precios y mallas curriculares en un solo lugar.
            </p>
            <div className="mt-10 flex flex-wrap gap-4 items-center">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input 
                  placeholder="¿Qué quieres estudiar? (Ej: Data Science, MBA)" 
                  className="pl-12 h-14 bg-white text-brand-slate rounded-2xl border-0 focus:ring-brand-mint"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button onClick={() => document.getElementById('programas')?.scrollIntoView({ behavior: 'smooth' })} size="lg" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold rounded-2xl px-8 h-14 shadow-lg shadow-brand-mint/20 border-0">Buscar</Button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main id="programas" className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Explora Programas</h2>
            <p className="text-slate-500 text-sm mt-1">Mostrando {filteredCourses.length} opciones encontradas en tiempo real.</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-zinc-800 p-1 rounded-xl self-start md:self-center">
            <Button size="sm" variant="ghost" className={cn("h-8 text-xs font-bold rounded-lg transition-all", viewMode === 'grid' ? "bg-white shadow-sm" : "text-slate-500")} onClick={() => setViewMode('grid')}>Mosaico</Button>
            <Button size="sm" variant="ghost" className={cn("h-8 text-xs font-bold rounded-lg transition-all", viewMode === 'list' ? "bg-white shadow-sm" : "text-slate-500")} onClick={() => setViewMode('list')}>Lista</Button>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
            {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-64 bg-slate-100 dark:bg-zinc-900 rounded-3xl" />)}
          </div>
        ) : filteredCourses.length > 0 ? (
          <div className={cn("grid gap-6", viewMode === 'grid' ? "md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1")}>
            {filteredCourses.map((course) => (
              <article key={course.id} className={cn("group flex flex-col justify-between rounded-3xl border border-brand-gray/50 bg-white dark:bg-zinc-900/40 p-7 shadow-premium transition-all hover:border-brand-blue/40 hover:shadow-xl", viewMode === 'list' && "md:flex-row md:items-center gap-8")}>
                <div className={cn(viewMode === 'list' ? "flex-1" : "")}>
                  <div className="flex items-center gap-2 mb-4">
                    <Badge variant="secondary" className="bg-brand-blue/10 text-brand-blue font-bold border-0 px-3">{course.category || "General"}</Badge>
                    <Badge variant="outline" className="border-brand-gray/50 text-slate-400 text-[10px] font-bold uppercase">{course.mode}</Badge>
                  </div>
                  <Link href={`/courses/${cleanSlug(course.slug)}`}>
                    <h3 className="text-xl font-bold group-hover:text-brand-blue transition-colors leading-tight mb-2">{course.name}</h3>
                  </Link>
                  <p className="text-sm text-slate-500 flex items-center gap-1.5"><GraduationCap className="h-4 w-4" /> {course.institution_name}</p>
                  <div className="mt-8 flex gap-8">
                    <div className="flex flex-col"><span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Duración</span><span className="font-semibold text-sm">{course.duration || "Consultar"}</span></div>
                    <div className="flex flex-col"><span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Inversión</span><span className="font-bold text-brand-blue text-sm">{course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}</span></div>
                  </div>
                </div>
                <div className={cn("mt-8 flex gap-3", viewMode === 'list' ? "md:flex-col md:w-48 mt-0" : "")}>
                  <Link href={`/courses/${cleanSlug(course.slug)}`} className="flex-1 rounded-xl border border-brand-blue/30 px-4 py-3 text-center text-sm font-bold text-brand-blue hover:bg-brand-blue hover:text-white transition-all shadow-sm">Ver detalle</Link>
                  <Button onClick={() => setIsModalOpen(true)} className="flex-1 rounded-xl bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold h-11 border-0">Quiero info</Button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="py-20 text-center border-2 border-dashed border-brand-gray/30 rounded-3xl">
            <h3 className="text-xl font-bold mb-2">No encontramos programas con esos filtros</h3>
            <p className="text-slate-500 mb-6">Prueba ajustando tu búsqueda o filtros.</p>
            <Button variant="outline" onClick={() => { setSearchTerm(""); setActiveFilters({ priceMin: "", priceMax: "", modes: [], durations: [], types: [], includeConsultar: true }); }} className="rounded-xl">Limpiar búsqueda</Button>
          </div>
        )}
      </main>

      {/* Footer y Modals permanecen similares, pero limpios */}
      <footer className="bg-slate-50 dark:bg-brand-slate border-t border-brand-gray/30 py-16 text-center">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-2xl font-bold mb-4">Yachachiy<span className="text-brand-blue">.ai</span></div>
          <p className="text-slate-500 text-sm font-bold max-w-xs mx-auto mb-8">Decisiones educativas inteligentes basadas en datos reales para profesionales del futuro.</p>
          <div className="flex justify-center gap-6 mb-8 text-sm font-bold">
            <Link href="#" className="hover:text-brand-blue transition">Sobre nosotros</Link>
            <Link href="#" className="hover:text-brand-blue transition">Instituciones</Link>
            <Link href="#" className="hover:text-brand-blue transition">Blog</Link>
            <Link href="#" className="hover:text-brand-blue transition">Contacto</Link>
          </div>
          <div className="text-[11px] text-slate-400 font-bold uppercase tracking-widest">© 2026 Yachachiy.ai - Hecho con ❤️ en Perú</div>
        </div>
      </footer>

      {/* Modal Form */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-brand-slate/70 backdrop-blur-md animate-in fade-in duration-300">
          <div className="bg-white dark:bg-zinc-900 w-full max-w-md rounded-[2.5rem] shadow-2xl overflow-hidden p-10 relative">
            <button onClick={() => setIsModalOpen(false)} className="absolute top-6 right-6 p-2 hover:bg-slate-100 dark:hover:bg-zinc-800 rounded-full transition"><X className="h-5 w-5" /></button>
            <h3 className="text-3xl font-bold mb-3 text-brand-slate dark:text-white">Asesoría Directa</h3>
            <p className="text-sm text-slate-500 mb-8 leading-relaxed">Deja tus datos y un experto en educación te ayudará a encontrar el programa que mejor se ajuste a tu perfil y presupuesto.</p>
            <div className="space-y-4 mb-8">
              <Input placeholder="Tu nombre completo" className="h-14 rounded-2xl bg-slate-50 dark:bg-zinc-800 border-0 focus:ring-2 focus:ring-brand-mint" />
              <Input placeholder="WhatsApp (+51 900 000 000)" className="h-14 rounded-2xl bg-slate-50 dark:bg-zinc-800 border-0 focus:ring-2 focus:ring-brand-mint" />
            </div>
            <Button className="w-full h-14 bg-brand-blue hover:bg-brand-blue/90 text-white font-bold rounded-2xl border-0 shadow-xl shadow-brand-blue/10" onClick={() => setIsModalOpen(false)}>Quiero hablar con un asesor</Button>
            <p className="text-[10px] text-center text-slate-400 mt-6 uppercase font-bold tracking-tighter">Sin compromiso · Privacidad garantizada</p>
          </div>
        </div>
      )}
    </div>
  );
}
