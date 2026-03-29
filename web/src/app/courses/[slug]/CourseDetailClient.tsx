"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  MapPin, Clock, ExternalLink, TrendingUp, ChevronLeft, 
  CheckCircle, ShieldCheck, Mail, Phone, User, MessageSquare 
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

  useEffect(() => {
    let isMounted = true;
    
    const fetchCourse = async () => {
      // Evitamos re-fetchear si ya tenemos la data correcta para este slug
      if (course && course.slug === slug) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/courses/${slug}`);
        
        if (!response.ok) {
          throw new Error("Course not found");
        }
        
        const data = await response.json();
        if (isMounted) {
          setCourse(data);
          setLoading(false);
        }
      } catch (error) {
        console.error("Error fetching course:", error);
        if (isMounted) {
          // Si hay error (ej. curso no existe), redirigir al inicio
          router.push("/");
        }
      }
    };

    if (slug) {
      fetchCourse();
    }

    return () => {
      isMounted = false;
    };
  }, [slug, router]); // Mantener slug y router como dependencias estables

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!course) return;

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/leads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          course_id: course.id
        })
      });

      if (response.ok) {
        setSubmitted(true);
      }
    } catch (error) {
      console.error("Error submitting lead:", error);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Cargando...</div>;
  if (!course) return null;

  return (
    <div className="min-h-screen bg-[#f8f9fa] dark:bg-zinc-950 font-sans">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <Link href="/" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-indigo-600 mb-8 transition-colors">
          <ChevronLeft className="h-4 w-4 mr-1" /> Volver a la búsqueda
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Info */}
          <div className="lg:col-span-2 space-y-8">
            <header>
              <div className="flex items-center gap-2 mb-4">
                <span className="text-indigo-600 font-bold uppercase tracking-widest text-xs">
                  {course.institution_name}
                </span>
                <Badge variant="outline" className="text-[10px] font-bold">
                  {course.mode.toUpperCase()}
                </Badge>
              </div>
              <h1 className="text-4xl font-extrabold text-slate-900 dark:text-white mb-6 leading-tight">
                {course.name}
              </h1>
              <div className="flex flex-wrap gap-6 text-slate-600 dark:text-zinc-400">
                <div className="flex items-center gap-2">
                  <MapPin className="h-5 w-5 text-indigo-500" />
                  <span>{course.address}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-indigo-500" />
                  <span>{course.duration || "N/A"}</span>
                </div>
              </div>
            </header>

            <section className="bg-white dark:bg-zinc-900 rounded-2xl p-8 border border-slate-200 dark:border-zinc-800 shadow-sm">
              <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-emerald-500" />
                Análisis de Inversión
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="space-y-1">
                  <div className="text-sm text-slate-500 uppercase font-bold tracking-wider">Costo Total</div>
                  <div className="text-2xl font-black text-slate-900 dark:text-white">
                    {course.price_pen === null ? "Consultar" : course.price_pen === 0 ? "Gratis" : `S/ ${course.price_pen.toLocaleString()}`}
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-slate-500 uppercase font-bold tracking-wider">Salario Esperado</div>
                  <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">
                    S/ {course.expected_monthly_salary?.toLocaleString() || "0"}
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-sm text-slate-500 uppercase font-bold tracking-wider">Recupero (ROI)</div>
                  <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400">
                    {course.roi_months?.toFixed(1) || "N/A"} meses
                  </div>
                </div>
              </div>
              <p className="mt-8 text-sm text-slate-500 italic">
                * Cálculos basados en promedios del mercado laboral tecnológico en Perú 2024.
              </p>
            </section>

            <section className="space-y-4">
              <h2 className="text-xl font-bold">Sobre este programa</h2>
              <p className="text-slate-600 dark:text-zinc-400 leading-relaxed">
                Este programa académico de {course.institution_name} está diseñado para formar profesionales
                altamente competitivos en {course.name}. Con una modalidad {course.mode}, 
                permite un equilibrio entre teoría y práctica, asegurando que los egresados estén listos
                para los desafíos del mercado global.
              </p>
            </section>
          </div>

          {/* Sidebar - Lead Form */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8 overflow-hidden border-slate-200 dark:border-zinc-800 shadow-xl">
              <div className="bg-indigo-600 p-6 text-white">
                <h3 className="text-xl font-bold mb-2">Solicitar Información</h3>
                <p className="text-indigo-100 text-sm">Recibe el brochure completo y asesoría personalizada.</p>
              </div>
              
              <div className="p-6 bg-white dark:bg-zinc-900">
                {!submitted ? (
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-500 ml-1">Nombre completo</label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                        <Input 
                          placeholder="Tu nombre" 
                          className="pl-10" 
                          required
                          value={formData.name}
                          onChange={e => setFormData({...formData, name: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-500 ml-1">Correo electrónico</label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                        <Input 
                          type="email" 
                          placeholder="tu@correo.com" 
                          className="pl-10" 
                          required
                          value={formData.email}
                          onChange={e => setFormData({...formData, email: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-500 ml-1">Teléfono / WhatsApp</label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                        <Input 
                          placeholder="987 654 321" 
                          className="pl-10" 
                          required
                          value={formData.phone}
                          onChange={e => setFormData({...formData, phone: e.target.value})}
                        />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-bold uppercase text-slate-500 ml-1">Consulta adicional</label>
                      <div className="relative">
                        <MessageSquare className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                        <textarea 
                          className="w-full min-h-[100px] pl-10 pr-3 py-2 text-sm rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                          placeholder="¿En qué podemos ayudarte?"
                          value={formData.message}
                          onChange={e => setFormData({...formData, message: e.target.value})}
                        />
                      </div>
                    </div>
                    <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700 h-12 text-md font-bold">
                      Enviar Solicitud
                    </Button>
                    <div className="flex items-center justify-center gap-2 text-[10px] text-slate-400 mt-4 uppercase font-medium">
                      <ShieldCheck className="h-3 w-3" /> Tus datos están protegidos
                    </div>
                  </form>
                ) : (
                  <div className="py-12 text-center space-y-4 animate-in fade-in zoom-in duration-500">
                    <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CheckCircle className="h-10 w-10 text-emerald-600" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">¡Solicitud Enviada!</h3>
                    <p className="text-slate-500 text-sm">
                      Un asesor de {course.institution_name} se pondrá en contacto contigo en las próximas 24 horas.
                    </p>
                    <Button variant="outline" className="mt-6" onClick={() => setSubmitted(false)}>
                      Enviar otra consulta
                    </Button>
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t border-slate-100 dark:border-zinc-800 text-center">
                {course.url && (
                  <a 
                    href={course.url.startsWith('http') ? course.url : `https://${course.url}`} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-xs text-indigo-600 font-bold hover:underline flex items-center justify-center gap-1"
                  >
                    Ver en sitio oficial <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
