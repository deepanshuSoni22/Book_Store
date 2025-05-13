# books/views.py

# library imports
import razorpay # For payment processing

# Django imports
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # For restricting access to logged-in users
from django.http import FileResponse, Http404, JsonResponse # For handling file downloads, 404 errors, and JSON responses
from django.urls import reverse # For generating URLs
from django.views.decorators.csrf import csrf_exempt # For webhook endpoint (payment callback)
from django.utils import timezone # For working with timezones
from django.db.models import Avg # For calculating average ratings
from django.contrib import messages # For displaying user feedback messages
from django.db.models import Count # For counting unique categories

# Local application imports
from .models import Book, Order, Review # Import necessary models
from .forms import BookUploadForm, ReviewForm # Import necessary forms

# Initialize Razorpay client
# Attempts to initialize the Razorpay client using keys from Django settings.
# If keys are not found, sets client to None and prints a warning.
try:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    # Optional: Set app details for Razorpay requests
    client.set_app_details({"app": "BookStore", "version": "1.0"})
except AttributeError:
    client = None
    print("WARNING: Razorpay keys not found in settings. Payment functionality might be disabled.")


# --- View to handle root URL based on login status ---
def home_redirect_view(request):
    """
    Redirects logged-in users to the book list page.
    Non-logged-in users see the home page.
    """
    if request.user.is_authenticated:
        # Logged-in users go to the books list
        return redirect('books:book_list')
    else:
        # Non-logged-in users see the home page
        return render(request, 'home.html')


# --- View to display the list of books ---
def book_list_view(request):
    """
    Displays a list of books, with an option to filter by category.
    Books are annotated with their average rating and ordered by upload date.
    """
    # Get the category from the query parameters
    selected_category = request.GET.get('category')

    # Start with all books annotated with average rating
    books_queryset = Book.objects.annotate(
        avg_rating=Avg('reviews__rating') # Calculate the average rating from related reviews
    )

    # If a category is selected (and not an empty string), filter the queryset
    if selected_category and selected_category != '':
        books_queryset = books_queryset.filter(category=selected_category)

    # Order the books by upload date (newest first)
    books = books_queryset.order_by('-uploaded_at')

    # Get all unique categories from the database for the filter dropdown
    # Use distinct() to get unique category values
    unique_categories = Book.objects.values_list('category', flat=True).distinct()
    # Convert the queryset result to a list
    unique_categories_list = list(unique_categories)

    context = {
        'books': books,
        'unique_categories': unique_categories_list, # Pass unique categories to the template
        'selected_category': selected_category, # Pass the selected category back to the template
    }

    return render(request, 'books/list.html', context)

# --- View to handle book uploads ---
@login_required # Requires user to be logged in
def upload_book_view(request):
    """
    Handles the uploading of new books by logged-in users.
    """
    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data but don't commit yet
            book = form.save(commit=False)
            # Assign the current logged-in user as the book owner
            book.owner = request.user
            # Save the book object to the database
            book.save()
            messages.success(request, f"Book '{book.title}' uploaded successfully!")
            # Redirect to the detail page of the newly uploaded book
            return redirect('books:book_detail', pk=book.pk)
        else:
            # If the form is invalid, errors will be available in the form object
            # The template will display these errors.
            pass

    else:
        # For GET requests, display a blank upload form
        form = BookUploadForm()

    return render(request, 'books/upload.html', {'form': form})


# --- View to display book details ---
def book_detail_view(request, pk):
    """
    Displays the details of a specific book, including reviews.
    Determines user permissions (download, read, review) based on ownership and purchase status.
    """
    # Get the book object or return 404 if not found
    book = get_object_or_404(Book, pk=pk)

    # Initialize permission flags
    can_download = False # Only owner can download the file
    can_read = False # Owner and purchaser can read in-app
    has_reviewed = False # Flag to check if the current user has reviewed this book
    can_review = False # Flag to determine if the current user is eligible to review

    # Fetch all reviews for this book, ordered by newest first
    reviews = Review.objects.filter(book=book).order_by('-created_at')

    # Initialize the review form
    review_form = ReviewForm()

    # Check permissions if the user is authenticated
    if request.user.is_authenticated:
        # Check if the current user owns the book
        if book.owner == request.user:
            can_download = True # Owner can always download
            can_read = True # Owner can always read in-app
            can_review = True # Owner can review their own book
        else:
            # If not the owner, check if the user has purchased the book
            purchase_order_exists = Order.objects.filter(
                user=request.user,
                book=book,
                order_type='purchase', # Only check for purchase orders
                status='paid'
            ).exists()
            if purchase_order_exists:
                # User has purchased the book
                can_read = True # Purchased users can read in-app
                can_review = True # User can review if they purchased
                # can_download remains False for purchasers

        # Check if the current user has already reviewed this book
        has_reviewed = Review.objects.filter(book=book, user=request.user).exists()

    context = {
        'book': book,
        'can_download': can_download,
        'can_read': can_read,
        'reviews': reviews,
        'review_form': review_form,
        'has_reviewed': has_reviewed,
        'can_review': can_review,
    }
    return render(request, 'books/detail.html', context)

