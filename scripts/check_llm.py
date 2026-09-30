from app.agents.llm import get_llm
print(get_llm().invoke("ответь одним словом: привет").content)