"use client";

import {
  AlertTriangle,
  BadgeCheck,
  Check,
  CheckCircle2,
  Clock3,
  FileSearch,
  Gavel,
  ListFilter,
  UploadCloud,
  BookOpenText,
  RefreshCw,
  ShieldAlert,
  Download,
  Trash2,
  ExternalLink,
  Save,
  X,
  XCircle,
  Users,
} from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { StatusPill } from "@/components/status-pill";
import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";
import { api } from "@/lib/api";
import { getRegions, getScamLabel } from "@/lib/scam-data";
import {
  AdminCourseContent,
  AdminLesson,
  AdminUser,
  ModerationNumber,
  ModerationReport,
  ModerationSummary,
} from "@/lib/types";

type Filter = "pending" | "approved" | "rejected";
type NumberFilter = "suspicious" | "scammer" | "verified_scammer" | "reported";
type ModerationTab = "reports" | "lessons" | "users";
type ReportPanel = "reports" | "numbers";
type UserRoleFilter = "all" | "citizen" | "moderator" | "admin";

type LessonImportResult = {
  status: "created" | "updated";
  lesson_id: string;
  lesson_slug: string;
  course_id: string;
  blocks_count: number;
  tasks_count: number;
  questions_count: number;
};

const moderationLocalText = {
  ru: {
    tabReports: "\u0417\u0430\u044f\u0432\u043a\u0438",
    tabLessons: "\u0423\u0440\u043e\u043a\u0438",
    tabUsers: "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438",
    citizenReports: "\u0417\u0430\u044f\u0432\u043a\u0438 \u0433\u0440\u0430\u0436\u0434\u0430\u043d",
    numberRegistry: "\u0420\u0435\u0435\u0441\u0442\u0440 \u043d\u043e\u043c\u0435\u0440\u043e\u0432",
    contentManagement: "\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043a\u043e\u043d\u0442\u0435\u043d\u0442\u043e\u043c",
    lessonImport: "\u0418\u043c\u043f\u043e\u0440\u0442 JSON-\u0443\u0440\u043e\u043a\u0430",
    lessonImportText:
      "\u0417\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u0435 \u043e\u0434\u0438\u043d JSON-\u0444\u0430\u0439\u043b \u0443\u0440\u043e\u043a\u0430 \u0432 \u0443\u043d\u0438\u0444\u0438\u0446\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e\u043c \u0444\u043e\u0440\u043c\u0430\u0442\u0435. \u041f\u043e\u0432\u0442\u043e\u0440\u043d\u0430\u044f \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0430 \u043e\u0431\u043d\u043e\u0432\u0438\u0442 \u0443\u0440\u043e\u043a \u0431\u0435\u0437 \u0434\u0443\u0431\u043b\u0435\u0439.",
    lessonJsonFile: "JSON-\u0444\u0430\u0439\u043b \u0443\u0440\u043e\u043a\u0430",
    chooseLessonJson: "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 JSON-\u0444\u0430\u0439\u043b \u0443\u0440\u043e\u043a\u0430.",
    importing: "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c...",
    importLesson: "\u0418\u043c\u043f\u043e\u0440\u0442\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0443\u0440\u043e\u043a",
    selectedFile: "\u0412\u044b\u0431\u0440\u0430\u043d \u0444\u0430\u0439\u043b:",
    lessonCreated: "\u0423\u0440\u043e\u043a \u0441\u043e\u0437\u0434\u0430\u043d",
    lessonUpdated: "\u0423\u0440\u043e\u043a \u043e\u0431\u043d\u043e\u0432\u043b\u0451\u043d",
    blocks: "\u0431\u043b\u043e\u043a\u043e\u0432",
    tasks: "\u0437\u0430\u0434\u0430\u043d\u0438\u0439",
    questions: "\u0432\u043e\u043f\u0440\u043e\u0441\u043e\u0432",
    coursesLessons: "\u041a\u0443\u0440\u0441\u044b \u0438 \u0443\u0440\u043e\u043a\u0438",
    contentManagerText: "\u041f\u0440\u043e\u0441\u043c\u043e\u0442\u0440, \u0441\u043a\u0430\u0447\u0438\u0432\u0430\u043d\u0438\u0435 JSON \u0438 \u0443\u0434\u0430\u043b\u0435\u043d\u0438\u0435 \u0443\u0440\u043e\u043a\u043e\u0432.",
    loadingCourses: "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c \u043a\u0443\u0440\u0441\u044b...",
    noCourses: "\u041a\u0443\u0440\u0441\u044b \u043f\u043e\u043a\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b.",
    lessons: "\u0443\u0440\u043e\u043a\u043e\u0432",
    published: "\u043e\u043f\u0443\u0431\u043b\u0438\u043a\u043e\u0432\u0430\u043d",
    hidden: "\u0441\u043a\u0440\u044b\u0442",
    noModule: "\u0411\u0435\u0437 \u043c\u043e\u0434\u0443\u043b\u044f",
    open: "\u041e\u0442\u043a\u0440\u044b\u0442\u044c",
    delete: "\u0423\u0434\u0430\u043b\u0438\u0442\u044c",
    deleteLessonConfirm: "\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0443\u0440\u043e\u043a \"{title}\"? \u042d\u0442\u043e \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043d\u0435\u043b\u044c\u0437\u044f \u043e\u0442\u043c\u0435\u043d\u0438\u0442\u044c.",
    userManagement: "\u0423\u043f\u0440\u0430\u0432\u043b\u0435\u043d\u0438\u0435 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f\u043c\u0438",
    platformUsers: "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 \u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c\u044b",
    userManagementText:
      "\u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u043c\u043e\u0436\u0435\u0442 \u043c\u0435\u043d\u044f\u0442\u044c \u0440\u043e\u043b\u044c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f, \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u0430 \u0438 \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0431\u0430\u043b\u043b\u043e\u0432. \u0421\u0432\u043e\u0439 \u0430\u043a\u043a\u0430\u0443\u043d\u0442 \u043d\u0435\u043b\u044c\u0437\u044f \u043f\u043e\u043d\u0438\u0437\u0438\u0442\u044c \u0438\u043b\u0438 \u043e\u0442\u043a\u043b\u044e\u0447\u0438\u0442\u044c.",
    searchByName: "\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u0438\u043c\u0435\u043d\u0438",
    allRoles: "\u0412\u0441\u0435 \u0440\u043e\u043b\u0438",
    citizens: "\u0413\u0440\u0430\u0436\u0434\u0430\u043d\u0435",
    moderators: "\u041c\u043e\u0434\u0435\u0440\u0430\u0442\u043e\u0440\u044b",
    admins: "\u0410\u0434\u043c\u0438\u043d\u044b",
    loadingUsers: "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439...",
    noUsers: "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u044b.",
    noName: "\u0411\u0435\u0437 \u0438\u043c\u0435\u043d\u0438",
    pointsShort: "\u0431\u0430\u043b\u043b\u043e\u0432",
    active: "\u0430\u043a\u0442\u0438\u0432\u0435\u043d",
    blocked: "\u0437\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u043d",
    pointsButton: "\u0411\u0430\u043b\u043b\u044b",
    block: "\u0417\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u0442\u044c",
    unblock: "\u0420\u0430\u0437\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u0442\u044c",
    loadingNumbers: "\u0417\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u043c \u043d\u043e\u043c\u0435\u0440\u0430...",
    noNumbersInStatus: "\u0412 \u044d\u0442\u043e\u043c \u0441\u0442\u0430\u0442\u0443\u0441\u0435 \u043d\u043e\u043c\u0435\u0440\u043e\u0432 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442.",
    approvedComplaints: "\u043e\u0434\u043e\u0431\u0440\u0435\u043d\u043d\u044b\u0445 \u0436\u0430\u043b\u043e\u0431",
    selectNumber: "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043d\u043e\u043c\u0435\u0440",
    selectNumberText: "\u0417\u0434\u0435\u0441\u044c \u043f\u043e\u044f\u0432\u044f\u0442\u0441\u044f \u0441\u0442\u0430\u0442\u0443\u0441, \u0436\u0430\u043b\u043e\u0431\u044b \u0438 \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0435 \u043f\u043e\u0434\u0442\u0432\u0435\u0440\u0436\u0434\u0435\u043d\u0438\u044f.",
    closeNumber: "\u0417\u0430\u043a\u0440\u044b\u0442\u044c \u043d\u043e\u043c\u0435\u0440",
    schemeTypes: "\u0422\u0438\u043f\u044b \u0441\u0445\u0435\u043c",
    noApprovedReports: "\u041f\u043e\u043a\u0430 \u043d\u0435\u0442 \u043e\u0434\u043e\u0431\u0440\u0435\u043d\u043d\u044b\u0445 \u0436\u0430\u043b\u043e\u0431",
    latestComplaint: "\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u044f\u044f \u0436\u0430\u043b\u043e\u0431\u0430",
    noData: "\u041d\u0435\u0442 \u0434\u0430\u043d\u043d\u044b\u0445",
    latestNumberReports: "\u041f\u043e\u0441\u043b\u0435\u0434\u043d\u0438\u0435 \u0437\u0430\u044f\u0432\u043a\u0438 \u043f\u043e \u043d\u043e\u043c\u0435\u0440\u0443",
    noReportsYet: "\u0417\u0430\u044f\u0432\u043e\u043a \u043f\u043e\u043a\u0430 \u043d\u0435\u0442.",
    targetType: "Объект заявки",
    targetTypes: {
      phone: "Телефонный номер",
      url: "Сайт или ссылка",
      account: "Аккаунт / мессенджер",
      card: "Карта или счёт",
      other: "Другое",
    },
    quickDecision: "Быстрое решение",
    approveSuspicious: "Одобрить как подозрительный",
    approveVerified: "Одобрить и подтвердить мошенника",
    rejectSpam: "Отклонить как спам/дубль",
    moderatorNote: "Комментарий будет виден заявителю в профиле.",
  },
  uz: {
    tabReports: "Arizalar",
    tabLessons: "Darslar",
    tabUsers: "Foydalanuvchilar",
    citizenReports: "Fuqarolar arizalari",
    numberRegistry: "Raqamlar reyestri",
    contentManagement: "Kontentni boshqarish",
    lessonImport: "JSON dars importi",
    lessonImportText:
      "Darsni yagona JSON formatida yuklang. Qayta yuklash darsni dublikatlarsiz yangilaydi.",
    lessonJsonFile: "Dars JSON fayli",
    chooseLessonJson: "Dars JSON faylini tanlang.",
    importing: "Yuklanmoqda...",
    importLesson: "Darsni import qilish",
    selectedFile: "Tanlangan fayl:",
    lessonCreated: "Dars yaratildi",
    lessonUpdated: "Dars yangilandi",
    blocks: "blok",
    tasks: "topshiriq",
    questions: "savol",
    coursesLessons: "Kurslar va darslar",
    contentManagerText: "Darslarni ko'rish, JSON yuklab olish va o'chirish.",
    loadingCourses: "Kurslar yuklanmoqda...",
    noCourses: "Hozircha kurslar topilmadi.",
    lessons: "dars",
    published: "e'lon qilingan",
    hidden: "yashirilgan",
    noModule: "Modulsiz",
    open: "Ochish",
    delete: "O'chirish",
    deleteLessonConfirm: "\"{title}\" darsini o'chirasizmi? Bu amalni bekor qilib bo'lmaydi.",
    userManagement: "Foydalanuvchilarni boshqarish",
    platformUsers: "Platforma foydalanuvchilari",
    userManagementText:
      "Administrator foydalanuvchi roli, akkaunt faolligi va ballarini o'zgartira oladi. O'z akkauntingizni pasaytirish yoki o'chirish mumkin emas.",
    searchByName: "Ism bo'yicha qidirish",
    allRoles: "Barcha rollar",
    citizens: "Fuqarolar",
    moderators: "Moderatorlar",
    admins: "Adminlar",
    loadingUsers: "Foydalanuvchilar yuklanmoqda...",
    noUsers: "Foydalanuvchilar topilmadi.",
    noName: "Ismsiz",
    pointsShort: "ball",
    active: "faol",
    blocked: "bloklangan",
    pointsButton: "Ballar",
    block: "Bloklash",
    unblock: "Blokdan chiqarish",
    loadingNumbers: "Raqamlar yuklanmoqda...",
    noNumbersInStatus: "Bu holatda raqamlar hozircha yo'q.",
    approvedComplaints: "tasdiqlangan shikoyat",
    selectNumber: "Raqamni tanlang",
    selectNumberText: "Bu yerda holat, shikoyatlar va tasdiqlash amali ko'rsatiladi.",
    closeNumber: "Raqamni yopish",
    schemeTypes: "Sxema turlari",
    noApprovedReports: "Hozircha tasdiqlangan shikoyatlar yo'q",
    latestComplaint: "Oxirgi shikoyat",
    noData: "Ma'lumot yo'q",
    latestNumberReports: "Raqam bo'yicha oxirgi arizalar",
    noReportsYet: "Hozircha arizalar yo'q.",
    targetType: "Ariza obyekti",
    targetTypes: {
      phone: "Telefon raqami",
      url: "Sayt yoki havola",
      account: "Akkaunt / messenjer",
      card: "Karta yoki hisob",
      other: "Boshqa",
    },
    quickDecision: "Tezkor qaror",
    approveSuspicious: "Shubhali sifatida tasdiqlash",
    approveVerified: "Tasdiqlash va firibgar raqam qilish",
    rejectSpam: "Spam/dublikat sifatida rad etish",
    moderatorNote: "Izoh arizachiga profilida ko'rinadi.",
  },
} as const;