# --- View to handle adding a review ---
@login_required # Requires user to be logged in
def add_review_view(request, book_pk):
    """
    Handles the submission of a review for a specific book.
    Requires the user to be logged in and authorized (owner or purchaser).
    """
    # Get the book object or return 404 if not found
    book = get_object_or_404(Book, pk=book_pk)

    # Check if the user is eligible to review (owner or purchaser)
    user_eligible_to_review = False
    if request.user.is_authenticated:
        if book.owner == request.user:
            user_eligible_to_review = True
        else:
            # Check for purchase
            purchase_order_exists = Order.objects.filter(
                user=request.user,
                book=book,
                order_type='purchase',
                status='paid'
            ).exists()
            if purchase_order_exists:
                user_eligible_to_review = True

    # Process the form submission if it's a POST request and the user is eligible
    if request.method == 'POST' and user_eligible_to_review:
        form = ReviewForm(request.POST)

        # Check if the user has already reviewed this book before processing the form
        if Review.objects.filter(book=book, user=request.user).exists():
             messages.warning(request, "You have already submitted a review for this book.")
             return redirect('books:book_detail', pk=book.pk)

        if form.is_valid():
            # Save the form data but don't commit yet
            review = form.save(commit=False)
            # Associate the review with the book and the current user
            review.book = book
            review.user = request.user
            try:
                # Save the review object to the database
                review.save()
                messages.success(request, "Your review has been added!")
            except Exception as e:
                messages.error(request, f"Error adding review: {e}")

        else:
            # If the form is invalid, display errors using messages framework
            for field, errors in form.errors.items():
                # Get the field label for better error messages
                field_label = form.fields[field].label if form.fields[field].label else field
                for error in errors:
                    messages.error(request, f"Error in {field_label}: {error}")

    # If it's a POST request but the user is not eligible
    elif request.method == 'POST' and not user_eligible_to_review:
         messages.error(request, "You must purchase this book to leave a review.")
         return redirect('books:book_detail', pk=book.pk)

    # Redirect back to the book detail page regardless of success or failure
    return redirect('books:book_detail', pk=book.pk)


# --- View to create a payment order ---
@login_required # Requires user to be logged in
def create_order_view(request, book_pk, order_type):
    """
    Creates a payment order for purchasing a book using Razorpay.
    Only 'purchase' order type is supported.
    Checks if the user has already purchased the book.
    """
    # Get the book object or return 404 if not found
    book = get_object_or_404(Book, pk=book_pk)
    amount = 0

    # Only allow 'purchase' order type
    if order_type != 'purchase':
        messages.error(request, "Invalid order type. Only purchase is allowed.")
        return redirect('books:book_detail', pk=book.pk)

    # Set the amount for purchase
    amount = book.purchase_price

    # Check if the user already has a successful purchase order for this book
    existing_order = Order.objects.filter(
        user=request.user,
        book=book,
        order_type='purchase',
        status='paid'
    ).first()
    if existing_order:
        messages.info(request, f"You have already purchased this book.")
        # Redirect to the read view directly since they already own it
        return redirect('books:read_book', pk=book.pk)

    # Proceed with creating the Razorpay order if no existing active order found
    if request.method == 'POST':
        # Convert amount to paise (Razorpay requires amount in smallest currency unit)
        razorpay_amount = int(amount * 100)
        currency = 'INR'
        # Generate a unique receipt ID
        receipt = f"order_rcptid_{book.pk}_{request.user.id}_{timezone.now().timestamp()}"

        try:
            # Create the order with Razorpay
            if client:
                razorpay_order = client.order.create(dict(
                    amount=razorpay_amount,
                    currency=currency,
                    receipt=receipt,
                    payment_capture='1' # Auto-capture payment upon successful transaction
                ))
            else:
                messages.error(request, "Payment service is not available. Please contact support.")
                return redirect('books:book_detail', pk=book.pk)

        except Exception as e:
            messages.error(request, f"Error creating Razorpay order: {e}")
            return redirect('books:book_detail', pk=book.pk)

        # Create a local Order object to track the transaction
        order = Order.objects.create(
            user=request.user,
            book=book,
            order_type='purchase', # Hardcoded to 'purchase' now
            amount=amount,
            razorpay_order_id=razorpay_order['id'],
            status='pending' # Initial status is pending
        )

        # Generate the callback URL for Razorpay to send payment response
        callback_url = request.build_absolute_uri(reverse('books:payment_callback'))

        # Prepare context data for the checkout page
        context = {
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': razorpay_amount,
            'currency': currency,
            'company_name': 'BookStore',
            'book_title': book.title,
            'user_email': request.user.email,
            'user_contact': '9999999999', # Placeholder contact number
            'callback_url': callback_url,
            'order_id': order.id, # Pass local order ID to the template
            'order': order, # Pass the order object
            'book': book, # Pass the book object
        }
        # Render the checkout page to initiate the Razorpay payment process
        return render(request, 'books/checkout.html', context)

    # Handle invalid request methods
    messages.error(request, "Invalid request method.")
    return redirect('books:book_detail', pk=book.pk)


