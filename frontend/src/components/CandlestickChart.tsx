import { useEffect, useRef, useState } from 'react';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandlestickChartProps {
  symbol: string;
  timeframe: string;
  width?: number;
  height?: number;
}

// Generate realistic OHLCV data
function generateCandles(symbol: string, timeframe: string, count: number = 100): Candle[] {
  const candles: Candle[] = [];
  const basePrices: Record<string, number> = {
    'BTC/USDT': 67000,
    'ETH/USDT': 3500,
    'SOL/USDT': 178,
    'BNB/USDT': 612,
    'XRP/USDT': 0.62,
    'ADA/USDT': 0.45,
    'DOGE/USDT': 0.12,
  };

  const basePrice = basePrices[symbol] || 100;
  const tfMinutes: Record<string, number> = { '5M': 5, '15M': 15, '1H': 60, '4H': 240, '1D': 1440 };
  const interval = (tfMinutes[timeframe] || 60) * 60 * 1000;

  let price = basePrice * (0.95 + Math.random() * 0.1);
  const now = Date.now();

  for (let i = count - 1; i >= 0; i--) {
    const time = now - i * interval;
    const volatility = basePrice * 0.008;
    const change = (Math.random() - 0.48) * volatility;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * volatility * 0.5;
    const low = Math.min(open, close) - Math.random() * volatility * 0.5;
    const volume = basePrice * (1000 + Math.random() * 5000);

    candles.push({ time, open, high, low, close, volume });
    price = close;
  }

  return candles;
}

