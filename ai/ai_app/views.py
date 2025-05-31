from django.shortcuts import render,redirect
from . models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import Product, category
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.conf import settings
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator


# Create your views here.

def index(request):
    product = Product.objects.all()
    return render(request, 'user/index.html', {'product': product})

def men(request):
    product = Product.objects.all()
    return render(request, 'user/men.html', {'product' : product})

def women(request):
    product = Product.objects.all()
    return render(request, 'user/women.html', {'product' : product})

def userin(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            request.session['username'] = username
            if  user.is_superuser:
                return redirect('adminhome')
            else:
                return redirect('index')
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, 'user/userin.html')

def userup(request):
    if request.method == 'POST':  
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirmpassword = request.POST.get('confirm_password', '')

        # Validation
        errors = []
        
        if not username or not email or not password or not confirmpassword:
            errors.append('All fields are required.')
        
        if username and len(username) < 3:
            errors.append('Username must be at least 3 characters long.')
            
        if username and len(username) > 30:
            errors.append('Username must be less than 30 characters.')
            
        # Email validation
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
        
        # Password validation (simplified)
        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
            
        if password and not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter.')
            
        if password and not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter.')
            
        if password and not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number.')
        
        if confirmpassword != password:
            errors.append("Passwords do not match.")
            
        if User.objects.filter(email=email).exists():
            errors.append("Email already exists.")
            
        if User.objects.filter(username=username).exists():
            errors.append("Username already exists.")
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password
                )
                
                messages.success(request, "Account created successfully!")
                return redirect('userin')
            except Exception as e:
                messages.error(request, "An error occurred while creating your account. Please try again.")

    return render(request, "user/userup.html")


def signout(request):
    logout(request)
    request.session.flush()
    return redirect('index')

