from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['WATERMARK'] = 'static/watermark.png'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def add_watermark(image_path, watermark_path):
    base_image = Image.open(image_path)
    watermark = Image.open(watermark_path).convert("RGBA")

    base_width, base_height = base_image.size
    watermark_width, watermark_height = watermark.size

    # Redimensiona a marca d'água para ter a mesma largura da imagem base
    new_watermark_height = int(base_width * watermark_height / watermark_width)
    watermark = watermark.resize((base_width, new_watermark_height), Image.Resampling.LANCZOS)

    # Cria uma nova imagem transparente para combinar a imagem base e a marca d'água
    transparent = Image.new('RGBA', (base_width, base_height), (0, 0, 0, 0))
    transparent.paste(base_image, (0, 0))
    # Posiciona a marca d'água na parte inferior da imagem
    transparent.paste(watermark, (0, base_height - new_watermark_height), mask=watermark)
    return transparent.convert("RGB")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            watermarked = add_watermark(filepath, app.config['WATERMARK'])
            watermarked_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'watermarked_' + file.filename)
            watermarked.save(watermarked_filepath)
            return redirect(url_for('uploaded_file', filename='watermarked_' + file.filename))
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
