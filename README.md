# FlipBook Pro - Interactive PDF FlipBook Viewer

A Django-based web application that converts PDFs into beautiful, interactive flipbooks with realistic page-turning animations.

## Features

✨ **Modern FlipBook Viewer**

- Realistic 3D page-flip animations using Turn.js
- Smooth transitions and interactive controls
- Mobile and desktop responsive design
- Fullscreen mode support

🔐 **Authentication System**

- User login/logout functionality
- Admin panel for PDF management
- Secure access control

📚 **PDF Management**

- Upload PDFs through Django admin
- Automatic PDF to image conversion
- Thumbnail generation
- Track book views and analytics

🎨 **Beautiful UI**

- Clean, modern interface like Heyzine
- Gradient backgrounds
- Smooth animations
- Mobile-first responsive design

## Tech Stack

- **Backend**: Django 5.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Libraries**:
  - Turn.js (flipbook animations)
  - jQuery
  - Font Awesome icons
- **PDF Processing**: pdf2image, Pillow

## Installation

### Prerequisites

- Python 3.8+
- Poppler (for PDF conversion)
  - Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases
  - Mac: `brew install poppler`
  - Linux: `sudo apt-get install poppler-utils`

### Setup Instructions

1. **Clone/Navigate to project directory**

   ```bash
   cd "c:\Users\Acer\Downloads\gagan\book flip new"
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   copy .env.example .env
   # Edit .env and set your SECRET_KEY
   ```

5. **Run migrations**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Create static directories**

   ```bash
   mkdir static
   mkdir media
   ```

8. **Run development server**

   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## Usage

### Uploading FlipBooks

1. Login to admin panel at `/admin`
2. Navigate to "FlipBooks"
3. Click "Add FlipBook"
4. Fill in:
   - Title
   - Description (optional)
   - PDF file
   - Is published (checkbox)
5. Save - PDF will automatically convert to images

### Viewing FlipBooks

1. Login to the main site
2. Browse the library
3. Click on any book to open the flipbook viewer
4. Use controls:
   - **Arrow buttons**: Navigate pages
   - **First/Last buttons**: Jump to start/end
   - **Zoom buttons**: Zoom in/out
   - **Fullscreen button**: Toggle fullscreen
   - **Keyboard**: Arrow keys, Home, End

## Project Structure

```
book flip new/
├── flipbook_project/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── books/                     # Main app
│   ├── models.py             # FlipBook & BookView models
│   ├── views.py              # View logic
│   ├── admin.py              # Admin configuration
│   └── urls.py               # URL routing
├── templates/                 # HTML templates
│   ├── base.html
│   └── books/
│       ├── login.html
│       ├── home.html
│       └── flipbook.html
├── static/                    # Static files (CSS, JS)
├── media/                     # User uploads
│   ├── pdfs/                 # Original PDFs
│   ├── books/                # Converted page images
│   └── thumbnails/           # Book thumbnails
├── manage.py
└── requirements.txt
```

## Features in Detail

### Mobile Responsive

- Single-page display on mobile devices
- Touch gestures for page turning
- Optimized controls for small screens
- Responsive layouts

### Desktop Experience

- Double-page spread view
- Keyboard navigation
- Zoom controls
- Fullscreen mode

### Admin Features

- Upload PDFs
- Edit book metadata
- Publish/unpublish books
- View analytics

## Troubleshooting

**PDF conversion fails:**

- Ensure Poppler is installed and in PATH
- Check PDF file is not corrupted
- Verify write permissions in media directory

**Turn.js not loading:**

- Check internet connection (CDN dependencies)
- Clear browser cache
- Check browser console for errors

**Images not displaying:**

- Verify media files are accessible
- Check MEDIA_URL and MEDIA_ROOT settings
- Ensure DEBUG=True for development

## License

MIT License - feel free to use for personal or commercial projects

## Credits

- Turn.js for flipbook animations
- Django framework
- Font Awesome for icons

---

**Enjoy your FlipBook experience! 📖✨**
