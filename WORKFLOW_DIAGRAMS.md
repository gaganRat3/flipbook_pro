# 📊 FLIPBOOK PROJECT - VISUAL WORKFLOWS & QUICK REFERENCE

---

## 🔄 COMPLETE REQUEST LIFECYCLE

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                         USER REQUEST JOURNEY                                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────┐
│  User's Browser     │
│  GET /home/         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│  Django Middleware Chain (In Order)             │
│  ┌──────────────────────────────────────────┐   │
│  │ 1. SecurityMiddleware                    │   │
│  │    - HTTPS enforcement                   │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ 2. SessionMiddleware                     │   │
│  │    - Load session from cookie            │   │
│  │    - request.session = SessionStore()    │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ 3. CommonMiddleware                      │   │
│  │    - URL normalization                   │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ 4. CsrfViewMiddleware                    │   │
│  │    - CSRF token validation               │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ 5. AuthenticationMiddleware               │   │
│  │    - Load User from session              │   │
│  │    - if session_key in Session table:    │   │
│  │      - Get user_id from session data     │   │
│  │      - request.user = User object()      │   │
│  │    - else:                               │   │
│  │      - request.user = AnonymousUser      │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ 6. AdminForceStaffLogoutMiddleware       │   │
│  │    - If path is /admin/                  │   │
│  │    - And user.is_staff == False          │   │
│  │    - Then logout(request)                │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ 7. MessageMiddleware                     │   │
│  │    - Prepare flash messages              │   │
│  └──────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │  URL Router (urls.py)       │
        │  Match: /home/ → home_view  │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  View: home_view(request)        │
        │  @login_required (decorator)     │
        │                                  │
        │  Check: request.user.is_auth?    │
        │  - YES → Continue                │
        │  - NO → Redirect to /login/      │
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  View Logic                      │
        │  ┌──────────────────────────────┤
        │  │ 1. cleanup_expired_sessions()│
        │  │    - Remove stale sessions   │
        │  └──────────────────────────────┤
        │  ┌──────────────────────────────┤
        │  │ 2. Query accessible books:   │
        │  │    FlipBookAccess.objects    │
        │  │    .filter(user=user)        │
        │  └──────────────────────────────┤
        │  ┌──────────────────────────────┤
        │  │ 3. Query published books:    │
        │  │    FlipBook.objects.filter   │
        │  │    (is_published=True)       │
        │  └──────────────────────────────┤
        │  ┌──────────────────────────────┤
        │  │ 4. Apply filters (event,     │
        │  │    gender, category)         │
        │  └──────────────────────────────┤
        │  ┌──────────────────────────────┤
        │  │ 5. Create context dict       │
        │  └──────────────────────────────┘
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  Template Rendering              │
        │  (books/home.html)               │
        │  ┌──────────────────────────────┤
        │  │ {% for book in books %}      │
        │  │   {% if book.id in          │
        │  │         accessible_ids %}   │
        │  │     Show book with link      │
        │  │   {% else %}                 │
        │  │     Show locked icon +       │
        │  │     "Request Access" btn     │
        │  │   {% endif %}                │
        │  │ {% endfor %}                 │
        │  └──────────────────────────────┘
        └────────────┬─────────────────────┘
                     │
                     ▼
        ┌──────────────────────────────────┐
        │  Response Created                │
        │  Rendered HTML page              │
        │  With context data injected      │
        └────────────┬─────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────┐
