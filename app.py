from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip, AudioFileClip
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with a strong secret key
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # Max file size: 100MB

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def convert_mp4_to_mp3(input_path, output_path):
    """Convert MP4 to MP3."""
    video_clip = VideoFileClip(input_path)
    video_clip.audio.write_audiofile(output_path)
    video_clip.close()

def convert_mp3_to_mp4(input_path, output_path):
    """Convert MP3 to MP4 (creates a silent video)."""
    audio_clip = AudioFileClip(input_path)
    video_clip = VideoFileClip("static/silent.mp4").subclip(0, audio_clip.duration)
    video_clip = video_clip.set_audio(audio_clip)
    video_clip.write_videofile(output_path)
    video_clip.close()
    audio_clip.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Check if a file is uploaded
        if "file" not in request.files:
            flash("No file selected.")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected.")
            return redirect(request.url)

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)

        # Perform conversion
        if "to_mp3" in request.form:
            output_file = os.path.splitext(filename)[0] + ".mp3"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_file)
            convert_mp4_to_mp3(file_path, output_path)
        elif "to_mp4" in request.form:
            output_file = os.path.splitext(filename)[0] + ".mp4"
            output_path = os.path.join(app.config["UPLOAD_FOLDER"], output_file)
            convert_mp3_to_mp4(file_path, output_path)
        else:
            flash("Invalid conversion type.")
            return redirect(request.url)

        return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
