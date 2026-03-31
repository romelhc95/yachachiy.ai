import { Suspense } from "react";
import CourseDetailClient from "./CourseDetailClient";

// Esta función es CRÍTICA para el despliegue estático en Cloudflare.
// Debe generar los slugs limpios (sin acentos) para que coincidan con el sistema de archivos.
export async function generateStaticParams() {
  const SUPABASE_URL = 'https://fmcxwoqvxatbrawwtqke.supabase.co';
  const SUPABASE_ANON_KEY = 'sb_publishable_rTQDiEIQYGn0q5VgCdEZlA__F8fDp0E';
  
  try {
    const response = await fetch(`${SUPABASE_URL}/rest/v1/courses?select=slug`, {
      headers: { 
        'apikey': SUPABASE_ANON_KEY, 
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}` 
      }
    });
    const courses = await response.json();
    
    // Normalizamos los slugs (quitamos acentos y caracteres especiales)
    return courses.map((c: { slug: string }) => ({
      slug: c.slug
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .replace(/[^a-z0-9-]/g, "-")
    }));
  } catch (error) {
    console.error("Error generating static params:", error);
    return [];
  }
}

export default async function CourseDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Cargando detalles del programa...</div>}>
      <CourseDetailClient slug={slug} />
    </Suspense>
  );
}
