import React from 'react';
import { 
  Github, 
  Key, 
  Terminal, 
  CheckCircle2, 
  AlertTriangle, 
  ExternalLink, 
  Clock, 
  Zap,
  ShieldCheck,
  Code2
} from 'lucide-react';
import { motion } from 'motion/react';

const SECRET_LIST = [
  { name: 'LINKEDIN_COOKIE', description: 'The "li_at" cookie from your LinkedIn session.', required: true },
  { name: 'NAUKRI_SID', description: 'The "nauk_sid" cookie from your Naukri session.', required: true },
  { name: 'TELEGRAM_BOT_TOKEN', description: 'Your Telegram Bot Token (from @BotFather).', required: false },
  { name: 'TELEGRAM_CHAT_ID', description: 'Your Telegram Chat ID (to receive questions).', required: false },
  { name: 'NAUKRI_NKWAP', description: 'The "NKWAP" cookie from your Naukri session.', required: false },
  { name: 'LINKEDIN_EMAIL', description: 'Your LinkedIn email (fallback if cookie fails).', required: false },
  { name: 'LINKEDIN_PASSWORD', description: 'Your LinkedIn password (fallback if cookie fails).', required: false },
];

export default function App() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-emerald-500/30">
      {/* Header */}
      <header className="border-b border-zinc-800 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center text-zinc-950">
              <Zap size={20} fill="currentColor" />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">Job Automation</h1>
              <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">GitHub Actions Edition</p>
            </div>
          </div>
          <div className="flex items-center gap-2 px-3 py-1 bg-zinc-900 border border-zinc-800 rounded-full">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs font-medium text-zinc-400">System Ready</span>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12 space-y-12">
        {/* Hero Section */}
        <section className="space-y-4">
          <h2 className="text-4xl font-black tracking-tight sm:text-5xl">
            Automation <span className="text-emerald-500">Enhanced.</span>
          </h2>
          <p className="text-zinc-400 max-w-2xl leading-relaxed">
            Your job application bots are now equipped with <strong>Stealth Mode</strong> and <strong>Advanced Error Handling</strong>. 
            If a run fails, you can now download screenshots and logs directly from the GitHub Actions dashboard.
          </p>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Left Column: Instructions */}
          <div className="lg:col-span-7 space-y-10">
            {/* Step 1: GitHub Secrets */}
            <section className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-zinc-900 border border-zinc-800 rounded-lg flex items-center justify-center text-emerald-500">
                  <Key size={16} />
                </div>
                <h3 className="text-xl font-bold">1. Configure GitHub Secrets</h3>
              </div>
              <p className="text-sm text-zinc-400">
                Go to your GitHub Repository → <strong>Settings</strong> → <strong>Secrets and variables</strong> → <strong>Actions</strong>. 
                Add the following secrets:
              </p>
              <div className="space-y-3">
                {SECRET_LIST.map((secret) => (
                  <div key={secret.name} className="p-4 bg-zinc-900/50 border border-zinc-800 rounded-2xl group hover:border-zinc-700 transition-colors">
                    <div className="flex items-center justify-between mb-1">
                      <code className="text-emerald-400 font-mono font-bold">{secret.name}</code>
                      {secret.required && (
                        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Required</span>
                      )}
                    </div>
                    <p className="text-xs text-zinc-500">{secret.description}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Step 2: Debugging */}
            <section className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-zinc-900 border border-zinc-800 rounded-lg flex items-center justify-center text-emerald-500">
                  <AlertTriangle size={16} />
                </div>
                <h3 className="text-xl font-bold">2. Debugging Failures</h3>
              </div>
              <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-3xl space-y-4">
                <p className="text-xs text-zinc-500">
                  If the automation fails, follow these steps:
                </p>
                <ul className="space-y-3 text-xs text-zinc-400 list-disc pl-4">
                  <li>Go to the <strong>Actions</strong> tab in GitHub.</li>
                  <li>Click on the failed run.</li>
                  <li>Scroll down to the <strong>Artifacts</strong> section.</li>
                  <li>Download <strong>automation-results</strong> to see logs and error screenshots.</li>
                  <li>Check if your cookies (<code className="text-emerald-400">li_at</code> or <code className="text-emerald-400">nauk_sid</code>) have expired.</li>
                </ul>
              </div>
            </section>
          </div>

          {/* Right Column: Status & Files */}
          <div className="lg:col-span-5 space-y-8">
            {/* File Structure */}
            <section className="p-8 bg-zinc-900 border border-zinc-800 rounded-3xl space-y-6">
              <div className="flex items-center gap-2 text-zinc-400">
                <Code2 size={16} />
                <span className="text-[10px] font-bold uppercase tracking-widest">Repository Structure</span>
              </div>
              <div className="font-mono text-xs space-y-2 text-zinc-500">
                <div className="flex items-center gap-2">
                  <span className="text-emerald-500">/</span> .github/workflows/
                </div>
                <div className="flex items-center gap-2 pl-4">
                  <CheckCircle2 size={12} className="text-emerald-500" /> job_automation.yml
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-emerald-500">/</span> automation/
                </div>
                <div className="flex items-center gap-2 pl-4">
                  <CheckCircle2 size={12} className="text-emerald-500" /> linkedin_bot.py
                </div>
                <div className="flex items-center gap-2 pl-4">
                  <CheckCircle2 size={12} className="text-emerald-500" /> naukri_bot.py
                </div>
                <div className="flex items-center gap-2 pl-4">
                  <CheckCircle2 size={12} className="text-emerald-500" /> requirements.txt
                </div>
              </div>
            </section>

            {/* Security Note */}
            <section className="p-8 bg-emerald-500/5 border border-emerald-500/20 rounded-3xl space-y-4">
              <div className="flex items-center gap-2 text-emerald-500">
                <ShieldCheck size={20} />
                <h4 className="font-bold">Security First</h4>
              </div>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Using cookies (<code className="text-emerald-400">li_at</code>, <code className="text-emerald-400">nauk_sid</code>) is the safest way to automate without triggering security checkpoints. 
                <strong>Never</strong> hardcode these in your scripts—always use GitHub Secrets.
              </p>
            </section>

            {/* Quick Links */}
            <div className="space-y-3">
              <a 
                href="https://github.com/new" 
                target="_blank" 
                rel="noreferrer"
                className="w-full p-4 bg-zinc-100 text-zinc-950 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-white transition-colors"
              >
                <Github size={18} />
                Create GitHub Repo
                <ExternalLink size={14} />
              </a>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-5xl mx-auto px-6 py-12 border-t border-zinc-900">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <p className="text-xs text-zinc-500">© 2026 Job Automation Engine. Built for GitHub Actions.</p>
          <div className="flex items-center gap-6 text-xs font-medium text-zinc-600">
            <span className="flex items-center gap-1"><CheckCircle2 size={12} /> Playwright Ready</span>
            <span className="flex items-center gap-1"><CheckCircle2 size={12} /> Python 3.11</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
