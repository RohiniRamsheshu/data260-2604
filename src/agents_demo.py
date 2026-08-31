from langchain_ollama import ChatOllama
import json

llm = ChatOllama(model="qwen2.5:3b", temperature=0.7)

def planner(title, content):
    prompt = f"""You are a Planner agent. Given a title and content, propose exactly 3 topical tags and a one-sentence summary (max 25 words).
Respond ONLY in valid JSON with keys "tags" (list of 3 strings) and "summary" (string).

Title: {title}
Content: {content}
"""
    response = llm.invoke(prompt)
    return response.content

def reviewer(planner_output):
    prompt = f"""You are a Reviewer agent. Review this draft output for quality and correctness.
If it's good, return it unchanged. If not, fix it. Respond ONLY in the same valid JSON format with keys "tags" and "summary".

Draft: {planner_output}
"""
    response = llm.invoke(prompt)
    return response.content

def finalize(reviewer_output):
    try:
        parsed = json.loads(reviewer_output)
    except json.JSONDecodeError:
        parsed = {"tags": [], "summary": "Error: could not parse model output"}
    return json.dumps(parsed, indent=2)

if __name__ == "__main__":
    title = "Prototype pollution in lodash"
    content = "A vulnerability in lodash allows attackers to modify object prototypes, potentially leading to denial of service or remote code execution in applications that merge untrusted user input."

    print("=== Planner Output ===")
    planner_result = planner(title, content)
    print(planner_result)

    print("\n=== Reviewer Output ===")
    reviewer_result = reviewer(planner_result)
    print(reviewer_result)

    print("\n=== Finalized Output ===")
    final_result = finalize(reviewer_result)
    print(final_result)