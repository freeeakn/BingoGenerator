import { createFileRoute } from '@tanstack/react-router';

interface HistoryItem {
  id: string;
  title: string;
  date: string;
  size: number;
  words: string[];
}

const HistoryComponent = () => {
  // В реальном приложении здесь будет загрузка истории из API
  const historyItems: HistoryItem[] = [
    {
      id: '1',
      title: 'Тестовая карточка',
      date: '2024-03-13',
      size: 5,
      words: ['Слово 1', 'Слово 2', '...'],
    },
  ];

  return (
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            История карточек
          </h2>

          <div className="space-y-4">
            {historyItems.map((item) => (
              <div
                key={item.id}
                className="border rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {item.title}
                    </h3>
                    <p className="text-sm text-gray-500">
                      Размер: {item.size}x{item.size}
                    </p>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(item.date).toLocaleDateString()}
                  </span>
                </div>
                
                <div className="mt-2">
                  <button
                    className="text-sm text-blue-600 hover:text-blue-800"
                    onClick={() => {
                      // Здесь будет логика повторного использования карточки
                    }}
                  >
                    Использовать снова
                  </button>
                </div>
              </div>
            ))}
          </div>

          {historyItems.length === 0 && (
            <p className="text-center text-gray-500 py-8">
              История пуста
            </p>
          )}
        </div>
      </div>
  );
};

export const Route = createFileRoute('/history')({
  component: HistoryComponent,
}); 