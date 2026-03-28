"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  ChevronLeft, MapPin, Clock, TrendingUp, DollarSign, 
  CheckCircle2, AlertCircle, Building, Star, ExternalLink
} from "lucide-react";
import { cn } from "@/lib/utils";
import { buttonVariants } from "@/components/ui/button";
import Link from "next/link";

interface Course {
  id: string;
  name: string;
  slug: string;
  institution_name: string;
  price_pen: number;
  mode: string;
  address: string;
  duration: string;
  url: string;
  distance_km?: number | null;
  roi_months?: number | null;
  expected_monthly_salary?: number;
}

function CompareContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const ids = searchParams.get("ids")?.split(",") || [];
    if (ids.length === 0) {
      router.push("/");
      return;
    }

    const fetchCourses = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/courses`);
        const allCourses: Course[] = await response.json();
        const selected = allCourses.filter(c => ids.includes(c.id));
        setCourses(selected);
      } catch (error) {
        console.error("Error fetching courses for comparison:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [searchParams, router]);

  if (loading) return <div className="min-h-screen flex items-center justify-center">Preparando comparativa...</div>;

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 py-12">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between mb-10">
          <div>
            <Link href="/" className="inline-flex items-center text-sm font-medium text-slate-500 hover:text-indigo-600 mb-4 transition-colors">
              <ChevronLeft className="h-4 w-4 mr-1" /> Volver a la búsqueda
            </Link>
            <h1 className="text-3xl font-black text-slate-900 dark:text-white">Comparativa de Programas</h1>
            <p className="text-slate-500 mt-1">Analiza detalladamente tus mejores opciones.</p>
          </div>
          <Badge variant="secondary" className="px-4 py-1 text-sm font-bold bg-indigo-100 text-indigo-700 border-indigo-200">
            {courses.length} Programas seleccionados
          </Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <Card key={course.id} className="relative overflow-hidden border-slate-200 dark:border-zinc-800 shadow-lg flex flex-col">
              <div className="h-2 bg-indigo-600 w-full" />
              
              <div className="p-6 flex-1 space-y-8">
                {/* Header Section */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Building className="h-4 w-4 text-indigo-500" />
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">{course.institution_name}</span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-white leading-snug h-14 overflow-hidden line-clamp-2">
                    {course.name}
                  </h2>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-50 dark:bg-zinc-900 p-3 rounded-xl border border-slate-100 dark:border-zinc-800">
                    <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">Inversión</div>
                    <div className="text-lg font-black text-slate-900 dark:text-white">S/ {course.price_pen.toLocaleString()}</div>
                  </div>
                  <div className="bg-slate-50 dark:bg-zinc-900 p-3 rounded-xl border border-slate-100 dark:border-zinc-800">
                    <div className="text-[10px] font-bold text-slate-400 uppercase mb-1">ROI Est.</div>
                    <div className="text-lg font-black text-indigo-600 dark:text-indigo-400">{course.roi_months?.toFixed(1)} meses</div>
                  </div>
                </div>

                {/* Comparison Details */}
                <div className="space-y-4 pt-4 border-t border-slate-100 dark:border-zinc-800">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center shrink-0">
                      <Clock className="h-4 w-4 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-[10px] font-bold text-slate-400 uppercase">Duración</div>
                      <div className="text-sm font-medium">{course.duration || "No especificado"}</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center shrink-0">
                      <Star className="h-4 w-4 text-emerald-600" />
                    </div>
                    <div>
                      <div className="text-[10px] font-bold text-slate-400 uppercase">Modalidad</div>
                      <div className="text-sm font-medium">{course.mode}</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-amber-50 dark:bg-amber-900/30 flex items-center justify-center shrink-0">
                      <MapPin className="h-4 w-4 text-amber-600" />
                    </div>
                    <div>
                      <div className="text-[10px] font-bold text-slate-400 uppercase">Ubicación</div>
                      <div className="text-sm font-medium line-clamp-1">{course.address}</div>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-full bg-purple-50 dark:bg-purple-900/30 flex items-center justify-center shrink-0">
                      <TrendingUp className="h-4 w-4 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-[10px] font-bold text-slate-400 uppercase">Salario Inicial</div>
                      <div className="text-sm font-medium">S/ {course.expected_monthly_salary?.toLocaleString()}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="p-6 bg-slate-50 dark:bg-zinc-900/50 border-t border-slate-100 dark:border-zinc-800 flex flex-col gap-2">
                <Link href={`/courses/${course.slug}`} className="w-full">
                  <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold h-10">
                    Solicitar Info
                  </Button>
                </Link>
                <a 
                  href={course.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={cn(
                    buttonVariants({ variant: "outline", size: "sm" }),
                    "w-full text-xs font-bold h-9 gap-2"
                  )}
                >
                  Sitio Oficial <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </Card>
          ))}

          {/* Add more slot if < 3 */}
          {courses.length < 3 && (
            <div className="border-2 border-dashed border-slate-200 dark:border-zinc-800 rounded-2xl flex flex-col items-center justify-center p-12 text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-slate-100 dark:bg-zinc-900 flex items-center justify-center">
                <AlertCircle className="h-8 w-8 text-slate-300" />
              </div>
              <div>
                <div className="font-bold text-slate-400">Espacio disponible</div>
                <p className="text-xs text-slate-400 px-8">Puedes agregar un programa más para comparar.</p>
              </div>
              <Link href="/">
                <Button variant="ghost" className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 font-bold">
                  Buscar más
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Cargando comparativa...</div>}>
      <CompareContent />
    </Suspense>
  );
}
