import { useState } from 'react';
import { useRegister } from '../../hooks/useAuth';
import { AxiosError } from 'axios';

const Register = () => {
  const [error, setError] = useState<string | null>(null);
  const register = useRegister();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;
    const confirmPassword = formData.get('confirmPassword') as string;

    if (password !== confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    try {
      await register.mutateAsync({ email, username, password });
    } catch (err) {
      const error = err as AxiosError<{ detail: string }>;
      setError(error.response?.data?.detail || 'Произошла ошибка при регистрации');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-900">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-gray-800 p-6 shadow-md">
        <div>
          <h2 className="text-center text-3xl font-bold text-white">
            Регистрация
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4 rounded-md shadow-sm">
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="relative block w-full rounded-md border-0 bg-gray-700 p-2 text-white placeholder-gray-400 focus:z-10 focus:ring-2 focus:ring-indigo-500"
                placeholder="Email"
              />
            </div>
            <div>
              <label htmlFor="username" className="sr-only">
                Имя пользователя
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="relative block w-full rounded-md border-0 bg-gray-700 p-2 text-white placeholder-gray-400 focus:z-10 focus:ring-2 focus:ring-indigo-500"
                placeholder="Имя пользователя"
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Пароль
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="relative block w-full rounded-md border-0 bg-gray-700 p-2 text-white placeholder-gray-400 focus:z-10 focus:ring-2 focus:ring-indigo-500"
                placeholder="Пароль"
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="sr-only">
                Подтвердите пароль
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                className="relative block w-full rounded-md border-0 bg-gray-700 p-2 text-white placeholder-gray-400 focus:z-10 focus:ring-2 focus:ring-indigo-500"
                placeholder="Подтвердите пароль"
              />
            </div>
          </div>

          {error && (
            <div className="text-center text-sm text-red-500">{error}</div>
          )}

          <div>
            <button
              type="submit"
              disabled={register.isPending}
              className="group relative flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 disabled:opacity-50"
            >
              {register.isPending ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
          </div>

          <div className="text-center text-sm">
            <a
              href="/login"
              className="font-medium text-indigo-400 hover:text-indigo-300"
            >
              Уже есть аккаунт? Войти
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register; 