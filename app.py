from flask import Flask, render_template, request
import os
from google import genai
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Gemini setup
client = genai.Client(api_key="AIzaSyDwTMgqlPSlyoXgDL7FH_9cC5v_46TlZpQ")


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
Write a school magazine article in simple English.

Event description: {hint}

Rules:
- Use simple language suitable for school students.
- Do NOT invent names or titles.
- Use the names exactly as given in the event description.
- Avoid difficult vocabulary.
- Write in clear paragraphs.

Format strictly like this:

Title: A short and clear title related to the event.

Article:
Write 100–120 words in 2 small paragraphs describing:
- what happened in the event
- student participation
- message of the event
"""

    contents = [prompt] + images_for_ai

    ai_failed = False
    title = ""
    article = ""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )

        ai_text = response.text

        if "Title:" in ai_text and "Article:" in ai_text:
            title = ai_text.split("Title:")[1].split("Article:")[0].strip()
            article = ai_text.split("Article:")[1].strip()

    except Exception as e:

        ai_failed = True

    return render_template(
        "magazine.html",
        title=title,
        article=article,
        images=image_paths,
        ai_failed=ai_failed
    )


@app.route("/manual", methods=["POST"])
def manual():

    title = request.form.get("title")
    article = request.form.get("article")
    images = request.form.getlist("images")

    return render_template(
        "magazine.html",
        title=title,
        article=article,
        images=images,
        ai_failed=False
    )


if __name__ == "__main__":
    app.run(debug=True)
