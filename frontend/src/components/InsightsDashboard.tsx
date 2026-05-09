import React from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import { motion } from 'framer-motion';
import { Database } from 'lucide-react';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

interface DashboardProps {
  data: any[];
  type?: 'bar' | 'pie' | 'line';
  title?: string;
}

export const InsightsDashboard: React.FC<DashboardProps> = ({ data, type = 'bar', title }) => {
  if (!data || data.length === 0) {
    return (
      <div className="glass-card rounded-3xl p-8 border border-white/5 bg-white/[0.01] flex flex-col items-center justify-center text-center space-y-3 min-h-[200px]">
        <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center text-white/20">
           <Database size={20} />
        </div>
        <p className="text-sm text-white/30 font-medium">No analytical data returned for this query.</p>
      </div>
    );
  }

  // Dynamically find keys for the chart
  const sample = data[0];
  const keys = Object.keys(sample);
  
  // Find a string/label key
  const labelKey = keys.find(k => k.toLowerCase() === 'title' || k.toLowerCase() === 'name') || 
                   keys.find(k => typeof sample[k] === 'string') || 
                   keys[0];
  
  // Find a numeric key
  const valueKey = keys.find(k => k.toLowerCase() === 'value' || k.toLowerCase() === 'revenue' || k.toLowerCase() === 'spend' || k.toLowerCase() === 'total') || 
                   keys.find(k => typeof sample[k] === 'number') || 
                   keys[1];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-3xl p-8 border border-white/10 bg-[#111214]/80 shadow-2xl backdrop-blur-xl flex flex-col space-y-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white tracking-tight">{title || 'Intelligence Synthesis'}</h3>
          <div className="flex items-center gap-2 mt-1">
             <span className="text-[9px] bg-accent/20 text-accent px-2 py-0.5 rounded-md font-bold uppercase tracking-wider">
               Mapping: {labelKey} vs {valueKey}
             </span>
          </div>
        </div>
        <div className="flex gap-1.5">
           <div className="w-1.5 h-1.5 rounded-full bg-accent" />
           <div className="w-1.5 h-1.5 rounded-full bg-white/10" />
        </div>
      </div>

      <div className="w-full" style={{ height: '350px' }}>
        <ResponsiveContainer width="100%" height="100%">
          {type === 'bar' ? (
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
              <XAxis dataKey={labelKey} stroke="#ffffff30" fontSize={11} tickLine={false} axisLine={false} angle={-45} textAnchor="end" interval={0} />
              <YAxis stroke="#ffffff30" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => val.toLocaleString()} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.03)' }} contentStyle={{ backgroundColor: '#000', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }} />
              <Bar dataKey={valueKey} fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={40} />
            </BarChart>
          ) : type === 'pie' ? (
            <PieChart>
              <Pie
                data={data}
                innerRadius={70}
                outerRadius={100}
                paddingAngle={8}
                dataKey={valueKey}
                nameKey={labelKey}
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(0,0,0,0)" />
                ))}
              </Pie>
              <Tooltip 
                 contentStyle={{ backgroundColor: '#000', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px' }}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          ) : (
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
              <XAxis dataKey={labelKey} stroke="#ffffff30" fontSize={11} />
              <YAxis stroke="#ffffff30" fontSize={11} />
              <Tooltip 
                 contentStyle={{ backgroundColor: '#000', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px' }}
              />
              <Line type="monotone" dataKey={valueKey} stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', r: 4 }} activeDot={{ r: 6, stroke: '#fff' }} />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};
