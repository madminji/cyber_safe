import { ShieldCheck } from "lucide-react";

export function Logo() {
  return (
    <span className="logo">
      <span className="logo-mark">
        <ShieldCheck size={22} strokeWidth={2.4} />
      </span>
      <span>
        CyberSafe
        <small>UZBEKISTAN</small>
      </span>
    </span>
  );
}

