import React from 'react';
import {
  House,
  Crosshair,
  ClockCounterClockwise,
  Gear,
  Question,
  Sparkle,
} from '@phosphor-icons/react';

interface SidebarProps {
  activeTab: string;
  onSelectTab: (tabId: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onSelectTab }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <House size={18} weight="fill" /> },
    { id: 'inspection', label: 'Inspection', icon: <Crosshair size={18} /> },
    { id: 'history', label: 'History', icon: <ClockCounterClockwise size={18} /> },
    { id: 'settings', label: 'Settings', icon: <Gear size={18} /> },
    { id: 'help', label: 'Help', icon: <Question size={18} /> },
  ];

  return (
    <aside className="w-56 shrink-0 bg-white border-r border-[#E5EBF5] flex flex-col justify-between p-4 min-h-screen sticky top-0 h-screen">
      <div>
        {/* Logo / Brand Header */}
        <div
          onClick={() => onSelectTab('dashboard')}
          className="flex items-center gap-3 px-2 py-3 mb-6 cursor-pointer hover:opacity-90 transition-opacity"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 to-blue-500 text-white shadow-md shadow-blue-500/25">
            <Crosshair size={22} weight="bold" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-gray-900 leading-tight">
              Inspec-Belt AI
            </h1>
            <p className="text-[10px] text-gray-400 font-medium">AOI Sorting Suite</p>
          </div>
        </div>

        {/* Navigation Menu Links */}
        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-md shadow-blue-500/25 font-semibold'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <span className={isActive ? 'text-white' : 'text-gray-400'}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Branding / Vision Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-blue-50/60 to-blue-100/40 p-4 border border-blue-100/60 text-center">
        <div className="absolute -bottom-6 -right-6 h-20 w-20 rounded-full bg-blue-200/40 blur-xl pointer-events-none" />
        <div className="mx-auto mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white shadow-sm">
          <Sparkle size={16} weight="fill" />
        </div>
        <p className="text-xs font-bold text-gray-800">Quality Beyond Vision</p>
        <div className="mt-2 flex items-center justify-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
          <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-700">
            Inspec-Belt AI
          </span>
        </div>
      </div>
    </aside>
  );
};
