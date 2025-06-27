# Book Store

## College Final Project: Online Bookstore

This project is a web application built with Django that functions as an online bookstore or digital content platform. It allows users to upload, browse, purchase, and securely read digital books (primarily PDFs) using an in-app reader. Payment processing is integrated using Razorpay.

This project was developed as a final project for Soundarya Institute of Management and Science - BCA.

---

## ✨ Features

### User Features:
* **User Authentication:** Secure signup, login, and logout.
* **Book Catalog:** Browse a list of all uploaded books.
* **Book Details:** View detailed information about each book, including author, reviews, and price.
* **Book Upload:** Authenticated users can upload new books (PDF format).
* **Purchase:** Users can purchase books for in-app reading access via Razorpay.
* **Secure Content Access:** Download access is restricted to book owners only. Buyers can read purchased books securely within the application using the in-app reader (powered by PDF.js).

### Admin Features:
* **User Dashboard:** Uploaders can view their uploaded books, track purchase activity on their books, and see their total earnings from sales.
* **Razorpay Integration:** Seamless payment processing for purchases.
* **Earnings Summary:** View total earnings from book sales in the dashboard.

---

## 🚀 Tech Stack

* **Backend:** Python, Django
* **Database:** SQLite (default) - easily configurable for PostgreSQL, MySQL, etc.
* **Frontend:** HTML, CSS (Tailwind CSS), JavaScript (Alpine.js, PDF.js)
* **Payment Gateway:** Razorpay API
* **Dependency Management:** Pip (using `requirements.txt`)

---

## 🎨 Design & Aesthetic

The frontend has been designed with a modern, premium, and luxury aesthetic, featuring:

* Clean and spacious layouts.
* Refined typography (e.g., Serif headings, clean Sans-serif body).
* A sophisticated color palette featuring deep blues, gold accents, and warm neutrals.
* Subtle hover effects and transitions.
* Responsive design using Tailwind CSS for optimal viewing on various devices.

---

## 📋 Setup and Installation

Follow these steps to get the project up and running on your local machine for development and testing.

### Prerequisites:
* Python 3.8+
* Git
* A Razorpay account (for testing payments)

### Steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/deepanshuSoni22/Book-Store.git
    cd Book-Store
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**
    Copy the example environment file and update it with your secret keys.
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file:
    ```dotenv
    # .env
    DJANGO_SECRET_KEY='<generate_your_secret_key>' # Find a Django Secret Key generator online
    DJANGO_DEBUG=True # Set to False for production-like testing
    DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1' # Add domains if deploying

    RAZORPAY_KEY_ID='rzp_test_...' # Your Razorpay Test Key ID
    RAZORPAY_KEY_SECRET='your_test_secret' # Your Razorpay Test Key Secret
    ```

5. **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

6. **Create a superuser (optional but recommended for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

7. **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

---

## 💡 Usage

* Open your browser and go to `http://127.0.0.1:8000/`.
* Browse the book collection (`/list/`).
* Sign up for a new account or log in.
* Authenticated users can upload books via the dashboard or upload link.
* View book details and purchase books.
* Complete the payment flow via Razorpay (use test card details if in test mode).
* Access purchased books securely using the in-app reader. Downloads are restricted to book owners only.
* Visit your dashboard (`/accounts/dashboard/`) to see your uploads and sales activity.

---

## 📷 Screenshots

### Home Page
![Home Page Screenshot](project_demo/home-page.png)

### Books Catalog Page
![Books Catalog Screenshot](project_demo/books-catalog.png)

### Book Details Page
![Book Details Screenshot](project_demo/book-details.png)

### Payment Page
![Book Details Screenshot](project_demo/payment-page1.png)
![Book Details Screenshot](project_demo/payment-page2.png)

### In-App Reader
![In-App Reader Screenshot](project_demo/app-reader1.png)
![In-App Reader Screenshot](project_demo/app-reader2.png)

### User Dashboard
![User Dashboard Screenshot](project_demo/dashboard.png)

---

<!-- ## 🎥 Video Demo

Watch the full demo of the application here:  
[![Video Demo](placeholder/video-thumbnail.png)](placeholder/video-link)

--- -->

## 📈 Project Status

This project is a completed college final project and is not intended for production deployment without further security audits and production-ready configurations.

---

## 🤝 Contributing

This project is primarily for academic purposes. Contributions are not expected, but feel free to fork and experiment!

---

## 🧑‍💻 Author

* Deepanshu Soni
* [Github Profile](https://www.github.com/deepanshuSoni22)
* [LinkedIn Profile](https://www.linkedin.com/in/deepanshu-soni22)

---