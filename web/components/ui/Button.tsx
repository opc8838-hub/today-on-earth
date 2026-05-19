export function Button({
  children,
  variant = "default",
  size = "md",
  className = "",
  ...props
}: {
  children: React.ReactNode;
  variant?: "default" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const base =
    "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none disabled:opacity-40 disabled:pointer-events-none";

  const variants = {
    default: "bg-earth-blue text-white hover:bg-earth-blue/80",
    outline:
      "border border-earth-600 text-earth-300 hover:border-earth-blue hover:text-earth-blue",
    ghost: "text-earth-300 hover:text-earth-100 hover:bg-earth-800",
  };

  const sizes = {
    sm: "h-8 px-3 text-xs",
    md: "h-10 px-4 text-sm",
    lg: "h-12 px-6 text-sm",
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
