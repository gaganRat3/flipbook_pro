# In-App Notification Process

This document describes the process for generating and displaying in-app notifications when a user is granted access to a FlipBook after an unlock request is approved.

## 1. Notification Trigger
- When an admin approves an unlock request in the Django admin panel, the `mark_as_approved` action is triggered.
- This action creates a new `Notification` object for the user associated with the unlock request.
- The notification message is: `You now have access to '[Book Title]'!`

## 2. Notification Model
- Defined in `books/models.py`:
  - `user`: ForeignKey to User
  - `message`: CharField
  - `created_at`: DateTimeField (auto_now_add)
  - `is_read`: BooleanField (default False)

## 3. Notification Creation (Admin Action)
- In `books/admin.py`, inside `UnlockRequestAdmin.mark_as_approved`:
  - After granting access, a `Notification` is created for the user.

## 4. Notification Display (Frontend)
- On the user dashboard/home page (`books/home.html`):
  - A notification bell icon is shown.
  - Clicking the bell displays a dropdown with recent notifications.
  - Each notification shows the message and timestamp.
  - Unread notifications can be highlighted.

## 5. Marking Notifications as Read
- When a user views their notifications, notifications can be marked as read (future enhancement).

## 6. Summary
- Users are notified in-app when their unlock request is approved and access is granted.
- The process is automatic and requires no user action to receive notifications.

---

**Related Files:**
- `books/models.py` (Notification model)
- `books/admin.py` (Notification creation in admin action)
- `templates/books/home.html` (Notification dropdown UI)
