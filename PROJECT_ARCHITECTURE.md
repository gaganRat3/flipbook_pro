# 📚 FLIPBOOK PROJECT - COMPLETE ARCHITECTURE & WORKFLOW GUIDE

---

## 🎯 PROJECT OVERVIEW

**Framework**: Django 4.2 + SQLite  
**Purpose**: Digital flipbook (PDF-to-image) viewer with user authentication  
**Database**: db.sqlite3

### Key Features:
- ✅ User registration & login
- ✅ Concurrent login limit (1 active session per user)
- ✅ Book access control (admin grant access)
- ✅ Unlock request system (users request book access)
- ✅ Event-based book organization
- ✅ PWA offline support (service worker)
- ✅ Session management & device tracking

---

## 🗂️ PROJECT STRUCTURE

```
flipbook_pro/
├── books/                          # Main Django app
│   ├── models.py                   # Database models
│   ├── views.py                    # View logic
│   ├── urls.py                     # URL routing
│   ├── forms.py                    # Form definitions
│   ├── middleware.py               # Custom middleware
│   ├── admin.py                    # Admin configuration
│   ├── management/commands/        # Django management commands
│   │   └── cleanup_sessions.py     # Session cleanup command
│   └── migrations/                 # Database migrations
│
├── flipbook_project/               # Django project settings
│   ├── settings.py                 # Configuration
│   ├── urls.py                     # Root URL routing
│   ├── asgi.py                     # ASGI config
│   └── wsgi.py                     # WSGI config
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   └── books/                      # App templates
│       ├── home.html               # Book listing
│       ├── login.html              # Login form
│       ├── register.html           # Registration form
│       ├── flipbook.html           # Book viewer
│       ├── active_sessions.html    # Session management
│       └── unlock_request.html     # Access request form
│
├── static/                         # Static files
│   ├── service-worker.js           # PWA offline support
│   └── manifest.json               # PWA manifest
│
├── media/                          # User uploads
│   ├── books/                      # Book page images
│   ├── thumbnails/                 # Book thumbnails
│   ├── pdfs/                       # Original PDFs
│   └── payment_screenshots/        # User uploads
│
└── db.sqlite3                      # SQLite database
```

---

## 🗄️ DATABASE MODELS & RELATIONSHIPS

### 1. **User** (Django Built-in)
- `username`: Unique login name
- `email`: User email
- `password`: Hashed password
- `is_staff`: Admin flag
- `is_authenticated`: Login status

### 2. **UserProfile** (Extended User Data)
```
UserProfile
├─ OneToOne→ User
└─ mobile_number
```

### 3. **Event** (Book organizer)
```
Event
├─ name (unique)
├─ description
├─ icon (Font Awesome class)
├─ color (hex)
└─ is_active (boolean)
```

### 4. **FlipBook** (The actual books)
```
FlipBook
├─ title
├─ description
├─ ForeignKey→ Event
├─ ForeignKey→ User (created_by)
├─ pdf_file (upload)
├─ thumbnail (generated from PDF)
├─ total_pages (count)
├─ is_published (boolean)
├─ created_at / updated_at
└── get_pages() → returns list of page image URLs
```

### 5. **BookView** (Activity tracking)
```
BookView
├─ ForeignKey→ FlipBook
├─ ForeignKey→ User (nullable)
├─ ip_address
└─ viewed_at
```

### 6. **FlipBookAccess** (Authorization layer)
```
FlipBookAccess (CONTROLS WHO CAN VIEW WHAT)
├─ ForeignKey→ User
├─ ForeignKey→ FlipBook
├─ unique_together: (User, FlipBook)
└─ granted_at
```

### 7. **UserLoginSession** (Session tracking - THE KEY MODEL)
```
UserLoginSession
├─ ForeignKey→ User
├─ session_key (unique) ← Links to Django's Session table
├─ ip_address
├─ user_agent (browser/device info)
├─ login_at
└─ last_activity
```

### 8. **UnlockRequest** (Access request system)
```
UnlockRequest
├─ ForeignKey→ FlipBook
├─ ForeignKey→ User
├─ candidate_full_name
├─ date_of_birth
├─ marital_status
├─ payment_screenshot
├─ status (pending/approved/rejected)
└─ submitted_at
```

### 9. **UnlockRequestBook** (Link unlock requests to books)
```
UnlockRequestBook
├─ ForeignKey→ UnlockRequest
├─ ForeignKey→ FlipBook
├─ price
└─ added_at
```

