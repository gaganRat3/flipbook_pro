from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import Event, FlipBook
import re


class Command(BaseCommand):
    help = 'Separate consolidated events back into individual events based on book titles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS('Starting event separation...')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Get all books
        books = FlipBook.objects.all()
        
        # Group books by their intended events (based on titles)
        book_groups = {}
        
        for book in books:
            intended_event = self.determine_event_from_title(book.title)
            if intended_event not in book_groups:
                book_groups[intended_event] = []
            book_groups[intended_event].append(book)

        # Create/find events and assign books
        for event_name, book_list in book_groups.items():
            self.stdout.write(f"\nProcessing event: '{event_name}' with {len(book_list)} books")
            
            for book in book_list:
                self.stdout.write(f"  - {book.title}")

            if not dry_run:
                with transaction.atomic():
                    # Create or get the event
                    event, created = Event.objects.get_or_create(name=event_name)
                    
                    if created:
                        self.stdout.write(f"  ✓ Created new event: '{event_name}'")
                    else:
                        self.stdout.write(f"  ✓ Using existing event: '{event_name}'")

                    # Move books to this event
                    for book in book_list:
                        book.event = event
                        book.save()
                    
                    self.stdout.write(f"  ✓ Moved {len(book_list)} books to '{event_name}'")

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN: Would create {len(book_groups)} separate events')
            )
        else:
            # Clean up empty events
            empty_events = Event.objects.filter(flipbooks__isnull=True)
            if empty_events.exists():
                count = empty_events.count()
                empty_events.delete()
                self.stdout.write(f"  ✓ Removed {count} empty events")
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully separated books into {len(book_groups)} events')
            )

    def determine_event_from_title(self, title):
        """Determine which event a book should belong to based on its title"""
        title_lower = title.lower()
        
        # Extract mela number from title
        mela_match = re.search(r'(\d+)(?:th|st|nd|rd)?\s*mela', title_lower)
        if mela_match:
            number = mela_match.group(1)
            return f"{number} mela"
        
        # Check for specific patterns
        if '32' in title_lower and 'mela' in title_lower:
            return "32 mela"
        elif '33' in title_lower and ('mela' in title_lower or '33' in title_lower):
            return "33 mela"  
        elif '34' in title_lower and 'mela' in title_lower:
            return "34 mela"
        
        # Default fallback - try to extract event name from title
        if 'mela' in title_lower:
            # Try to find a number before 'mela'
            number_match = re.search(r'(\d+)', title_lower)
            if number_match:
                return f"{number_match.group(1)} mela"
        
        # If no specific pattern found, use a generic name
        return "General Events"