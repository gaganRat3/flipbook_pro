from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from books.models import UserLoginSession
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clean up expired and orphaned login sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force delete all UserLoginSession records (use with caution)',
        )
        parser.add_argument(
            '--reset-user',
            type=int,
            help='Reset login sessions for a specific user ID',
        )

    def handle(self, *args, **options):
        force = options.get('force')
        reset_user_id = options.get('reset_user')

        if force:
            # Delete ALL UserLoginSession records
            count = UserLoginSession.objects.count()
            UserLoginSession.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f'Force deleted {count} UserLoginSession records')
            )
            return

        if reset_user_id:
            # Reset sessions for specific user
            count = UserLoginSession.objects.filter(user_id=reset_user_id).delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f'Reset {count} sessions for user ID {reset_user_id}')
            )
            return

        # Normal cleanup: Remove UserLoginSession records that don't have a valid Django session
        valid_sessions = set(Session.objects.values_list('session_key', flat=True))
        orphaned = UserLoginSession.objects.exclude(session_key__in=valid_sessions)
        count = orphaned.count()
        orphaned.delete()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleaned up {count} orphaned session records')
        )

        # Also delete expired Django sessions
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        session_count = expired_sessions.count()
        expired_sessions.delete()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {session_count} expired Django session records')
        )
