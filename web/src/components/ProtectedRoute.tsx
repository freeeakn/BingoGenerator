import { ReactNode, useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate({ to: '/login' });
    }
  }, [navigate]);

  return <>{children}</>;
}; 