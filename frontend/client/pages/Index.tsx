import { motion, useScroll, useTransform } from "framer-motion";
import { Link } from "react-router-dom";
import { useRef } from "react";
import Header from "@/components/Header";

const features = [
  {
    icon: "https://api.builder.io/api/v1/image/assets/TEMP/a4032af5239f6f06e7d62d577f3c048f67f1af7b?width=146",
    title: "Загрузка и получение писем",
    description:
      "Через интерактивный чат со мной Вы сможете загрузить неограниченное количество информации - я смогу прочитать все!",
  },
  {
    icon: "https://api.builder.io/api/v1/image/assets/TEMP/f70b397bbbb45709ee4fa79690fc44f0fdab7546?width=146",
    title: "Чтение и обработка текста",
    description:
      "Обработаю текст загруженного письма и выделю ключевые параметры - адреса, даты, наименования документов.",
  },
  {
    icon: "https://api.builder.io/api/v1/image/assets/TEMP/46d861d663871102dbe1824490feff2e2654c158?width=130",
    title: "Работа с разными форматами",
    description:
      "Могу обрабатывать официальные документы .pdf, изображения .jpg/png, получать с них информацию.",
  },
  {
    icon: "https://api.builder.io/api/v1/image/assets/TEMP/67b8a74bb045bbe0785e22b8c411d5e9248ef383?width=128",
    title: "Выделение ключевых значений",
    description:
      "Тон письма (претензия/уведомление/предложение), адреса отправителя, важные даты - все будет выделено в отдельной графе.",
  },
  {
    icon: "https://api.builder.io/api/v1/image/assets/TEMP/90de03390b6e94029fea2033417962af32af5d7f?width=146",
    title: "Генерация приемлемого ответа",
    description:
      "Будет создан текст для ответного письма в корректном стиле: деловой. информационный, клиентоориентированный",
  },
  {
    icon: "https://api.builder.io/api/v1/image/assets/TEMP/a4e3e4af97c6aad12681611d8147bf6b4112736c?width=130",
    title: "Отправка с привязкой к почтовому ящику",
    description:
      "Смогу прочитать сообщения напрямую из почты и автоматически отправить их адресату без необходимости загружать их по отдельности!",
  },
];

export default function Index() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  const section1Opacity = useTransform(scrollYProgress, [0, 0.15, 0.25], [1, 1, 0]);
  const section2Opacity = useTransform(scrollYProgress, [0.2, 0.33, 0.55, 0.65], [0, 1, 1, 0]);
  const section3Opacity = useTransform(scrollYProgress, [0.6, 0.75, 1], [0, 1, 1]);

  return (
    <div ref={containerRef} className="relative bg-gradient-to-r from-white to-[#80A8FF] h-[300vh]">
      <Header />

      {/* Section 1: Welcome */}
      <motion.section
        style={{ opacity: section1Opacity }}
        className="h-screen flex flex-col items-center justify-center px-4 sticky top-0"
      >
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="text-center"
        >
          <h1 className="text-4xl md:text-[60px] font-semibold leading-[110%] tracking-[-1.8px] text-black font-raleway mb-8 md:mb-12">
            Добрый день!
            <br />
            Меня зовут Захар.
          </h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="text-xl md:text-[30px] font-semibold leading-[110%] tracking-[-0.9px] text-black font-raleway max-w-[502px] mx-auto"
          >
            Я - ваш личный виртуальный ассистент, который поможет разобраться с
            корреспонденцией и ускорить рутинные процессы.
          </motion.p>
        </motion.div>
      </motion.section>

      {/* Section 2: Features */}
      <motion.section
        style={{ opacity: section2Opacity }}
        className="h-screen flex flex-col items-center justify-center px-4 sticky top-0"
      >
        <h2 className="text-4xl md:text-[60px] font-semibold leading-[110%] tracking-[-1.8px] text-black font-raleway mb-12 md:mb-16 text-center">
          С чем я могу помочь?
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 max-w-[1280px] mx-auto">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="bg-white rounded-[50px] border-2 border-black/30 shadow-[0_7px_4px_0_rgba(0,0,0,0.5)] p-6 flex flex-col items-center text-center min-h-[154px]"
            >
              <img
                src={feature.icon}
                alt=""
                className="w-[65px] h-[65px] mb-4"
              />
              <h3 className="text-lg md:text-[25px] font-semibold leading-[110%] tracking-[-0.75px] text-black font-raleway mb-3">
                {feature.title}
              </h3>
              <p className="text-sm md:text-[15px] font-medium leading-[110%] tracking-[-0.45px] text-black font-raleway">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Section 3: CTA */}
      <motion.section
        style={{ opacity: section3Opacity }}
        className="h-screen flex flex-col items-center justify-center px-4 sticky top-0"
      >
        <h2 className="text-4xl md:text-[60px] font-semibold leading-[110%] tracking-[-1.8px] text-black font-raleway mb-12 md:mb-16 text-center">
          Начнём сейчас?
        </h2>

        <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-12 mb-12">
          <img
            src="https://api.builder.io/api/v1/image/assets/TEMP/77277ba7b6c28052e0260a7fecf541bbe1a8e8cd?width=742"
            alt=""
            className="w-[280px] md:w-[371px] h-auto shadow-[0_4px_4px_0_rgba(0,0,0,0.5)_inset]"
          />
          <img
            src="https://api.builder.io/api/v1/image/assets/TEMP/a285d51b61148f087e89d84f2ba0e36954690ffc?width=742"
            alt=""
            className="w-[280px] md:w-[371px] h-auto shadow-[0_4px_4px_0_rgba(0,0,0,0.5)_inset]"
          />
        </div>

        <Link to="/chat">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-[320px] md:w-[400px] h-[82px] rounded-full bg-[#8FB8FF] shadow-[0_8px_4px_0_rgba(0,0,0,0.5)] flex items-center justify-center hover:bg-[#7DA7EE] transition-all"
          >
            <span className="text-2xl md:text-[30px] font-semibold leading-[110%] tracking-[-0.9px] text-black font-raleway">
              Перейти в чат с Захаром
            </span>
          </motion.button>
        </Link>

        <p className="text-xl md:text-[30px] font-semibold leading-[110%] tracking-[-0.9px] text-black font-raleway mt-8 text-center max-w-[630px]">
          (для использования потребуется зарегистрироваться)
        </p>

        <div className="absolute bottom-4 left-0 right-0 flex justify-between px-4 md:px-8">
          <p className="text-sm md:text-xl font-medium leading-[110%] tracking-[-0.6px] text-black/75 font-inter">
            Лицензия на использование GigaChat 3
          </p>
          <p className="text-sm md:text-xl font-medium leading-[110%] tracking-[-0.6px] text-black/75 font-inter">
            Разработано в рамках хакатона ПСБ x МАИ
          </p>
        </div>
      </motion.section>
    </div>
  );
}
