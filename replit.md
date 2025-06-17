# Kompresi Wlee - Aplikasi Kompresi Gambar

## Overview
Ini adalah aplikasi web berbasis Flask untuk kompresi gambar yang dibangun dengan Python. Aplikasi ini memungkinkan pengguna mengunggah gambar dan mengompresnya sambil mempertahankan kualitas visual. Fitur aplikasi mencakup UI Bootstrap modern dengan fungsionalitas drag-and-drop, validasi file real-time, dan opsi target ukuran kompresi yang dapat disesuaikan.

## System Architecture
The application follows a simple Flask web application architecture with the following structure:
- **Frontend**: HTML templates with Bootstrap 5 styling and vanilla JavaScript
- **Backend**: Flask web framework with Python 3.11
- **File Storage**: Local file system storage in `static/uploads/`
- **Image Processing**: Pillow (PIL) library for image manipulation and compression
- **Deployment**: Gunicorn WSGI server with autoscale deployment target

## Key Components

### Backend Components
- **Flask Application** (`app.py`): Main application logic including file upload handling, image compression, and route definitions
- **Entry Point** (`main.py`): Application entry point that runs the Flask development server
- **Image Processing**: Uses Pillow library for image compression with configurable quality settings
- **File Validation**: Supports PNG, JPG, JPEG, WEBP, BMP, and TIFF formats with 16MB size limit

### Frontend Components
- **Templates**: Jinja2 templates with Bootstrap 5 UI framework
  - `index.html`: Main upload interface with drag-and-drop functionality
  - `result.html`: Compression results display with before/after comparison
- **Static Assets**:
  - `style.css`: Custom styling with CSS variables and responsive design
  - `main.js`: Client-side file validation and preview functionality
- **Upload Directory**: `static/uploads/` for storing original and compressed images

### Configuration
- **Dependencies**: Managed via `pyproject.toml` with UV lock file
- **Environment**: Configurable via environment variables (SESSION_SECRET)
- **Deployment**: Gunicorn production server with reloading capabilities
- **File Limits**: 16MB maximum file size, multiple image format support

## Data Flow
1. User uploads image via web interface
2. Client-side validation checks file type and size
3. Image preview displayed before compression
4. Server receives file and validates again
5. Pillow processes and compresses the image
6. Compressed image saved to uploads directory
7. Results page shows compression statistics and download options

## External Dependencies
- **Flask**: Web framework for HTTP request handling
- **Pillow**: Image processing and compression library
- **Werkzeug**: WSGI utilities and secure filename handling
- **Bootstrap 5**: Frontend CSS framework via CDN
- **Bootstrap Icons**: Icon library via CDN
- **Gunicorn**: Production WSGI server
- **PostgreSQL**: Database packages included but not currently implemented

## Deployment Strategy
The application is configured for Replit deployment with:
- **Runtime**: Python 3.11 with Nix package management
- **Server**: Gunicorn with auto-scaling deployment target
- **Port Binding**: 0.0.0.0:5000 for external access
- **Process Management**: Parallel workflow execution
- **Development**: Hot reload enabled for development workflow

## Changelog
- June 17, 2025: Initial setup
- June 17, 2025: Updated to Indonesian language interface, changed title to "Kompresi Wlee", increased file limit to 50MB, added target compression size feature, updated footer to "Nico Djadug Apriliano"

## Recent Changes
- Complete interface translation to Indonesian language
- Title changed from "Image Compressor" to "Kompresi Wlee"
- Maximum file upload size increased from 16MB to 50MB
- Added target compression size selection feature (0.5MB to 10MB presets + custom input)
- Enhanced compression algorithm with dynamic quality adjustment based on target size
- Updated footer attribution to "Nico Djadug Apriliano"
- All user-facing text, error messages, and alerts translated to Indonesian

## User Preferences
Preferred communication style: Simple, everyday language in Indonesian.