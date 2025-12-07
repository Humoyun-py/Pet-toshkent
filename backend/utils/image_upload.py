import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """Save uploaded image and return filename"""
    print(f"[save_image] Called with file: {file}")
    
    if not file:
        print("[save_image] No file provided")
        return None
    
    print(f"[save_image] Filename: {file.filename}")
    
    if not file.filename:
        print("[save_image] Empty filename")
        return None
        
    if not allowed_file(file.filename):
        print(f"[save_image] File not allowed: {file.filename}")
        return None
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Ensure upload folder exists
    upload_folder = current_app.config['UPLOAD_FOLDER']
    print(f"[save_image] Upload folder: {upload_folder}")
    os.makedirs(upload_folder, exist_ok=True)
    
    # Save file
    filepath = os.path.join(upload_folder, filename)
    print(f"[save_image] Saving to: {filepath}")
    
    try:
        file.save(filepath)
        print(f"[save_image] SUCCESS! Saved as: {filename}")
        return filename
    except Exception as e:
        print(f"[save_image] ERROR saving file: {e}")
        return None

def delete_image(filename):
    """Delete image file"""
    if filename:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    return False

def get_image_url(filename):
    """Get full URL for image"""
    if filename:
        return f"/static/uploads/{filename}"
    return None
