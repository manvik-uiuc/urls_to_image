from flask import Flask, request, render_template, send_file, redirect, url_for, flash
import requests
from pathlib import Path
import os
import uuid
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'

save_directory = Path("downloaded_images")
save_directory.mkdir(parents=True, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_images():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash("No selected file")
        return redirect(url_for('index'))

    if file and file.filename.endswith('.csv'):
        try:
            df = pd.read_csv(file)
        except Exception as e:
            flash(f"Error reading CSV file: {e}")
            return redirect(url_for('index'))

        if 'image_url' not in df.columns:
            flash("CSV file must contain a column named 'image_url'")
            return redirect(url_for('index'))

        downloaded_files = []

        for image_url in df['image_url']:
            try:
                img_data = requests.get(image_url).content
                filename = f"{uuid.uuid4()}.jpg"
                file_path = save_directory / filename

                with open(file_path, 'wb') as handler:
                    handler.write(img_data)
                downloaded_files.append(file_path)
            except Exception as e:
                flash(f"Failed to download image from {image_url}: {e}")
                continue

        if downloaded_files:
            return render_template('download.html', files=downloaded_files)

        flash("No images were downloaded")
        return redirect(url_for('index'))

    flash("Invalid file format, please upload a CSV file")
    return redirect(url_for('index'))

@app.route('/files/<filename>')
def files(filename):
    return send_file(save_directory / filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
