from .llm_base_model import LLMBaseModel

from enum import Enum

from vertexai import generative_models
from vertexai.generative_models import GenerativeModel, FinishReason

class LLMGeminiBaseModel(LLMBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._model_instance = None

    def initialize_model(self, system_instruction=[]):
        self._model_instance = GenerativeModel(
            model_name=self.name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens
            },
            system_instruction=system_instruction,
            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            }
        )

    def start_chat(self):
        if self._model_instance is None:
            raise ValueError("Model has not been initialized. Call initialize_model() first")
        return self._model_instance.start_chat(response_validation=False)

    def process_ai_response_stream(self, responses):
        new_ai_message_args = {}

        try:
            for index, response in enumerate(responses):
                new_ai_message_args = {
                    "index": index,
                    "usage_metadata": str(response.usage_metadata),
                    "candidates": [str(response.candidates) for candidate in response.candidates],
                    "prompt_feedback": str(response.prompt_feedback),
                }

                context_error = ":yellow[Tente reenviar a mensagem novamente]"

                if len(response.candidates) == 0:
                    text_message = f":red[Erro: a resposta gerado pela está vazia. {context_error}]"
                    yield text_message, new_ai_message_args
                    continue

                candidate = response.candidates[0]
                
                new_ai_message_args.update({
                    "candidate_index": candidate.index,
                    "candidate_content": candidate.content if hasattr(candidate, "content") else None,
                    "candidate_finish_reason": candidate.finish_reason,
                    "candidate_safety_ratings": candidate.safety_ratings,
                    "candidate_function_calls": candidate.function_calls,
                    "candidate_finish_message": candidate.finish_message,
                    "candidate_citation_metadata": candidate.citation_metadata,
                })

                text_message = candidate.text if hasattr(candidate, "text") else ""
                print("Ai finish reason:", candidate.finish_reason)

                if not hasattr(candidate, "finish_reason") or candidate.finish_reason is None:
                    pass
                elif candidate.finish_reason == FinishReason.STOP:
                    text_message += ""
                elif candidate.finish_reason == FinishReason.MAX_TOKENS:
                    text_message += "...\n\n:yellow[Continue a conversa para mais detalhes]"
                elif candidate.finish_reason == FinishReason.SAFETY:
                    text_message += "\n\n:red[Erro: A resposta contém conteúdo inapropriado.]\n\n"
                    text_message += ":yellow[Tente reformular a mensagem e enviar novamente]"
                elif candidate.finish_reason == FinishReason.RECITATION:
                    text_message += "\n\n:red[Erro: A resposta contém citações não autorizadas.]\n\n"
                    text_message += ":yellow[Tente reformular a mensagem e enviar novamente]"
                yield text_message, new_ai_message_args
                print("\n\n-----------\n\n")
        except Exception as e:
            text_message = f":red[Erro ao processar a mensagem: {e}]"
            yield text_message, new_ai_message_args
            print(f"Erro ao enviar mensagem para a IA: {e}")

class LLMGeminiModel1_5Pro(LLMGeminiBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.5-pro-preview-0409",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModel1_0Pro002(LLMGeminiBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-1.0-pro-002",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModelExperimental(LLMGeminiBaseModel):
    def __init__(self, temperature=0.1, max_output_tokens=8192):
        super().__init__(
            model_name="gemini-experimental",
            temperature=temperature,
            temperature_range=(0.0, 2.0),
            max_output_tokens=max_output_tokens,
            output_tokens_range=(1, 8192)
        )

class LLMGeminiModels(Enum):
    GEMINI_1_5_PRO = LLMGeminiModel1_5Pro()
    GEMINI_1_0_PRO_002 = LLMGeminiModel1_0Pro002()
    GEMINI_EXPERIMENTAL = LLMGeminiModelExperimental()

    def __str__(self):
        return self.value.name
