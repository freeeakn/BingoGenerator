import { useMutation } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { bingoApi } from '../services/api';
import { useAuthStore } from '../store/auth';

interface RegisterData {
  email: string;
  username: string;
  password: string;
}

interface LoginData {
  email: string;
  password: string;
}

export const useRegister = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  return useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await bingoApi.register(data.email, data.username, data.password);
      return response;
    },
    onSuccess: (data) => {
      login(data);
      navigate({ to: '/' });
    },
  });
};

export const useLogin = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  return useMutation({
    mutationFn: async (data: LoginData) => {
      const response = await bingoApi.login(data.email, data.password);
      return response;
    },
    onSuccess: (data) => {
      login(data);
      navigate({ to: '/' });
    },
  });
};

export const useLogout = () => {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);

  return () => {
    logout();
    navigate({ to: '/' });
  };
}; 