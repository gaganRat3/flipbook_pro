from django.core.management.base import BaseCommand
from books.models import Event, FlipBook


class Command(BaseCommand):
    help = 'Check for duplicate events and show detailed info'

    def handle(self, *args, **options):
        events = Event.objects.all().order_by('name', 'id')
        books = FlipBook.objects.all()
        
        self.stdout.write("=== ALL EVENTS (Detailed) ===")
        for event in events:
            book_count = event.flipbooks.count()
            self.stdout.write(f"ID: {event.id} | Name: '{event.name}' | Books: {book_count}")
            # Show the books for this event
            event_books = event.flipbooks.all()
            for book in event_books:
                self.stdout.write(f"    - {book.title}")
            
        # Check for events with the same name
        self.stdout.write("\n=== CHECKING FOR DUPLICATES ===")
        event_names = {}
        for event in events:
            if event.name in event_names:
                event_names[event.name].append(event)
            else:
                event_names[event.name] = [event]
        
        for name, event_list in event_names.items():
            if len(event_list) > 1:
                self.stdout.write(f"DUPLICATE FOUND: '{name}' has {len(event_list)} entries:")
                for event in event_list:
                    self.stdout.write(f"  - ID: {event.id}, Books: {event.flipbooks.count()}")
            
        self.stdout.write(f"\nTotal events: {events.count()}")
        self.stdout.write(f"Total books: {books.count()}")