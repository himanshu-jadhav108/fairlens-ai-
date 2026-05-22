import { useEffect, useRef, useState, type ReactNode, type CSSProperties } from "react";

interface StaggerItemProps {
  children: ReactNode;
  index?: number;
  delay?: number;
  className?: string;
}

export default function StaggerItem({ children, index = 0, delay = 80, className = "" }: StaggerItemProps) {
  const [visible, setVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), index * delay);
    return () => clearTimeout(timer);
  }, [index, delay]);

  const style: CSSProperties = {
    transitionProperty: "opacity, transform",
    transitionDuration: "400ms",
    transitionTimingFunction: "cubic-bezier(0.16, 1, 0.3, 1)",
    opacity: visible ? 1 : 0,
    transform: visible ? "translateY(0)" : "translateY(12px)",
  };

  return (
    <div ref={ref} style={style} className={className}>
      {children}
    </div>
  );
}
