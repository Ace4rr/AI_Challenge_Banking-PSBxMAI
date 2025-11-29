// frontend/src/context/AuthContext.tsx
import React, { createContext, useContext, useState, ReactNode } from 'react';

// Определяем интерфейс для контекста
interface AuthContextType {
    user: { name: string } | null;
    handleLogout: () => void;
    // ... можно добавить handleLogin, isAuthenticated
}

// Создаем контекст с дефолтными значениями
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Компонент провайдера (обертка)
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    // Временно используем заглушку для пользователя
    const [user] = useState<{ name: string } | null>({ name: "Белкин Сергей" });

    const handleLogout = () => {
        console.log("Logout function called (Stub)");
        // Здесь должна быть логика очистки токена
    };

    const value = { user, handleLogout };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Хук для использования контекста
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};