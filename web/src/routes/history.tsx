import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useState } from 'react';
import { bingoApi, GameHistory } from '../services/api';

const HistoryComponent = () => {
  const [historyItems, setHistoryItems] = useState<GameHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await bingoApi.getHistory();
        setHistoryItems(data);
      } catch (err) {
        setError('Не удалось загрузить историю. Пожалуйста, попробуйте позже.');
        console.error('Error fetching history:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-lg rounded-lg overflow-hidden">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          История карточек
        </h2>

        {error ? (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        ) : (
          <div className="space-y-4">
            {historyItems.map((item) => (
              <div
                key={item.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {item.title}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Размер: {item.size}x{item.size}
                    </p>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Слова: {item.words.slice(0, 3).join(', ')}
                        {item.words.length > 3 && '...'}
                      </p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(item.date).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="mt-2">
                  <button
                    className="text-sm text-blue-600 hover:text-blue-800"
                    onClick={() => {
                      // TODO: Добавить логику повторного использования карточки
                    }}
                  >
                    Использовать снова
                  </button>
                </div>
              </div>
            ))}

            {historyItems.length === 0 && (
              <p className="text-center text-gray-500 py-8">
                История пуста
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export const Route = createFileRoute('/history')({
  component: HistoryComponent,
}); 