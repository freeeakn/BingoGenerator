interface BingoSettings {
  size: number;
  words: string[];
  title: string;
}

interface BingoSettingsProps {
  settings: BingoSettings;
  onSettingsChange: (settings: BingoSettings) => void;
}

export const BingoSettings = ({ settings, onSettingsChange }: BingoSettingsProps) => {
  const handleSizeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onSettingsChange({
      ...settings,
      size: parseInt(event.target.value),
    });
  };

  const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onSettingsChange({
      ...settings,
      title: event.target.value,
    });
  };

  const handleWordsChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const words = event.target.value.split('\n').filter(word => word.trim() !== '');
    onSettingsChange({
      ...settings,
      words,
    });
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6 space-y-6">
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700">
          Название карточки
        </label>
        <input
          type="text"
          id="title"
          value={settings.title}
          onChange={handleTitleChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Введите название карточки"
        />
      </div>

      <div>
        <label htmlFor="size" className="block text-sm font-medium text-gray-700">
          Размер сетки
        </label>
        <select
          id="size"
          value={settings.size}
          onChange={handleSizeChange}
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
          Слова для карточки
        </label>
        <p className="mt-1 text-sm text-gray-500">
          Введите слова или фразы, по одному на строку. Минимальное количество: {settings.size * settings.size}
        </p>
        <textarea
          id="words"
          rows={10}
          value={settings.words.join('\n')}
          onChange={handleWordsChange}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          placeholder="Введите слова или фразы..."
        />
      </div>

      <div className="bg-gray-50 -mx-6 -mb-6 px-6 py-3 flex justify-end space-x-3 rounded-b-lg">
        <button
          type="button"
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          onClick={() => onSettingsChange({
            size: 5,
            words: [],
            title: '',
          })}
        >
          Сбросить
        </button>
        <button
          type="button"
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          onClick={() => {
            // Здесь можно добавить валидацию перед сохранением
            if (settings.words.length < settings.size * settings.size) {
              alert(`Необходимо ввести минимум ${settings.size * settings.size} слов`);
              return;
            }
            // Сохранение настроек
          }}
        >
          Сохранить
        </button>
      </div>
    </div>
  );
}; 