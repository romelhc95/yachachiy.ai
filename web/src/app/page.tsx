"use client";

import { useEffect, useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Clock, TrendingUp, CheckCircle2, ChevronDown, X, GraduationCap, Briefcase, DollarSign, ArrowRight, MapPin } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface Course {
  id: string;
  name: string;
  slug: string;
  institution_name: string;
  price_pen: number | null;
  mode: string;
  address: string;
  duration: string;
  category: string;
  url: string;
  distance_km?: number | null;
  roi_months?: number | null;
  expected_monthly_salary?: number;
}

interface Institution {
  id: string;
  name: string;
  slug: string;
  website_url: string;
}

// FUNCIÓN DE NORMALIZACIÓN ÚNICA
const cleanSlug = (slug: string) => {
  if (!slug) return "";
  return slug
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
};

function parseDurationToMonths(duration: string | null): number {
  if (!duration) return 0;
  const match = duration.match(/(\d+)\s*(mes|semana|año|month|week|year)s?/i);
  if (!match) return 0;
  const value = parseInt(match[1]);
  const unit = match[2].toLowerCase();
  if (unit.startsWith('mes') || unit.startsWith('month')) return value;
  if (unit.startsWith('semana') || unit.startsWith('week')) return value / 4.33;
  if (unit.startsWith('año') || unit.startsWith('year')) return value * 12;
  return 0;
}

