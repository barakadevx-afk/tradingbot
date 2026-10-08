import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const url = new URL(req.url)
    const path = url.pathname.replace('/functions/v1/baraka-api', '')
    const method = req.method

    if (path === '/health' && method === 'GET') {
      return new Response(
        JSON.stringify({ status: 'healthy', service: 'BARAKA AI', timestamp: new Date().toISOString() }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (path === '/markets' && method === 'GET') {
      const markets = [
        { symbol: 'BTC/USDT', price: 67432.50, change_24h: 2.34, volume_24h: 28500000000 },
        { symbol: 'ETH/USDT', price: 3542.80, change_24h: 1.87, volume_24h: 15200000000 },
        { symbol: 'SOL/USDT', price: 178.45, change_24h: -0.92, volume_24h: 3800000000 },
        { symbol: 'BNB/USDT', price: 612.30, change_24h: 0.56, volume_24h: 1900000000 },
        { symbol: 'XRP/USDT', price: 0.6234, change_24h: -1.23, volume_24h: 1200000000 },
        { symbol: 'ADA/USDT', price: 0.4521, change_24h: 0.78, volume_24h: 450000000 },
        { symbol: 'DOGE/USDT', price: 0.1234, change_24h: -2.15, volume_24h: 890000000 },
      ]
      return new Response(
        JSON.stringify(markets),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (path === '/signals' && method === 'GET') {
      const { data, error } = await supabase
        .from('signals')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(50)
      if (error) throw error
      return new Response(JSON.stringify(data || []), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/trades' && method === 'GET') {
      const { data, error } = await supabase
        .from('trades')
        .select('*')
        .order('closed_at', { ascending: false })
        .limit(100)
      if (error) throw error
      return new Response(JSON.stringify(data || []), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/portfolio' && method === 'GET') {
      const { data, error } = await supabase
        .from('portfolio_snapshots')
        .select('*')
        .order('snapshot_time', { ascending: false })
        .limit(1)
      if (error) throw error
      return new Response(JSON.stringify(data?.[0] || {}), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/risk' && method === 'GET') {
      const { data, error } = await supabase.from('risk_configs').select('*').limit(1)
      if (error) throw error
      return new Response(JSON.stringify(data?.[0] || {}), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/strategies' && method === 'GET') {
      const { data, error } = await supabase.from('strategies').select('*')
      if (error) throw error
      return new Response(JSON.stringify(data || []), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/models' && method === 'GET') {
      const { data, error } = await supabase.from('model_versions').select('*')
      if (error) throw error
      return new Response(JSON.stringify(data || []), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/alerts' && method === 'GET') {
      const { data, error } = await supabase.from('alerts').select('*').order('created_at', { ascending: false }).limit(50)
      if (error) throw error
      return new Response(JSON.stringify(data || []), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    if (path === '/system/health' && method === 'GET') {
      return new Response(JSON.stringify({ frontend: { status: 'HEALTHY' }, backend: { status: 'HEALTHY' }, database: { status: 'HEALTHY' } }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
    }

    return new Response(JSON.stringify({ error: 'Not found' }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 404 })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' }, status: 500 })
  }
})
