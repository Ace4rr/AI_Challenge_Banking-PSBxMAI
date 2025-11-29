// frontend/src/components/Message.tsx
import React from 'react';

// Определяем интерфейс для пропсов
export interface MessageProps {
    text: string;
    type: 'user' | 'ai'; // Тип сообщения: пользователь или AI
    time: string;
    isNew: boolean;
}

// Компонент Message
export const Message: React.FC<MessageProps> = ({ text, type, time }) => {
    const isUser = type === 'user';
    
    // Используйте классы Tailwind, чтобы сообщение выглядело хорошо
    const messageClass = isUser 
        ? "bg-blue-500 text-white self-end rounded-br-none" 
        : "bg-gray-200 text-black self-start rounded-tl-none";

    return (
        <div className={`flex flex-col max-w-xs md:max-w-md p-3 my-2 shadow-md rounded-xl ${messageClass}`}>
            <p className="text-sm">{text}</p>
            <span className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-500'} self-end`}>{time}</span>
        </div>
    );
};