document.addEventListener('DOMContentLoaded', function() {
    // File input and upload area elements
    const fileInput = document.getElementById('file');
    const uploadArea = document.getElementById('uploadArea');
    const imagePreview = document.getElementById('imagePreview');
    const previewImage = document.getElementById('previewImage');
    const fileInfo = document.getElementById('fileInfo');
    const uploadForm = document.getElementById('uploadForm');
    const compressBtn = document.getElementById('compressBtn');

    // Supported file types
    const supportedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'];
    const maxFileSize = 16 * 1024 * 1024; // 16MB

    // File size formatter
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Validate file
    function validateFile(file) {
        if (!file) return { valid: false, error: 'No file selected' };
        
        if (!supportedTypes.includes(file.type)) {
            return { 
                valid: false, 
                error: 'Unsupported file type. Please select a JPEG, PNG, WEBP, BMP, or TIFF image.' 
            };
        }
        
        if (file.size > maxFileSize) {
            return { 
                valid: false, 
                error: 'File too large. Maximum size is 16MB.' 
            };
        }
        
        return { valid: true };
    }

    // Show image preview
    function showPreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result;
            fileInfo.textContent = `${file.name} (${formatFileSize(file.size)})`;
            imagePreview.style.display = 'block';
            
            // Smooth scroll to preview
            imagePreview.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        };
        reader.readAsDataURL(file);
    }

    // Handle file selection
    function handleFileSelect(file) {
        const validation = validateFile(file);
        
        if (!validation.valid) {
            showAlert(validation.error, 'danger');
            fileInput.value = '';
            imagePreview.style.display = 'none';
            return;
        }
        
        showPreview(file);
        uploadArea.classList.remove('dragover');
    }

    // Show alert message
    function showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert:not(.alert-dismissible)');
        existingAlerts.forEach(alert => alert.remove());
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            <i class="bi bi-${type === 'danger' ? 'exclamation-triangle' : 'info-circle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert alert at the top of the card body
        const cardBody = document.querySelector('.card-body');
        cardBody.insertBefore(alertDiv, cardBody.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // File input change event
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                handleFileSelect(file);
            }
        });
    }

    // Drag and drop functionality
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            uploadArea.classList.add('dragover');
        }

        function unhighlight() {
            uploadArea.classList.remove('dragover');
        }

        uploadArea.addEventListener('drop', function(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        });
    }

    // Form submission with loading state
    if (uploadForm && compressBtn) {
        uploadForm.addEventListener('submit', function(e) {
            const file = fileInput.files[0];
            const validation = validateFile(file);
            
            if (!validation.valid) {
                e.preventDefault();
                showAlert(validation.error, 'danger');
                return;
            }
            
            // Show loading state
            compressBtn.disabled = true;
            compressBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Compressing...';
            
            // Show processing message
            showAlert('Processing your image... Please wait.', 'info');
        });
    }

    // Auto-dismiss alerts
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-close')) {
            const alert = e.target.closest('.alert');
            if (alert) {
                alert.remove();
            }
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Image loading enhancement for result page
    const comparisonImages = document.querySelectorAll('.comparison-image');
    comparisonImages.forEach(img => {
        img.addEventListener('load', function() {
            this.style.opacity = '0';
            this.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                this.style.opacity = '1';
            }, 100);
        });
    });

    // Keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Escape key to clear preview
        if (e.key === 'Escape' && imagePreview && imagePreview.style.display !== 'none') {
            imagePreview.style.display = 'none';
            fileInput.value = '';
        }
        
        // Enter key on file input to trigger click
        if (e.key === 'Enter' && e.target === fileInput) {
            e.target.click();
        }
    });

    // Progressive enhancement for older browsers
    if (!window.FileReader) {
        console.warn('FileReader not supported. Preview functionality disabled.');
    }

    // Handle page unload when form is being submitted
    let formSubmitted = false;
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', function() {
            formSubmitted = true;
        });
        
        window.addEventListener('beforeunload', function(e) {
            if (compressBtn && compressBtn.disabled && !formSubmitted) {
                e.preventDefault();
                e.returnValue = 'Your image is being processed. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }

    console.log('Image Compressor: JavaScript initialized successfully');
});
