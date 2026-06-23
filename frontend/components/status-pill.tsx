export function StatusPill({
  tone,
  children,
}: {
  tone: "safe" | "warning" | "danger" | "neutral";
  children: React.ReactNode;
}) {
  return <span className={`status-pill ${tone}`}>{children}</span>;
}

