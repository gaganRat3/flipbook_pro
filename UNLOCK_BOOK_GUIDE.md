# 🔓 FlipBook Access Control - Troubleshooting & Setup Guide

## ✅ How to Grant Book Access to Users

Your application has **three ways** to grant flipbook access to users:

---

## **Method 1: Custom Admin Panel** (Recommended)

### Access the Panel:

1. Go to Django Admin: `http://yoursite.com/admin/`
2. Navigate to: **Books → FlipBook Access → User-FlipBook Access Management**
   - Or direct URL: `/admin/books/flipbookaccess/user-access/`

### How to Use:

1. **Find the user** in the table (username and email are shown)
2. **Check the flipbooks** you want to grant access to
   - Scroll in the box to see all available books
   - Check the checkbox next to the book name
3. **Click "Save Changes"** button at the bottom
4. **Success message** will confirm the update

### Example:

```
User: admin
Email: admin@example.com

✓ 32th mela          ← Book is now accessible
☐ Another Book
☐ Third Book
```

---

## **Method 2: Standard Django Admin**

1. Go to Django Admin: `http://yoursite.com/admin/`
2. Navigate to: **Books → FlipBook Access**
3. **Click "Add FlipBook Access"**
4. Select:
   - **User**: admin
   - **FlipBook**: 32th mela
5. **Click "Save"**

---

## **Method 3: Management Command**

```bash
# Inside your project directory
python manage.py shell

# In the Django shell:
from django.contrib.auth.models import User
from books.models import FlipBook, FlipBookAccess

user = User.objects.get(username='admin')
book = FlipBook.objects.get(title='32th mela')
FlipBookAccess.objects.get_or_create(user=user, flipbook=book)

# Verify:
FlipBookAccess.objects.filter(user=user)
```

---

## 🐛 Troubleshooting

### ❌ **Problem: Book still shows as "Locked" after granting access**

**Check 1: Verify Access Was Saved**

1. Go to: `http://yoursite.com/admin/debug/access/` (staff users only)
2. Look for your username and the book title
3. If it's not there, the access wasn't saved

**Check 2: Clear Browser Cache**

- Press: `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
- Clear: Cached images and files
- Reload the page

**Check 3: Log Out and Back In**

- The access list is loaded when you log in
- Log out, clear cookies, and log back in

**Check 4: Verify the Form Submission**

1. In Admin Panel, check the HTML:
   - Right-click → Inspect Element
   - Look for: `<input type="checkbox" name="flipbooks_[user_id]" value="[book_id]">`
2. Make sure it's checked before saving

---

### ❌ **Problem: FlipBook Access admin page is blank**

**Solution:**

1. Make sure you're logged in as staff/superuser
2. URL should be: `/admin/books/flipbookaccess/user-access/`
3. Check that there are users in the system
4. Check that there are flipbooks created

---

### ❌ **Problem: Can't find "User-FlipBook Access Management"**

**Make sure you:**

1. Are logged in as superuser or staff member
2. Go to: Django Admin → Books → FlipBook Access
3. Click the "User-FlipBook Access" link in the breadcrumb
4. Or directly visit: `/admin/books/flipbookaccess/user-access/`

---

### ❌ **Problem: "You do not have access to this booklet" error**

**This means:**

- The `FlipBookAccess` record wasn't created
- The user-book pair doesn't exist in the database

**Solution:**

1. Go to Admin Panel as shown above
2. Find the user
3. **Check** the flipbook checkbox
4. Click **Save Changes**
5. Refresh the home page

---

## 🔍 How the Access System Works

### Behind the Scenes:

**In the database:**

```
FlipBookAccess Table:
┌────────┬──────────┬────────────┐
│ USER   │ FLIPBOOK │ GRANTED_AT │
├────────┼──────────┼────────────┤
│ admin  │ 32th ... │ 2026-02-03 │
└────────┴──────────┴────────────┘
```

**When user visits home page:**

1. Django queries: "Get all books this user can access"
   ```python
   accessible_ids = FlipBookAccess.objects.filter(user=request.user)
   ```
2. Shows books with ✅ **Accessible** badge
3. Hides other books with 🔒 **Locked** badge

**When user clicks a book:**

1. Django checks: "Does this user have access?"
   ```python
   if FlipBookAccess.objects.filter(user=user, flipbook_id=book_id).exists():
       # Allow access
   else:
       # Show error: "You do not have access"
   ```

---

## 📊 Debug Information

### Check Access via Django Shell:

```bash
python manage.py shell

# Import models
from django.contrib.auth.models import User
from books.models import FlipBook, FlipBookAccess

# Get your user
user = User.objects.get(username='admin')

# Check how many books they can access
access_count = FlipBookAccess.objects.filter(user=user).count()
print(f"Admin has access to {access_count} books")

# List all books they can access
accessible_books = FlipBookAccess.objects.filter(user=user).values_list('flipbook__title', flat=True)
print("Books accessible to admin:")
for book in accessible_books:
    print(f"  - {book}")

# Check specific book
book = FlipBook.objects.get(title='32th mela')
has_access = FlipBookAccess.objects.filter(user=user, flipbook=book).exists()
print(f"Admin has access to '32th mela': {has_access}")

# Create access if needed
FlipBookAccess.objects.get_or_create(user=user, flipbook=book)
print("Access granted!")
```

---

## 🎯 Quick Checklist

- [ ] User account is **active** (not deactivated)
- [ ] FlipBook is **published** (`is_published = True`)
- [ ] **FlipBookAccess** record exists in database
- [ ] User **logged out and logged back in** after granting access
- [ ] Checked admin page: `/admin/debug/access/`
- [ ] Cleared browser cache (Ctrl+Shift+Delete)

---

## 📞 Still Having Issues?

1. **Check the debug page:** `/admin/debug/access/` (staff only)
2. **Check database directly:**
   ```bash
   python manage.py dbshell
   SELECT * FROM books_flipbookaccess WHERE user_id=1;
   ```
3. **Check logs:** Look for error messages in Django console

---

**Last Updated:** February 3, 2026
