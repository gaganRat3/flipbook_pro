from django.contrib import admin
from .models import FlipBook, BookView, Event, FlipBookAccess, UserProfile
from .models import UnlockRequest
from django.utils.html import format_html
from django.contrib import messages

@admin.register(UnlockRequest)
class UnlockRequestAdmin(admin.ModelAdmin):
    list_display = ('flipbook', 'candidate_full_name', 'date_of_birth', 'parents_mobile_number', 'marital_status', 'status', 'submitted_at', 'user')
    list_filter = ('status', 'flipbook', 'marital_status', 'user')
    search_fields = ('candidate_full_name', 'parents_mobile_number')
    readonly_fields = ('submitted_at',)
    actions = ['mark_as_pending', 'mark_as_approved', 'mark_as_rejected']
    
    fieldsets = (
        ('Candidate Information', {
            'fields': ('flipbook', 'candidate_full_name', 'date_of_birth', 'parents_mobile_number', 'marital_status')
        }),
        ('Request Status', {
            'fields': ('status', 'submitted_at', 'user')
        }),
        ('Terms & Conditions', {
            'fields': ('terms_accepted',)
        }),
    )
    
    # Custom Actions for Status Update
    def mark_as_pending(self, request, queryset):
        """Mark selected unlock requests as pending"""
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} request(s) marked as Pending.')
    mark_as_pending.short_description = '✓ Mark as Pending'
    
    def mark_as_approved(self, request, queryset):
        """Mark selected unlock requests as approved"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} request(s) marked as Approved.')
    mark_as_approved.short_description = '✓ Mark as Approved'
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected unlock requests as rejected"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} request(s) marked as Rejected.')
    mark_as_rejected.short_description = '✗ Mark as Rejected'
    
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path
from django import forms
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'icon', 'book_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'color_preview', 'book_count']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('name', 'description', 'icon', 'color', 'color_preview'),
            'description': 'Create events to categorize your flipbooks. Check if a similar event already exists before creating a new one.'
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('book_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_preview(self, obj):
        return f'<div style="width: 50px; height: 50px; background-color: {obj.color}; border-radius: 8px; border: 2px solid #ddd; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"></div>'
    color_preview.short_description = 'Color Preview'
    color_preview.allow_tags = True

    def book_count(self, obj):
        count = obj.flipbooks.count()
        return f'{count} book{"s" if count != 1 else ""}'
    book_count.short_description = 'Books Count'

    class Media:
        js = ('admin/js/event_admin.js',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # If creating new event
            messages.success(request, f"Event '{obj.name}' created successfully!")


@admin.register(FlipBook)
class FlipBookAdmin(admin.ModelAdmin):
    list_display = ['title', 'event', 'thumbnail_preview', 'created_by', 'total_pages', 'is_published', 'created_at']
    list_filter = ['is_published', 'event', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['total_pages', 'thumbnail_preview', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'description', 'event', 'pdf_file', 'thumbnail', 'thumbnail_preview')
        }),
        ('Settings', {
            'fields': ('is_published', 'created_by')
        }),
        ('Metadata', {
            'fields': ('total_pages', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            # Order events by name for easier selection
            kwargs["queryset"] = Event.objects.filter(is_active=True).order_by('name')
        if db_field.name == "created_by":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
            return forms.ModelChoiceField(queryset=kwargs["queryset"])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/event_admin.js',)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return f'<img src="{obj.thumbnail.url}" style="max-width: 200px; max-height: 200px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />'
        return '<span style="color: #999;">No thumbnail</span>'
    thumbnail_preview.short_description = 'Thumbnail Preview'
    thumbnail_preview.allow_tags = True

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "created_by":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
            return forms.ModelChoiceField(queryset=kwargs["queryset"])
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(BookView)
class BookViewAdmin(admin.ModelAdmin):
    list_display = ['book', 'user', 'ip_address', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['book__title', 'ip_address']
    readonly_fields = ['book', 'user', 'ip_address', 'viewed_at']


class GrantFlipBookAccessForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="User")
    flipbook = forms.ModelChoiceField(queryset=FlipBook.objects.all(), label="FlipBook")


def grant_flipbook_access_view(request, admin_site):
    if request.method == 'POST':
        form = GrantFlipBookAccessForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            flipbook = form.cleaned_data['flipbook']
            from .models import FlipBookAccess
            obj, created = FlipBookAccess.objects.get_or_create(user=user, flipbook=flipbook)
            if created:
                admin_site.message_user(request, f"Access granted to {user.username} for {flipbook.title}.")
            else:
                admin_site.message_user(request, f"{user.username} already has access to {flipbook.title}.")
            return redirect('..')
    else:
        form = GrantFlipBookAccessForm()
    return render(request, 'admin/grant_flipbook_access.html', {'form': form})

class FlipBookAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'flipbook', 'granted_at', 'user_email', 'user_status']
    list_filter = ['user', 'flipbook', 'granted_at']
    search_fields = ['user__username', 'user__email', 'flipbook__title']
    readonly_fields = ['granted_at', 'user_info']
    actions = []
    change_list_template = "admin/flipbookaccess_change_list.html"

    fieldsets = (
        ('Access Information', {
            'fields': ('user', 'flipbook', 'granted_at')
        }),
        ('User Details', {
            'fields': ('user_info',),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('css/admin-fix.css',)
        }

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_status(self, obj):
        if obj.user.is_active:
            return '<span style="color: green; font-weight: bold;">Active</span>'
        return '<span style="color: red; font-weight: bold;">Inactive</span>'
    user_status.short_description = 'Status'
    user_status.allow_tags = True

    def user_info(self, obj):
        user = obj.user
        info = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
            <p><strong>Username:</strong> {user.username}</p>
            <p><strong>Phone Number:</strong> {getattr(user.profile, 'mobile_number', 'N/A')}</p>
            <p><strong>Full Name:</strong> {user.get_full_name() or 'N/A'}</p>
            <p><strong>Active:</strong> {'Yes' if user.is_active else 'No'}</p>
            <p><strong>Staff Member:</strong> {'Yes' if user.is_staff else 'No'}</p>
            <p><strong>Joined:</strong> {user.date_joined.strftime('%B %d, %Y')}</p>
            <p><strong>Last Login:</strong> {user.last_login.strftime('%B %d, %Y %H:%M') if user.last_login else 'Never'}</p>
        </div>
        """
        return info
    user_info.short_description = 'User Information'
    user_info.allow_tags = True

    def show_user_details(self, request, queryset):
        self.message_user(request, f"Showing details for {queryset.count()} user(s)")
    show_user_details.short_description = "Show user details for selected accesses"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('user-access/', user_flipbook_access_view, name='user-flipbook-access'),
        ]
        return custom_urls + urls


