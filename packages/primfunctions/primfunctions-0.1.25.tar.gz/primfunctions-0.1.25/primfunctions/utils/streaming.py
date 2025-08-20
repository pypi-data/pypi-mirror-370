import re
import asyncio


# Language-specific punctuation sets for commonly used languages
PUNCTUATION_BY_LANGUAGE = {
    'en': ['.', '!', '?', '\n'],  # English
    'zh': ['.', '!', '?', '\n', '。', '！', '？', '，', '；', '：'],  # Chinese
    'ko': ['.', '!', '?', '\n', '。', '！', '？', '，', '；', '：'],  # Korean
    'ja': ['.', '!', '?', '\n', '。', '！', '？', '、', '；', '：'],  # Japanese (uses 、 instead of ，)
    'es': ['.', '!', '?', '\n', '¡', '¿'],  # Spanish (inverted punctuation)
    'fr': ['.', '!', '?', '\n', '«', '»'],  # French (guillemets)
    'it': ['.', '!', '?', '\n'],  # Italian
    'de': ['.', '!', '?', '\n'],  # German
    'hi': ['.', '!', '?', '\n', '।', '!', '?', '।', ';', ':'],  # Hindi
}

# Default punctuation marks (comprehensive set covering most languages)
DEFAULT_PUNCTUATION = ['.', '!', '?', '\n', '。', '！', '？', '，', '、', '；', '：', '¡', '¿', '«', '»', '।']


# Helper function to handle streaming response and chunking
async def stream_sentences(streaming_response, punctuation_marks=None, clean_text=True, min_sentence_length=6, language=None):
    """
    Streams OpenAI or Google Gemini response and yields complete sentences as strings.

    Args:
        streaming_response: The streaming response from OpenAI or Google Gemini
        punctuation_marks: Optional set of punctuation marks to use for sentence boundaries
                          Defaults to comprehensive set covering most languages
        clean_text: Whether to clean markdown and special characters for speech
                   Defaults to True
        min_sentence_length: Minimum length (in characters) for a sentence to be yielded
                           Defaults to 6 characters
        language: Optional language code to use language-specific punctuation
                 Supported: 'en', 'zh', 'ko', 'ja', 'es', 'fr', 'it', 'de'

    Yields:
        str: Complete sentences as they are formed
    """
    # Set punctuation marks based on language or use provided/default
    if language and language in PUNCTUATION_BY_LANGUAGE:
        punctuation_marks = PUNCTUATION_BY_LANGUAGE[language]
    elif punctuation_marks is None:
        punctuation_marks = DEFAULT_PUNCTUATION

    sentence_buffer = ""

    # Check if this is an async iterator (OpenAI) or sync iterator (Gemini)
    if hasattr(streaming_response, "__aiter__"):
        # OpenAI async streaming
        async for chunk in streaming_response:
            tool_calls = _extract_tool_calls_from_chunk(chunk)
            if tool_calls:
                yield {"tool_calls": tool_calls}

            content = _extract_content_from_chunk(chunk)
            sentence_buffer, complete_sentence = _update_sentence_buffer(
                content,
                sentence_buffer,
                punctuation_marks,
                clean_text,
                min_sentence_length,
            )

            if complete_sentence:
                yield {"content": complete_sentence}
    else:
        # Gemini sync streaming - wrap in async to prevent blocking
        for chunk in streaming_response:
            content = _extract_content_from_chunk(chunk)
            sentence_buffer, complete_sentence = _update_sentence_buffer(
                content,
                sentence_buffer,
                punctuation_marks,
                clean_text,
                min_sentence_length,
            )

            if complete_sentence:
                yield {"content": complete_sentence}

            # Yield control to prevent blocking the event loop
            await asyncio.sleep(0)

    # Handle any remaining text in buffer
    if sentence_buffer.strip():
        if clean_text:
            sentence_buffer = _clean_text_for_speech(sentence_buffer)

        if sentence_buffer:
            # Force yield remaining content regardless of minimum length
            # This ensures no content is lost, especially for short phrases without punctuation
            yield {"content": sentence_buffer}


def _extract_tool_calls_from_chunk(chunk):
    if hasattr(chunk, "choices") and chunk.choices:
        if hasattr(chunk.choices[0], "delta") and hasattr(
            chunk.choices[0].delta, "tool_calls"
        ):
            return chunk.choices[0].delta.tool_calls or ""
    return ""


def _extract_content_from_chunk(chunk):
    """
    Extract content from streaming chunk, supporting OpenAI and Direct Gemini API formats only.

    Args:
        chunk: The streaming chunk from either OpenAI or Google Gemini (direct API)

    Returns:
        str: The content text from the chunk, or empty string if no content
    """
    # OpenAI format: chunk.choices[0].delta.content
    if hasattr(chunk, "choices") and chunk.choices:
        if hasattr(chunk.choices[0], "delta") and hasattr(
            chunk.choices[0].delta, "content"
        ):
            return chunk.choices[0].delta.content or ""

    # Google Gemini Direct API format: chunk.text
    if hasattr(chunk, "text"):
        return chunk.text or ""

    return ""


