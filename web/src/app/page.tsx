"use client";

import { useEffect, useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button, buttonVariants } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, MapPin, Clock, ExternalLink, Filter, Navigation2, TrendingUp, CheckCircle2, ChevronDown, X, Check } from "lucide-react";
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

function parseDurationToMonths(duration: string | null): number {
  if (!duration) return 0;
  // Handle various formats like "24 meses", "12 semanas", "1 año"
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
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [selectedForCompare, setSelectedForCompare] = useState<Course[]>([]);
  
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

  const fetchCourses = async (search = "") => {
    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const url = search 
        ? `${apiUrl}/courses?name=${encodeURIComponent(search)}`
        : `${apiUrl}/courses`;
      const response = await fetch(url);
      const data = await response.json();
      setAllCourses(data);
    } catch (error) {
      console.error("Error fetching courses:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCourses();
  }, []);

  const filteredCourses = useMemo(() => {
    return allCourses.filter((course) => {
      // Modality filter
      if (activeFilters.modes.length > 0) {
        if (!activeFilters.modes.includes(course.mode)) return false;
      }

      // Type filter
      if (activeFilters.types.length > 0) {
        if (!activeFilters.types.includes(course.category)) return false;
      }

      // Duration filter
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

      // Price filter
      const price = course.price_pen;
      if (price === null) {
        // Handle "Consultar" cases
        // Show if "includeConsultar" is true, OR if no price filter is active
        const isPriceFilterActive = activeFilters.priceMin !== "" || activeFilters.priceMax !== "";
        if (isPriceFilterActive && !activeFilters.includeConsultar) {
          return false;
        }
      } else {
        if (activeFilters.priceMin !== "" && price < parseFloat(activeFilters.priceMin)) return false;
        if (activeFilters.priceMax !== "" && price > parseFloat(activeFilters.priceMax)) return false;
      }

      return true;
    });
  }, [allCourses, activeFilters]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCourses(searchTerm);
  };

  const toggleFilter = (type: 'modes' | 'durations' | 'types', value: string) => {
    setActiveFilters(prev => ({
      ...prev,
      [type]: prev[type].includes(value) 
        ? prev[type].filter(v => v !== value) 
        : [...prev[type], value]
    }));
  };

  const toggleCompare = (course: Course) => {
    if (selectedForCompare.find(c => c.id === course.id)) {
      setSelectedForCompare(selectedForCompare.filter(c => c.id !== course.id));
    } else {
      if (selectedForCompare.length < 3) {
        setSelectedForCompare([...selectedForCompare, course]);
      }
    }
  };

  const clearFilters = () => {
    setActiveFilters({
      priceMin: "",
      priceMax: "",
      modes: [],
      durations: [],
      types: [],
      includeConsultar: true
    });
  };

  return (
    <div className="min-h-screen bg-[#f8f9fa] dark:bg-zinc-950 font-sans text-slate-900 dark:text-zinc-100">
      {/* Search Header - Inspired by Google Flights minimalist style */}
      <div className="bg-white dark:bg-zinc-900 border-b border-slate-200 dark:border-zinc-800 shadow-sm sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3 mb-6">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center text-white font-bold">Y</div>
              <h1 className="text-xl font-medium tracking-tight">Yachachiy.ai</h1>
            </Link>
          </div>

          <form onSubmit={handleSearch} className="relative flex flex-col md:flex-row gap-2 bg-white dark:bg-zinc-900 p-2 rounded-lg border border-slate-300 dark:border-zinc-700 shadow-md focus-within:ring-2 focus-within:ring-indigo-500/20 transition-all">
            <div className="flex-1 relative flex items-center">
              <Search className="absolute left-4 h-5 w-5 text-slate-400" />
              <Input 
                type="text" 
                placeholder="¿Qué quieres estudiar?" 
                className="pl-12 h-12 border-none bg-transparent text-lg focus-visible:ring-0 placeholder:text-slate-400"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div className="h-10 w-px bg-slate-200 dark:bg-zinc-700 hidden md:block self-center" />
            <div className="flex items-center px-4 gap-2 text-slate-500 min-w-[140px]">
              <MapPin className="h-5 w-5" />
              <span className="text-sm font-medium">Lima, PE</span>
            </div>
            <Button type="submit" className="h-12 px-8 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md font-medium">
              Explorar
            </Button>
          </form>

          {/* Filters Bar */}
          <div className="flex flex-wrap gap-2 mt-6">
            <div className="relative">
              <Button 
                variant={activeFilters.modes.length > 0 ? "default" : "outline"} 
                size="sm" 
                className="rounded-full border-slate-300 dark:border-zinc-700 text-xs h-8 px-4 gap-2"
                onClick={() => setOpenFilterMenu(openFilterMenu === 'mode' ? null : 'mode')}
              >
                Modalidad {activeFilters.modes.length > 0 && `(${activeFilters.modes.length})`} <ChevronDown className="h-3 w-3" />
              </Button>
              {openFilterMenu === 'mode' && (
                <div className="absolute top-full mt-2 left-0 w-48 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg shadow-xl p-3 z-50">
                  <div className="space-y-2">
                    {['Remoto', 'Presencial', 'Híbrido'].map(mode => (
                      <label key={mode} className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 dark:hover:bg-zinc-800 p-1 rounded transition-colors" onClick={() => toggleFilter('modes', mode)}>
                        <div 
                          className={cn(
                            "w-4 h-4 rounded border flex items-center justify-center transition-colors",
                            activeFilters.modes.includes(mode) ? "bg-indigo-600 border-indigo-600 text-white" : "border-slate-300"
                          )}
                        >
                          {activeFilters.modes.includes(mode) && <Check className="h-3 w-3" />}
                        </div>
                        <span className="text-sm">{mode}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="relative">
              <Button 
                variant={activeFilters.types.length > 0 ? "default" : "outline"} 
                size="sm" 
                className="rounded-full border-slate-300 dark:border-zinc-700 text-xs h-8 px-4 gap-2"
                onClick={() => setOpenFilterMenu(openFilterMenu === 'type' ? null : 'type')}
              >
                Tipo {activeFilters.types.length > 0 && `(${activeFilters.types.length})`} <ChevronDown className="h-3 w-3" />
              </Button>
              {openFilterMenu === 'type' && (
                <div className="absolute top-full mt-2 left-0 w-48 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg shadow-xl p-3 z-50">
                  <div className="space-y-2">
                    {['Curso', 'Especialidad', 'Diplomado', 'Taller', 'Programa', 'Maestría', 'Doctorado'].map(type => (
                      <label key={type} className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 dark:hover:bg-zinc-800 p-1 rounded transition-colors" onClick={() => toggleFilter('types', type)}>
                        <div 
                          className={cn(
                            "w-4 h-4 rounded border flex items-center justify-center transition-colors",
                            activeFilters.types.includes(type) ? "bg-indigo-600 border-indigo-600 text-white" : "border-slate-300"
                          )}
                        >
                          {activeFilters.types.includes(type) && <Check className="h-3 w-3" />}
                        </div>
                        <span className="text-sm">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="relative">
              <Button 
                variant={(activeFilters.priceMin !== "" || activeFilters.priceMax !== "") ? "default" : "outline"} 
                size="sm" 
                className="rounded-full border-slate-300 dark:border-zinc-700 text-xs h-8 px-4 gap-2"
                onClick={() => setOpenFilterMenu(openFilterMenu === 'price' ? null : 'price')}
              >
                Precio <ChevronDown className="h-3 w-3" />
              </Button>
              {openFilterMenu === 'price' && (
                <div className="absolute top-full mt-2 left-0 w-64 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg shadow-xl p-4 z-50">
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-2">
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-slate-400">Min (S/)</label>
                        <Input 
                          type="number" 
                          placeholder="0" 
                          className="h-9 text-sm"
                          value={activeFilters.priceMin}
                          onChange={(e) => setActiveFilters(prev => ({ ...prev, priceMin: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-1">
                        <label className="text-[10px] uppercase font-bold text-slate-400">Max (S/)</label>
                        <Input 
                          type="number" 
                          placeholder="50000" 
                          className="h-9 text-sm"
                          value={activeFilters.priceMax}
                          onChange={(e) => setActiveFilters(prev => ({ ...prev, priceMax: e.target.value }))}
                        />
                      </div>
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveFilters(prev => ({ ...prev, includeConsultar: !prev.includeConsultar }))}>
                      <div 
                        className={cn(
                          "w-4 h-4 rounded border flex items-center justify-center transition-colors",
                          activeFilters.includeConsultar ? "bg-indigo-600 border-indigo-600 text-white" : "border-slate-300"
                        )}
                      >
                        {activeFilters.includeConsultar && <Check className="h-3 w-3" />}
                      </div>
                      <span className="text-sm">Mostrar "A consultar"</span>
                    </label>
                  </div>
                </div>
              )}
            </div>

            <div className="relative">
              <Button 
                variant={activeFilters.durations.length > 0 ? "default" : "outline"} 
                size="sm" 
                className="rounded-full border-slate-300 dark:border-zinc-700 text-xs h-8 px-4 gap-2"
                onClick={() => setOpenFilterMenu(openFilterMenu === 'duration' ? null : 'duration')}
              >
                Duración {activeFilters.durations.length > 0 && `(${activeFilters.durations.length})`} <ChevronDown className="h-3 w-3" />
              </Button>
              {openFilterMenu === 'duration' && (
                <div className="absolute top-full mt-2 left-0 w-48 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg shadow-xl p-3 z-50">
                  <div className="space-y-2">
                    {[
                      { label: '< 6 meses', value: '<6' },
                      { label: '6 - 12 meses', value: '6-12' },
                      { label: '> 12 meses', value: '>12' },
                    ].map(dur => (
                      <label key={dur.value} className="flex items-center gap-2 cursor-pointer hover:bg-slate-50 dark:hover:bg-zinc-800 p-1 rounded transition-colors" onClick={() => toggleFilter('durations', dur.value)}>
                        <div 
                          className={cn(
                            "w-4 h-4 rounded border flex items-center justify-center transition-colors",
                            activeFilters.durations.includes(dur.value) ? "bg-indigo-600 border-indigo-600 text-white" : "border-slate-300"
                          )}
                        >
                          {activeFilters.durations.includes(dur.value) && <Check className="h-3 w-3" />}
                        </div>
                        <span className="text-sm">{dur.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {(activeFilters.modes.length > 0 || activeFilters.durations.length > 0 || activeFilters.types.length > 0 || activeFilters.priceMin !== "" || activeFilters.priceMax !== "") && (
              <Button 
                variant="ghost" 
                size="sm" 
                className="rounded-full text-xs h-8 px-3 gap-1.5 text-slate-500 hover:text-indigo-600"
                onClick={clearFilters}
              >
                <X className="h-3 w-3" /> Limpiar
              </Button>
            )}
          </div>
        </div>
      </div>

      <main className="max-w-5xl mx-auto px-4 py-10">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-sm font-medium text-slate-500 uppercase tracking-wider">
            {loading ? "Buscando..." : `${filteredCourses.length} opciones encontradas`}
          </h2>
          {!loading && (
            <div className="flex items-center gap-1 text-xs text-slate-500">
              <Navigation2 className="h-3 w-3 fill-slate-500" />
              Ordenado por cercanía
            </div>
          )}
        </div>

        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {filteredCourses.map((course) => (
              <Card key={course.id} className={cn(
                "group overflow-hidden border-slate-200 dark:border-zinc-800 hover:shadow-md hover:border-slate-300 dark:hover:border-zinc-700 transition-all p-0",
                selectedForCompare.find(c => c.id === course.id) && "ring-2 ring-indigo-500 border-indigo-500"
              )}>
                <div className="flex flex-col md:flex-row items-stretch md:items-center p-4 md:p-5 gap-4">
                  {/* Selection Checkbox */}
                  <div className="hidden md:flex items-center pr-2">
                    <button 
                      onClick={() => toggleCompare(course)}
                      className={cn(
                        "w-5 h-5 rounded border flex items-center justify-center transition-colors",
                        selectedForCompare.find(c => c.id === course.id) 
                          ? "bg-indigo-600 border-indigo-600 text-white" 
                          : "border-slate-300 hover:border-indigo-400"
                      )}
                    >
                      {selectedForCompare.find(c => c.id === course.id) && <CheckCircle2 className="h-4 w-4" />}
                    </button>
                  </div>

                  {/* Institution & Mode */}
                  <div className="flex flex-col gap-1 min-w-[160px]">
                    <div className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 truncate">
                      {course.institution_name}
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="bg-slate-100 dark:bg-zinc-800 text-[10px] font-bold h-5 px-1.5 border-0 rounded text-slate-600 dark:text-zinc-400">
                        {course.mode.toUpperCase()}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] font-bold h-5 px-1.5 border-indigo-200 text-indigo-600 dark:text-indigo-400">
                        {course.category.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  {/* Divider for mobile */}
                  <div className="h-px w-full bg-slate-100 dark:bg-zinc-800 md:hidden" />

                  {/* Course Info */}
                  <div className="flex-1 min-w-0">
                    <Link href={`/courses/${course.slug}`}>
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white truncate mb-1 group-hover:text-indigo-600 transition-colors cursor-pointer">
                        {course.name}
                      </h3>
                    </Link>
                    <div className="flex flex-wrap gap-x-5 gap-y-1 text-sm text-slate-500 dark:text-zinc-400">
                      <div className="flex items-center gap-1.5">
                        <MapPin className="h-3.5 w-3.5 shrink-0" />
                        <span className="truncate max-w-[200px]">{course.address}</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Clock className="h-3.5 w-3.5 shrink-0" />
                        <span>{course.duration || "N/A"}</span>
                      </div>
                      {course.distance_km != null && (
                        <div className="flex items-center gap-1.5 text-indigo-600 dark:text-indigo-400 font-medium">
                          <Navigation2 className="h-3 w-3 fill-current" />
                          <span>{course.distance_km.toFixed(1)} km</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Price & Action */}
                  <div className="flex items-center md:items-end md:flex-col justify-between md:justify-center gap-4 min-w-[140px] md:pl-6 md:border-l border-slate-100 dark:border-zinc-800">
                    <div className="flex flex-col md:items-end">
                      <div className="text-xl font-bold text-slate-900 dark:text-white">
                        {course.price_pen === null ? "Consultar" : course.price_pen === 0 ? "Gratis" : `S/ ${course.price_pen.toLocaleString()}`}
                      </div>
                      <div className="text-[10px] text-slate-400 uppercase font-medium mb-2">Precio total</div>
                      
                      {course.roi_months != null && (
                        <div className="flex flex-col md:items-end border-t border-slate-100 dark:border-zinc-800 pt-2 w-full">
                          <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                            <TrendingUp className="h-3.5 w-3.5" />
                            {course.roi_months.toFixed(1)} meses
                          </div>
                          <div className="text-[10px] text-slate-400 uppercase font-medium">Recupero ROI</div>
                        </div>
                      )}
                    </div>
                    <Link 
                      href={`/courses/${course.slug}`}
                      className={cn(
                        buttonVariants({ size: "sm", variant: "ghost" }),
                        "h-9 px-4 text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 gap-1.5 rounded-full border border-indigo-100 dark:border-indigo-900/50"
                      )}
                    >
                      Detalle <ExternalLink className="h-3 w-3" />
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Floating Comparison Bar */}
        {selectedForCompare.length > 0 && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-700 shadow-2xl rounded-2xl px-6 py-4 flex items-center gap-8 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center gap-4">
              <div className="flex -space-x-3">
                {selectedForCompare.map(c => (
                  <div key={c.id} className="w-10 h-10 rounded-full border-2 border-white dark:border-zinc-900 bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center text-xs font-bold text-indigo-600 dark:text-indigo-400">
                    {c.institution_name.substring(0, 2)}
                  </div>
                ))}
              </div>
              <div>
                <div className="text-sm font-bold text-slate-900 dark:text-white">
                  {selectedForCompare.length} programa{selectedForCompare.length > 1 ? "s" : ""} seleccionado{selectedForCompare.length > 1 ? "s" : ""}
                </div>
                <div className="text-[10px] text-slate-500 uppercase font-medium">Compara hasta 3 opciones</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Button 
                variant="ghost" 
                size="sm" 
                className="text-slate-500 hover:text-red-500"
                onClick={() => setSelectedForCompare([])}
              >
                Limpiar
              </Button>
              <Link href={{
                pathname: '/compare',
                query: { ids: selectedForCompare.map(c => c.id).join(',') }
              }}>
                <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full px-6">
                  Comparar ahora
                </Button>
              </Link>
            </div>
          </div>
        )}

        {!loading && filteredCourses.length === 0 && (
          <div className="text-center py-24 bg-white dark:bg-zinc-900 rounded-xl border border-dashed border-slate-300 dark:border-zinc-700">
            <Search className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-1">No hay resultados</h3>
            <p className="text-slate-500 dark:text-zinc-400">Intenta ajustar los términos de búsqueda o filtros.</p>
            <Button variant="link" className="text-indigo-600 mt-2" onClick={() => { setSearchTerm(""); clearFilters(); fetchCourses(""); }}>
              Ver todos los programas
            </Button>
          </div>
        )}
      </main>
      
      <footer className="max-w-5xl mx-auto px-4 py-12 border-t border-slate-200 dark:border-zinc-800 text-center text-slate-400 text-sm">
        <p>© 2026 Yachachiy.ai - Democratizando la educación superior en el Perú</p>
      </footer>
    </div>
  );
}
