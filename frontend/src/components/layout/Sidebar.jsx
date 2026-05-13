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
      <div className="logo mb-12">
        <Shield className="text-primary" size={32} />
        <span className="text-gradient">Forensic AI</span>
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
          <p className="text-[10px] text-muted font-bold uppercase mb-1">Engine Status</p>
          <p className="text-[10px] text-white">ConvNext-Tiny-V1 Active</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
