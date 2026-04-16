from pprint import pp

from flask import Flask, render_template, request, jsonify
from google import genai
import base64
from PIL import Image
import io

app = Flask(__name__)

# ── Multiple API Keys ──────────────────────────────────────
import os

import os

API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]

PROMPT = """You are an AI assistant built into smart glasses for visually impaired people.
Look at this image and do the following:

1. If there is TEXT:
   - Read it clearly
   - If it's English → translate to Arabic
   - If it's Arabic → translate to English
   - If the user asks for a specific language → translate to that language
   - Always say: "Original: ..." then "Translation: ..."

2. If there is an OBJECT (no text):
   - Describe it clearly (what it is, color, shape, size)
   - Respond in Arabic

3. If there is BOTH text and object:
   - Describe the object first
   - Then read and translate the text

4. Keep response SHORT and CLEAR.
5. IGNORE any UI text like "SPACE: Capture" or "ESC: Exit"."""


def analyze_image(img, custom_prompt=None):
    for key in API_KEYS:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=[custom_prompt or PROMPT, img]
            )
            return response.text.strip()
        except Exception as e:
            last_error = str(e)
            continue
    return f"⚠ Error: {last_error}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    image_data = data['image'].split(',')[1]
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))
    result = analyze_image(img)
    return jsonify({'result': result})


@app.route('/analyze_prompt', methods=['POST'])
def analyze_prompt():
    data = request.json
    image_data = data['image'].split(',')[1]
    user_prompt = data['prompt']
    img = Image.open(io.BytesIO(base64.b64decode(image_data)))

    custom_prompt = f"""You are an AI assistant in smart glasses.
The user says: '{user_prompt}'
Based on the image, respond to the user's request.
If the user asks to translate → translate to the language they specified.
If no language specified → translate to the opposite language (Arabic↔English).
Be short and clear."""

    result = analyze_image(img, custom_prompt)
    return jsonify({'result': result})

if __name__ == '__main__':
    import os

    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))