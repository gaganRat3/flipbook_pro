from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import UsernameMobileAuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
import json
from .models import FlipBook, BookView, Event, FlipBookAccess, UserProfile, UnlockRequest


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

    # Mela type filter (shows when event is selected)
    selected_mela_type = request.GET.get('mela_type', None)
    if selected_mela_type == 'boys':
        books = books.filter(title__icontains='boy')
    elif selected_mela_type == 'girls':
        books = books.filter(title__icontains='girl')

    # Category sub-filter
    selected_category = request.GET.get('category', None)
    if selected_category:
        books = books.filter(title__icontains=selected_category)

    # Order books by event, then accessible status
    # This ensures the regroup template tag works properly
    books = books.select_related('event').order_by('event__name', 'title')

    # Category button lists
    girl_categories = [
        'NRI Girls',
        'Gujarat Girls',
        'Saurashtra Girls',
        'Mumbai Mah Rest of India (MMR) Girls',
        'Divorce & Widow Girls',
    ]
    boy_categories = [
        'NRI Boys',
        'Gujarat Boys',
        'Saurashtra Boys',
        'Mumbai Mah Rest of India (MMR) Boys',
        'Divorce & Widow Boys',
    ]

    # Categories for filtering
    categories = [
        {'id': 'nri', 'name': 'NRI'},
        {'id': 'gujarat', 'name': 'Gujarat'},
        {'id': 'saurashtra', 'name': 'Saurashtra'},
        {'id': 'mumbai', 'name': 'Mumbai MMR'},
        {'id': 'divorce-widow', 'name': 'Divorce & Widow'},
    ]

    context = {
        'books': books,
        'events': events,
        'selected_event': selected_event,
        'selected_gender': selected_gender,
        'selected_mela_type': selected_mela_type,
        'selected_category': selected_category,
        'accessible_ids': accessible_ids,
        'my_books_filter': my_books_filter,
        'show_sammelan': show_sammelan,
        'girl_categories': girl_categories,
        'boy_categories': boy_categories,
        'categories': categories,
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
from datetime import datetime

@csrf_exempt  # If you use AJAX, ensure CSRF token is handled in JS; otherwise, remove this and use @require_POST
def unlock_request_view(request):
    if request.method == 'POST':
        try:
            data = request.POST.copy()
            files = request.FILES.copy()
            
            # Debug: Log the received date
            print(f"Received date_of_birth: {data.get('date_of_birth')}")
            
            form = UnlockRequestForm(data, files)
            if form.is_valid():
                flipbook = form.cleaned_data['flipbook']
                candidate_full_name = form.cleaned_data['candidate_full_name']
                date_of_birth = form.cleaned_data['date_of_birth']
                parents_mobile_number = form.cleaned_data['parents_mobile_number']
                marital_status = form.cleaned_data['marital_status']

                # Check for existing request (customize fields as needed)
                existing = UnlockRequest.objects.filter(
                    flipbook=flipbook,
                    candidate_full_name=candidate_full_name,
                    date_of_birth=date_of_birth,
                    parents_mobile_number=parents_mobile_number,
                    marital_status=marital_status,
                )
                if request.user.is_authenticated:
                    existing = existing.filter(user=request.user)

                if existing.exists():
                    return JsonResponse({'success': False, 'error': 'A request with these details already exists.'}, status=400)

                unlock_request = form.save(commit=False)
                if request.user.is_authenticated:
                    unlock_request.user = request.user
                unlock_request.save()
                return JsonResponse({'success': True, 'message': 'Request submitted successfully.'})
            else:
                print(f"Form errors: {form.errors}")
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        except Exception as e:
            import traceback
            print(f"Exception in unlock_request_view: {str(e)}")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e), 'traceback': traceback.format_exc()}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


@login_required
def debug_access_view(request):
    """Debug view to check user's flipbook access (staff only)"""
    if not request.user.is_staff:
        return redirect('home')
    
    # Get all users and their access
    users = User.objects.filter(is_active=True).exclude(is_superuser=True)
    flipbooks = FlipBook.objects.filter(is_published=True)
    
    data = []
    for user in users:
        accessible = FlipBookAccess.objects.filter(user=user).values_list('flipbook__title', flat=True)
        data.append({
            'username': user.username,
            'email': user.email,
            'access_count': len(accessible),
            'books': list(accessible) if accessible else ['(no access)']
        })
    
    html = '<h1>User FlipBook Access Debug</h1>'
    html += '<style>table { border-collapse: collapse; width: 100%; margin: 20px 0; } th, td { border: 1px solid #ddd; padding: 10px; text-align: left; } th { background-color: #f0f0f0; font-weight: bold; } tr:nth-child(even) { background-color: #f9f9f9; }</style>'
    html += '<table><tr><th>Username</th><th>Email</th><th>Access Count</th><th>Books</th></tr>'
    
    for item in data:
        html += f'<tr><td>{item["username"]}</td><td>{item["email"]}</td><td>{item["access_count"]}</td><td>{", ".join(item["books"])}</td></tr>'
    
    html += '</table>'
    html += f'<p><strong>Total Users:</strong> {len(data)}</p>'
    html += f'<p><strong>Total FlipBooks:</strong> {flipbooks.count()}</p>'
    html += f'<p><a href="/admin/books/flipbookaccess/user-access/">Go to Access Manager →</a></p>'
    
    from django.http import HttpResponse
    return HttpResponse(html)
