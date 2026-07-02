"use client";

import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  BookOpenText,
  Check,
  CheckCircle2,
  ClipboardList,
  Clock3,
  ListChecks,
  PlayCircle,
  ShieldCheck,
  Sparkles,
  Target,
  X,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import type { TranslationKey } from "@/lib/translations";
import { LessonDetail } from "@/lib/types";

type AnswerResult = {
  correct: boolean;
  completed: boolean;
  completed_now: boolean;
  explanation: string;
};

type LessonSection = {
  title: string;
  type: "intro" | "theory" | "risk" | "steps" | "practice" | "note" | "default";
  items: string[];
};

type LessonBlock = NonNullable<LessonDetail["blocks"]>[number];
type LessonTask = NonNullable<LessonDetail["tasks"]>[number];
type LessonQuestion = NonNullable<LessonDetail["questions"]>[number];

const lessonUi = {
  ru: {
    theoryPlus: "Теория + практика + мини-тест",
    learningEyebrow: "Что вы научитесь делать",
    learningTitle: "После урока у вас будет понятный алгоритм действий",
    recognizeTitle: "Распознавать ситуацию",
    recognizeText: "Понимать, где мошенник давит на срочность, страх или выгоду.",
    safeStepTitle: "Выбирать безопасный шаг",
    safeStepText: "Проверять источник через официальный канал, не отдавая коды.",
    selfCheckTitle: "Проверить себя",
    selfCheckText: "Сначала изучить теорию, затем выполнить задания и мини-тест.",
    readingLead:
      "Сначала изучите основные понятия и правила. После теории будут признаки риска, практические задания и мини-тест.",
    riskSigns: "Ключевые признаки риска",
    practiceEyebrow: "Практика после теории",
    practiceTitle: "Выполните задания",
    practiceText: "Теперь примените правила из урока на коротких учебных ситуациях.",
    taskFallback: "Задание",
    textPlaceholder: "Введите короткий ответ или своё правило...",
    answerSaved: "Ответ сохранён на этой странице. Можно сравнить его с правилами из урока.",
    correct: "Верно.",
    correctOption: "Правильный вариант",
    question: "Вопрос",
    blockLabels: {
      theory: "Теория",
      definition: "Определение",
      example: "Пример",
      warning: "Важно",
      note: "Заметка",
      code: "Код",
      checklist: "Чеклист",
      task: "Практика",
      quiz: "Мини-тест",
      materials: "Материалы",
    },
  },
  uz: {
    theoryPlus: "Nazariya + amaliyot + mini-test",
    learningEyebrow: "Nimani o‘rganasiz",
    learningTitle: "Darsdan so‘ng sizda aniq harakat algoritmi bo‘ladi",
    recognizeTitle: "Vaziyatni tanish",
    recognizeText: "Firibgar shoshilish, qo‘rquv yoki foyda bilan bosim qilayotganini tushunish.",
    safeStepTitle: "Xavfsiz qadamni tanlash",
    safeStepText: "Kodlarni bermasdan, manbani rasmiy kanal orqali tekshirish.",
    selfCheckTitle: "O‘zingizni tekshirish",
    selfCheckText: "Avval nazariyani o‘rganish, keyin topshiriqlar va mini-testni bajarish.",
    readingLead:
      "Avval asosiy tushunchalar va qoidalarni o‘rganing. Nazariyadan keyin xavf belgilari, amaliy topshiriqlar va mini-test bo‘ladi.",
    riskSigns: "Asosiy xavf belgilari",
    practiceEyebrow: "Nazariyadan keyingi amaliyot",
    practiceTitle: "Topshiriqlarni bajaring",
    practiceText: "Endi darsdagi qoidalarni qisqa o‘quv vaziyatlarida qo‘llang.",
    taskFallback: "Topshiriq",
    textPlaceholder: "Qisqa javob yoki shaxsiy qoidangizni kiriting...",
    answerSaved: "Javob shu sahifada saqlandi. Uni dars qoidalari bilan solishtirishingiz mumkin.",
    correct: "To‘g‘ri.",
    correctOption: "To‘g‘ri variant",
    question: "Savol",
    blockLabels: {
      theory: "Nazariya",
      definition: "Ta’rif",
      example: "Misol",
      warning: "Muhim",
      note: "Eslatma",
      code: "Kod",
      checklist: "Tekshiruv ro‘yxati",
      task: "Amaliyot",
      quiz: "Mini-test",
      materials: "Materiallar",
    },
  },
} as const;

const majorHeadingTypes: Record<string, LessonSection["type"]> = {
  "Основной учебный материал": "theory",
  "Теория": "theory",
  "Цель урока": "intro",
  "На что обратить внимание": "risk",
  "Признаки риска": "risk",
  "Безопасный алгоритм действий": "steps",
  "Что делать": "steps",
  "Практическое задание для пользователя": "practice",
  "Практика": "practice",
  "Актуальное дополнение": "note",
  "Памятка": "note",
  "Дополнительный разбор": "note",
  "Дополнительно": "note",
};

