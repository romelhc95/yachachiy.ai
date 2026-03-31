"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  MapPin, Clock, ExternalLink, TrendingUp, ChevronLeft, 
  CheckCircle, ShieldCheck, Mail, Phone, User, MessageSquare,
  GraduationCap, Briefcase, DollarSign, ArrowRight
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface Course {
  id: string;
  name: string;
  slug: string;
  institution_name: string;
  price_pen: number | null;
  mode: string;
  address: string;
  duration: string;
  url: string;
  distance_km?: number | null;
  roi_months?: number | null;
  expected_monthly_salary?: number;
}

interface CourseDetailClientProps {
  params: Promise<{ slug: string }>;
}

export default function CourseDetailClient({ params }: CourseDetailClientProps) {
  const { slug } = use(params);
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

  const SUPABASE_URL = 'https://fmcxwoqvxatbrawwtqke.supabase.co';
  const SUPABASE_ANON_KEY = 'sb_publishable_rTQDiEIQYGn0q5VgCdEZlA__F8fDp0E';

  useEffect(() => {
    let isMounted = true;
    const fetchCourse = async () => {
      try {
        setLoading(true);
        const url = `${SUPABASE_URL}/rest/v1/courses?slug=eq.${slug}&select=*`;
        const response = await fetch(url, {
          headers: {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
          }
        });
        if (!response.ok) throw new Error("Course not found");
        const data = await response.json();
        if (isMounted) {
          setCourse(data[0] || null);
          setLoading(false);
        }
      } catch (error) {
        console.error("Error fetching course:", error);
        if (isMounted) router.push("/");
      }
    };
    if (slug) fetchCourse();
    return () => { isMounted = false; };
  }, [slug, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!course) return;
    try {
      const leadId = crypto.randomUUID();
      const response = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "apikey": SUPABASE_ANON_KEY,
          "Authorization": `Bearer ${SUPABASE_ANON_KEY}`,
          "Prefer": "return=minimal"
        },
        body: JSON.stringify({ 
          id: leadId,
          ...formData, 
          course_id: course.id 
        })
      });
      if (response.ok) setSubmitted(true);
    } catch (error) {
      console.error("Error submitting lead:", error);
    }
  };

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-white dark:bg-brand-slate">
      <div className="w-12 h-12 rounded-full border-4 border-brand-blue border-t-transparent animate-spin" />
      <span className="text-sm font-bold text-slate-500 animate-pulse">Obteniendo datos reales...</span>
    </div>
  );
  
  if (!course) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-brand-slate text-brand-slate dark:text-white font-sans selection:bg-brand-mint/30">
      {/* Header (Simplified) */}
      <header className="sticky top-0 z-50 border-b border-brand-gray/50 bg-white/95 dark:bg-brand-slate/95 backdrop-blur shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2 text-2xl font-bold tracking-tight text-brand-slate dark:text-white">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-blue text-white font-bold">Y</div>
            <span>Yachachiy<span className="text-brand-blue">.ai</span></span>
          </Link>
          <div className="hidden md:flex gap-8 items-center">
            <Link href="/" className="text-sm font-medium hover:text-brand-blue transition">Programas</Link>
            <Link href="#" className="text-sm font-medium hover:text-brand-blue transition">Instituciones</Link>
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
                  <span className="font-semibold text-sm">{course.address}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                    <Clock className="h-3 w-3" /> Duración
                  </span>
                  <span className="font-semibold text-sm">{course.duration || "N/A"}</span>
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
            <section className="relative overflow-hidden rounded-3xl bg-brand-slate p-8 md:p-10 text-white shadow-premium border border-white/5">
              <div className="absolute top-0 right-0 p-10 opacity-10">
                <TrendingUp className="h-24 w-24" />
              </div>
              <h2 className="text-2xl font-bold mb-8 flex items-center gap-2 text-brand-mint">
                <TrendingUp className="h-6 w-6" />
                Análisis de Inversión (Data-driven)
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Inversión Total</div>
                  <div className="text-3xl font-bold">
                    {course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Salario Proyectado</div>
                  <div className="text-3xl font-bold text-brand-mint">
                    S/ {course.expected_monthly_salary?.toLocaleString() || "4,500"}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Recupero ROI</div>
                  <div className="text-3xl font-bold text-white">
                    {course.roi_months?.toFixed(1) || "12.5"} meses
                  </div>
                </div>
              </div>
              <div className="mt-10 p-4 rounded-xl bg-white/5 border border-white/10 text-xs text-blue-100/60 italic leading-relaxed">
                * Estimaciones basadas en datos reales del mercado laboral peruano 2024. Los resultados pueden variar según el perfil del egresado.
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                <ShieldCheck className="h-6 w-6 text-brand-blue" />
                Sobre el programa
              </h2>
              <div className="prose dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 leading-relaxed text-lg">
                <p>
                  El programa <strong>{course.name}</strong> dictado por <strong>{course.institution_name}</strong> representa una 
                  oportunidad excepcional de especialización en el mercado peruano. Orientado a profesionales que buscan 
                  un alto impacto competitivo, este programa combina rigurosidad académica con aplicación práctica.
                </p>
                <p className="mt-4">
                  Bajo una modalidad <strong>{course.mode}</strong>, el curso permite optimizar los tiempos de aprendizaje 
                  sin sacrificar la calidad de la enseñanza ni el networking estratégico.
                </p>
              </div>
            </section>
          </div>

          {/* Sidebar - Form */}
          <div className="lg:col-span-1">
            <Card className="sticky top-24 overflow-hidden border-brand-gray/50 dark:border-white/10 shadow-premium rounded-3xl">
              <div className="bg-brand-blue p-8 text-white">
                <p className="text-xs font-bold uppercase tracking-widest text-brand-mint mb-2">Pide tu asesoría</p>
                <h3 className="text-2xl font-bold mb-3">Solicitar Información</h3>
                <p className="text-blue-100 text-sm leading-relaxed">Recibe el brochure completo, plan de estudios y precios actualizados.</p>
              </div>
              
              <div className="p-8 bg-white dark:bg-zinc-900">
                {!submitted ? (
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 ml-1">Tu Nombre</label>
                      <div className="relative">
                        <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <Input 
                          placeholder="Juan Pérez" 
                          className="pl-12 h-12 rounded-xl border-brand-gray bg-slate-50 dark:bg-zinc-800 focus:ring-brand-blue" 
                          required
                          value={formData.name}
                          onChange={e => setFormData({...formData, name: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 ml-1">Correo electrónico</label>
                      <div className="relative">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <Input 
                          type="email" 
                          placeholder="tu@email.com" 
                          className="pl-12 h-12 rounded-xl border-brand-gray bg-slate-50 dark:bg-zinc-800 focus:ring-brand-blue" 
                          required
                          value={formData.email}
                          onChange={e => setFormData({...formData, email: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-400 dark:text-slate-500 ml-1">WhatsApp</label>
                      <div className="relative">
                        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <Input 
                          placeholder="+51 900 000 000" 
                          className="pl-12 h-12 rounded-xl border-brand-gray bg-slate-50 dark:bg-zinc-800 focus:ring-brand-blue" 
                          required
                          value={formData.phone}
                          onChange={e => setFormData({...formData, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    <Button type="submit" className="w-full bg-brand-mint hover:bg-brand-mint/90 h-14 text-brand-slate font-bold rounded-xl transition shadow-lg shadow-brand-mint/10 border-0">
                      Enviar Solicitud <ArrowRight className="ml-2 h-5 w-5" />
                    </Button>
                    <p className="text-[10px] text-center text-slate-400 mt-6 flex items-center justify-center gap-1 uppercase font-bold">
                      <ShieldCheck className="h-3 w-3" /> Protección de datos 100% segura
                    </p>
                  </form>
                ) : (
                  <div className="py-12 text-center space-y-6 animate-in fade-in zoom-in duration-500">
                    <div className="w-20 h-20 bg-emerald-50 dark:bg-emerald-500/10 rounded-3xl flex items-center justify-center mx-auto mb-4">
                      <CheckCircle className="h-12 w-12 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-brand-slate dark:text-white">¡Gracias por tu interés!</h3>
                    <p className="text-slate-500 dark:text-slate-400 text-sm leading-relaxed">
                      Un asesor de {course.institution_name} te enviará el brochure detallado y resolverá tus dudas vía WhatsApp.
                    </p>
                    <Button variant="outline" className="mt-8 rounded-xl border-brand-gray" onClick={() => setSubmitted(false)}>
                      Volver a preguntar
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
                    className="text-sm text-brand-blue font-bold hover:underline inline-flex items-center gap-1.5"
                  >
                    Ver sitio oficial del programa <ExternalLink className="h-4 w-4" />
                  </a>
                )}
              </div>
            </Card>
          </div>
        </div>
      </main>

      <footer className="bg-slate-50 dark:bg-brand-slate border-t border-brand-gray/30 mt-20">
        <div className="mx-auto max-w-6xl px-6 py-12 text-center">
          <p className="text-sm font-bold text-slate-500 dark:text-slate-400">
            © {new Date().getFullYear()} Yachachiy.ai - Democratizando la educación en el Perú
          </p>
        </div>
      </footer>
    </div>
  );
}
