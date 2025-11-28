// frontend/src/App.jsx

import EmailProcessor from './EmailProcessor';
// Удалите импорт App.css и логотипов, если они вам не нужны

function App() {
  // Весь стандартный код Vite можно удалить, оставив только ваш компонент
  return (
    <div className="main-container">
      <EmailProcessor />
    </div>
  );
}

export default App;