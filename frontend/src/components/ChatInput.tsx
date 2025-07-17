import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Escribe tu mensaje aquí..." 
}: ChatInputProps) => {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className={cn(
              "min-h-[60px] max-h-32 resize-none pr-14 pl-4 py-4",
              "border-2 border-border bg-background focus:ring-2 focus:ring-ring",
              "placeholder:text-muted-foreground rounded-xl",
              "text-base leading-relaxed"
            )}
            rows={1}
          />
          
          <Button
            type="submit"
            disabled={disabled || !message.trim()}
            size="icon"
            className={cn(
              "absolute right-2 bottom-2 h-10 w-10 shrink-0 rounded-lg",
              "bg-primary hover:bg-primary-hover text-primary-foreground",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-all duration-200"
            )}
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">Enviar mensaje</span>
          </Button>
        </div>
        
        <div className="text-xs text-muted-foreground text-center mt-2">
          Presiona Enter para enviar, Shift + Enter para nueva línea
        </div>
      </form>
    </div>
  );
};