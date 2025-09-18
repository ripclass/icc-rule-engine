import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  CheckSquare,
  Heart,
  Upload,
  Play
} from 'lucide-react';

const Sidebar: React.FC = () => {
  const navItems = [
    {
      path: '/',
      icon: LayoutDashboard,
      label: 'Dashboard'
    },
    {
      path: '/rules',
      icon: BookOpen,
      label: 'Rules'
    },
    {
      path: '/validation',
      icon: CheckSquare,
      label: 'Validation'
    },
    {
      path: '/health',
      icon: Heart,
      label: 'Health'
    }
  ];

  const quickActions = [
    {
      path: '/rules/upload',
      icon: Upload,
      label: 'Upload Rulebook'
    },
    {
      path: '/validation/new',
      icon: Play,
      label: 'Run Validation'
    }
  ];

  return (
    <div className="bg-white dark:bg-gray-800 shadow-lg h-full flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900 dark:text-white">
              ICC Rule Engine
            </h1>
            <p className="text-xs text-gray-500 dark:text-gray-400">v1.0.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <div className="space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
            Main Menu
          </h3>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>

        <div className="mt-8 space-y-2">
          <h3 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
            Quick Actions
          </h3>
          {quickActions.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className="flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          © 2024 ICC Rule Engine
        </div>
      </div>
    </div>
  );
};

export default Sidebar;