import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import aiAvatar from "@/assets/ai-avatar.png";
import userAvatar from "@/assets/user-avatar.png";

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === 'user';

  return (
    <div className="max-w-3xl mx-auto w-full">
      <div
        className={cn(
          "flex gap-4 p-6 rounded-lg animate-message-in",
          isUser 
            ? "ml-auto max-w-2xl bg-primary text-primary-foreground" 
            : "bg-card border border-border"
        )}
      >
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarImage 
            src={isUser ? userAvatar : aiAvatar} 
            alt={isUser ? "Usuario" : "IA"} 
          />
          <AvatarFallback className={cn(
            "text-xs font-medium",
            isUser ? "bg-primary-foreground text-primary" : "bg-secondary text-secondary-foreground"
          )}>
            {isUser ? "TÚ" : "IA"}
          </AvatarFallback>
        </Avatar>
        
        <div className="flex-1 space-y-2 min-w-0">
          <div className="flex items-center gap-2">
            <span className={cn(
              "text-sm font-medium",
              isUser ? "text-primary-foreground" : "text-foreground"
            )}>
              {isUser ? "Tú" : "Asistente IA"}
            </span>
            <span className={cn(
              "text-xs",
              isUser ? "text-primary-foreground/70" : "text-muted-foreground"
            )}>
              {message.timestamp.toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </span>
          </div>
          
          <div className={cn(
            "text-sm leading-relaxed whitespace-pre-wrap",
            isUser ? "text-primary-foreground" : "text-foreground"
          )}>
            {message.content}
          </div>
        </div>
      </div>
    </div>
  );
};