# --- View to handle Razorpay payment callback ---
@csrf_exempt # Exempt from CSRF protection as this is a webhook endpoint
def payment_callback_view(request):
    """
    Handles the callback from Razorpay after a payment attempt.
    Verifies the payment signature and updates the order status.
    """
    if request.method == "POST":
        try:
            # Get payment data from the POST request
            payload = request.POST
            razorpay_order_id = payload.get('razorpay_order_id')
            razorpay_payment_id = payload.get('razorpay_payment_id')
            razorpay_signature = payload.get('razorpay_signature')

            # Check if all required payment data is present
            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                messages.error(request, "Missing payment data received from Razorpay.")
                return JsonResponse({'status': 'error', 'message': 'Missing payment data'}, status=400)

            # Prepare data for signature verification
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            }

            # Verify the payment signature with Razorpay
            try:
                if client:
                    client.utility.verify_payment_signature(params_dict)
                else:
                    messages.error(request, "Payment service is not available for verification.")
                    return redirect('/') # Redirect to home or an error page
            except Exception as e:
                # Raise a specific error for signature verification failure
                raise razorpay.errors.SignatureVerificationError(f"Signature verification failed: {e}")

            # Find the corresponding local order with pending status
            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id, status='pending')

            # Ensure the found order is a purchase order
            if order.order_type != 'purchase':
                 messages.error(request, "Invalid order type for this payment callback.")
                 return redirect('/') # Redirect to home or an error page

            # Check if the order is already paid to prevent double processing
            if order.status == 'paid':
                messages.info(request, "This order has already been processed.")
                return redirect('books:book_detail', pk=order.book.pk)

            # Update the order details and status upon successful verification
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.status = 'paid' # Set status to paid
            order.paid_at = timezone.now() # Record payment time

            # Save the updated order
            order.save()

            messages.success(request, f"Payment successful! You can now read '{order.book.title}' in the app reader.")
            # Redirect directly to the book reader view
            return redirect('books:read_book', pk=order.book.pk)

        except razorpay.errors.SignatureVerificationError as e:
            # Handle signature verification failure
            razorpay_order_id = request.POST.get('razorpay_order_id')
            if razorpay_order_id:
                 try:
                     # Attempt to find the order and mark it as failed if not already paid
                     order = Order.objects.get(razorpay_order_id=razorpay_order_id)
                     if order.status != 'paid':
                         order.status = 'failed'
                         order.save()
                 except Order.DoesNotExist:
                     # If order not found, do nothing
                     pass

            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('/') # Redirect to home or an error page
        except Order.DoesNotExist:
            # Handle case where the order is not found or not in pending status
            messages.error(request, "Order not found or already processed.")
            return redirect('/') # Redirect to home or an error page
        except Exception as e:
            # Handle other unexpected errors during payment processing
            razorpay_order_id = request.POST.get('razorpay_order_id')
            if razorpay_order_id:
                 try:
                     # Attempt to find the order and mark it as failed if not already paid
                     order = Order.objects.get(razorpay_order_id=razorpay_order_id, status__in=['pending', 'paid'])
                     if order.status != 'paid':
                         order.status = 'failed'
                         order.save()
                 except Order.DoesNotExist:
                     # If order not found, do nothing
                     pass

            messages.error(request, f"An error occurred processing payment: {str(e)}")
            return redirect('/') # Redirect to home or an error page

    # Handle invalid request methods to the callback URL
    messages.error(request, "Invalid request to callback.")
    return redirect('/') # Redirect to home or an error page


