import { useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';

interface Settings {
  darkMode: boolean;
  language: 'ru' | 'en';
  autoSave: boolean;
}

const SettingsComponent = () => {
  const [settings, setSettings] = useState<Settings>({
    darkMode: false,
    language: 'ru',
    autoSave: true,
  });

  const handleSettingChange = (key: keyof Settings, value: boolean | 'ru' | 'en') => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  return (
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Настройки
          </h2>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Тёмная тема
                </h3>
                <p className="text-sm text-gray-500">
                  Включить тёмную тему интерфейса
                </p>
              </div>
              <button
                className={`
                  relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent
                  transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                  ${settings.darkMode ? 'bg-blue-600' : 'bg-gray-200'}
                `}
                onClick={() => handleSettingChange('darkMode', !settings.darkMode)}
              >
                <span
                  className={`
                    pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0
                    transition duration-200 ease-in-out
                    ${settings.darkMode ? 'translate-x-5' : 'translate-x-0'}
                  `}
                />
              </button>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Язык
                </h3>
                <p className="text-sm text-gray-500">
                  Выберите язык интерфейса
                </p>
                <select
                  value={settings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value as 'ru' | 'en')}
                  className="mt-2 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="ru">Русский</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Автосохранение
                  </h3>
                  <p className="text-sm text-gray-500">
                    Автоматически сохранять карточки в историю
                  </p>
                </div>
                <button
                  className={`
                    relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent
                    transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    ${settings.autoSave ? 'bg-blue-600' : 'bg-gray-200'}
                  `}
                  onClick={() => handleSettingChange('autoSave', !settings.autoSave)}
                >
                  <span
                    className={`
                      pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0
                      transition duration-200 ease-in-out
                      ${settings.autoSave ? 'translate-x-5' : 'translate-x-0'}
                    `}
                  />
                </button>
              </div>
            </div>
          </div>

          <div className="mt-8 flex justify-end space-x-3">
            <button
              type="button"
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              onClick={() => {
                setSettings({
                  darkMode: false,
                  language: 'ru',
                  autoSave: true,
                });
              }}
            >
              Сбросить
            </button>
            <button
              type="button"
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              onClick={() => {
                // Здесь будет сохранение настроек
                alert('Настройки сохранены');
              }}
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
  );
};

export const Route = createFileRoute('/settings')({
  component: SettingsComponent,
}); 