# chatbot/test_resume_builder.py

from chatbot.knowledge.resume_builder import build_resume_knowledge_base

USER_ID = "6593eba4-0118-4e49-ba9c-c2b6a9e879cf"

def main():
    chunks = build_resume_knowledge_base(USER_ID)

    print("\n==============================")
    print(f"TOTAL CHUNKS: {len(chunks)}")
    print("==============================\n")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n---- CHUNK {i} ----\n")
        print(chunk)

if __name__ == "__main__":
    main()


