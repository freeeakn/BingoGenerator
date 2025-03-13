import { useState } from 'react';
import { BingoCard } from './BingoCard';
import { BingoSettings } from './BingoSettings';

interface BingoCell {
  text: string;
  isMarked: boolean;
}

interface BingoSettings {
  size: number;
  words: string[];
  title: string;
}

export const BingoGenerator = () => {
  const [settings, setSettings] = useState<BingoSettings>({
    size: 5,
    words: [],
    title: '',
  });

  const [cells, setCells] = useState<BingoCell[]>([]);
  const [isGenerated, setIsGenerated] = useState(false);

  const generateBingoCard = () => {
    if (settings.words.length < settings.size * settings.size) {
      alert(`Необходимо ввести минимум ${settings.size * settings.size} слов`);
      return;
    }

    // Перемешиваем слова
    const shuffledWords = [...settings.words].sort(() => Math.random() - 0.5);
    const selectedWords = shuffledWords.slice(0, settings.size * settings.size);

    // Создаем ячейки
    const newCells = selectedWords.map(word => ({
      text: word,
      isMarked: false,
    }));

    setCells(newCells);
    setIsGenerated(true);
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
  };

  return (
    <div className="space-y-8">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Генератор карточек бинго
          </h2>
          
          <BingoSettings
            settings={settings}
            onSettingsChange={handleSettingsChange}
          />
          
          <div className="mt-6 flex justify-center">
            <button
              onClick={generateBingoCard}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Сгенерировать карточку
            </button>
          </div>
        </div>
      </div>

      {isGenerated && (
        <div className="animate-fade-in">
          <BingoCard
            cells={cells}
            size={settings.size}
            onCellClick={handleCellClick}
            title={settings.title}
          />
        </div>
      )}
    </div>
  );
}; 