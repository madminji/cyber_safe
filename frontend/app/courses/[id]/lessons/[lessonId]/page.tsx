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
    almost: "Не совсем.",
    correctOption: "Правильный вариант",
    question: "Вопрос",
    riskExists: "Риск есть",
    safe: "Безопасно",
    completed: "Выполнено",
    solved: "Решено",
    selected: "Выбрано",
    sorted: "Распределено",
    ruleInstruction: "Сформулируйте свои правила коротко и конкретно.",
    ruleLabel: "Правило",
    ruleExample: "Например: не называю SMS-коды",
    rulePlaceholder: "Введите своё правило",
    rulesSuccess: "Отлично. Эти правила можно использовать как личную памятку.",
    scenarioInstruction: "Выберите безопасное действие в каждом кейсе.",
    checklistInstruction: "Отметьте, что вы готовы проверить после урока.",
    numberInstruction: "Сопоставьте статус номера с безопасным действием.",
    incidentInstruction: "Выберите ситуацию и получите чек-лист первых действий.",
    done: "Готово",
    markDone: "Отметить как выполненное",
    reportPlaceholder:
      "Кратко опишите факты: дата, канал связи, что просили сделать, сумма ущерба, какие доказательства есть.",
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
    almost: "Uncha emas.",
    correctOption: "To‘g‘ri variant",
    question: "Savol",
    riskExists: "Xavf bor",
    safe: "Xavfsiz",
    completed: "Bajarildi",
    solved: "Yechildi",
    selected: "Tanlandi",
    sorted: "Taqsimlandi",
    ruleInstruction: "Qoidalaringizni qisqa va aniq yozing.",
    ruleLabel: "Qoida",
    ruleExample: "Masalan: SMS-kodlarni aytmayman",
    rulePlaceholder: "Qoidangizni kiriting",
    rulesSuccess: "Ajoyib. Bu qoidalardan shaxsiy eslatma sifatida foydalanishingiz mumkin.",
    scenarioInstruction: "Har bir vaziyatda xavfsiz harakatni tanlang.",
    checklistInstruction: "Darsdan keyin nimalarni tekshirishga tayyor ekaningizni belgilang.",
    numberInstruction: "Raqam holatini xavfsiz harakat bilan moslang.",
    incidentInstruction: "Vaziyatni tanlang va birinchi harakatlar ro‘yxatini oling.",
    done: "Tayyor",
    markDone: "Bajarildi deb belgilash",
    reportPlaceholder:
      "Faktlarni qisqa yozing: sana, aloqa kanali, nima so‘raldi, zarar miqdori, qanday dalillar bor.",
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

type LocalizedText = Record<"ru" | "uz", string>;

type LocalizedRiskCard = {
  text: LocalizedText;
  risky: boolean;
  reason: LocalizedText;
};

type LocalizedDataCard = {
  text: LocalizedText;
  zone: string;
};

type LocalizedZone = {
  id: string;
  label: LocalizedText;
};

type LocalizedScenario = {
  text: LocalizedText;
  options: Array<{ text: LocalizedText; safe: boolean }>;
  reason: LocalizedText;
};

type LocalizedNumberCard = {
  status: LocalizedText;
  action: LocalizedText;
  reason: LocalizedText;
};

function lt(value: LocalizedText, language: "ru" | "uz") {
  return value[language];
}

