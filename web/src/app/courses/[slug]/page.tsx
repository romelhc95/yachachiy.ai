import CourseDetailClient from "./CourseDetailClient";

export async function generateStaticParams() {
  // En una implementación real, esto consultaría la base de datos o API
  // Para el MVP/Static Export, incluimos los slugs principales conocidos
  return [
    { slug: "data-science-piloto" },
    { slug: "ingenieria-software" },
  ];
}

interface PageProps {
  params: Promise<{ slug: string }>;
}

export default function CourseDetailPage({ params }: PageProps) {
  // En Next.js 15/16, pasamos la promesa directamente al Client Component
  // para una hidratación más robusta usando React.use()
  return <CourseDetailClient params={params} />;
}
