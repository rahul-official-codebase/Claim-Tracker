from langchain_ollama import ChatOllama


class LLMService:

    def __init__(
        self,
        model_name: str = "gemma3:4b"
    ):

        self.llm = ChatOllama(
            model=model_name,
            temperature=0
        )

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = f"""
You are an insurance policy analysis assistant.

Answer the user's question ONLY using
the policy context provided below.

If the answer cannot be determined from
the provided context, say:
"Insufficient information in the policy."

Always explain the reasoning.

Include the relevant page number
when available.

POLICY CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

        response = self.llm.invoke(prompt)

        return response.content