const riskTrainingCards: LocalizedRiskCard[] = [
  {
    text: {
      ru: "Ваша карта заблокирована. Срочно подтвердите данные по ссылке.",
      uz: "Kartangiz bloklandi. Ma’lumotlarni havola orqali zudlik bilan tasdiqlang.",
    },
    risky: true,
    reason: {
      ru: "Есть срочность, угроза блокировки и ссылка для ввода данных.",
      uz: "Shoshirish, bloklash tahdidi va ma’lumot kiritish uchun havola bor.",
    },
  },
  {
    text: {
      ru: "Вы выиграли 1 000 000 сум. Отправьте фото паспорта для получения приза.",
      uz: "Siz 1 000 000 so‘m yutdingiz. Sovrinni olish uchun pasport rasmini yuboring.",
    },
    risky: true,
    reason: {
      ru: "Обещание выигрыша и просьба отправить документ — высокий риск.",
      uz: "Yutuq va hujjat yuborish talabi — yuqori xavf belgisi.",
    },
  },
  {
    text: {
      ru: "Ваш заказ доставлен. Проверьте трек-номер в официальном приложении.",
      uz: "Buyurtmangiz yetkazildi. Trek raqamini rasmiy ilovada tekshiring.",
    },
    risky: false,
    reason: {
      ru: "Безопаснее открывать трек внутри официального приложения.",
      uz: "Trekni rasmiy ilova ichida ochish xavfsizroq.",
    },
  },
  {
    text: {
      ru: "Служба безопасности банка просит назвать SMS-код для отмены перевода.",
      uz: "Bank xavfsizlik xizmati o‘tkazmani bekor qilish uchun SMS-kodni so‘ramoqda.",
    },
    risky: true,
    reason: {
      ru: "SMS-код нельзя передавать никому, даже сотруднику банка.",
      uz: "SMS-kodni hech kimga, hatto bank xodimiga ham aytib bo‘lmaydi.",
    },
  },
  {
    text: {
      ru: "Напоминание: обновите приложение через официальный магазин приложений.",
      uz: "Eslatma: ilovani rasmiy ilovalar do‘koni orqali yangilang.",
    },
    risky: false,
    reason: {
      ru: "Официальный магазин — нормальный и безопасный канал обновления.",
      uz: "Rasmiy do‘kon — yangilash uchun odatiy va xavfsiz kanal.",
    },
  },
];

const dataSortingCards: LocalizedDataCard[] = [
  { text: { ru: "Имя и город", uz: "Ism va shahar" }, zone: "public" },
  { text: { ru: "Номер телефона", uz: "Telefon raqami" }, zone: "trusted" },
  { text: { ru: "Фото паспорта", uz: "Pasport rasmi" }, zone: "trusted" },
  { text: { ru: "SMS-код", uz: "SMS-kod" }, zone: "secret" },
  { text: { ru: "CVV-код карты", uz: "Karta CVV-kodi" }, zone: "secret" },
  { text: { ru: "Пароль от почты", uz: "Elektron pochta paroli" }, zone: "secret" },
];

const dataZones: LocalizedZone[] = [
  { id: "public", label: { ru: "Можно указывать публично", uz: "Ommaviy ko‘rsatish mumkin" } },
  { id: "trusted", label: { ru: "Только проверенным сервисам", uz: "Faqat ishonchli servislarga" } },
  { id: "secret", label: { ru: "Никому не передавать", uz: "Hech kimga bermaslik" } },
];

const scenarioChoices: LocalizedScenario[] = [
  {
    text: {
      ru: "В сообщении обещают выплату и просят перейти по короткой ссылке.",
      uz: "Xabarda to‘lov va’da qilinib, qisqa havolaga o‘tish so‘ralgan.",
    },
    options: [
      { text: { ru: "Перейти и проверить", uz: "O‘tib tekshirish" }, safe: false },
      { text: { ru: "Открыть официальный сайт вручную", uz: "Rasmiy saytni qo‘lda ochish" }, safe: true },
      { text: { ru: "Отправить ссылку друзьям", uz: "Havolani do‘stlarga yuborish" }, safe: false },
    ],
    reason: {
      ru: "Безопаснее открыть официальный сайт вручную и не использовать ссылку из сообщения.",
      uz: "Rasmiy saytni qo‘lda ochish va xabardagi havoladan foydalanmaslik xavfsizroq.",
    },
  },
  {
    text: {
      ru: "Звонящий говорит, что он из банка, и просит назвать SMS-код.",
      uz: "Qo‘ng‘iroq qilgan odam bankdan ekanini aytib, SMS-kodni so‘rayapti.",
    },
    options: [
      { text: { ru: "Назвать код", uz: "Kodni aytish" }, safe: false },
      { text: { ru: "Попросить перезвонить", uz: "Qayta qo‘ng‘iroq qilishni so‘rash" }, safe: false },
      { text: { ru: "Завершить разговор и позвонить в банк самому", uz: "Suhbatni tugatib, bankka o‘zingiz qo‘ng‘iroq qilish" }, safe: true },
    ],
    reason: {
      ru: "Код подтверждения нельзя сообщать никому. Связывайтесь с банком самостоятельно.",
      uz: "Tasdiqlash kodini hech kimga aytmang. Bank bilan mustaqil bog‘laning.",
    },
  },
  {
    text: {
      ru: "В Telegram прислали APK «для получения бонуса».",
      uz: "Telegramda “bonus olish uchun” APK yuborishdi.",
    },
    options: [
      { text: { ru: "Установить APK", uz: "APKni o‘rnatish" }, safe: false },
      { text: { ru: "Проверить приложение в официальном магазине", uz: "Ilovani rasmiy do‘konda tekshirish" }, safe: true },
      { text: { ru: "Отключить защиту телефона", uz: "Telefon himoyasini o‘chirish" }, safe: false },
    ],
    reason: {
      ru: "Приложения безопаснее устанавливать только из официального магазина или официального сайта.",
      uz: "Ilovalarni faqat rasmiy do‘kon yoki rasmiy saytdan o‘rnatish xavfsizroq.",
    },
  },
];

