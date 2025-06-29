import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, ImageFile
import uuid
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Allow loading of truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size(filepath):
    """Get file size in bytes"""
    return os.path.getsize(filepath)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f}{size_names[i]}"

def compress_image(input_path, output_path, quality=75, target_size_mb=None):
    """
    Compress image while maintaining reasonable quality
    Returns compression info dictionary
    """
    try:
        with Image.open(input_path) as img:
            # Get original dimensions and size
            original_width, original_height = img.size
            original_size = get_file_size(input_path)
            
            # Convert to RGB if necessary for better compression
            if img.mode in ('RGBA', 'LA'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode == 'P':
                img = img.convert('RGB')
            
            # Determine output format - force JPEG for better compression
            output_ext = os.path.splitext(output_path)[1].lower()
            
            # For maximum compression, convert PNG/other formats to JPEG
            if output_ext in ['.png', '.bmp', '.tiff']:
                output_path = output_path.rsplit('.', 1)[0] + '.jpg'
                output_ext = '.jpg'
            
            # Resize image if it's too large (helps with compression)
            max_dimension = 2048  # Maximum width or height
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Set initial quality based on target size
            if target_size_mb:
                target_size_bytes = target_size_mb * 1024 * 1024
                # Estimate initial quality based on target size
                if target_size_bytes < original_size * 0.1:
                    current_quality = 30
                elif target_size_bytes < original_size * 0.3:
                    current_quality = 50
                else:
                    current_quality = 70
            else:
                current_quality = quality
            
            # Compression with iterative quality adjustment
            best_quality = current_quality
            attempts = 0
            max_attempts = 8
            
            while attempts < max_attempts:
                # Set compression parameters
                if output_ext in ['.jpg', '.jpeg']:
                    img.save(output_path, 
                            format='JPEG',
                            quality=current_quality,
                            optimize=True,
                            progressive=True)
                elif output_ext == '.webp':
                    img.save(output_path,
                            format='WEBP',
                            quality=current_quality,
                            optimize=True,
                            method=6)  # Higher compression method
                else:
                    # For other formats, convert to JPEG
                    output_path = output_path.rsplit('.', 1)[0] + '.jpg'
                    img.save(output_path,
                            format='JPEG',
                            quality=current_quality,
                            optimize=True,
                            progressive=True)
                
                compressed_size = get_file_size(output_path)
                
                # Check if we have a target size
                if target_size_mb:
                    if compressed_size <= target_size_bytes:
                        break
                    elif current_quality <= 15:
                        break
                    else:
                        # Reduce quality more aggressively
                        current_quality = max(15, current_quality - 10)
                else:
                    # For general compression, ensure we're actually reducing size
                    if compressed_size < original_size * 0.8:  # At least 20% reduction
                        break
                    elif current_quality <= 25:
                        break
                    else:
                        current_quality = max(25, current_quality - 10)
                
                attempts += 1
            
            # Final check - ensure file was actually compressed
            final_size = get_file_size(output_path)
            compression_ratio = ((original_size - final_size) / original_size) * 100
            
            # If compression failed to reduce size significantly, try more aggressive approach
            if compression_ratio < 5 and not target_size_mb:
                # More aggressive compression
                img.save(output_path,
                        format='JPEG',
                        quality=40,
                        optimize=True,
                        progressive=True)
                final_size = get_file_size(output_path)
                compression_ratio = ((original_size - final_size) / original_size) * 100
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': final_size,
                'compression_ratio': max(compression_ratio, 0),  # Ensure non-negative
                'original_dimensions': (original_width, original_height),
                'compressed_dimensions': img.size
            }
            
    except Exception as e:
        logging.error(f"Error compressing image: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/')
def index():
    """Main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and compression"""
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada file yang dipilih', 'error')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        try:
            # Get target compression size from form
            target_size_mb = request.form.get('target_size_mb', type=float)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1].lower() if file.filename else '.jpg'
            unique_id = str(uuid.uuid4())
            original_filename = f"{unique_id}_original{file_extension}"
            compressed_filename = f"{unique_id}_compressed{file_extension}"
            
            # Save original file
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            file.save(original_path)
            
            # Compress image with target size if specified
            compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], compressed_filename)
            compression_info = compress_image(original_path, compressed_path, target_size_mb=target_size_mb)
            
            if compression_info['success']:
                # Prepare data for template
                result_data = {
                    'original_filename': original_filename,
                    'compressed_filename': compressed_filename,
                    'original_name': file.filename,
                    'original_size': format_file_size(compression_info['original_size']),
                    'compressed_size': format_file_size(compression_info['compressed_size']),
                    'compression_ratio': f"{compression_info['compression_ratio']:.1f}%",
                    'original_dimensions': compression_info['original_dimensions'],
                    'compressed_dimensions': compression_info['compressed_dimensions']
                }
                
                return render_template('result.html', **result_data)
            else:
                # Clean up original file on compression failure
                if os.path.exists(original_path):
                    os.remove(original_path)
                flash(f'Gagal mengompres gambar: {compression_info["error"]}', 'error')
                return redirect(url_for('index'))
                
        except Exception as e:
            logging.error(f"Upload error: {str(e)}")
            flash(f'Gagal memproses file: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('Tipe file tidak valid. Silakan upload file PNG, JPG, JPEG, WEBP, BMP, atau TIFF.', 'error')
        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/cleanup')
def cleanup_files():
    """Clean up old uploaded files (optional endpoint for maintenance)"""
    try:
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        files_removed = 0
        
        for file_path in upload_dir.glob('*'):
            if file_path.is_file() and file_path.name != '.gitkeep':
                file_path.unlink()
                files_removed += 1
        
        flash(f'Successfully removed {files_removed} files', 'success')
    except Exception as e:
        flash(f'Error during cleanup: {str(e)}', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