export default function CandlestickChart({ symbol, timeframe, height = 400 }: CandlestickChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height });
  const [candles] = useState<Candle[]>(() => generateCandles(symbol, timeframe));
  const [hoveredCandle, setHoveredCandle] = useState<Candle | null>(null);
  const [crosshair, setCrosshair] = useState<{ x: number; y: number } | null>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        setDimensions({ width: entry.contentRect.width, height });
      }
    });

    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || candles.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = dimensions.width * dpr;
    canvas.height = dimensions.height * dpr;
    ctx.scale(dpr, dpr);

    const { width, height } = dimensions;
    const padding = { top: 20, right: 60, bottom: 30, left: 10 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    // Calculate price range
    const visibleCount = Math.min(60, candles.length);
    const visibleCandles = candles.slice(-visibleCount);
    const minPrice = Math.min(...visibleCandles.map((c) => c.low));
    const maxPrice = Math.max(...visibleCandles.map((c) => c.high));
    const priceRange = maxPrice - minPrice || 1;
    const pricePadding = priceRange * 0.05;
    const adjustedMin = minPrice - pricePadding;
    const adjustedMax = maxPrice + pricePadding;
    const adjustedRange = adjustedMax - adjustedMin;

    // Clear
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, width, height);

    // Grid lines
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 0.5;
    const gridLines = 6;
    for (let i = 0; i <= gridLines; i++) {
      const y = padding.top + (chartHeight / gridLines) * i;
      ctx.beginPath();
      ctx.moveTo(padding.left, y);
      ctx.lineTo(width - padding.right, y);
      ctx.stroke();

      // Price labels
      const price = adjustedMax - (adjustedRange / gridLines) * i;
      ctx.fillStyle = '#64748b';
      ctx.font = '10px Inter, system-ui, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(
        price > 1000 ? price.toFixed(0) : price > 1 ? price.toFixed(2) : price.toFixed(4),
        width - padding.right + 5,
        y + 3
      );
    }

    // Volume bars
    const maxVolume = Math.max(...visibleCandles.map((c) => c.volume));
    const volumeHeight = chartHeight * 0.15;
    const candleWidth = chartWidth / visibleCount;
    const bodyWidth = Math.max(1, candleWidth * 0.7);

    visibleCandles.forEach((candle, i) => {
      const x = padding.left + i * candleWidth + candleWidth / 2;
      const volHeight = (candle.volume / maxVolume) * volumeHeight;
      const volY = height - padding.bottom - volHeight;

      ctx.fillStyle = candle.close >= candle.open ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
      ctx.fillRect(x - bodyWidth / 2, volY, bodyWidth, volHeight);
    });

    // Candlesticks
    visibleCandles.forEach((candle, i) => {
      const x = padding.left + i * candleWidth + candleWidth / 2;
      const isGreen = candle.close >= candle.open;

      const openY = padding.top + ((adjustedMax - candle.open) / adjustedRange) * chartHeight;
      const closeY = padding.top + ((adjustedMax - candle.close) / adjustedRange) * chartHeight;
      const highY = padding.top + ((adjustedMax - candle.high) / adjustedRange) * chartHeight;
      const lowY = padding.top + ((adjustedMax - candle.low) / adjustedRange) * chartHeight;

      const color = isGreen ? '#10b981' : '#ef4444';

      // Wick
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, highY);
      ctx.lineTo(x, lowY);
      ctx.stroke();

      // Body
      ctx.fillStyle = color;
      const bodyTop = Math.min(openY, closeY);
      const bodyHeight = Math.max(1, Math.abs(closeY - openY));
      ctx.fillRect(x - bodyWidth / 2, bodyTop, bodyWidth, bodyHeight);
    });

    // Crosshair
    if (crosshair) {
      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 0.5;
      ctx.setLineDash([4, 4]);

      ctx.beginPath();
      ctx.moveTo(crosshair.x, padding.top);
      ctx.lineTo(crosshair.x, height - padding.bottom);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(padding.left, crosshair.y);
      ctx.lineTo(width - padding.right, crosshair.y);
      ctx.stroke();

      ctx.setLineDash([]);
    }

    // Time labels
    ctx.fillStyle = '#64748b';
    ctx.font = '9px Inter, system-ui, sans-serif';
    ctx.textAlign = 'center';
    const timeStep = Math.floor(visibleCount / 5);
    for (let i = 0; i < visibleCount; i += timeStep) {
      const x = padding.left + i * candleWidth + candleWidth / 2;
      const date = new Date(visibleCandles[i].time);
      const label = timeframe === '1D'
        ? date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        : date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
      ctx.fillText(label, x, height - 10);
    }
  }, [candles, dimensions, crosshair, timeframe]);

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setCrosshair({ x, y });

    // Find hovered candle
    const padding = { top: 20, right: 60, bottom: 30, left: 10 };
    const chartWidth = dimensions.width - padding.left - padding.right;
    const visibleCount = Math.min(60, candles.length);
    const candleWidth = chartWidth / visibleCount;
    const index = Math.floor((x - padding.left) / candleWidth);

    if (index >= 0 && index < visibleCount) {
      setHoveredCandle(candles[candles.length - visibleCount + index]);
    }
  };

  const handleMouseLeave = () => {
    setCrosshair(null);
    setHoveredCandle(null);
  };

  return (
    <div ref={containerRef} className="relative w-full">
      {/* OHLC Info */}
      <div className="flex items-center gap-4 text-xs text-slate-400 mb-2 px-1">
        {hoveredCandle ? (
          <>
            <span>{new Date(hoveredCandle.time).toLocaleString()}</span>
            <span>O: <span className="text-white">{hoveredCandle.open.toFixed(2)}</span></span>
            <span>H: <span className="text-emerald-400">{hoveredCandle.high.toFixed(2)}</span></span>
            <span>L: <span className="text-red-400">{hoveredCandle.low.toFixed(2)}</span></span>
            <span>C: <span className="text-white">{hoveredCandle.close.toFixed(2)}</span></span>
            <span>Vol: <span className="text-white">{(hoveredCandle.volume / 1000).toFixed(1)}K</span></span>
          </>
        ) : (
          <span>Hover over chart for details</span>
        )}
      </div>
      <canvas
        ref={canvasRef}
        style={{ width: dimensions.width, height: dimensions.height }}
        className="cursor-crosshair rounded-lg"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />
    </div>
  );
}
