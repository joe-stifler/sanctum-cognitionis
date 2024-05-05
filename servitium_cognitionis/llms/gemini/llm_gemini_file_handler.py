from io import BytesIO
from vertexai.generative_models import Part, Image

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
        for filename, content, file_type in self.processed_files:
            if file_type == "image":
                img_byte_arr = BytesIO()
                content.save(img_byte_arr, format='PNG')  # You can change the format as needed
                img_bytes = img_byte_arr.getvalue()
                part = Image.from_bytes(img_bytes)
            elif file_type in ["json", "text", "code"]:
                part = Part.from_text(content)
            elif file_type == "pandas":
                part = Part.from_text(content.to_string())
            elif file_type == "pdf":
                # Assuming PDF handling is supported by Part.from_bytes
                part = Part.from_data(content, mime_type="application/pdf")
            else:
                raise Exception(f"Unsupported file format for Gemini conversion: {file_type}")

            filename_part = Part.from_text(f"File: `{filename}`\n")

            gemini_parts.extend([filename_part, part])
        return gemini_parts

    def create_llm_request(self, prompt):
        """
        Creates a complete LLM request with processed files and prompt.
        """
        gemini_parts = self.convert_to_gemini_parts()
        llm_request = gemini_parts + [Part.from_text(prompt)]
        return llm_request
