import { useEffect, useRef } from 'react';

interface TradingViewMarketOverviewProps {
  symbols: string[];
  theme?: 'light' | 'dark';
}

export default function TradingViewMarketOverview({ symbols, theme = 'dark' }: TradingViewMarketOverviewProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      colorTheme: theme,
      dateRange: '12M',
      showChart: true,
      locale: 'en',
      largeChartUrl: '',
      isTransparent: false,
      showSymbolLogo: true,
      showFloatingTooltip: false,
      width: '100%',
      height: '100%',
      tabs: [
        {
          title: 'Crypto',
          symbols: symbols.filter((s) => s.includes('USDT') || s.includes('USD')).map((s) => ({ s, d: s })),
          originalTitle: 'Cryptocurrencies',
        },
        {
          title: 'Forex',
          symbols: symbols.filter((s) => !s.includes('USDT') && !s.includes('BTC') && !s.includes('ETH')).map((s) => ({ s, d: s })),
          originalTitle: 'Forex',
        },
      ],
      plotLineColorGrowing: 'rgba(106, 168, 79, 1)',
      plotLineColorFalling: 'rgba(255, 0, 0, 1)',
      gridLineColor: 'rgba(42, 46, 57, 1)',
      scaleFontColor: 'rgba(120, 123, 134, 1)',
      belowLineFillColorGrowing: 'rgba(106, 168, 79, 0.12)',
      belowLineFillColorFalling: 'rgba(255, 0, 0, 0.12)',
      belowLineFillColorGrowingBottom: 'rgba(106, 168, 79, 0.05)',
      belowLineFillColorFallingBottom: 'rgba(255, 0, 0, 0.05)',
      symbolActiveColor: 'rgba(64, 152, 255, 0.12)',
    });

    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbols, theme]);

  return (
    <div ref={containerRef} className="w-full h-[500px] overflow-hidden rounded-lg" />
  );
}