---

## 🔐 LOGIN SESSION WORKFLOW (STEP-BY-STEP)

### **SCENARIO 1: User Login (First Time)**

```
┌──────────────────────────────────────┐
│  User visits: /login/                │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  login_view() is called              │
│  - Session key created in Django     │
│  - Cleanup expired sessions          │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  User submits form (username/pwd)    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  System checks:                      │
│  - Valid credentials? (YES)          │
│  - User has active session? (NO)     │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  login(request, user) called         │
│  - Django sets session cookie        │
│  - Django creates Session record     │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  UserLoginSession.objects.create()   │
│  - Records:                          │
│    • user_id                         │
│    • session_key (from Django)       │
│    • ip_address                      │
│    • user_agent                      │
│    • login_at (now)                  │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  ✅ Login success!                   │
│  User redirected to /home/           │
└──────────────────────────────────────┘
```

---

### **SCENARIO 2: User Login (Already Has Active Session)**

```
┌──────────────────────────────────────┐
│  User submits login form             │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  System checks:                      │
│  - Valid credentials? (YES)          │
│  - UserLoginSession.objects.filter() │
│    (user=user).count() >= 1? (YES)   │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  ❌ LOGIN BLOCKED!                   │
│  Error message:                      │
│  "Someone is already using this      │
│   account. Please logout and try     │
│   again."                            │
└──────────────────────────────────────┘
```

---

### **SCENARIO 3: User Logout**

```
┌──────────────────────────────────────┐
│  User clicks "LOG OUT"               │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  logout_view() is called             │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  STEP 1:                             │
│  Delete UserLoginSession record      │
│  .filter(user=user,                  │
│          session_key=session_key)    │
│  .delete()                           │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  STEP 2:                             │
│  logout(request) called              │
│  - Django deletes Session record     │
│  - Session cookie cleared            │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  ✅ Logout complete!                 │
│  User redirected to /login/          │
│  Message: "Successfully logged out"  │
└──────────────────────────────────────┘
```

---

### **SCENARIO 4: Session Expires (Auto-logout)**

```
┌──────────────────────────────────────────┐
│  Browser closes or timeout occurs        │
│  (SESSION_EXPIRE_AT_BROWSER_CLOSE=True)  │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  Django's Session record expires         │
│  (based on SESSION_COOKIE_AGE)           │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  BUT: UserLoginSession record still      │
│  exists (ORPHANED SESSION)               │
│                                          │
│  This causes: "Someone already logged    │
│   in" error even though no session!      │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  SOLUTION:                               │
│  cleanup_expired_sessions() removes      │
│  orphaned UserLoginSession records       │
└──────────────────────────────────────────┘
```

---

## 🔄 SESSION CLEANUP MECHANISM

### **Function: cleanup_expired_sessions()**
Located in: `books/views.py`

```python
def cleanup_expired_sessions():
    """Remove login sessions that no longer exist in Django's session table"""
    
    # STEP 1: Get all VALID Django session keys
    valid_sessions = set(Session.objects.values_list('session_key', flat=True))
    
    # STEP 2: Delete UserLoginSession records that reference expired Django sessions
    orphaned = UserLoginSession.objects.exclude(session_key__in=valid_sessions)
    deleted_count = orphaned.count()
    orphaned.delete()
    
    # STEP 3: Also delete expired Django sessions themselves
    expired = Session.objects.filter(expire_date__lt=timezone.now())
    expired.delete()
```

### **When is cleanup called?**
1. ✅ **During login** - Checks before counting active sessions
2. ✅ **During logout** - Ensures clean state
3. ✅ **On home page load** - Ensures consistency
4. ✅ **On session view** - Before displaying sessions
5. ✅ **Management command** - Manual cleanup: `python manage.py cleanup_sessions`

---

## 🔗 AUTHENTICATION FLOW (Complete Request Cycle)

### **REQUEST 1: User Accesses Protected Page (e.g., /home/)**

```
Request comes in:
  ↓
Django Middleware Chain:
  ├─ SessionMiddleware         → Loads session from cookie
  ├─ AuthenticationMiddleware  → Loads user from session
  ├─ AdminForceStaffLogoutMiddleware → Logout non-staff from /admin/
  └─ MessageMiddleware         → Handle flash messages
  ↓
View Handler: @login_required decorator
  ├─ Checks: request.user.is_authenticated?
  ├─ YES → Allow access
  └─ NO → Redirect to /login/
  ↓
View Code Execution:
  ├─ Ensure session_key exists
  ├─ Query: FlipBookAccess.objects.filter(
  │            user=request.user
  │         )
  └─ Show only accessible books
  ↓
Response sent to browser
```

