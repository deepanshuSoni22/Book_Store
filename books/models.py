# books/models.py
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.db.models import Avg


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(help_text="A brief description of the book.", default='')
    category = models.CharField(max_length=100, default='Others')
    file = models.FileField(upload_to='book_pdfs/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_books')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    file_hash = models.CharField(max_length=64, unique=True, blank=True, null=True) # Using SHA-256, length 64

    def __str__(self):
        return self.title

    # Property to get the average rating
    @property
    def average_rating(self):
        # Calculate the average of ratings for this book's reviews
        # Use aggregate and Avg, default to 0 if no reviews
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_type} for {self.book.title} by {self.user.username} - {self.status}"


# Review Model
class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5, choices=[(i, str(i)) for i in range(1, 6)], help_text="Rating out of 5 stars")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only leave one review per book
        unique_together = ('book', 'user')
        ordering = ['-created_at'] # Order reviews by newest first

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"
