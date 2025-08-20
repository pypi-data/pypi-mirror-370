import re
import os

def parse_lua_file(filename: str) -> str:
    """
    Parse a Lua file for triple-dash documentation comments and function definitions.
    Returns formatted GitBook-ready Markdown.
    """
    basename = os.path.basename(filename)
    docs = [f"# Documentation for `{basename}`\n"]
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    comment_block = []
    for i, line in enumerate(lines):
        if line.strip().startswith('---'):
            comment_block.append(line.strip().lstrip('---').strip())
        elif comment_block and re.match(r"function\s+\w+\s*\(", line.strip()):
            func_line = line.strip()
            func_match = re.match(r"function\s+(\w+)\s*\((.*)\)", func_line)
            if func_match:
                func_name = func_match.group(1)
                params = func_match.group(2)
            else:
                func_name = "Unknown"
                params = ""
            docs.append(f"## 🛠️ {comment_block[0] if comment_block else func_name}\n")
            docs.append(f"**Function:** `{func_name}`\n")
            if len(comment_block) > 1:
                docs.append(f"**Author:** {comment_block[1]}\n")
            if len(comment_block) > 2:
                docs.append(f"**Purpose:** {comment_block[2]}\n")
            if len(comment_block) > 3:
                docs.append(f"**Params:** {comment_block[3]}\n")
            else:
                docs.append(f"**Params:** {params}\n")
            docs.append("\n---\n")
            comment_block = []
        else:
            comment_block = []
    return "\n".join(docs)