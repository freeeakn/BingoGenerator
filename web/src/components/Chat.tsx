import { useEffect, useState, useRef } from 'react';
import { chatWS, WebSocketMessage } from '../services/websocket';

interface ChatMessage {
  type: 'message' | 'system';
  player?: string;
  text: string;
  timestamp: string;
}

interface ChatProps {
  gameId: string;
}

export const Chat = ({ gameId }: ChatProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      chatWS.connect(token);

      const unsubscribe = chatWS.onMessage((message: WebSocketMessage) => {
        if (message.type === 'message' || message.type === 'system') {
          setMessages((prev) => [...prev, message as ChatMessage]);
        }
      });

      return () => {
        unsubscribe();
        chatWS.disconnect();
      };
    }
  }, [gameId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMessage.trim()) {
      chatWS.send({
        type: 'message',
        data: {
          text: newMessage.trim(),
          gameId,
        },
      });
      setNewMessage('');
    }
  };

  return (
    <div className="flex flex-col h-96 bg-white rounded-lg shadow-lg">
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`${
                message.type === 'system'
                  ? 'bg-gray-100'
                  : 'bg-blue-50'
              } p-3 rounded-lg`}
            >
              {message.type === 'message' && (
                <div className="font-medium text-blue-600">{message.player}</div>
              )}
              <div className="text-gray-700">{message.text}</div>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <form onSubmit={handleSendMessage} className="p-4 border-t">
        <div className="flex space-x-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Введите сообщение..."
            className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={!newMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Отправить
          </button>
        </div>
      </form>
    </div>
  );
}; 