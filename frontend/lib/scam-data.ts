import { Language } from "@/lib/translations";

export const scamTypes = [
  { value: "bank_call", ru: "Лжесотрудник банка", uz: "Soxta bank xodimi" },
  { value: "sms_code", ru: "Кража SMS-кода", uz: "SMS kodini o‘g‘irlash" },
  {
    value: "malware",
    ru: "Вредоносное приложение или APK",
    uz: "Zararli ilova yoki APK",
  },
  {
    value: "marketplace",
    ru: "Мошенничество на торговой площадке",
    uz: "Savdo maydonchasidagi firibgarlik",
  },
  {
    value: "prize",
    ru: "Ложный выигрыш или компенсация",
    uz: "Soxta yutuq yoki kompensatsiya",
  },
  { value: "relative", ru: "Лжеродственник", uz: "Soxta qarindosh" },
  {
    value: "romance",
    ru: "Романтическое мошенничество",
    uz: "Romantik firibgarlik",
  },
  { value: "investment", ru: "Лжеинвестиции", uz: "Soxta investitsiya" },
  { value: "other", ru: "Другая схема", uz: "Boshqa sxema" },
] as const;

export const scamLabels = Object.fromEntries(
  scamTypes.map((item) => [item.value, item.ru]),
) as Record<string, string>;

export const regions = [
  { value: "tashkent_city", ru: "город Ташкент", uz: "Toshkent shahri" },
  {
    value: "karakalpakstan",
    ru: "Республика Каракалпакстан",
    uz: "Qoraqalpog‘iston Respublikasi",
  },
  { value: "andijan", ru: "Андижанская область", uz: "Andijon viloyati" },
  { value: "bukhara", ru: "Бухарская область", uz: "Buxoro viloyati" },
  { value: "jizzakh", ru: "Джизакская область", uz: "Jizzax viloyati" },
  {
    value: "kashkadarya",
    ru: "Кашкадарьинская область",
    uz: "Qashqadaryo viloyati",
  },
  { value: "navoi", ru: "Навоийская область", uz: "Navoiy viloyati" },
  { value: "namangan", ru: "Наманганская область", uz: "Namangan viloyati" },
  {
    value: "samarkand",
    ru: "Самаркандская область",
    uz: "Samarqand viloyati",
  },
  {
    value: "surkhandarya",
    ru: "Сурхандарьинская область",
    uz: "Surxondaryo viloyati",
  },
  { value: "syrdarya", ru: "Сырдарьинская область", uz: "Sirdaryo viloyati" },
  {
    value: "tashkent_region",
    ru: "Ташкентская область",
    uz: "Toshkent viloyati",
  },
  { value: "fergana", ru: "Ферганская область", uz: "Farg‘ona viloyati" },
  { value: "khorezm", ru: "Хорезмская область", uz: "Xorazm viloyati" },
] as const;

export const getScamTypes = (language: Language) =>
  scamTypes.map((item) => ({ value: item.value, label: item[language] }));

export const getRegions = (language: Language) =>
  regions.map((item) => ({ value: item.value, label: item[language] }));

export const getScamLabel = (value: string, language: Language) =>
  scamTypes.find((item) => item.value === value)?.[language] || value;
