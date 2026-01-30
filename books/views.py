from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import UsernameMobileAuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
import json
from .models import FlipBook, BookView, Event, FlipBookAccess, UserProfile


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        mobile_number = request.POST.get('mobile_number')
        if form.is_valid():
            user = form.save()
            # Save mobile number
            UserProfile.objects.create(user=user, mobile_number=mobile_number)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'books/register.html', {'form': form})


def login_view(request):
    """User login view (username, mobile, and password required)"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UsernameMobileAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid login details.")
    else:
        form = UsernameMobileAuthenticationForm()

    return render(request, 'books/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')



@login_required
def home_view(request):
    """Home page - list only flipbooks user can access, with event, gender, and category filtering"""
    accessible_ids = list(FlipBookAccess.objects.filter(user=request.user).values_list('flipbook_id', flat=True))
    books = FlipBook.objects.filter(is_published=True)
    events = Event.objects.filter(is_active=True)

    # Sammelan logic: if 'sammelan' param is present, show all event buttons
    show_sammelan = request.GET.get('sammelan', None) == 'true'

    # Check if user selected "My FlipBook" filter
    my_books_filter = request.GET.get('my_books', None)
    if my_books_filter == 'true':
        books = books.filter(id__in=accessible_ids)

    # Get selected event from query parameter
    selected_event = request.GET.get('event', None)
    if selected_event:
        try:
            selected_event = int(selected_event)
            books = books.filter(event_id=selected_event)
        except (ValueError, TypeError):
            selected_event = None

    # Gender sub-filter (renamed for template logic)
    selected_gender = request.GET.get('gender', None)
    if selected_gender == 'girl':
        books = books.filter(title__icontains='girl')
    elif selected_gender == 'boy':
        books = books.filter(title__icontains='boy')

    # Category sub-filter
    selected_category = request.GET.get('category', None)
    if selected_category:
        books = books.filter(title__icontains=selected_category)

    # Sort books: accessible first, then locked
    books = sorted(books, key=lambda b: b.id not in accessible_ids)

    # Category button lists
    girl_categories = [
        'NRI Girls',
        'Gujarat Girls',
        'Saurashtra Girls',
        'Mumbai Mah Rest of India (MMR) Girls',
        'Doctor Girls',
        'Divorce & Widow Girls',
    ]
    boy_categories = [
        'NRI Boys',
        'Gujarat Boys',
        'Saurashtra Boys',
        'Mumbai Mah Rest of India (MMR) Boys',
        'Doctor Boys',
        'Divorce & Widow Boys',
    ]

    context = {
        'books': books,
        'events': events,
        'selected_event': selected_event,
        'selected_gender': selected_gender,
        'selected_category': selected_category,
        'accessible_ids': accessible_ids,
        'my_books_filter': my_books_filter,
        'show_sammelan': show_sammelan,
        'girl_categories': girl_categories,
        'boy_categories': boy_categories,
    }
    return render(request, 'books/home.html', context)


@login_required
def flipbook_view(request, book_id):
    """View individual flipbook only if user has access"""
    # Check access
    if not FlipBookAccess.objects.filter(user=request.user, flipbook_id=book_id).exists():
        messages.error(request, "You do not have access to this booklet.")
        return redirect('home')
    
    book = get_object_or_404(FlipBook, id=book_id, is_published=True)
    
    # Track view
    BookView.objects.create(
        book=book,
        user=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request)
    )
    
    # Get all page URLs
    pages = book.get_pages()
    
    context = {
        'book': book,
        'pages': json.dumps(pages),  # Convert to JSON for JavaScript
        'pages_list': pages,  # Keep as list for template iteration
        'total_pages': book.total_pages,
    }
    
    return render(request, 'books/flipbook.html', context)


# Handle unlock request form submission (AJAX POST)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import UnlockRequestForm

@csrf_exempt  # If you use AJAX, ensure CSRF token is handled in JS; otherwise, remove this and use @require_POST
def unlock_request_view(request):
    if request.method == 'POST':
        data = request.POST.copy()
        files = request.FILES.copy()
        form = UnlockRequestForm(data, files)
        if form.is_valid():
            unlock_request = form.save(commit=False)
            if request.user.is_authenticated:
                unlock_request.user = request.user
            unlock_request.save()
            return JsonResponse({'success': True, 'message': 'Request submitted successfully.'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
