from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route("/review", methods=["POST"])
def review_code():
    code = request.data.decode("utf-8")
    print("🧠 Reviewing code snippet...")

    # 🧩 New: Structured, more powerful prompt for Ollama
    prompt = f"""
You are a senior Java backend engineer.
Analyze the following Java source code for:
- Bugs or logical errors
- Missing null checks or exception handling
- Code smells or bad practices (e.g., use of System.out.println)
- SOLID principle violations
- Optimization suggestions

Then output two sections:
🧩 REVIEW COMMENTS:
(list of bullet points describing issues and fixes)

🚀 FIXED & OPTIMIZED CODE:
(complete improved Java class with fixes applied)

Java Source Code:
{code[:5000]}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True, text=True, check=True
        )
        output = result.stdout.strip()
        return jsonify({"review": output})

    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.stderr}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)