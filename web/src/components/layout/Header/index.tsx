import { Link } from "@tanstack/react-router";
import Aurora from "../../background/Aurora";

const Header = () => {
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
    </header>
  )
};

export default Header;
