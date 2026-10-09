import { useEffect, useRef } from 'react';

interface TradingViewTickerProps {
  symbols: string[];
  theme?: 'light' | 'dark';
}

export default function TradingViewTicker({ symbols, theme = 'dark' }: TradingViewTickerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbols: symbols.map((s) => ({
        proName: s,
        title: s,
      })),
      showSymbolLogo: true,
      isTransparent: false,
      displayMode: 'adaptive',
      colorTheme: theme,
      locale: 'en',
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
    <div ref={containerRef} className="w-full h-12 overflow-hidden" />
  );
}
