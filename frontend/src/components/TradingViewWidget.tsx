import { useEffect, useRef } from 'react';

interface TradingViewWidgetProps {
  symbol: string;
  theme?: 'light' | 'dark';
  height?: number;
  width?: number;
}

export default function TradingViewWidget({ symbol, theme = 'dark', height = 500, width = '100%' }: TradingViewWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: symbol,
      interval: '60',
      timezone: 'Etc/UTC',
      theme: theme,
      style: '1',
      locale: 'en',
      backgroundColor: theme === 'dark' ? 'rgba(10, 10, 20, 1)' : 'rgba(255, 255, 255, 1)',
      gridColor: theme === 'dark' ? 'rgba(42, 46, 57, 1)' : 'rgba(240, 243, 250, 1)',
      hide_side_toolbar: false,
      allow_symbol_change: true,
      studies: [
        'STD;Supertrend',
        'STD;RSI',
        'STD;MACD',
        'STD;BollingerBands',
        'STD;Volume',
        'STD;EMA',
        'STD;SMA',
        'STD;ATR',
        'STD;Stochastic',
        'STD;ADX',
        'STD;Ichimoku',
        'STD;VWAP',
        'STD;PivotPointsHighLow',
        'STD;PivotPointsStandard',
      ],
      show_popup_button: true,
      popup_width: '1000',
      popup_height: '650',
      support_host: 'https://www.tradingview.com',
    });

    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [symbol, theme]);

  return (
    <div
      ref={containerRef}
      style={{ height, width }}
      className="rounded-lg overflow-hidden"
    />
  );
}
