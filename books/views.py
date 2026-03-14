from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import UsernameEmailAuthenticationForm, RegistrationForm
from django.contrib.auth.models import User
from django.contrib import messages
import json
from .models import FlipBook, BookView, Event, FlipBookAccess, UserProfile, UnlockRequest, UserLoginSession, UnlockRequestBook


def offline_view(request):
    return render(request, 'offline.html')


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def cleanup_expired_sessions():
    """Remove login sessions that no longer exist in Django's session table"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    
    try:
        # Get all active session keys in Django
        valid_sessions = set(Session.objects.values_list('session_key', flat=True))
        
        # Delete any UserLoginSession that references an expired session
        orphaned = UserLoginSession.objects.exclude(session_key__in=valid_sessions)
        deleted_count = orphaned.count()
        orphaned.delete()
        
        # Also clean up expired Django sessions
        expired = Session.objects.filter(expire_date__lt=timezone.now())
        expired.delete()
        
        return deleted_count
    except Exception as e:
        print(f"Error during session cleanup: {e}")
        return 0


@login_required
def active_sessions_view(request):
    """Show user their active login sessions and allow logout from other devices"""
    user = request.user
    # Exclude admin users from session management
    if user.is_staff or user.is_superuser:
        sessions = []
    else:
        sessions = UserLoginSession.objects.filter(user=user).order_by('-login_at')
    
    # Cleanup expired sessions
    cleanup_expired_sessions()
    
    # Recount after cleanup
    sessions = UserLoginSession.objects.filter(user=user).order_by('-login_at')
    
    context = {
        'sessions': sessions,
        'current_session_key': request.session.session_key,
    }
    return render(request, 'books/active_sessions.html', context)


@login_required
def logout_other_session(request, session_id):
    """Allow user to logout from another session/device"""
    if request.method == 'POST':
        # Exclude admin users from session management
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, "Admin users cannot manage sessions here.")
            return redirect('active_sessions')
        session = get_object_or_404(UserLoginSession, id=session_id, user=request.user)
        # Don't allow logout from current session
        if session.session_key == request.session.session_key:
            messages.error(request, "You cannot logout from your current session here. Use the logout button instead.")
            return redirect('active_sessions')
        session.delete()
        messages.success(request, "That session has been logged out successfully.")
    return redirect('active_sessions')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        mobile_number = request.POST.get('mobile_number')
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data.get('email')
            user.save()
            UserProfile.objects.create(user=user, mobile_number=mobile_number)
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegistrationForm()
    
    return render(request, 'books/register.html', {'form': form})


def login_view(request):
    """User login view (username, email, and password required)"""
    # Ensure session key exists before checking for existing sessions
    if not request.session.session_key:
        request.session.create()

    # Cleanup expired sessions before checking for active sessions
    cleanup_expired_sessions()

    if request.user.is_authenticated:
        return redirect('home')

    session_limit_error = False

    if request.method == 'POST':
        form = UsernameEmailAuthenticationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            # Check concurrent login limit (max 1)
            from django.contrib.sessions.models import Session
            user_sessions = UserLoginSession.objects.filter(user=user)
            stale_sessions = []
            for s in user_sessions:
                if not Session.objects.filter(session_key=s.session_key).exists():
                    stale_sessions.append(s.id)
            if stale_sessions:
                UserLoginSession.objects.filter(id__in=stale_sessions).delete()
            # Recount after cleanup
            active_sessions = UserLoginSession.objects.filter(user=user).count()
            if active_sessions >= 1:
                session_limit_error = True
                return render(request, 'books/login.html', {
                    'form': form,
                    'session_limit_error': True
                })
            # Login the user
            login(request, user)
            # Get IP address and user agent
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            # Create a new login session record
            try:
                # Ensure the session key is created
                if not request.session.session_key:
                    request.session.create()
                
                # Try to create the session record
                UserLoginSession.objects.create(
                    user=user,
                    session_key=request.session.session_key,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
            except Exception as e:
                # Log error but allow login to proceed
                print(f"Error creating UserLoginSession: {e}")
                import traceback
                traceback.print_exc()
            
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials. Please try again.")
    else:
        form = UsernameEmailAuthenticationForm()

    return render(request, 'books/login.html', {
        'form': form,
        'session_limit_error': session_limit_error
    })


def logout_view(request):
    """User logout view - Removes session from database."""
    if request.method != 'POST':
        return redirect('home')

    if request.user.is_authenticated:
        user = request.user
        session_key = request.session.session_key

        try:
            # Prefer exact match for current browser session.
            if session_key:
                deleted_count, _ = UserLoginSession.objects.filter(
                    user=user,
                    session_key=session_key
                ).delete()

                if deleted_count == 0:
                    # Fallback for any session-key mismatch edge case.
                    deleted_count, _ = UserLoginSession.objects.filter(user=user).delete()
            else:
                deleted_count, _ = UserLoginSession.objects.filter(user=user).delete()

        except Exception as e:
            print(f"Error removing UserLoginSession during logout: {e}")
            import traceback
            traceback.print_exc()

    # Django logout
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')



@login_required
def home_view(request):
    """Home page - list only flipbooks user can access, with event, gender, and category filtering"""
    # Ensure session key exists
    if not request.session.session_key:
        request.session.create()
    # Ensure UserLoginSession exists for authenticated user
    from .models import UserLoginSession
    if request.user.is_authenticated:
        session_key = request.session.session_key
        if not UserLoginSession.objects.filter(user=request.user, session_key=session_key).exists():
            ip_address = request.META.get('REMOTE_ADDR', '')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            UserLoginSession.objects.create(
                user=request.user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent
            )
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


# Page view for unlock request form (non-AJAX)
@login_required
def unlock_request_page_view(request, book_id):
    """Display unlock request form as a dedicated page"""
    book = get_object_or_404(FlipBook, id=book_id, is_published=True)
    all_books = FlipBook.objects.filter(is_published=True).order_by('title')
    accessible_ids = list(FlipBookAccess.objects.filter(user=request.user).values_list('flipbook_id', flat=True))
    context = {
        'book': book,
        'all_books': all_books,
        'accessible_ids': accessible_ids,
    }
    return render(request, 'books/unlock_request.html', context)


# Handle unlock request form submission (AJAX POST)
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .forms import UnlockRequestForm
from datetime import datetime

@csrf_protect
def unlock_request_view(request):
    if request.method == 'POST':
        # For AJAX: Ensure CSRF token is sent in the X-CSRFToken header.
        # Example JS:
        # function getCookie(name) {
        #     let cookieValue = null;
        #     if (document.cookie && document.cookie !== '') {
        #         const cookies = document.cookie.split(';');
        #         for (let i = 0; i < cookies.length; i++) {
        #             const cookie = cookies[i].trim();
        #             if (cookie.substring(0, name.length + 1) === (name + '=')) {
        #                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        #                 break;
        #             }
        #         }
        #     }
        #     return cookieValue;
        # }
        # $.ajaxSetup({
        #     beforeSend: function(xhr, settings) {
        #         if (!(/^GET|HEAD|OPTIONS|TRACE$/.test(settings.type)) && !this.crossDomain) {
        #             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        #         }
        #     }
        # });
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
                
                # Save selected books
                selected_books_ids = request.POST.getlist('selected_books')
                if selected_books_ids:
                    for book_id in selected_books_ids:
                        try:
                            selected_book = FlipBook.objects.get(id=int(book_id))
                            UnlockRequestBook.objects.create(
                                unlock_request=unlock_request,
                                flipbook=selected_book,
                                price=300
                            )
                        except (FlipBook.DoesNotExist, ValueError):
                            print(f"Invalid book ID: {book_id}")
                
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
