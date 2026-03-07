// frontend/components/InputBar.tsx

import { useState, useRef } from "react";

export default function InputBar({
  onSend,
  disabled = false,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
}) {
  const [text, setText] = useState("");
  const recognitionRef = useRef<any>(null);

  // 🎤 Voice input
  function startVoiceInput() {
    if (!("webkitSpeechRecognition" in window)) {
      alert("Voice input is not supported in this browser.");
      return;
    }

    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (e: any) => {
      setText(e.results[0][0].transcript);
    };

    recognition.start();
    recognitionRef.current = recognition;
  }

  function send() {
    if (!text.trim()) return;
    onSend(text);
    setText("");
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        width: "100%",
        opacity: disabled ? 0.7 : 1,
      }}
    >
      {/* TEXT INPUT */}
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !disabled) {
            send();
          }
        }}
        placeholder={disabled ? "Assistant is typing..." : "Type a message..."}
        disabled={disabled}
        style={{
          flex: 1,
          height: 44,
          padding: "0 14px",
          borderRadius: 22,
          border: "1px solid #d1d5db",
          background: disabled ? "#e5e7eb" : "#fff",
          fontSize: 14,
        }}
      />

      {/* 🎤 MIC BUTTON */}
      <button
        disabled={disabled}
        onClick={startVoiceInput}
        style={{
          height: 44,
          width: 44,
          background: "#facc15",
          borderRadius: "50%",
          fontSize: 14,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
        onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.92)")}
        onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      >
        🎤
      </button>

      {/* SEND BUTTON */}
      <button
        disabled={disabled}
        onClick={send}
        style={{
          height: 44,
          background: disabled ? "#9ca3af" : "#4c79ff",
          color: "#fff",
          fontSize: 14,
          borderRadius: 22,
          padding: "0 18px",
          cursor: disabled ? "not-allowed" : "pointer",
                }}
        onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.92)")}
        onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      >
        {disabled ? "…" : "Send →"}
      </button>
    </div>
  );
}
