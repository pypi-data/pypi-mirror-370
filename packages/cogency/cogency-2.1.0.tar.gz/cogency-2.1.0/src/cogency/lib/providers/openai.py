"""OpenAI provider - LLM and Embedder protocol implementation."""

from ...core.protocols import LLM, Embedder
from ..result import Err, Ok, Result


class OpenAI(LLM, Embedder):
    """OpenAI provider implementing LLM and Embedder protocols."""

    def __init__(
        self,
        api_key: str,
        llm_model: str = "gpt-4o-mini",
        embed_model: str = "text-embedding-3-small",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        self.api_key = api_key
        self.llm_model = llm_model
        self.embed_model = embed_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None  # Set by _get_client() or tests

    def _get_client(self):
        """Get or create OpenAI client."""
        if self.client is None:
            import openai

            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        return self.client

    async def generate(self, messages: list[dict]) -> Result[str, str]:
        """Generate text from conversation messages."""
        try:
            client = self._get_client()

            response = await client.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            return Ok(response.choices[0].message.content)

        except ImportError:
            return Err("Please install openai: pip install openai")
        except Exception as e:
            return Err(f"OpenAI LLM Error: {str(e)}")

    async def embed(self, texts: list[str]) -> Result[list[list[float]], str]:
        """Generate embeddings for input texts."""
        try:
            client = self._get_client()

            response = await client.embeddings.create(model=self.embed_model, input=texts)

            return Ok([item.embedding for item in response.data])

        except ImportError:
            return Err("Please install openai: pip install openai")
        except Exception as e:
            return Err(f"OpenAI Embedder Error: {str(e)}")


# Backward compatibility - keep existing functions
async def generate(prompt: str, model: str = "gpt-4o-mini") -> Result[str, str]:
    """Generate LLM response - pure function for backward compatibility."""
    from ..credentials import detect_api_key

    api_key = detect_api_key("openai")
    if not api_key:
        return Err("Please set OPENAI_API_KEY environment variable.")

    provider = OpenAI(api_key=api_key, llm_model=model)
    messages = [{"role": "user", "content": prompt}]
    return await provider.generate(messages)


async def embed(text: str) -> Result[list, str]:
    """Generate embedding - pure function for backward compatibility."""
    from ..credentials import detect_api_key

    api_key = detect_api_key("openai")
    if not api_key:
        return Err("Please set OPENAI_API_KEY environment variable.")

    provider = OpenAI(api_key=api_key)
    result = await provider.embed([text])
    if result.success:
        return Ok(result.unwrap()[0])  # Return single embedding
    return Err(result.error)
