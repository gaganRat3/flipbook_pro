from django.core.management.base import BaseCommand
from books.models import Event, FlipBook


class Command(BaseCommand):
    help = 'Test how books are grouped for the template'

    def handle(self, *args, **options):
        books = FlipBook.objects.filter(is_published=True).select_related('event').order_by('event__name', 'title')
        
        self.stdout.write("=== BOOKS ORDER FOR TEMPLATE ===")
        current_event = None
        for i, book in enumerate(books):
            if book.event != current_event:
                if current_event is not None:
                    self.stdout.write("")  # Empty line between events
                self.stdout.write(f"--- Event: {book.event.name if book.event else 'No Event'} ---")
                current_event = book.event
            self.stdout.write(f"  {i+1}. {book.title}")
            
        # Simulate template regroup logic
        self.stdout.write("\n=== TEMPLATE REGROUP SIMULATION ===")
        from itertools import groupby
        books_by_event = groupby(books, key=lambda b: b.event)
        
        for event, group in books_by_event:
            event_name = event.name if event else "No Event"
            books_in_event = list(group)
            self.stdout.write(f"Event Section: {event_name}")
            for book in books_in_event:
                self.stdout.write(f"  - {book.title}")
            self.stdout.write("")