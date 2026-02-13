from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from books.models import Event, FlipBook


class Command(BaseCommand):
    help = 'Consolidate duplicate events and merge similar events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually making changes',
        )
        parser.add_argument(
            '--sammelan-only',
            action='store_true',
            help='Only consolidate Sammelan-related events',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        sammelan_only = options['sammelan_only']

        self.stdout.write(
            self.style.SUCCESS('Starting event consolidation...')
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        # Find duplicate or similar events
        if sammelan_only:
            events = Event.objects.filter(name__icontains='sammelan')
        else:
            events = Event.objects.all()

        # Group events by similar names
        event_groups = self.group_similar_events(events)

        total_consolidated = 0
        for group in event_groups:
            if len(group) > 1:
                consolidated = self.consolidate_event_group(group, dry_run)
                total_consolidated += consolidated

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN: Would consolidate {total_consolidated} events'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully consolidated {total_consolidated} events'
                )
            )

    def group_similar_events(self, events):
        """Group events by similar names"""
        groups = []
        processed = set()

        for event in events:
            if event.id in processed:
                continue

            # Find similar events
            similar = [event]
            processed.add(event.id)

            for other_event in events:
                if other_event.id in processed:
                    continue

                if self.are_events_similar(event, other_event):
                    similar.append(other_event)
                    processed.add(other_event.id)

            groups.append(similar)

        return groups

    def are_events_similar(self, event1, event2):
        """Check if two events are similar enough to be consolidated"""
        name1 = event1.name.lower().strip()
        name2 = event2.name.lower().strip()

        # Check for same base name with variations
        if 'sammelan' in name1 and 'sammelan' in name2:
            return True

        # Check for very similar names (allowing for numbers, spaces, etc.)
        # Remove numbers, spaces, and common ordinal suffixes
        import re
        
        # Remove numbers, ordinal suffixes (st, nd, rd, th), and extra spaces
        def normalize_name(name):
            # Remove ordinal suffixes like "1st", "2nd", "3rd", "4th", etc.
            name = re.sub(r'\d+(st|nd|rd|th)', '', name)
            # Remove standalone numbers
            name = re.sub(r'\d+', '', name)
            # Remove extra spaces and normalize
            name = re.sub(r'\s+', ' ', name).strip()
            # Keep only alphabetic characters and single spaces
            return ''.join(c for c in name if c.isalpha() or c == ' ').strip()

        base1 = normalize_name(name1)
        base2 = normalize_name(name2)

        # Check if normalized names match
        if base1 and base2 and base1 == base2:
            return True
            
        # Also check for common patterns like "mela", "event", "conference"
        common_patterns = ['mela', 'event', 'conference', 'sammelan']
        for pattern in common_patterns:
            if pattern in base1 and pattern in base2 and len(base1) <= 10 and len(base2) <= 10:
                return True

        return False

    def consolidate_event_group(self, event_group, dry_run):
        """Consolidate a group of similar events"""
        if len(event_group) <= 1:
            return 0

        # Choose the primary event (oldest or with most books)
        primary_event = self.choose_primary_event(event_group)
        events_to_merge = [e for e in event_group if e.id != primary_event.id]

        self.stdout.write(
            f'Consolidating {len(events_to_merge)} events into "{primary_event.name}":'
        )

        books_moved = 0
        for event in events_to_merge:
            book_count = event.flipbooks.count()
            self.stdout.write(f'  - Merging "{event.name}" ({book_count} books)')

            if not dry_run:
                with transaction.atomic():
                    # Move all books to primary event
                    FlipBook.objects.filter(event=event).update(event=primary_event)
                    # Delete the duplicate event
                    event.delete()

            books_moved += book_count

        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ Moved {books_moved} books to "{primary_event.name}"'
                )
            )

        return len(events_to_merge)

    def choose_primary_event(self, event_group):
        """Choose which event should be the primary one"""
        # Prioritize by:
        # 1. Number of books (more books = primary)
        # 2. Creation date (older = primary)
        # 3. Cleaner name (shorter, without numbers)

        def event_score(event):
            book_count = event.flipbooks.count()
            # More books = higher score
            score = book_count * 1000
            # Older events = higher score
            score += (event.created_at.timestamp() / 100000)
            # Cleaner names = higher score (penalize names with numbers)
            if any(c.isdigit() for c in event.name):
                score -= 100
            return score

        return max(event_group, key=event_score)