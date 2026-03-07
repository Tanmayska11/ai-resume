//frontend/app/page.tsx

"use client";

import { useEffect, useState, useRef } from "react";
import MessageBubble from "@/components/MessageBubble";
import MenuCard from "@/components/MenuCard";
import InputBar from "@/components/InputBar";
import { askChatbot} from "@/lib/api";
import { Message } from "@/types/chat";
import { useAuth0 } from "@auth0/auth0-react"





type MenuContext = "main" | "experience" | "education" | null;

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [menu, setMenu] = useState<MenuContext>("main");
  const [isTyping, setIsTyping] = useState(false);
  const [previousMenu, setPreviousMenu] = useState<MenuContext>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const [cameFromSubmenu, setCameFromSubmenu] = useState(false);
  const recognitionRef = useRef<any>(null);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const wasVoiceQueryRef = useRef(false);
  const { loginWithRedirect } = useAuth0()




  




  const buttonStyle = {
    padding: "10px 16px",
    margin: "10px",
    borderRadius: 10,
    border: "none",
    fontWeight: 600,
    cursor: "pointer",
    background: "#2563eb",
    color: "#fff",
    transition: "transform 0.08s ease, box-shadow 0.08s ease",
    boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
  };


  // Initial greeting
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        content:
          "I’m Tanmay’s AI Resume Assistant. What would you like to know about me?",
      },
    ]);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, menu]);


  async function sendUserMessage(question: string) {

    window.speechSynthesis.cancel(); 

    
      
    setIsTyping(true);

    setMessages((m) => [
      ...m,
      { role: "user", content: question },
      { role: "assistant", content: "Typing..." },
    ]);

    try {
      const res = await askChatbot(question);

      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "assistant",
          content: res.answer,
        };
        return updated;
      });

      if (wasVoiceQueryRef.current) {
        speakAnswer(res.answer);
        wasVoiceQueryRef.current = false; // reset
      }



    } catch {
      setMessages((m) => {
        const updated = [...m];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "That information is not part of Tanmay’s resume or documented projects.",
        };
        return updated;
      });
    } finally {
      setIsTyping(false);
      setMenu(null);
    }
  }


  function startVoiceInput() {
    if (typeof window === "undefined") return;

    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Voice input is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.continuous = false;

    recognition.onstart = () => setIsListening(true);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      wasVoiceQueryRef.current = true;       // 🔥 mark as voice query
      sendUserMessage(transcript);
    };


    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.start();
    recognitionRef.current = recognition;
  }


  function stopSpeaking() {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }

  function speakAnswer(text: string) {
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US";
    utterance.rate = 1;
    utterance.pitch = 1;

    setIsSpeaking(true); // 🔴 NOW React WILL re-render

    utterance.onend = () => {
      setIsSpeaking(false);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
    };

    window.speechSynthesis.speak(utterance);
  }






  return (
    <div
      style={{
        maxWidth: 820,
        margin: "0 auto",
        padding: 24,
      }}
    >

      {/* TOP RIGHT BUTTONs */}
      
     <a
      
      target="_blank"
      rel="noopener noreferrer"
      onClick={() =>
          window.open(`${window.location.origin}/match`, "_blank")
        }
      style={{
        ...buttonStyle,
        margin:"0px 0px 0px 850px",
        background: "#16a34a",
        color: "#fff",
        padding: "20px 20px 20px 20px",
        borderRadius: 999,
        fontSize: 20,
        fontWeight: 600,
        textDecoration: "none",
        boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
        whiteSpace: "nowrap",
      }}
    >
      📈 View Career Prediction
    </a>
    <a
      
      target="_blank"
      rel="noopener noreferrer"
      onClick={() =>
        loginWithRedirect({
          authorizationParams: {
            redirect_uri: `${window.location.origin}/admin`,
            connection: "email"
          }
        })
      }
      style={{
        ...buttonStyle,
        margin:"0px 0px 0px 10px",
        background: "#165fa3",
        color: "#fff",
        padding: "20px 20px 20px 20px",
        borderRadius: 999,
        fontSize: 20,
        fontWeight: 600,
        textDecoration: "none",
        boxShadow: "0 6px 16px rgba(0,0,0,0.15)",
        whiteSpace: "nowrap",
      }}
    >
      Admin
    </a>



      {/* HEADER */}
      <h1
      style={{
        textAlign: "center",
        marginBottom: 20,
        padding: "14px 18px",
        background: "rgba(247, 78, 236, 0.82)",
        borderRadius: 14,
        fontWeight: 700,
        letterSpacing: "0.3px",
        color: "#111827",
        boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
      }}
    >
      🤖<br/> AI Resume Assistant
    </h1>

      {/* CHAT */}
      <div
      style={{
        minHeight: "100px",
        padding: "16px",
        margin: "18px 0",
        background: "#f3f4f6",            // light dark-gray background
        borderRadius: 18,
        boxShadow: "0 10px 28px rgba(0,0,0,0.08)",
        border: "1px solid #e5e7eb",
      }}
    >
      {messages.map((m, i) => (
        <MessageBubble key={i} role={m.role} text={m.content} />
      ))}

      {/* AUTO-SCROLL ANCHOR */}
      <div ref={bottomRef} />
    </div>


      {/* MENUS */}
      {menu === "main" && (
        <MenuCard
          title="Main Menu"
          items={[
            "Profile",
            "Experience",
            "Projects",
            "Skills",
            "Education",
            "Certifications",
            "Languages",
            "Interests",
            
          ]}
          onSelect={(item) => {
            console.log("MENU CLICKED:", item);
            

            if (item === "Experience") {
              setPreviousMenu("experience");
              setCameFromSubmenu(true);
              return setMenu("experience");
            }

            if (item === "Education") {
              setPreviousMenu("education");
              setCameFromSubmenu(true);
              return setMenu("education");
            }

            setCameFromSubmenu(false);
            sendUserMessage(mapMain(item));
          }}
        />
      )}

      {menu === "experience" && (
        <MenuCard
          title="Choose Experience Type"
          items={[
            "Professional Experience",
            "Experimental Experience",
          ]}
          onSelect={(item) => {

            setPreviousMenu("experience");

            sendUserMessage(
              item === "Professional Experience"
                ? "Explain Tanmay's professional work experience"
                : "Explain Tanmay's experimental experience"
            )

          }}
        />
      )}

      {menu === "education" && (
        <MenuCard
          title="Choose Education Type"
          items={["Master’s Degree", "Engineering Degree"]}
          onSelect={(item) => {

            setPreviousMenu("education");

            sendUserMessage(
              item === "Master’s Degree"
                ? "Explain Tanmay's master's education"
                : "Explain Tanmay's engineering education"
            )

          }}
        />
      )}

      {/* NAV BUTTONS AFTER ANSWER */}
      {menu === null && (
        <div >
          {cameFromSubmenu && (
            <button
            style={buttonStyle}
            onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.96)")}
            onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
            onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")} 

            onClick={() => setMenu(previousMenu)}>
              ⬅ Back to Submenu
            </button>
          )}

          <button
          style={buttonStyle}
          onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.96)")}
          onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
          onClick={() => setMenu("main")}>
            🏠 Main Menu
          </button>
        </div>
      )}

      


      {/* INPUT */}
      {/* INPUT BAR + ACTIONS */}
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 10,
        padding: "12px",
        background: "#e5e7eb",
        borderRadius: 14,
      }}
    >
      <InputBar onSend={sendUserMessage} disabled={isTyping} />

      <button
        onClick={isSpeaking ? stopSpeaking : startVoiceInput}
        disabled={isListening && !isSpeaking}
        style={{
          height: 44,
          padding: "0 16px",
          borderRadius: 999,
          border: "none",
          fontWeight: 600,
          cursor: "pointer",
          background: isSpeaking ? "#dc2626" : "#2563eb", // 🔴 when speaking
          color: "#fff",
          whiteSpace: "nowrap",
          boxShadow: "0 4px 10px rgba(0,0,0,0.15)",
        }}
      >
        {isSpeaking ? "🔇 Stop Speaking" : "🎙️ Ask by Voice"}
      </button>



    </div>



    </div>
  );
}

function mapMain(label: string) {
  const map: Record<string, string> = {
    Profile: "Tell me about Tanmay",
    Projects: "Describe Tanmay's projects",
    Skills: "Describe Tanmay's skills",
    Certifications: "List Tanmay's certifications",
    Languages: "Which languages do Tanmay speak and at what proficiency",
    Interests: "Tell me about Tanmay's extracurricular activities and interests",
    
  };

  return map[label];
}
