from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/how-to-use')
def how_to_use():
    return render_template('how-to-use.html')
users = {}

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if email in users:
            flash('Email already registered. Please log in.')
        else:
            users[email] = {'username': username, 'password': password}
            flash('Sign up successful! You can now log in.')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = users.get(email)
        if user and user['password'] == password:
            flash('Login successful!')
            return redirect(url_for('index'))  # or dashboard if you have one
        else:
            flash('Invalid email or password.')
    return render_template('login.html')


@app.route('/edit', methods=['POST'])
def edit():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Read image with OpenCV
    image = cv2.imdecode(np.fromfile(filepath, np.uint8), cv2.IMREAD_UNCHANGED)
    if image is None:
        flash('Invalid image file')
        return redirect(url_for('index'))

    # Get form inputs
    action = request.form.get('action')
    flip = request.form.get('flip')
    resize_width = request.form.get('resize_width')
    resize_height = request.form.get('resize_height')
    target_size_kb = request.form.get('target_size_kb')

    # Flip image if requested
    if flip == 'horizontal':
        image = cv2.flip(image, 1)
    elif flip == 'vertical':
        image = cv2.flip(image, 0)

    # Resize if both dimensions are provided
    try:
        if resize_width and resize_height:
            w = int(resize_width)
            h = int(resize_height)
            image = cv2.resize(image, (w, h))
    except Exception as e:
        flash('Invalid resize dimensions')

    output_buffer = io.BytesIO()

    # Process based on action
    if action == 'grayscale':
        # Convert to grayscale
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ext = '.png'
        success, encoded_img = cv2.imencode(ext, image)
        if not success:
            flash('Failed to process grayscale image')
            return redirect(url_for('index'))
        output_buffer.write(encoded_img.tobytes())
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/png', as_attachment=True, download_name='grayscale.png')

    elif action == 'jpg':
        quality = 95
        if target_size_kb:
            try:
                quality = max(10, min(95, int(target_size_kb) // 2))  # rough quality approx
            except:
                pass
        is_success, im_buf_arr = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not is_success:
            flash('Failed to convert to JPG')
            return redirect(url_for('index'))
        output_buffer.write(im_buf_arr.tobytes())
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/jpeg', as_attachment=True, download_name='converted.jpg')

    elif action == 'webp':
        quality = 90
        if target_size_kb:
            try:
                quality = max(10, min(100, int(target_size_kb) // 2))
            except:
                pass
        is_success, im_buf_arr = cv2.imencode('.webp', image, [int(cv2.IMWRITE_WEBP_QUALITY), quality])
        if not is_success:
            flash('Failed to convert to WEBP')
            return redirect(url_for('index'))
        output_buffer.write(im_buf_arr.tobytes())
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/webp', as_attachment=True, download_name='converted.webp')

    elif action == 'pdf':
        # Convert image to PIL format for PDF
        if len(image.shape) == 2:
            pil_img = Image.fromarray(image)
        else:
            pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        pdf_bytes = io.BytesIO()
        pil_img.save(pdf_bytes, format='PDF')
        pdf_bytes.seek(0)
        return send_file(pdf_bytes, mimetype='application/pdf', as_attachment=True, download_name='converted.pdf')

    else:  # default is PNG output (including 'none')
        success, im_buf_arr = cv2.imencode('.png', image)
        if not success:
            flash('Failed to process image')
            return redirect(url_for('index'))
        output_buffer.write(im_buf_arr.tobytes())
        output_buffer.seek(0)
        return send_file(output_buffer, mimetype='image/png', as_attachment=True, download_name='edited.png')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
