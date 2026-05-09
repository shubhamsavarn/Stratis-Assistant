import React from 'react';
import { TrendingUp, Users, DollarSign, Film, ArrowUpRight } from 'lucide-react';
import { motion } from 'framer-motion';

const stats = [
  { label: 'Total Revenue', value: '$4.2B', change: '+12.5%', icon: DollarSign, color: 'text-emerald-400' },
  { label: 'Active Viewers', value: '1.2M', change: '+5.2%', icon: Users, color: 'text-blue-400' },
  { label: 'Titles Indexed', value: '104', change: '+2', icon: Film, color: 'text-amber-400' },
  { label: 'Market Share', value: '24%', change: '+1.4%', icon: TrendingUp, color: 'text-violet-400' },
];

export const StatsGrid: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {stats.map((stat, i) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          className="glass-card p-5 rounded-2xl relative overflow-hidden group hover:border-accent/40 transition-colors"
        >
          <div className="flex justify-between items-start">
            <div className="p-2 rounded-xl bg-white/5 border border-white/5 group-hover:bg-accent/10 transition-colors">
              <stat.icon size={20} className={stat.color} />
            </div>
            <div className="flex items-center gap-1 text-[10px] font-bold text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded-full">
              <ArrowUpRight size={10} /> {stat.change}
            </div>
          </div>
          <div className="mt-4">
            <p className="text-xs text-white/40 font-medium uppercase tracking-widest">{stat.label}</p>
            <h3 className="text-2xl font-bold mt-1 tracking-tight">{stat.value}</h3>
          </div>
          <div className="absolute -right-4 -bottom-4 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity">
            <stat.icon size={100} />
          </div>
        </motion.div>
      ))}
    </div>
  );
};
