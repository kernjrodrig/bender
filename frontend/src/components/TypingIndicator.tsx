import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import aiAvatar from "@/assets/ai-avatar.png";

export const TypingIndicator = () => {
  return (
    <div className="max-w-3xl mx-auto w-full">
      <div className="flex gap-4 p-6 rounded-lg bg-card border border-border animate-message-in">
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarImage src={aiAvatar} alt="IA escribiendo" />
          <AvatarFallback className="bg-secondary text-secondary-foreground text-xs font-medium">
            IA
          </AvatarFallback>
        </Avatar>
        
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-foreground">
              Asistente IA
            </span>
            <span className="text-xs text-muted-foreground">
              escribiendo...
            </span>
          </div>
          
          <div className="flex items-center space-x-1 text-muted-foreground">
            <div className="w-2 h-2 bg-current rounded-full typing-dots"></div>
            <div className="w-2 h-2 bg-current rounded-full typing-dots"></div>
            <div className="w-2 h-2 bg-current rounded-full typing-dots"></div>
          </div>
        </div>
      </div>
    </div>
  );
};