ALTER TABLE public.leads ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Permitir inserción pública de leads" ON public.leads;
CREATE POLICY "Permitir inserción pública de leads" ON public.leads 
FOR INSERT 
TO anon 
WITH CHECK (true);
