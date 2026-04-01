"use client";

import { useEffect, useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Clock, TrendingUp, ChevronDown, X, GraduationCap, ArrowRight, CheckCircle2, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { SUPABASE_URL, SUPABASE_ANON_KEY, cleanSlug, parseDurationToMonths, type Course, type Institution } from "@/lib/supabase";

export default function Home() {
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCourseForInfo, setSelectedCourseForInfo] = useState<Course | null>(null);
  const [modalType, setModalType] = useState<'recommendation' | 'info'>('recommendation');

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    whatsapp: "",
    area_interest: "",
    budget: "",
    modality: "Remoto",
    description: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const openModal = (type: 'recommendation' | 'info', course: Course | null = null) => {
    setModalType(type);
    setSelectedCourseForInfo(course);
    setIsModalOpen(true);
    setIsSuccess(false);
  };

  const handleSubmitLead = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      const leadData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        whatsapp: formData.whatsapp,
        type: modalType,
        course_id: selectedCourseForInfo?.id || null,
        area_interest: formData.area_interest || (modalType === 'info' ? selectedCourseForInfo?.category : ""),
        budget: formData.budget ? parseFloat(formData.budget.replace(/[^0-9.]/g, '')) : null,
        modality: formData.modality,
        description: formData.description
      };

      const response = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify(leadData)
      });

      if (response.ok) {
        setIsSuccess(true);
        setTimeout(() => {
          setIsModalOpen(false);
          setIsSuccess(false);
          setFormData({
            first_name: "",
            last_name: "",
            email: "",
            whatsapp: "",
            area_interest: "",
            budget: "",
            modality: "Remoto",
            description: ""
          });
        }, 2500);
      }
    } catch (error) {
      console.error("Error submitting lead:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const [selectedCategory, setSelectedCategory] = useState<string>("Todos");
  const [compareList, setCompareList] = useState<Course[]>([]);
  
  const categories = ["Todos", "Curso", "Maestría", "Diplomado", "Postgrado"];

  const toggleCompare = (course: Course) => {
    setCompareList(prev => {
      if (prev.find(c => c.id === course.id)) {
        return prev.filter(c => c.id !== course.id);
      }
      if (prev.length >= 3) return prev;
      return [...prev, course];
    });
  };

  const [activeFilters, setActiveFilters] = useState({
    priceMin: "",
    priceMax: "",
    modes: [] as string[],
    durations: [] as string[],
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

        const courseRes = await fetch(`${SUPABASE_URL}/rest/v1/courses?select=*&order=created_at.desc`, { headers });
        const courseData = await courseRes.json();
        
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

  const filteredCourses = useMemo(() => {
    let result = [...allCourses];

    if (searchTerm) {
      const normalize = (text: string) => 
        text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
      
      const normalizedSearch = normalize(searchTerm);

      result = result.filter(c => 
        (normalize(c.name || "").includes(normalizedSearch) || 
         normalize(c.institution_name || "").includes(normalizedSearch))
      );
    }

    if (selectedCategory !== "Todos") {
      result = result.filter(c => c.category === selectedCategory);
    }

    return result.filter((course) => {
      if (activeFilters.modes.length > 0 && !activeFilters.modes.includes(course.mode)) return false;
      
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
  }, [allCourses, activeFilters, searchTerm, selectedCategory]);

  return (
    <div className="min-h-screen bg-white text-brand-slate font-sans selection:bg-brand-mint/30">
      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-6 pt-12 pb-16">
        <div className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-brand-slate via-[#1E293B] to-brand-blue p-10 md:p-20 text-white shadow-2xl">
          <div className="relative z-10 max-w-3xl">
            <Badge className="mb-6 bg-brand-mint/20 text-brand-mint border-brand-mint/30 py-1.5 px-4 rounded-full text-xs font-bold uppercase tracking-widest">Yachachiy · Data-driven education</Badge>
            <h1 className="text-4xl font-bold leading-[1.1] md:text-6xl lg:text-7xl">
              Elige tu próximo programa con <span className="text-brand-mint">datos reales</span>, no con promesas.
            </h1>
            <p className="mt-8 text-lg md:text-xl text-blue-100/80 leading-relaxed max-w-2xl">
              Compara contenido, docentes, modalidad y ROI real de la oferta educativa tech en un solo lugar. Transparencia total para tu futuro.
            </p>
            <div className="mt-12 flex flex-col sm:flex-row gap-4 items-stretch sm:items-center">
              <div className="relative flex-1 group">
                <Search className="absolute left-5 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400 group-focus-within:text-brand-blue transition-colors" />
                <Input 
                  placeholder="¿Qué quieres estudiar? (Ej: Data Science, MBA)" 
                  className="pl-14 h-16 bg-white text-brand-slate rounded-2xl border-0 text-lg shadow-xl focus:ring-4 focus:ring-brand-mint/30"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button onClick={() => scrollToSection('programas')} size="lg" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold rounded-2xl px-10 h-16 shadow-xl shadow-brand-mint/30 border-0 text-lg transition-transform hover:scale-[1.02] active:scale-[0.98]">Explorar</Button>
            </div>
            <div className="mt-8 flex items-center gap-6 text-sm text-blue-100/60 font-medium">
              <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-brand-mint" /> Datos verificados</div>
              <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-brand-mint" /> Actualizado hoy</div>
              <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-brand-mint" /> 100% Gratuito</div>
            </div>
          </div>
          {/* Abstract decor */}
          <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-brand-blue/20 rounded-full blur-[100px]" />
          <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-80 h-80 bg-brand-mint/10 rounded-full blur-[80px]" />
        </div>
      </section>

      {/* Filter Bar */}
      <div id="programas" className="sticky top-[73px] z-40 bg-white/80 backdrop-blur-md border-b border-brand-gray/40 py-6">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-sm font-bold text-slate-400 uppercase tracking-widest mr-2">Categorías:</span>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={cn(
                  "px-6 py-2.5 rounded-2xl text-sm font-bold transition-all border-2",
                  selectedCategory === cat 
                    ? "bg-brand-blue border-brand-blue text-white shadow-lg shadow-brand-blue/20" 
                    : "bg-white border-brand-gray/60 text-slate-600 hover:border-brand-blue/40 hover:text-brand-blue"
                )}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Results */}
      <main className="mx-auto max-w-6xl px-6 py-16">
        <div className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h2 className="text-4xl font-bold tracking-tight text-brand-slate">Programas comparables</h2>
            <p className="text-slate-500 text-lg mt-2 font-medium">Hemos encontrado {filteredCourses.length} opciones analizadas para ti.</p>
          </div>
          <div className="flex items-center gap-3 bg-slate-100 p-1.5 rounded-2xl">
            <button 
              onClick={() => setViewMode('grid')}
              className={cn("px-4 py-2 rounded-xl text-xs font-bold transition-all", viewMode === 'grid' ? "bg-white text-brand-blue shadow-sm" : "text-slate-500 hover:text-slate-700")}
            >Mosaico</button>
            <button 
              onClick={() => setViewMode('list')}
              className={cn("px-4 py-2 rounded-xl text-xs font-bold transition-all", viewMode === 'list' ? "bg-white text-brand-blue shadow-sm" : "text-slate-500 hover:text-slate-700")}
            >Lista</button>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-pulse">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-80 bg-slate-100 rounded-3xl" />)}
          </div>
        ) : filteredCourses.length > 0 ? (
          <div className={cn("grid gap-8", viewMode === 'grid' ? "md:grid-cols-2" : "grid-cols-1")}>
            {filteredCourses.map((course) => (
              <article key={course.id} className="group relative flex flex-col justify-between rounded-[2rem] border border-brand-gray/60 bg-white p-8 shadow-premium transition-all hover:-translate-y-1 hover:shadow-2xl hover:border-brand-blue/30">
                {course.roi_months && course.roi_months <= 12 && (
                  <div className="absolute -top-4 -right-4 bg-brand-mint text-brand-slate text-[10px] font-black uppercase tracking-tighter px-4 py-2 rounded-xl shadow-lg border-2 border-white z-10 animate-bounce">
                    Alto ROI: {course.roi_months} meses
                  </div>
                )}
                
                <div>
                  <div className="flex items-center gap-3 mb-6">
                    <Badge className="bg-slate-100 text-slate-600 border-0 px-4 py-1.5 rounded-full font-bold text-[11px] uppercase tracking-wide">{course.category || "General"}</Badge>
                    <Badge className="bg-brand-blue/5 text-brand-blue border-brand-blue/10 px-4 py-1.5 rounded-full font-bold text-[11px] uppercase tracking-wide">{course.mode}</Badge>
                  </div>
                  
                  <Link href={`/courses/${cleanSlug(course.slug)}`}>
                    <h3 className="text-2xl font-bold text-brand-slate leading-tight group-hover:text-brand-blue transition-colors mb-3">
                      {course.name}
                    </h3>
                  </Link>
                  <p className="text-slate-500 font-semibold flex items-center gap-2 mb-8">
                    <GraduationCap className="h-5 w-5 text-brand-blue" /> {course.institution_name}
                  </p>

                  <div className="grid grid-cols-2 gap-8 p-6 bg-slate-50 rounded-2xl border border-slate-100">
                    <div className="space-y-1">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.15em]">Duración</span>
                      <p className="font-bold text-slate-700 flex items-center gap-2">
                        <Clock className="h-4 w-4 text-slate-400" /> {course.duration || "Consultar"}
                      </p>
                    </div>
                    <div className="space-y-1">
                      <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.15em]">Inversión</span>
                      <p className="font-black text-brand-blue text-xl">
                        {course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "S/ Consultar"}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="mt-10 flex flex-col gap-3">
                  <div className="flex gap-4">
                    <Link href={`/courses/${cleanSlug(course.slug)}`} className="flex-1 rounded-2xl border-2 border-brand-blue px-6 py-4 text-center text-sm font-black text-brand-blue hover:bg-brand-blue hover:text-white transition-all shadow-sm">
                      Ver detalle
                    </Link>
                    <Button onClick={() => openModal('info', course)} className="flex-1 rounded-2xl bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-black h-auto py-4 text-sm border-0 shadow-lg shadow-brand-mint/20">
                      Quiero info
                    </Button>
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={() => toggleCompare(course)}
                    className={cn(
                      "w-full rounded-2xl border-2 font-bold py-6 transition-all",
                      compareList.find(c => c.id === course.id)
                        ? "bg-brand-blue border-brand-blue text-white hover:bg-brand-blue/90"
                        : "border-brand-gray/60 text-slate-500 hover:border-brand-blue hover:text-brand-blue"
                    )}
                  >
                    {compareList.find(c => c.id === course.id) ? "✓ Seleccionado" : "+ Comparar"}
                  </Button>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="py-24 text-center border-4 border-dashed border-slate-100 rounded-[3rem]">
            <div className="inline-flex h-20 w-20 items-center justify-center rounded-full bg-slate-50 mb-6">
              <Search className="h-10 w-10 text-slate-300" />
            </div>
            <h3 className="text-2xl font-bold text-brand-slate mb-3">No hay coincidencias</h3>
            <p className="text-slate-500 mb-8 max-w-md mx-auto">Prueba ajustando los filtros o realizando una búsqueda más general.</p>
            <Button variant="outline" onClick={() => { setSearchTerm(""); setSelectedCategory("Todos"); }} className="rounded-2xl px-8 h-12 font-bold border-2">Limpiar todo</Button>
          </div>
        )}
      </main>

      {/* Floating Comparison Bar */}
      {compareList.length > 0 && (
        <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-[60] w-[90%] max-w-2xl animate-in slide-in-from-bottom-10 duration-500">
          <div className="bg-brand-slate/95 backdrop-blur-xl rounded-[2.5rem] p-4 shadow-2xl border border-white/10 flex items-center justify-between gap-6">
            <div className="flex items-center gap-4 pl-4">
              <div className="flex -space-x-3">
                {compareList.map((c, i) => (
                  <div key={c.id} className="h-12 w-12 rounded-full border-2 border-brand-slate bg-brand-blue flex items-center justify-center text-white font-bold text-xs overflow-hidden shadow-lg">
                    {c.name.charAt(0)}
                  </div>
                ))}
                {[...Array(3 - compareList.length)].map((_, i) => (
                  <div key={i} className="h-12 w-12 rounded-full border-2 border-dashed border-white/20 bg-white/5 flex items-center justify-center text-white/20 font-bold text-xs">
                    +
                  </div>
                ))}
              </div>
              <div>
                <p className="text-white font-bold text-sm">{compareList.length} seleccionados</p>
                <p className="text-white/50 text-[10px] font-medium uppercase tracking-wider">Máximo 3 programas</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setCompareList([])}
                className="text-white/40 hover:text-white text-xs font-bold px-4"
              >
                Limpiar
              </button>
              <Link href={`/compare?ids=${compareList.map(c => c.id).join(",")}`}>
                <Button className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-black rounded-2xl px-8 h-14 border-0 shadow-lg shadow-brand-mint/20">
                  Comparar ahora
                </Button>
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* How it Works Section */}
      <section id="como-funciona" className="bg-slate-50 py-24 scroll-mt-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl font-bold mb-6">Cómo Funciona</h2>
            <p className="text-slate-500 text-lg font-medium">Tres pasos simples para asegurar tu inversión educativa.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-10">
            {[
              { title: "Busca", desc: "Encuentra programas por categoría, precio o institución en nuestro catálogo verificado.", icon: Search },
              { title: "Compara", desc: "Analiza el ROI estimado, temarios y duración para elegir lo que realmente te sirve.", icon: TrendingUp },
              { title: "Decide", desc: "Contacta con un asesor o inscríbete directamente con total confianza.", icon: CheckCircle2 }
            ].map((step, idx) => (
              <div key={idx} className="bg-white p-10 rounded-[2.5rem] shadow-premium border border-brand-gray/40 relative group hover:border-brand-blue/30 transition-colors">
                <div className="absolute -top-6 left-10 h-12 w-12 bg-brand-blue text-white rounded-2xl flex items-center justify-center font-bold text-xl shadow-lg shadow-brand-blue/20">{idx + 1}</div>
                <div className="mt-4">
                  <step.icon className="h-10 w-10 text-brand-blue mb-6 opacity-80" />
                  <h3 className="text-2xl font-bold mb-4">{step.title}</h3>
                  <p className="text-slate-500 leading-relaxed font-medium">{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About Us Section */}
      <section id="nosotros" className="py-24 scroll-mt-20 overflow-hidden relative">
        <div className="mx-auto max-w-6xl px-6">
          <div className="flex flex-col md:flex-row items-center gap-20">
            <div className="flex-1 space-y-8">
              <Badge className="bg-brand-blue text-white px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-[0.2em] border-0">Nuestra Misión</Badge>
              <h2 className="text-4xl md:text-5xl font-bold leading-tight">Yachachiy.ai nace para <span className="text-brand-blue">democratizar</span> la información educativa.</h2>
              <p className="text-xl text-slate-500 leading-relaxed font-medium">
                En un mercado saturado de promesas, nosotros aportamos claridad. Consolidamos los datos reales de las instituciones peruanas para que tomes decisiones basadas en el retorno de inversión y calidad real.
              </p>
              <div className="grid sm:grid-cols-2 gap-6 pt-4">
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50">
                  <div className="h-10 w-10 rounded-xl bg-white flex items-center justify-center shadow-sm"><CheckCircle2 className="h-6 w-6 text-brand-mint" /></div>
                  <p className="font-bold text-sm text-slate-600">Transparencia Total</p>
                </div>
                <div className="flex items-start gap-4 p-4 rounded-2xl bg-slate-50">
                  <div className="h-10 w-10 rounded-xl bg-white flex items-center justify-center shadow-sm"><CheckCircle2 className="h-6 w-6 text-brand-mint" /></div>
                  <p className="font-bold text-sm text-slate-600">Datos Actualizados</p>
                </div>
              </div>
            </div>
            <div className="flex-1 relative">
              <div className="relative z-10 rounded-[3rem] overflow-hidden shadow-2xl bg-gradient-to-tr from-brand-slate to-brand-blue aspect-square flex items-center justify-center p-12">
                 <div className="text-center space-y-4">
                    <p className="text-6xl font-black text-brand-mint">+500</p>
                    <p className="text-white font-bold uppercase tracking-widest text-sm opacity-80">Programas Analizados</p>
                 </div>
              </div>
              <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-brand-mint rounded-full blur-[60px] opacity-40" />
            </div>
          </div>
        </div>
      </section>

      {/* Recommendation CTA */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="rounded-[3rem] bg-brand-slate p-12 text-center text-white relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">¿Listo para elegir con confianza?</h2>
            <p className="text-blue-100/70 text-lg mb-10 max-w-2xl mx-auto font-medium">Recibe una recomendación rápida basada en tus objetivos y tu momento ideal para empezar.</p>
            <Button onClick={() => openModal('recommendation')} size="lg" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-black rounded-2xl px-12 h-16 shadow-xl shadow-brand-mint/20 border-0 text-lg transition-transform hover:scale-105">
              Quiero mi recomendación
            </Button>
          </div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-brand-blue/20 via-transparent to-transparent" />
        </div>
      </section>

      {/* Premium Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-brand-slate/80 backdrop-blur-xl animate-in fade-in duration-300">
          <div className="bg-white w-full max-w-2xl rounded-[3rem] shadow-2xl overflow-hidden relative animate-in zoom-in-95 duration-300 max-h-[90vh] overflow-y-auto">
            <button 
              onClick={() => setIsModalOpen(false)} 
              className="absolute top-8 right-8 p-3 hover:bg-slate-100 rounded-full transition-colors z-20"
            >
              <X className="h-6 w-6 text-slate-400" />
            </button>
            
            <div className="flex flex-col md:flex-row">
              <div className="hidden md:flex md:w-48 bg-brand-blue p-10 flex-col justify-between text-white">
                <div className="h-10 w-10 bg-white/20 rounded-xl backdrop-blur-md flex items-center justify-center font-bold">Y</div>
                <div className="space-y-4">
                  <div className="h-1 w-8 bg-brand-mint rounded-full" />
                  <p className="text-[10px] font-black uppercase tracking-widest leading-relaxed opacity-70">
                    {modalType === 'info' ? 'Consulta de Programa' : 'Asesoría de IA'}
                  </p>
                </div>
              </div>
              
              <div className="flex-1 p-10 md:p-14">
                <Badge className="bg-brand-mint/10 text-brand-mint border-brand-mint/20 px-3 py-1 rounded-full text-[10px] font-black uppercase mb-6">
                  {modalType === 'info' ? 'Interés en Curso' : 'Recomendación Algorítmica'}
                </Badge>
                
                <h3 className="text-3xl font-bold mb-4 text-brand-slate leading-tight">
                  {modalType === 'info' 
                    ? `Más info sobre: ${selectedCourseForInfo?.name}`
                    : 'Obtén tu recomendación ideal'}
                </h3>
                
                <p className="text-slate-500 mb-8 leading-relaxed font-medium text-sm">
                  {modalType === 'info'
                    ? 'Déjanos tus datos para que un asesor te brinde detalles específicos de este programa y otras opciones similares.'
                    : 'Completa tu perfil para que nuestro algoritmo encuentre los programas que mejor se adaptan a tus metas y presupuesto.'}
                </p>
                
                {isSuccess ? (
                  <div className="py-12 text-center animate-in zoom-in duration-500">
                    <CheckCircle2 className="h-20 w-20 text-emerald-500 mx-auto mb-6" />
                    <h3 className="text-3xl font-bold text-brand-slate">¡Solicitud recibida!</h3>
                    <p className="text-slate-500 mt-4 text-lg">En breve un especialista te contactará.</p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmitLead}>
                    <div className="space-y-5 mb-10">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Nombres</label>
                          <Input 
                            required
                            placeholder="Ej: Juan" 
                            className="h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold" 
                            value={formData.first_name}
                            onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                          />
                        </div>
                        <div className="space-y-1.5">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Apellidos</label>
                          <Input 
                            required
                            placeholder="Ej: Pérez" 
                            className="h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold" 
                            value={formData.last_name}
                            onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Email</label>
                          <Input 
                            required
                            type="email" 
                            placeholder="juan@ejemplo.com" 
                            className="h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold" 
                            value={formData.email}
                            onChange={(e) => setFormData({...formData, email: e.target.value})}
                          />
                        </div>
                        <div className="space-y-1.5">
                          <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">WhatsApp</label>
                          <Input 
                            required
                            placeholder="+51 987 654 321" 
                            className="h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold" 
                            value={formData.whatsapp}
                            onChange={(e) => setFormData({...formData, whatsapp: e.target.value})}
                          />
                        </div>
                      </div>

                      {modalType === 'recommendation' && (
                        <>
                          <div className="space-y-1.5">
                            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">¿En qué área estás interesado?</label>
                            <Input 
                              placeholder="Ej: Data Science, Marketing Digital" 
                              className="h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold" 
                              value={formData.area_interest}
                              onChange={(e) => setFormData({...formData, area_interest: e.target.value})}
                            />
                          </div>
                          
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-1.5">
                              <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Presupuesto máx.</label>
                              <Input 
                                placeholder="S/ 5,000" 
                                className="h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold" 
                                value={formData.budget}
                                onChange={(e) => setFormData({...formData, budget: e.target.value})}
                              />
                            </div>
                            <div className="space-y-1.5">
                              <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Modalidad</label>
                              <select 
                                className="w-full h-12 rounded-2xl bg-slate-50 border-0 px-6 font-semibold text-sm appearance-none focus:ring-4 focus:ring-brand-blue/10"
                                value={formData.modality}
                                onChange={(e) => setFormData({...formData, modality: e.target.value})}
                              >
                                <option>Remoto</option>
                                <option>Presencial</option>
                                <option>Virtual (Asíncrono)</option>
                                <option>Híbrido</option>
                              </select>
                            </div>
                          </div>

                          <div className="space-y-1.5">
                            <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Cuéntanos más</label>
                            <textarea 
                              placeholder="Breve descripción de tus metas..."
                              className="w-full h-24 rounded-2xl bg-slate-50 border-0 p-6 font-semibold text-sm focus:ring-4 focus:ring-brand-blue/10 resize-none"
                              value={formData.description}
                              onChange={(e) => setFormData({...formData, description: e.target.value})}
                            ></textarea>
                          </div>
                        </>
                      )}
                    </div>
                    
                    <Button 
                      disabled={isSubmitting}
                      type="submit"
                      className="w-full h-16 bg-brand-blue hover:bg-brand-blue/90 text-white font-black rounded-2xl border-0 shadow-2xl shadow-brand-blue/20 text-lg"
                    >
                      {isSubmitting ? (
                        <div className="flex items-center gap-2">
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          PROCESANDO...
                        </div>
                      ) : (
                        modalType === 'info' ? 'SOLICITAR DETALLES' : 'GENERAR MI RECOMENDACIÓN'
                      )}
                    </Button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
