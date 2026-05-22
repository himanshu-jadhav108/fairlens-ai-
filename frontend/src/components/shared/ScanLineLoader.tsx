interface ScanLineLoaderProps {
  text?: string;
}

export default function ScanLineLoader({ text }: ScanLineLoaderProps) {
  return (
    <div className="w-full space-y-3">
      <div className="scan-line-loader w-full" />
      {text && (
        <p className="text-foreground-secondary text-xs font-mono text-center">{text}</p>
      )}
    </div>
  );
}
