import styles from "./Home.module.css"
import { Header } from "../../components/layout/Header/Header"
import { Hero } from "../../components/layout/Hero/Hero"
import { NewsCard } from "../../components/layout/NewsCard/NewsCard"
import { ServiceCard } from "../../components/layout/ServiceCard/ServiceCard"
import { Footer } from "../../components/layout/Footer/Footer"

export function Home() {
    const handlePlumberClick = () => {
        alert('Заявка сантехнику будет доступна в ближайшее время.')
    }

    const handleElectricianClick = () => {
        alert('Заявка электрику будет доступна в ближайшее время.')
    }

    return (
        <div className={styles.home}>
            <Header />
            <main className={styles.main}>
                <Hero />
                <h2 className={styles["section-title"]}>Последние новости</h2>
                <NewsCard />
                <h2 className={styles["section-title"]}>Услуги</h2>
                <div className={styles.services}>
                    <ServiceCard
                        icon={
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                strokeWidth="2">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M19.428 15.428a2 2 0 0 0-1.022-.547l-2.387-.477a6 6 0 0 0-3.86.517l-.318.158a6 6 0 0 1-3.86.517L6.05 15.21a2 2 0 0 0-1.806.547M8
                                 4h8l-1 1v5.172a2 2 0 0 0 .586
                                 1.414l5 5c1.26 1.26.367 3.414-1.415
                                 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0
                                 0 0 9 10.172V5L8 4z" />
                            </svg>
                        }
                        name="Вызов сантехника"
                        description="Устранение протечек, засоров, замена труб"
                        onClick={handlePlumberClick}
                    />
                    <ServiceCard
                        icon={
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"
                                strokeWidth="2">
                                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        }
                        name="Вызов электрика"
                        description="Ремонт проводки, замена светильников, автоматов"
                        onClick={handleElectricianClick}
                    />
                </div>
            </main>
            <Footer />
        </div>
    )
}