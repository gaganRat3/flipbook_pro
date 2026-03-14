"""
Django Shell Script to Clear Login Sessions

Run this in Django shell:
python manage.py shell

Then paste the content below:
"""

from django.contrib.sessions.models import Session
from books.models import UserLoginSession
from django.utils import timezone

print("=" * 60)
print("CLEARING LOGIN SESSIONS")
print("=" * 60)

# Step 1: Delete all expired Django sessions
expired = Session.objects.filter(expire_date__lt=timezone.now())
exp_count = expired.count()
expired.delete()
print(f"\n✓ Deleted {exp_count} expired Django sessions")

# Step 2: Delete orphaned UserLoginSession records
valid_sessions = set(Session.objects.values_list('session_key', flat=True))
orphaned = UserLoginSession.objects.exclude(session_key__in=valid_sessions)
orphan_count = orphaned.count()
orphaned.delete()
print(f"✓ Deleted {orphan_count} orphaned UserLoginSession records")

# Step 3: Show remaining sessions
remaining = UserLoginSession.objects.count()
print(f"✓ Remaining UserLoginSession records: {remaining}")

if remaining > 0:
    print("\nRemaining sessions:")
    for session in UserLoginSession.objects.all():
        print(f"  - User: {session.user.username}, IP: {session.ip_address}, Login: {session.login_at}")

print("\n" + "=" * 60)
print("CLEANUP COMPLETE")
print("=" * 60)
print("\nNow try logging in again!")
