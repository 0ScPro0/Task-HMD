// hooks/useNews.js
import { useState, useEffect } from 'react'
import { newsService } from '../services/api/news'

export function useNews() {
    const [news, setNews] = useState([]) // Уже массив по умолчанию
    const [isLoading, setIsLoading] = useState(true) // Начинаем с true
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchNews = async () => {
            setIsLoading(true)
            try {
                const response = await newsService.getNewsList()
                // Убеждаемся, что response - это массив
                let newsData = Array.isArray(response) ? response : (response?.data || [])
                
                // Сортируем новости от новых к старым по дате created_at
                newsData = newsData.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                
                setNews(newsData)
                setError(null)
            } catch (err) {
                setError(err.message || 'Ошибка загрузки новостей')
                console.error('Ошибка загрузки новостей:', err)
                setNews([]) // Устанавливаем пустой массив при ошибке
            } finally {
                setIsLoading(false)
            }
        }

        fetchNews()
    }, [])

    return { news, isLoading, error }
}