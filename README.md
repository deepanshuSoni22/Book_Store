# Book Store

## College Final Project: Online Bookstore

This project is a web application built with Django that functions as an online bookstore or digital content platform. It allows users to upload, browse, purchase, and time-borrow digital books (primarily PDFs). Payment processing is integrated using Razorpay.

This project was developed as a final project for Soundarya Institute of Management and Science - BCA.

## ✨ Features

* **User Authentication:** Secure signup, login, and logout.
* **Book Catalog:** Browse a list of all uploaded books.
* **Book Details:** View detailed information about each book, including author, prices, and availability (purchase/borrow).
* **Book Upload:** Authenticated users can upload new books (PDF format).
* **Purchase:** Users can purchase books for permanent download access via Razorpay.
* **Time-Based Borrowing:** Users can borrow books for a defined period (set by the uploader) for in-browser reading via Razorpay. Access expires automatically.
* **Secure Content Access:** Download/Read access is strictly controlled based on ownership, purchase status, or active borrow status.
* **In-Browser Reader:** Borrowed books can be read directly within the application (using PDF.js).
* **User Dashboard:** Uploaders can view their uploaded books, track purchase and borrow activity on their books, and see their total earnings from sales.
* **Razorpay Integration:** Seamless payment processing for purchases and borrows.

## 🚀 Tech Stack

* **Backend:** Python, Django
* **Database:** SQLite (default) - easily configurable for PostgreSQL, MySQL, etc.
* **Frontend:** HTML, CSS (Tailwind CSS), JavaScript (Alpine.js, PDF.js)
* **Payment Gateway:** Razorpay API
* **Dependency Management:** Pip (using `requirements.txt`)

## 🎨 Design & Aesthetic

The frontend has been designed with a modern, premium, and luxury aesthetic, featuring:

* Clean and spacious layouts.
* Refined typography (e.g., Serif headings, clean Sans-serif body).
* A sophisticated color palette [Optional: Mention specific primary/accent colors if you know their names, e.g., featuring deep blues, gold accents, and warm neutrals].
* Subtle hover effects and transitions.
* Responsive design using Tailwind CSS for optimal viewing on various devices.

## 📋 Setup and Installation

Follow these steps to get the project up and running on your local machine for development and testing.

**Prerequisites:**

* Python 3.8+
* Git
* A Razorpay account (for testing payments)

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/deepanshuSoni22/Book-Store.git
    cd Book-Store
    ```
    

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    # venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Copy the example environment file and update it with your secret keys.
    ```bash
    cp .env.example .env
    ```
    Now, **edit the `.env` file** and replace the placeholder values with your actual Django Secret Key and Razorpay API keys.
    ```dotenv
    # .env
    DJANGO_SECRET_KEY='<generate_your_secret_key>' # Find a Django Secret Key generator online
    DJANGO_DEBUG=True # Set to False for production-like testing
    DJANGO_ALLOWED_HOSTS='localhost,127.0.0.1' # Add domains if deploying

    RAZORPAY_KEY_ID='rzp_test_...' # Your Razorpay Test Key ID
    RAZORPAY_KEY_SECRET='your_test_secret' # Your Razorpay Test Key Secret

    # Optional: Database configuration if not using default SQLite
    # DB_NAME='<database_name>'
    # DB_USER='<database_user>'
    # DB_PASSWORD='<database_password>'
    # DB_HOST='<database_host>'
    # DB_PORT='<database_port>'
    ```

5.  **Apply migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser (optional but recommended for admin access):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create an admin user.

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## 💡 Usage

* Open your browser and go to `http://127.0.0.1:8000/`.
* Browse the book collection (`/list/`).
* Sign up for a new account or log in.
* Authenticated users can upload books via the dashboard or upload link.
* View book details, purchase, or borrow.
* Complete the payment flow via Razorpay (use test card details if in test mode).
* Access purchased books via download and borrowed books via the online reader from the book detail page.
* Visit your dashboard (`/accounts/dashboard/`) to see your uploads and sales/borrow activity.

## 📈 Project Status

This project is a completed college final project and is not intended for production deployment without further security audits and production-ready configurations.

## 🤝 Contributing

This project is primarily for academic purposes. Contributions are not expected, but feel free to fork and experiment!

## 🧑‍💻 Author

* Deepanshu Soni
* [Github Profile](https://www.github.com/deepanshuSoni22)
* [LinkedIn Profile](www.linkedin.com/in/deepanshu-soni22)

---