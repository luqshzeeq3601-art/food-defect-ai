import React, { useState, useEffect } from 'react';
import { Sun, Moon, CalendarBlank, Clock } from '@phosphor-icons/react';

export const Header: React.FC = () => {
  const [isDark, setIsDark] = useState<boolean>(() => {
    if (typeof window !== 'undefined') {
      return (
        localStorage.getItem('aoi_theme') === 'dark' ||
        document.documentElement.classList.contains('dark')
      );
    }
    return false;
  });

  const [now, setNow] = useState<Date>(() => new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setNow(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('aoi_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('aoi_theme', 'light');
    }
  }, [isDark]);

  const dateStr = now.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const timeStr = now.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
  });

  const toggleTheme = () => {
    setIsDark((prev) => !prev);
  };

  return (
    <header className="bg-white dark:bg-[#16191E] border-b border-[#E5EBF5] dark:border-[#262B33] px-4 sm:px-6 py-2.5 flex items-center justify-between gap-3 shadow-[0_1px_3px_rgba(0,0,0,0.02)]">
      {/* Left: Brand & Subtitle */}
      <div className="flex items-center gap-3">
        {/* Hexagon AOI Logo Icon */}
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-[#1E40AF] to-[#2563EB] text-white shadow-xs">
          <svg
            viewBox="0 0 24 24"
            className="h-5 w-5 fill-none stroke-current stroke-2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2l8.5 4.9v9.8L12 21.5 3.5 16.7V6.9L12 2z" />
            <circle cx="12" cy="12" r="3" />
            <path d="M12 9v-2M12 17v-2M9 12H7M17 12h-2" />
          </svg>
        </div>

        <div>
          <h1 className="text-base sm:text-lg font-extrabold tracking-tight text-gray-900 dark:text-white leading-tight">
            Inspec-Belt AI
          </h1>
          <p className="hidden sm:block text-xs text-gray-500 dark:text-slate-400 font-medium">
            Automated Optical Surface Defect Quantification & Quality Sorting Pipeline
          </p>
        </div>
      </div>

      {/* Right: Theme Toggle & Actual Calendar + Realtime Clock */}
      <div className="flex items-center gap-2 sm:gap-3 text-xs shrink-0">
        {/* Sun / Moon Theme Toggle */}
        <button
          type="button"
          onClick={toggleTheme}
          className="rounded-lg p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-100 dark:text-slate-400 dark:hover:text-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer"
          title="Toggle Theme"
        >
          {isDark ? <Moon size={16} weight="fill" /> : <Sun size={16} />}
        </button>

        <span className="text-gray-200 dark:text-slate-700">|</span>

        {/* Live Actual Calendar & Realtime Clock */}
        <div className="flex items-center gap-3 bg-slate-50 dark:bg-[#1A1F26] border border-slate-200/80 dark:border-slate-800 rounded-xl px-3.5 py-1.5 shadow-2xs">
          <div className="flex items-center gap-1.5 text-slate-600 dark:text-slate-300 font-medium text-xs">
            <CalendarBlank size={15} weight="bold" className="text-blue-600 dark:text-sky-400" />
            <span className="whitespace-nowrap">{dateStr}</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">•</span>
          <div className="flex items-center gap-1.5 text-slate-900 dark:text-slate-100 font-mono font-bold text-xs tabular-nums">
            <Clock size={15} weight="bold" className="text-blue-600 dark:text-sky-400" />
            <span>{timeStr}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