const homeChecklistItems: LocalizedText[] = [
  { ru: "Проверить активные сеансы Telegram", uz: "Telegramdagi faol seanslarni tekshirish" },
  { ru: "Включить двухфакторную защиту на почте", uz: "Pochtada ikki bosqichli himoyani yoqish" },
  { ru: "Проверить, кто видит номер телефона в мессенджере", uz: "Messengerda telefon raqamini kim ko‘rishini tekshirish" },
  { ru: "Удалить неизвестные приложения", uz: "Noma’lum ilovalarni o‘chirish" },
];

const numberPracticeCards: LocalizedNumberCard[] = [
  {
    status: { ru: "Не найден", uz: "Topilmadi" },
    action: { ru: "Не считать номер безопасным автоматически", uz: "Raqamni avtomatik xavfsiz deb hisoblamaslik" },
    reason: { ru: "Отсутствие жалоб не доказывает безопасность номера.", uz: "Shikoyatlar yo‘qligi raqam xavfsizligini isbotlamaydi." },
  },
  {
    status: { ru: "Подозрительно", uz: "Shubhali" },
    action: { ru: "Не отвечать и сохранить доказательства", uz: "Javob bermaslik va dalillarni saqlash" },
    reason: { ru: "Есть признаки риска, лучше не продолжать разговор.", uz: "Xavf belgilari bor, suhbatni davom ettirmagan ma’qul." },
  },
  {
    status: { ru: "Опасно", uz: "Xavfli" },
    action: { ru: "Заблокировать номер и отправить репорт", uz: "Raqamni bloklash va xabar yuborish" },
    reason: { ru: "Подтверждённый риск нужно зафиксировать для модерации.", uz: "Tasdiqlangan xavfni moderatsiya uchun qayd etish kerak." },
  },
];

