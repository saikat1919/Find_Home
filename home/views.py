from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import *
from .forms import *
from django.utils import timezone


def home(request):
    """Homepage with search functionality"""
    form = SearchForm(request.GET)
    listings = HouseListing.objects.filter(status='available', is_reported=False)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        house_type = form.cleaned_data.get('house_type')
        min_rent = form.cleaned_data.get('min_rent')
        max_rent = form.cleaned_data.get('max_rent')
        
        if query:
            listings = listings.filter(
                Q(area__icontains=query) | 
                Q(address__icontains=query) | 
                Q(title__icontains=query)
            )
        
        if house_type:
            listings = listings.filter(house_type=house_type)
        
        if min_rent:
            listings = listings.filter(rent__gte=min_rent)
        
        if max_rent:
            listings = listings.filter(rent__lte=max_rent)
    
    paginator = Paginator(listings, 12)
    page = request.GET.get('page')
    listings = paginator.get_page(page)
    
    return render(request, 'home.html', {'form': form, 'listings': listings})

def register(request):
    """User registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                user_type=form.cleaned_data['user_type'],
                phone=form.cleaned_data['phone']
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    """User logout"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')
    else:
        # Handle GET request for logout
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')


# @login_required
# def dashboard(request):
#     """User dashboard based on user type"""
#     profile = get_object_or_404(UserProfile, user=request.user)
    
#     if profile.user_type == 'renter':
#         saved_listings = SavedListing.objects.filter(user=request.user)
#         interests = Interest.objects.filter(renter=request.user)
#         context = {'saved_listings': saved_listings, 'interests': interests}
#         return render(request, 'dashboard/renter.html', context)
    
#     elif profile.user_type == 'owner':
#         listings = HouseListing.objects.filter(owner=request.user)
#         interests = Interest.objects.filter(listing__owner=request.user, is_read=False)
#         context = {'listings': listings, 'new_interests': interests}
#         return render(request, 'dashboard/owner.html', context)
    
#     else:  # admin
#         reports = Report.objects.filter(is_resolved=False)
#         context = {'reports': reports}
#         return render(request, 'dashboard/admin.html', context)
    
@login_required
def dashboard(request):
    """User dashboard based on user type"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type == 'renter':
        saved_listings = SavedListing.objects.filter(user=request.user)
        interests = Interest.objects.filter(renter=request.user)
        context = {'saved_listings': saved_listings, 'interests': interests}
        return render(request, 'dashboard/renter.html', context)
    
    elif profile.user_type == 'owner':
        listings = HouseListing.objects.filter(owner=request.user)
        interests = Interest.objects.filter(listing__owner=request.user, is_read=False)
        context = {'listings': listings, 'new_interests': interests}
        return render(request, 'dashboard/owner.html', context)
    
    else:  # admin
        # Get today's date for filtering
        today = timezone.now().date()
        
        # Calculate statistics
        total_listings = HouseListing.objects.count()
        total_users = User.objects.filter(userprofile__user_type__in=['renter', 'owner']).count()
        pending_reports = Report.objects.filter(is_resolved=False).count()
        new_listings_today = HouseListing.objects.filter(created_at__date=today).count()
        
        # Get recent data
        recent_listings = HouseListing.objects.select_related('owner').order_by('-created_at')[:10]
        reports = Report.objects.filter(is_resolved=False).select_related('listing', 'reporter').order_by('-created_at')
        recent_users = User.objects.filter(
            userprofile__user_type__in=['renter', 'owner']
        ).select_related('userprofile').order_by('-date_joined')[:10]
        
        context = {
            'total_listings': total_listings,
            'total_users': total_users,
            'pending_reports': pending_reports,
            'new_listings_today': new_listings_today,
            'recent_listings': recent_listings,
            'reports': reports,
            'recent_users': recent_users,
        }
        return render(request, 'dashboard/admin.html', context)
    
@login_required
def toggle_user_status(request, pk):
    """Toggle user active status (Admin only)"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'admin':
        messages.error(request, 'Unauthorized access.')
        return redirect('home')
    
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f'User {user.username} has been {status}.')
    
    return redirect('dashboard')

# @login_required
# def resolve_report(request, pk):
#     """Resolve a report (Admin only)"""
#     profile = get_object_or_404(UserProfile, user=request.user)
#     if profile.user_type != 'admin':
#         messages.error(request, 'Unauthorized access.')
#         return redirect('home')
    
#     report = get_object_or_404(Report, pk=pk)
    
#     if request.method == 'POST':
#         action = request.POST.get('action', 'resolve')
        
#         if action == 'remove_listing':
#             # Mark the listing as reported and hide it
#             report.listing.is_reported = True
#             report.listing.save()
#             messages.success(request, 'Listing has been hidden due to false advertisement.')
        
#         # Mark report as resolved
#         report.is_resolved = True
#         report.save()
#         messages.success(request, 'Report has been resolved.')
    
#     return redirect('dashboard')

