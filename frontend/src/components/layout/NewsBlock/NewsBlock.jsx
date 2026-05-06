// NewsBlock.jsx
import { useState } from "react"
import styles from "./NewsBlock.module.css"
import { useNews } from "../../../hooks/useNews"

export function NewsBlock() {
    const [expandedId, setExpandedId] = useState(null)

    const toggleExpand = (id) => {
        setExpandedId(prev => prev === id ? null : id)
    }

    const { news, isLoading, error } = useNews()
    
    // Форматирование даты из ISO формата в читаемый вид
    const formatDate = (dateString) => {
        if (!dateString) return "Дата не указана"
        const date = new Date(dateString)
        return date.toLocaleDateString("ru-RU", {
            year: "numeric",
            month: "long",
            day: "numeric"
        })
    }

    // Если загрузка
    if (isLoading) {
        return <div className={styles.newsList}>Загрузка новостей...</div>
    }

    // Если ошибка
    if (error) {
        return <div className={styles.newsList}>Ошибка: {error}</div>
    }

    // Если новостей нет
    if (!news || news.length === 0) {
        return <div className={styles.newsList}>Новостей пока нет</div>
    }

    return (
        <div className={styles.newsList}>
            {news.map(item => {
                // Преобразуем данные с бекенда в нужный формат
                const newsItem = {
                    id: item.id,
                    date: formatDate(item.created_at),
                    title: item.title,
                    content: item.content
                }
                
                return (
                    <article key={newsItem.id} className={`${styles.newsItem} ${expandedId === newsItem.id ? styles.active : ''}`}>
                        <div className={styles.newsItem__header}>
                            <div className={styles.newsItem__meta}>
                                <span className={styles.newsItem__date}>{newsItem.date}</span>
                                <h2 className={styles.newsItem__title}>{newsItem.title}</h2>
                            </div>
                            <button
                                className={styles.newsItem__toggle}
                                onClick={() => toggleExpand(newsItem.id)}
                                aria-expanded={expandedId === newsItem.id}
                            >
                                <span className={styles.newsItem__toggleText}>
                                    {expandedId === newsItem.id ? 'свернуть' : 'развернуть'}
                                </span>
                                <svg className={styles.newsItem__icon} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                        </div>
                        <div className={styles.newsItem__content}>
                            <p>{newsItem.content}</p>
                        </div>
                    </article>
                )
            })}
        </div>
    )
}