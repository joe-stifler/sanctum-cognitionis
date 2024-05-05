from vertexai.generative_models import Part

def convert_to_gemini_parts(processed_files):
    """
    Converts processed files to Gemini Part objects with filenames.
    """
    gemini_parts = []
    for file in processed_files:
        part = Part.from_data(file.get_content_as_bytes(), mime_type=file.mime_type)

        filename_part = Part.from_text(f"File: `{file.name}`\n")

        gemini_parts.extend([filename_part, part])
    return gemini_parts

def create_llm_request(prompt, system_message, processed_files):
    """
    Creates a complete LLM request with processed files and prompt.
    """
    gemini_system_part = [Part.from_text(system_message), ] if system_message else []
    gemini_file_parts = convert_to_gemini_parts(processed_files)
    gemini_prompt_part = [Part.from_text(prompt)]
    return gemini_system_part + gemini_file_parts + gemini_prompt_part
