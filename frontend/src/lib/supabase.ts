import { createClient } from '@supabase/supabase-js'

const supabaseUrl =
  import.meta.env.VITE_SUPABASE_URL || 'https://jaqltdqkohvadfpcmzhd.supabase.co'
const supabaseAnonKey =
  import.meta.env.VITE_SUPABASE_ANON_KEY ||
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImphcWx0ZHFrb2h2YWRmcGNtemhkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk3MjMxNTQsImV4cCI6MjA4NTI5OTE1NH0.xMLvXc0eGkOTdGG9jYj35FmiMDWLkkGlr8DhcP_9qgw'

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
})
