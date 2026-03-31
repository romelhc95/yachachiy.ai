"use client";

import { useEffect, useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Clock, TrendingUp, CheckCircle2, ChevronDown, X, GraduationCap, Briefcase, DollarSign, ArrowRight } from "lucide-react";
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

// FUNCIÓN DE NORMALIZACIÓN ÚNICA (DEBE COINCIDIR CON [slug]/page.tsx)
const cleanSlug = (slug: string) => {
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
  const [openFilterMenu, setOpenFilterMenu] = useState<string | null>(null);

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
      setAllCourses(data || []);
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
      setInstitutions(data || []);
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
        const matchesDuration = activeFilters.durations.some(range => {
          if (range === "<6") return months > 0 && months < 6;
          if (range === "6-12") return months >= 6 && months <= 12;
          if (range === ">12") return months > 12;
          return false;
        });
        if (!matchesDuration) return false;
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
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-blue text-white">Y</div>
            <span>Yachachiy<span className="text-brand-blue">.ai</span></span>
          </Link>
          <nav className="hidden md:flex gap-8 items-center">
            <Link href="/" className="text-sm font-medium text-brand-blue">Inicio</Link>
            <button onClick={() => document.getElementById('como-funciona')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Cómo Funciona</button>
            <button onClick={() => document.getElementById('nosotros')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Nosotros</button>
            <button onClick={() => document.getElementById('instituciones')?.scrollIntoView({ behavior: 'smooth' })} className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition">Instituciones</button>
            <Button onClick={() => setIsModalOpen(true)} size="sm" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-semibold rounded-xl px-5 h-9">Solicitar asesoría</Button>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-brand-slate to-brand-blue p-10 md:p-16 text-white shadow-premium">
          <div className="relative z-10">
            <p className="mb-4 text-sm font-bold uppercase tracking-[0.24em] text-brand-mint">Yachachiy · Data-driven education</p>
            <h1 className="max-w-3xl text-4xl font-bold md:text-6xl leading-tight">Elige tu próximo programa con datos reales.</h1>
            <p className="mt-6 max-w-2xl text-lg text-blue-100/90">Compara contenido, duración, modalidad y precio en un solo lugar.</p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Button onClick={() => document.getElementById('programas')?.scrollIntoView({ behavior: 'smooth' })} size="lg" className="bg-brand-mint text-brand-slate font-bold rounded-xl px-8 h-12 shadow-lg shadow-brand-mint/20">Explorar programas</Button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <main id="programas" className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-8 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Programas recomendados</h2>
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-zinc-800 p-1 rounded-lg">
            <Button size="sm" variant="ghost" className={cn("h-7 text-xs font-bold rounded-md", viewMode === 'grid' && "bg-white dark:bg-zinc-700")} onClick={() => setViewMode('grid')}>Grid</Button>
            <Button size="sm" variant="ghost" className={cn("h-7 text-xs font-bold rounded-md", viewMode === 'list' && "bg-white dark:bg-zinc-700")} onClick={() => setViewMode('list')}>List</Button>
          </div>
        </div>

        <div className={cn("grid gap-6", viewMode === 'grid' ? "md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1")}>
          {filteredCourses.map((course) => (
            <article key={course.id} className={cn("group rounded-2xl border border-brand-gray/50 bg-white dark:bg-zinc-900/40 p-6 shadow-premium transition-all hover:border-brand-blue/30", viewMode === 'list' && "md:flex md:items-center md:justify-between")}>
              <div>
                <Badge variant="secondary" className="mb-4 bg-brand-blue/10 text-brand-blue font-bold">{course.category}</Badge>
                {/* ENLACE NORMALIZADO: AQUÍ ESTÁ EL FIX CRÍTICO */}
                <Link href={`/courses/${cleanSlug(course.slug)}`}>
                  <h3 className="text-xl font-bold hover:text-brand-blue transition-colors">{course.name}</h3>
                </Link>
                <p className="mt-2 text-sm text-slate-500">{course.institution_name}</p>
                
                <div className="mt-6 flex gap-6 flex-wrap">
                  <div className="flex flex-col"><span className="text-[10px] font-bold text-slate-400">DURACIÓN</span><span className="text-sm font-semibold">{course.duration || "Consultar"}</span></div>
                  <div className="flex flex-col"><span className="text-[10px] font-bold text-slate-400">INVERSIÓN</span><span className="text-sm font-bold text-brand-blue">{course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}</span></div>
                </div>
              </div>
              <div className="mt-8 flex gap-3 md:mt-0">
                <Link href={`/courses/${cleanSlug(course.slug)}`} className="flex-1 rounded-xl border border-brand-blue/30 px-4 py-2.5 text-center text-sm font-bold text-brand-blue hover:bg-brand-blue hover:text-white transition-all shadow-sm">Ver detalle</Link>
                <Button onClick={() => setIsModalOpen(true)} className="flex-1 rounded-xl bg-brand-mint text-brand-slate font-bold h-10 border-0">Quiero info</Button>
              </div>
            </article>
          ))}
        </div>
      </main>

      {/* Nosotros */}
      <section id="nosotros" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <h2 className="text-3xl font-bold mb-6 text-center">Nuestra Misión</h2>
        <p className="text-lg text-slate-600 dark:text-slate-400 text-center max-w-3xl mx-auto">Ayudar a profesionales de LATAM a elegir programas educativos con métricas comparables y transparentes.</p>
      </section>

      {/* Footer */}
      <footer className="bg-slate-50 dark:bg-brand-slate border-t border-brand-gray/30 py-12 text-center">
        <p className="text-sm font-bold text-slate-500">© 2026 Yachachiy.ai - Datos para decidir mejor.</p>
      </footer>

      {/* Modal Reusable (Simplified) */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-brand-slate/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-zinc-900 w-full max-w-md rounded-3xl shadow-2xl p-8 relative">
            <button onClick={() => setIsModalOpen(false)} className="absolute top-4 right-4 p-2">
              <X className="h-5 w-5" />
            </button>
            <h3 className="text-2xl font-bold mb-4">Recibir recomendación</h3>
            <Input placeholder="Nombre" className="mb-4 h-12 rounded-xl" />
            <Input placeholder="Email" className="mb-6 h-12 rounded-xl" />
            <Button className="w-full h-12 bg-brand-blue text-white font-bold rounded-xl" onClick={() => setIsModalOpen(false)}>Enviar solicitud</Button>
          </div>
        </div>
      )}
    </div>
  );
}