│  Django Middleware Chain (Response Phase)        │
│  (Reverse order)                                 │
│  - Add Set-Cookie headers                        │
│  - Set other response headers                    │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌─────────────────────┐
│  Browser Receives   │
│  HTML + Headers     │
│  Renders page       │
└─────────────────────┘
```

---

## 🔑 DATABASE RELATIONSHIP DIAGRAM

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    DATABASE RELATIONSHIPS                                │
└──────────────────────────────────────────────────────────────────────────┘

User (Django Built-in)
  ├─ id
  ├─ username
  ├─ email
  ├─ password (hashed)
  ├─ is_staff
  └─ is_active


UserProfile (1-to-1)
  ├─ id
  ├─ user_id (OneToOneField)
  └─ mobile_number


UserLoginSession (Many-to-1)
  ├─ id
  ├─ user_id (ForeignKey) ←─┐
  ├─ session_key (unique)   │  A user can have
  ├─ ip_address             │  multiple sessions
  ├─ user_agent             │  (but limited by logic)
  ├─ login_at               │
  └─ last_activity          ├─ User
                             │
Event (Standard)             │
  ├─ id                      │
  ├─ name                    │
  ├─ description             │
  ├─ icon                    │
  ├─ color                   │
  └─ is_active               │


FlipBook (Many-to-1 to both Event and User)
  ├─ id
  ├─ title
  ├─ description
  ├─ event_id (ForeignKey) ──────────────┘ Event
  ├─ created_by (ForeignKey) ────────────┘ User
  ├─ pdf_file
  ├─ thumbnail
  ├─ total_pages
  ├─ is_published
  ├─ created_at
  └─ updated_at


BookView (Many-to-1 to both FlipBook and User)
  ├─ id
  ├─ book_id (ForeignKey)
  ├─ user_id (ForeignKey) ←─┐
  ├─ ip_address             │  Multiple views
  └─ viewed_at              │  per user per book


FlipBookAccess (Many-to-Many "through" model)
  ├─ id
  ├─ user_id (ForeignKey) ←─┐
  ├─ flipbook_id (ForeignKey) ─→ FlipBook
  ├─ unique_together: (user, flipbook)
  │  └─ Ensures 1-to-1 mapping
  └─ granted_at


UnlockRequest (One-to-1 to FlipBook, Many-to-1 to User)
  ├─ id
  ├─ flipbook_id (ForeignKey) ──→ FlipBook
  ├─ user_id (ForeignKey) ──────→ User
  ├─ candidate_full_name
  ├─ date_of_birth
  ├─ marital_status
  ├─ payment_screenshot
  ├─ status (pending/approved/rejected)
  └─ submitted_at


UnlockRequestBook (Junction table)
  ├─ id
  ├─ unlock_request_id (ForeignKey) ────→ UnlockRequest
  ├─ flipbook_id (ForeignKey)            ──→ FlipBook
  ├─ price (300 rupees default)
  ├─ added_at
  └─ unique_together: (unlock_request, flipbook)


Django Session Table (Built-in)
  ├─ session_key (PK)
  ├─ session_data (JSON)
  │  └─ Contains: {
  │       "_auth_user_id": "123",
  │       "_auth_user_backend": "...",
  │       "_auth_user_hash": "...",
  │       "_auth_user_name": "john"
  │     }
  ├─ expire_date (when session expires)
  └─ Created by: SessionMiddleware
     Updated by: AuthenticationMiddleware


Link between Django Session and UserLoginSession:
┌────────────────────────────┐
│  Django Session Table      │  ← One of these
│  ┌──────────────────────┐  │    exists (Django
│  │ session_key: ABC123  │  │     manages)
│  │ session_data: {...}  │  │
│  │ expire_date: 2026... │  │
│  └──────────────────────┘  │
└────────┬───────────────────┘
         │
         │ LINKED BY session_key
         │
┌────────▼───────────────────┐
│ UserLoginSession Table     │
│ ┌──────────────────────┐   │
│ │ id: 1                │   │
│ │ user_id: 5           │   │ ← Points to same User
│ │ session_key: ABC123  │   │
│ │ ip_address: 192...   │   │
│ │ user_agent: "Moz..." │   │
│ └──────────────────────┘   │
└────────────────────────────┘
```

---

