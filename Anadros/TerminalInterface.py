import os


class TerminalInterface:
    class Color:
        PINK = '\033[95m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        GREEN = '\033[92m'
        GOLDEN = '\033[93m'
        RED = '\033[91m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    @staticmethod
    def get_user_input(name="User", name_colour=Color.PINK, prompt_symbol="➤"):
        """Prompt the user for input."""
        # Set the TERM environment variable
        os.environ['TERM'] = 'xterm-256color'

        formatted_name = f"{TerminalInterface.Color.BOLD}{name}{TerminalInterface.Color.END}"
        prompt = f"{name_colour}{formatted_name}{TerminalInterface.Color.END} {prompt_symbol} "
        user_input = input(prompt)
        return user_input

    @staticmethod
    def bot_response(text, name="Bot", name_colour=Color.GREEN, text_colour=Color.END):
        """Display the bot's response."""
        formatted_name = f"{TerminalInterface.Color.BOLD}{name}{TerminalInterface.Color.END}"
        print(
            f"{name_colour}{formatted_name}{TerminalInterface.Color.END}: {text_colour}{text}{TerminalInterface.Color.END}")

    @staticmethod
    def clean_up(text):
        """Clean up the text by removing non-user and non-bot information."""
        cleaned_text = ""
        for line in text.split("\n"):
            if line.startswith("User:") or line.startswith("Bot:"):
                cleaned_text += line + "\n"
        return cleaned_text
