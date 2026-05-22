import { X } from "lucide-react";

interface ErrorAlertProps {
  message: string;
  onDismiss: () => void;
}

export default function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-md bg-danger/10 border border-danger/20 text-danger text-xs font-mono">
      <span className="flex-1">{message}</span>
      <button onClick={onDismiss} className="text-danger hover:text-foreground transition-colors cursor-pointer">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}
