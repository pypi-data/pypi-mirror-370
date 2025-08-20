import typer
from pathlib import Path
import os
import requests
from .menu import main_menu

app = typer.Typer()

@app.command()
def menu():
    """
    Launch the interactive in-terminal menu for Doccsy.
    """
    main_menu()

from .parser_lua import parse_lua_file

# Add imports for newly supported languages
try:
    from .parser_js import parse_js_file
except ImportError:
    parse_js_file = None

try:
    from .parser_php import parse_php_file
except ImportError:
    parse_php_file = None

def write_markdown(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def ai_explain_code(code_text, model="llama3"):
    """
    Call Ollama local API to get a detailed explanation for a code snippet.
    """
    prompt = (
        "Read the following function and its documentation comments. "
        "Explain in greater detail how to utilize this function, with a practical example if possible.\n\n"
        f"{code_text}\n"
    )
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"(AI explanation failed: {e})"

@app.command()
def generate(
    source: str = typer.Argument(..., help="Source file or directory"),
    language: str = typer.Option("lua", "--language", "-l", help="Source language (lua/js/php)"),
    output_dir: str = typer.Option("docs", "--output-dir", "-o", help="Output directory"),
    explain: bool = typer.Option(False, "--explain", help="Add AI-generated explanations using Ollama"),
    model: str = typer.Option("mistral", "--model", help="Ollama model to use for explanations (default: mistral)")
):
    """
    Generate GitBook-ready Markdown documentation from code comments in a file or folder.
    Optionally add AI-powered usage explanations (requires Ollama running locally).
    """
    source_path = Path(source).expanduser().resolve()
    output_dir = Path(output_dir).expanduser().resolve()
    markdown_files = []

    # Select parser and file extension
    if language == "lua":
        parser_func = parse_lua_file
        ext = ".lua"
    elif language == "js":
        if not parse_js_file:
            typer.echo("JS support not installed.")
            raise typer.Exit(code=1)
        parser_func = parse_js_file
        ext = ".js"
    elif language == "php":
        if not parse_php_file:
            typer.echo("PHP support not installed.")
            raise typer.Exit(code=1)
        parser_func = parse_php_file
        ext = ".php"
    else:
        typer.echo("Language not supported. Supported: lua, js, php")
        raise typer.Exit(code=1)

    def add_ai_explanation(docs, code_path):
        """Inject AI explanation section at the end of each doc file."""
        try:
            with open(code_path, "r", encoding="utf-8") as f:
                code_content = f.read()
            ai_text = ai_explain_code(code_content, model=model)
            docs += f"\n### AI Explanation\n{ai_text}\n"
        except Exception as e:
            docs += f"\n### AI Explanation\n(AI explanation failed: {e})\n"
        return docs

    if source_path.is_file():
        docs = parser_func(str(source_path))
        if explain:
            docs = add_ai_explanation(docs, str(source_path))
        out_file = output_dir / (source_path.with_suffix('.md').name)
        write_markdown(str(out_file), docs)
        markdown_files.append(out_file)
    elif source_path.is_dir():
        for file in source_path.rglob(f"*{ext}"):
            docs = parser_func(str(file))
            if explain:
                docs = add_ai_explanation(docs, str(file))
            rel_path = file.relative_to(source_path).with_suffix('.md')
            out_file = output_dir / rel_path
            write_markdown(str(out_file), docs)
            markdown_files.append(out_file)
    else:
        typer.echo("Source path not found.")
        raise typer.Exit(code=1)

    # Generate SUMMARY.md for GitBook navigation
    summary_lines = ["# Summary\n"]
    for md_file in markdown_files:
        rel_md = md_file.relative_to(output_dir)
        title = rel_md.stem.replace("_", " ").title()
        icon = "📄"
        summary_lines.append(f"* {icon} [{title}]({rel_md.as_posix()})")
    write_markdown(str(output_dir / "SUMMARY.md"), "\n".join(summary_lines))
    typer.echo(f"Documentation generated in {output_dir}")

if __name__ == "__main__":
    app()