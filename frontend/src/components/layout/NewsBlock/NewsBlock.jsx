import { useState } from "react"
import styles from "./NewsBlock.module.css"
// import { useNews } from "../../hooks/useNews" // раскомментировать, когда бекенд готов

// Временные данные для демонстрации (заменятся на данные с бекенда)
const initialNews = [
    {
        id: 1,
        date: "5 апреля 2026",
        title: "Плановая промывка системы отопления в домах по ул. Ленина",
        content: "С 7 по 10 апреля 2026 года будут проводиться работы по плановой промывке внутридомовой системы отопления в жилых домах № 12, 14 и 16 по улице Ленина. На период проведения работ горячее водоснабжение будет временно приостановлено. Приносим извинения за временные неудобства. По всем вопросам обращайтесь по телефону диспетчерской."
    },
    {
        id: 2,
        date: "1 апреля 2026",
        title: "Обновление графика вывоза ТКО в весенний период",
        content: "Уважаемые жители! С 1 апреля 2026 года вводится новый график вывоза твёрдых коммунальных отходов. Мусоровозы будут прибывать во дворы в утренние часы (с 06:00 до 09:00) для минимизации шума. Просим вас своевременно выносить мусор в контейнеры и не оставлять отходы на площадке после вывоза."
    },
    {
        id: 3,
        date: "28 марта 2026",
        title: "Замена входных групп в подъездах №3 и №4 по пр. Мира",
        content: "В рамках программы капитального ремонта фасадов и входных групп, в период с 30 марта по 5 апреля будут заменены дверные блоки и установлены новые козырьки в подъездах №3 и №4. Работы будут выполняться в дневное время. Доступ в подъезды сохранён через временные конструкции."
    }
]

export function NewsBlock() {
    const [expandedId, setExpandedId] = useState(null)

    const toggleExpand = (id) => {
        setExpandedId(prev => prev === id ? null : id)
    }

    // TODO: заменить на хук, который будет получать новости с бекенда через axios
    // const { news, isLoading, error } = useNews()
    // if (isLoading) return <div>Загрузка новостей...</div>
    // if (error) return <div>Ошибка: {error}</div>
    // const displayedNews = news.length > 0 ? news : initialNews

    const displayedNews = initialNews // временно используем статические данные

    return (
        <div className={styles.newsList}>
            {displayedNews.map(item => (
                <article key={item.id} className={`${styles.newsItem} ${expandedId === item.id ? styles.active : ''}`}>
                    <div className={styles.newsItem__header}>
                        <div className={styles.newsItem__meta}>
                            <span className={styles.newsItem__date}>{item.date}</span>
                            <h2 className={styles.newsItem__title}>{item.title}</h2>
                        </div>
                        <button
                            className={styles.newsItem__toggle}
                            onClick={() => toggleExpand(item.id)}
                            aria-expanded={expandedId === item.id}
                        >
                            <span className={styles.newsItem__toggleText}>
                                {expandedId === item.id ? 'свернуть' : 'развернуть'}
                            </span>
                            <svg className={styles.newsItem__icon} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>
                    <div className={styles.newsItem__content}>
                        <p>{item.content}</p>
                    </div>
                </article>
            ))}
        </div>
    )
}