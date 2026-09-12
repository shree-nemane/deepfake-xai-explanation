import React from 'react';
import { 
  FileAudio, 
  FileText, 
  History, 
  BarChart3, 
  Fingerprint
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab, hasActiveResult }) => {
  const menuItems = [
    { 
      id: 'investigate', 
      label: 'New Investigation', 
      icon: FileAudio 
    },
    { 
      id: 'dashboard', 
      label: 'Forensic Report', 
      icon: FileText,
      badge: hasActiveResult ? 'Active' : null,
      badgeType: hasActiveResult ? 'success' : null,
    },
    { 
      id: 'history', 
      label: 'Audit History', 
      icon: History 
    },
    { 
      id: 'analytics', 
      label: 'System Telemetry', 
      icon: BarChart3 
    },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="logo mb-8 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center shrink-0">
          <Fingerprint className="text-primary" size={22} />
        </div>
        <div className="min-w-0">
          <span className="text-gradient font-bold text-lg" style={{ display: 'block', lineHeight: 1.2 }}>
            Forensic AI
          </span>
          <span className="text-[10px] text-muted uppercase tracking-wider font-mono">
            Intelligence Suite
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
            title={item.label}
          >
            <item.icon size={18} className="shrink-0" />
            <span className="text-sm font-medium flex-1 text-left">{item.label}</span>
            {item.badge && (
              <span 
                className="text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider font-mono"
                style={{ 
                  background: item.badgeType === 'success' ? 'var(--success-soft)' : 'var(--primary-soft)',
                  color: item.badgeType === 'success' ? 'var(--success)' : 'var(--primary-light)',
                  border: `1px solid ${item.badgeType === 'success' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(0, 210, 255, 0.2)'}`
                }}
              >
                {item.badge}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Real System Telemetry Footer */}
      <div className="mt-auto flex flex-col gap-3 pt-6 border-t border-white/5">
        <div className="glass p-3 rounded-xl">
          <div className="flex items-center gap-2 mb-1.5">
            <div className="pulse-dot" style={{ background: 'var(--success)' }} />
            <span className="text-[10px] text-success font-bold uppercase tracking-wider font-mono">
              Engine Ready
            </span>
          </div>
          <p className="text-xs text-white font-medium">4 Forensic Agents Active</p>
          <p className="text-[10px] text-muted mt-0.5">ConvNeXt · WavLM · Bio · Signal</p>
        </div>
        <div className="text-center">
          <span className="text-[10px] text-muted font-mono" style={{ opacity: 0.5 }}>
            v2.0 · Localhost :8000
          </span>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
