import { Link } from '@tanstack/react-router';
import Aurora from '../background/Aurora';

export const Header = () => {
  return (
    <header className="relative p-4">
        <div className="absolute top-0 left-0 w-full h-full">
            <Aurora
            colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
            blend={0.5}
            amplitude={1.0}
            speed={0.5}
            />
        </div>
        <div className="relative z-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                <div className="flex-shrink-0">
                    <Link to="/" className="flex items-center">
                    <img src="logo.svg" alt="Bingo" className="h-24" />
                    </Link>
                </div>
                
                <nav className="hidden sm:flex space-x-8">
                    <Link
                    to="/"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    activeProps={{ className: 'text-blue-600' }}
                    >
                    Главная
                    </Link>
                    <Link
                    to="/history"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    activeProps={{ className: 'text-blue-600' }}
                    >
                    История
                    </Link>
                    <Link
                    to="/settings"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    activeProps={{ className: 'text-blue-600' }}
                    >
                    Настройки
                    </Link>
                    <Link
                    to="/about"
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
                    activeProps={{ className: 'text-blue-600' }}
                    >
                    О проекте
                    </Link>
                </nav>

                <div className="sm:hidden">
                    <button
                    type="button"
                    className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                    aria-controls="mobile-menu"
                    aria-expanded="false"
                    >
                    <span className="sr-only">Open main menu</span>
                    <svg
                        className="block h-6 w-6"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        aria-hidden="true"
                    >
                        <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 6h16M4 12h16M4 18h16"
                        />
                    </svg>
                    </button>
                </div>
                </div>
            </div>

            {/* Mobile menu */}
            <div className="sm:hidden" id="mobile-menu">
                <div className="px-2 pt-2 pb-3 space-y-1">
                <Link
                    to="/"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100"
                    activeProps={{ className: 'text-blue-600 bg-gray-100' }}
                >
                    Главная
                </Link>
                <Link
                    to="/history"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100"
                    activeProps={{ className: 'text-blue-600 bg-gray-100' }}
                >
                    История
                </Link>
                <Link
                    to="/settings"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100"
                    activeProps={{ className: 'text-blue-600 bg-gray-100' }}
                >
                    Настройки
                </Link>
                <Link
                    to="/about"
                    className="block px-3 py-2 rounded-md text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-gray-100"
                    activeProps={{ className: 'text-blue-600 bg-gray-100' }}
                >
                    О проекте
                </Link>
                </div>
            </div>
        </div>
    </header>
  );
}; 