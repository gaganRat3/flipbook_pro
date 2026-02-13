from django.core.management.base import BaseCommand
from books.models import Event, FlipBook


class Command(BaseCommand):
    help = 'Show current events and books distribution'

    def handle(self, *args, **options):
        events = Event.objects.all()
        books = FlipBook.objects.all()
        
        self.stdout.write("Current Events:")
        for event in events:
            book_count = event.flipbooks.count()
            self.stdout.write(f"- {event.name} (ID: {event.id}) - {book_count} books")
            
        self.stdout.write("\nBooks distribution:")
        for book in books:
            event_name = book.event.name if book.event else "No event"
            self.stdout.write(f"  {book.title} -> {event_name}")