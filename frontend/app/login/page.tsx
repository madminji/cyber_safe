"use client";

import { ArrowLeft, ArrowRight, LockKeyhole, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { useAuth } from "@/context/auth-context";
import { useLanguage } from "@/context/language-context";

export default function LoginPage() {
  const router = useRouter();
  const { requestOtp, verifyOtp } = useAuth();
  const { language } = useLanguage();
  const [step, setStep] = useState<"phone" | "code">("phone");
  const [phone, setPhone] = useState("+998");
  const [name, setName] = useState("");
  const [challengeId, setChallengeId] = useState("");
  const [code, setCode] = useState("");
  const [devCode, setDevCode] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const sendCode = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const result = await requestOtp({
        phone,
        full_name: name,
        language,
      });
      setChallengeId(result.challenge_id);
      setDevCode(result.development_otp || "");
      setStep("code");
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const confirmCode = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      await verifyOtp({ phone, challenge_id: challengeId, code });
      const nextPath = new URLSearchParams(window.location.search).get("next");
      router.push(
        nextPath && nextPath.startsWith("/") && !nextPath.startsWith("//")
          ? nextPath
          : "/account",
      );
    } catch (requestError) {
      setError((requestError as Error).message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="auth-section">
      <div className="auth-glow" />
      <div className="auth-card">
        <div className="auth-icon">
          {step === "phone" ? <ShieldCheck /> : <LockKeyhole />}
        </div>
        <span className="eyebrow">Без пароля</span>
        <h1>{step === "phone" ? "Войти в CyberSafe" : "Введите код"}</h1>
        <p>
          {step === "phone"
            ? "Мы отправим одноразовый код на ваш номер телефона."
            : `Код отправлен на ${phone}`}
        </p>

        {step === "phone" ? (
          <form onSubmit={sendCode} className="form-stack">
            <label>
              Ваше имя
              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="Имя и фамилия"
              />
            </label>
            <label>
              Номер телефона
              <input
                value={phone}
                onChange={(event) => setPhone(event.target.value)}
                placeholder="+998 90 123 45 67"
                required
              />
            </label>
            {error && <div className="form-error">{error}</div>}
            <button className="button button-primary button-wide" disabled={busy}>
              {busy ? "Отправляем..." : "Получить код"}
              <ArrowRight size={18} />
            </button>
          </form>
        ) : (
          <form onSubmit={confirmCode} className="form-stack">
            <label>
              Код из SMS
              <input
                className="otp-input"
                value={code}
                onChange={(event) =>
                  setCode(event.target.value.replace(/\D/g, "").slice(0, 6))
                }
                placeholder="000000"
                inputMode="numeric"
                autoFocus
                required
              />
            </label>
            {devCode && (
              <div className="dev-code">
                Код для локальной разработки: <strong>{devCode}</strong>
              </div>
            )}
            {error && <div className="form-error">{error}</div>}
            <button
              className="button button-primary button-wide"
              disabled={busy || code.length !== 6}
            >
              {busy ? "Проверяем..." : "Подтвердить"}
              <ArrowRight size={18} />
            </button>
            <button
              type="button"
              className="back-button"
              onClick={() => setStep("phone")}
            >
              <ArrowLeft size={16} /> Изменить номер
            </button>
          </form>
        )}
        <small className="privacy-note">
          Номер хранится в зашифрованном виде и не отображается публично.
        </small>
      </div>
    </section>
  );
}
