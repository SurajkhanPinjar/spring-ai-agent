from flask import Flask, request, jsonify
import subprocess
import textwrap
import re
import os
from pathlib import Path

app = Flask(__name__)

# ------------- CONFIG -------------
MODEL = "mistral"
# 💾 Save generated test files inside your correct Spring Boot test directory
DEFAULT_TEST_SAVE_DIR = Path("../app/src/test/java/com/ai_agent/app")
# ----------------------------------

def run_ollama(model: str, prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout or result.stderr or ""

def strip_code_fences(text: str) -> str:
    text = re.sub(r"```(?:java)?", "", text, flags=re.IGNORECASE)
    lines = []
    for line in text.splitlines():
        if re.match(r'^\s*(explain|note|output|analysis)\b', line.strip(), flags=re.I):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def extract_test_class_name(java_text: str, source_filename: str) -> str:
    m = re.search(r'\bclass\s+([A-Za-z0-9_]+Test)\b', java_text)
    if m:
        return m.group(1)
    base = Path(source_filename).stem
    name = base.replace(".java", "")
    if name.endswith(("Service", "Controller", "Repository")):
        return name + "Test"
    return (name + "Test").replace("-", "_")

def ensure_package_and_imports(test_code: str, package: str = "com.ai_agent.app") -> str:
    code = test_code.strip()
    if not re.search(r'^\s*package\s+[a-zA-Z0-9_.]+;', code, flags=re.M):
        header = f"package {package};\n\n"
    else:
        header = ""
    imports = []
    needed = [
        "org.junit.jupiter.api.BeforeEach",
        "org.junit.jupiter.api.Test",
        "org.mockito.MockitoAnnotations",
        "org.mockito.InjectMocks",
        "org.mockito.Mock",
        "org.mockito.Mockito",
        "static org.mockito.Mockito.*",
        "static org.junit.jupiter.api.Assertions.*"
    ]
    for imp in needed:
        if re.search(rf'^\s*import\s+{re.escape(imp)}\b', code, flags=re.M):
            continue
        imports.append(f"import {imp};")
    imports_block = "\n".join(imports)
    if imports_block:
        header += imports_block + "\n\n"
    return header + code

def pretty_indent(code: str) -> str:
    lines = [ln.rstrip() for ln in code.splitlines()]
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

# ---------------- Flask API ----------------

@app.route("/generate-tests", methods=["POST"])
def generate_tests():
    """
    Accept Java source code and generate a professional-grade test class.
    """
    try:
        source_code = request.data.decode("utf-8")
        if not source_code.strip():
            return jsonify({"error": "No source code received"}), 400

        # 🧩 Enhanced High-Quality Prompt for JUnit + Mockito generation
        prompt = textwrap.dedent(f"""
        You are a **Principal QA Automation Engineer** with 12+ years of experience designing test strategies,
        writing enterprise-grade JUnit 5 tests using Mockito, and ensuring 90%+ coverage.

        Your job is to analyze the following Java class and output a **complete, compilable, and realistic**
        JUnit 5 test class.

        ---
        ### 🧠 TEST STRATEGY
        - Identify core methods, branches, and exception paths.
        - Mock all external dependencies (repositories, services, clients).
        - Follow Arrange–Act–Assert format.
        - Use `@Mock`, `@InjectMocks`, and `MockitoAnnotations.openMocks(this)` in `@BeforeEach`.

        ---
        ### 🧪 TEST OUTPUT RULES
        - Output ONLY Java code (no markdown or explanations).
        - Start with `package com.ai_agent.app;`
        - Include necessary imports.
        - Use descriptive test method names.
        - Cover both positive and negative scenarios.
        - Verify mocks using `verify()`.
        - Follow clean code standards and SOLID test principles.

        ---
        ### 🚀 INPUT CODE:
        {source_code[:5000]}
        """)

        raw = run_ollama(MODEL, prompt)
        cleaned = strip_code_fences(raw)
        test_class = extract_test_class_name(cleaned, "Source.java")

        final_code = ensure_package_and_imports(cleaned, package="com.ai_agent.app")
        final_code = pretty_indent(final_code)

        if not re.search(r'\bclass\s+[A-Za-z0-9_]+Test\b', final_code):
            wrapper = textwrap.dedent(f"""
                package com.ai_agent.app;

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
            final_code = wrapper + "\n/* AI-generated test bodies (below) */\n" + cleaned + "\n"

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