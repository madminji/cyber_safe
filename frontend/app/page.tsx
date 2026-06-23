import {
  ArrowRight,
  BadgeCheck,
  BookOpenCheck,
  CheckCircle2,
  MessageSquareWarning,
  PhoneCall,
  SearchCheck,
  GraduationCap,
  BrainCircuit,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import Link from "next/link";

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <div className="hero-orb orb-one" />
        <div className="hero-orb orb-two" />
        <div className="container hero-grid">
          <div className="hero-copy">
            <span className="eyebrow">
              <Sparkles size={15} />
              Знания, которые защищают
            </span>
            <h1>
              Будьте на шаг впереди <em>цифровых мошенников</em>
            </h1>
            <p>
              Научитесь распознавать обман, проверьте подозрительный номер и
              подтвердите свои знания официальным сертификатом.
            </p>
            <div className="hero-actions">
              <Link className="button button-primary" href="/quiz">
                Пройти тест
                <ArrowRight size={18} />
              </Link>
              <Link className="button button-ghost" href="/numbers">
                Проверить номер
              </Link>
            </div>
            <div className="trust-row">
              <span>
                <CheckCircle2 size={17} /> Бесплатно
              </span>
              <span>
                <CheckCircle2 size={17} /> Безопасно
              </span>
              <span>
                <CheckCircle2 size={17} /> RU / UZ
              </span>
            </div>
          </div>
          <div className="hero-visual">
            <div className="shield-stage">
              <div className="shield-rings" />
              <div className="hero-shield">
                <ShieldAlert size={76} strokeWidth={1.45} />
                <span>CYBER</span>
                <strong>SAFE</strong>
              </div>
              <div className="floating-card card-a">
                <BadgeCheck size={22} />
                <span>
                  Сертификат
                  <strong>подтверждён</strong>
                </span>
              </div>
              <div className="floating-card card-b">
                <PhoneCall size={22} />
                <span>
                  Номер
                  <strong>проверен</strong>
                </span>
              </div>
              <div className="floating-card card-c">
                <BookOpenCheck size={22} />
                <span>
                  Уровень
                  <strong>Эксперт</strong>
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-heading">
            <span className="eyebrow">Ваш цифровой щит</span>
            <h2>Три инструмента — одна цель</h2>
            <p>Помочь принять верное решение до того, как станет слишком поздно.</p>
          </div>
          <div className="feature-grid">
            <Link href="/quiz" className="feature-card feature-blue">
              <span className="feature-icon">
                <BookOpenCheck />
              </span>
              <span className="feature-number">01</span>
              <h3>Проверьте знания</h3>
              <p>
                10 практических ситуаций из реальной жизни и понятные объяснения
                после каждого ответа.
              </p>
              <span className="text-link">
                Начать тест <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/numbers" className="feature-card feature-amber">
              <span className="feature-icon">
                <PhoneCall />
              </span>
              <span className="feature-number">02</span>
              <h3>Проверьте номер</h3>
              <p>
                Узнайте, поступали ли подтверждённые жалобы, и сообщите о
                подозрительном звонке.
              </p>
              <span className="text-link">
                Проверить <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/analyzer" className="feature-card feature-green">
              <span className="feature-icon">
                <SearchCheck />
              </span>
              <span className="feature-number">03</span>
              <h3>Проверьте сообщение</h3>
              <p>
                Разберите подозрительную ссылку или SMS без перехода на сайт и
                без сохранения исходного содержимого.
              </p>
              <span className="text-link">
                Открыть анализатор <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/courses" className="feature-card feature-cyan">
              <span className="feature-icon">
                <GraduationCap />
              </span>
              <span className="feature-number">04</span>
              <h3>Пройдите обучение</h3>
              <p>
                Освойте основные правила защиты короткими уроками и закрепите
                знания контрольными вопросами.
              </p>
              <span className="text-link">
                Открыть курсы <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/simulator" className="feature-card feature-red">
              <span className="feature-icon">
                <BrainCircuit />
              </span>
              <span className="feature-number">05</span>
              <h3>Отразите атаку</h3>
              <p>
                Потренируйтесь в безопасном диалоге с мошенником и получите
                подробный разбор применённых манипуляций.
              </p>
              <span className="text-link">
                Запустить симуляцию <ArrowRight size={17} />
              </span>
            </Link>
            <Link href="/certificates" className="feature-card feature-violet">
              <span className="feature-icon">
                <BadgeCheck />
              </span>
              <span className="feature-number">06</span>
              <h3>Получите сертификат</h3>
              <p>
                Подтвердите уровень цифровой грамотности именным документом с
                публичной QR-проверкой.
              </p>
              <span className="text-link">
                Мои сертификаты <ArrowRight size={17} />
              </span>
            </Link>
          </div>
        </div>
      </section>

      <section className="danger-section">
        <div className="container danger-grid">
          <div>
            <span className="eyebrow eyebrow-light">
              <MessageSquareWarning size={15} /> Запомните главное
            </span>
            <h2>Мошенники торопят. Вы — остановитесь.</h2>
          </div>
          <div className="danger-list">
            <p>Никому не называйте SMS-код</p>
            <p>Не устанавливайте APK из Telegram</p>
            <p>Не переводите деньги на «безопасный счёт»</p>
            <p>Перезвоните в банк по официальному номеру</p>
          </div>
        </div>
      </section>
    </>
  );
}