---

## 📊 CONCURRENT LOGIN SETTINGS

**Current Limit**: MAX 1 active session per user

### Settings in settings.py:
```python
SESSION_EXPIRE_AT_BROWSER_CLOSE = True     # Auto-logout on browser close
SESSION_COOKIE_SECURE = True               # HTTPS only
SESSION_COOKIE_AGE = 1209600               # 14 days (if not at browser close)
CSRF_COOKIE_SECURE = True                  # HTTPS only
```

---

## 📱 KEY VIEWS & FUNCTIONS

### 1. **login_view()** - User Login
- **Path**: POST `/login/`
- **Steps**:
  1. Create session key (if not exists)
  2. Run cleanup_expired_sessions()
  3. Check if username XOR email + password valid
  4. Check concurrent session limit (>= 1)
  5. If limit exceeded → Show error
  6. If ok → Call login(), create UserLoginSession
  7. Redirect to /home/

### 2. **logout_view()** - User Logout
- **Path**: GET `/logout/`
- **Steps**:
  1. Delete UserLoginSession record
  2. Call Django's logout()
  3. Redirect to /login/

### 3. **home_view()** - Protected Home Page
- **Path**: GET `/home/` (requires @login_required)
- **Steps**:
  1. Ensure UserLoginSession exists
  2. Query FlipBookAccess for user
  3. Show only accessible books
  4. Support filtering by event/category

### 4. **active_sessions_view()** - Session Management
- **Path**: GET `/active-sessions/` (requires @login_required)
- **Shows**:
  - All active sessions for current user
  - Device info (User-Agent)
  - IP address
  - Login time
  - Logout button for other devices

### 5. **logout_other_session()** - Logout Other Device
- **Path**: POST `/logout-session/<session_id>/`
- **Action**: Delete specific UserLoginSession record

### 6. **flipbook_view()** - View Book
- **Path**: GET `/book/<book_id>/`
- **Checks**:
  - User has FlipBookAccess?
  - If NO → Error message
  - If YES → Show flipbook pages
  - Track view in BookView

---

## 🐛 KNOWN ISSUES & FIXES

### **Issue 1: "Someone is already using this account" error on login**
**Root Cause**: Orphaned UserLoginSession records remain after Django session expires

**Solution**: Run cleanup command
```bash
python manage.py cleanup_sessions
```

---

### **Issue 2: Users can't view books even though access granted**
**Root Cause**: FlipBookAccess record missing or user_id mismatch

**Debug**:
```bash
# Check via admin panel
/admin/books/flipbookaccess/
```

---

### **Issue 3: Session doesn't auto-logout after browser close**
**Settings Check**:
```python
# In settings.py:
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Must be True
```

---

## 🛠️ MANAGEMENT COMMANDS

### **cleanup_sessions.py** - Session Management
```bash
# Normal cleanup (recommended)
python manage.py cleanup_sessions

# Force delete ALL UserLoginSession records
python manage.py cleanup_sessions --force

# Reset sessions for specific user (by user_id)
python manage.py cleanup_sessions --reset-user=1
```

---

## 📝 HOW TO ADD AUTO-LOGOUT WHEN SESSION DELETED

If you want to **force auto-logout** when session is deleted:

### **Option 1**: AJAX polling (user's browser checks periodically)
```javascript
// Add to base.html
setInterval(function() {
    fetch('/check-session/').then(r => r.json()).then(data => {
        if (!data.is_valid) {
            // Session invalid, logout
            location.href = '/logout/';
        }
    });
}, 5000); // Check every 5 seconds
```

### **Option 2**: Middleware checking
```python
# Add to middleware.py
class SessionValidationMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated:
            if not UserLoginSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key
            ).exists():
                logout(request)
                return redirect('login')
        return self.get_response(request)
```

---

## Summary
- **Session tracking uses TWO tables**: Django's `Session` + Custom `UserLoginSession`
- **Orphaned records are the main issue**: When Django session expires but UserLoginSession remains
- **Cleanup is the solution**: Regular cleanup removes orphaned records
- **Concurrent limit is enforced**: Only 1 active session per user currently
- **Auto-logout needs client-side or middleware check**: Simple session deletion isn't enough

