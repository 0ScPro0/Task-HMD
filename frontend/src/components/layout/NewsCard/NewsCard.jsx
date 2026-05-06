import { useEffect, useState } from "react";
import styles from "./NewsCard.module.css";
import { newsService } from "../../../services/api/news";

export function NewsCard() {
    const [news, setNews] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchNews = async () => {
            try {
                setLoading(true);
                const latestNews = await newsService.getNewsLast();
                console.log("Полученные данные:", latestNews);
                console.log("Есть ли данные:", !!latestNews);
                
                // Убедимся, что данные пришли
                if (latestNews && latestNews.id) {
                    setNews(latestNews);
                    setError(null);
                } else {
                    setError("Новости не найдены");
                }
            } catch (err) {
                setError("Не удалось загрузить новости");
                console.error("Error fetching news:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchNews();
    }, []);

    if (loading) {
        return (
            <article className={styles.newsCard}>
                <div className={styles.newsCard__body}>Загрузка...</div>
            </article>
        );
    }

    // Отдельная проверка на ошибку
    if (error) {
        return (
            <article className={styles.newsCard}>
                <div className={styles.newsCard__body}>{error}</div>
            </article>
        );
    }

    // Отдельная проверка на наличие новости
    if (!news || !news.id) {
        return (
            <article className={styles.newsCard}>
                <div className={styles.newsCard__body}>Новости не найдены</div>
            </article>
        );
    }

    // Форматирование даты
    const formatDate = (dateString) => {
        if (!dateString) return "Дата не указана";
        const date = new Date(dateString);
        return date.toLocaleDateString("ru-RU", {
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    };

    return (
        <article className={styles.newsCard}>
            <div className={styles.newsCard__date}>
                {formatDate(news.created_at)}
            </div>
            <h3 className={styles.newsCard__heading}>
                {news.title}
            </h3>
            <p className={styles.newsCard__body}>
                {news.content}
            </p>
            <a href="/news" className={styles.newsCard__link}>
                Все новости →
            </a>
        </article>
    );
}