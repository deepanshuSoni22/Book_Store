# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from books.models import Book, Order # Import Book and Order models
from django.contrib import messages
from django.utils import timezone
# Removed timedelta as it's no longer needed for borrow expiry calculation

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful! Welcome!")
            return redirect('/') # Redirect to homepage or user dashboard
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def user_dashboard(request):
    user = request.user

    # 1. Get books uploaded by the user
    uploaded_books = Book.objects.filter(owner=user).order_by('-uploaded_at')

    # 2. Get relevant orders for the user's uploaded books (purchases by others)
    # We want orders where the book's owner is the current user AND the order is a paid purchase.
    relevant_orders = Order.objects.filter(
        book__owner=user,             # Filter for books owned by the current user
        order_type='purchase',        # Only include purchase orders
        status='paid'                 # Only include paid orders
    ).exclude(
        user=user                     # Exclude orders where the owner bought their own book
    ).select_related('user', 'book').order_by('-created_at') # Optimize queries and order

    # 3. Calculate total earnings from successful purchases of the user's books
    # Earnings now only come from PURCHASE orders ('paid') on THEIR books.

    total_earnings = Order.objects.filter(
        book__owner=user,
        order_type='purchase',
        status='paid'
    ).aggregate(sum_amount=Sum('amount'))['sum_amount'] or 0

    # Removed calculation and passing of total_borrow_earnings

    context = {
        'uploaded_books': uploaded_books,
        'relevant_orders': relevant_orders,
        'total_earnings': total_earnings,
        'user': user,
        # Removed 'total_purchase_earnings' and 'total_borrow_earnings' if you only need the total
        # If you need to display purchase earnings separately on the dashboard, you can keep total_earnings
        # and rename it to total_purchase_earnings, as they are now the same.
    }

    # Assuming you have a template for the user dashboard, e.g., 'accounts/dashboard.html'
    return render(request, 'accounts/dashboard.html', context)


@login_required
def user_profile_view(request):
    """
    Displays the personal profile page for the logged-in user,
    including their purchased books.
    """
    user = request.user

    # Get all purchased orders for the user
    purchased_orders = Order.objects.filter(
        user=user,
        order_type='purchase',
        status='paid'
    ).select_related('book').order_by('-paid_at') # Order by purchase date

    # Removed fetching of borrowed orders

    context = {
        'user': user,
        'purchased_orders': purchased_orders,
        # Removed 'borrowed_orders' from context
    }

    return render(request, 'accounts/profile.html', context)