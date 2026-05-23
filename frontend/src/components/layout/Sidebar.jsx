import React from 'react';
import { 
  Shield, 
  Activity, 
  History, 
  Zap
} from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'investigate', label: 'Investigate', icon: Zap },
    { id: 'dashboard', label: 'Dashboard', icon: Activity, hidden: activeTab !== 'dashboard' },
    { id: 'history', label: 'Audit History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: Shield },
  ];

  return (
    <div className="sidebar">
      <div className="logo mb-12 flex items-center gap-3">
        <Shield className="text-primary" size={28} />
        <span className="text-gradient font-bold text-xl">Forensic AI</span>
      </div>

      <nav className="flex flex-col">
        {menuItems.map((item) => (
          !item.hidden && (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`nav-link ${activeTab === item.id ? 'active' : ''}`}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </button>
          )
        ))}
      </nav>

      <div className="mt-auto">
        <div className="glass p-4 rounded-xl">
          <p className="text-xs text-muted font-bold uppercase mb-1">Engine Status</p>
          <p className="text-sm text-white">WavLM + ConvNext<br/>Consensus Active</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
