from openai import AsyncOpenAI, OpenAI

from django_ai_agent.models import Document


class ContextualizeChunkMixin:
    @classmethod
    def _prepare_content(cls, document: Document, index: int, chunk: str):
        openai_client = OpenAI()

        DOCUMENT_CONTEXT_PROMPT = """
        <document>
        {doc_content}
        </document>
        """

        CHUNK_CONTEXT_PROMPT = """
        Here is the chunk we want to situate within the whole document
        <chunk>
        {chunk_content}
        </chunk>

        Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk.
        Answer only with the succinct context and nothing else.
        """

        response = openai_client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": DOCUMENT_CONTEXT_PROMPT.format(doc_content=document.content),
                        },
                        {
                            "type": "input_text",
                            "text": CHUNK_CONTEXT_PROMPT.format(chunk_content=chunk),
                        },
                    ],
                }
            ],
            text={"format": {"type": "text"}},
            temperature=0.0,
            max_output_tokens=1024,
            store=True,
        )

        return response.output[0].text
