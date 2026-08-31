from model_client import ModelClient

def main():
    client = ModelClient()

    conversation_turns = [
        "What is prototype pollution in JavaScript?",
        "How does it affect libraries like lodash specifically?",
        "What's a real-world example of this being exploited?",
        "How can developers prevent it in their own code?",
        "Summarize everything we discussed in 3 bullet points."
    ]

    for i, user_message in enumerate(conversation_turns, start=1):
        print(f"\n--- User (Turn {i}) ---")
        print(user_message)

        messages = [{"role": "user", "content": user_message}]
        response = client.complete(messages)

        print(f"--- Assistant (Turn {i}) ---")
        print(response)

        if i == 3 or i == 5:
            print(f"\n[/stats after turn {i}]")
            print(client.stats())

if __name__ == "__main__":
    main()