//frontend/lib/api.ts


export type ChatResponse = {
  answer: string;
  sources: {
    label: string;
    url?: string | null;
    source: string;
  }[];
};

export async function askChatbot(question: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/chat/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  return res.json();
}
