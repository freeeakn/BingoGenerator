import { useState } from 'react';
import { bingoApi, BingoCard } from '../services/api';

interface BingoSettings {
  size: number;
  words: string[];
  title: string;
}

interface BingoCell {
  text: string;
  isMarked: boolean;
}

export const BingoGenerator = () => {
  const [settings, setSettings] = useState<BingoSettings>({
    size: 5,
    words: [],
    title: '',
  });

  const [cells, setCells] = useState<BingoCell[]>([]);
  const [isGenerated, setIsGenerated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateBingoCard = async () => {
    if (settings.words.length < settings.size * settings.size) {
      setError(`Необходимо ввести минимум ${settings.size * settings.size} слов`);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await bingoApi.generateCard(settings);
      const newCells = response.words.map(word => ({
        text: word,
        isMarked: false,
      }));

      setCells(newCells);
      setIsGenerated(true);
      
      // Сохраняем карточку в истории
      await bingoApi.saveCard(settings);
    } catch (err) {
      setError('Произошла ошибка при генерации карточки. Пожалуйста, попробуйте снова.');
      console.error('Error generating bingo card:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCellClick = (index: number) => {
    const newCells = [...cells];
    newCells[index] = {
      ...newCells[index],
      isMarked: !newCells[index].isMarked,
    };
    setCells(newCells);
  };

  const handleSettingsChange = (newSettings: BingoSettings) => {
    setSettings(newSettings);
    setIsGenerated(false);
    setError(null);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white shadow-lg rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Генератор Бинго
        </h1>

        {/* Форма настроек */}
        <div className="mb-8">
          <div className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Название карточки
              </label>
              <input
                type="text"
                id="title"
                value={settings.title}
                onChange={(e) => handleSettingsChange({ ...settings, title: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label htmlFor="size" className="block text-sm font-medium text-gray-700">
                Размер карточки
              </label>
              <select
                id="size"
                value={settings.size}
                onChange={(e) => handleSettingsChange({ ...settings, size: Number(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value={3}>3x3</option>
                <option value={4}>4x4</option>
                <option value={5}>5x5</option>
                <option value={6}>6x6</option>
              </select>
            </div>

            <div>
              <label htmlFor="words" className="block text-sm font-medium text-gray-700">
                Слова (по одному в строке)
              </label>
              <textarea
                id="words"
                value={settings.words.join('\n')}
                onChange={(e) => handleSettingsChange({
                  ...settings,
                  words: e.target.value.split('\n').filter(word => word.trim()),
                })}
                rows={6}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                placeholder="Введите слова, каждое с новой строки"
              />
            </div>
          </div>

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <button
            onClick={generateBingoCard}
            disabled={isLoading}
            className={`mt-6 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
              isLoading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Генерация...' : 'Сгенерировать карточку'}
          </button>
        </div>

        {/* Карточка бинго */}
        {isGenerated && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {settings.title || 'Карточка бинго'}
            </h2>
            <div
              className={`grid gap-4`}
              style={{
                gridTemplateColumns: `repeat(${settings.size}, minmax(0, 1fr))`,
              }}
            >
              {cells.map((cell, index) => (
                <div
                  key={index}
                  onClick={() => handleCellClick(index)}
                  className={`aspect-square p-2 flex items-center justify-center text-center border-2 rounded-lg cursor-pointer transition-colors ${
                    cell.isMarked
                      ? 'bg-blue-100 border-blue-500'
                      : 'hover:bg-gray-50 border-gray-200'
                  }`}
                >
                  <span className="text-sm">{cell.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}; 