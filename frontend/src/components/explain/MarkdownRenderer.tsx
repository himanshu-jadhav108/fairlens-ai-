interface Props {
  text: string;
}

export default function MarkdownRenderer({ text }: Props) {
  const lines = text.split("\n");

  return (
    <div className="space-y-3 leading-relaxed text-[14px]">
      {lines.map((line, i) => {
        const trimmed = line.trim();

        if (trimmed === "---") {
          return <hr key={i} className="border-border my-6" />;
        }

        if (trimmed.startsWith("#### ")) {
          return (
            <h4 key={i} className="font-display text-[14px] font-bold text-primary/80 uppercase tracking-wider mt-6 mb-2">
              {renderInline(trimmed.slice(5))}
            </h4>
          );
        }

        if (trimmed.startsWith("### ")) {
          return (
            <h3 key={i} className="font-display text-[16px] font-bold text-foreground mt-6 mb-3">
              {renderInline(trimmed.slice(4))}
            </h3>
          );
        }

        if (trimmed.startsWith("## ")) {
          return (
            <h2 key={i} className="font-display text-[20px] font-bold text-primary mt-8 mb-4 border-b border-border/50 pb-2">
              {renderInline(trimmed.slice(3))}
            </h2>
          );
        }

        if (trimmed.startsWith("> ")) {
          return (
            <blockquote key={i} className="border-l-4 border-warning/50 pl-4 bg-warning/5 p-3 rounded-r italic text-foreground-muted text-sm my-3">
              {renderInline(trimmed.slice(2))}
            </blockquote>
          );
        }

        // Bullet lists
        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          return (
            <div key={i} className="flex items-start gap-3 mt-1 mb-2 ml-2">
              <span className="text-primary mt-1 flex-shrink-0 text-[10px]">●</span>
              <p className="text-foreground-secondary">{renderInline(trimmed.slice(2))}</p>
            </div>
          );
        }

        // Numbered lists (e.g. "1. ", "2. ")
        const numberedListMatch = trimmed.match(/^(\d+)\.\s+(.*)/);
        if (numberedListMatch) {
          return (
            <div key={i} className="flex items-start gap-3 mt-2 mb-2 ml-2">
              <span className="text-primary font-mono font-bold flex-shrink-0">{numberedListMatch[1]}.</span>
              <p className="text-foreground-secondary">{renderInline(numberedListMatch[2])}</p>
            </div>
          );
        }

        if (trimmed === "") {
          return <div key={i} className="h-1" />;
        }

        return (
          <p key={i} className="text-foreground-secondary">
            {renderInline(trimmed)}
          </p>
        );
      })}
    </div>
  );
}

function renderInline(text: string) {
  // Regex to match **bold** or `code`
  const parts = text.split(/(\*\*.*?\*\*|`.*?`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="text-foreground font-bold font-display">
          {part.slice(2, -2)}
        </strong>
      );
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code key={i} className="text-primary bg-primary/10 px-1.5 py-0.5 rounded font-mono text-[12px] font-semibold">
          {part.slice(1, -1)}
        </code>
      );
    }
    return part;
  });
}
