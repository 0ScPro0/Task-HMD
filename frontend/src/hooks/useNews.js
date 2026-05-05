import { useState, useEffect } from 'react'
import axios from 'axios'

/**
 * Хук для получения списка новостей с бекенда.
 * @returns {Object} { news, isLoading, error }
 */
export function useNews() {
    const [news, setNews] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchNews = async () => {
            setIsLoading(true)
            try {
                // TODO: заменить на реальный эндпоинт бекенда
                const response = await axios.get('/api/v1/news')
                setNews(response.data)
            } catch (err) {
                setError(err.message)
                console.error('Ошибка загрузки новостей:', err)
            } finally {
                setIsLoading(false)
            }
        }

        fetchNews()
    }, [])

    return { news, isLoading, error }
}