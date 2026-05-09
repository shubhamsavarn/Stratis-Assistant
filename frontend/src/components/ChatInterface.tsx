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

   const handleSubmit = async (e?: React.FormEvent, customQuery?: string) => {
      if (e) e.preventDefault();
      const queryToUse = customQuery || input;
      if (!queryToUse.trim() || isLoading) return;

      if (view === 'overview') setView('chat');

      const userMsg: Message = { id: Date.now().toString(), role: 'user', content: queryToUse };
      setMessages(prev => [...prev, userMsg]);
      setInput('');
      setIsLoading(true);

      try {
         const res = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
               'Content-Type': 'application/json',
               'X-API-KEY': 'sk-insight-flow-2025'
            },
            body: JSON.stringify({ query: queryToUse }),
         });
         const data = await res.json();

         const assistantMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: data.answer,
            thought: data.thought_trace,
            data: data.data || null
         };

         setMessages(prev => [...prev, assistantMsg]);
         if (data.data) setActiveData(data.data);
      } catch (err) {
         console.error(err);
      } finally {
         setIsLoading(false);
      }
   };

   return (
      <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-accent/30 relative">

         {/* 1. LEFT NAVIGATION */}
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
                  <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center text-accent text-xs font-bold">SJ</div>
                  <div className="hidden lg:block flex-1 overflow-hidden">
                     <p className="text-xs font-bold truncate">Shubham Savarn</p>
                  </div>
                  <LogOut size={14} className="text-white/20 hidden lg:block" />
               </div>
            </div>
         </aside>

         {/* 2. MAIN WORKSPACE */}
         <main className="flex-1 flex flex-col relative overflow-hidden z-10">

            {/* Header Bar */}
            <header className="h-16 border-b border-white/5 flex items-center justify-between px-8 bg-surface/30 backdrop-blur-md shrink-0">
               <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1 text-[10px] text-white/20 font-bold uppercase tracking-widest">
                     Nodes <ChevronRight size={10} /> {view === 'overview' ? 'Dashboard' : 'AI Inquiry'}
                  </div>
               </div>
               <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2 text-[10px] bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full font-bold border border-emerald-500/20 shadow-lg shadow-emerald-500/5">
                     <Zap size={12} fill="currentColor" /> LOCAL OLLAMA: QWEN2.5 ACTIVE
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
                              <h2 className="text-4xl font-bold tracking-tighter text-white">Welcome back.</h2>
                              <p className="text-white/40 mt-2 text-xl font-light">Here is what the Intelligence Layer synthesized today.</p>
                           </header>
                           <StatsGrid />
                           <SourceExplorer />
                        </motion.div>
                     ) : (
                        <motion.div key="chat" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="max-w-4xl mx-auto space-y-12 pb-32">
                           {messages.length === 0 ? (
                              <div className="h-full flex flex-col items-center justify-center text-center space-y-8 animate-in fade-in duration-1000">
                                 <div className="w-24 h-24 rounded-[40px] bg-white/5 flex items-center justify-center border border-white/10 shadow-inner">
                                    <Cpu size={48} className="text-white/10" />
                                 </div>
                                 <div className="space-y-3">
                                    <h2 className="text-2xl font-bold tracking-tight text-white/80">Autonomous Analytics Node</h2>
                                 </div>
                              </div>
                           ) : (
                              messages.map((m) => (
                                 <div key={m.id} className={clsx("flex gap-8", m.role === 'user' ? "flex-row-reverse" : "")}>
                                    <div className={clsx(
                                       "w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 border transition-all duration-700",
                                       m.role === 'user' ? "bg-accent border-white/20 text-white shadow-2xl" : "bg-surface border-white/10 text-accent"
                                    )}>
                                       {m.role === 'user' ? <User size={20} /> : <Bot size={20} />}
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
                                          "p-6 rounded-[28px] leading-relaxed text-[16px]",
                                          m.role === 'user' ? "bg-accent text-white border border-white/10" : "bg-card border border-white/5 text-white/90"
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
                              ))
                           )}
                           {isLoading && (
                              <div className="flex gap-8 items-center">
                                 <div className="w-10 h-10 rounded-2xl bg-accent/20 border border-accent/20 flex items-center justify-center text-accent animate-pulse">
                                    <Sparkles size={20} />
                                 </div>
                                 <div className="text-white/20 font-bold uppercase tracking-widest text-[10px]">Synthesizing...</div>
                              </div>
                           )}
                           <div ref={scrollRef} />
                        </motion.div>
                     )}
                  </AnimatePresence>
               </div>

               {/* 3. RIGHT SIDEBAR: INTELLIGENCE PANEL (Selectors & Filters) */}
               {view === 'chat' && (
                  <aside className="w-80 border-l border-white/5 bg-surface/20 backdrop-blur-3xl hidden xl:flex flex-col p-6 space-y-8 overflow-y-auto custom-scrollbar shrink-0">
                     <div className="space-y-6">
                        <div className="flex items-center gap-2 text-white/40">
                           <LayoutDashboard size={14} />
                           <span className="text-[10px] font-bold uppercase tracking-widest">BI Selectors</span>
                        </div>

                        {/* MARKET SELECTORS */}
                        <div className="space-y-3">
                           <p className="text-[10px] text-white/20 uppercase font-bold tracking-tighter">Genre Focus</p>
                           <div className="flex flex-wrap gap-2">
                              {['Action', 'Sci-Fi', 'Comedy', 'Drama'].map(genre => (
                                 <button
                                    key={genre}
                                    onClick={() => handleSubmit(undefined, `How did ${genre} perform this year?`)}
                                    className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/5 text-[10px] font-medium text-white/40 hover:bg-accent/10 hover:text-accent transition-all"
                                 >
                                    {genre}
                                 </button>
                              ))}
                           </div>
                        </div>

                        {/* TIMEFRAME SELECTORS */}
                        <div className="space-y-3 pt-4">
                           <p className="text-[10px] text-white/20 uppercase font-bold tracking-tighter">Timeline</p>
                           <div className="grid grid-cols-2 gap-2">
                              {['2024 Analysis', '2025 Forecast'].map(year => (
                                 <button
                                    key={year}
                                    onClick={() => handleSubmit(undefined, `Best titles in ${year.split(' ')[0]}?`)}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 text-[10px] font-medium text-white/40 hover:bg-accent/10 hover:text-accent transition-all text-center"
                                 >
                                    {year}
                                 </button>
                              ))}
                           </div>
                        </div>
                     </div>

                     <div className="h-px bg-white/5" />

                     {/* ACTIVE DASHBOARD (Insights Panel) */}
                     <div className="space-y-4 flex-1">
                        <div className="flex items-center gap-2 text-white/40">
                           <TrendingUp size={14} />
                           <span className="text-[10px] font-bold uppercase tracking-widest">Active Synthesis</span>
                        </div>

                        {activeData ? (
                           <div className="scale-90 origin-top -mt-4">
                              <InsightsDashboard data={activeData} title="Current Focus" />
                           </div>
                        ) : (
                           <div className="flex flex-col items-center justify-center h-40 text-center space-y-3 opacity-20">
                              <Sparkles size={24} />
                              <p className="text-[10px] font-medium italic">Ask a data query...</p>
                           </div>
                        )}
                     </div>
                  </aside>
               )}
            </div>

            {/* Floating Input Area (Positioned relative to the workspace) */}
            {view === 'chat' && (
               <div className="fixed bottom-10 left-20 lg:left-64 right-0 lg:right-80 flex justify-center px-12 z-20">
                  <form onSubmit={handleSubmit} className="w-full max-w-4xl relative group">
                     <div className="absolute -inset-1 bg-gradient-to-r from-accent to-violet-500 rounded-[30px] blur opacity-10 group-focus-within:opacity-40 transition-all duration-700" />
                     <div className="relative bg-card/80 backdrop-blur-3xl border border-white/10 rounded-[28px] overflow-hidden flex items-center shadow-2xl">
                        <div className="pl-6 text-white/20"><Command size={24} /></div>
                        <input
                           type="text"
                           value={input}
                           onChange={(e) => setInput(e.target.value)}
                           placeholder="Initiate cross-data analysis..."
                           className="flex-1 bg-transparent border-none py-6 px-4 text-white placeholder:text-white/20 focus:outline-none text-sm font-medium"
                        />
                        <button
                           type="submit"
                           disabled={isLoading}
                           className="mr-3 w-12 h-12 rounded-2xl bg-accent hover:bg-accent-hover flex items-center justify-center text-white shadow-lg shadow-accent/20 transition-all active:scale-95 disabled:opacity-50"
                        >
                           {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
                        </button>
                     </div>
                  </form>
               </div>
            )}
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