## 🎯 SESSION LIFECYCLE STATE MACHINE

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          SESSION STATES                                  │
└──────────────────────────────────────────────────────────────────────────┘

                            ┌─────────────────┐
                            │  NO SESSION     │
                            │                 │
                            │ User browsing   │
                            │ without login   │
                            └────────┬────────┘
                                     │
                          ┌──────────▼──────────┐
                          │ User submits login  │
                          │ form (valid creds)  │
                          └──────────┬──────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │  SESSION CREATED               │
                    │                                │
                    │ Django creates Session record  │
                    │ Creates UserLoginSession       │
                    │ Sets session cookie            │
                    │                                │
                    │ State in DB:                   │
                    │ - Session.objects: exists      │
                    │ - UserLoginSession: exists     │
                    │ - Cookie: set in browser       │
                    └───┬─────────────────┬──────────┘
                        │                 │
            ┌───────────┴─┐       ┌───────┴──────┐
            │ ACTIVE      │       │ EXPIRED      │
            │ Session     │       │ Session      │
            │             │       │              │
            │ Browser     │       │ Time:        │
            │ active      │       │ SESSION_COOK │
            │ (< 14 days) │       │ IE_AGE limit │
            │             │       │ (14 days)    │
            └────┬────────┘       └───┬──────────┘
                 │                    │
        ┌────────▼────────┐  ┌───────▼─────────┐
        │ User clicks     │  │ cleanup_expired_│
        │ logout button   │  │ sessions() runs │
        │                 │  │                 │
        │ logout_view()   │  │ OR              │
        │ called:         │  │                 │
        │ - Delete        │  │ Browser closes  │
        │   UserLoginSes  │  │ (if EXPIRE_AT   │
        │ - Delete Django │  │ _BROWSER_CLOSE) │
        │   Session       │  │                 │
        │ - Clear cookie  │  │ ORPHANED:       │
        └────────┬────────┘  │ UserLoginSes    │
                 │           │ still exists,   │
                 │           │ Django Session  │
                 │           │ deleted         │
                 │           └────────┬────────┘
                 │                    │
                 │      ┌─────────────┘
                 │      │ cleanup_expired_
                 │      │ sessions()
                 │      │ removes orphaned
                 │      │
                 └──────┴───────────────┘
                        │
                        ▼
                ┌────────────────────────┐
                │  SESSION DESTROYED     │
                │                        │
                │ All records deleted    │
                │ Cookie cleared         │
                │ User logged out        │
                └────────────┬───────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │  NO SESSION        │
                    │  (Back to start)   │
                    └────────────────────┘
