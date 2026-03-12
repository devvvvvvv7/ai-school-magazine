from flask import Flask, render_template, request
import os
from google import genai
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Gemini setup
API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    hint = request.form.get("hint")
    photos = request.files.getlist("photos")

    image_paths = []
    images_for_ai = []

    for photo in photos:
        if photo and photo.filename != "":
            path = os.path.join(app.config["UPLOAD_FOLDER"], photo.filename)
            photo.save(path)

            image_paths.append(path)

            img = Image.open(path)
            images_for_ai.append(img)

    prompt = f"""
You are a professional school magazine writer.

Write a magazine article about the following event.

Event: {hint}

Format exactly like this:

Title: <creative title>

Article:
Write 120-150 words describing the event, atmosphere, participation,
and why it was important for the school.
"""

    contents = [prompt] + images_for_ai

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )

        ai_text = response.text

    except Exception as e:

        ai_text = "AI service temporarily unavailable. Please try again later."

    title = ""
    article = ""

    if "Title:" in ai_text and "Article:" in ai_text:
        title = ai_text.split("Title:")[1].split("Article:")[0].strip()
        article = ai_text.split("Article:")[1].strip()
    else:
        article = ai_text

    return render_template(
        "magazine.html",
        title=title,
        article=article,
        images=image_paths
    )


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)

