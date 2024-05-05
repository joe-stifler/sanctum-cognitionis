from vertexai.generative_models import Part

class GeminiFileHandler:
    """
    Converts and encapsulates files into Gemini 1.5 Vertex AI compatible format
    with filename association.
    """

    def __init__(self, processed_files):
        self.processed_files = processed_files

    def convert_to_gemini_parts(self):
        """
        Converts processed files to Gemini Part objects with filenames.
        """
        gemini_parts = []
        for file in self.processed_files:
            part = Part.from_data(file.get_content_as_bytes(), mime_type=file.mime_type)

            # elif file_type in ["json", "text", "code"]:
            #     part = Part.from_text(content)
            # elif file_type == "pandas":
            #     part = Part.from_text(content.to_string())
            # elif file_type == "pdf":
            #     # Assuming PDF handling is supported by Part.from_bytes
            #     part = Part.from_data(content, mime_type="application/pdf")
            # else:
            #     raise Exception(f"Unsupported file format for Gemini conversion: {file_type}")

            filename_part = Part.from_text(f"File: `{file.name}`\n")

            gemini_parts.extend([filename_part, part])
        return gemini_parts

    def create_llm_request(self, prompt):
        """
        Creates a complete LLM request with processed files and prompt.
        """
        gemini_parts = self.convert_to_gemini_parts()
        llm_request = gemini_parts + [Part.from_text(prompt)]
        return llm_request
