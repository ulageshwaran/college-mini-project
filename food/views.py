from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Grocery, GroceryType, ShoppingList
from .forms import GroceryForm, ShoppingListForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Home / Index - List all groceries with search
@login_required
def index(request):
    search_query = request.GET.get('search', '').strip()
    groceries = Grocery.objects.filter(user=request.user).select_related('grocerie_type')
    
    if search_query:
        groceries = groceries.filter(
            Q(grocery_name__icontains=search_query) |
            Q(grocerie_type__type_name__icontains=search_query)
        )
    
    groceries = groceries.order_by('-ex_date')
    
    return render(request, 'food/index.html', {
        'groceries': groceries,
        'search_query': search_query
    })

# Add a new grocery
@login_required
def add_grocery(request):
    grocery_types = GroceryType.objects.all()
    
    if request.method == 'POST':
        grocery_name = request.POST.get('grocery_name')
        ex_date = request.POST.get('ex_date')
        quantity = request.POST.get('quantity')
        grocerie_type_id = request.POST.get('grocerie_type')
        
        try:
            grocerie_type = GroceryType.objects.get(id=grocerie_type_id)
            Grocery.objects.create(
                grocery_name=grocery_name,
                ex_date=ex_date,
                quantity=quantity,
                grocerie_type=grocerie_type,
                user=request.user
            )
            messages.success(request, 'Grocery added successfully!')
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Error adding grocery: {str(e)}')
    
    return render(request, 'food/add.html', {
        'grocery_types': grocery_types,
        'is_editing': False
    })

# Edit an existing grocery
@login_required
def edit_grocery(request, pk):
    grocery = get_object_or_404(Grocery, pk=pk, user=request.user)
    grocery_types = GroceryType.objects.all()
    
    if request.method == 'POST':
        grocery_name = request.POST.get('grocery_name')
        ex_date = request.POST.get('ex_date')
        quantity = request.POST.get('quantity')
        grocerie_type_id = request.POST.get('grocerie_type')
        
        try:
            grocerie_type = GroceryType.objects.get(id=grocerie_type_id)
            grocery.grocery_name = grocery_name
            grocery.ex_date = ex_date
            grocery.quantity = quantity
            grocery.grocerie_type = grocerie_type
            grocery.save()
            messages.success(request, 'Grocery updated successfully!')
            return redirect('index')
        except Exception as e:
            messages.error(request, f'Error updating grocery: {str(e)}')
    
    # Create a form-like object for template
    form_data = {
        'grocery_name': {'value': grocery.grocery_name},
        'ex_date': {'value': grocery.ex_date.strftime('%Y-%m-%d')},
        'quantity': {'value': grocery.quantity},
        'grocerie_type': {'value': grocery.grocerie_type.id}
    }
    
    return render(request, 'food/add.html', {
        'form': type('obj', (object,), form_data),
        'grocery_types': grocery_types,
        'is_editing': True
    })

# Delete a grocery
@login_required
def delete_grocery(request, pk):
    grocery = get_object_or_404(Grocery, pk=pk, user=request.user)
    grocery.delete()
    messages.success(request, 'Grocery deleted successfully!')
    return redirect('index')

# Shopping List - View current shopping list with search
@login_required
def shopping_list(request):
    search_query = request.GET.get('search', '').strip()
    
    shop_list = ShoppingList.objects.filter(user=request.user).select_related('grocery', 'grocery__grocerie_type')
    groceries = Grocery.objects.filter(user=request.user).select_related('grocerie_type')
    
    if search_query:
        groceries = groceries.filter(
            Q(grocery_name__icontains=search_query) |
            Q(grocerie_type__type_name__icontains=search_query)
        )
    
    groceries = groceries.order_by('grocery_name')
    
    return render(request, 'food/shopping.html', {
        'shop_list': shop_list,
        'groceries': groceries,
        'search_query': search_query
    })

# Add grocery to shopping list
@login_required
def add_to_shopping_list(request, pk):
    grocery = get_object_or_404(Grocery, pk=pk, user=request.user)
    shop_item, created = ShoppingList.objects.get_or_create(
        user=request.user,
        grocery=grocery,
        defaults={'quantity': 1}
    )
    if not created:
        shop_item.quantity += 1
        shop_item.save()
    messages.success(request, f'{grocery.grocery_name} added to your shopping list!')
    return redirect('shopping')

# Remove grocery from shopping list
@login_required
def remove_from_shopping_list(request, pk):
    shop_item = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    shop_item.delete()
    messages.success(request, 'Item removed from shopping list!')
    return redirect('shopping')

# Signin view
def signin_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not email or not password:
            messages.error(request, "Please provide both email and password")
            return render(request, 'food/signin.html')
        
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return render(request, 'food/signin.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password")
    
    return render(request, 'food/signin.html')

# Signup view
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Validation
        if not username or not email or not password:
            messages.error(request, "All fields are required")
            return redirect('signup')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('signup')

        try:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "Account created successfully! Please sign in.")
            return redirect('signin')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('signup')

    return render(request, 'food/signup.html')

# Signout view
@login_required
def signout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully")
    return redirect('signin')