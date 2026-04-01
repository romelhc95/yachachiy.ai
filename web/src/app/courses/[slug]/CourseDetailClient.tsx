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
import { SUPABASE_URL, SUPABASE_ANON_KEY, cleanSlug } from "@/lib/supabase";

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
  roi_months?: number | null;
  expected_monthly_salary?: number;
}

export default function CourseDetailClient({ slug }: { slug: string }) {
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorInfo, setErrorInfo] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({ first_name: "", last_name: "", email: "", whatsapp: "" });

  const handleSubmitLead = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!course) return;
    
    setIsSubmitting(true);
    try {
      const leadData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        whatsapp: formData.whatsapp,
        type: 'info',
        course_id: course.id
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
        setSubmitted(true);
      }
    } catch (error) {
      console.error("Error submitting lead:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true);
        setErrorInfo(null);
        
        console.log("🔍 Buscando programa con slug:", slug);

        // ESTRATEGIA DE BÚSQUEDA RESILIENTE (DOS NIVELES)
        // 1. Intentamos por slug exacto
        let url = `${SUPABASE_URL}/rest/v1/courses?slug=eq.${slug}&select=*`;
        let response = await fetch(url, {
          headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
        });
        let data = await response.json();

        // 2. Si falla (común por acentos en DB), búsqueda robusta por normalización
        if (!data || data.length === 0) {
          console.warn("⚠️ No encontrado por slug exacto, aplicando búsqueda resiliente...");
          const allUrl = `${SUPABASE_URL}/rest/v1/courses?select=*`;
          const allRes = await fetch(allUrl, {
            headers: { 'apikey': SUPABASE_ANON_KEY, 'Authorization': `Bearer ${SUPABASE_ANON_KEY}` }
          });
          const allCourses = await allRes.json();
          
          if (Array.isArray(allCourses)) {
            const target = cleanSlug(slug);
            const found = allCourses.find(c => cleanSlug(c.slug) === target);
            if (found) {
              data = [found];
              console.log("🎯 Coincidencia encontrada mediante normalización:", found.name);
            }
          }
        }

        if (Array.isArray(data) && data.length > 0) {
          setCourse(data[0]);
          console.log("✅ Programa cargado:", data[0].name);
        } else {
          setErrorInfo(`El programa "${slug}" no está disponible actualmente en nuestra base de datos.`);
        }
      } catch (err) {
        console.error("❌ Error crítico en fetch:", err);
        setErrorInfo("Ocurrió un error técnico al conectar con el servidor de datos.");
      } finally {
        setLoading(false);
      }
    };

    if (slug) fetchCourse();
  }, [slug]);

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-brand-slate text-white">
      <div className="w-12 h-12 border-4 border-brand-mint border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="animate-pulse font-bold uppercase tracking-widest text-xs text-brand-mint">Validando credenciales académicas...</p>
    </div>
  );

  if (errorInfo) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-brand-slate p-6 text-center">
      <div className="bg-red-50 dark:bg-red-500/10 p-10 rounded-[3rem] border border-red-100 dark:border-red-500/20 max-w-lg">
        <h2 className="text-3xl font-bold mb-4 text-brand-slate dark:text-white">Lo sentimos</h2>
        <p className="text-slate-500 dark:text-slate-400 mb-8 leading-relaxed">{errorInfo}</p>
        <Link href="/">
          <Button className="bg-brand-blue text-white rounded-2xl h-12 px-8 font-bold shadow-lg shadow-brand-blue/20">Volver al buscador</Button>
        </Link>
      </div>
    </div>
  );

  if (!course) return null;

  return (
    <div className="min-h-screen bg-white dark:bg-brand-slate text-brand-slate dark:text-white font-sans selection:bg-brand-mint/30 pb-20">
      <main className="mx-auto max-w-6xl px-6 py-10">
        <Link href="/" className="inline-flex items-center text-sm font-bold text-brand-blue hover:translate-x-[-4px] transition-all mb-10 group">
          <ChevronLeft className="h-5 w-5 mr-1" /> Volver a la búsqueda
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-12">
            <header>
              <div className="flex items-center gap-3 mb-6">
                <Badge className="bg-brand-blue/10 text-brand-blue font-bold border-0 px-3 py-1">{course.institution_name}</Badge>
                <Badge variant="outline" className="border-brand-gray/50 text-slate-500 font-bold uppercase tracking-wider text-[10px] px-3 py-1">{course.mode}</Badge>
              </div>
              <h1 className="text-4xl md:text-6xl font-bold leading-tight tracking-tight mb-8">{course.name}</h1>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
                <div className="flex flex-col gap-1"><span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Ubicación</span><span className="font-semibold text-sm">{course.address || "No especificada"}</span></div>
                <div className="flex flex-col gap-1"><span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Duración</span><span className="font-semibold text-sm">{course.duration || "Consultar"}</span></div>
                <div className="flex flex-col gap-1"><span className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Modalidad</span><span className="font-semibold text-sm">{course.mode}</span></div>
              </div>
            </header>

            <section className="relative overflow-hidden rounded-[3rem] bg-brand-slate p-10 md:p-14 text-white shadow-premium border border-white/5">
              <div className="absolute top-0 right-0 p-10 opacity-10"><TrendingUp className="h-32 w-32" /></div>
              <h2 className="text-2xl font-bold mb-10 flex items-center gap-3 text-brand-mint"><TrendingUp className="h-7 w-7" /> Análisis de Inversión y ROI</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
                <div className="space-y-2"><div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Inversión Estimada</div><div className="text-4xl font-bold">{course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}</div></div>
                <div className="space-y-2"><div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Salario Promedio</div><div className="text-4xl font-bold text-brand-mint">S/ {course.expected_monthly_salary?.toLocaleString() || "4,800"}</div></div>
                <div className="space-y-2"><div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Retorno (Meses)</div><div className="text-4xl font-bold text-white">{course.roi_months?.toFixed(1) || "14.2"}</div></div>
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-2xl font-bold flex items-center gap-2"><ShieldCheck className="h-6 w-6 text-brand-blue" /> Resumen del programa</h2>
              <div className="prose dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 leading-relaxed text-lg italic">
                Este programa representa una oportunidad estratégica de especialización. El análisis de Yachachiy destaca su alta demanda en el mercado laboral peruano actual.
              </div>
            </section>
          </div>

          <div className="lg:col-span-1">
            <Card className="sticky top-24 overflow-hidden border-brand-gray/50 shadow-premium rounded-[2.5rem] p-10 bg-white dark:bg-zinc-900 border-0">
              <div className="mb-10">
                <h3 className="text-3xl font-bold mb-3 tracking-tight">Solicitar Info</h3>
                <p className="text-slate-500 text-sm">Obtén el plan de estudios completo para <strong>{course.name}</strong> y asesoría personalizada.</p>
              </div>
              {!submitted ? (
                <form className="space-y-5" onSubmit={handleSubmitLead}>
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-2">Nombres</label>
                      <Input 
                        required
                        placeholder="Ej: Juan" 
                        className="h-12 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 px-5 font-semibold" 
                        value={formData.first_name}
                        onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-2">Apellidos</label>
                      <Input 
                        required
                        placeholder="Ej: Pérez" 
                        className="h-12 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 px-5 font-semibold" 
                        value={formData.last_name}
                        onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-2">Email corporativo/personal</label>
                      <Input 
                        required
                        type="email" 
                        placeholder="juan@ejemplo.com" 
                        className="h-12 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 px-5 font-semibold" 
                        value={formData.email}
                        onChange={(e) => setFormData({...formData, email: e.target.value})}
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-2">WhatsApp</label>
                      <Input 
                        required
                        placeholder="+51 987 654 321" 
                        className="h-12 rounded-2xl border-brand-gray bg-slate-50 dark:bg-zinc-800 px-5 font-semibold" 
                        value={formData.whatsapp}
                        onChange={(e) => setFormData({...formData, whatsapp: e.target.value})}
                      />
                    </div>
                  </div>
                  <Button 
                    disabled={isSubmitting}
                    type="submit" 
                    className="w-full bg-brand-mint hover:bg-brand-mint/90 h-16 text-brand-slate font-black text-lg rounded-2xl transition-all shadow-lg shadow-brand-mint/20 border-0 mt-4"
                  >
                    {isSubmitting ? (
                      <div className="flex items-center gap-2">
                        <div className="w-5 h-5 border-2 border-brand-slate/30 border-t-brand-slate rounded-full animate-spin" />
                        ENVIANDO...
                      </div>
                    ) : (
                      "ENVIAR SOLICITUD"
                    )}
                  </Button>
                </form>
              ) : (
                <div className="py-10 text-center animate-in zoom-in duration-500">
                  <CheckCircle className="h-16 w-16 text-emerald-500 mx-auto mb-6" />
                  <h3 className="text-2xl font-bold">¡Recibido!</h3>
                  <p className="text-slate-500 mt-2">Un asesor se pondrá en contacto contigo para darte detalles de <strong>{course.name}</strong>.</p>
                </div>
              )}
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
