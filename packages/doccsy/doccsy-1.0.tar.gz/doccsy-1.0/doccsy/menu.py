import questionary
from pathlib import Path
import os
import sys

def choose_source():
    while True:
        source = questionary.path(
            "🔍 Source file or directory to document?",
            default=str(Path.cwd())
        ).ask()
        if source is None:
            if questionary.confirm("Exit Doccsy?").ask():
                sys.exit(0)
            continue
        try: 
            source_path = Path(os.path.normpath(source)).resolve()
        except Exception:
            source_path = Path(source)
        if source_path.exists():
            return str(source_path)
        print(f"❌ Path '{source}' not found. Try again.")

def choose_language():
    return questionary.select(
        "🌐 What language is your code?",
        choices=[
            "lua",
            "js",
            "php",
            "Go Back"
        ]
    ).ask()

def choose_output_dir():
    output_dir = questionary.text(
        "📁 Output directory for markdown docs?",
        default="docs"
    ).ask()
    return output_dir

def ask_explanation():
    return questionary.confirm(
        "✨ Add AI-generated explanations to docs?",
        default=True
    ).ask()

def choose_model():
    return questionary.text(
        "🤖 Ollama model to use for explanations (e.g. mistral, llama3)?",
        default="mistral"
    ).ask()

def main_menu():
    print("\n🌟 Welcome to Doccsy! 🌟\n")
    print("Generate GitBook-ready docs from comments in your code.\n")
    while True:
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Generate documentation",
                "Exit"
            ]
        ).ask()
        if action == "Exit":
            print("\n👋 Goodbye!\n")
            sys.exit(0)

        # Start wizard
        source = choose_source()
        while True:
            language = choose_language()
            if language == "Go Back":
                source = choose_source()
                continue
            break
        output_dir = choose_output_dir()
        explain = ask_explanation()
        model = choose_model() if explain else None

        print("\n🚀 Generating documentation...\n")
        try:
            from .doccsy import generate  # Avoid circular import
            generate(
                source=source,
                language=language,
                output_dir=output_dir,
                explain=explain,
                model=model
            )
            print(f"\n✅ Documentation generated in '{output_dir}'!\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
        
        if not questionary.confirm("Do you want to generate another documentation?").ask():
            print("\n👋 Thanks for using Doccsy!\n")
            break

if __name__ == "__main__":
    main_menu()