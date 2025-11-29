import { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Message, MessageProps } from '../../src/components/Message'; 
import { useAuth } from '../../src/context/AuthContext'; 

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// Интерфейс для ответа от FastAPI
interface ApiMessageResponse {
    id: number;
    input_text: string;
    classification: string | null;
    generated_answer: string | null;
    created_at: string;
    // !!! НОВОЕ ПОЛЕ !!!
    extracted_data: string | null; 
}

// Вспомогательный компонент для отображения структурированных данных
interface EntityDisplayProps {
    extractedData: string;
}

const EntityDisplay: React.FC<EntityDisplayProps> = ({ extractedData }) => {
    let data: any;
    try {
        data = JSON.parse(extractedData);
        // Проверяем, что объект не пуст
        if (Object.keys(data).length === 0) {
            return null;
        }
    } catch (e) {
        // Если это невалидный JSON, выведем сообщение об ошибке
        return (
            <div className="bg-red-100 p-4 rounded-lg border border-red-400 mt-4">
                <h4 className="font-bold text-red-700">Ошибка парсинга сущностей:</h4>
                <pre className="text-sm whitespace-pre-wrap">{extractedData}</pre>
            </div>
        );
    }
    
    // Преобразование данных для отображения
    const displayItems = Object.entries(data)
        .filter(([, value]) => value !== null && value !== "" && value !== "null")
        .map(([key, value]) => (
            <div key={key} className="flex justify-between border-b border-gray-200 py-1">
                <span className="font-semibold text-gray-700">{key.replace('_', ' ')}:</span>
                <span className="text-black font-medium">{String(value)}</span>
            </div>
        ));

    if (displayItems.length === 0) {
        return null;
    }

    return (
        <div className="bg-white p-4 rounded-xl shadow-lg border-l-4 border-blue-500 mt-4 max-w-lg mx-auto w-full">
            <h3 className="text-lg font-bold text-blue-800 mb-2">Извлеченные данные:</h3>
            <div className="space-y-1">
                {displayItems}
            </div>
        </div>
    );
};

