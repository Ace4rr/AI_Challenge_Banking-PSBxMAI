import React, { createContext, useContext, useState, ReactNode } from 'react';

interface AuthContextType {
    user: { name: string } | null;
    handleLogout: () => void;
    // ... можно добавить handleLogin, isAuthenticated
}


const AuthContext = createContext<AuthContextType | undefined>(undefined);


export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {

    const [user] = useState<{ name: string } | null>({ name: "Белкин Сергей" });

    const handleLogout = () => {
        console.log("Logout function called (Stub)");
    };

    const value = { user, handleLogout };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};


export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};