def _update_sentence_buffer(
    content, sentence_buffer, punctuation_marks=None, clean_text=True, min_sentence_length=3
):
    if punctuation_marks is None:
        punctuation_marks = DEFAULT_PUNCTUATION

    if content:
        sentence_buffer += content

        # Check if we have a complete sentence (ends with punctuation)
        if any(punct in sentence_buffer for punct in punctuation_marks):
            # Find the last sentence boundary
            last_sentence_end = max(
                (sentence_buffer.rfind(punct) for punct in punctuation_marks),
                default=-1,
            )

            if last_sentence_end != -1:
                # Extract complete sentence
                complete_sentence = sentence_buffer[: last_sentence_end + 1]

                # Keep remaining text in buffer
                sentence_buffer = sentence_buffer[last_sentence_end + 1 :]

                # Clean and yield complete sentence
                if clean_text:
                    complete_sentence = _clean_text_for_speech(complete_sentence)

                if complete_sentence and len(complete_sentence.strip()) >= min_sentence_length:
                    return sentence_buffer, complete_sentence

    return sentence_buffer, None


def _clean_text_for_speech(text):
    """
    Clean text for better speech synthesis by removing/replacing problematic characters,
    and ensure the sentence contains at least one character (including Unicode).

    Args:
        text: The text to clean

    Returns:
        str: Cleaned text suitable for speech synthesis, or empty string if no meaningful chars
    """
    if not text:
        return text

    # Remove markdown formatting
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)  # **bold** -> bold
    text = re.sub(r"\*(.*?)\*", r"\1", text)  # *italic* -> italic
    text = re.sub(r"__(.*?)__", r"\1", text)  # __bold__ -> bold
    text = re.sub(r"_(.*?)_", r"\1", text)  # _italic_ -> italic
    text = re.sub(r"~~(.*?)~~", r"\1", text)  # ~~strikethrough~~ -> strikethrough
    text = re.sub(r"`(.*?)`", r"\1", text)  # `code` -> code

    # Remove markdown headers
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)  # # Header -> Header

    # Smart replacements - only replace symbols that are truly problematic for speech
    # and preserve context where possible
    
    # Handle currency symbols more intelligently
    text = re.sub(r'\$(\d+(?:\.\d{2})?)', r'$\1', text)  # Keep $200 as $200, don't replace
    
    # Handle percentages
    text = re.sub(r'(\d+)%', r'\1 percent', text)  # 50% -> 50 percent
    
    # Handle ampersands in common contexts
    text = re.sub(r'\b&\b', ' and ', text)  # A & B -> A and B
    
    # Handle mathematical operators only in mathematical contexts
    # Don't replace +, =, <, > in normal text as they might be part of natural language
    
    # Handle truly problematic symbols for speech
    replacements = {
        "|": " or ",  # A|B -> A or B
        "\\": " backslash ",  # Only when needed
        "/": " slash ",  # Only when needed
        "^": " caret ",  # Only when needed
        "~": " tilde ",  # Only when needed
    }

    for symbol, replacement in replacements.items():
        text = text.replace(symbol, replacement)

    # Remove brackets and their content (often contains technical info)
    # But be more selective - don't remove if it's part of natural language
    text = re.sub(r"\[.*?\]", "", text)  # [link text] ->
    text = re.sub(r"\{.*?\}", "", text)  # {code} ->

    # Clean up URLs (replace with "link") - this is actually good
    text = re.sub(r"https?://\S+", "link", text)
    text = re.sub(r"www\.\S+", "link", text)

    # Clean up email addresses - this is also good
    text = re.sub(r"\S+@\S+\.\S+", "email address", text)

    # Clean up multiple spaces and newlines
    text = re.sub(r"\s+", " ", text)  # Multiple spaces -> single space
    text = re.sub(r"\n+", ". ", text)  # Multiple newlines -> period space

    # Remove leading/trailing whitespace
    text = text.strip()

    # Ensure the sentence contains at least one meaningful character (including Unicode)
    # This includes letters, numbers, CJK characters, and Indic scripts
    if not re.search(r"[\w\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\uf900-\ufaff\u3300-\u33ff\ufe30-\ufe4f\u0900-\u097f\u0980-\u09ff\u0a00-\u0a7f\u0a80-\u0aff\u0b00-\u0b7f\u0b80-\u0bff\u0c00-\u0c7f\u0c80-\u0cff\u0d00-\u0d7f\u0d80-\u0dff\u0e00-\u0e7f\u0e80-\u0eff\u0f00-\u0fff]", text):
        return ""

    return text