```

---

## 🔑 QUICK REFERENCE - FUNCTION CALLS & DATABASE OPERATIONS

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    COMMON OPERATIONS                                     │
└──────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
LOGIN FLOW
═══════════════════════════════════════════════════════════════════════════

1. User submits login form
   ├─ Request: POST /login/
   └─ Handler: login_view()

2. Validate credentials
   ├─ Code: UsernameEmailAuthenticationForm.is_valid()
   ├─ Query: User.objects.get(username=X)
   │         User.objects.get(email=X)
   │         authenticate(username=X, password=X)
   └─ Result: ✓ User object, ✗ None

3. Check concurrent login limit
   ├─ Code: cleanup_expired_sessions()
   ├─ DB: DELETE FROM Session WHERE expire_date < now
   ├─ DB: DELETE FROM UserLoginSession 
   │      WHERE session_key NOT IN (valid Session keys)
   ├─ Query: UserLoginSession.objects.filter(user=user).count()
   └─ Check: if count >= 1 → Block login

4. Login user
   ├─ Code: login(request, user)
   ├─ Django creates Session record:
   │  INSERT INTO auth_session 
   │  (session_key, session_data, expire_date)
   │  VALUES ('abc123', '{...}', 2026-08-15)
   └─ Sets response cookie: sessionid=abc123

5. Create session tracking record
   ├─ Code: UserLoginSession.objects.create()
   ├─ DB: INSERT INTO UserLoginSession
   │     (user_id, session_key, ip_address, user_agent, login_at)
   │     VALUES (5, 'abc123', '192.1.1.1', 'Mozilla...', now())
   └─ Result: UserLoginSession object created

6. Redirect to home
   ├─ Response: 302 /home/
   └─ Browser: Receives sessionid cookie


═══════════════════════════════════════════════════════════════════════════
LOGOUT FLOW
═══════════════════════════════════════════════════════════════════════════

1. User clicks logout
   ├─ Request: GET /logout/
   └─ Handler: logout_view()

2. Delete session tracking record
   ├─ Code: UserLoginSession.objects.filter(
   │         user=user, 
   │         session_key=request.session.session_key
   │      ).delete()
   ├─ Query: SELECT * FROM UserLoginSession 
   │         WHERE user_id=5 AND session_key='abc123'
   ├─ DB: DELETE FROM UserLoginSession WHERE ...
   └─ Result: 1 record deleted

3. Django logout
   ├─ Code: logout(request)
   ├─ DB: DELETE FROM auth_session WHERE session_key='abc123'
   ├─ Response: Set-Cookie: sessionid=empty; expires=past
   └─ Browser: Clears session cookie

4. Redirect to login
   ├─ Response: 302 /login/
   └─ Browser: Redirects to login page


═══════════════════════════════════════════════════════════════════════════
GRANT BOOK ACCESS (ADMIN)
═══════════════════════════════════════════════════════════════════════════

1. Admin selects user + book
   ├─ Admin page: /admin/books/flipbookaccess/add/
   └─ Form: Select user, select flipbook

2. System validates unique constraint
   ├─ Query: SELECT * FROM FlipBookAccess 
   │         WHERE user_id=5 AND flipbook_id=3
   ├─ Check: If exists → Error
   └─ If not → Continue

3. Create access record
   ├─ Code: FlipBookAccess.objects.create(user=user, flipbook=book)
   ├─ DB: INSERT INTO books_flipbookaccess
   │     (user_id, flipbook_id, granted_at)
   │     VALUES (5, 3, now())
   └─ Result: Access granted instantly

4. User sees book
   ├─ Next time home_view() called:
   ├─ accessible_ids = list(FlipBookAccess.objects
   │                         .filter(user=request.user)
   │                         .values_list('flipbook_id'))
   ├─ Book appears in list if id in accessible_ids
   └─ User can click and view


═══════════════════════════════════════════════════════════════════════════
CLEANUP ORPHANED SESSIONS (MANUAL)
═══════════════════════════════════════════════════════════════════════════

Command: python manage.py cleanup_sessions

1. Get all valid Django session keys
   ├─ Query: SELECT session_key FROM auth_session
   └─ Result: Set(['abc123', 'def456', ...])

2. Find orphaned UserLoginSession records
   ├─ Query: SELECT * FROM UserLoginSession 
   │         WHERE session_key NOT IN (valid keys)
   └─ Result: Records with deleted Django sessions

3. Delete orphaned records
   ├─ DB: DELETE FROM UserLoginSession WHERE ...
   └─ Result: N records deleted

4. Delete expired Django sessions
   ├─ Query: SELECT * FROM auth_session 
   │         WHERE expire_date < now()
   ├─ DB: DELETE FROM auth_session WHERE ...
   └─ Result: M records deleted


═══════════════════════════════════════════════════════════════════════════
VIEW BOOK (AUTHENTICATED USER)
═══════════════════════════════════════════════════════════════════════════

1. User clicks book
   ├─ Request: GET /book/5/
   └─ Handler: flipbook_view()

2. Check access
   ├─ Query: SELECT * FROM books_flipbookaccess 
   │         WHERE user_id=5 AND flipbook_id=5
   ├─ Found? YES → Continue
   └─ Found? NO → Error message, redirect

3. Get book details
   ├─ Query: SELECT * FROM books_flipbook WHERE id=5
   ├─ Result: FlipBook object with pages
   └─ pages = ['/media/books/5/page_1.jpg', ...]

4. Track view
   ├─ Code: BookView.objects.create(...)
   ├─ DB: INSERT INTO books_bookview
   │     (book_id, user_id, ip_address, viewed_at)
   │     VALUES (5, 5, '192.1.1.1', now())
   └─ Result: View recorded

5. Render template
   ├─ Template: books/flipbook.html
   ├─ Context: { book, pages, total_pages }
   └─ JavaScript: Flipbook viewer shows pages
```

---

## 🚨 EMERGENCY COMMANDS

```bash
# When users can't login (orphaned sessions)
python manage.py cleanup_sessions

# Force clear ALL sessions (use only if cleanup doesn't work)
python manage.py cleanup_sessions --force

# Check state via Django shell
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> from books.models import UserLoginSession
>>> Session.objects.count()  # Should be low
>>> UserLoginSession.objects.count()  # Should be low

# Logout specific user
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(id=5)
>>> UserLoginSession.objects.filter(user=user).delete()

# Check if book access working
>>> from books.models import FlipBookAccess, User, FlipBook
>>> user = User.objects.get(id=5)
>>> access = FlipBookAccess.objects.filter(user=user)
>>> [a.flipbook.title for a in access]
['Book 1', 'Book 2', ...]
```

