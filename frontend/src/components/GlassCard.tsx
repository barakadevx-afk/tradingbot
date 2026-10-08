import { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
  glow?: 'emerald' | 'red' | 'cyan' | 'none';
}

export default function GlassCard({ children, className = '', hover = false, glow = 'none' }: GlassCardProps) {
  const glowStyles = {
    emerald: 'shadow-emerald-500/5 hover:shadow-emerald-500/10',
    red: 'shadow-red-500/5 hover:shadow-red-500/10',
    cyan: 'shadow-cyan-500/5 hover:shadow-cyan-500/10',
    none: '',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`rounded-xl border border-slate-800/50 bg-slate-900/50 backdrop-blur-sm shadow-lg ${
        hover ? 'transition-all duration-300 hover:border-slate-700/50 hover:shadow-xl' : ''
      } ${glowStyles[glow]} ${className}`}
    >
      {children}
    </motion.div>
  );
}
