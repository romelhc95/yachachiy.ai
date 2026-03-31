"use client";

import { useEffect, useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, MapPin, Clock, ExternalLink, Filter, Navigation2, TrendingUp, CheckCircle2, ChevronDown, X, Check, GraduationCap, Briefcase, DollarSign } from "lucide-react";
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
}

interface Institution {
  id: string;
  name: string;
  slug: string;
  website_url: string;
}

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
  
  // Filter States
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
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setAllCourses(data);
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
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setInstitutions(data);
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
        const isPriceFilterActive = activeFilters.priceMin !== "" || activeFilters.priceMax !== "";
        if (isPriceFilterActive && !activeFilters.includeConsultar) return false;
      } else {
        if (activeFilters.priceMin !== "" && price < parseFloat(activeFilters.priceMin)) return false;
        if (activeFilters.priceMax !== "" && price > parseFloat(activeFilters.priceMax)) return false;
      }

      return true;
    });
  }, [allCourses, activeFilters]);

  const toggleFilter = (type: 'modes' | 'durations' | 'types', value: string) => {
    setActiveFilters(prev => ({
      ...prev,
      [type]: prev[type].includes(value) ? prev[type].filter(v => v !== value) : [...prev[type], value]
    }));
  };

  const clearFilters = () => {
    setActiveFilters({ priceMin: "", priceMax: "", modes: [], durations: [], types: [], includeConsultar: true });
  };

  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>, field: 'priceMin' | 'priceMax') => {
    setActiveFilters(prev => ({ ...prev, [field]: e.target.value }));
  };

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
            <button 
              onClick={() => document.getElementById('como-funciona')?.scrollIntoView({ behavior: 'smooth' })}
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition"
            >
              Cómo Funciona
            </button>
            <button 
              onClick={() => document.getElementById('nosotros')?.scrollIntoView({ behavior: 'smooth' })}
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition"
            >
              Nosotros
            </button>
            <button 
              onClick={() => document.getElementById('instituciones')?.scrollIntoView({ behavior: 'smooth' })}
              className="text-sm font-medium text-slate-600 dark:text-slate-300 hover:text-brand-blue transition"
            >
              Instituciones
            </button>
            <Button 
              onClick={() => setIsModalOpen(true)}
              size="sm" 
              className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-semibold rounded-xl px-5 h-9"
            >
              Solicitar asesoría
            </Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-brand-slate to-brand-blue p-10 md:p-16 text-white shadow-premium">
          <div className="relative z-10">
            <p className="mb-4 text-sm font-bold uppercase tracking-[0.24em] text-brand-mint">Yachachiy · Data-driven education</p>
            <h1 className="max-w-3xl text-4xl font-bold leading-tight md:text-6xl">
              Elige tu próximo programa con datos reales, no con promesas.
            </h1>
            <p className="mt-6 max-w-2xl text-lg text-blue-100/90 leading-relaxed">
              Compara contenido, duración, modalidad y precio en un solo lugar. Toma decisiones informadas para potenciar tu carrera profesional en el Perú.
            </p>
            <div className="mt-10 flex flex-wrap gap-4">
              <Button 
                onClick={() => document.getElementById('programas')?.scrollIntoView({ behavior: 'smooth' })}
                size="lg" 
                className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold rounded-xl px-8 h-12 shadow-lg shadow-brand-mint/20"
              >
                Explorar programas
              </Button>
              <Button 
                onClick={() => document.getElementById('como-funciona')?.scrollIntoView({ behavior: 'smooth' })}
                size="lg" 
                variant="outline" 
                className="border-white/20 hover:bg-white/10 text-white font-bold rounded-xl px-8 h-12"
              >
                ¿Cómo funciona?
              </Button>
            </div>
          </div>
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 h-80 w-80 rounded-full bg-white/5 blur-3xl" />
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 h-64 w-64 rounded-full bg-brand-mint/5 blur-3xl" />
        </div>
      </section>

      {/* Filter Section */}
      <section id="programas" className="mx-auto max-w-6xl px-6 -mt-8 relative z-20">
        <div className="rounded-2xl border border-brand-gray/30 bg-white dark:bg-zinc-900/50 dark:backdrop-blur-xl p-6 shadow-xl">
          <div className="grid gap-4 md:grid-cols-4 items-end">
            <div className="md:col-span-2">
              <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 mb-2 block">¿Qué quieres aprender?</label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                <Input 
                  className="rounded-xl border-brand-gray bg-slate-50 dark:bg-zinc-800/50 pl-11 h-12 focus-visible:ring-brand-blue"
                  placeholder="Buscar por programa, institución o categoría"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchCourses(searchTerm)}
                />
              </div>
            </div>
            <div>
              <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 mb-2 block">Modalidad</label>
              <select 
                className="w-full rounded-xl border-brand-gray bg-slate-50 dark:bg-zinc-800/50 px-4 h-12 text-sm focus:ring-2 focus:ring-brand-blue outline-none transition"
                onChange={(e) => {
                  const val = e.target.value;
                  setActiveFilters(prev => ({ ...prev, modes: val === "Todas" ? [] : [val] }));
                }}
              >
                <option>Todas</option>
                <option>Remoto</option>
                <option>Presencial</option>
                <option>Híbrido</option>
              </select>
            </div>
            <div>
              <Button 
                onClick={() => fetchCourses(searchTerm)}
                className="w-full h-12 bg-brand-slate dark:bg-white dark:text-brand-slate hover:bg-brand-slate/90 dark:hover:bg-white/90 text-white font-bold rounded-xl transition shadow-lg"
              >
                Buscar ahora
              </Button>
            </div>
          </div>

          {/* Extended Filters Toggle */}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <div className="flex flex-wrap gap-2 relative">
              <Button 
                variant="outline" 
                size="sm" 
                className={cn("rounded-lg h-8 px-3 text-xs gap-1.5", activeFilters.types.length > 0 && "bg-brand-blue/10 border-brand-blue text-brand-blue")}
                onClick={() => setOpenFilterMenu(openFilterMenu === 'type' ? null : 'type')}
              >
                Categoría {activeFilters.types.length > 0 && `(${activeFilters.types.length})`} <ChevronDown className="h-3 w-3" />
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className={cn("rounded-lg h-8 px-3 text-xs gap-1.5", (activeFilters.priceMin || activeFilters.priceMax) && "bg-brand-blue/10 border-brand-blue text-brand-blue")}
                onClick={() => setOpenFilterMenu(openFilterMenu === 'price' ? null : 'price')}
              >
                Precio <ChevronDown className="h-3 w-3" />
              </Button>

              {/* Filter Popovers (Simulated) */}
              {openFilterMenu === 'type' && (
                <div className="absolute top-full left-0 mt-2 bg-white dark:bg-zinc-900 border border-brand-gray/30 rounded-xl shadow-2xl p-4 grid grid-cols-2 gap-2 z-50 min-w-[300px]">
                  {['Curso', 'Especialidad', 'Diplomado', 'Programa', 'Maestría'].map(type => (
                    <label key={type} className="flex items-center gap-2 cursor-pointer p-2 hover:bg-slate-50 dark:hover:bg-zinc-800 rounded-lg">
                      <input 
                        type="checkbox" 
                        className="rounded border-slate-300 text-brand-blue focus:ring-brand-blue"
                        checked={activeFilters.types.includes(type)}
                        onChange={() => toggleFilter('types', type)}
                      />
                      <span className="text-sm">{type}</span>
                    </label>
                  ))}
                  <div className="col-span-2 pt-2 border-t mt-2">
                    <Button variant="ghost" size="sm" className="w-full h-8 text-xs" onClick={() => setOpenFilterMenu(null)}>Cerrar</Button>
                  </div>
                </div>
              )}

              {openFilterMenu === 'price' && (
                <div className="absolute top-full left-1/4 mt-2 bg-white dark:bg-zinc-900 border border-brand-gray/30 rounded-xl shadow-2xl p-6 z-50 min-w-[280px]">
                  <div className="space-y-4">
                    <h4 className="font-bold text-sm mb-2">Rango de inversión (S/)</h4>
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-[10px] uppercase font-bold text-slate-400 mb-1 block">Min</label>
                        <Input 
                          type="number"
                          placeholder="0"
                          className="h-9 text-sm"
                          value={activeFilters.priceMin}
                          onChange={(e) => handlePriceChange(e, 'priceMin')}
                        />
                      </div>
                      <div>
                        <label className="text-[10px] uppercase font-bold text-slate-400 mb-1 block">Max</label>
                        <Input 
                          type="number"
                          placeholder="Max"
                          className="h-9 text-sm"
                          value={activeFilters.priceMax}
                          onChange={(e) => handlePriceChange(e, 'priceMax')}
                        />
                      </div>
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer pt-2">
                      <input 
                        type="checkbox" 
                        className="rounded border-slate-300 text-brand-blue focus:ring-brand-blue"
                        checked={activeFilters.includeConsultar}
                        onChange={(e) => setActiveFilters(prev => ({ ...prev, includeConsultar: e.target.checked }))}
                      />
                      <span className="text-xs text-slate-500">Incluir programas por consultar</span>
                    </label>
                  </div>
                  <div className="pt-4 border-t mt-4">
                    <Button className="w-full bg-brand-blue text-white h-9 rounded-lg text-sm" onClick={() => setOpenFilterMenu(null)}>Aplicar filtros</Button>
                  </div>
                </div>
              )}
            </div>
            {(activeFilters.modes.length > 0 || activeFilters.types.length > 0 || activeFilters.priceMin || activeFilters.priceMax) && (
              <Button variant="ghost" size="sm" className="h-8 text-xs text-slate-500 hover:text-red-500" onClick={clearFilters}>
                <X className="mr-1 h-3 w-3" /> Limpiar filtros
              </Button>
            )}
          </div>
        </div>
      </section>

      {/* Results Section */}
      <main className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Programas recomendados</h2>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
              {loading ? "Cargando ofertas..." : `Mostrando ${filteredCourses.length} programas encontrados en el Perú`}
            </p>
          </div>
          <div className="hidden md:flex items-center gap-2 bg-slate-100 dark:bg-zinc-800 p-1 rounded-lg">
            <Button 
              size="sm" 
              variant="ghost" 
              className={cn("h-7 text-xs font-bold rounded-md transition-all", viewMode === 'grid' ? "bg-white dark:bg-zinc-700 shadow-sm" : "text-slate-500")}
              onClick={() => setViewMode('grid')}
            >
              Grid
            </Button>
            <Button 
              size="sm" 
              variant="ghost" 
              className={cn("h-7 text-xs font-bold rounded-md transition-all", viewMode === 'list' ? "bg-white dark:bg-zinc-700 shadow-sm" : "text-slate-500")}
              onClick={() => setViewMode('list')}
            >
              List
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-[420px] rounded-2xl bg-slate-100 dark:bg-zinc-800 animate-pulse" />
            ))}
          </div>
        ) : (
          <div className={cn(
            "grid gap-6",
            viewMode === 'grid' ? "md:grid-cols-2 lg:grid-cols-3" : "grid-cols-1"
          )}>
            {filteredCourses.map((course) => (
              <article 
                key={course.id} 
                className={cn(
                  "group flex flex-col justify-between rounded-2xl border border-brand-gray/50 bg-white dark:bg-zinc-900/40 p-6 shadow-premium transition-all hover:border-brand-blue/30",
                  viewMode === 'grid' ? "hover:-translate-y-1 hover:shadow-2xl" : "md:flex-row md:items-center gap-6"
                )}
              >
                <div className={cn(viewMode === 'list' ? "flex-1" : "")}>
                  <div className="mb-4 flex items-center justify-between">
                    <Badge variant="secondary" className="bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20 font-bold border-0">
                      {course.category}
                    </Badge>
                    <button 
                      onClick={() => {
                        if (selectedForCompare.find(c => c.id === course.id)) {
                          setSelectedForCompare(selectedForCompare.filter(c => c.id !== course.id));
                        } else if (selectedForCompare.length < 3) {
                          setSelectedForCompare([...selectedForCompare, course]);
                        }
                      }}
                      className={cn(
                        "flex h-8 w-8 items-center justify-center rounded-full border transition-all",
                        selectedForCompare.find(c => c.id === course.id) 
                          ? "bg-brand-blue border-brand-blue text-white shadow-lg" 
                          : "border-brand-gray hover:border-brand-blue hover:text-brand-blue"
                      )}
                    >
                      <CheckCircle2 className="h-4 w-4" />
                    </button>
                  </div>

                  <Link href={`/courses/${course.slug}`}>
                    <h3 className="text-xl font-bold leading-snug group-hover:text-brand-blue transition-colors">
                      {course.name}
                    </h3>
                  </Link>
                  <p className="mt-2 flex items-center gap-1.5 text-sm font-medium text-slate-500 dark:text-slate-400">
                    <GraduationCap className="h-4 w-4" />
                    {course.institution_name}
                  </p>

                  <div className={cn(
                    "mt-6 gap-6",
                    viewMode === 'grid' ? "space-y-3" : "flex flex-wrap items-center"
                  )}>
                    <div className="flex items-center gap-6 flex-wrap">
                      <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-bold text-slate-400 mb-1 flex items-center gap-1"><Clock className="h-3 w-3" /> Duración</span>
                        <span className="font-semibold text-sm">{course.duration || "Consultar"}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-bold text-slate-400 mb-1 flex items-center gap-1"><Briefcase className="h-3 w-3" /> Modalidad</span>
                        <span className="font-semibold text-sm">{course.mode}</span>
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[10px] uppercase font-bold text-slate-400 mb-1 flex items-center gap-1"><DollarSign className="h-3 w-3" /> Inversión</span>
                        <span className="font-bold text-brand-blue dark:text-brand-mint text-sm">
                          {course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {course.roi_months != null && (
                    <div className={cn(
                      "mt-5 rounded-xl bg-emerald-50 dark:bg-emerald-500/10 p-3 flex items-center justify-between",
                      viewMode === 'list' ? "inline-flex gap-4 px-4 py-2 mt-4" : ""
                    )}>
                      <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase">Retorno ROI</span>
                      <span className="text-sm font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
                        <TrendingUp className="h-4 w-4" /> {course.roi_months.toFixed(1)} meses
                      </span>
                    </div>
                  )}
                </div>

                <div className={cn(
                  "mt-8 flex gap-3",
                  viewMode === 'list' ? "mt-0 md:flex-col md:w-48" : ""
                )}>
                  <Link 
                    href={`/courses/${course.slug}`}
                    className="flex-1 rounded-xl border border-brand-blue/30 px-4 py-2.5 text-center text-sm font-bold text-brand-blue hover:bg-brand-blue hover:text-white transition-all shadow-sm"
                  >
                    Ver detalle
                  </Link>
                  <Button 
                    onClick={() => setIsModalOpen(true)}
                    className="flex-1 rounded-xl bg-brand-mint hover:bg-brand-mint/90 px-4 py-2.5 text-sm font-bold text-brand-slate transition shadow-lg shadow-brand-mint/10 border-0"
                  >
                    Quiero info
                  </Button>
                </div>
              </article>
            ))}
          </div>
        )}

        {!loading && filteredCourses.length === 0 && (
          <div className="text-center py-24 bg-slate-50 dark:bg-zinc-900/50 rounded-3xl border-2 border-dashed border-brand-gray/50">
            <div className="mx-auto w-16 h-16 bg-white dark:bg-zinc-800 rounded-2xl flex items-center justify-center shadow-sm mb-6">
              <Search className="h-8 w-8 text-brand-blue" />
            </div>
            <h3 className="text-xl font-bold mb-2">No encontramos resultados</h3>
            <p className="text-slate-500 max-w-xs mx-auto mb-8">
              Prueba ajustando tus filtros o buscando un término más general.
            </p>
            <Button variant="outline" className="rounded-xl border-brand-gray" onClick={() => { setSearchTerm(""); clearFilters(); fetchCourses(""); }}>
              Restablecer búsqueda
            </Button>
          </div>
        )}
      </main>

      {/* Cómo Funciona Section */}
      <section id="como-funciona" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <div className="text-center mb-16">
          <Badge className="bg-brand-blue/10 text-brand-blue hover:bg-brand-blue/20 mb-4 px-4 py-1 rounded-full border-0">PROCESO</Badge>
          <h2 className="text-3xl font-bold md:text-4xl mb-4">¿Cómo funciona Yachachiy?</h2>
          <p className="text-slate-500 max-w-2xl mx-auto text-lg">
            Nuestra plataforma utiliza IA para analizar miles de programas y ofrecerte una visión clara y objetiva para tu futuro.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              step: "01",
              title: "Filtra y Descubre",
              desc: "Usa nuestro buscador inteligente para encontrar programas por nombre, categoría o precio que se ajusten a tu perfil.",
              icon: <Search className="h-6 w-6 text-brand-blue" />
            },
            {
              step: "02",
              title: "Compara con Datos",
              desc: "Selecciona hasta 3 programas y compara su ROI estimado, malla curricular, docentes y modalidad lado a lado.",
              icon: <TrendingUp className="h-6 w-6 text-emerald-500" />
            },
            {
              step: "03",
              title: "Toma el Control",
              desc: "Solicita información directa o una asesoría personalizada para dar el siguiente paso en tu carrera con total seguridad.",
              icon: <CheckCircle2 className="h-6 w-6 text-brand-mint" />
            }
          ].map((item, idx) => (
            <div key={idx} className="relative group p-8 rounded-3xl bg-slate-50 dark:bg-zinc-900/50 border border-brand-gray/30 transition-all hover:border-brand-blue">
              <div className="absolute top-6 right-8 text-4xl font-black text-brand-blue/5 group-hover:text-brand-blue/10 transition-colors">{item.step}</div>
              <div className="mb-6 h-12 w-12 rounded-2xl bg-white dark:bg-zinc-800 flex items-center justify-center shadow-sm">
                {item.icon}
              </div>
              <h3 className="text-xl font-bold mb-3">{item.title}</h3>
              <p className="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                {item.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="rounded-3xl border border-brand-gray/30 bg-slate-50 dark:bg-zinc-900/50 p-10 md:p-16 text-center shadow-premium">
          <h2 className="text-3xl font-bold md:text-4xl">¿Listo para elegir con confianza?</h2>
          <p className="mt-4 text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Recibe una recomendación personalizada basada en tus objetivos profesionales y tu momento ideal para empezar.
          </p>
          <Button 
            onClick={() => setIsModalOpen(true)}
            className="mt-10 rounded-xl bg-brand-mint hover:bg-brand-mint/90 px-10 h-14 text-lg font-bold text-brand-slate shadow-xl shadow-brand-mint/20 border-0"
          >
            Quiero mi recomendación
          </Button>
        </div>
      </section>

      {/* Nosotros Section */}
      <section id="nosotros" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl font-bold mb-6">Nuestra Misión</h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed mb-8">
              Ayudar a profesionales de LATAM a elegir programas tech con métricas comparables y transparentes.
            </p>
            <h2 className="text-3xl font-bold mb-6">Nuestra Visión</h2>
            <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed">
              Ser la plataforma de referencia para decisiones educativas data-driven en la región.
            </p>
          </div>
          <div className="bg-brand-blue/5 dark:bg-brand-blue/10 rounded-3xl p-8 border border-brand-blue/20">
            <h3 className="text-2xl font-bold mb-4 text-brand-blue">Propuesta de Valor</h3>
            <p className="text-lg text-slate-700 dark:text-slate-300 leading-relaxed">
              Unificamos contenido, docentes, formato y precio para que compares sin fricción y actúes rápido.
            </p>
            <div className="mt-8 grid grid-cols-2 gap-4">
              <div className="bg-white dark:bg-brand-slate p-4 rounded-xl shadow-sm">
                <CheckCircle2 className="text-brand-mint mb-2" />
                <p className="font-bold text-sm">Datos Reales</p>
              </div>
              <div className="bg-white dark:bg-brand-slate p-4 rounded-xl shadow-sm">
                <TrendingUp className="text-brand-blue mb-2" />
                <p className="font-bold text-sm">ROI Visible</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Institutions Section */}
      <section id="instituciones" className="mx-auto max-w-6xl px-6 py-20 border-t border-brand-gray/20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Instituciones Aliadas</h2>
          <p className="text-slate-500 max-w-2xl mx-auto">
            Trabajamos con las mejores universidades y escuelas de tecnología del Perú para brindarte información veraz.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {institutions.map((inst) => (
            <div key={inst.id} className="group relative flex flex-col items-center justify-center p-6 rounded-2xl bg-slate-50 dark:bg-zinc-900/50 border border-brand-gray/30 hover:border-brand-blue transition-all hover:shadow-lg">
              <div className="w-12 h-12 rounded-xl bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-xl mb-3 group-hover:bg-brand-blue group-hover:text-white transition-colors">
                {inst.name.charAt(0)}
              </div>
              <span className="text-xs font-bold text-center group-hover:text-brand-blue transition-colors">{inst.name}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Floating Comparison Bar */}
      {selectedForCompare.length > 0 && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 w-[90%] max-w-2xl animate-in fade-in slide-in-from-bottom-8 duration-500">
          <div className="bg-brand-slate text-white border border-white/10 shadow-2xl rounded-2xl px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex -space-x-3">
                {selectedForCompare.map(c => (
                  <div key={c.id} className="w-10 h-10 rounded-full border-2 border-brand-slate bg-brand-blue flex items-center justify-center text-[10px] font-bold ring-2 ring-brand-mint/30">
                    {c.institution_name.substring(0, 2).toUpperCase()}
                  </div>
                ))}
              </div>
              <div>
                <div className="text-sm font-bold">
                  {selectedForCompare.length} programa{selectedForCompare.length > 1 ? "s" : ""} seleccionado{selectedForCompare.length > 1 ? "s" : ""}
                </div>
                <div className="text-[10px] text-brand-mint uppercase font-bold tracking-wider">Compara y elige mejor</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-white/60 hover:text-white hover:bg-white/10"
                onClick={() => setSelectedForCompare([])}
              >
                Limpiar
              </Button>
              <Link href={{
                pathname: '/compare',
                query: { ids: selectedForCompare.map(c => c.id).join(',') }
              }}>
                <Button size="sm" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold rounded-xl px-6 shadow-lg shadow-brand-mint/20">
                  Comparar ahora
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-brand-slate/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-white dark:bg-zinc-900 w-full max-w-md rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
            <div className="bg-brand-blue p-8 text-white relative">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-full transition"
              >
                <X className="h-5 w-5" />
              </button>
              <div className="h-12 w-12 bg-white/20 rounded-2xl flex items-center justify-center mb-4">
                <Badge className="bg-brand-mint text-brand-slate font-bold">TOP</Badge>
              </div>
              <h3 className="text-2xl font-bold">Recomendación Personalizada</h3>
              <p className="text-blue-100/80 text-sm mt-2">Dinos qué buscas y nuestro algoritmo encontrará el programa ideal para ti.</p>
            </div>
            
            <div className="p-8 space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase text-slate-500">Nombre Completo</label>
                <Input placeholder="Ej. Juan Pérez" className="rounded-xl border-brand-gray h-11" />
              </div>
              
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase text-slate-500">Interés Académico</label>
                <select className="w-full rounded-xl border border-brand-gray bg-white dark:bg-zinc-800 px-4 h-11 text-sm focus:ring-2 focus:ring-brand-blue outline-none transition">
                  <option>Data Science & AI</option>
                  <option>Desarrollo Web / Mobile</option>
                  <option>Ciberseguridad</option>
                  <option>Marketing Digital</option>
                  <option>Gestión de Proyectos Tech</option>
                  <option>Otro</option>
                </select>
              </div>
              
              <div className="space-y-2">
                <label className="text-xs font-bold uppercase text-slate-500">Presupuesto Estimado (S/)</label>
                <Input type="number" placeholder="Ej. 5000" className="rounded-xl border-brand-gray h-11" />
              </div>

              <Button 
                onClick={() => {
                  alert("¡Gracias! Pronto recibirás tu recomendación por correo.");
                  setIsModalOpen(false);
                }}
                className="w-full h-12 bg-brand-blue hover:bg-brand-blue/90 text-white font-bold rounded-xl shadow-lg shadow-brand-blue/20"
              >
                Obtener mi recomendación
              </Button>
              <p className="text-center text-[10px] text-slate-400">
                Al solicitar, aceptas nuestros términos de privacidad.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-slate-50 dark:bg-brand-slate border-t border-brand-gray/30 mt-12">
        <div className="mx-auto max-w-6xl px-6 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex items-center gap-2 text-xl font-bold tracking-tight">
              <div className="flex h-6 w-6 items-center justify-center rounded bg-brand-blue text-white text-xs">Y</div>
              <span>Yachachiy.ai</span>
            </div>
            <div className="flex gap-8 text-sm font-medium text-slate-500 dark:text-slate-400">
              <Link href="#" className="hover:text-brand-blue">Términos</Link>
              <Link href="#" className="hover:text-brand-blue">Privacidad</Link>
              <Link href="#" className="hover:text-brand-blue">Contacto</Link>
            </div>
            <p className="text-xs text-slate-400">
              © {new Date().getFullYear()} Yachachiy.ai. Datos para decidir mejor.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
