export const scamTypes = [
  { value: "bank_call", label: "Лжесотрудник банка" },
  { value: "sms_code", label: "Кража SMS-кода" },
  { value: "malware", label: "Вредоносное приложение или APK" },
  { value: "marketplace", label: "Мошенничество на торговой площадке" },
  { value: "prize", label: "Ложный выигрыш или компенсация" },
  { value: "relative", label: "Лжеродственник" },
  { value: "romance", label: "Романтическое мошенничество" },
  { value: "investment", label: "Лжеинвестиции" },
  { value: "other", label: "Другая схема" },
] as const;

export const scamLabels = Object.fromEntries(
  scamTypes.map((item) => [item.value, item.label]),
) as Record<string, string>;

export const regions = [
  { value: "tashkent_city", label: "город Ташкент" },
  { value: "karakalpakstan", label: "Республика Каракалпакстан" },
  { value: "andijan", label: "Андижанская область" },
  { value: "bukhara", label: "Бухарская область" },
  { value: "jizzakh", label: "Джизакская область" },
  { value: "kashkadarya", label: "Кашкадарьинская область" },
  { value: "navoi", label: "Навоийская область" },
  { value: "namangan", label: "Наманганская область" },
  { value: "samarkand", label: "Самаркандская область" },
  { value: "surkhandarya", label: "Сурхандарьинская область" },
  { value: "syrdarya", label: "Сырдарьинская область" },
  { value: "tashkent_region", label: "Ташкентская область" },
  { value: "fergana", label: "Ферганская область" },
  { value: "khorezm", label: "Хорезмская область" },
] as const;