const Chat = () => {
    const { user, handleLogout } = useAuth();
    const navigate = useNavigate();

    const [messages, setMessages] = useState<MessageProps[]>([]);   
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isHistoryLoaded, setIsHistoryLoaded] = useState(false);

    // --- Состояния для загрузки файла ---
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [fileInputKey, setFileInputKey] = useState(0); 

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // --- ФУНКЦИИ БЭКЕНД-ВЗАИМОДЕЙСТВИЯ ---

    const transformApiResponse = (msg: ApiMessageResponse): MessageProps => {
        return {
            id: msg.id,
            // Сообщение клиента всегда user
            userMessage: msg.input_text, 
            // Ответ от AI
            aiResponse: {
                classification: msg.classification || "Не классифицировано",
                answer: msg.generated_answer || "Нет ответа",
                extractedData: msg.extracted_data || null, // <-- НОВОЕ ПОЛЕ
            },
            timestamp: new Date(msg.created_at),
        };
    };

    // 1. Загрузка истории
    const fetchHistory = useCallback(async () => {
        if (isHistoryLoaded) return;
        try {
            const response = await axios.get<ApiMessageResponse[]>(`${API_BASE_URL}/history`);
            const transformedMessages = response.data.map(transformApiResponse).reverse(); // Сортируем от старых к новым
            setMessages(transformedMessages);
            setIsHistoryLoaded(true);
        } catch (error) {
            console.error('Ошибка загрузки истории:', error);
            // При ошибке истории мы всё равно считаем её загруженной, чтобы не повторять запрос
            setIsHistoryLoaded(true); 
        }
    }, [isHistoryLoaded]);

    // 2. Отправка текстового сообщения
    const sendMessage = useCallback(async () => {
        if (!inputText.trim() || isLoading) return;

        const text = inputText.trim();
        setIsLoading(true);
        setInputText(''); 

        // Добавляем сообщение пользователя в список
        const userMsg: MessageProps = {
            id: Date.now(),
            userMessage: text,
            aiResponse: null,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMsg]);
        
        try {
            const response = await axios.post<ApiMessageResponse>(`${API_BASE_URL}/analyze`, { text });
            const aiMsg = transformApiResponse(response.data);

            // Заменяем сообщение-заглушку на полный ответ от AI
            setMessages(prev => prev.map(m => m.id === userMsg.id ? aiMsg : m));
        } catch (error) {
            console.error('Ошибка анализа текста:', error);
            // Заменяем заглушку на сообщение об ошибке
             setMessages(prev => prev.map(m => m.id === userMsg.id ? 
                {...m, aiResponse: { classification: "Ошибка", answer: "Произошла ошибка при обработке запроса.", extractedData: null}} 
                : m));
        } finally {
            setIsLoading(false);
        }
    }, [inputText, isLoading]);

    // 3. Отправка файла
    const sendFile = useCallback(async () => {
        if (!selectedFile || isLoading) return;

        setIsLoading(true);
        const file = selectedFile;
        setSelectedFile(null); // Сбрасываем выбранный файл
        setFileInputKey(prev => prev + 1); // Сбрасываем input type=file

        // Добавляем сообщение пользователя (файл) в список
        const userMsg: MessageProps = {
            id: Date.now(),
            userMessage: `**Файл:** ${file.name} (Размер: ${(file.size / 1024).toFixed(2)} КБ)`,
            aiResponse: null,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, userMsg]);

        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await axios.post<ApiMessageResponse>(`${API_BASE_URL}/analyze_file`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const aiMsg = transformApiResponse(response.data);

            // Заменяем сообщение-заглушку на полный ответ от AI
            setMessages(prev => prev.map(m => m.id === userMsg.id ? aiMsg : m));

        } catch (error: any) {
            console.error('Ошибка анализа файла:', error);
            const errorMessage = error.response?.data?.detail || "Произошла ошибка при обработке файла.";
            // Заменяем заглушку на сообщение об ошибке
             setMessages(prev => prev.map(m => m.id === userMsg.id ? 
                {...m, aiResponse: { classification: "Ошибка", answer: errorMessage, extractedData: null}} 
                : m));

        } finally {
            setIsLoading(false);
        }
    }, [selectedFile, isLoading]);
    
    // --- ОБРАБОТЧИКИ СОБЫТИЙ UI ---

    const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setSelectedFile(file);
        } else {
            setSelectedFile(null);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    };

    // --- ЭФФЕКТЫ ---

    useEffect(() => {
        // Загрузка истории при первом рендере
        fetchHistory();
    }, [fetchHistory]);

    useEffect(() => {
        // Прокрутка при добавлении нового сообщения
        scrollToBottom();
    }, [messages]);


    // --- РЕНДЕРИНГ UI ---

    if (!user) {
        navigate('/login'); // Перенаправляем на логин, если пользователя нет
        return null;
    }
    
    // Группировка сообщений по дням (для красоты)
    const groupedMessages: { [date: string]: MessageProps[] } = messages.reduce((acc, msg) => {
        const dateKey = msg.timestamp.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
        if (!acc[dateKey]) {
            acc[dateKey] = [];
        }
        acc[dateKey].push(msg);
        return acc;
    }, {} as { [date: string]: MessageProps[] });


    return (
        <div className="min-h-screen bg-gray-100 flex flex-col font-raleway">
            {/* Header */}
            <header className="bg-white shadow-md p-4 flex justify-between items-center fixed top-0 left-0 right-0 z-10">
                <h1 className="text-2xl font-bold text-gray-800">Bank AI Assistant</h1>
                <div className="flex items-center space-x-4">
                    <span className="text-gray-600 font-medium hidden sm:inline">Привет, {user.name}</span>
                    <button
                        onClick={handleLogout}
                        className="text-white bg-red-500 hover:bg-red-600 font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                        Выйти
                    </button>
                </div>
            </header>

            {/* Main Chat Area */}
            <main className="flex-grow pt-20 pb-40 px-4 md:px-8 max-w-4xl w-full mx-auto">
                
                {/* Сообщения */}
                <div className="space-y-6 pt-4">
                    {Object.entries(groupedMessages).map(([date, msgs]) => (
                        <div key={date}>
                            {/* Разделитель по дате */}
                            <div className="relative flex justify-center my-4">
                                <div className="absolute inset-x-0 top-1/2 h-px bg-gray-300 transform -translate-y-1/2"></div>
                                <span className="relative bg-gray-100 px-3 text-sm font-medium text-gray-500">
                                    {date}
                                </span>
                            </div>

                            {/* Сообщения за день */}
                            {msgs.map(msg => (
                                <div key={msg.id} className="mb-6">
                                    <Message 
                                        {...msg} 
                                        // Передаем компонент EntityDisplay, если есть данные
                                        aiResponse={{
                                            ...msg.aiResponse!,
                                            extraContent: msg.aiResponse?.extractedData ? (
                                                <EntityDisplay extractedData={msg.aiResponse.extractedData} />
                                            ) : null,
                                        }}
                                    />
                                </div>
                            ))}
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
                
            </main>

            {/* Input Area (fixed at bottom) */}
            <footer className="fixed bottom-0 left-0 right-0 bg-white shadow-2xl p-4 border-t border-gray-200">
                <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center space-y-3 sm:space-y-0 sm:space-x-3">
                    
                    {/* Input Text */}
                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={isLoading}
                        placeholder={isLoading ? "Подождите, идет анализ..." : "Напишите ваше обращение..."}
                        className="flex-grow w-full sm:w-auto p-4 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-gray-800 text-lg"
                    />

                    {/* Send Button */}
                    <button
                        onClick={sendMessage}
                        disabled={!inputText.trim() || isLoading}
                        className="w-full sm:w-auto h-14 px-6 rounded-xl bg-blue-500 text-white font-semibold text-lg hover:bg-blue-600 disabled:bg-gray-400 transition-colors flex-shrink-0"
                    >
                        Отправить
                    </button>

                    {/* File Upload Button */}
                    <div className="relative w-full sm:w-auto flex-shrink-0">
                        <input
                            key={fileInputKey}
                            type="file"
                            onChange={handleFileInput}
                            accept=".pdf,.txt"
                            disabled={isLoading}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />
                        <button
                            disabled={isLoading}
                            className={`w-full sm:w-auto h-14 px-6 rounded-xl font-semibold text-lg transition-colors ${
                                selectedFile 
                                ? 'bg-green-500 text-white hover:bg-green-600' 
                                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
                            } disabled:bg-gray-400`}
                        >
                            {selectedFile ? selectedFile.name : 'Загрузить файл'}
                        </button>
                        
                        {selectedFile && (
                            <button
                                onClick={sendFile}
                                disabled={isLoading}
                                className="absolute right-0 top-0 h-14 w-14 rounded-xl bg-green-600 text-white hover:bg-green-700 disabled:bg-gray-500"
                                style={{ transform: 'translateX(calc(100% + 8px))' }}
                                title="Анализировать файл"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6 mx-auto">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                                </svg>
                            </button>
                        )}
                    </div>
                </div>
                
                {selectedFile && (
                    <p className="mt-2 text-sm text-center text-gray-500">
                        Нажмите ✅ рядом с кнопкой "Загрузить файл", чтобы начать анализ.
                    </p>
                )}
            </footer>
        </div>
    );
};

export default Chat;