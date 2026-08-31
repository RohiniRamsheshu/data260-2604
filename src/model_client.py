from langchain_ollama import ChatOllama

class ModelClient:
    def __init__(self, model="qwen2.5:3b"):
        self.llm = ChatOllama(model=model)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.turn_count = 0
        self.history = []

    def complete(self, messages, tools=None):
        prompt = "\n".join(m["content"] for m in messages)
        response = self.llm.invoke(prompt)

        input_tokens = response.usage_metadata.get("input_tokens", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0
        output_tokens = response.usage_metadata.get("output_tokens", 0) if hasattr(response, "usage_metadata") and response.usage_metadata else 0

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.turn_count += 1

        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": response.content})

        print(f"[Turn {self.turn_count}] input_tokens={input_tokens}, output_tokens={output_tokens}, total_tokens={input_tokens + output_tokens}")

        return response.content

    def stats(self):
        import json
        history_length = len(json.dumps(self.history))
        return {
            "turn_count": self.turn_count,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "history_length_chars": history_length
        }