const shortHeadingHints = [
  "Что такое",
  "Почему",
  "Как",
  "Пример",
  "Важно",
  "Безопасный",
  "На что",
  "Практика",
  "Итог",
];

function isLikelyHeading(line: string, nextLine?: string) {
  if (majorHeadingTypes[line]) return true;
  if (!nextLine || line.length > 82) return false;
  if (/[.!?]$/.test(line)) return false;
  return shortHeadingHints.some((hint) => line.startsWith(hint));
}

function parseLessonContent(content: string): LessonSection[] {
  const lines = content
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  const sections: LessonSection[] = [];
  let current: LessonSection = {
    title: "О чём этот урок",
    type: "intro",
    items: [],
  };

  const pushCurrent = () => {
    if (current.items.length) {
      sections.push(current);
    }
  };

  lines.forEach((line, index) => {
    const nextLine = lines[index + 1];
    if (isLikelyHeading(line, nextLine)) {
      pushCurrent();
      current = {
        title: line,
        type: majorHeadingTypes[line] || "default",
        items: [],
      };
      return;
    }
    current.items.push(line);
  });

  pushCurrent();
  return sections;
}

function sectionIcon(type: LessonSection["type"]) {
  if (type === "risk") return <AlertTriangle size={20} />;
  if (type === "steps") return <ShieldCheck size={20} />;
  if (type === "practice") return <ClipboardList size={20} />;
  if (type === "note") return <Sparkles size={20} />;
  if (type === "intro") return <Target size={20} />;
  return <BookOpenText size={20} />;
}

const riskTrainingCards = [
  {
    text: "Ваша карта заблокирована. Срочно подтвердите данные по ссылке.",
    risky: true,
    reason: "Есть срочность, угроза блокировки и ссылка для ввода данных.",
  },
  {
    text: "Вы выиграли 1 000 000 сум. Отправьте фото паспорта для получения приза.",
    risky: true,
    reason: "Обещание выигрыша и просьба отправить документ — высокий риск.",
  },
  {
    text: "Ваш заказ доставлен. Проверьте трек-номер в официальном приложении.",
    risky: false,
    reason: "Безопаснее открывать трек внутри официального приложения.",
  },
  {
    text: "Служба безопасности банка просит назвать SMS-код для отмены перевода.",
    risky: true,
    reason: "SMS-код нельзя передавать никому, даже “сотруднику банка”.",
  },
  {
    text: "Напоминание: обновите приложение через официальный магазин приложений.",
    risky: false,
    reason: "Официальный магазин — нормальный и безопасный канал обновления.",
  },
];

const dataSortingCards = [
  { text: "Имя и город", zone: "public" },
  { text: "Номер телефона", zone: "trusted" },
  { text: "Фото паспорта", zone: "trusted" },
  { text: "SMS-код", zone: "secret" },
  { text: "CVV-код карты", zone: "secret" },
  { text: "Пароль от почты", zone: "secret" },
];

const dataZones = [
  { id: "public", label: "Можно указывать публично" },
  { id: "trusted", label: "Только проверенным сервисам" },
  { id: "secret", label: "Никому не передавать" },
];

const scenarioChoices = [
  {
    text: "В сообщении обещают выплату и просят перейти по короткой ссылке.",
    options: [
      { text: "Перейти и проверить", safe: false },
      { text: "Открыть официальный сайт вручную", safe: true },
      { text: "Отправить ссылку друзьям", safe: false },
    ],
    reason: "Безопаснее открыть официальный сайт вручную и не использовать ссылку из сообщения.",
  },
  {
    text: "Звонящий говорит, что он из банка, и просит назвать SMS-код.",
    options: [
      { text: "Назвать код", safe: false },
      { text: "Попросить перезвонить", safe: false },
      { text: "Завершить разговор и позвонить в банк самому", safe: true },
    ],
    reason: "Код подтверждения нельзя сообщать никому. Связывайтесь с банком самостоятельно.",
  },
  {
    text: "В Telegram прислали APK “для получения бонуса”.",
    options: [
      { text: "Установить APK", safe: false },
      { text: "Проверить приложение в официальном магазине", safe: true },
      { text: "Отключить защиту телефона", safe: false },
    ],
    reason: "Приложения безопаснее устанавливать только из официального магазина или официального сайта.",
  },
];

const homeChecklistItems = [
  "Проверить активные сеансы Telegram",
  "Включить двухфакторную защиту на почте",
  "Проверить, кто видит номер телефона в мессенджере",
  "Удалить неизвестные приложения",
];

const numberPracticeCards = [
  {
    status: "Не найден",
    action: "Не считать номер безопасным автоматически",
    reason: "Отсутствие жалоб не доказывает безопасность номера.",
  },
  {
    status: "Подозрительно",
    action: "Не отвечать и сохранить доказательства",
    reason: "Есть признаки риска, лучше не продолжать разговор.",
  },
  {
    status: "Опасно",
    action: "Заблокировать номер и отправить репорт",
    reason: "Подтверждённый риск нужно зафиксировать для модерации.",
  },
];

