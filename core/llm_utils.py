import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Gemini LLM utility (inlined from llm_utils.py)
class LoggingGeminiLLM:
    def __init__(self, llms, model_names):
        self.llms = llms
        self.model_names = model_names
        self.llm = llms[0].with_fallbacks(llms[1:])

    def invoke(self, *args, **kwargs):
        for i, llm in enumerate(self.llms):
            try:
                print(f"[Gemini LLM] Trying model: {self.model_names[i]}")
                result = llm.invoke(*args, **kwargs)
                print(f"[Gemini LLM] Model succeeded: {self.model_names[i]}")
                return result
            except Exception as e:
                print(f"[Gemini LLM] Model failed: {self.model_names[i]} | Error: {e}")
        raise RuntimeError("All Gemini fallback models failed.")

    async def ainvoke(self, *args, **kwargs):
        for i, llm in enumerate(self.llms):
            try:
                print(f"[Gemini LLM] Trying model: {self.model_names[i]}")
                result = await llm.ainvoke(*args, **kwargs)
                print(f"[Gemini LLM] Model succeeded: {self.model_names[i]}")
                return result
            except Exception as e:
                print(f"[Gemini LLM] Model failed: {self.model_names[i]} | Error: {e}")
        raise RuntimeError("All Gemini fallback models failed.")

    def bind_tools(self, *args, **kwargs):
        return self.llm.bind_tools(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.llm, name)

def get_gemini_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-2.5-flash-lite-preview-06-17",
    ]
    llms = [ChatGoogleGenerativeAI(model=m, temperature=0.2, max_retries=3, google_api_key=api_key) for m in models]
    return LoggingGeminiLLM(llms, models) 