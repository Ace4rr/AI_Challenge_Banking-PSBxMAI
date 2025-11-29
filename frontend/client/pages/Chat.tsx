import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Message, MessageProps } from '../../src/components/Message'; 
import { useAuth } from '../../src/context/AuthContext'; 

// Интерфейс для ответа от FastAPI
interface ApiMessageResponse {
    id: number;
    input_text: string;
    classification: string | null;
    generated_answer: string | null;
    created_at: string;
}

const Chat = () => {
    const { user, handleLogout } = useAuth();
    const navigate = useNavigate();

    const [messages, setMessages] = useState<MessageProps[]>([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);

    // --- Состояния для загрузки файла (Восстановлено) ---
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileInputKey, setFileInputKey] = useState(0); 

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // --- ФУНКЦИИ БЭКЕНД-ВЗАИМОДЕЙСТВИЯ ---
    
    // Функция отправки текстового сообщения
    const sendMessage = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        const textToSend = inputText.trim();
        if (textToSend === '') return;

        // Сообщение пользователя
        const userMessage: MessageProps = { 
            text: textToSend, 
            type: 'user', 
            time: new Date().toLocaleTimeString(),
            isNew: true 
        };
        setMessages((prev) => [...prev, userMessage]); 
        
        setInputText('');
        setIsLoading(true);

        try {
            const response = await axios.post<ApiMessageResponse>(
                'http://localhost:8000/analyze', 
                { text: textToSend }
            );

            const apiData = response.data;
            const aiText = `[КЛАССИФИКАЦИЯ] ${apiData.classification}\n[ОТВЕТ AI] ${apiData.generated_answer}`;

            // Ответ AI
            const aiResponse: MessageProps = {
                text: aiText,
                type: 'ai',
                time: new Date().toLocaleTimeString(),
                isNew: true
            };

            setMessages((prev) => [...prev, aiResponse]);

        } catch (error) {
            console.error('Ошибка при отправке сообщения:', error);
            const errorMessage: MessageProps = {
                text: 'Не удалось связаться с сервером (API). Проверьте бэкенд (Fast API).',
                type: 'ai',
                time: new Date().toLocaleTimeString(),
                isNew: true
            };
            setMessages((prev) => [...prev, errorMessage]);

        } finally {
            setIsLoading(false);
        }
    }, [inputText]); // Добавлены все зависимости

    // Функция отправки файла (НОВАЯ/ВОССТАНОВЛЕННАЯ)
    const sendFile = async () => {
        if (!selectedFile) return;

        // Внимание: Здесь мы не отправляем реальный файл, а только его имя/содержимое
        // В реальном приложении здесь был бы код с FormData и роутом /upload.
        // Используем заглушку, чтобы отправить текст файла на роут /analyze
        
        // 1. Читаем файл как текст
        const fileReader = new FileReader();
        
        fileReader.onloadstart = () => setIsLoading(true);
        
        fileReader.onload = async (e) => {
            const fileContent = e.target?.result as string;
            
            // Сообщение пользователя (текст файла)
            const userMessage: MessageProps = { 
                text: `[ЗАГРУЖЕН ФАЙЛ] ${selectedFile.name}\n\nСодержимое:\n${fileContent.substring(0, 500)}...`, 
                type: 'user', 
                time: new Date().toLocaleTimeString(),
                isNew: true 
            };
            setMessages((prev) => [...prev, userMessage]); 
            
            // 2. Отправляем содержимое файла на роут /analyze
            try {
                const response = await axios.post<ApiMessageResponse>(
                    'http://localhost:8000/analyze', 
                    { text: fileContent } // Отправляем полное содержимое файла
                );

                const apiData = response.data;
                const aiText = `[КЛАССИФИКАЦИЯ] ${apiData.classification}\n[ОТВЕТ AI] ${apiData.generated_answer}`;

                const aiResponse: MessageProps = {
                    text: aiText,
                    type: 'ai',
                    time: new Date().toLocaleTimeString(),
                    isNew: true
                };

                setMessages((prev) => [...prev, aiResponse]);
                
                // Сброс файла после успешной отправки
                setSelectedFile(null);
                setFileInputKey(prev => prev + 1); // Сброс поля ввода файла

            } catch (error) {
                console.error('Ошибка при отправке файла:', error);
                const errorMessage: MessageProps = {
                    text: 'Не удалось отправить файл на анализ.',
                    type: 'ai',
                    time: new Date().toLocaleTimeString(),
                    isNew: true
                };
                setMessages((prev) => [...prev, errorMessage]);
            } finally {
                setIsLoading(false);
            }
        };

        // Запускаем чтение файла как текста
        fileReader.readAsText(selectedFile);
    };

    // 3. Загрузка истории
    useEffect(() => {
        const fetchHistory = async () => {
            // ... (Код fetchHistory, который вы уже отладили)
            try {
                const response = await axios.get<ApiMessageResponse[]>('http://localhost:8000/history');
                const apiHistory = response.data;
                
                const historyMessages: MessageProps[] = [];

                apiHistory.reverse().forEach(msg => { 
                    // 1. Сообщение пользователя
                    historyMessages.push({
                        text: msg.input_text.length > 500 
                              ? `[ЗАПРОС-ФАЙЛ] ${msg.input_text.substring(0, 500)}...` // Укорачиваем длинный текст файла
                              : msg.input_text,
                        type: 'user', 
                        time: new Date(msg.created_at).toLocaleTimeString(),
                        isNew: false
                    });
                    
                    // 2. Ответ AI
                    historyMessages.push({
                        text: `[КЛАССИФИКАЦИЯ] ${msg.classification}\n[ОТВЕТ AI] ${msg.generated_answer}`, 
                        type: 'ai', 
                        time: new Date(msg.created_at).toLocaleTimeString(),
                        isNew: false
                    });
                });
                
                setMessages(historyMessages);
                setIsHistoryLoaded(true);

            } catch (error) {
                console.error("Не удалось загрузить историю:", error);
                setMessages([{ 
                    text: 'Не удалось загрузить историю из БД. Проверьте Fast API.', 
                    type: 'ai', 
                    time: new Date().toLocaleTimeString(),
                    isNew: true
                }]);
            }
        };
        fetchHistory();
    }, []); 

    // Эффект для прокрутки при добавлении сообщений
    useEffect(() => {
        scrollToBottom();
    }, [messages]);
    
    // --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
    
    const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setSelectedFile(file);
        }
    };

    const handleLogoutClick = () => {
        handleLogout();
        navigate('/login');
    };


    return (
        <div className="flex min-h-screen bg-gradient-to-r from-white to-[#80A8FF]">
            {/* Sidebar */}
            <aside className="hidden md:flex md:w-[265px] flex-col justify-between p-6 border-r-2 border-black relative">
                <div>
                    <h2 className="text-[30px] font-medium leading-[110%] tracking-[-0.9px] text-center text-black font-raleway">
                        История анализа писем
                    </h2>
                    {/* Логика отображения загрузки истории */}
                    <div className="mt-4">
                        {!isHistoryLoaded && <p className="text-center text-gray-500">Загрузка истории...</p>}
                        {/* Сообщения в sidebar отображаются не будут, т.к. они уже в основном окне */}
                    </div>
                </div>

                <div className="text-center">
                    <p className="text-xl font-medium leading-[110%] tracking-[-0.6px] text-black/75 mb-2 font-inter">
                        Вы вошли как Белкин Сергей Викторович.
                    </p>
                    <button 
                        onClick={handleLogoutClick}
                        className="text-lg font-bold text-red-600 hover:text-red-800 transition-colors font-raleway"
                    >
                        Выйти
                    </button>
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="flex-1 flex flex-col relative">
                <header className="p-4 border-b-2 border-black flex justify-between items-center bg-white shadow-md">
                    <h1 className="text-3xl font-bold font-raleway text-black">Чат с Захаром</h1>
                </header>

                {/* Messages Display */}
                <div className="flex-1 overflow-y-auto p-4 flex flex-col space-y-2">
                    {messages.map((msg, index) => (
                        <Message key={index} {...msg} />
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area (для текста) */}
                <div className="p-4 bg-gray-100 border-t-2 border-black">
                    <form onSubmit={sendMessage} className="flex space-x-2 mb-4">
                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            placeholder="Введите текст для анализа..."
                            className="flex-grow p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            disabled={isLoading}
                        />
                        <button 
                            type="submit" 
                            disabled={isLoading || inputText.trim() === ''}
                            className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 font-semibold transition-colors"
                        >
                            {isLoading ? 'Отправка...' : 'Отправить'}
                        </button>
                    </form>
                    
                    {/* Input Area (для файла, восстановлено из оригинального UI) */}
                    <div className="flex flex-col items-center justify-center space-y-4 pt-4 border-t border-gray-300">
                        <input
                            type="file"
                            id="file-upload"
                            key={fileInputKey}
                            onChange={handleFileSelect}
                            className="hidden"
                            accept=".txt,.pdf" // Указание принимаемых типов (при необходимости)
                            disabled={isLoading}
                        />
                        <label
                            htmlFor="file-upload"
                            className="block w-[300px] h-[60px] rounded-full bg-[#8FB8FF] shadow-[0_4px_4px_0_rgba(0,0,0,0.5)] flex items-center justify-center cursor-pointer hover:bg-[#7DA7EE] transition-all"
                        >
                            <span className="text-xl font-semibold leading-[110%] tracking-[-0.9px] text-black font-raleway">
                                Выберите файл
                            </span>
                        </label>
                        
                        <div className="text-center">
                            <p className="text-lg font-medium text-black font-raleway">
                                {selectedFile ? selectedFile.name : "Файл не выбран"}
                            </p>
                        </div>

                        {selectedFile && (
                            <button 
                                onClick={sendFile}
                                disabled={isLoading}
                                className="w-[300px] h-[60px] rounded-full bg-green-500 text-white shadow-[0_4px_4px_0_rgba(0,0,0,0.5)] flex items-center justify-center hover:bg-green-600 disabled:bg-gray-400 font-semibold transition-colors mt-2"
                            >
                                {isLoading ? 'Анализ файла...' : 'Анализировать файл'}
                            </button>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Chat;