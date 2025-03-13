interface BingoCell {
  text: string;
  isMarked: boolean;
}

interface BingoCardProps {
  cells: BingoCell[];
  size?: number;
  onCellClick?: (index: number) => void;
  title?: string;
}

export const BingoCard = ({ cells, size = 5, onCellClick, title }: BingoCardProps) => {
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${size}, 1fr)`,
    gap: '0.5rem',
    padding: '1rem',
    maxWidth: '800px',
    margin: '0 auto',
  };

  return (
    <div className="bg-white rounded-xl shadow-xl p-6 transform transition-all duration-300 hover:scale-[1.02]">
      {title && (
        <h2 className="text-2xl font-bold text-center mb-6 text-gray-800">{title}</h2>
      )}
      <div style={gridStyle}>
        {cells.map((cell, index) => (
          <button
            key={index}
            onClick={() => onCellClick?.(index)}
            className={`
              aspect-square p-3 text-sm sm:text-base md:text-lg rounded-lg
              font-medium transition-all duration-300 transform
              ${cell.isMarked 
                ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white scale-105 shadow-lg' 
                : 'bg-gray-50 hover:bg-gray-100 hover:shadow-md'
              }
              hover:scale-105 active:scale-95
              border-2 ${cell.isMarked ? 'border-blue-400' : 'border-gray-200'}
            `}
          >
            <div className="flex items-center justify-center h-full">
              <span className={`
                text-center break-words
                ${cell.isMarked ? 'animate-pulse' : ''}
              `}>
                {cell.text}
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}; 