admin.site.register(FlipBookAccess, FlipBookAccessAdmin)

from django.core.paginator import Paginator
@staff_member_required
def user_flipbook_access_view(request):
    users_qs = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')
    paginator = Paginator(users_qs, 10)  # 10 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    flipbooks = FlipBook.objects.all()
    from .models import FlipBookAccess
    user_flipbook_ids = {}
    for user in users:
        user_flipbook_ids[user.id] = set(FlipBookAccess.objects.filter(user=user).values_list('flipbook_id', flat=True))

    if request.method == 'POST':
        # For POST, update only users on current page to avoid data loss
        try:
            for user in users:
                selected = set()
                flipbook_ids = request.POST.getlist(f'flipbooks_{user.id}')
                for fb_id in flipbook_ids:
                    try:
                        selected.add(int(fb_id))
                    except (ValueError, TypeError):
                        continue
                
                current = set(FlipBookAccess.objects.filter(user=user).values_list('flipbook_id', flat=True))
                
                # Add new access
                for fb_id in selected - current:
                    try:
                        FlipBookAccess.objects.get_or_create(user=user, flipbook_id=fb_id)
                    except Exception as e:
                        print(f"Error creating access for user {user.id}, flipbook {fb_id}: {e}")
                
                # Remove access
                for fb_id in current - selected:
                    try:
                        FlipBookAccess.objects.filter(user=user, flipbook_id=fb_id).delete()
                    except Exception as e:
                        print(f"Error deleting access for user {user.id}, flipbook {fb_id}: {e}")
            
            messages.success(request, f"✅ FlipBook access updated successfully for {len(users)} user(s).")
        except Exception as e:
            messages.error(request, f"❌ Error updating access: {str(e)}")
        
        return redirect(request.path)

    context = {
        'users': users,
        'flipbooks': flipbooks,
        'user_flipbook_ids': user_flipbook_ids,
        'paginator': paginator,
        'page_obj': users,
    }
    return render(request, 'admin/user_flipbook_access.html', context)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile_number']
    search_fields = ['user__username', 'mobile_number']

admin.site.register(UserProfile, UserProfileAdmin)
