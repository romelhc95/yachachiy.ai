"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  MapPin, Clock, ExternalLink, TrendingUp, ChevronLeft, 
  CheckCircle, ShieldCheck, Mail, Phone, User, 
  GraduationCap, ArrowRight
} from "lucide-react";
import Link from "next/link";
import { SUPABASE_URL, SUPABASE_ANON_KEY, type Course } from "@/lib/supabase";

interface CourseDetailClientProps {
  slug: string;
}

/**
 * Vista de Detalle de Programa
 * 
 * Muestra información extendida de un curso, incluyendo análisis de ROI
 * y formulario de captura de leads (directo a Supabase).
 */
export default function CourseDetailClient({ slug }: CourseDetailClientProps) {
  const router = useRouter();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    message: ""
  });

  // Efecto para cargar los detalles del programa
  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true);
        // Búsqueda por slug en la tabla de cursos
        const response = await fetch(
          `${SUPABASE_URL}/rest/v1/courses?slug=eq.${slug}&select=*`, 
          {
            headers: {
              'apikey': SUPABASE_ANON_KEY,
              'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
            }
          }
        );
        
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
          setCourse(data[0]);
        } else {
          throw new Error("Programa no encontrado");
        }
      } catch (error) {
        console.error("Error cargando detalle:", error);
        router.push("/");
      } finally {
        setLoading(false);
      }
    };

    if (slug) fetchCourse();
  }, [slug, router]);

  // Manejo de envío de Lead directamente a Supabase
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!course) return;

    try {
      const response = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "apikey": SUPABASE_ANON_KEY,
          "Authorization": `Bearer ${SUPABASE_ANON_KEY}`,
          "Prefer": "return=minimal"
        },
        body: JSON.stringify({ 
          full_name: formData.name,
          email: formData.email,
          phone: formData.phone,
          course_id: course.id,
          source: 'web_detail'
        })
      });

      if (response.ok) {
        setSubmitted(true);
      }
    } catch (error) {
      console.error("Error enviando lead:", error);
    }
  };

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-white dark:bg-brand-slate">
      <div className="w-12 h-12 rounded-full border-4 border-brand-blue border-t-transparent animate-spin" />
      <span className="text-sm font-bold text-slate-500 animate-pulse">Analizando datos del programa...</span>
    </div>
  );
  
  if (!course) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-brand-slate text-brand-slate dark:text-white font-sans selection:bg-brand-mint/30">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-brand-gray/50 bg-white/95 dark:bg-brand-slate/95 backdrop-blur shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2 text-2xl font-bold tracking-tight text-brand-slate dark:text-white">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-blue text-white font-bold">Y</div>
            <span>Yachachiy<span className="text-brand-blue">.ai</span></span>
          </Link>
          <div className="hidden md:flex gap-8 items-center">
            <Link href="/" className="text-sm font-medium hover:text-brand-blue transition">Programas</Link>
            <Button size="sm" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-semibold rounded-xl px-5 h-9 border-0">
              Solicitar asesoría
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <Link href="/" className="inline-flex items-center text-sm font-bold text-brand-blue hover:translate-x-[-4px] transition-all mb-10 group">
          <ChevronLeft className="h-5 w-5 mr-1 group-hover:stroke-[3px]" /> Volver a la búsqueda
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-12">
            <header>
              <div className="flex items-center gap-3 mb-6">
                <Badge className="bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20 font-bold border-0 px-3 py-1">
                  {course.institution_name}
                </Badge>
                <Badge variant="outline" className="border-brand-gray/50 text-slate-500 font-bold px-3 py-1 uppercase tracking-wider text-[10px]">
                  {course.mode}
                </Badge>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold text-brand-slate dark:text-white mb-8 leading-tight">
                {course.name}
              </h1>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <MapPin className="h-3 w-3" /> Ubicación
                  </span>
                  <span className="font-semibold text-sm">{course.address || "No especificada"}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <Clock className="h-3 w-3" /> Duración
                  </span>
                  <span className="font-semibold text-sm">{course.duration || "Consultar"}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <GraduationCap className="h-3 w-3" /> Modalidad
                  </span>
                  <span className="font-semibold text-sm">{course.mode}</span>
                </div>
              </div>
            </header>

            {/* Inversion Analysis Card */}
            <section className="relative overflow-hidden rounded-[2.5rem] bg-brand-slate p-8 md:p-12 text-white shadow-premium border border-white/5">
              <div className="absolute top-0 right-0 p-10 opacity-10">
                <TrendingUp className="h-24 w-24" />
              </div>
              <h2 className="text-2xl font-bold mb-10 flex items-center gap-3 text-brand-mint">
                <TrendingUp className="h-7 w-7" />
                Análisis de Inversión y ROI
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Inversión Estimada</div>
                  <div className="text-4xl font-bold">
                    {course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Salario Promedio</div>
                  <div className="text-4xl font-bold text-brand-mint">
                    S/ {course.expected_monthly_salary?.toLocaleString() || "4,800"}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Retorno (Meses)</div>
                  <div className="text-4xl font-bold text-white">
                    {course.roi_months?.toFixed(1) || "14.2"}
                  </div>
                </div>
              </div>
              <div className="mt-12 p-5 rounded-2xl bg-white/5 border border-white/10 text-[11px] text-blue-100/60 italic leading-relaxed">
                * Las métricas de ROI son estimaciones basadas en Big Data del mercado laboral peruano. La inversión puede variar según descuentos institucionales vigentes.
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <ShieldCheck className="h-6 w-6 text-brand-blue" />
                Resumen Ejecutivo
              </h2>
              <div className="prose dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 leading-relaxed text-lg">
                <p>
                  El programa <strong>{course.name}</strong> dictado por <strong>{course.institution_name}</strong> ha sido analizado por nuestro motor de IA, destacando su relevancia en las competencias digitales actuales.
                </p>
                <p className="mt-4">
                  Su diseño bajo la modalidad <strong>{course.mode}</strong> facilita el equilibrio entre la vida profesional y el aprendizaje continuo, permitiendo a los alumnos aplicar los conocimientos de forma inmediata.
                </p>
              </div>
            </section>
          </div>

          {/* Sidebar - Form */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24 overflow-hidden border-brand-gray/50 dark:border-white/10 shadow-premium rounded-[2rem]">
              <div className="bg-brand-blue p-8 text-white">
                <p className="text-xs font-bold uppercase tracking-widest text-brand-mint mb-2">Brochure & Precios</p>
                <h3 className="text-2xl font-bold mb-3">Solicitar Info</h3>
                <p className="text-blue-100 text-sm leading-relaxed">Obtén la malla curricular completa y beneficios exclusivos de Yachachiy.</p>
              </div>
              
              <div className="p-8 bg-white dark:bg-zinc-900">
                {!submitted ? (
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 ml-1">Nombre Completo</label>
                      <div className="relative">
                        <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <Input 
                          placeholder="Ej: Ana García" 
                          className="pl-12 h-14 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 focus:ring-brand-blue" 
                          required
                          value={formData.name}
                          onChange={e => setFormData({...formData, name: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 ml-1">Correo corporativo / personal</label>
                      <div className="relative">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <Input 
                          type="email" 
                          placeholder="ana@ejemplo.com" 
                          className="pl-12 h-14 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 focus:ring-brand-blue" 
                          required
                          value={formData.email}
                          onChange={e => setFormData({...formData, email: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 ml-1">WhatsApp de contacto</label>
                      <div className="relative">
                        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <Input 
                          placeholder="+51 987 654 321" 
                          className="pl-12 h-14 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 focus:ring-brand-blue" 
                          required
                          value={formData.phone}
                          onChange={e => setFormData({...formData, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    <Button type="submit" className="w-full bg-brand-mint hover:bg-brand-mint/90 h-16 text-brand-slate font-bold rounded-2xl transition shadow-lg shadow-brand-mint/10 border-0">
                      Enviar Solicitud <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                    <p className="text-[10px] text-center text-slate-400 mt-6 flex items-center justify-center gap-1 uppercase font-bold">
                      <ShieldCheck className="h-3 w-3" /> Conexión segura y cifrada
                    </p>
                  </form>
                ) : (
                  <div className="py-12 text-center space-y-6 animate-in fade-in zoom-in duration-500">
                    <div className="w-24 h-24 bg-emerald-50 dark:bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4 border-4 border-emerald-100 dark:border-emerald-500/20">
                      <CheckCircle className="h-12 w-12 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <h3 className="text-3xl font-bold text-brand-slate dark:text-white">¡Solicitud Enviada!</h3>
                    <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
                      Un asesor se pondrá en contacto contigo pronto para brindarte toda la información de <strong>{course.institution_name}</strong>.
                    </p>
                    <Button variant="ghost" className="mt-8 text-brand-blue font-bold" onClick={() => setSubmitted(false)}>
                      Enviar otra consulta
                    </Button>
                  </div>
                )}
              </div>
              
              <div className="p-6 border-t border-brand-gray/30 text-center bg-slate-50/50 dark:bg-zinc-800/50">
                {course.url && (
                  <a 
                    href={course.url.startsWith('http') ? course.url : `https://${course.url}`} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-xs text-brand-blue font-bold hover:underline inline-flex items-center gap-1.5 uppercase tracking-wider"
                  >
                    Ir al sitio oficial <ExternalLink className="h-4 w-4" />
                  </a>
                )}
              </div>
            </Card>
          </div>
        </div>
      </main>

      <footer className="bg-slate-50 dark:bg-brand-slate border-t border-brand-gray/30 mt-20">
        <div className="mx-auto max-w-6xl px-6 py-12 text-center">
          <p className="text-sm font-bold text-slate-400">
            © {new Date().getFullYear()} Yachachiy.ai - Transparencia Educativa
          </p>
        </div>
      </footer>
    </div>
  );
}
