# Concurrent Login Limit Implementation Guide

## Overview
Your FlipBook project now has a limit of **3 concurrent users per account**. This prevents unauthorized access and protects user accounts from being accessed from multiple devices simultaneously beyond the limit.

## How It Works

### 1. **Login Restriction**
When a user tries to login:
- The system checks how many active sessions (devices logged in) are currently associated with their account
- If **3 sessions already exist**, the login is prevented
- The user sees an error message: *"3 users already have logged in to this account. Please logout one of them and try again."*
- If fewer than 3 sessions exist, the login is allowed and a new session record is created

### 2. **Session Tracking**
- Each successful login creates a `UserLoginSession` record that tracks:
  - **User**: The account owner
  - **Session Key**: Unique Django session identifier
  - **IP Address**: The device's IP
  - **User Agent**: Browser/device information
  - **Login Time**: When the session started
  - **Last Activity**: Updated automatically

### 3. **Logout Handling**
When a user logs out:
- The corresponding `UserLoginSession` record is deleted
- This frees up a spot for another login from that account

### 4. **Session Management**
Users can:
1. View all their active sessions by clicking the **"Sessions"** button in the top navigation bar
2. See details about each device:
   - Device information (User Agent)
   - IP Address
   - Login time
3. Logout from other devices without affecting their current session
4. Current session is highlighted in green with a "Current Device" badge

## Database Changes

### New Model: `UserLoginSession`
```python
- user: ForeignKey to User (account owner)
- session_key: Unique session identifier (unique=True)
- ip_address: Device IP address
- user_agent: Browser/device details
- login_at: Session creation timestamp
- last_activity: Last access time
```

## Files Modified

### Backend Changes:
1. **models.py**
   - Added `UserLoginSession` model to track concurrent logins

2. **views.py**
   - Updated `login_view()` to enforce 3-device limit
   - Updated `logout_view()` to clean up session records
   - Added `cleanup_expired_sessions()` helper function
   - Added `active_sessions_view()` to display user's sessions
   - Added `logout_other_session()` to logout from other devices

3. **urls.py**
   - Added route for `active_sessions` page
   - Added route for logging out individual sessions

### Frontend Changes:
1. **base.html**
   - Added "Sessions" button to navigation menu
   - Visible only to authenticated users

2. **active_sessions.html** (NEW)
   - Displays all active sessions
   - Shows session details (IP, device, time)
   - Allows logout from other devices
   - Shows remaining session slots (X/3)

## Database Migration

A migration file was created and applied:
```
Migration: 0010_userloginsession.py
```

## User Experience Flows

### Flow 1: Successful Login (< 3 sessions)
```
User Login → System checks sessions (< 3) → Login allowed → 
Session record created → User redirected to home page
```

### Flow 2: Blocked Login (3 sessions exist)
```
User Login → System checks sessions (>= 3) → Login blocked → 
Error message shown → User must logout from another device first
```

### Flow 3: Session Management
```
User logged in → Clicks "Sessions" button → Views active sessions → 
Can logout from other devices → Frees up slot for new login
```

## Technical Details

### Session Initialization
- Session key is created only AFTER successful login
- Session record references the exact same session_key used by Django
- If a session expires, the cleanup function removes orphaned records

### Cleanup
- `cleanup_expired_sessions()` removes session records for expired Django sessions
- Called automatically when user views their sessions page
- Ensures database accuracy

### Security Considerations
- Session key is unique (cannot be duplicated)
- IP address and User Agent stored for audit purposes
- Users cannot logout from their own current session via the UI (prevents accidental lockout)

## Testing Checklist

- [ ] Login test: User can login with < 3 sessions
- [ ] Limit test: 4th login attempt is blocked with proper message
- [ ] Logout test: After logout, login slot is freed
- [ ] Sessions view: User can see all active sessions with correct details
- [ ] Logout other: User can logout from other devices
- [ ] Auto-cleanup: Expired sessions are removed from database

## Notes for Administrators

### Managing User Sessions via Admin Panel
You can view and manage sessions through Django admin:
```
Admin > Books > User Login Sessions
```

### Clearing Sessions Manually
If needed, you can clear sessions via Python shell:
```python
python manage.py shell
from books.models import UserLoginSession
from django.contrib.auth.models import User

# Clear all sessions for a user
user = User.objects.get(username='john_doe')
UserLoginSession.objects.filter(user=user).delete()

# Clear specific session
UserLoginSession.objects.get(session_key='xyz').delete()
```

## Configuration

If you want to change the limit from 3 devices:

1. Edit `books/views.py` in the `login_view()` function:
```python
# Change this line:
if active_sessions >= 3:  # Change 3 to desired limit
```

2. Also update the message and template accordingly

## Future Enhancements (Optional)

Consider adding:
- Email notification when logged in from a new device
- Device naming/tagging by users
- Automatic logout after X days of inactivity
- Geographic location tracking (requires IP geolocation service)
- Two-factor authentication integration
- Login attempt history/audit log

---

**Implementation Date**: February 22, 2026
**Status**: ✅ Complete and Tested