const incidentChecklists: Record<string, string[]> = {
  "Назвал код": [
    "Сразу заблокировать карту или аккаунт",
    "Сменить пароль",
    "Отключить чужие сеансы",
    "Сообщить в банк или поддержку",
  ],
  "Установил APK": [
    "Удалить приложение",
    "Отключить интернет при подозрительной активности",
    "Проверить разрешения приложений",
    "Сменить пароли с другого устройства",
  ],
  "Отправил паспорт": [
    "Сохранить переписку",
    "Сообщить в сервис/банк",
    "Следить за заявками на займы",
    "Подготовить обращение в органы",
  ],
  "Перевёл деньги": [
    "Связаться с банком немедленно",
    "Сохранить чек и переписку",
    "Подать заявление",
    "Сообщить номер/аккаунт в базу",
  ],
};

function PracticeTaskCard({ item, index }: { item: string; index: number }) {
  const [riskAnswers, setRiskAnswers] = useState<Record<number, boolean>>({});
  const [rules, setRules] = useState(["", "", ""]);
  const [zones, setZones] = useState<Record<string, string>>({});
  const [scenarioAnswers, setScenarioAnswers] = useState<Record<number, number>>({});
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({});
  const [selectedIncident, setSelectedIncident] = useState("Назвал код");
  const [reportDraft, setReportDraft] = useState("");
  const [done, setDone] = useState(false);
  const [title, ...descriptionParts] = item.split(". ");
  const description = descriptionParts.join(". ") || item;
  const lower = item.toLowerCase();
  const isRiskCards =
    lower.includes("сообщени") &&
    (lower.includes("карточ") || lower.includes("6 учебных"));
  const isRules =
    lower.includes("запишите 3") ||
    lower.includes("3 личных правила") ||
    lower.includes("10 правил") ||
    lower.includes("карточку безопасности");
  const isSorting = lower.includes("распредел") && lower.includes("зон");
  const isScenario = lower.includes("учебный кейс") || lower.includes("безопасное действие");
  const isHomeChecklist = lower.includes("домашнее задание") || lower.includes("реальный элемент");
  const isNumberPractice = lower.includes("карточки номеров") || lower.includes("репорт");
  const isIncidentPractice = lower.includes("назвал код") || lower.includes("персональный чек-лист");

  if (isRiskCards) {
    const answeredCount = Object.keys(riskAnswers).length;
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>{description}</p>
          </div>
        </div>
        <div className="practice-risk-grid">
          {riskTrainingCards.map((card, cardIndex) => {
            const selected = riskAnswers[cardIndex];
            const answered = typeof selected === "boolean";
            const correct = answered && selected === card.risky;
            return (
              <div
                className={`practice-risk-card ${
                  answered ? (correct ? "correct" : "wrong") : ""
                }`}
                key={card.text}
              >
                <p>{card.text}</p>
                <div>
                  <button onClick={() => setRiskAnswers({ ...riskAnswers, [cardIndex]: true })}>
                    Риск есть
                  </button>
                  <button onClick={() => setRiskAnswers({ ...riskAnswers, [cardIndex]: false })}>
                    Безопасно
                  </button>
                </div>
                {answered && (
                  <small>
                    {correct ? "Верно. " : "Не совсем. "}
                    {card.reason}
                  </small>
                )}
              </div>
            );
          })}
        </div>
        <div className="practice-score-line">
          Выполнено: {answeredCount}/{riskTrainingCards.length}
        </div>
      </article>
    );
  }

  if (isRules) {
    const ruleCount = lower.includes("10 правил") || lower.includes("карточку безопасности") ? 5 : 3;
    const visibleRules = rules.length === ruleCount ? rules : Array(ruleCount).fill("");
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>Сформулируйте свои правила коротко и конкретно.</p>
          </div>
        </div>
        <div className="practice-rule-list">
          {visibleRules.map((rule, ruleIndex) => (
            <label key={ruleIndex}>
              Правило {ruleIndex + 1}
              <input
                value={rule}
                onChange={(event) => {
                  const nextRules = [...visibleRules];
                  nextRules[ruleIndex] = event.target.value;
                  setRules(nextRules);
                }}
                placeholder={
                  ruleIndex === 0
                    ? "Например: не называю SMS-коды"
                    : "Введите своё правило"
                }
              />
            </label>
          ))}
        </div>
        {visibleRules.filter(Boolean).length === ruleCount && (
          <div className="practice-score-line success">
            Отлично. Эти правила можно использовать как личную памятку.
          </div>
        )}
      </article>
    );
  }

  if (isScenario) {
    const answeredCount = Object.keys(scenarioAnswers).length;
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>Выберите безопасное действие в каждом кейсе.</p>
          </div>
        </div>
        <div className="practice-risk-grid">
          {scenarioChoices.map((scenario, scenarioIndex) => {
            const selected = scenarioAnswers[scenarioIndex];
            const answered = typeof selected === "number";
            const correct = answered && scenario.options[selected]?.safe;
            return (
              <div
                className={`practice-risk-card ${
                  answered ? (correct ? "correct" : "wrong") : ""
                }`}
                key={scenario.text}
              >
                <p>{scenario.text}</p>
                <div>
                  {scenario.options.map((option, optionIndex) => (
                    <button
                      key={option.text}
                      onClick={() =>
                        setScenarioAnswers({
                          ...scenarioAnswers,
                          [scenarioIndex]: optionIndex,
                        })
                      }
                    >
                      {option.text}
                    </button>
                  ))}
                </div>
                {answered && (
                  <small>
                    {correct ? "Верно. " : "Не совсем. "}
                    {scenario.reason}
                  </small>
                )}
              </div>
            );
          })}
        </div>
        <div className="practice-score-line">
          Решено: {answeredCount}/{scenarioChoices.length}
        </div>
      </article>
    );
  }

  if (isHomeChecklist) {
    const checkedCount = Object.values(checkedItems).filter(Boolean).length;
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>Отметьте, что вы готовы проверить после урока.</p>
          </div>
        </div>
        <div className="practice-checklist">
          {homeChecklistItems.map((checkItem) => (
            <label key={checkItem}>
              <input
                type="checkbox"
                checked={Boolean(checkedItems[checkItem])}
                onChange={(event) =>
                  setCheckedItems({
                    ...checkedItems,
                    [checkItem]: event.target.checked,
                  })
                }
              />
              {checkItem}
            </label>
          ))}
        </div>
        <div className={checkedCount ? "practice-score-line success" : "practice-score-line"}>
          Выбрано: {checkedCount}/{homeChecklistItems.length}
        </div>
      </article>
    );
  }

  if (isNumberPractice) {
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>Сопоставьте статус номера с безопасным действием.</p>
          </div>
        </div>
        <div className="practice-sort-list">
          {numberPracticeCards.map((card) => (
            <div className="correct" key={card.status}>
              <strong>{card.status}</strong>
              <p>{card.action}</p>
              <small>{card.reason}</small>
            </div>
          ))}
        </div>
      </article>
    );
  }

  if (isIncidentPractice) {
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>Выберите ситуацию и получите чек-лист первых действий.</p>
          </div>
        </div>
        <div className="practice-incident-tabs">
          {Object.keys(incidentChecklists).map((incident) => (
            <button
              className={selectedIncident === incident ? "selected" : ""}
              key={incident}
              onClick={() => setSelectedIncident(incident)}
            >
              {incident}
            </button>
          ))}
        </div>
        <ol className="practice-incident-list">
          {incidentChecklists[selectedIncident].map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      </article>
    );
  }

  if (isSorting) {
    const completedCount = Object.keys(zones).length;
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{title || `Задание ${index + 1}`}</strong>
            <p>{description}</p>
          </div>
        </div>
        <div className="practice-sort-list">
          {dataSortingCards.map((card) => {
            const selectedZone = zones[card.text];
            const answered = Boolean(selectedZone);
            const correct = selectedZone === card.zone;
            return (
              <div className={answered ? (correct ? "correct" : "wrong") : ""} key={card.text}>
                <strong>{card.text}</strong>
                <div>
                  {dataZones.map((zone) => (
                    <button
                      className={selectedZone === zone.id ? "selected" : ""}
                      key={zone.id}
                      onClick={() => setZones({ ...zones, [card.text]: zone.id })}
                    >
                      {zone.label}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        <div className="practice-score-line">
          Распределено: {completedCount}/{dataSortingCards.length}
        </div>
      </article>
    );
  }

  return (
    <article className="practice-interactive-card">
      <div className="practice-task-head">
        <CheckCircle2 size={20} />
        <div>
          <strong>{title || `Задание ${index + 1}`}</strong>
          <p>{description}</p>
        </div>
      </div>
      <button
        className={done ? "practice-done-button done" : "practice-done-button"}
        onClick={() => setDone(!done)}
      >
        {done ? "Готово" : "Отметить как выполненное"}
      </button>
      {lower.includes("шаблон обращения") || lower.includes("корректный репорт") ? (
        <textarea
          className="practice-draft-field"
          value={reportDraft}
          onChange={(event) => setReportDraft(event.target.value)}
          placeholder="Кратко опишите факты: дата, канал связи, что просили сделать, сумма ущерба, какие доказательства есть."
        />
      ) : null}
    </article>
  );
}

function LessonSectionCard({ section }: { section: LessonSection }) {
  const listMode = section.type === "risk" || section.type === "steps";
  const exerciseMode = section.type === "practice";
  return (
    <section className={`lesson-content-section ${section.type}`}>
      <h3>
        <span>{sectionIcon(section.type)}</span>
        {section.title}
      </h3>
      {exerciseMode ? (
        <div className="lesson-practice-tasks">
          {section.items.map((item, index) => (
            <PracticeTaskCard item={item} index={index} key={item} />
          ))}
        </div>
      ) : listMode ? (
        section.type === "steps" ? (
          <ol>
            {section.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ol>
        ) : (
          <ul>
            {section.items.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        )
      ) : (
        section.items.map((item) => <p key={item}>{item}</p>)
      )}
    </section>
  );
}

function getBlockMeta(language: "ru" | "uz"): Record<
  LessonBlock["type"],
  { className: string; label: string; icon: ReactNode }
> {
  const labels = lessonUi[language].blockLabels;
  return {
  theory: {
    className: "theory",
    label: labels.theory,
    icon: <BookOpenText size={20} />,
  },
  definition: {
    className: "definition",
    label: labels.definition,
    icon: <Target size={20} />,
  },
  example: {
    className: "example",
    label: labels.example,
    icon: <Sparkles size={20} />,
  },
  warning: {
    className: "warning",
    label: labels.warning,
    icon: <AlertTriangle size={20} />,
  },
  note: {
    className: "note",
    label: labels.note,
    icon: <ShieldCheck size={20} />,
  },
  code: {
    className: "code",
    label: labels.code,
    icon: <ClipboardList size={20} />,
  },
  checklist: {
    className: "checklist",
    label: labels.checklist,
    icon: <ListChecks size={20} />,
  },
  task: {
    className: "practice",
    label: labels.task,
    icon: <ClipboardList size={20} />,
  },
  quiz: {
    className: "quiz",
    label: labels.quiz,
    icon: <CheckCircle2 size={20} />,
  },
  materials: {
    className: "materials",
    label: labels.materials,
    icon: <BookOpenText size={20} />,
  },
};
}

function renderTextBlocks(text: string) {
  return text
    .split(/\n{2,}/)
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => {
      const lines = part
        .split(/\n/)
        .map((line) => line.trim())
        .filter(Boolean);
      const isList = lines.length > 1 && lines.every((line) => /^[-*•]\s+/.test(line));
      if (isList) {
        return (
          <ul key={part}>
            {lines.map((line) => (
              <li key={line}>{line.replace(/^[-*•]\s+/, "")}</li>
            ))}
          </ul>
        );
      }
      return <p key={part}>{part}</p>;
    });
}

function localizedDataText(
  value: unknown,
  language: "ru" | "uz",
): string {
  if (typeof value === "string") return value;
  if (!value || typeof value !== "object") return "";
  const data = value as Record<string, unknown>;
  const localized = data[language] || data[`text_${language}`] || data.text || data.ru;
  return typeof localized === "string" ? localized : "";
}

function LessonBlockCard({
  block,
  language,
}: {
  block: LessonBlock;
  language: "ru" | "uz";
}) {
  const blockMeta = getBlockMeta(language);
  const meta = blockMeta[block.type] || blockMeta.theory;
  const items = Array.isArray(block.data?.items)
    ? block.data.items
        .map((item) => localizedDataText(item, language))
        .filter(Boolean)
    : [];
  const links = Array.isArray(block.data?.links) ? block.data.links : [];

  return (
    <section className={`lesson-content-section lesson-block ${meta.className}`}>
      <h3>
        <span>{meta.icon}</span>
        {block.title || meta.label}
      </h3>
      {block.type === "code" ? (
        <pre className="lesson-code-block">
          <code>{block.body}</code>
        </pre>
      ) : block.body ? (
        renderTextBlocks(block.body)
      ) : null}
      {items.length > 0 && (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      )}
      {links.length > 0 && (
        <div className="lesson-material-links">
          {links.map((link) => (
            <a href={link.url} key={link.url} rel="noreferrer" target="_blank">
              {link.title || link.url}
            </a>
          ))}
        </div>
      )}
    </section>
  );
}

function StructuredTaskCard({
  task,
  index,
  language,
}: {
  task: LessonTask;
  index: number;
  language: "ru" | "uz";
}) {
  const ui = lessonUi[language];
  const [textAnswer, setTextAnswer] = useState("");
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [selected, setSelected] = useState<Record<string, string>>({});
  const items = Array.isArray(task.data?.items) ? task.data.items : [];
  const options = Array.isArray(task.data?.options) ? task.data.options : [];

  return (
    <article className="practice-interactive-card structured-task-card">
      <div className="practice-task-head">
        <CheckCircle2 size={20} />
        <div>
          <strong>{task.title || `${ui.taskFallback} ${index + 1}`}</strong>
          <p>{task.instruction}</p>
        </div>
      </div>

      {task.type === "text" && (
        <>
          <textarea
            className="practice-draft-field"
            value={textAnswer}
            onChange={(event) => setTextAnswer(event.target.value)}
            placeholder={ui.textPlaceholder}
          />
          {textAnswer.trim().length > 0 && (
            <div className="practice-score-line success">
              {ui.answerSaved}
            </div>
          )}
        </>
      )}

      {task.type === "checklist" && (
        <div className="practice-checklist">
          {items.map((item) => (
            <label key={localizedDataText(item.text || item, language)}>
              <input
                checked={Boolean(checked[localizedDataText(item.text || item, language)])}
                onChange={(event) =>
                  setChecked({
                    ...checked,
                    [localizedDataText(item.text || item, language)]: event.target.checked,
                  })
                }
                type="checkbox"
              />
              {localizedDataText(item.text || item, language)}
            </label>
          ))}
        </div>
      )}

      {(task.type === "sorting" || task.type === "scenario") && (
        <div className="practice-sort-list">
          {items.map((item) => {
            const itemText = localizedDataText(item.text || item, language);
            const correctValue = item.risk || item.category || "";
            const selectedValue = selected[itemText];
            const answered = Boolean(selectedValue);
            const correct = answered && selectedValue === correctValue;
            const availableOptions =
              options.length > 0
                ? options
                : task.type === "sorting"
                  ? ["low", "medium", "high"]
                  : ["safe", "suspicious", "dangerous"];
            return (
              <div
                className={answered ? (correct ? "correct" : "wrong") : ""}
                key={itemText}
              >
                <strong>{itemText}</strong>
                <div>
                  {availableOptions.map((option) => (
                    <button
                      className={selectedValue === option ? "selected" : ""}
                      key={option}
                      onClick={() => setSelected({ ...selected, [itemText]: option })}
                    >
                      {option}
                    </button>
                  ))}
                </div>
                {answered && correctValue && (
                  <small>
                    {correct ? ui.correct : `${ui.correctOption}: ${correctValue}.`}
                  </small>
                )}
              </div>
            );
          })}
        </div>
      )}
    </article>
  );
}

function LessonQuestionsCheckpoint({
  questions,
  completed,
  busy,
  selectedChoices,
  answerResults,
  onSelect,
  onSubmit,
  t,
  language,
}: {
  questions: LessonQuestion[];
  completed: boolean;
  busy: boolean;
  selectedChoices: Record<number, string>;
  answerResults: Record<number, AnswerResult>;
  onSelect: (questionIndex: number, choiceId: string) => void;
  onSubmit: (questionIndex: number) => void;
  t: (key: TranslationKey, values?: Record<string, string | number>) => string;
  language: "ru" | "uz";
}) {
  if (questions.length === 0) return null;
  const ui = lessonUi[language];

  return (
    <section className="lesson-checkpoint lesson-page-checkpoint">
      <span className="eyebrow">{t("course.checkYourself")}</span>
      <div className="lesson-question-stack">
        {questions.map((question, questionIndex) => {
          const selectedChoice = selectedChoices[questionIndex] || "";
          const answerResult = answerResults[questionIndex];
          return (
            <article className="lesson-question-card" key={`${question.text}-${questionIndex}`}>
              <span className="lesson-question-number">
                {ui.question} {questionIndex + 1} / {questions.length}
              </span>
              <h2>{question.text}</h2>
              <div className="lesson-choices">
                {question.choices.map((choice) => (
                  <button
                    key={choice.id}
                    className={selectedChoice === choice.id ? "selected" : ""}
                    onClick={() => onSelect(questionIndex, choice.id)}
                  >
                    <span>{String.fromCharCode(64 + choice.order)}</span>
                    {choice.text}
                  </button>
                ))}
              </div>
              {answerResult && (
                <div
                  className={
                    answerResult.correct
                      ? "checkpoint-result correct"
                      : "checkpoint-result wrong"
                  }
                >
                  {answerResult.correct ? <CheckCircle2 /> : <X />}
                  <div>
                    <strong>
                      {answerResult.correct
                        ? t("course.lessonComplete")
                        : t("course.tryAgain")}
                    </strong>
                    <p>{answerResult.explanation}</p>
                  </div>
                </div>
              )}
              {!completed || !answerResult ? (
                <button
                  className="button button-primary"
                  disabled={!selectedChoice || busy}
                  onClick={() => onSubmit(questionIndex)}
                >
                  {t("course.checkAnswer")} <ArrowRight size={17} />
                </button>
              ) : null}
            </article>
          );
        })}
      </div>
      {completed && Object.keys(answerResults).length === 0 && (
        <div className="checkpoint-result correct">
          <CheckCircle2 />
          <strong>{t("course.alreadyComplete")}</strong>
        </div>
      )}
    </section>
  );
}

function videoEmbedUrl(url: string) {
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("youtube.com")) {
      const id = parsed.searchParams.get("v");
      return id ? `https://www.youtube.com/embed/${id}` : url;
    }
    if (parsed.hostname === "youtu.be") {
      return `https://www.youtube.com/embed/${parsed.pathname.slice(1)}`;
    }
  } catch {
    return url;
  }
  return url;
}

export default function LessonPage() {
  const params = useParams<{ id: string; lessonId: string }>();
  const { reloadUser } = useAuth();
  const { language, t } = useLanguage();
  const [lesson, setLesson] = useState<LessonDetail | null>(null);
  const [selectedChoices, setSelectedChoices] = useState<Record<number, string>>({});
  const [answerResults, setAnswerResults] = useState<Record<number, AnswerResult>>({});
  const [busy, setBusy] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setBusy(true);
    setError("");
    setAnswerResults({});
    setSelectedChoices({});
    api<LessonDetail>(
      `/courses/lessons/${params.lessonId}/?language=${language}`,
      { auth: true },
    )
      .then(setLesson)
      .catch((requestError) => setError(requestError.message))
      .finally(() => setBusy(false));
  }, [language, params.lessonId]);

  const navigation = useMemo(() => {
    if (!lesson) return { previous: null, next: null };
    const index = lesson.course_lessons.findIndex((item) => item.id === lesson.id);
    return {
      previous: index > 0 ? lesson.course_lessons[index - 1] : null,
      next:
        index >= 0 && index < lesson.course_lessons.length - 1
          ? lesson.course_lessons[index + 1]
          : null,
    };
  }, [lesson]);

  const modules = useMemo(() => {
    if (!lesson) return [];
    const grouped = new Map<string, typeof lesson.course_lessons>();
    for (const item of lesson.course_lessons) {
      const title = item.module_title || lesson.course_title;
      grouped.set(title, [...(grouped.get(title) || []), item]);
    }
    return Array.from(grouped.entries());
  }, [lesson]);

  const submitAnswer = async (questionIndex: number) => {
    if (!lesson || !selectedChoices[questionIndex]) return;
    setBusy(true);
    setError("");
    try {
      const result = await api<AnswerResult>(
        `/courses/lessons/${lesson.id}/answer/`,
        {
          method: "POST",
          auth: true,
          body: JSON.stringify({ choice_id: selectedChoices[questionIndex] }),
        },
      );
      setAnswerResults((current) => ({ ...current, [questionIndex]: result }));
      if (result.correct) {
        setLesson({
          ...lesson,
          completed: true,
          course_lessons: lesson.course_lessons.map((item) =>
            item.id === lesson.id ? { ...item, completed: true } : item,
          ),
        });
        await reloadUser();
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  if (busy && !lesson) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> {t("course.loading")}
        </div>
      </section>
    );
  }

  if (!lesson) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <h1>{t("course.notFound")}</h1>
          <p>{error}</p>
          <Link className="button button-primary" href={`/courses/${params.id}`}>
            {t("course.backToCourse")}
          </Link>
        </div>
      </section>
    );
  }

  const completedCount = lesson.course_lessons.filter(
    (item) => item.completed,
  ).length;
  const progress = Math.round(
    (completedCount * 100) / lesson.course_lessons.length,
  );
  const embedUrl = lesson.video_url ? videoEmbedUrl(lesson.video_url) : "";
  const isEmbed = embedUrl.includes("youtube.com/embed/");
  const structuredBlocks = lesson.blocks?.length ? lesson.blocks : [];
  const structuredTasks = lesson.tasks?.length ? lesson.tasks : [];
  const checkpointQuestions =
    lesson.questions && lesson.questions.length > 0
      ? lesson.questions
      : lesson.question
        ? [lesson.question]
        : [];
  const lessonSections = structuredBlocks.length ? [] : parseLessonContent(lesson.content);
  const theorySections = lessonSections.filter(
    (section) => section.type !== "practice",
  );
  const practiceSections = lessonSections.filter(
    (section) => section.type === "practice",
  );
  const keyTakeaways = lessonSections
    .find((section) => section.type === "risk")
    ?.items.slice(0, 3);
  const structuredKeyTakeaways = structuredBlocks
    .find((block) => block.type === "warning" || block.type === "checklist")
    ?.data?.items?.slice(0, 3)
    .map((item) => localizedDataText(item, language))
    .filter(Boolean);
  const ui = lessonUi[language];

  return (
    <section className="page-section lesson-page">
      <div className="container lesson-layout">
        <aside className="lesson-sidebar">
          <Link href={`/courses/${lesson.course_id}`} className="back-link">
            <ArrowLeft size={16} /> {t("course.backToCourse")}
          </Link>
          <h2>{lesson.course_title}</h2>
          <div className="lesson-sidebar-progress">
            <span>{t("course.moduleProgress")}</span>
            <strong>{progress}%</strong>
            <div className="progress-track compact-progress">
              <span style={{ width: `${progress}%` }} />
            </div>
          </div>
          <strong className="lesson-sidebar-title">
            <ListChecks size={17} /> {t("course.contents")}
          </strong>
          <nav>
            {modules.map(([moduleTitle, items]) => (
              <div className="lesson-module" key={moduleTitle}>
                <h3>{moduleTitle}</h3>
                {items.map((item) => (
                  <Link
                    key={item.id}
                    href={`/courses/${lesson.course_id}/lessons/${item.id}`}
                    className={`${item.id === lesson.id ? "active" : ""} ${
                      item.completed ? "completed" : ""
                    }`}
                  >
                    <span>
                      {item.completed ? <Check size={15} /> : item.order}
                    </span>
                    <div>
                      <strong>{item.title}</strong>
                      <small>
                        <Clock3 size={12} /> {item.duration_minutes}{" "}
                        {t("course.minuteShort")}
                      </small>
                    </div>
                  </Link>
                ))}
              </div>
            ))}
          </nav>
        </aside>

        <main className="lesson-main">
          <div className="lesson-page-head">
            <span className="eyebrow">
              {t("course.lesson", { number: lesson.order })}
            </span>
            <h1>{lesson.title}</h1>
            <p>{lesson.summary}</p>
            <div className="lesson-head-stats">
              <span>
                <Clock3 size={16} /> {lesson.duration_minutes}{" "}
                {t("course.minuteShort")}
              </span>
              <span>
                <ListChecks size={16} /> {lesson.course_lessons.length}{" "}
                {t("courses.lessons")}
              </span>
              <span>
                <ShieldCheck size={16} /> {ui.theoryPlus}
              </span>
            </div>
          </div>

          <section className="lesson-learning-card">
            <div>
              <span className="eyebrow">{ui.learningEyebrow}</span>
              <h2>{ui.learningTitle}</h2>
            </div>
            <div className="lesson-learning-grid">
              <article>
                <Target />
                <strong>{ui.recognizeTitle}</strong>
                <p>{ui.recognizeText}</p>
              </article>
              <article>
                <ShieldCheck />
                <strong>{ui.safeStepTitle}</strong>
                <p>{ui.safeStepText}</p>
              </article>
              <article>
                <ClipboardList />
                <strong>{ui.selfCheckTitle}</strong>
                <p>{ui.selfCheckText}</p>
              </article>
            </div>
          </section>

          {lesson.video_url && (
            <section className="lesson-video-section">
              <h2>
                <PlayCircle size={21} /> {t("course.video")}
              </h2>
              {isEmbed ? (
                <iframe
                  src={embedUrl}
                  title={lesson.title}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : (
                <video controls src={lesson.video_url} />
              )}
            </section>
          )}

          <article className="lesson-article">
            <h2>{t("course.reading")}</h2>
            <div className="lesson-article-lead">
              {ui.readingLead}
            </div>
            <div className="lesson-section-stack">
              {structuredBlocks.length > 0
                ? structuredBlocks
                    .filter((block) => block.type !== "task" && block.type !== "quiz")
                    .map((block) => (
                      <LessonBlockCard
                        block={block}
                        key={block.id}
                        language={language}
                      />
                    ))
                : theorySections.map((section, index) => (
                    <LessonSectionCard
                      key={`${section.title}-${index}`}
                      section={section}
                    />
                  ))}
            </div>
          </article>

          {((structuredKeyTakeaways && structuredKeyTakeaways.length > 0) ||
            (keyTakeaways && keyTakeaways.length > 0)) && (
            <section className="lesson-risk-strip">
              <strong>
                <AlertTriangle size={18} /> {ui.riskSigns}
              </strong>
              <div>
                {(structuredKeyTakeaways || keyTakeaways || []).map((item) => (
                  <span key={item}>{item}</span>
                ))}
              </div>
            </section>
          )}

          {(structuredTasks.length > 0 || practiceSections.length > 0) && (
            <section className="lesson-practice-block">
              <span className="eyebrow">{ui.practiceEyebrow}</span>
              <h2>{ui.practiceTitle}</h2>
              <p>{ui.practiceText}</p>
              <div className="lesson-section-stack">
                {structuredTasks.length > 0
                  ? structuredTasks.map((task, index) => (
                      <StructuredTaskCard
                        index={index}
                        key={task.id}
                        language={language}
                        task={task}
                      />
                    ))
                  : practiceSections.map((section, index) => (
                      <LessonSectionCard
                        key={`${section.title}-${index}`}
                        section={section}
                      />
                    ))}
              </div>
            </section>
          )}

          <LessonQuestionsCheckpoint
            answerResults={answerResults}
            busy={busy}
            completed={lesson.completed}
            onSelect={(questionIndex, choiceId) => {
              setSelectedChoices((current) => ({
                ...current,
                [questionIndex]: choiceId,
              }));
              setAnswerResults((current) => {
                const next = { ...current };
                delete next[questionIndex];
                return next;
              });
            }}
            onSubmit={submitAnswer}
            questions={checkpointQuestions}
            selectedChoices={selectedChoices}
            t={t}
            language={language}
          />

          <div className="lesson-page-navigation">
            {navigation.previous ? (
              <Link
                className="button button-ghost"
                href={`/courses/${lesson.course_id}/lessons/${navigation.previous.id}`}
              >
                <ArrowLeft size={17} /> {t("course.previousLesson")}
              </Link>
            ) : (
              <span />
            )}
            {navigation.next && (
              <Link
                className="button button-primary"
                href={`/courses/${lesson.course_id}/lessons/${navigation.next.id}`}
              >
                {t("course.nextLesson")} <ArrowRight size={17} />
              </Link>
            )}
          </div>
        </main>
      </div>
    </section>
  );
}
