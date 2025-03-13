import { Link } from "@tanstack/react-router";
import Aurora from "../../background/Aurora";
import { useAuthStore } from "../../../store/auth";
import { useLogout } from "../../../hooks/useAuth";

const Header = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const logout = useLogout();

  return (
    <header className="relative flex items-center justify-between w-full min-w-screen p-4">
      <div className="absolute top-0 left-0 w-full">
        <Aurora
          colorStops={["#3A29FF", "#FF94B4", "#FF3232"]}
          blend={0.5}
          amplitude={1.0}
          speed={0.5}
        />
      </div>
      <Link className="z-10" to="/">
        <img src="logo.svg" alt="Bingo" className="h-24" />
      </Link>
      <div className="z-10 flex gap-4">
        {isAuthenticated ? (
          <button
            onClick={logout}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-500"
          >
            Выйти
          </button>
        ) : (
          <>
            <Link
              to="/login"
              className="rounded-md bg-gray-600 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-500"
            >
              Войти
            </Link>
            <Link
              to="/register"
              className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500"
            >
              Регистрация
            </Link>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;
