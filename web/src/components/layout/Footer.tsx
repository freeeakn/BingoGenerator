import { Link } from '@tanstack/react-router';

export const Footer = () => {
  return (
    <footer className="bg-gray-50">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-sm font-semibold text-gray-600 tracking-wider uppercase">О проекте</h3>
            <p className="mt-4 text-base text-gray-500">
              Bingo Generator - инструмент для создания уникальных карточек бинго для ваших игр и мероприятий.
            </p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-600 tracking-wider uppercase">Навигация</h3>
            <ul className="mt-4 space-y-4">
              <li>
                <Link to="/" className="text-base text-gray-500 hover:text-gray-900">
                  Главная
                </Link>
              </li>
              <li>
                <Link to="/history" className="text-base text-gray-500 hover:text-gray-900">
                  История
                </Link>
              </li>
              <li>
                <Link to="/settings" className="text-base text-gray-500 hover:text-gray-900">
                  Настройки
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-600 tracking-wider uppercase">Контакты</h3>
            <ul className="mt-4 space-y-4">
              <li>
                <a href="https://github.com/yourusername/BingoGenerator" className="text-base text-gray-500 hover:text-gray-900">
                  GitHub
                </a>
              </li>
              <li>
                <a href="mailto:support@bingogenerator.com" className="text-base text-gray-500 hover:text-gray-900">
                  Поддержка
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 border-t border-gray-200 pt-8">
          <p className="text-base text-gray-400 text-center">
            &copy; {new Date().getFullYear()} Bingo Generator. Все права защищены.
          </p>
        </div>
      </div>
    </footer>
  );
}; 