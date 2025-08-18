

class PrintUtil:
    """
    Utility class for validator-related functions.
    """

    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitizes the text for printing by removing sensitive information.
        :param text: The text to sanitize.
        :return: Sanitized text.
        """
        # Implement sanitization logic here if needed
        safe_text = str(text).replace("\n", "\\n").replace("\r", "\\r")[:200]
        return safe_text
