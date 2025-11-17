import json
import os
import requests
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv
from . import symbol_cache

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful.'})
        else:
            return JsonResponse({'message': 'Invalid credentials.'}, status=401)

    return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return HttpResponseBadRequest('Username and password are required.')

            if User.objects.filter(username=username).exists():
                return JsonResponse({'message': 'Username already exists.'}, status=400)

            User.objects.create_user(username=username, password=password)
            return JsonResponse({'message': 'User created successfully.'}, status=201)

        except json.JSONDecodeError:
            return HttpResponseBadRequest('Invalid JSON.')

    return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)


@csrf_exempt
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logout successful.'})
    return JsonResponse({'message': 'Only POST method is allowed.'}, status=405)

def stock_quote_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    # Load API key from .env file on each request.
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    api_key = os.environ.get("FINNHUB_API_KEY")

    symbol = request.GET.get('symbol')
    if not symbol:
        return HttpResponseBadRequest('Stock symbol is required.')

    try:
        headers = {'X-Finnhub-Token': api_key}
        response = requests.get(f'https://finnhub.io/api/v1/quote?symbol={symbol.upper()}', headers=headers)
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        if data.get('o') == 0 and data.get('c') == 0: # Finnhub returns 0 for unknown symbols
            return JsonResponse({'error': f'Symbol "{symbol}" not found.'}, status=404)

        return JsonResponse({'symbol': symbol.upper(), 'open_price': data.get('o')})

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Failed to retrieve data from Finnhub: {e}'}, status=502)

def symbol_search_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    query = request.GET.get('q', '').upper()
    if not query:
        return JsonResponse([], safe=False)

    # Search the cached symbols
    matches = [
        s for s in symbol_cache.SYMBOLS 
        if s['symbol'].startswith(query)
    ]
    return JsonResponse(matches[:5], safe=False)