# --- View to handle book downloads ---
# Secure Content Delivery - ONLY FOR OWNERS
@login_required # Requires user to be logged in
def download_book_view(request, pk):
    """
    Allows the owner of a book to download the file.
    Redirects unauthorized users (non-owners) to the read view if purchased,
    otherwise to the book detail page.
    """
    # Get the book object or return 404 if not found
    book = get_object_or_404(Book, pk=pk)
    is_owner = book.owner == request.user

    # Only the owner can download the file
    if not is_owner:
        messages.error(request, "You do not have permission to download this book.")
        # Check if the user has purchased the book
        has_purchased = Order.objects.filter(user=request.user, book=book, order_type='purchase', status='paid').exists()
        if has_purchased:
             # If purchased, redirect to the in-app reader
             return redirect('books:read_book', pk=book.pk)
        else:
            # If not owner and not purchased, redirect to book detail
            return redirect('books:book_detail', pk=book.pk)

    try:
        # Serve the book file as an attachment for download
        return FileResponse(book.file.open('rb'), as_attachment=True, filename=book.file.name.split('/')[-1])

    except FileNotFoundError:
        # Handle case where the book file is not found on the server
        raise Http404("Book file not found.")
    except Exception as e:
        # Handle other potential errors during file serving
        messages.error(request, f"Error serving file: {e}")
        return redirect('books:book_detail', pk=book.pk)


# --- View for the in-app book reader ---
@login_required # Requires user to be logged in
def read_book_view(request, pk):
    """
    Renders the in-app book reader page.
    Requires the user to be logged in and authorized (owner or purchaser).
    Passes the book details and file URL to the template.
    """
    # Get the book object or return 404 if not found
    book = get_object_or_404(Book, pk=pk)
    is_owner = book.owner == request.user

    # Check if user has purchased the book
    has_purchased = Order.objects.filter(
        user=request.user,
        book=book,
        order_type='purchase', # Only check for purchase orders
        status='paid'
    ).exists()

    # User must be owner OR have purchased the book to read in-app
    if not (is_owner or has_purchased):
        messages.error(request, "You must purchase this book to read it.")
        return redirect('books:book_detail', pk=book.pk)

    # Assuming book.file.url provides the URL to the PDF file.
    # Note: For true DRM, serving the file directly via URL might not be sufficient.
    # More advanced solutions involve streaming or token-based access.
    book_file_url = book.file.url

    context = {
        'book': book,
        'book_file_url': book_file_url # This URL needs to be protected against direct access
    }
    # Render the main in-app reader template
    return render(request, 'books/reader.html', context)


# --- New view for the dedicated full-screen reader page ---
@login_required # Ensure user is logged in to access fullscreen reader
def fullscreen_reader_view(request):
    """
    Renders the dedicated full-screen reader page.
    Expects 'book_pk' and optionally 'page' (initial page number)
    as query parameters.
    Requires the user to be logged in and authorized (owner or purchaser).
    """
    # Get book_pk and initial_page from query parameters
    book_pk = request.GET.get('book_pk')
    initial_page = request.GET.get('page', 1) # Get initial page, default to 1

    # Basic validation: Ensure book_pk is provided
    if not book_pk:
        messages.error(request, "Book identifier is missing for full-screen reader.")
        return redirect('books:book_list') # Redirect to book list as a fallback

    try:
        # Get the book object or return 404 if not found
        book = get_object_or_404(Book, pk=book_pk)

        # Check if user is authorized to read this book (owner or purchaser)
        is_owner = book.owner == request.user
        has_purchased = Order.objects.filter(user=request.user, book=book, order_type='purchase', status='paid').exists()

        # If user is not authorized, show an error and redirect
        if not (is_owner or has_purchased):
             messages.error(request, "You are not authorized to access this book.")
             return redirect('books:book_detail', pk=book.pk)

        # Get the secure URL for the book file
        book_file_url = book.file.url

    except Http404:
        # Handle case where the book is not found
        messages.error(request, "Book not found.")
        return redirect('books:book_list')
    except Exception as e:
        # Handle other potential errors during book loading
        messages.error(request, f"An error occurred loading book for full-screen reader: {e}")
        return redirect('books:book_list')

    # Prepare context data for the template
    context = {
        'book': book, # Pass the book object for title/author in the template
        'book_pk': book_pk, # Pass book_pk to the template for JS to use
        'book_file_url': book_file_url, # Pass the secure URL
        'initial_page': initial_page, # Pass the initial page
    }
    # Render the new fullscreen reader template
    return render(request, 'books/fullscreen_reader.html', context)
