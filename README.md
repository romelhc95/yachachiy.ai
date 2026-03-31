# Yachachiy.ai - Plataforma Educativa Serverless de Alta Fidelidad 🇵🇪

**Yachachiy.ai** es la plataforma líder en el Perú para la toma de decisiones educativas basadas en datos reales. Nuestra misión es democratizar el acceso a la información académica (precios, ROI, mallas curriculares) para que cada profesional elija el programa que maximice su potencial.

## 🚀 Arquitectura Purificada (High Fidelity)

El proyecto ha sido consolidado en una arquitectura **100% Serverless** y **Edge-Native**, eliminando cualquier dependencia de servidores tradicionales (EC2, Heroku, Docker) para garantizar latencia mínima y escalabilidad infinita.

### Core Stack
- **Frontend:** [Next.js 15](https://nextjs.org/) (App Router) desplegado en **Cloudflare Pages**.
- **Data Engine:** [Supabase](https://supabase.com/) (PostgreSQL + PostgREST) para persistencia y APIs instantáneas.
- **Edge Logic:** [Cloudflare Workers](https://workers.cloudflare.com/) (Localizado en `cloudflare_backend/`) para tareas críticas de procesamiento en el borde.
- **Data Ingestion:** Sistema de scraping de alta fidelidad con **AI-Parsing** para normalización de datos institucionales.

## 🏛️ Estructura del Repositorio

```text
yachachiy_ai/
├── web/                # Aplicación Next.js 15 (Frontend + Client Logic)
├── cloudflare_backend/ # Workers para lógica pesada o webhooks
├── scripts/            # Engine de Recolección (Harvesters & AI Parsers)
├── db/                 # Esquemas y migraciones de Supabase
└── tests/              # Suite de validación de integridad de datos
```

## 🛡️ Seguridad y Performance
1. **Direct-to-Supabase:** La comunicación entre el cliente y la base de datos es directa via REST, protegida por **Row Level Security (RLS)**.
2. **Data-Driven ROI:** Algoritmos que calculan el retorno de inversión comparando el costo del programa vs. salarios reales del mercado peruano.
3. **SEO & Edge Rendering:** Rutas dinámicas optimizadas para ser servidas desde el CDN de Cloudflare, garantizando tiempos de carga <1s.

## 📊 Misión de Impacto
En un mercado educativo fragmentado, **Yachachiy.ai** actúa como el faro de transparencia. No solo listamos cursos; analizamos su valor real para el futuro del estudiante.

---
© 2026 **Yachachiy.ai** - Transformando la educación en el Perú con datos.
