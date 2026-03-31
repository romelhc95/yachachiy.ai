import { Suspense } from "react";
import CourseDetailClient from "./CourseDetailClient";

export async function generateStaticParams() {
  // En una implementación real, esto consultaría la base de datos o API.
  // Aseguramos que los slugs estén normalizados (sin acentos, minúsculas).
  const slugs = [
    "data-science-piloto",
    "ingenieria-software",
    "maestria-en-ciencias-en-quimica-uni"
  ];
  
  return slugs.map(slug => ({ slug }));
}

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function CourseDetailPage({ params }: PageProps) {
  // En Next.js 15/16, pasamos la promesa directamente al Client Component
  // para una hidratación más robusta usando React.use()
  // Es obligatorio envolver en Suspense cuando el Client Component usa React.use(params)
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Cargando detalles...</div>}>
      <CourseDetailClient params={params} />
    </Suspense>
  );
}
