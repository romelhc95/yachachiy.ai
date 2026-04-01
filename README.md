# Yachachiy.ai - Plataforma Educativa Serverless de Alta Fidelidad 🇵🇪

**Yachachiy.ai** es la plataforma líder en el Perú para la toma de decisiones educativas basadas en datos reales. Nuestra misión es democratizar el acceso a la información académica (precios, ROI, mallas curriculares) para que cada profesional elija el programa que maximice su potencial.

## 🚀 Estado Actual: Versión Estable 2026

El proyecto ha sido consolidado en una arquitectura **100% Serverless** y **Edge-Native**, optimizada para el mercado peruano.

### 🌟 Funcionalidades Implementadas
- **Búsqueda Avanzada:** Motor de búsqueda resiliente con normalización de acentos y caracteres especiales (ej: "economia" -> "Economía").
- **Comparador Inteligente:** Herramienta para comparar hasta 3 programas educativos simultáneamente, analizando inversión, ROI y modalidad.
- **Captación de Leads (IA Orientation):** 
  - Consultas específicas de programas vinculadas automáticamente.
  - Generador de recomendaciones personalizadas basado en área de interés, presupuesto y modalidad.
- **Arquitectura de UI:** Layout global con Header y Footer persistentes en todas las rutas dinámicas.
- **Análisis de ROI:** Cálculo automático del tiempo de retorno de inversión basado en salarios proyectados.

### 🛠️ Core Stack
- **Frontend:** [Next.js 15](https://nextjs.org/) desplegado en **Cloudflare Pages**.
- **Data Engine:** [Supabase](https://supabase.com/) (PostgreSQL + PostgREST) con **Row Level Security (RLS)** habilitado.
- **Edge Logic:** [Cloudflare Workers](https://workers.cloudflare.com/) para procesamiento en el borde.
- **Security:** Gestión estricta de secretos mediante variables de entorno (`.env`) y saneamiento total del código fuente.

## 🏛️ Estructura del Repositorio

```text
yachachiy_ai/
├── web/                # Aplicación Next.js 15 (Frontend + Client Logic)
├── cloudflare_backend/ # Workers para lógica pesada o webhooks
├── scripts/            # Engine de Recolección Asegurado (Harvesters & AI Parsers)
├── db/                 # Esquemas y scripts de migración/seguridad
└── tests/              # Suite de validación de integridad y seguridad
```

## 🛡️ Seguridad y Calidad
1. **Zero Secret Policy:** Eliminación de toda credencial administrativa del código fuente.
2. **RLS Hardening:** Políticas de base de datos que permiten inserciones públicas anónimas pero protegen la lectura de datos sensibles.
3. **Validación Integral:** Reportes de calidad y seguridad generados periódicamente para asegurar estabilidad.

## 📊 Misión de Impacto
En un mercado educativo fragmentado, **Yachachiy.ai** actúa como el faro de transparencia. No solo listamos cursos; analizamos su valor real para el futuro del estudiante.

---
© 2026 **Yachachiy.ai** - Transformando la educación en el Perú con datos.
