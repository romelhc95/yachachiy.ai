export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://fmcxwoqvxatbrawwtqke.supabase.co';
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_rTQDiEIQYGn0q5VgCdEZlA__F8fDp0E';

export interface Course {
  id: string;
  name: string;
  slug: string;
  institution_id: string;
  institution_name: string;
  price_pen: number | null;
  mode: string;
  address: string;
  duration: string;
  category: string;
  url: string;
  distance_km?: number | null;
  roi_months?: number | null;
  expected_monthly_salary?: number;
  created_at?: string;
}

export interface Institution {
  id: string;
  name: string;
  slug: string;
  website_url: string;
}

/**
 * Normaliza un slug eliminando acentos y caracteres especiales.
 * Crítico para consistencia entre DB y routing de Cloudflare.
 */
export const cleanSlug = (slug: string) => {
  if (!slug) return "";
  return slug
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
};

/**
 * Calcula meses aproximados a partir de un string de duración.
 */
export function parseDurationToMonths(duration: string | null): number {
  if (!duration) return 0;
  const match = duration.match(/(\d+)\s*(mes|semana|año|month|week|year)s?/i);
  if (!match) return 0;
  const value = parseInt(match[1]);
  const unit = match[2].toLowerCase();
  if (unit.startsWith('mes') || unit.startsWith('month')) return value;
  if (unit.startsWith('semana') || unit.startsWith('week')) return value / 4.33;
  if (unit.startsWith('año') || unit.startsWith('year')) return value * 12;
  return 0;
}
