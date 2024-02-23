from flask import Flask, request, send_file, render_template
import os
from PIL import Image
import cairosvg
import io

app = Flask(__name__)

# Configure upload folder and allowed extension
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'svg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_and_resize(svg_input_path):
    # Convert SVG to PNG
    png_output_path = svg_input_path.rsplit('.', 1)[0] + '.png'
    cairosvg.svg2png(url=svg_input_path, write_to=png_output_path)
    
    # Resize the image if larger than 144x32
    max_width, max_height = 144, 32
    img = Image.open(png_output_path)
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height))
        img.save(png_output_path)
    
    return png_output_path

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        svg_filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(svg_filename)
        
        # Convert and resize the image
        output_filename = convert_and_resize(svg_filename)
        
        return send_file(output_filename, as_attachment=True)

    return 'Invalid file type'

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
