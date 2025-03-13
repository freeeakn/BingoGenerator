import { createFileRoute } from '@tanstack/react-router';

const AboutComponent = () => {
  return (
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            О проекте
          </h2>

          <div className="prose max-w-none">
            <p className="text-lg text-gray-700 mb-4">
              Bingo Generator - это современный инструмент для создания уникальных карточек бинго для ваших игр и мероприятий.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mt-8 mb-4">
              Возможности
            </h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Создание карточек бинго разных размеров (от 3x3 до 6x6)</li>
              <li>Сохранение истории созданных карточек</li>
              <li>Настраиваемый интерфейс</li>
              <li>Поддержка русского и английского языков</li>
              <li>Возможность повторного использования карточек</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mt-8 mb-4">
              Технологии
            </h3>
            <ul className="list-disc list-inside space-y-2 text-gray-700">
              <li>Frontend: React, TypeScript, Tailwind CSS</li>
              <li>Backend: Python, FastAPI</li>
              <li>База данных: PostgreSQL</li>
              <li>Контейнеризация: Docker</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mt-8 mb-4">
              Разработка
            </h3>
            <p className="text-gray-700 mb-4">
              Проект разрабатывается с открытым исходным кодом. Вы можете внести свой вклад в развитие проекта на GitHub.
            </p>

            <div className="mt-8 flex space-x-4">
              <a
                href="https://github.com/yourusername/BingoGenerator"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-gray-800 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              >
                GitHub Repository
              </a>
              <a
                href="https://github.com/yourusername/BingoGenerator/issues"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Сообщить о проблеме
              </a>
            </div>
          </div>
        </div>
      </div>
  );
};

export const Route = createFileRoute('/about')({
  component: AboutComponent,
}); 