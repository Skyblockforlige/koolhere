import io
import contextlib

from agentic_rag_system import agent


def ask(question: str):
    # Suppress the engine's internal debug prints for a clean Q&A experience.
    with contextlib.redirect_stdout(io.StringIO()):
        result = agent.invoke({"query": question})
    return result


def main():
    print("\n" + "=" * 60)
    print("  ShopUNow Assistant - Ask me anything")
    print("=" * 60)
    print("Type your question and press Enter. Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in ("exit", "quit"):
            print("\nGoodbye!")
            break

        result = ask(question)

        print(f"\nAssistant: {result['response']}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
