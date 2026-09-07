import React, { useState, useEffect } from 'react';
import { Sun, Moon } from '@phosphor-icons/react';

export const GreetingRow: React.FC = () => {
  const [timeStr, setTimeStr] = useState<string>('');
  const [dateStr, setDateStr] = useState<string>('');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setDateStr(
        now.toLocaleDateString('en-US', {
          weekday: 'short',
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        })
      );
      setTimeStr(
        now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true,
        })
      );
    };

    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = (dark: boolean) => {
    setIsDarkMode(dark);
    if (dark) {
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
      {/* Greeting Title */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-gray-900">
          Good Day!
        </h2>
        <p className="text-xs text-gray-400 font-medium">
          Ready to inspect and detect defects
        </p>
      </div>

      {/* Date, Time & Theme Toggle */}
      <div className="flex items-center gap-4">
        <div className="text-right font-mono">
          <span className="block text-[11px] font-medium text-gray-400">
            {dateStr}
          </span>
          <span className="block text-base font-bold text-gray-800 leading-tight">
            {timeStr}
          </span>
        </div>

        {/* Sun / Moon Toggle Pill */}
        <div className="flex items-center rounded-xl border border-gray-200 bg-white p-1 shadow-xs">
          <button
            type="button"
            onClick={() => toggleTheme(false)}
            className={`rounded-lg p-1.5 transition-all cursor-pointer ${
              !isDarkMode
                ? 'bg-blue-50 text-blue-600 shadow-xs'
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title="Light Theme"
          >
            <Sun size={18} weight={!isDarkMode ? 'fill' : 'regular'} />
          </button>
          <button
            type="button"
            onClick={() => toggleTheme(true)}
            className={`rounded-lg p-1.5 transition-all cursor-pointer ${
              isDarkMode
                ? 'bg-blue-50 text-blue-600 shadow-xs'
                : 'text-gray-400 hover:text-gray-600'
            }`}
            title="Dark Theme"
          >
            <Moon size={18} weight={isDarkMode ? 'fill' : 'regular'} />
          </button>
        </div>
      </div>
    </div>
  );
};
