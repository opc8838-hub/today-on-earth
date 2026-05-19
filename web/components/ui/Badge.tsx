export function Badge({
  children,
  variant = "default",
  className = "",
}: {
  children: React.ReactNode;
  variant?: "default" | "gold" | "blue";
  className?: string;
}) {
  const variants = {
    default: "bg-earth-700 text-earth-300 border-earth-600",
    gold: "bg-earth-gold/10 text-earth-gold border-earth-gold/20",
    blue: "bg-earth-blue/10 text-earth-blue border-earth-blue/20",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
