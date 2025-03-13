import axios from 'axios';
import { useAuthStore } from '../store/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для добавления токена авторизации
api.interceptors.request.use((config) => {
  const accessToken = useAuthStore.getState().accessToken;
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Интерцептор для обработки ошибок и обновления токена
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = useAuthStore.getState().refreshToken;

      try {
        const response = await api.post('/auth/refresh-token', { token: refreshToken });
        const { access_token, refresh_token } = response.data;
        
        useAuthStore.getState().login({ access_token, refresh_token });
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch {
        // Если не удалось обновить токен, разлогиниваем пользователя
        useAuthStore.getState().logout();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Интерфейсы для типизации данных
export interface BingoCard {
  size: number;
  words: string[];
  title: string;
}

export interface GameHistory {
  id: number;
  title: string;
  date: string;
  size: number;
  words: string[];
}

// API методы
export const bingoApi = {
  // Генерация карточки бинго
  generateCard: async (data: BingoCard) => {
    const response = await api.post('/game/generate', data);
    return response.data;
  },

  // Получение истории карточек
  getHistory: async () => {
    const response = await api.get<GameHistory[]>('/game/history');
    return response.data;
  },

  // Сохранение карточки
  saveCard: async (data: BingoCard) => {
    const response = await api.post('/game/save', data);
    return response.data;
  },

  // Авторизация
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/token', {
      email,
      password,
    });
    return response.data;
  },

  // Регистрация
  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/auth/register', {
      email,
      username,
      password,
    });
    return response.data;
  },
};

export default api; 