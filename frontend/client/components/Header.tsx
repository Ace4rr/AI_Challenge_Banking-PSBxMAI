import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="w-full h-[71px] absolute top-0 left-0 z-50">
      <div className="max-w-[1280px] mx-auto px-4 h-full flex items-center justify-between">
        <Link to="/" className="flex-shrink-0">
          <img
            src="https://api.builder.io/api/v1/image/assets/TEMP/9815e7ff7ef2932dfbdf8b03f9d7b98a01936c3f?width=498"
            alt="ПСБ"
            className="h-[60px] md:h-[97px] w-auto"
          />
        </Link>

        <nav className="hidden md:flex items-center gap-10">
          <Link
            to="/chat"
            className="text-black text-base font-medium font-inter leading-[145%] tracking-[-0.08px] capitalize hover:underline transition-all"
          >
            Кнопка Для Отладки
          </Link>
          <Link
            to="/register"
            className="text-black text-base font-medium font-inter leading-[145%] tracking-[-0.08px] capitalize hover:underline transition-all"
          >
            Зарегистрироваться
          </Link>
          <Link
            to="/login"
            className="text-black text-base font-medium font-inter leading-[145%] tracking-[-0.08px] capitalize hover:underline transition-all"
          >
            Войти
          </Link>
        </nav>

        <Link
          to="/chat"
          className="md:hidden text-black text-sm font-medium font-inter hover:underline transition-all"
        >
          Чат
        </Link>
      </div>
    </header>
  );
}
