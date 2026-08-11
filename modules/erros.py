import openai
import chromadb.errors


def mensagem_erro_ia(excecao: Exception) -> str:
    if isinstance(excecao, openai.AuthenticationError):
        return "Nao foi possivel autenticar com o servico de IA. Avise o responsavel pelo site."

    if isinstance(excecao, openai.RateLimitError):
        return "O servico de IA atingiu o limite de uso. Tente novamente em alguns minutos."

    if isinstance(excecao, (openai.APIConnectionError, openai.APITimeoutError)):
        return "Nao foi possivel conectar ao servico de IA. Verifique sua internet e tente novamente."

    if isinstance(excecao, chromadb.errors.ChromaError):
        return "A base de versiculos esta indisponivel no momento. Tente novamente mais tarde."

    if isinstance(excecao, openai.APIStatusError):
        return "O servico de IA esta indisponivel no momento. Tente novamente mais tarde."

    return "Nao foi possivel completar a busca. Tente novamente."