@login_required
def create_listing(request):
    """Create new house listing (Owner only)"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'owner':
        messages.error(request, 'Only owners can create listings.')
        return redirect('home')
    
    if request.method == 'POST':
        form = HouseListingForm(request.POST)
        images = request.FILES.getlist('images')
        
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.save()
            
            for image in images:
                HouseImage.objects.create(listing=listing, image=image)
            
            messages.success(request, 'Listing created successfully!')
            return redirect('dashboard')
    else:
        form = HouseListingForm()
    
    return render(request, 'listings/create.html', {'form': form})

def listing_detail(request, pk):
    """Detailed view of a house listing"""
    listing = get_object_or_404(HouseListing, pk=pk)
    comments = listing.comments.filter(parent=None)
    
    # Check if user has saved this listing
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedListing.objects.filter(user=request.user, listing=listing).exists()
    
    context = {
        'listing': listing,
        'comments': comments,
        'is_saved': is_saved,
        'comment_form': CommentForm(),
        'report_form': ReportForm(),
    }
    
    return render(request, 'listings/detail.html', context)

@login_required
@require_POST
def save_listing(request, pk):
    """Save/unsave a listing"""
    listing = get_object_or_404(HouseListing, pk=pk)
    saved, created = SavedListing.objects.get_or_create(user=request.user, listing=listing)
    
    if not created:
        saved.delete()
        return JsonResponse({'saved': False})
    
    return JsonResponse({'saved': True})

@login_required
@require_POST
def show_interest(request, pk):
    """Show interest in a listing"""
    listing = get_object_or_404(HouseListing, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type != 'renter':
        return JsonResponse({'error': 'Only renters can show interest'})
    
    interest, created = Interest.objects.get_or_create(
        renter=request.user,
        listing=listing,
        defaults={'message': f'{request.user.get_full_name()} is interested in visiting your property.'}
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'Interest shown successfully!'})
    else:
        return JsonResponse({'success': False, 'message': 'You have already shown interest in this property.'})

@login_required
@require_POST
def add_comment(request, pk):
    """Add comment to a listing"""
    listing = get_object_or_404(HouseListing, pk=pk)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.listing = listing
        comment.author = request.user
        
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, pk=parent_id)
        
        comment.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

@login_required
def update_listing_status(request, pk):
    """Update listing status (Owner only)"""
    listing = get_object_or_404(HouseListing, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['available', 'booked']:
            listing.status = status
            listing.save()
            messages.success(request, f'Listing status updated to {status}.')
    
    return redirect('dashboard')

@login_required
@require_POST
def report_listing(request, pk):
    """Report a false advertisement"""
    listing = get_object_or_404(HouseListing, pk=pk)
    form = ReportForm(request.POST)
    
    if form.is_valid():
        report = form.save(commit=False)
        report.listing = listing
        report.reporter = request.user
        report.save()
        
        return JsonResponse({'success': True, 'message': 'Report submitted successfully.'})
    
    return JsonResponse({'success': False, 'message': 'Please provide a valid reason for reporting.'})

@login_required
def chat_view(request, pk):
    """Chat between renter and owner"""
    listing = get_object_or_404(HouseListing, pk=pk)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if profile.user_type == 'renter':
        other_user = listing.owner
    elif profile.user_type == 'owner' and listing.owner == request.user:
        # Get the renter from the URL parameter or latest message
        renter_id = request.GET.get('renter_id')
        if renter_id:
            other_user = get_object_or_404(User, pk=renter_id)
        else:
            messages.error(request, 'Renter not specified.')
            return redirect('listing_detail', pk=pk)
    else:
        messages.error(request, 'Unauthorized access.')
        return redirect('listing_detail', pk=pk)
    
    # Get chat messages
    messages_list = ChatMessage.objects.filter(
        listing=listing,
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    )
    
    # Mark messages as read
    ChatMessage.objects.filter(
        listing=listing,
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    context = {
        'listing': listing,
        'other_user': other_user,
        'messages': messages_list,
    }
    
    return render(request, 'chat/chat.html', context)

@login_required
@require_POST
def send_message(request, pk):
    """Send chat message"""
    listing = get_object_or_404(HouseListing, pk=pk)
    receiver_id = request.POST.get('receiver_id')
    message_content = request.POST.get('message')
    
    if receiver_id and message_content:
        receiver = get_object_or_404(User, pk=receiver_id)
        
        ChatMessage.objects.create(
            listing=listing,
            sender=request.user,
            receiver=receiver,
            message=message_content
        )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

# Admin Views
@login_required
def admin_resolve_report(request, pk):
    """Admin resolves a report"""
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'admin':
        messages.error(request, 'Unauthorized access.')
        return redirect('home')
    
    report = get_object_or_404(Report, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'remove':
            report.listing.delete()
            messages.success(request, 'False advertisement removed.')
        elif action == 'dismiss':
            report.is_resolved = True
            report.save()
            messages.success(request, 'Report dismissed.')
    
    return redirect('dashboard')
