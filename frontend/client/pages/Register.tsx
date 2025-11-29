import { Link } from "react-router-dom";
import Header from "@/components/Header";

export default function Register() {
  return (
    <div className="min-h-screen bg-gradient-to-r from-white to-[#80A8FF]">
      <Header />
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="text-center max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-semibold text-black font-raleway mb-6">
            Страница регистрации
          </h1>
          <p className="text-xl text-black/75 font-inter mb-8">
            Эта страница находится в разработке. Пожалуйста, продолжайте создавать свое приложение.
          </p>
          <Link
            to="/"
            className="inline-block px-8 py-4 bg-[#8FB8FF] rounded-full text-xl font-semibold text-black font-raleway hover:bg-[#7DA7EE] transition-all shadow-[0_8px_4px_0_rgba(0,0,0,0.5)]"
          >
            Вернуться на главную
          </Link>
        </div>
      </div>
    </div>
  );
}
