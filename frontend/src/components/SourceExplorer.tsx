import React from 'react';
import { FileText, Database, Table, CheckCircle2, AlertCircle } from 'lucide-react';

const sources = [
  { name: 'movies.csv', type: 'SQL', size: '24KB', status: 'Healthy' },
  { name: 'watch_activity.csv', type: 'SQL', size: '1.2MB', status: 'Healthy' },
  { name: 'q1_report.pdf', type: 'Vector', size: '4.5MB', status: 'Indexed' },
  { name: 'policy_v2.pdf', type: 'Vector', size: '120KB', status: 'Indexed' },
];

export const SourceExplorer: React.FC = () => {
  return (
    <div className="glass-card rounded-2xl p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white/90">Knowledge Base</h3>
        <div className="flex items-center gap-2 text-[10px] bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full font-bold uppercase tracking-widest">
           <CheckCircle2 size={12} /> Sync Active
        </div>
      </div>

      <div className="space-y-3 overflow-y-auto pr-2 custom-scrollbar">
        {sources.map((src) => (
          <div key={src.name} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 hover:bg-white/[0.08] transition-all cursor-pointer group">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center text-white/40 group-hover:text-accent transition-colors">
                {src.type === 'SQL' ? <Database size={18} /> : <FileText size={18} />}
              </div>
              <div>
                <p className="text-sm font-medium text-white/80">{src.name}</p>
                <div className="flex items-center gap-2 text-[10px] text-white/30 uppercase font-bold tracking-tighter">
                  <span>{src.type}</span> • <span>{src.size}</span>
                </div>
              </div>
            </div>
            <span className="text-[10px] text-emerald-400 font-bold bg-emerald-400/5 px-2 py-0.5 rounded border border-emerald-400/10">{src.status}</span>
          </div>
        ))}
      </div>

      <button className="mt-6 w-full py-3 rounded-xl bg-white/5 border border-white/10 text-xs font-bold uppercase tracking-widest hover:bg-white/10 transition-all text-white/60">
        Update Indexes
      </button>
    </div>
  );
};
