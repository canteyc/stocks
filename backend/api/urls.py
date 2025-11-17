from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('quote/', views.stock_quote_view, name='stock-quote'),
    path('symbol-search/', views.symbol_search_view, name='symbol-search'),
]
