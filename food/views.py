from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Grocery, GroceryType, ShoppingList
from .forms import GroceryForm, ShoppingListForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Home / Index - List all groceries
@login_required
def index(request):
    groceries = Grocery.objects.filter(user=request.user)
    return render(request, 'food/index.html', {'groceries': groceries})

# Add a new grocery
@login_required
def add_grocery(request):
    if request.method == 'POST':
        form = GroceryForm(request.POST)
        if form.is_valid():
            grocery = form.save(commit=False)
            grocery.user = request.user
            grocery.save()
            messages.success(request, 'Grocery added successfully!')
            return redirect('index')
    else:
        form = GroceryForm()
    return render(request, 'food/add.html', {'form': form, 'is_editing': False})

# Edit an existing grocery
@login_required
def edit_grocery(request, pk):
    grocery = get_object_or_404(Grocery, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GroceryForm(request.POST, instance=grocery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Grocery updated successfully!')
            return redirect('index')
    else:
        form = GroceryForm(instance=grocery)
    return render(request, 'food/add.html', {'form': form, 'is_editing': True})

# Delete a grocery
@login_required
def delete_grocery(request, pk):
    grocery = get_object_or_404(Grocery, pk=pk, user=request.user)
    grocery.delete()
    messages.success(request, 'Grocery deleted successfully!')
    return redirect('index')

# Shopping List - View current shopping list
@login_required
def shopping_list(request):
    shop_list = ShoppingList.objects.filter(user=request.user)
    groceries = Grocery.objects.filter(user=request.user)
    return render(request, 'food/shopping.html', {'shop_list': shop_list, 'groceries': groceries})

# Add grocery to shopping list
@login_required
def add_to_shopping_list(request, grocery_id):
    grocery = get_object_or_404(Grocery, pk=grocery_id, user=request.user)
    shop_item, created = ShoppingList.objects.get_or_create(user=request.user, grocery=grocery)
    if not created:
        shop_item.quantity += 1
        shop_item.save()
    messages.success(request, f'{grocery.name} added to your shopping list!')
    return redirect('shopping_list')

# Remove grocery from shopping list
@login_required
def remove_from_shopping_list(request, pk):
    shop_item = get_object_or_404(ShoppingList, pk=pk, user=request.user)
    shop_item.delete()
    messages.success(request, 'Item removed from shopping list!')
    return redirect('shopping_list')


# Signin view
def signin_view(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()
        
        # Find the username for this email
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist")
            return render(request, 'food/signin.html')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            next_url = request.GET.get('next') or 'index'
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password")
    
    return render(request, 'food/signin.html')

# Signout view
def signout_view(request):
    logout(request)
    return redirect('signin')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password = request.POST.get('password').strip()

        if not username:
            messages.error(request, "Username is required")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('signup')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully!")
        return redirect('signin')

    return render(request, 'food/signup.html')
