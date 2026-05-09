import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, History, ShieldCheck, TrendingUp, Info, LayoutDashboard, Database, FileText, Settings, LogOut, Search, Command, ChevronRight, Activity, Zap, Cpu } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { InsightsDashboard } from './InsightsDashboard';
import { StatsGrid } from './StatsGrid';
import { SourceExplorer } from './SourceExplorer';
import { DataTable } from './DataTable';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  thought?: string;
  data?: any[];
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeData, setActiveData] = useState<any[] | null>(null);
  const [view, setView] = useState<'overview' | 'chat'>('overview');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    if (view === 'overview') setView('chat');

    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      const data = await res.json();
      
      let chartData = null;
      if (data.thought_trace.includes("HighestRevenue") || data.thought_trace.includes("movies")) {
         chartData = [
            { title: "Stellar Run", revenue: 500000000, category: "Sci-Fi" },
            { title: "Dark Orbit", revenue: 350000000, category: "Sci-Fi" },
            { title: "Last Kingdom", revenue: 120000000, category: "Action" },
            { title: "Neo Seoul", revenue: 95000000, category: "Drama" }
         ];
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        thought: data.thought_trace,
        data: chartData
      };

      setMessages(prev => [...prev, assistantMsg]);
      if (chartData) setActiveData(chartData);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-accent/30 relative">
      
      {/* BACKGROUND ATMOSPHERE */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
         <motion.div 
            animate={{ 
               x: [0, 100, 0], 
               y: [0, -50, 0],
               scale: [1, 1.2, 1]
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-accent/10 blur-[120px] rounded-full" 
         />
         <motion.div 
            animate={{ 
               x: [0, -100, 0], 
               y: [0, 80, 0],
               scale: [1.2, 1, 1.2]
            }}
            transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
            className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-violet-500/10 blur-[120px] rounded-full" 
         />
      </div>

      {/* 1. LEFT NAVIGATION (COMPRESSED) */}
      <aside className="w-20 lg:w-64 border-r border-white/5 flex flex-col bg-surface/80 backdrop-blur-3xl shrink-0 z-20">
        <div className="p-6 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent to-accent-hover flex items-center justify-center shadow-lg shadow-accent/20">
            <ShieldCheck size={24} className="text-white" />
          </div>
          <div className="hidden lg:block">
            <h1 className="font-bold text-lg tracking-tight leading-tight">InsightEngine</h1>
            <p className="text-[10px] text-white/30 uppercase tracking-widest font-bold">Enterprise AI v2</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto custom-scrollbar">
          <NavItem icon={LayoutDashboard} label="Dashboard" active={view === 'overview'} onClick={() => setView('overview')} />
          <NavItem icon={Bot} label="AI Inquiry" active={view === 'chat'} onClick={() => setView('chat')} />
          <div className="my-6 border-t border-white/5 mx-2" />
          <NavItem icon={Database} label="SQL Engine" />
          <NavItem icon={FileText} label="Vector Store" />
          <NavItem icon={Activity} label="System Logs" />
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="p-3 rounded-2xl bg-white/5 flex items-center gap-3 group cursor-pointer hover:bg-white/10 transition-colors">
             <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">JD</div>
             <div className="hidden lg:block flex-1 overflow-hidden">
                <p className="text-xs font-bold truncate">John Doe</p>
                <p className="text-[10px] text-white/30 truncate">Senior Quant Engineer</p>
             </div>
             <LogOut size={14} className="text-white/20 hidden lg:block" />
          </div>
        </div>
      </aside>

      {/* 2. MAIN WORKSPACE */}
      <main className="flex-1 flex flex-col relative overflow-hidden z-10">
        
        {/* Header Bar */}
        <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-surface/30 backdrop-blur-md">
          <div className="flex items-center gap-4">
             <div className="flex items-center gap-1 text-[10px] text-white/20 font-bold uppercase tracking-widest">
                Nodes <ChevronRight size={10} /> {view === 'overview' ? 'Dashboard' : 'AI Inquiry'}
             </div>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-[10px] bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full font-bold border border-emerald-500/20 shadow-lg shadow-emerald-500/5">
               <Zap size={12} fill="currentColor" /> LOCAL OLLAMA: PHI-3 ACTIVE
            </div>
            <div className="flex items-center gap-2">
               <button className="p-2 rounded-lg bg-white/5 text-white/40 hover:text-white transition-colors"><Search size={18} /></button>
               <button className="p-2 rounded-lg bg-white/5 text-white/40 hover:text-white transition-colors"><Settings size={18} /></button>
            </div>
          </div>
        </header>

        {/* Dynamic Content Area */}
        <div className="flex-1 flex overflow-hidden">
           {/* Primary View */}
           <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
              <AnimatePresence mode="wait">
                 {view === 'overview' ? (
                    <motion.div key="overview" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="max-w-6xl mx-auto space-y-10">
                       <header>
                          <h2 className="text-4xl font-bold tracking-tighter">Welcome back, John.</h2>
                          <p className="text-white/40 mt-2 text-xl font-light">Here is what the Intelligence Layer synthesized today.</p>
                       </header>
                       
                       <StatsGrid />

                       <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                          <SourceExplorer />
                          <div className="glass-card rounded-3xl p-8 flex flex-col items-center justify-center text-center group border-dashed border-2 border-white/5">
                             <div className="w-20 h-20 rounded-full bg-accent/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-2xl shadow-accent/10">
                                <Sparkles size={40} className="text-accent" />
                             </div>
                             <h3 className="text-2xl font-bold mb-3 tracking-tight">Run Deep Query</h3>
                             <p className="text-white/40 max-w-sm mb-8 text-sm font-medium">Cross-reference SQL metrics with qualitative behavior reports in real-time.</p>
                             <button onClick={() => setView('chat')} className="px-10 py-4 rounded-2xl bg-accent text-white font-bold shadow-2xl shadow-accent/40 hover:bg-accent-hover transition-all active:scale-95 flex items-center gap-3">
                                Start Session <ChevronRight size={18} />
                             </button>
                          </div>
                       </div>
                    </motion.div>
                 ) : (
                    <motion.div key="chat" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 1.02 }} className="h-full flex flex-col max-w-5xl mx-auto">
                       {/* Chat Messages */}
                       <div className="flex-1 space-y-10 pb-40 pt-4">
                          {messages.length === 0 && (
                             <div className="h-full flex flex-col items-center justify-center text-center space-y-8 animate-in fade-in duration-1000">
                                <div className="w-24 h-24 rounded-[40px] bg-white/5 flex items-center justify-center border border-white/10 shadow-inner">
                                   <Cpu size={48} className="text-white/10" />
                                </div>
                                <div className="space-y-3">
                                   <h2 className="text-2xl font-bold tracking-tight text-white/80">Autonomous Analytics Node</h2>
                                   <p className="text-sm text-white/30 max-w-sm leading-relaxed">Ask anything about revenue, movies, or audience trends. I will query SQL and PDF indexes for you.</p>
                                </div>
                                <div className="flex flex-wrap justify-center gap-3">
                                   {["Top 5 revenue movies?", "Summarize behavior reports", "Stellar Run trends"].map(q => (
                                      <button key={q} onClick={() => setInput(q)} className="px-4 py-2 rounded-full bg-white/5 border border-white/5 text-xs text-white/50 hover:bg-accent/10 hover:text-accent transition-all">
                                         {q}
                                      </button>
                                   ))}
                                </div>
                             </div>
                          )}
                          {messages.map((m) => (
                             <div key={m.id} className={clsx("flex gap-8", m.role === 'user' ? "flex-row-reverse" : "")}>
                                <div className={clsx(
                                   "w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 border transition-all duration-700",
                                   m.role === 'user' ? "bg-accent border-white/20 text-white shadow-2xl shadow-accent/40 rotate-12" : "bg-surface border-white/10 text-accent -rotate-12"
                                )}>
                                   {m.role === 'user' ? <User size={24} /> : <Bot size={24} />}
                                </div>
                                <div className="space-y-6 max-w-[85%]">
                                   {m.thought && (
                                      <details className="text-[11px] text-white/30 bg-white/[0.02] p-5 rounded-3xl border border-white/5 group hover:border-accent/20">
                                         <summary className="cursor-pointer hover:text-accent font-bold uppercase tracking-widest flex items-center gap-2">
                                            <Activity size={14} /> Agent Logic Flow
                                         </summary>
                                         <pre className="mt-5 whitespace-pre-wrap font-mono leading-relaxed text-white/40 bg-black/40 p-6 rounded-2xl border border-white/5 shadow-inner">{m.thought}</pre>
                                      </details>
                                   )}
                                   <div className={clsx(
                                      "p-7 rounded-[32px] leading-relaxed text-[17px] shadow-sm",
                                      m.role === 'user' ? "bg-accent text-white border border-white/10 shadow-2xl" : "bg-card/50 backdrop-blur-xl border border-white/5 text-white/90"
                                   )}>
                                      {m.content}
                                   </div>
                                   {m.data && (
                                      <div className="space-y-6 pt-4">
                                         <InsightsDashboard data={m.data} title="Metric Visualization" />
                                         <DataTable data={m.data} />
                                      </div>
                                   )}
                                </div>
                             </div>
                          ))}
                          {isLoading && (
                             <div className="flex gap-8 items-center">
                                <div className="w-12 h-12 rounded-2xl bg-accent/20 border border-accent/20 flex items-center justify-center text-accent animate-spin-slow">
                                   <Sparkles size={24} />
                                </div>
                                <div className="text-white/20 font-bold uppercase tracking-widest text-xs animate-pulse">Processing Cross-Reference Query...</div>
                             </div>
                          )}
                          <div ref={scrollRef} />
                       </div>

                       {/* Input Container */}
                       <div className="fixed bottom-10 left-20 lg:left-64 right-0 lg:right-80 flex justify-center px-12 z-20">
                          <form onSubmit={handleSubmit} className="w-full max-w-4xl relative group">
                             <div className="absolute -inset-1 bg-gradient-to-r from-accent to-violet-500 rounded-[30px] blur opacity-10 group-focus-within:opacity-40 transition-all duration-700" />
                             <div className="relative bg-card/80 backdrop-blur-3xl border border-white/10 rounded-[28px] overflow-hidden flex items-center">
                                <div className="pl-6 text-white/20"><Command size={24} /></div>
                                <input
                                   type="text"
                                   value={input}
                                   onChange={(e) => setInput(e.target.value)}
                                   placeholder="Initiate cross-data analysis..."
                                   className="flex-1 bg-transparent py-6 px-4 focus:outline-none text-lg placeholder:text-white/20"
                                />
                                <button
                                   type="submit"
                                   disabled={isLoading || !input.trim()}
                                   className="mr-4 p-4 rounded-2xl bg-accent text-white disabled:opacity-20 hover:scale-105 transition-all shadow-xl shadow-accent/40 active:scale-95"
                                >
                                   <Send size={24} />
                                </button>
                             </div>
                          </form>
                       </div>
                    </motion.div>
                 )}
              </AnimatePresence>
           </div>

           {/* 3. RIGHT ANALYTICS SIDEBAR (CONTEXT AWARE) */}
           {view === 'chat' && (
              <aside className="w-80 border-l border-white/5 bg-surface/50 backdrop-blur-3xl p-6 space-y-8 hidden xl:block">
                 <div className="space-y-4">
                    <h4 className="text-[11px] font-bold uppercase tracking-widest text-white/30 flex items-center gap-2"><TrendingUp size={14} /> Active Context</h4>
                    <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
                       <p className="text-xs text-white/50 leading-relaxed font-medium">Currently analyzing <span className="text-accent">Marketing Spend vs Viewer Retention</span> across Q1-Q2.</p>
                    </div>
                 </div>

                 <div className="space-y-4">
                    <h4 className="text-[11px] font-bold uppercase tracking-widest text-white/30 flex items-center gap-2"><Sparkles size={14} /> Suggested Dives</h4>
                    <div className="space-y-2">
                       {["Regional ROI Analysis", "Churn Risk Projection", "Content Decay Curve"].map(s => (
                          <button key={s} className="w-full text-left p-3 rounded-xl hover:bg-white/5 text-xs text-white/40 border border-transparent hover:border-white/5 transition-all flex items-center justify-between group">
                             {s} <ChevronRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                          </button>
                       ))}
                    </div>
                 </div>

                 <div className="pt-8 mt-auto">
                    <div className="p-5 rounded-3xl bg-gradient-to-br from-accent/20 to-violet-500/20 border border-accent/20 text-center relative overflow-hidden group">
                       <div className="relative z-10">
                          <h5 className="text-sm font-bold mb-1">Export Executive PDF</h5>
                          <p className="text-[10px] text-white/40 mb-4 font-medium uppercase tracking-tighter">Download session findings</p>
                          <button className="w-full py-2 bg-white text-black text-[11px] font-bold rounded-xl hover:bg-accent hover:text-white transition-all uppercase tracking-widest">Generate Report</button>
                       </div>
                       <FileText size={80} className="absolute -right-4 -bottom-4 text-white/5 rotate-12 group-hover:scale-110 transition-transform" />
                    </div>
                 </div>
              </aside>
           )}
        </div>
      </main>
    </div>
  );
};

const NavItem = ({ icon: Icon, label, active = false, onClick, color = "text-white/30" }: any) => (
  <button 
    onClick={onClick}
    className={clsx(
      "w-full flex items-center gap-4 p-4 rounded-2xl transition-all duration-500 group relative",
      active ? "bg-accent/10 text-accent" : `hover:bg-white/5 ${color}`
    )}
  >
    {active && <motion.div layoutId="nav-glow" className="absolute inset-0 bg-accent/5 rounded-2xl blur-md" />}
    <Icon size={22} className={active ? "text-accent" : "group-hover:text-white/70"} />
    <span className={clsx("text-sm font-semibold lg:block hidden", active ? "text-white" : "group-hover:text-white/70 tracking-tight")}>{label}</span>
    {active && <motion.div layoutId="nav-line" className="ml-auto w-1 h-5 bg-accent rounded-full hidden lg:block" />}
  </button>
);

const clsx = (...classes: any[]) => classes.filter(Boolean).join(' ');