export default function Home() {
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedForCompare, setSelectedForCompare] = useState<Course[]>([]);
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

  const SUPABASE_URL = 'https://fmcxwoqvxatbrawwtqke.supabase.co';
  const SUPABASE_ANON_KEY = 'sb_publishable_rTQDiEIQYGn0q5VgCdEZlA__F8fDp0E';

  const fetchCourses = async (search = "") => {
    setLoading(true);
    try {
      const url = search 
        ? `${SUPABASE_URL}/rest/v1/courses?name=ilike.*${encodeURIComponent(search)}*&select=*`
        : `${SUPABASE_URL}/rest/v1/courses?select=*`;
      
      const response = await fetch(url, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        }
      });
      const data = await response.json();
      setAllCourses(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching courses:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInstitutions = async () => {
    try {
      const response = await fetch(`${SUPABASE_URL}/rest/v1/institutions?select=*`, {
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
        }
      });
      const data = await response.json();
      setInstitutions(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error fetching institutions:", error);
    }
  };

  useEffect(() => {
    fetchCourses();
    fetchInstitutions();
  }, []);

  const filteredCourses = useMemo(() => {
    const coursesToFilter = Array.isArray(allCourses) ? allCourses : [];
    return coursesToFilter.filter((course) => {
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
  }, [allCourses, activeFilters]);

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
            <button onClick={() => document.getElementById('nosotros')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Nosotros</button>
            <button onClick={() => document.getElementById('instituciones')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Instituciones</button>
            <Button onClick={() => setIsModalOpen(true)} size="sm" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-semibold rounded-xl px-5 h-9 border-0">Solicitar asesoría</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-brand-slate to-brand-blue p-10 md:p-16 text-white shadow-premium">
          <div className="relative z-10">
            <p className="mb-4 text-sm font-bold uppercase tracking-[0.24em] text-brand-mint">Yachachiy · Data-driven education</p>
            <h1 className="max-w-3xl text-4xl font-bold leading-tight md:text-6xl">Elige tu próximo programa con datos reales.</h1>
            <p className="mt-6 max-w-2xl text-lg text-blue-100/90 leading-relaxed">Compara contenido, duración, modalidad y precio en un solo lugar.</p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Button onClick={() => document.getElementById('programas')?.scrollIntoView({ behavior: 'smooth' })} size="lg" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold rounded-xl px-8 h-12 shadow-lg shadow-brand-mint/20 border-0">Explorar programas</Button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main id="programas" className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Programas recomendados</h2>
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-zinc-800 p-1 rounded-lg">
            <Button size="sm" variant="ghost" className={cn("h-7 text-xs font-bold rounded-md transition-all", viewMode === 'grid' ? "bg-white shadow-sm" : "text-slate-500")} onClick={() => setViewMode('grid')}>Grid</Button>
            <Button size="sm" variant="ghost" className={cn("h-7 text-xs font-bold rounded-md transition-all", viewMode === 'list' ? "bg-white shadow-sm" : "text-slate-500")} onClick={() => setViewMode('list')}>List</Button>
          </div>
        </div>

        <div className={cn("grid gap-6", viewMode === 'grid' ? "md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1")}>
          {filteredCourses.map((course) => (
            <article key={course.id} className={cn("group flex flex-col justify-between rounded-2xl border border-brand-gray/50 bg-white dark:bg-zinc-900/40 p-6 shadow-premium transition-all hover:border-brand-blue/30", viewMode === 'list' && "md:flex-row md:items-center gap-6")}>
              <div className={cn(viewMode === 'list' ? "flex-1" : "")}>
                <Badge variant="secondary" className="mb-4 bg-brand-blue/10 text-brand-blue font-bold border-0">{course.category}</Badge>
                <Link href={`/courses/${cleanSlug(course.slug)}`}>
                  <h3 className="text-xl font-bold group-hover:text-brand-blue transition-colors leading-snug">{course.name}</h3>
                </Link>
                <p className="mt-2 text-sm text-slate-500 flex items-center gap-1.5"><GraduationCap className="h-4 w-4" /> {course.institution_name}</p>
                <div className="mt-6 flex gap-6 flex-wrap">
                  <div className="flex flex-col"><span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Duración</span><span className="font-semibold text-sm">{course.duration || "Consultar"}</span></div>
                  <div className="flex flex-col"><span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Inversión</span><span className="font-bold text-brand-blue text-sm">{course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}</span></div>
                </div>
              </div>
              <div className={cn("mt-8 flex gap-3", viewMode === 'list' ? "md:flex-col md:w-48 mt-0" : "")}>
                <Link href={`/courses/${cleanSlug(course.slug)}`} className="flex-1 rounded-xl border border-brand-blue/30 px-4 py-2.5 text-center text-sm font-bold text-brand-blue hover:bg-brand-blue hover:text-white transition-all shadow-sm">Ver detalle</Link>
                <Button onClick={() => setIsModalOpen(true)} className="flex-1 rounded-xl bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold h-10 border-0">Quiero info</Button>
              </div>
            </article>
          ))}
        </div>
      </main>

      {/* Cómo Funciona */}
      <section id="como-funciona" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <div className="text-center mb-16">
          <Badge className="bg-brand-blue/10 text-brand-blue mb-4 border-0">PROCESO</Badge>
          <h2 className="text-3xl font-bold md:text-4xl mb-4">¿Cómo funciona Yachachiy?</h2>
          <p className="text-slate-500 max-w-2xl mx-auto">Análisis de datos real para decisiones educativas objetivas.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { step: "01", title: "Filtra", desc: "Encuentra programas por categoría, precio o modalidad." },
            { step: "02", title: "Compara", desc: "Analiza el ROI estimado y la malla curricular lado a lado." },
            { step: "03", title: "Elige", desc: "Solicita información directa para dar el siguiente paso." }
          ].map((item, i) => (
            <div key={i} className="p-8 rounded-3xl bg-slate-50 dark:bg-zinc-900/50 border border-brand-gray/30">
              <div className="text-4xl font-black text-brand-blue/10 mb-4">{item.step}</div>
              <h3 className="text-xl font-bold mb-2">{item.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Nosotros */}
      <section id="nosotros" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl font-bold mb-6">Nuestra Misión</h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed mb-8">Ayudar a profesionales de LATAM a elegir programas educativos con métricas transparentes.</p>
            <h2 className="text-3xl font-bold mb-6">Nuestra Visión</h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed">Ser la plataforma de referencia para decisiones data-driven en la región.</p>
          </div>
          <div className="bg-brand-blue/5 p-8 rounded-3xl border border-brand-blue/20">
            <h3 className="text-2xl font-bold mb-4 text-brand-blue">Propuesta de Valor</h3>
            <p className="text-lg text-slate-700 dark:text-slate-300">Unificamos contenido y precio para que compares sin fricción.</p>
          </div>
        </div>
      </section>

      {/* Instituciones */}
      <section id="instituciones" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <h2 className="text-3xl font-bold mb-12 text-center">Instituciones Aliadas</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {institutions.map((inst) => (
            <div key={inst.id} className="p-6 rounded-2xl bg-slate-50 dark:bg-zinc-900/50 border border-brand-gray/30 text-center hover:border-brand-blue transition-all">
              <span className="text-xs font-bold">{inst.name}</span>
            </div>
          ))}
        </div>
      </section>

      <footer className="bg-slate-50 dark:bg-brand-slate border-t border-brand-gray/30 py-12 text-center text-slate-500 text-sm font-bold">
        © 2026 Yachachiy.ai - Datos para decidir mejor.
      </footer>

      {/* Modal Form */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-brand-slate/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white dark:bg-zinc-900 w-full max-w-md rounded-3xl shadow-2xl overflow-hidden p-8 relative">
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 p-2 hover:bg-slate-100 rounded-full transition"><X className="h-5 w-5" /></button>
            <h3 className="text-2xl font-bold mb-2 text-brand-slate">Solicitar Asesoría</h3>
            <p className="text-sm text-slate-500 mb-6">Un experto te ayudará a elegir tu programa ideal.</p>
            <Input placeholder="Nombre" className="mb-4 h-12 rounded-xl" />
            <Input placeholder="WhatsApp" className="mb-6 h-12 rounded-xl" />
            <Button className="w-full h-12 bg-brand-blue hover:bg-brand-blue/90 text-white font-bold rounded-xl border-0 shadow-lg" onClick={() => setIsModalOpen(false)}>Enviar solicitud</Button>
          </div>
        </div>
      )}
    </div>
  );
}
