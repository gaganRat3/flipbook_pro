#!/usr/bin/env python
"""
Login Session Cleanup Script
Run this from the project root:
    python cleanup_login_sessions.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flipbook_project.settings')
django.setup()

from django.contrib.sessions.models import Session
from books.models import UserLoginSession
from django.utils import timezone

def cleanup_sessions():
    """Clean up expired and orphaned login sessions"""
    print("\n" + "=" * 70)
    print(" " * 15 + "CLEARING LOGIN SESSIONS")
    print("=" * 70)
    
    # Step 1: Count initial state
    initial_user_sessions = UserLoginSession.objects.count()
    initial_django_sessions = Session.objects.count()
    print(f"\nInitial state:")
    print(f"  - UserLoginSession records: {initial_user_sessions}")
    print(f"  - Django Session records: {initial_django_sessions}")
    
    # Step 2: Delete expired Django sessions
    expired = Session.objects.filter(expire_date__lt=timezone.now())
    exp_count = expired.count()
    if exp_count > 0:
        expired.delete()
        print(f"\n✓ Deleted {exp_count} expired Django sessions")
    else:
        print(f"\n✓ No expired Django sessions found")
    
    # Step 3: Delete orphaned UserLoginSession records
    valid_sessions = set(Session.objects.values_list('session_key', flat=True))
    orphaned = UserLoginSession.objects.exclude(session_key__in=valid_sessions)
    orphan_count = orphaned.count()
    if orphan_count > 0:
        orphaned.delete()
        print(f"✓ Deleted {orphan_count} orphaned UserLoginSession records")
    else:
        print(f"✓ No orphaned UserLoginSession records found")
    
    # Step 4: Show final state
    final_user_sessions = UserLoginSession.objects.count()
    final_django_sessions = Session.objects.count()
    
    print(f"\nFinal state:")
    print(f"  - UserLoginSession records: {final_user_sessions}")
    print(f"  - Django Session records: {final_django_sessions}")
    
    if final_user_sessions > 0:
        print(f"\nRemaining sessions:")
        for session in UserLoginSession.objects.all():
            print(f"  - User: {session.user.username}, IP: {session.ip_address}, Login: {session.login_at}")
    
    print("\n" + "=" * 70)
    print(" " * 20 + "CLEANUP COMPLETE!")
    print("=" * 70)
    print(f"\n✓ Total deleted: {initial_user_sessions - final_user_sessions} UserLoginSession(s)")
    print("\n→ You can now try logging in again!")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    try:
        cleanup_sessions()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