const incidentChecklists: Record<string, { label: LocalizedText; steps: LocalizedText[] }> = {
  code: {
    label: { ru: "Назвал код", uz: "Kodni aytdim" },
    steps: [
      { ru: "Сразу заблокировать карту или аккаунт", uz: "Darhol karta yoki akkauntni bloklash" },
      { ru: "Сменить пароль", uz: "Parolni almashtirish" },
      { ru: "Отключить чужие сеансы", uz: "Begona seanslarni o‘chirish" },
      { ru: "Сообщить в банк или поддержку", uz: "Bank yoki qo‘llab-quvvatlash xizmatiga xabar berish" },
    ],
  },
  apk: {
    label: { ru: "Установил APK", uz: "APK o‘rnatdim" },
    steps: [
      { ru: "Удалить приложение", uz: "Ilovani o‘chirish" },
      { ru: "Отключить интернет при подозрительной активности", uz: "Shubhali faollikda internetni o‘chirish" },
      { ru: "Проверить разрешения приложений", uz: "Ilova ruxsatlarini tekshirish" },
      { ru: "Сменить пароли с другого устройства", uz: "Parollarni boshqa qurilmadan almashtirish" },
    ],
  },
  passport: {
    label: { ru: "Отправил паспорт", uz: "Pasport yubordim" },
    steps: [
      { ru: "Сохранить переписку", uz: "Yozishmani saqlash" },
      { ru: "Сообщить в сервис или банк", uz: "Servis yoki bankka xabar berish" },
      { ru: "Следить за заявками на займы", uz: "Kredit arizalarini kuzatish" },
      { ru: "Подготовить обращение в органы", uz: "Tegishli organlarga murojaat tayyorlash" },
    ],
  },
  money: {
    label: { ru: "Перевёл деньги", uz: "Pul o‘tkazdim" },
    steps: [
      { ru: "Связаться с банком немедленно", uz: "Darhol bank bilan bog‘lanish" },
      { ru: "Сохранить чек и переписку", uz: "Chek va yozishmani saqlash" },
      { ru: "Подать заявление", uz: "Ariza berish" },
      { ru: "Сообщить номер или аккаунт в базу", uz: "Raqam yoki akkauntni bazaga xabar qilish" },
    ],
  },
};
function PracticeTaskCard({ item, index, language }: { item: string; index: number; language: "ru" | "uz" }) {
  const [riskAnswers, setRiskAnswers] = useState<Record<number, boolean>>({});
  const [rules, setRules] = useState(["", "", "", "", ""]);
  const [zones, setZones] = useState<Record<string, string>>({});
  const [scenarioAnswers, setScenarioAnswers] = useState<Record<number, number>>({});
  const [checkedItems, setCheckedItems] = useState<Record<string, boolean>>({});
  const [selectedIncident, setSelectedIncident] = useState("code");
  const [reportDraft, setReportDraft] = useState("");
  const [done, setDone] = useState(false);
  const ui = lessonUi[language];
  const [title, ...descriptionParts] = item.split(". ");
  const description = descriptionParts.join(". ") || item;
  const lower = item.toLowerCase();
  const taskTitle = title || `${ui.taskFallback} ${index + 1}`;
  const isRiskCards =
    lower.includes("сообщени") ||
    lower.includes("xabar") ||
    lower.includes("карточ") ||
    lower.includes("karta");
  const isRules =
    lower.includes("правил") ||
    lower.includes("qoid") ||
    lower.includes("карточку безопасности");
  const isSorting =
    lower.includes("распредел") ||
    lower.includes("taqsim") ||
    lower.includes("зон") ||
    lower.includes("zona");
  const isScenario =
    lower.includes("кейс") ||
    lower.includes("case") ||
    lower.includes("безопасное действие") ||
    lower.includes("xavfsiz harakat");
  const isHomeChecklist =
    lower.includes("домаш") ||
    lower.includes("real") ||
    lower.includes("tekshir");
  const isNumberPractice =
    lower.includes("номер") ||
    lower.includes("raqam") ||
    lower.includes("репорт") ||
    lower.includes("report");
  const isIncidentPractice =
    lower.includes("назвал код") ||
    lower.includes("kod") ||
    lower.includes("чек-лист") ||
    lower.includes("checklist");

  if (isRiskCards) {
    const answeredCount = Object.keys(riskAnswers).length;
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{taskTitle}</strong>
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
                key={lt(card.text, language)}
              >
                <p>{lt(card.text, language)}</p>
                <div>
                  <button onClick={() => setRiskAnswers({ ...riskAnswers, [cardIndex]: true })}>
                    {ui.riskExists}
                  </button>
                  <button onClick={() => setRiskAnswers({ ...riskAnswers, [cardIndex]: false })}>
                    {ui.safe}
                  </button>
                </div>
                {answered && (
                  <small>
                    {correct ? `${ui.correct} ` : `${ui.almost} `}
                    {lt(card.reason, language)}
                  </small>
                )}
              </div>
            );
          })}
        </div>
        <div className="practice-score-line">
          {ui.completed}: {answeredCount}/{riskTrainingCards.length}
        </div>
      </article>
    );
  }

  if (isRules) {
    const ruleCount = lower.includes("10") || lower.includes("карточку") ? 5 : 3;
    const visibleRules = rules.slice(0, ruleCount);
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{taskTitle}</strong>
            <p>{ui.ruleInstruction}</p>
          </div>
        </div>
        <div className="practice-rule-list">
          {visibleRules.map((rule, ruleIndex) => (
            <label key={ruleIndex}>
              {ui.ruleLabel} {ruleIndex + 1}
              <input
                value={rule}
                onChange={(event) => {
                  const nextRules = [...rules];
                  nextRules[ruleIndex] = event.target.value;
                  setRules(nextRules);
                }}
                placeholder={ruleIndex === 0 ? ui.ruleExample : ui.rulePlaceholder}
              />
            </label>
          ))}
        </div>
        {visibleRules.filter(Boolean).length === ruleCount && (
          <div className="practice-score-line success">{ui.rulesSuccess}</div>
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
            <strong>{taskTitle}</strong>
            <p>{ui.scenarioInstruction}</p>
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
                key={lt(scenario.text, language)}
              >
                <p>{lt(scenario.text, language)}</p>
                <div>
                  {scenario.options.map((option, optionIndex) => (
                    <button
                      key={lt(option.text, language)}
                      onClick={() =>
                        setScenarioAnswers({
                          ...scenarioAnswers,
                          [scenarioIndex]: optionIndex,
                        })
                      }
                    >
                      {lt(option.text, language)}
                    </button>
                  ))}
                </div>
                {answered && (
                  <small>
                    {correct ? `${ui.correct} ` : `${ui.almost} `}
                    {lt(scenario.reason, language)}
                  </small>
                )}
              </div>
            );
          })}
        </div>
        <div className="practice-score-line">
          {ui.solved}: {answeredCount}/{scenarioChoices.length}
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
            <strong>{taskTitle}</strong>
            <p>{ui.checklistInstruction}</p>
          </div>
        </div>
        <div className="practice-checklist">
          {homeChecklistItems.map((checkItem) => {
            const text = lt(checkItem, language);
            return (
              <label key={text}>
                <input
                  type="checkbox"
                  checked={Boolean(checkedItems[text])}
                  onChange={(event) =>
                    setCheckedItems({
                      ...checkedItems,
                      [text]: event.target.checked,
                    })
                  }
                />
                {text}
              </label>
            );
          })}
        </div>
        <div className={checkedCount ? "practice-score-line success" : "practice-score-line"}>
          {ui.selected}: {checkedCount}/{homeChecklistItems.length}
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
            <strong>{taskTitle}</strong>
            <p>{ui.numberInstruction}</p>
          </div>
        </div>
        <div className="practice-sort-list">
          {numberPracticeCards.map((card) => (
            <div className="correct" key={lt(card.status, language)}>
              <strong>{lt(card.status, language)}</strong>
              <p>{lt(card.action, language)}</p>
              <small>{lt(card.reason, language)}</small>
            </div>
          ))}
        </div>
      </article>
    );
  }

  if (isIncidentPractice) {
    const selectedChecklist = incidentChecklists[selectedIncident] || incidentChecklists.code;
    return (
      <article className="practice-interactive-card">
        <div className="practice-task-head">
          <CheckCircle2 size={20} />
          <div>
            <strong>{taskTitle}</strong>
            <p>{ui.incidentInstruction}</p>
          </div>
        </div>
        <div className="practice-incident-tabs">
          {Object.entries(incidentChecklists).map(([incident, config]) => (
            <button
              className={selectedIncident === incident ? "selected" : ""}
              key={incident}
              onClick={() => setSelectedIncident(incident)}
            >
              {lt(config.label, language)}
            </button>
          ))}
        </div>
        <ol className="practice-incident-list">
          {selectedChecklist.steps.map((step) => (
            <li key={lt(step, language)}>{lt(step, language)}</li>
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
            <strong>{taskTitle}</strong>
            <p>{description}</p>
          </div>
        </div>
        <div className="practice-sort-list">
          {dataSortingCards.map((card) => {
            const cardText = lt(card.text, language);
            const selectedZone = zones[cardText];
            const answered = Boolean(selectedZone);
            const correct = selectedZone === card.zone;
            return (
              <div className={answered ? (correct ? "correct" : "wrong") : ""} key={cardText}>
                <strong>{cardText}</strong>
                <div>
                  {dataZones.map((zone) => (
                    <button
                      className={selectedZone === zone.id ? "selected" : ""}
                      key={zone.id}
                      onClick={() => setZones({ ...zones, [cardText]: zone.id })}
                    >
                      {lt(zone.label, language)}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
        <div className="practice-score-line">
          {ui.sorted}: {completedCount}/{dataSortingCards.length}
        </div>
      </article>
    );
  }

  return (
    <article className="practice-interactive-card">
      <div className="practice-task-head">
        <CheckCircle2 size={20} />
        <div>
          <strong>{taskTitle}</strong>
          <p>{description}</p>
        </div>
      </div>
      <button
        className={done ? "practice-done-button done" : "practice-done-button"}
        onClick={() => setDone(!done)}
      >
        {done ? ui.done : ui.markDone}
      </button>
      {(lower.includes("шаблон обращения") ||
        lower.includes("корректный репорт") ||
        lower.includes("murojaat") ||
        lower.includes("report")) && (
        <textarea
          className="practice-draft-field"
          value={reportDraft}
          onChange={(event) => setReportDraft(event.target.value)}
          placeholder={ui.reportPlaceholder}
        />
      )}
    </article>
  );
}
function LessonSectionCard({
  section,
  language,
}: {
  section: LessonSection;
  language: "ru" | "uz";
}) {
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
            <PracticeTaskCard item={item} index={index} key={item} language={language} />
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
            {ui.rulesSuccess}
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
                      language={language}
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
                        language={language}
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
