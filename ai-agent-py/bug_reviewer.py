from flask import Flask, request, jsonify
import subprocess
import textwrap
import re
import os
from pathlib import Path

app = Flask(__name__)

# ------------- CONFIG -------------
MODEL = "mistral"
# Where to save generated tests relative to ai-agent-py folder
DEFAULT_TEST_SAVE_DIR = Path("../app/src/test/java/com/ai_agent/app/reviewed")
# ----------------------------------

def run_ollama(model: str, prompt: str) -> str:
    """
    Run Ollama and return stdout. Raises CalledProcessError on failure.
    """
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout or result.stderr or ""

def strip_code_fences(text: str) -> str:
    """
    Remove Markdown code fences and leading explanation lines.
    """
    # Remove triple backticks and language tags
    text = re.sub(r"```(?:java)?", "", text, flags=re.IGNORECASE)
    # Remove common explanation prefixes lines like "Explanation:" etc.
    lines = []
    for line in text.splitlines():
        if re.match(r'^\s*(explain|note|output|analysis)\b', line.strip(), flags=re.I):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def extract_test_class_name(java_text: str, source_filename: str) -> str:
    """
    Try to determine the test class name. Fallback to <SourceName>Test.
    """
    # Look for `class XTest` or `public class XTest`
    m = re.search(r'\bclass\s+([A-Za-z0-9_]+Test)\b', java_text)
    if m:
        return m.group(1)
    # fallback: derive from source file
    base = Path(source_filename).stem
    name = base.replace(".java", "")
    # ensure proper Test suffix
    if name.endswith("Service") or name.endswith("Controller") or name.endswith("Repository"):
        return name + "Test"
    return (name + "Test").replace("-", "_")

def ensure_package_and_imports(test_code: str, package: str = "com.ai_agent.app.reviewed") -> str:
    """
    Ensure there's a package declaration and necessary imports.
    If package exists in AI output, keep it.
    """
    code = test_code.strip()
    if not re.search(r'^\s*package\s+[a-zA-Z0-9_.]+;', code, flags=re.M):
        header = f"package {package};\n\n"
    else:
        header = ""
    # Ensure essential imports exist (don't duplicate if present)
    imports = []
    needed = [
        "org.junit.jupiter.api.BeforeEach",
        "org.junit.jupiter.api.Test",
        "org.mockito.MockitoAnnotations",
        "org.mockito.InjectMocks",
        "org.mockito.Mock",
        "org.mockito.Mockito"
    ]
    for imp in needed:
        if re.search(rf'^\s*import\s+{re.escape(imp)}\b', code, flags=re.M):
            continue
        imports.append(f"import {imp};")
    imports_block = "\n".join(imports)
    # If imports_block empty, avoid extra blank line
    if imports_block:
        header += imports_block + "\n\n"
    return header + code

def pretty_indent(code: str) -> str:
    """
    Basic normalization: remove mixed tabs, trim trailing spaces.
    (We avoid heavy formatting tools to keep offline.)
    """
    lines = [ln.rstrip() for ln in code.splitlines()]
    # Remove excessive blank lines (max 2)
    out = []
    blank = 0
    for ln in lines:
        if ln.strip() == "":
            blank += 1
            if blank <= 2:
                out.append(ln)
        else:
            blank = 0
            out.append(ln)
    return "\n".join(out).strip() + "\n"

def save_test_file(test_code: str, test_class_name: str, save_dir: Path) -> Path:
    save_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{test_class_name}.java"
    path = save_dir / file_name
    path.write_text(test_code, encoding="utf-8")
    return path

# ---------------- End utilities ----------------

@app.route("/generate-tests", methods=["POST"])
def generate_tests():
    """
    Accept Java source code in request body (text/plain).
    Calls Ollama with a strong JUnit+Mockito prompt, cleans the response,
    ensures package/imports, and saves the output as a formatted .java test file.
    """
    try:
        source_code = request.data.decode("utf-8")
        if not source_code.strip():
            return jsonify({"error": "No source code received"}), 400

        # Build strong prompt instructing to output ONLY Java test class (no markdown)
        prompt = textwrap.dedent(f"""
            You are a Senior Java SDET Engineer. Generate a complete, compilable JUnit 5 test class
            using Mockito for the following Java class. Follow these rules strictly:
            - Output ONLY the Java test source code (no explanations, no markdown, no backticks).
            - Include package declaration `package com.ai_agent.app.reviewed;` unless the source requires otherwise.
            - Include necessary imports, @BeforeEach, @Test annotations, and use Arrange-Act-Assert pattern.
            - Name the test class properly, ending with 'Test'.
            - Mock dependencies (repositories/services/clients) with Mockito and verify important interactions.
            - Keep code clean and well-indented.

            Java Source:
            {source_code[:5000]}
        """)

        raw = run_ollama(MODEL, prompt)
        cleaned = strip_code_fences(raw)

        # Determine test class name
        test_class = extract_test_class_name(cleaned, "Source.java")

        # If AI returned only method bodies or missing imports, wrap/ensure package+imports
        final_code = ensure_package_and_imports(cleaned, package="com.ai_agent.app.reviewed")
        final_code = pretty_indent(final_code)

        # If no class declaration detected (AI returned only methods), attempt to wrap in a generated test class
        if not re.search(r'\bclass\s+[A-Za-z0-9_]+Test\b', final_code):
            # create a simple test class wrapper
            wrapper = textwrap.dedent(f"""
                package com.ai_agent.app.reviewed;

                import org.junit.jupiter.api.BeforeEach;
                import org.junit.jupiter.api.Test;
                import org.mockito.InjectMocks;
                import org.mockito.Mock;
                import org.mockito.MockitoAnnotations;

                import static org.mockito.Mockito.*;
                import static org.junit.jupiter.api.Assertions.*;

                public class {test_class} {{

                    @BeforeEach
                    void setUp() {{
                        MockitoAnnotations.openMocks(this);
                    }}

                    // AI-generated tests (wrapped)
                }}

            """)
            # append AI content inside comment block for developer to move/test manually
            final_code = wrapper + "\n/* AI-generated test bodies (below) */\n" + cleaned + "\n"

        # Save file
        saved_path = save_test_file(final_code, test_class, DEFAULT_TEST_SAVE_DIR)

        return jsonify({
            "generated_tests": final_code,
            "saved_path": str(saved_path)
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Ollama execution failed", "details": e.stderr}), 500
    except Exception as exc:
        return jsonify({"error": "Unexpected error", "details": str(exc)}), 500


if __name__ == "__main__":
    print("🤖 AI Agent Flask service (testgen) starting on port 5000...")
    app.run(host="0.0.0.0", port=5000)