export default function ModerationPage() {
  const { user, loading } = useAuth();
  const { language, t } = useLanguage();
  const [activeTab, setActiveTab] = useState<ModerationTab>("reports");
  const [reportPanel, setReportPanel] = useState<ReportPanel>("reports");
  const [filter, setFilter] = useState<Filter>("pending");
  const [numberFilter, setNumberFilter] = useState<NumberFilter>("suspicious");
  const [reports, setReports] = useState<ModerationReport[]>([]);
  const [numbers, setNumbers] = useState<ModerationNumber[]>([]);
  const [summary, setSummary] = useState<ModerationSummary | null>(null);
  const [selected, setSelected] = useState<ModerationReport | null>(null);
  const [selectedNumber, setSelectedNumber] = useState<ModerationNumber | null>(
    null,
  );
  const [comment, setComment] = useState("");
  const [lessonFile, setLessonFile] = useState<File | null>(null);
  const [lessonImportResult, setLessonImportResult] =
    useState<LessonImportResult | null>(null);
  const [lessonImportError, setLessonImportError] = useState("");
  const [lessonImportBusy, setLessonImportBusy] = useState(false);
  const [courseContent, setCourseContent] = useState<AdminCourseContent[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [contentBusy, setContentBusy] = useState(false);
  const [adminUsers, setAdminUsers] = useState<AdminUser[]>([]);
  const [userRoleFilter, setUserRoleFilter] = useState<UserRoleFilter>("all");
  const [userSearch, setUserSearch] = useState("");
  const [usersBusy, setUsersBusy] = useState(false);
  const [usersError, setUsersError] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const canModerate =
    user?.role === "moderator" || user?.role === "admin";
  const canManageLessons = canModerate;
  const canManageUsers = user?.role === "admin";
  const mt = moderationLocalText[language];
  const regionLabels = Object.fromEntries(
    getRegions(language).map((region) => [region.value, region.label]),
  ) as Record<string, string>;
  const getNumberStatusLabel = (status: ModerationNumber["status"]) =>
    status === "verified_scammer"
      ? t("moderation.verifiedScammer")
      : status === "scammer"
        ? t("moderation.scammer")
        : status === "suspicious"
          ? t("moderation.suspicious")
          : t("moderation.new");
  const getReportTargetLabel = (report: ModerationReport) =>
    report.target_type === "phone"
      ? report.phone_full || report.target_value || report.phone_masked
      : report.target_display || report.target_value;
  const getNumberLabel = (number: ModerationNumber) =>
    number.phone_full || number.phone_masked;
  const getTargetTypeLabel = (targetType: ModerationReport["target_type"]) =>
    mt.targetTypes[targetType];
  const getCalculatedNumberStatus = (
    approvedReports: number,
  ): ModerationNumber["status"] =>
    approvedReports >= 4
      ? "scammer"
      : approvedReports >= 1
        ? "suspicious"
        : "reported";

  const loadData = useCallback(async () => {
    if (!canModerate) return;
    setBusy(true);
    setError("");
    try {
      const [queue, numberRegistry, counters] = await Promise.all([
        api<ModerationReport[]>(
          `/scammer-db/moderation/reports/?status=${filter}`,
          { auth: true },
        ),
        api<ModerationNumber[]>(
          `/scammer-db/moderation/numbers/?status=${numberFilter}`,
          { auth: true },
        ),
        api<ModerationSummary>("/scammer-db/moderation/summary/", {
          auth: true,
        }),
      ]);
      setReports(queue);
      setNumbers(numberRegistry);
      setSummary(counters);
      if (selected) {
        const updated = queue.find((item) => item.id === selected.id);
        setSelected(updated || null);
      }
      if (selectedNumber) {
        const updatedNumber = numberRegistry.find(
          (item) => item.number_id === selectedNumber.number_id,
        );
        setSelectedNumber(updatedNumber || null);
      }
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  }, [canModerate, filter, numberFilter, selected, selectedNumber]);

  useEffect(() => {
    if (!loading) loadData();
    // Selected report is intentionally excluded to avoid a reload loop.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, filter, numberFilter, canModerate]);

  const loadCourseContent = useCallback(async () => {
    if (!canManageLessons) return;
    setContentBusy(true);
    setLessonImportError("");
    try {
      const content = await api<AdminCourseContent[]>("/courses/admin/content/", {
        auth: true,
      });
      setCourseContent(content);
      setSelectedCourseId((current) => current || content[0]?.id || "");
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    } finally {
      setContentBusy(false);
    }
  }, [canManageLessons]);

  useEffect(() => {
    if (!loading && activeTab === "lessons") loadCourseContent();
  }, [activeTab, loadCourseContent, loading]);

  const loadAdminUsers = useCallback(async () => {
    if (!canManageUsers) return;
    setUsersBusy(true);
    setUsersError("");
    try {
      const params = new URLSearchParams();
      if (userRoleFilter !== "all") params.set("role", userRoleFilter);
      if (userSearch.trim()) params.set("search", userSearch.trim());
      const query = params.toString();
      const users = await api<AdminUser[]>(
        `/auth/admin/users/${query ? `?${query}` : ""}`,
        { auth: true },
      );
      setAdminUsers(users);
    } catch (requestError) {
      setUsersError((requestError as Error).message);
    } finally {
      setUsersBusy(false);
    }
  }, [canManageUsers, userRoleFilter, userSearch]);

  useEffect(() => {
    if (!loading && activeTab === "users") loadAdminUsers();
  }, [activeTab, loadAdminUsers, loading]);

  const updateAdminUser = async (
    target: AdminUser,
    payload: Partial<Pick<AdminUser, "role" | "points" | "is_active">>,
  ) => {
    setUsersBusy(true);
    setUsersError("");
    try {
      const updated = await api<AdminUser>(`/auth/admin/users/${target.id}/`, {
        method: "PATCH",
        auth: true,
        body: JSON.stringify(payload),
      });
      setAdminUsers((current) =>
        current.map((item) => (item.id === updated.id ? updated : item)),
      );
    } catch (requestError) {
      setUsersError((requestError as Error).message);
    } finally {
      setUsersBusy(false);
    }
  };

  const moderate = async (
    status: "approved" | "rejected",
    options: { verifyNumber?: boolean; fallbackComment?: string } = {},
  ) => {
    if (!selected) return;
    const moderatorComment = comment.trim() || options.fallbackComment || "";
    if (status === "rejected" && moderatorComment.length < 5) {
      setError(t("moderation.rejectReason"));
      return;
    }
    setBusy(true);
    setError("");
    try {
      const updatedReport = await api<ModerationReport>(
        `/scammer-db/moderation/reports/${selected.id}/`,
        {
          method: "PATCH",
          auth: true,
          body: JSON.stringify({
            status,
            moderator_comment: moderatorComment,
          }),
        },
      );
      if (options.verifyNumber && updatedReport.number_id) {
        await api(
          `/scammer-db/moderation/numbers/${updatedReport.number_id}/verification/`,
          {
            method: "PATCH",
            auth: true,
            body: JSON.stringify({ verified: true }),
          },
        );
      }
      setSelected(null);
      setComment("");
      await loadData();
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const toggleVerification = async () => {
    const target = selectedNumber
      ? {
          id: selectedNumber.number_id,
          verified: selectedNumber.number_verified,
          approvedReports: selectedNumber.approved_reports_count,
        }
      : selected
        && selected.number_id
        ? {
            id: selected.number_id,
            verified: selected.number_verified,
            approvedReports: selected.approved_reports_count,
          }
        : null;
    if (!target) return;
    setBusy(true);
    setError("");
    try {
      const updated = await api<{
        number_id: string;
        phone_masked: string;
        status: ModerationNumber["status"];
        verified_at: string | null;
      }>(`/scammer-db/moderation/numbers/${target.id}/verification/`, {
        method: "PATCH",
        auth: true,
        body: JSON.stringify({ verified: !target.verified }),
      });
      if (selected?.number_id === target.id) {
        setSelected({
          ...selected,
          number_verified: !target.verified,
          number_status: updated.status,
        });
      }
      if (selectedNumber?.number_id === target.id) {
        setSelectedNumber({
          ...selectedNumber,
          number_verified: !target.verified,
          status: updated.status,
          verified_at: updated.verified_at,
        });
      }
      setNumbers((current) =>
        current.map((item) =>
          item.number_id === target.id
            ? {
                ...item,
                number_verified: !target.verified,
                status: updated.status,
                verified_at: updated.verified_at,
              }
            : item,
        ),
      );
      setReports((current) =>
        current.map((item) =>
          item.number_id === target.id
            ? {
                ...item,
                number_verified: !target.verified,
                number_status: target.verified
                  ? getCalculatedNumberStatus(target.approvedReports)
                  : "verified_scammer",
              }
            : item,
        ),
      );
      await loadData();
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const importLessonJson = async () => {
    if (!lessonFile) {
      setLessonImportError(mt.chooseLessonJson);
      return;
    }
    setLessonImportBusy(true);
    setLessonImportError("");
    setLessonImportResult(null);
    try {
      const formData = new FormData();
      formData.append("file", lessonFile);
      const result = await api<LessonImportResult>(
        "/courses/admin/lessons/import/",
        {
          method: "POST",
          auth: true,
          body: formData,
        },
      );
      setLessonImportResult(result);
      setLessonFile(null);
      await loadCourseContent();
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    } finally {
      setLessonImportBusy(false);
    }
  };

  const downloadLessonJson = async (lesson: AdminLesson) => {
    try {
      const payload = await api<unknown>(
        `/courses/admin/lessons/${lesson.id}/export/`,
        { auth: true },
      );
      const blob = new Blob([JSON.stringify(payload, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${String(lesson.order).padStart(2, "0")}-${lesson.slug || lesson.id}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    }
  };

  const deleteLesson = async (lesson: AdminLesson) => {
    const confirmed = window.confirm(mt.deleteLessonConfirm.replace("{title}", lesson.title));
    if (!confirmed) return;
    setContentBusy(true);
    setLessonImportError("");
    try {
      await api(`/courses/admin/lessons/${lesson.id}/`, {
        method: "DELETE",
        auth: true,
      });
      await loadCourseContent();
    } catch (requestError) {
      setLessonImportError((requestError as Error).message);
    } finally {
      setContentBusy(false);
    }
  };

  if (loading) {
    return (
      <section className="page-section">
        <div className="loading-card">
          <span className="loader" /> {t("moderation.checkingAccess")}
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <Gavel />
          <h1>{t("moderation.authRequired")}</h1>
          <Link className="button button-primary" href="/login?next=/moderation">
            {t("common.login")}
          </Link>
        </div>
      </section>
    );
  }

  if (!canModerate) {
    return (
      <section className="page-section">
        <div className="empty-state">
          <ShieldAlert />
          <h1>{t("moderation.accessDenied")}</h1>
          <p>{t("moderation.accessText")}</p>
          <Link className="button button-primary" href="/">
            {t("moderation.home")}
          </Link>
        </div>
      </section>
    );
  }

  const selectedCourse =
    courseContent.find((course) => course.id === selectedCourseId) ||
    courseContent[0] ||
    null;

  return (
    <section className="page-section moderation-page">
      <div className="container">
        <div className="moderation-heading">
          <div>
            <span className="eyebrow">
              <Gavel size={16} /> {t("moderation.eyebrow")}
            </span>
            <h1>{t("moderation.title")}</h1>
            <p>{t("moderation.lead")}</p>
          </div>
          <button
            className="button button-ghost"
            onClick={loadData}
            disabled={busy}
          >
            <RefreshCw size={17} /> {t("moderation.refresh")}
          </button>
        </div>

        <div className="moderation-section-tabs">
          <button
            className={activeTab === "reports" ? "active" : ""}
            onClick={() => setActiveTab("reports")}
          >
            <Gavel size={17} /> {mt.tabReports}
          </button>
          <button
            className={activeTab === "lessons" ? "active" : ""}
            onClick={() => setActiveTab("lessons")}
          >
            <BookOpenText size={17} /> {mt.tabLessons}
          </button>
          {canManageUsers && (
            <button
              className={activeTab === "users" ? "active" : ""}
              onClick={() => setActiveTab("users")}
            >
              <Users size={17} /> {mt.tabUsers}
            </button>
          )}
        </div>

        {activeTab === "reports" && summary && (
          <div className="moderation-metrics">
            <article className="pending">
              <Clock3 />
              <div>
                <strong>{summary.pending}</strong>
                <span>{t("moderation.waiting")}</span>
              </div>
            </article>
            <article className="approved">
              <CheckCircle2 />
              <div>
                <strong>{summary.approved}</strong>
                <span>{t("status.approved")}</span>
              </div>
            </article>
            <article className="rejected">
              <XCircle />
              <div>
                <strong>{summary.rejected}</strong>
                <span>{t("status.rejected")}</span>
              </div>
            </article>
            <article className="verified">
              <BadgeCheck />
              <div>
                <strong>{summary.verified_numbers}</strong>
                <span>{t("moderation.verified")}</span>
              </div>
            </article>
          </div>
        )}

        {activeTab === "reports" && (
        <div className="moderation-toolbar">
          <div className="moderation-filters">
            <ListFilter size={17} />
            {(["reports", "numbers"] as ReportPanel[]).map((panel) => (
              <button
                key={panel}
                className={reportPanel === panel ? "active" : ""}
                onClick={() => {
                  setReportPanel(panel);
                  setSelected(null);
                  setSelectedNumber(null);
                }}
              >
                {panel === "reports" ? mt.citizenReports : mt.numberRegistry}
              </button>
            ))}
            <span className="moderation-filter-divider" />
            {reportPanel === "reports"
              ? (["pending", "approved", "rejected"] as Filter[]).map((status) => (
                <button
                  key={status}
                  className={filter === status ? "active" : ""}
                  onClick={() => {
                    setFilter(status);
                    setSelected(null);
                  }}
                >
                  {status === "pending"
                    ? t("moderation.pendingTab")
                    : status === "approved"
                      ? t("moderation.approvedTab")
                      : t("moderation.rejectedTab")}
                </button>
                ))
              : (
                [
                  "suspicious",
                  "scammer",
                  "verified_scammer",
                  "reported",
                ] as NumberFilter[]
              ).map((status) => (
                <button
                  key={status}
                  className={numberFilter === status ? "active" : ""}
                  onClick={() => {
                    setNumberFilter(status);
                    setSelectedNumber(null);
                  }}
                >
                  {getNumberStatusLabel(status)}
                </button>
              ))}
          </div>
          {summary && (
            <span className="reports-today">
              {t("moderation.today")} <strong>{summary.reports_today}</strong>
            </span>
          )}
        </div>
        )}

        {error && <div className="form-error centered">{error}</div>}

        {activeTab === "lessons" && canManageLessons && (
          <section className="moderation-admin-panel">
            <div className="admin-panel-head">
              <span>
                <BookOpenText size={18} /> {mt.contentManagement}
              </span>
              <strong>{mt.lessonImport}</strong>
              <p>{mt.lessonImportText}</p>
            </div>
            <div className="lesson-import-box">
              <label>
                {mt.lessonJsonFile}
                <input
                  accept="application/json,.json"
                  type="file"
                  onChange={(event) => {
                    setLessonFile(event.target.files?.[0] || null);
                    setLessonImportError("");
                    setLessonImportResult(null);
                  }}
                />
              </label>
              <button
                className="button button-primary"
                disabled={!lessonFile || lessonImportBusy}
                onClick={importLessonJson}
              >
                <UploadCloud size={17} />
                {lessonImportBusy ? mt.importing : mt.importLesson}
              </button>
            </div>
            {lessonFile && (
              <div className="admin-file-note">
                {mt.selectedFile} <strong>{lessonFile.name}</strong>
              </div>
            )}
            {lessonImportError && (
              <div className="form-error">{lessonImportError}</div>
            )}
            {lessonImportResult && (
              <div className="admin-import-result">
                <CheckCircle2 size={18} />
                <div>
                  <strong>{lessonImportResult.status === "created" ? mt.lessonCreated : mt.lessonUpdated}</strong>
                  <p>
                    slug: {lessonImportResult.lesson_slug} · {mt.blocks}: {lessonImportResult.blocks_count} · {mt.tasks}: {lessonImportResult.tasks_count} · {mt.questions}: {lessonImportResult.questions_count}
                  </p>
                </div>
              </div>
            )}
            <div className="content-manager">
              <div className="content-manager-head">
                <div>
                  <strong>{mt.coursesLessons}</strong>
                  <p>{mt.contentManagerText}</p>
                </div>
                <button
                  className="button button-ghost button-small"
                  disabled={contentBusy}
                  onClick={loadCourseContent}
                >
                  <RefreshCw size={15} /> {t("moderation.refresh")}
                </button>
              </div>

              {contentBusy && courseContent.length === 0 ? (
                <div className="loading-card">
                  <span className="loader" /> {mt.loadingCourses}
                </div>
              ) : courseContent.length === 0 ? (
                <div className="panel-empty moderation-empty">
                  <BookOpenText />
                  <p>{mt.noCourses}</p>
                </div>
              ) : (
                <div className="content-manager-grid">
                  <aside className="content-course-list">
                    {courseContent.map((course) => (
                      <button
                        className={selectedCourse?.id === course.id ? "active" : ""}
                        key={course.id}
                        onClick={() => setSelectedCourseId(course.id)}
                      >
                        <strong>{course.title}</strong>
                        <span>
                          {course.level} · {course.lessons_count} {mt.lessons} ·{" "}
                          {course.is_published ? mt.published : mt.hidden}
                        </span>
                      </button>
                    ))}
                  </aside>

                  <div className="content-lesson-list">
                    {selectedCourse?.lessons.map((lesson) => (
                      <article key={lesson.id}>
                        <div>
                          <span>
                            #{lesson.order} · {lesson.module_title || mt.noModule}
                          </span>
                          <strong>{lesson.title}</strong>
                          <p>{lesson.summary}</p>
                        </div>
                        <div className="content-lesson-actions">
                          <Link
                            className="button button-ghost button-small"
                            href={`/courses/${selectedCourse.id}/lessons/${lesson.id}`}
                          >
                            <ExternalLink size={15} /> {mt.open}
                          </Link>
                          <button
                            className="button button-ghost button-small"
                            onClick={() => downloadLessonJson(lesson)}
                          >
                            <Download size={15} /> JSON
                          </button>
                          <button
                            className="button button-danger button-small"
                            disabled={contentBusy}
                            onClick={() => deleteLesson(lesson)}
                          >
                            <Trash2 size={15} /> {mt.delete}
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </section>
        )}

        {activeTab === "users" && canManageUsers && (
          <section className="moderation-admin-panel">
            <div className="admin-panel-head">
              <span>
                <Users size={18} /> {mt.userManagement}
              </span>
              <strong>{mt.platformUsers}</strong>
              <p>{mt.userManagementText}</p>
            </div>

            <div className="admin-users-toolbar">
              <input
                value={userSearch}
                onChange={(event) => setUserSearch(event.target.value)}
                placeholder={mt.searchByName}
              />
              <select
                value={userRoleFilter}
                onChange={(event) =>
                  setUserRoleFilter(event.target.value as UserRoleFilter)
                }
              >
                <option value="all">{mt.allRoles}</option>
                <option value="citizen">{mt.citizens}</option>
                <option value="moderator">{mt.moderators}</option>
                <option value="admin">{mt.admins}</option>
              </select>
              <button
                className="button button-ghost button-small"
                disabled={usersBusy}
                onClick={loadAdminUsers}
              >
                <RefreshCw size={15} /> {t("moderation.refresh")}
              </button>
            </div>

            {usersError && <div className="form-error">{usersError}</div>}

            {usersBusy && adminUsers.length === 0 ? (
              <div className="loading-card">
                <span className="loader" /> {mt.loadingUsers}
              </div>
            ) : adminUsers.length === 0 ? (
              <div className="panel-empty moderation-empty">
                <Users />
                <p>{mt.noUsers}</p>
              </div>
            ) : (
              <div className="admin-users-table">
                {adminUsers.map((managedUser) => (
                  <article key={managedUser.id}>
                    <div className="admin-user-main">
                      <strong>{managedUser.full_name || mt.noName}</strong>
                      <span>{managedUser.phone_masked}</span>
                      <small>
                        #{managedUser.rank} · {managedUser.points} {mt.pointsShort} ·{" "}
                        {managedUser.is_active ? mt.active : mt.blocked}
                      </small>
                    </div>
                    <select
                      value={managedUser.role}
                      disabled={usersBusy}
                      onChange={(event) =>
                        updateAdminUser(managedUser, {
                          role: event.target.value as AdminUser["role"],
                        })
                      }
                    >
                      <option value="citizen">{mt.citizens}</option>
                      <option value="moderator">{mt.moderators}</option>
                      <option value="admin">{mt.admins}</option>
                    </select>
                    <input
                      type="number"
                      min={0}
                      value={managedUser.points}
                      disabled={usersBusy}
                      onChange={(event) =>
                        setAdminUsers((current) =>
                          current.map((item) =>
                            item.id === managedUser.id
                              ? {
                                  ...item,
                                  points: Math.max(
                                    0,
                                    Number(event.target.value) || 0,
                                  ),
                                }
                              : item,
                          ),
                        )
                      }
                    />
                    <button
                      className="button button-ghost button-small"
                      disabled={usersBusy}
                      onClick={() =>
                        updateAdminUser(managedUser, {
                          points: managedUser.points,
                        })
                      }
                    >
                      <Save size={15} /> {mt.pointsButton}
                    </button>
                    <button
                      className={
                        managedUser.is_active
                          ? "button button-danger button-small"
                          : "button button-ghost button-small"
                      }
                      disabled={usersBusy}
                      onClick={() =>
                        updateAdminUser(managedUser, {
                          is_active: !managedUser.is_active,
                        })
                      }
                    >
                      {managedUser.is_active ? mt.block : mt.unblock}
                    </button>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

        {activeTab === "reports" && (
        <div className="moderation-layout">
          <div className="moderation-list">
            {reportPanel === "reports" && busy && reports.length === 0 ? (
              <div className="loading-card">
                <span className="loader" /> {t("moderation.loading")}
              </div>
            ) : reportPanel === "numbers" && busy && numbers.length === 0 ? (
              <div className="loading-card">
                <span className="loader" /> {mt.loadingNumbers}
              </div>
            ) : reportPanel === "reports" && reports.length === 0 ? (
              <div className="panel-empty moderation-empty">
                <FileSearch />
                <p>{t("moderation.empty")}</p>
              </div>
            ) : reportPanel === "numbers" && numbers.length === 0 ? (
              <div className="panel-empty moderation-empty">
                <BadgeCheck />
                <p>{mt.noNumbersInStatus}</p>
              </div>
            ) : reportPanel === "reports" ? (
              reports.map((report) => (
                <button
                  key={report.id}
                  className={
                    selected?.id === report.id
                      ? "moderation-list-item active"
                      : "moderation-list-item"
                  }
                  onClick={() => {
                    setSelected(report);
                    setSelectedNumber(null);
                    setComment(report.moderator_comment || "");
                    setError("");
                  }}
                >
                  <span className="moderation-item-icon">
                    <AlertTriangle />
                  </span>
                  <div>
                    <strong>{getReportTargetLabel(report)}</strong>
                    <p>{getScamLabel(report.scam_type, language)}</p>
                    <small>
                      #{report.id.slice(0, 8)} ·{" "}
                      {new Date(report.created_at).toLocaleDateString(
                        language === "uz" ? "uz-UZ" : "ru-RU",
                      )}
                    </small>
                  </div>
                  <StatusPill
                    tone={
                      report.status === "approved"
                        ? "safe"
                        : report.status === "rejected"
                          ? "danger"
                          : "warning"
                    }
                  >
                    {report.status === "approved"
                      ? t("status.approved")
                      : report.status === "rejected"
                        ? t("status.rejected")
                        : t("moderation.awaiting")}
                  </StatusPill>
                </button>
              ))
            ) : (
              numbers.map((number) => (
                <button
                  key={number.number_id}
                  className={
                    selectedNumber?.number_id === number.number_id
                      ? "moderation-list-item active"
                      : "moderation-list-item"
                  }
                  onClick={() => {
                    setSelectedNumber(number);
                    setSelected(null);
                    setError("");
                  }}
                >
                  <span className="moderation-item-icon number-icon">
                    <BadgeCheck />
                  </span>
                  <div>
                    <strong>{getNumberLabel(number)}</strong>
                    <p>{getNumberStatusLabel(number.status)}</p>
                    <small>
                      {number.approved_reports_count} {mt.approvedComplaints}
                      {number.last_reported_at
                        ? ` · ${new Date(number.last_reported_at).toLocaleDateString(
                            language === "uz" ? "uz-UZ" : "ru-RU",
                          )}`
                        : ""}
                    </small>
                  </div>
                  <StatusPill
                    tone={
                      number.status === "verified_scammer"
                        ? "danger"
                        : number.status === "scammer"
                          ? "danger"
                          : number.status === "suspicious"
                            ? "warning"
                            : "neutral"
                    }
                  >
                    {getNumberStatusLabel(number.status)}
                  </StatusPill>
                </button>
              ))
            )}
          </div>

          <aside className="moderation-detail">
            {reportPanel === "reports" && !selected ? (
              <div className="moderation-placeholder">
                <FileSearch />
                <h2>{t("moderation.select")}</h2>
                <p>{t("moderation.selectText")}</p>
              </div>
            ) : reportPanel === "numbers" && !selectedNumber ? (
              <div className="moderation-placeholder">
                <BadgeCheck />
                <h2>{mt.selectNumber}</h2>
                <p>{mt.selectNumberText}</p>
              </div>
            ) : reportPanel === "reports" && selected ? (
              <>
                <div className="moderation-detail-head">
                  <div>
                    <span className="eyebrow">{mt.numberRegistry}</span>
                    <h2>{getReportTargetLabel(selected)}</h2>
                  </div>
                  <button
                    className="detail-close"
                    onClick={() => setSelected(null)}
                    aria-label={t("moderation.close")}
                  >
                    <X />
                  </button>
                </div>

                {selected.number_id && (
                  <div className="number-state">
                    <div>
                      <span>{t("moderation.numberStatus")}</span>
                      <strong>
                        {getNumberStatusLabel(
                          selected.number_status as ModerationNumber["status"],
                        )}
                      </strong>
                    </div>
                    <div>
                      <span>{t("moderation.approvedReports")}</span>
                      <strong>{selected.approved_reports_count}</strong>
                    </div>
                  </div>
                )}

                <dl className="report-facts">
                  <div>
                    <dt>{mt.targetType}</dt>
                    <dd>{getTargetTypeLabel(selected.target_type)}</dd>
                  </div>
                  <div>
                    <dt>{t("report.number")}</dt>
                    <dd>{getReportTargetLabel(selected)}</dd>
                  </div>
                  <div>
                    <dt>{t("moderation.scamType")}</dt>
                    <dd>
                      {getScamLabel(selected.scam_type, language)}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.incidentDate")}</dt>
                    <dd>
                      {new Date(selected.incident_date).toLocaleDateString(
                        language === "uz" ? "uz-UZ" : "ru-RU",
                      )}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.region")}</dt>
                    <dd>
                      {regionLabels[selected.region] || selected.region}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.damage")}</dt>
                    <dd>
                      {selected.damage_amount
                        ? `${Number(selected.damage_amount).toLocaleString(
                            language === "uz" ? "uz-UZ" : "ru-RU",
                          )} UZS`
                        : t("moderation.notSpecified")}
                    </dd>
                  </div>
                  <div>
                    <dt>{t("moderation.reporter")}</dt>
                    <dd>{selected.reporter_name || t("moderation.noName")}</dd>
                  </div>
                </dl>

                <div className="report-story">
                  <strong>{t("moderation.story")}</strong>
                  <p>{selected.story}</p>
                </div>

                <label className="moderator-comment-field">
                  {t("moderation.comment")}
                  <textarea
                    value={comment}
                    onChange={(event) => setComment(event.target.value)}
                    maxLength={500}
                    placeholder={t("moderation.commentPlaceholder")}
                  />
                  <small>{mt.moderatorNote}</small>
                </label>

                {selected.status === "pending" ? (
                  <div className="moderation-actions moderation-actions-quick">
                    <span>{mt.quickDecision}</span>
                    <button
                      className="button moderation-reject"
                      disabled={busy}
                      onClick={() =>
                        moderate("rejected", {
                          fallbackComment:
                            language === "uz"
                              ? "Spam yoki dublikat ariza."
                              : "Спам или дублирующая заявка.",
                        })
                      }
                    >
                      <XCircle size={17} /> {mt.rejectSpam}
                    </button>
                    <button
                      className="button moderation-approve"
                      disabled={busy}
                      onClick={() => moderate("approved")}
                    >
                      <Check size={17} /> {mt.approveSuspicious}
                    </button>
                    {selected.number_id && (
                      <button
                        className="button button-danger moderation-verify-approve"
                        disabled={busy}
                        onClick={() =>
                          moderate("approved", {
                            verifyNumber: true,
                            fallbackComment:
                              language === "uz"
                                ? "Moderator raqamni tasdiqlangan firibgar deb belgiladi."
                                : "Модератор отметил номер как подтверждённый мошеннический.",
                          })
                        }
                      >
                        <BadgeCheck size={17} /> {mt.approveVerified}
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="decision-banner">
                    {t("moderation.decision")}{" "}
                    <strong>
                      {selected.status === "approved"
                        ? t("moderation.decisionApproved")
                        : t("moderation.decisionRejected")}
                    </strong>
                  </div>
                )}

                {selected.number_id && (
                  <button
                    className={
                      selected.number_verified
                        ? "button button-ghost button-wide"
                        : "button button-danger button-wide"
                    }
                    disabled={busy}
                    onClick={toggleVerification}
                  >
                    <BadgeCheck size={17} />
                    {selected.number_verified
                      ? t("moderation.unverify")
                      : t("moderation.verify")}
                  </button>
                )}
              </>
            ) : selectedNumber ? (
              <>
                <div className="moderation-detail-head">
                  <div>
                    <span className="eyebrow">{mt.numberRegistry}</span>
                    <h2>{getNumberLabel(selectedNumber)}</h2>
                  </div>
                  <button
                    className="detail-close"
                    onClick={() => setSelectedNumber(null)}
                    aria-label={mt.closeNumber}
                  >
                    <X />
                  </button>
                </div>

                <div className="number-state">
                  <div>
                    <span>{t("moderation.numberStatus")}</span>
                    <strong>{getNumberStatusLabel(selectedNumber.status)}</strong>
                  </div>
                  <div>
                    <span>{t("moderation.approvedReports")}</span>
                    <strong>{selectedNumber.approved_reports_count}</strong>
                  </div>
                </div>

                <dl className="report-facts">
                  <div>
                    <dt>{mt.schemeTypes}</dt>
                    <dd>
                      {selectedNumber.scam_types.length
                        ? selectedNumber.scam_types
                            .map((type) => getScamLabel(type, language))
                            .join(", ")
                        : mt.noApprovedReports}
                    </dd>
                  </div>
                  <div>
                    <dt>{mt.latestComplaint}</dt>
                    <dd>
                      {selectedNumber.last_reported_at
                        ? new Date(selectedNumber.last_reported_at).toLocaleDateString(
                            language === "uz" ? "uz-UZ" : "ru-RU",
                          )
                        : mt.noData}
                    </dd>
                  </div>
                </dl>

                <div className="report-story number-reports">
                  <strong>{mt.latestNumberReports}</strong>
                  {selectedNumber.latest_reports.length ? (
                    <div className="number-report-list">
                      {selectedNumber.latest_reports.map((report) => (
                        <article key={report.id}>
                          <span>
                            #{report.id.slice(0, 8)} ·{" "}
                            {getScamLabel(report.scam_type, language)}
                          </span>
                          <p>{report.story}</p>
                        </article>
                      ))}
                    </div>
                  ) : (
                    <p>{mt.noReportsYet}</p>
                  )}
                </div>

                <button
                  className={
                    selectedNumber.number_verified
                      ? "button button-ghost button-wide"
                      : "button button-danger button-wide"
                  }
                  disabled={busy}
                  onClick={toggleVerification}
                >
                  <BadgeCheck size={17} />
                  {selectedNumber.number_verified
                    ? t("moderation.unverify")
                    : t("moderation.verify")}
                </button>
              </>
            ) : null}
          </aside>
        </div>
        )}
      </div>
    </section>
  );
}
