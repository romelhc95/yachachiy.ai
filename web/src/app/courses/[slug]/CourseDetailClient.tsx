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

export default function CourseDetailClient({ slug }: { slug: string }) {
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
        // Búsqueda resiliente por slug (insensible a mayúsculas/minúsculas)
        const url = `${SUPABASE_URL}/rest/v1/courses?slug=ilike.${slug}&select=*`;
        const response = await fetch(url, {
          headers: {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
          }
        });
        const data = await response.json();
        
        if (isMounted) {
          if (data && data.length > 0) {
            setCourse(data[0]);
            setLoading(false);
          } else {
            console.error("Course not found in database for slug:", slug);
            setLoading(false);
          }
        }
      } catch (error) {
        console.error("Error fetching course:", error);
        if (isMounted) setLoading(false);
      }
    };
    if (slug) fetchCourse();
    return () => { isMounted = false; };
  }, [slug]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!course) return;
    try {
      const response = await fetch(`${SUPABASE_URL}/rest/v1/leads`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "apikey": SUPABASE_ANON_KEY,
          "Authorization": `Bearer ${SUPABASE_ANON_KEY}`
        },
        body: JSON.stringify({ 
          id: crypto.randomUUID(),
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
      <span className="text-sm font-bold text-slate-500 animate-pulse">Cargando programa...</span>
    </div>
  );
  
  if (!course) return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-white dark:bg-brand-slate">
      <h2 className="text-2xl font-bold">Programa no encontrado</h2>
      <Link href="/"><Button>Volver al inicio</Button></Link>
    </div>
  );

  return (
    <div className="min-h-screen bg-white dark:bg-brand-slate text-brand-slate dark:text-white font-sans selection:bg-brand-mint/30">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-brand-gray/50 bg-white/95 dark:bg-brand-slate/95 backdrop-blur shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2 text-2xl font-bold tracking-tight text-brand-slate dark:text-white">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-blue text-white font-bold">Y</div>
            <span>Yachachiy<span className="text-brand-blue">.ai</span></span>
          </Link>
          <div className="hidden md:flex gap-8 items-center text-sm font-medium">
            <Link href="/" className="hover:text-brand-blue">Inicio</Link>
            <Button size="sm" className="bg-brand-mint hover:bg-brand-mint/90 text-brand-slate font-bold rounded-xl px-5 border-0 h-9">
              Solicitar asesoría
            </Button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <Link href="/" className="inline-flex items-center text-sm font-bold text-brand-blue hover:translate-x-[-4px] transition-all mb-10 group">
          <ChevronLeft className="h-5 w-5 mr-1" /> Volver a la búsqueda
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-12">
            <header>
              <div className="flex items-center gap-3 mb-6">
                <Badge className="bg-brand-blue/10 text-brand-blue font-bold border-0">{course.institution_name}</Badge>
                <Badge variant="outline" className="border-brand-gray/50 text-slate-500 font-bold uppercase tracking-wider text-[10px]">{course.mode}</Badge>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold leading-tight">{course.name}</h1>
              <div className="mt-8 grid grid-cols-2 md:grid-cols-3 gap-8">
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Ubicación</span>
                  <span className="font-semibold text-sm">{course.address || "No especificada"}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Duración</span>
                  <span className="font-semibold text-sm">{course.duration || "Consultar"}</span>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-xs font-bold uppercase tracking-widest text-slate-400">Modalidad</span>
                  <span className="font-semibold text-sm">{course.mode}</span>
                </div>
              </div>
            </header>

            <section className="relative overflow-hidden rounded-3xl bg-brand-slate p-8 md:p-10 text-white shadow-premium">
              <h2 className="text-2xl font-bold mb-8 flex items-center gap-2 text-brand-mint">
                <TrendingUp className="h-6 w-6" /> Análisis de Inversión
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Inversión</div>
                  <div className="text-3xl font-bold">{course.price_pen ? `S/ ${course.price_pen.toLocaleString()}` : "Consultar"}</div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">Salario Est.</div>
                  <div className="text-3xl font-bold text-brand-mint">S/ {course.expected_monthly_salary?.toLocaleString() || "4,500"}</div>
                </div>
                <div className="space-y-2">
                  <div className="text-xs text-blue-100/50 uppercase font-bold tracking-widest">ROI</div>
                  <div className="text-3xl font-bold">{course.roi_months?.toFixed(1) || "12.5"} meses</div>
                </div>
              </div>
            </section>
          </div>

          <div className="lg:col-span-1">
            <Card className="sticky top-24 overflow-hidden border-brand-gray/50 shadow-premium rounded-3xl p-8 bg-white dark:bg-zinc-900">
              <h3 className="text-2xl font-bold mb-6">Solicitar Información</h3>
              {!submitted ? (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <Input placeholder="Nombre" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="h-12 rounded-xl" />
                  <Input placeholder="Email" type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="h-12 rounded-xl" />
                  <Input placeholder="WhatsApp" required value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} className="h-12 rounded-xl" />
                  <Button type="submit" className="w-full bg-brand-mint hover:bg-brand-mint/90 h-14 text-brand-slate font-bold rounded-xl border-0">Enviar Solicitud</Button>
                </form>
              ) : (
                <div className="py-8 text-center space-y-4">
                  <CheckCircle className="h-12 w-12 text-emerald-600 mx-auto" />
                  <h3 className="text-xl font-bold">¡Solicitud Enviada!</h3>
                  <Button variant="outline" className="rounded-xl" onClick={() => setSubmitted(false)}>Volver</Button>
                </div>
              )}
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
