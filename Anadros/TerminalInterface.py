import re


class TerminalInterface:
    @staticmethod
    def get_user_input(prompt_symbol="➤"):
        """Prompt the user for input."""
        return input(f"{prompt_symbol} ")

    @staticmethod
    def bot_response(text):
        """Display the bot's response."""
        print(text)

    @staticmethod
    def clean_up(text):
        """Clean up the text by removing ANSI escape codes and non-user/bot information."""
        # Remove ANSI escape codes
        text_no_ansi = re.sub(r'\x1b\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]', '', text)
        # Remove specific sequence
        text_no_ansi = text_no_ansi.replace('\x1B[3J\x1B[H\x1B[2J', '')
        cleaned_text = ""
        for line in text_no_ansi.split("\n"):
            if line.startswith("User:") or line.startswith("Bot:"):
                cleaned_text += line + "\n"
        return cleaned_text
