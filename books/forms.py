# books/forms.py
import hashlib
from django import forms
from django.core.exceptions import ValidationError
from .models import Book, Review
import sys

# Define the category choices
CATEGORY_CHOICES = [
    ('', '--------'), # Default empty choice
    ('BCA', 'BCA'),
    ('BCOM', 'BCOM'),
    ('BBA', 'BBA'),
    ('BSC', 'BSC'),
    ('Others', 'Others'),
]

class BookUploadForm(forms.ModelForm):
    # Add the category ChoiceField
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=True,
        label="Category"
    )
    # Add a CharField for the custom category when 'Others' is selected
    other_category = forms.CharField(
        max_length=100,
        required=False, # Not required unless 'Others' is selected
        label="Specify Category (if 'Others')"
    )

    class Meta:
        model = Book
        # Add 'category' to the fields
        fields = ['title', 'author', 'description', 'category', 'file', 'cover_image', 'purchase_price', 'file_hash']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter a brief description of the book...'}),
            'file': forms.ClearableFileInput(attrs={'accept': '.pdf'}),
            'purchase_price': forms.TextInput(attrs={'placeholder': 'e.g., ₹100.00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].help_text = 'Only PDF files are allowed.'
        self.fields['purchase_price'].help_text = 'Enter price in Indian Rupees (₹).'
        self.fields['cover_image'].help_text = 'Optional: Upload a cover image (JPG, PNG, etc.).'
        self.fields['description'].help_text = 'Provide a summary of the book content.'
        self.fields['file_hash'].widget = forms.HiddenInput()
        self.fields['file_hash'].required = False

        # Add Tailwind classes to existing fields (already present, keeping)
        self.fields['description'].widget.attrs.update({
             'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gold focus:border-gold'
        })

        # Add Tailwind classes to new fields
        self.fields['category'].widget.attrs.update({
            'class': 'block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-gold focus:border-gold rounded-md'
        })
        self.fields['other_category'].widget.attrs.update({
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gold focus:border-gold',
            'placeholder': 'e.g., Engineering, Arts, etc.'
        })

    def clean(self):
        cleaned_data = super().clean()
        uploaded_file = cleaned_data.get('file')
        category = cleaned_data.get('category')
        other_category = cleaned_data.get('other_category')

        # --- File Hash Calculation (Existing Logic) ---
        file_hash = None
        if uploaded_file:
            hasher = hashlib.sha256()
            uploaded_file.seek(0)
            try:
                for chunk in uploaded_file.chunks():
                    hasher.update(chunk)
                file_hash = hasher.hexdigest()
                cleaned_data['file_hash'] = file_hash
            except Exception as e:
                # Log the error for debugging
                print(f"Error hashing file: {e}", file=sys.stderr)
                raise ValidationError("Error processing file.")
            finally:
                 uploaded_file.seek(0) # Reset file pointer after reading


        # --- Duplicate Check Logic (Existing Logic) ---
        if file_hash: # Only perform check if a file was uploaded and hashed
             existing_books_by_hash = Book.objects.filter(file_hash=file_hash)

             existing_book_by_hash = existing_books_by_hash.first()

             if existing_book_by_hash:
                 if self.instance and self.instance.pk and existing_book_by_hash.pk == self.instance.pk:
                     pass # It's the same book being updated, no duplicate error
                 else:
                     raise ValidationError(
                         "This book file has already been uploaded."
                     )

        # --- Category Logic ---
        if category == 'Others':
            if not other_category:
                # Raise error if 'Others' is selected but the custom field is empty
                self.add_error('other_category', "Please specify the category.")
            else:
                # Use the value from other_category for the book's category
                cleaned_data['category'] = other_category
        elif not category:
             # Raise error if no category is selected (including the default '--------')
             self.add_error('category', "Please select a category.")


        return cleaned_data

# --- Review Form (Kept as is) ---
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here...'}),
        }
        labels = {
            'rating': 'Your Rating',
            'comment': 'Your Review',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.attrs.update({
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-gold focus:border-gold'
        })
        self.fields['comment'].widget.attrs.update({
            'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-gold focus:border-gold'
        })
