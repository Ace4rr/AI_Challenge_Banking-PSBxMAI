// frontend/src/EmailProcessor.jsx

import React, { useState } from 'react';
import axios from 'axios'; // Используем установленный Axios

// Порт 8000 - это порт вашего FastAPI
const API_ENDPOINT = 'http://localhost:8000/analyze_email'; 

function EmailProcessor() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    // Сохраняем выбранный файл
    setFile(event.target.files[0]);
    setAiResponse(null); 
    setError(null);
  };

  const handleSubmit = async () => {
    if (!file) {
      alert('Пожалуйста, выберите файл письма.');
      return;
    }

    setLoading(true);

    // 1. Создаем объект FormData для отправки файла
    const formData = new FormData();
    // Имя 'file' должно совпадать с аргументом FastAPI (file: UploadFile = File(...))
    formData.append('file', file);

    try {
      // 2. Асинхронный вызов FastAPI через Axios
      const response = await axios.post(API_ENDPOINT, formData, {
        headers: {
          'Content-Type': 'multipart/form-data', // Axios часто устанавливает его сам, но лучше явно указать
        },
      });

      setAiResponse(response.data); // Axios автоматически возвращает .data

    } catch (err) {
      // Axios обрабатывает ошибки по-другому, проверяем структуру ответа
      setError(err.response?.data?.detail || err.message || "Произошла ошибка при обработке письма.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <h1>📧 GigaChat Банковский Ассистент</h1>
      
      <div style={{ marginBottom: '20px', border: '1px dashed #ccc', padding: '15px' }}>
          <input 
            type="file" 
            accept=".eml,.txt,.pdf,.docx" 
            onChange={handleFileChange} 
          />
          {file && <p>Выбран файл: <strong>{file.name}</strong></p>}
          
          <button 
            onClick={handleSubmit} 
            disabled={loading || !file}
            style={{ padding: '10px 20px', marginTop: '10px', backgroundColor: loading ? '#ccc' : '#4CAF50', color: 'white', border: 'none', cursor: 'pointer' }}
          >
            {loading ? '⏳ AI Обрабатывает...' : '🚀 Отправить на AI'}
          </button>
      </div>

      {error && <div style={{ color: 'red', border: '1px solid red', padding: '10px' }}>Ошибка: {error}</div>}

      {aiResponse && (
        <div style={{ marginTop: '30px', border: '1px solid #eee', padding: '15px' }}>
          <h2>✅ Результат анализа</h2>
          
          <h3>Категория:</h3>
          <p style={{ fontWeight: 'bold', fontSize: '1.2em', color: '#007bff' }}>{aiResponse.category}</p>
          
          <h3>Резюме письма:</h3>
          <p>{aiResponse.summary}</p>

          <h3>Черновик ответа:</h3>
          <textarea 
            value={aiResponse.reply_draft} 
            readOnly 
            rows="10" 
            cols="80"
            style={{ width: '100%', padding: '10px', border: '1px solid #ddd' }}
          />
        </div>
      )}
    </div>
  );
}

export default EmailProcessor;