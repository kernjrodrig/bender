import { useState, useRef, useEffect } from "react";
import { ChatMessage, type Message } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { TypingIndicator } from "./TypingIndicator";
import { Button } from "@/components/ui/button";
import { Trash2, MessageSquare, Sun, Moon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "next-themes";

export const ChatInterface = () => {
  const { theme, setTheme } = useTheme();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      content: "¡Hola! Soy Bender, tu asistente IA. Puedo ayudarte con consultas sobre Jira y responder preguntas generales. ¿En qué puedo ayudarte hoy?",
      role: "assistant",
      timestamp: new Date(),
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (content: string) => {
    // Agregar mensaje del usuario
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      // Conectar con el backend de Bender
      const API_URL = import.meta.env.VITE_API_URL || "/chat";
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mensaje: content
        }),
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.respuesta || "Lo siento, no pude procesar tu mensaje.",
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Lo siento, hubo un error al procesar tu mensaje. Por favor, intenta de nuevo.",
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome",
        content: "¡Hola! Soy Bender, tu asistente IA. Puedo ayudarte con consultas sobre Jira y responder preguntas generales. ¿En qué puedo ayudarte hoy?",
        role: "assistant",
        timestamp: new Date(),
      }
    ]);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navigation */}
      <header className="flex items-center justify-between p-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-6 w-6 text-primary" />     <h1 className="text-xl font-semibold text-foreground">
            Bender - Asistente IA
          </h1>  </div>
        
        <div className="flex items-center gap-2">
          <Button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            {theme === "dark" ? "Modo claro" : "Modo oscuro"}
          </Button>
          
          <Button
            onClick={clearChat}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <Trash2 className="h-4 w-4"/>
            Limpiar
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Chat Container */}
        <div className="w-full max-w-4xl mx-auto flex flex-col h-full">
          {/* Messages Area */}
          <div className={cn(
            "flex-1 overflow-y-auto chat-scroll p-4      space-y-4   ")}>
            {messages.length === 1 && (
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6">
                <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="h-8 w-8 text-primary" />
                </div>
                <div className="space-y-2">
                  <h2 className="text-2xl font-semibold text-foreground">
                    ¿En qué puedo ayudarte?
                  </h2>
                  <p className="text-muted-foreground max-w-md">
                    Puedes preguntarme sobre tickets de Jira, proyectos, o cualquier consulta general. 
                    ¡Estoy aquí para ayudarte!
                  </p>
                </div>
              </div>
            )}
            
            {messages.length > 1 && messages.slice(1).map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            
            {isTyping && <TypingIndicator />}
            
            <div ref={messagesEndRef} />
          </div>

      {/* Input Area */}
          <div className="p-4 border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <ChatInput
              onSendMessage={handleSendMessage}
              disabled={isTyping}
              placeholder="Escribe tu mensaje aquí... (puedes preguntar sobre tickets de Jira como SD-1SD-2)"
            />
          </div>
        </div>
      </div>
    </div>
  );
}; 