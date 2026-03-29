import CourseDetailClient from "./CourseDetailClient";

export async function generateStaticParams() {
  // En una implementación real, esto consultaría la base de datos o API
  // Para el MVP/Static Export, incluimos los slugs principales conocidos
  return [
    { slug: "data-science-piloto" },
    { slug: "ingenieria-software" },
  ];
}

export default function CourseDetailPage() {
  return <CourseDetailClient />;
}
