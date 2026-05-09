import React from 'react';
import { motion } from 'framer-motion';
import { Table as TableIcon } from 'lucide-react';

interface DataTableProps {
  data: any[];
}

export const DataTable: React.FC<DataTableProps> = ({ data }) => {
  if (!data || data.length === 0) return null;

  const headers = Object.keys(data[0]);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card rounded-2xl overflow-hidden border border-white/5"
    >
      <div className="bg-white/5 px-6 py-3 border-b border-white/5 flex items-center gap-2">
         <TableIcon size={14} className="text-accent" />
         <span className="text-[10px] font-bold uppercase tracking-widest text-white/50">Structured Dataset</span>
      </div>
      <div className="overflow-x-auto custom-scrollbar">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/[0.02]">
              {headers.map(h => (
                <th key={h} className="px-6 py-4 text-[11px] font-bold uppercase tracking-wider text-white/30 border-b border-white/5">
                  {h.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {data.map((row, i) => (
              <tr key={i} className="hover:bg-accent/5 transition-colors group">
                {headers.map(h => (
                  <td key={h} className="px-6 py-4 text-sm text-white/70 group-hover:text-white transition-colors">
                    {row[h]?.toString()}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};
