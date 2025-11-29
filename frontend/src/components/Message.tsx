import React, { ReactNode } from 'react';

export interface AiResponse {
    // Старые поля (которые вы переименовали)
    classification: string;
    answer: string;
    extractedData: string | null;
    extraContent?: React.ReactNode; // Если у вас есть это поле
    
    // НОВЫЕ ПОЛЯ, которые вы добавили в Chat.tsx
    replyStyle: string | null;
    timeToReply: string | null;
    summary: string | null;
    infrastructureSphere: string | null;
    risksAndFixes: string | null;
}

export interface MessageProps {
    id: number;
    userMessage: string;
    aiResponse: AiResponse | null;
    timestamp: Date;
}


export const Message: React.FC<MessageProps> = ({ userMessage, aiResponse, timestamp }) => {
    

    const timeString = timestamp.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });

    const renderUserMessage = () => (
        <div className="flex justify-end mb-4">
            <div className="max-w-3xl bg-blue-500 text-white p-4 rounded-t-xl rounded-bl-xl shadow-lg">
                <p className="text-base font-medium whitespace-pre-wrap">{userMessage}</p>
                <div className="text-right text-xs mt-1 text-blue-200">
                    {timeString}
                </div>
            </div>
        </div>
    );

    const renderAIResponse = () => (
        <div className="flex justify-start">
            <div className="max-w-3xl bg-gray-200 text-gray-900 p-4 rounded-t-xl rounded-br-xl shadow-lg">
                
                {/* Классификация */}
                <div className="mb-2 p-2 bg-gray-100 rounded-lg border border-gray-300">
                    <span className="text-sm font-bold text-gray-700">Классификация:</span>
                    <span className="ml-2 text-sm font-semibold text-blue-600">{aiResponse!.classification}</span>
                </div>

                {/* Ответ AI */}
                <p className="text-base font-medium whitespace-pre-wrap">{aiResponse!.answer}</p>

                {/* Извлеченные данные (extraContent) */}
                {aiResponse!.extraContent && (
                    <div className="mt-4">
                        {aiResponse!.extraContent}
                    </div>
                )}
                
                <div className="text-right text-xs mt-1 text-gray-500">
                    {timeString}
                </div>
            </div>
        </div>
    );

    return (
        <div className="w-full">
            {/* Сообщение пользователя всегда рендерится */}
            {renderUserMessage()}
            
            {/* Ответ AI рендерится только если он есть */}
            {aiResponse && renderAIResponse()}
        </div>
    );
};