def cart(request, product_id):
    """
    Add a product to the cart by product_id.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)

        if not request.user.is_authenticated:
            messages.error(request, "You must log in to add items to cart.")
            return redirect('userin')  # Redirect to custom login view

        cart_item = Cart.objects.filter(user=request.user, product=product).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.totalprice = cart_item.quantity * product.price
            cart_item.save()
            messages.success(request, f"{product.name} quantity updated in your cart")
        else:
            Cart.objects.create(
                user=request.user,
                product=product,
                quantity=1,
                totalprice=product.price
            )
            messages.success(request, f"{product.name} added to your cart")

    return redirect('view_cart')  # Redirect to cart view
    
    # If not POST, redirect to cart as a fallback
    return redirect('cart')

def view_cart(request):
    """
    View the current user's cart.
    """
    if not request.user.is_authenticated:
        messages.warning(request, "Login to view your cart.")
        return redirect('userin')

    cart_items = Cart.objects.filter(user=request.user)

    total_price = sum(item.totalprice for item in cart_items)
    # Example: assuming 10% discount for each item (you can customize logic)
    total_discount = sum((item.product.price * item.quantity * 0.10) for item in cart_items)
    total_payable = total_price - total_discount

    return render(request, 'user/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_payable': total_payable,
        'cart_count': cart_items.count()
    })

# Add this function for removing items from cart
def remove_from_cart(request, item_id):
    """
    Remove an item from the cart.
    """
    if not request.user.is_authenticated:
        return redirect('userin')
    
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from your cart.")
    return redirect('view_cart')

# Add this function for updating cart quantities
def update_cart(request, item_id, action):
    """
    Update cart item quantity.
    """
    if not request.user.is_authenticated:
        return redirect('userin')
    
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            # If quantity becomes 0, remove the item
            return redirect('remove_from_cart', item_id=item_id)
    
    cart_item.totalprice = cart_item.quantity * cart_item.product.price
    cart_item.save()
    
    return redirect('view_cart')

def checkout(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.totalprice for item in cart_items)
    
    # Get user's saved addresses
    saved_addresses = Address.objects.filter(user=user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Initialize address variables
        name = None
        address_str = None
        city = None
        state = None
        pincode = None
        phone = None
        saved_address = None
        
        # Check if using an existing address or creating a new one
        if 'address_id' in request.POST:
            # Using existing address
            address_id = request.POST.get('address_id')
            saved_address = Address.objects.get(id=address_id, user=user)
            
            # Use the details from the existing address
            name = saved_address.name
            address_str = saved_address.address
            city = saved_address.city
            state = saved_address.state
            pincode = saved_address.pincode
            phone = saved_address.phone
            
        else:
            # Creating a new address
            name = request.POST.get('name')
            address_str = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            phone = request.POST.get('phone')
            
            # Save address if checkbox is checked
            if request.POST.get('save_for_future'):
                saved_address = Address.objects.create(
                    user=user,
                    name=name,
                    address=address_str,
                    city=city,
                    state=state,
                    pincode=pincode,
                    phone=phone
                )
        
        # Create one order per cart item
        for item in cart_items:
            order = Order.objects.create(
                user=user,
                product=item.product,
                quantity=item.quantity,
                amount=item.totalprice,
                status="PENDING",  # Use the PaymentStatus.PENDING value
            )
            
            # If using online payment, update with payment details
            if payment_method == 'online':
                # Implement payment gateway integration here
                # This would typically involve redirecting to a payment page
                # and updating the order status and payment IDs upon return
                pass
        
        # Clear the cart after purchase
        cart_items.delete()
        
        # Redirect to order confirmation page
        return redirect('payment')
    
    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'saved_addresses': saved_addresses
    })  

@login_required
def order_details(request, order_id, product_id=None):
    """
    Display detailed information about a specific order.
    Only the order owner can view their order details.
    """
    # Get the order and ensure it belongs to the current user
    # Using select_related to optimize database queries
    order = get_object_or_404(
        Order.objects.select_related('product', 'user'),
        id=order_id,
        user=request.user
    )
    
    # Calculate totals for the template
    subtotal = order.product.price * order.quantity
    shipping = 0.00  # Free shipping as shown in your template
    tax = 0.00  # No tax as shown in your template
    
    # Prepare context for the template
    context = {
        'order': order,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'page_title': f'Order #{order.id:05d} Details',
    }
    
    return render(request, 'user/order_details.html', context)


@login_required
@require_POST
@csrf_protect
def cancel_order(request, order_id):
    """
    Cancel an order if it's still in pending status.
    Returns JSON response for AJAX calls from the template.
    """
    try:
        order = get_object_or_404(
            Order.objects.select_related('product'),
            id=order_id,
            user=request.user
        )
        
        # Check if order can be cancelled (only pending orders)
        if order.status.lower() != 'pending':
            return JsonResponse({
                'success': False,
                'message': f'Cannot cancel order with status: {order.get_status_display()}'
            }, status=400)
        
        # Update order status to cancelled
        order.status = 'CANCELLED'  # Assuming you have a CANCELLED status
        order.updated_at = timezone.now()  # If you have this field
        order.save()
        
        # Add success message
        messages.success(
            request, 
            f'Order #{order.id:05d} for {order.product.title} has been cancelled successfully.'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Order cancelled successfully'
        })
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)
    
    except Exception as e:
        # Log the error in production
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while cancelling the order'
        }, status=500)


def order_summary(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-id')[:5]  # Show last 5 orders
    return render(request, 'user/order_summary.html', {'orders': orders})

def product_details(request, pk):
    """
    View function for displaying product details.
    
    Args:
        request: The HTTP request object
        pk: The ID of the product to display
        
    Returns:
        Rendered product details page with product data
    """
    # Get the product by ID or return 404 if not found
    product = get_object_or_404(Product, id=pk)
    
    # Get all images for this product - ensure we only add images that exist
    images = []
    if product.image:
        images.append(product.image)
    if product.image1:
        images.append(product.image1)
    if product.image2:
        images.append(product.image2)
    if product.image3:
        images.append(product.image3)
    if product.image4:
        images.append(product.image4)
    if product.image5:
        images.append(product.image5)
    
    # If no images were found, use a placeholder or default image
    if not images:
        # You might want to set a default image here
        pass
    
    # Default values for non-authenticated users
    cart_product_ids = []
    cart_item_count = 0
    
    # Get cart information for authenticated users
    if request.user.is_authenticated:
        # Fetch cart items for the authenticated user
        cart_items = Cart.objects.filter(user=request.user)
        
        # Extract product IDs from the cart
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        cart_item_count = cart_items.count()
    
    # Get related products (same category)
    related_products = []
    if hasattr(product, 'category') and product.category:
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=pk)[:4]  # Get 4 related products
    
    # Prepare the context to pass to the template
    context = {
        'product': product,
        'images': images,
        'cart_product_ids': cart_product_ids,
        'cart_item_count': cart_item_count,
        'page_title': f"{product.name} - OPTICFRAMES",
        'first_image': images[0] if images else None,
        'related_products': related_products,
    }
    
    return render(request, 'user/product_details.html', context)

def lenses_page(request):
    return render(request, 'user/lenses_page.html')

def about(request):
    return render(request, 'user/about.html')

def Profile(request):
    return render(request , 'user/Profile.html')

@login_required
def adminhome(request):
    product = Product.objects.all()
    return render(request, 'adminpage/adminhome.html', {'product': product})

@login_required
def adminadd(request):
    # Get all available options for dropdown fields
    categories = category.objects.all()
    genders = Gender.objects.all()
    materials = Material.objects.all()
    frame_types = FrameType.objects.all()
    frame_shapes = FrameShape.objects.all()
    frame_styles = FrameStyle.objects.all()
    
    if request.method == 'POST':
        # Collect form data
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        color = request.POST.get('color')
        
        # Get foreign key objects
        gender_id = request.POST.get('gender')
        material_id = request.POST.get('material')
        frame_type_id = request.POST.get('frame_type')
        frame_shape_id = request.POST.get('frame_shape')
        frame_style_id = request.POST.get('frame_style')
        category_id = request.POST.get('category')
        
        # Get image files
        main_image = request.FILES.get('main_image')
        additional_images = request.FILES.getlist('additional_images')
        
        # Validate required fields
        if not all([name, price, description, main_image]):
            messages.error(request, "Please fill in all required fields!")
            return render(request, 'adminpage/adminadd.html', {
                'categories': categories,
                'genders': genders,
                'materials': materials,
                'frame_types': frame_types,
                'frame_shapes': frame_shapes,
                'frame_styles': frame_styles,
            })

        try:
            # Create product with all details
            product = Product(
                name=name,
                price=float(price),
                description=description,
                color=color,
                image=main_image,  # Set main image
            )
            
            # Set foreign keys if provided
            if gender_id:
                try:
                    gender_obj = Gender.objects.get(id=gender_id)
                    product.gender = gender_obj
                except Gender.DoesNotExist:
                    pass
                
            if material_id:
                try:
                    material_obj = Material.objects.get(id=material_id)
                    product.material = material_obj
                except Material.DoesNotExist:
                    pass
                
            if frame_type_id:
                try:
                    frame_type_obj = FrameType.objects.get(id=frame_type_id)
                    product.frameType = frame_type_obj
                except FrameType.DoesNotExist:
                    pass
                
            if frame_shape_id:
                try:
                    frame_shape_obj = FrameShape.objects.get(id=frame_shape_id)
                    product.frameShape = frame_shape_obj
                except FrameShape.DoesNotExist:
                    pass
                
            if frame_style_id:
                try:
                    frame_style_obj = FrameStyle.objects.get(id=frame_style_id)
                    product.frameStyle = frame_style_obj
                except FrameStyle.DoesNotExist:
                    pass
                
            if category_id:
                try:
                    category_obj = category.objects.get(id=category_id)
                    product.category = category_obj
                except category.DoesNotExist:
                    pass
            
            # Save the product
            product.save()
            
            # Handle additional images (up to 5)
            if additional_images:
                for i, img in enumerate(additional_images[:5]):
                    if i == 0:
                        product.image1 = img
                    elif i == 1:
                        product.image2 = img
                    elif i == 2:
                        product.image3 = img
                    elif i == 3:
                        product.image4 = img
                    elif i == 4:
                        product.image5 = img
                
                # Save again with additional images
                product.save()
            
            messages.success(request, f"Product '{name}' added successfully!")
            return redirect('adminhome')
        
        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")
    
    # For GET requests or when form submission fails
    return render(request, 'adminpage/adminadd.html', {
        'categories': categories,
        'genders': genders,
        'materials': materials,
        'frame_types': frame_types,
        'frame_shapes': frame_shapes,
        'frame_styles': frame_styles,
    })

@login_required
def adminedit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        
        # Get the category instance by name
        category_name = request.POST.get('category')
        try:
            cat = category.objects.get(name=category_name)
            product.category = cat
        except category.DoesNotExist:
            messages.error(request, f"Category '{category_name}' does not exist.")
            categories = category.objects.all()
            return render(request, 'adminpage/adminedit.html', {'product': product, 'categories': categories})
        
        product.price = request.POST.get('price')
        
        # Handle main image update
        if 'image1' in request.FILES and request.FILES['image1']:
            product.image = request.FILES['image1']
        
        # Handle additional images
        if 'image2' in request.FILES and request.FILES['image2']:
            product.image2 = request.FILES['image2']
            
        if 'image3' in request.FILES and request.FILES['image3']:
            product.image3 = request.FILES['image3']
            
        if 'image4' in request.FILES and request.FILES['image4']:
            product.image4 = request.FILES['image4']
            
        if 'image5' in request.FILES and request.FILES['image5']:
            product.image5 = request.FILES['image5']
        
        product.save()
        messages.success(request, f"Product '{product.name}' updated successfully!")
        return redirect('adminhome')    
    
    # Pass categories to the template for the dropdown
    categories = category.objects.all()
    return render(request, 'adminpage/adminedit.html', {'product': product, 'categories': categories})

def adminremove(request, product_id):
    """
    View function to remove a product
    """
    product = get_object_or_404(Product, id=product_id)
    product_name = product.name
    product.delete()
    messages.success(request, f"Product '{product_name}' removed successfully!")
    return redirect('adminhome')

def admin_logout_view(request):
    logout(request)
    return render(request, 'adminpage/adminin.html')


def search_products(request):
    """
    Search products based on query and filters
    """
    query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    gender_filter = request.GET.get('gender', '')
    material_filter = request.GET.get('material', '')
    frame_type_filter = request.GET.get('frame_type', '')
    frame_shape_filter = request.GET.get('frame_shape', '')
    frame_style_filter = request.GET.get('frame_style', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort', 'name')
    
    # Start with all products
    products = Product.objects.all()
    
    # Apply search query
    if query: 
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(color__icontains=query) |
            Q(category__name__icontains=query) |
            Q(gender__name__icontains=query) |
            Q(material__name__icontains=query) |
            Q(frameType__name__icontains=query) |
            Q(frameShape__name__icontains=query) |
            Q(frameStyle__name__icontains=query)
        )
    
    # Apply filters
    if category_filter:
        products = products.filter(category__id=category_filter)
    
    if gender_filter:
        products = products.filter(gender__id=gender_filter)
    
    if material_filter:
        products = products.filter(material__id=material_filter)
    
    if frame_type_filter:
        products = products.filter(frameType__id=frame_type_filter)
    
    if frame_shape_filter:
        products = products.filter(frameShape__id=frame_shape_filter)
    
    if frame_style_filter:
        products = products.filter(frameStyle__id=frame_style_filter)
    
    # Apply price filters
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-id')
    else:
        products = products.order_by('name')
    
    # Get filter options for the template
    categories = category.objects.all()
    genders = Gender.objects.all()
    materials = Material.objects.all()
    frame_types = FrameType.objects.all()
    frame_shapes = FrameShape.objects.all()
    frame_styles = FrameStyle.objects.all()
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Count results
    total_results = products.count()
    
    context = {
        'products': page_obj,
        'query': query,
        'total_results': total_results,
        'categories': categories,
        'genders': genders,
        'materials': materials,
        'frame_types': frame_types,
        'frame_shapes': frame_shapes,
        'frame_styles': frame_styles,
        'selected_category': category_filter,
        'selected_gender': gender_filter,
        'selected_material': material_filter,
        'selected_frame_type': frame_type_filter,
        'selected_frame_shape': frame_shape_filter,
        'selected_frame_style': frame_style_filter,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    
    return render(request, "user/search_products.html", context)

# -------------------------------------------------------------------- #
@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        amount = product.price * quantity

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            "amount": int(amount * 100),  # in paise
            "currency": "INR",
            "payment_capture": 1
        })

        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            amount=amount,
            status=PaymentStatus.PENDING,
            provider_order_id=razorpay_order['id']
        )

        return render(request, 'payment.html', {
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'amount': int(amount * 100),
            'user': user
        })

    return render(request, 'order_form.html', {'product': product})

