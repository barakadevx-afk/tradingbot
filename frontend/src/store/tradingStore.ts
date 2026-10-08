import { create } from 'zustand';
import type { Market, Signal, Position, Order, Portfolio, RiskConfig, Alert, SystemHealth } from '../types';

interface TradingState {
  // Markets
  markets: Market[];
  selectedSymbol: string;
  candles: Record<string, { timestamp: string; open: number; high: number; low: number; close: number; volume: number }[]>;
  marketLoading: boolean;
  marketError: string | null;

  // Signals
  signals: Signal[];
  signalsLoading: boolean;

  // Positions & Orders
  positions: Position[];
  orders: Order[];

  // Portfolio
  portfolio: Portfolio | null;
  portfolioLoading: boolean;

  // Risk
  riskConfig: RiskConfig | null;
  killSwitchActive: boolean;

  // Alerts
  alerts: Alert[];
  unreadAlerts: number;

  // System
  systemHealth: SystemHealth[];
  tradingMode: 'paper' | 'live' | 'backtest';
  isConnected: boolean;

  // Actions
  setMarkets: (markets: Market[]) => void;
  setSelectedSymbol: (symbol: string) => void;
  setCandles: (symbol: string, candles: { timestamp: string; open: number; high: number; low: number; close: number; volume: number }[]) => void;
  setSignals: (signals: Signal[]) => void;
  setPositions: (positions: Position[]) => void;
  setOrders: (orders: Order[]) => void;
  setPortfolio: (portfolio: Portfolio) => void;
  setRiskConfig: (config: RiskConfig) => void;
  setKillSwitch: (active: boolean) => void;
  setAlerts: (alerts: Alert[]) => void;
  setSystemHealth: (health: SystemHealth[]) => void;
  setTradingMode: (mode: 'paper' | 'live' | 'backtest') => void;
  setConnected: (connected: boolean) => void;
  setMarketLoading: (loading: boolean) => void;
  setMarketError: (error: string | null) => void;
}

export const useTradingStore = create<TradingState>((set) => ({
  markets: [],
  selectedSymbol: 'BTC/USDT',
  candles: {},
  marketLoading: false,
  marketError: null,
  signals: [],
  signalsLoading: false,
  positions: [],
  orders: [],
  portfolio: null,
  portfolioLoading: false,
  riskConfig: null,
  killSwitchActive: false,
  alerts: [],
  unreadAlerts: 0,
  systemHealth: [],
  tradingMode: 'paper',
  isConnected: false,

  setMarkets: (markets) => set({ markets }),
  setSelectedSymbol: (selectedSymbol) => set({ selectedSymbol }),
  setCandles: (symbol, candles) => set((state) => ({
    candles: { ...state.candles, [symbol]: candles },
  })),
  setSignals: (signals) => set({ signals }),
  setPositions: (positions) => set({ positions }),
  setOrders: (orders) => set({ orders }),
  setPortfolio: (portfolio) => set({ portfolio }),
  setRiskConfig: (riskConfig) => set({ riskConfig }),
  setKillSwitch: (killSwitchActive) => set({ killSwitchActive }),
  setAlerts: (alerts) => set({
    alerts,
    unreadAlerts: alerts.filter((a) => !a.read).length,
  }),
  setSystemHealth: (systemHealth) => set({ systemHealth }),
  setTradingMode: (tradingMode) => set({ tradingMode }),
  setConnected: (isConnected) => set({ isConnected }),
  setMarketLoading: (marketLoading) => set({ marketLoading }),
  setMarketError: (marketError) => set({ marketError }),
}));
