# books/urls.py
from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('list/', views.book_list_view, name='book_list'),
    path('upload/', views.upload_book_view, name='upload_book'),
    path('book/<int:pk>/', views.book_detail_view, name='book_detail'),
    # Keep download and read views, but update their permissions in views.py
    path('book/<int:pk>/download/', views.download_book_view, name='download_book'),
    path('book/<int:pk>/read/', views.read_book_view, name='read_book'),

    # Payment URL - kept the structure but will update the view to only handle 'purchase'
    path('book/<int:book_pk>/order/<str:order_type>/', views.create_order_view, name='create_order'),
    path('payment/callback/', views.payment_callback_view, name='payment_callback'),

    # Review URL (Kept as is)
    path('book/<int:book_pk>/add_review/', views.add_review_view, name='add_review'),

    path('fullscreen_reader/', views.fullscreen_reader_view, name='fullscreen_reader'),

]