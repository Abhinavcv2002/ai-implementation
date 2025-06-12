from django.shortcuts import render

# Create your views here.
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
from .read_content import *
from .vectorize import vectorize_product_with_reviews,vectorize_user_with_search,pd
import json
from django.db.models import Case, When
import logging



# Create your views here.

# def index(request):
#     # Get all products initially
#     all_products = Product.objects.all()
#     products = []

#     # Extract product data
#     product_ids = []
#     product_vectors = []
    
#     for product in all_products:
#         if product.vector_data:
#             try:
#                 vector_data = json.loads(product.vector_data)
#                 product_ids.append(product.pk)
#                 product_vectors.append(vector_data)
#             except (json.JSONDecodeError, ValueError) as e:
#                 print(f"Error parsing vector data for product {product.pk}: {e}")
#                 continue

#     if not product_vectors:
#         print("No valid product vectors found, falling back to default")
#         products = Product.objects.all()[:12]
#     else:
#         try:
#             # Convert to numpy array first, then to tensor
#             product_vectors = np.array(product_vectors, dtype=np.float32)
#             product_vectors = torch.tensor(product_vectors)

#             if request.user.is_authenticated:
#                 try:
#                     print("Authenticated user:", request.user.username)
#                     user = User.objects.get(username=request.user.username)
#                     user_profile = users.objects.get(name=user)
                    
#                     if user_profile.vector_data:
#                         user_vector = json.loads(user_profile.vector_data)
                        
#                         # Recommend products
#                         recommend_products = recommend_product(
#                             user_vector, product_vectors, product_ids, top_n=12
#                         )
#                         print("Recommended products:", recommend_products)

#                         if recommend_products:
#                             # Get product IDs and maintain order
#                             product_ids_ordered = [item[0] for item in recommend_products]
#                             preserved_order = Case(
#                                 *[When(pk=pk, then=pos) for pos, pk in enumerate(product_ids_ordered)]
#                             )
#                             products = Product.objects.filter(
#                                 pk__in=product_ids_ordered
#                             ).order_by(preserved_order)

#                             print("Products to render:", [p.name for p in products])
#                         else:
#                             print("No recommendations generated, using default")
#                             products = Product.objects.all()[:12]
#                     else:
#                         print("User has no vector data, using default products")
#                         products = Product.objects.all()[:12]

#                 except (User.DoesNotExist, users.DoesNotExist, json.JSONDecodeError) as e:
#                     print("Error fetching user or parsing user vector:", e)
#                     products = Product.objects.all()[:12]
#                 except Exception as e:
#                     print("Unexpected error in recommendation:", e)
#                     products = Product.objects.all()[:12]
#             else:
#                 print("Unauthenticated user, showing default products")
#                 products = Product.objects.all()[:12]
                
#         except Exception as e:
#             print(f"Error processing product vectors: {e}")
#             products = Product.objects.all()[:12]

#     # Other product sections
#     data2 = Product.objects.all()[:4]
#     data3 = Product.objects.all().order_by('-id')[:3]

#     context = {
#         'product': all_products,
#         'products': products,
#         'data2': data2,
#         'data3': data3,
#     }

#     return render(request, 'user/index.html', context)





# def index(request):
#     # Get all products initially
#     all_products = Product.objects.all()
#     products = []

#     # Extract product data
#     product_ids = []
#     product_vectors = []
    
#     for product in all_products:
#         if product.vector_data:
#             try:
#                 vector_data = json.loads(product.vector_data)
#                 product_ids.append(product.pk)
#                 product_vectors.append(vector_data)
#             except (json.JSONDecodeError, ValueError) as e:
#                 print(f"Error parsing vector data for product {product.pk}: {e}")
#                 continue

#     if not product_vectors:
#         print("No valid product vectors found, falling back to default")
#         products = Product.objects.all()[:4]
#     else:
#         try:
#             # Convert to numpy array first, then to tensor
#             product_vectors = np.array(product_vectors, dtype=np.float32)
#             product_vectors = torch.tensor(product_vectors)

#             if request.user.is_authenticated:
#                 try:
#                     print("Authenticated user:", request.user.username)
#                     user = User.objects.get(username=request.user.username)
#                     user_profile = users.objects.get(name=user)
                    
#                     if user_profile.vector_data:
#                         user_vector = json.loads(user_profile.vector_data)
                        
#                         # Get last clicked product from session
#                         last_clicked_product_id = request.session.get('last_clicked_product')
                        
#                         # Recommend products
#                         recommend_products = recommend_product(
#                             user_vector, 
#                             product_vectors, 
#                             product_ids, 
#                             top_n=4,
#                             last_clicked_product_id=last_clicked_product_id
#                         )
#                         print("Recommended products:", recommend_products)

#                         if recommend_products:
#                             # Get product IDs and maintain order
#                             product_ids_ordered = [item[0] for item in recommend_products]
#                             preserved_order = Case(
#                                 *[When(pk=pk, then=pos) for pos, pk in enumerate(product_ids_ordered)]
#                             )
#                             products = Product.objects.filter(
#                                 pk__in=product_ids_ordered
#                             ).order_by(preserved_order)

#                             print("Products to render:", [p.name for p in products])
#                         else:
#                             print("No recommendations generated, using default")
#                             products = Product.objects.all()[:4]
#                     else:
#                         print("User has no vector data, using default products")
#                         products = Product.objects.all()[:4]

#                 except (User.DoesNotExist, users.DoesNotExist, json.JSONDecodeError) as e:
#                     print("Error fetching user or parsing user vector:", e)
#                     products = Product.objects.all()[:4]
#                 except Exception as e:
#                     print("Unexpected error in recommendation:", e)
#                     products = Product.objects.all()[:4]
#             else:
#                 print("Unauthenticated user, checking last clicked product")
#                 last_clicked_product_id = request.session.get('last_clicked_product')
#                 if last_clicked_product_id:
#                     try:
#                         last_clicked_product = Product.objects.get(id=last_clicked_product_id)
#                         products = Product.objects.filter(categorys=last_clicked_product.categorys)[:4]
#                     except Product.DoesNotExist:
#                         products = Product.objects.all()[:4]
#                 else:
#                     products = Product.objects.all()[:4]
                
#         except Exception as e:
#             print(f"Error processing product vectors: {e}")
#             products = Product.objects.all()[:4]

#     # Other product sections
#     data2 = Product.objects.all()[:4]
#     data3 = Product.objects.all().order_by('-id')[:3]

#     context = {
#         'product': all_products,
#         'products': products,
#         'data2': data2,
#         'data3': data3,
#     }

#     return render(request, 'user/index.html', context)

def index(request):
    # Get all products initially
    all_products = Product.objects.all()
    products = []

    # Extract product data
    product_ids = []
    product_vectors = []
    
    for product in all_products:
        if product.vector_data:
            try:
                vector_data = json.loads(product.vector_data)
                product_ids.append(product.pk)
                product_vectors.append(vector_data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error parsing vector data for product {product.pk}: {e}")
                continue

    if not product_vectors:
        logger.info("No valid product vectors found, falling back to default")
        products = Product.objects.all().order_by('price')[:4]
    else:
        try:
            # Convert to numpy array first, then to tensor
            product_vectors = np.array(product_vectors, dtype=np.float32)
            product_vectors = torch.tensor(product_vectors)

            # Get last clicked product from session
            last_clicked_product_id = request.session.get('last_clicked_product')
            logger.info(f"Last clicked product ID: {last_clicked_product_id}")
            
            last_clicked_product = None
            if last_clicked_product_id:
                try:
                    last_clicked_product = Product.objects.get(id=last_clicked_product_id)
                    logger.info(f"Last clicked product: {last_clicked_product.name}, Category: {last_clicked_product.categorys.name if last_clicked_product.categorys else 'None'}")
                except Product.DoesNotExist:
                    logger.warning(f"Last clicked product {last_clicked_product_id} not found")
                    last_clicked_product_id = None

            if request.user.is_authenticated:
                try:
                    logger.info(f"Authenticated user: {request.user.username}")
                    user = User.objects.get(username=request.user.username)
                    user_profile = users.objects.get(name=user)
                    
                    if user_profile.vector_data:
                        user_vector = json.loads(user_profile.vector_data)
                        
                        # Recommend products
                        recommend_products = recommend_product(
                            user_vector, 
                            product_vectors, 
                            product_ids, 
                            top_n=4,
                            last_clicked_product_id=last_clicked_product_id
                        )
                        logger.info(f"Recommended products: {recommend_products}")

                        if recommend_products:
                            # Get product IDs and maintain order
                            product_ids_ordered = [item[0] for item in recommend_products]
                            preserved_order = Case(
                                *[When(pk=pk, then=pos) for pos, pk in enumerate(product_ids_ordered)]
                            )
                            products = Product.objects.filter(
                                pk__in=product_ids_ordered
                            ).order_by(preserved_order)

                            logger.info(f"Products to render: {[p.name for p in products]}")
                        else:
                            logger.info("No recommendations generated, falling back to category or default")
                            if last_clicked_product and last_clicked_product.categorys:
                                # Fallback to category-based recommendations
                                category_products = Product.objects.filter(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id)
                                if category_products.count() >= 4:
                                    products = category_products[:4]
                                else:
                                    products = list(category_products)
                                    remaining_slots = 4 - len(products)
                                    other_products = Product.objects.exclude(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id).order_by('price')[:remaining_slots]
                                    products.extend(other_products)
                                    products = products[:4]
                            else:
                                products = Product.objects.all().order_by('price')[:4]
                    else:
                        logger.info("User has no vector data, using category-based recommendations")
                        if last_clicked_product and last_clicked_product.categorys:
                            category_products = Product.objects.filter(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id)
                            if category_products.count() >= 4:
                                products = category_products[:4]
                            else:
                                products = list(category_products)
                                remaining_slots = 4 - len(products)
                                other_products = Product.objects.exclude(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id).order_by('price')[:remaining_slots]
                                products.extend(other_products)
                                products = products[:4]
                        else:
                            products = Product.objects.all().order_by('price')[:4]

                except (User.DoesNotExist, users.DoesNotExist, json.JSONDecodeError) as e:
                    logger.error(f"Error fetching user or parsing user vector: {e}")
                    if last_clicked_product and last_clicked_product.categorys:
                        category_products = Product.objects.filter(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id)
                        if category_products.count() >= 4:
                            products = category_products[:4]
                        else:
                            products = list(category_products)
                            remaining_slots = 4 - len(products)
                            other_products = Product.objects.exclude(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id).order_by('price')[:remaining_slots]
                            products.extend(other_products)
                            products = products[:4]
                    else:
                        products = Product.objects.all().order_by('price')[:4]
                except Exception as e:
                    logger.error(f"Unexpected error in recommendation: {e}")
                    products = Product.objects.all().order_by('price')[:4]
            else:
                logger.info("Unauthenticated user, using category-based recommendations")
                if last_clicked_product and last_clicked_product.categorys:
                    category_products = Product.objects.filter(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id)
                    if category_products.count() >= 4:
                        products = category_products[:4]
                    else:
                        products = list(category_products)
                        remaining_slots = 4 - len(products)
                        if last_clicked_product:
                            other_products = Product.objects.exclude(categorys=last_clicked_product.categorys).exclude(id=last_clicked_product_id)
                            other_products = sorted(other_products, key=lambda p: abs(p.price - last_clicked_product.price))[:remaining_slots]
                            products.extend(other_products)
                        else:
                            other_products = Product.objects.all().order_by('price')[:remaining_slots]
                            products.extend(other_products)
                        products = products[:4]
                    logger.info(f"Products for unauthenticated user: {[p.name for p in products]}")
                else:
                    logger.info("No last clicked product, using default")
                    products = Product.objects.all().order_by('price')[:4]

        except Exception as e:
            logger.error(f"Error processing product vectors: {e}")
            products = Product.objects.all().order_by('price')[:4]

    # Other product sections
    data2 = Product.objects.all()[:4]
    data3 = Product.objects.all().order_by('-id')[:3]

    context = {
        'product': all_products,
        'products': products,
        'data2': data2,
        'data3': data3,
    }

    return render(request, 'user/index.html', context)
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

# User signup
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
        elif len(username) > 30:
            errors.append('Username must be less than 30 characters.')

        try:
            validate_email(email)
        except ValidationError:
            errors.append('Please enter a valid email address.')

        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        if not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter.')
        if not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter.')
        if not any(c.isdigit() for c in password):
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
            return render(request, "user/userup.html")

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create user profile
        dt = users.objects.create(name=user)

        # Vectorize user data
        user_data = [{
            "user_id": user.id,
            "product": "",
            "search": "",
        }]
        df = pd.DataFrame(user_data)
        user_vectors = vectorize_user_with_search(df)

        # Save vector data
        if user_vectors:
            dt.vector_data = json.dumps(user_vectors[0])  # Fixed: Removed .tolist()
        else:
            messages.warning(request, "User vectorization failed, proceeding without vector data.")
            dt.vector_data = json.dumps([])  # Save empty list as fallback
        dt.save()

        messages.success(request, "Account created successfully!")
        return redirect('userin')

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

# def product_details(request, pk):
#     product = get_object_or_404(Product, id=pk)

#     images = [img for img in [
#         product.image, product.image1, product.image2,
#         product.image3, product.image4, product.image5
#     ] if img]

#     cart_product_ids = []
#     cart_item_count = 0

#     if request.user.is_authenticated:
#         cart_items = Cart.objects.filter(user=request.user)
#         cart_product_ids = list(cart_items.values_list('product_id', flat=True))
#         cart_item_count = cart_items.count()

#     related_products = Product.objects.filter(
#         categorys=product.categorys
#     ).exclude(id=pk)[:4] if product.categorys else []

#     product_reviews = reviews.objects.filter(pname=product)

#     is_reviewed = False
#     if request.user.is_authenticated:
#         try:
#             user_profile = users.objects.get(name=request.user)
#             is_reviewed = reviews.objects.filter(uname=user_profile, pname=product).exists()
#         except users.DoesNotExist:
#             pass

#     context = {
#         'product': product,
#         'images': images,
#         'cart_product_ids': cart_product_ids,
#         'cart_item_count': cart_item_count,
#         'page_title': f"{product.name} - OPTICFRAMES",
#         'first_image': images[0] if images else None,
#         'related_products': related_products,
#         'reviews': product_reviews,
#         'is_reviewed': is_reviewed,
#     }

#     return render(request, 'user/product_details.html', context)



logger = logging.getLogger(__name__)

# def product_details(request, pk):
#     product = get_object_or_404(Product, id=pk)

#     # Track product click
#     if request.user.is_authenticated:
#         try:
#             user_profile = users.objects.get(name=request.user)  # Replace 'name' with 'user' if needed
#             # Create ViewHistory if it doesn't exist
#             view_history, created = ViewHistory.objects.get_or_create(
#                 user=user_profile,
#                 product=product
#             )
#             if created:
#                 logger.info(f"ViewHistory created for user {user_profile} and product {product.name}")
#             else:
#                 logger.info(f"ViewHistory already exists for user {user_profile} and product {product.name}")

#             # Update user vector
#             try:
#                 # Get user search and view history
#                 user_search = [s.query for s in SearchHistory.objects.filter(user=user_profile)]
#                 user_products = [p.product.name for p in ViewHistory.objects.filter(user=user_profile)]

#                 # Prepare data for vectorization
#                 user_data = [{
#                     'user_id': request.user.id,
#                     'product': ','.join(user_products) if user_products else '',
#                     'search': ','.join(user_search) if user_search else ''
#                 }]
#                 df = pd.DataFrame(user_data)

#                 # Vectorize and save
#                 user_vectors = vectorize_user_with_search(df)
#                 if user_vectors:
#                     user_profile.vector_data = json.dumps(user_vectors[0])
#                     user_profile.save()
#                     logger.info(f"User vector updated for user {user_profile}")
#                 else:
#                     logger.warning(f"Failed to vectorize user {user_profile}")
#             except Exception as e:
#                 logger.error(f"Error updating user vector for {user_profile}: {e}")

#         except users.DoesNotExist:
#             logger.warning(f"User profile not found for authenticated user {request.user.username}")

#     # Store in session
#     request.session['last_clicked_product'] = pk
#     request.session.modified = True

#     images = [img for img in [
#         product.image, product.image1, product.image2,
#         product.image3, product.image4, product.image5
#     ] if img]

#     cart_product_ids = []
#     cart_item_count = 0

#     if request.user.is_authenticated:
#         cart_items = Cart.objects.filter(user=request.user)
#         cart_product_ids = list(cart_items.values_list('product_id', flat=True))
#         cart_item_count = cart_items.count()

#     related_products = Product.objects.filter(
#         categorys=product.categorys
#     ).exclude(id=pk)[:4]

#     product_reviews = reviews.objects.filter(pname=product)

#     is_reviewed = False
#     if request.user.is_authenticated:
#         try:
#             user_profile = users.objects.get(name=request.user)  # Replace 'name' with 'user' if needed
#             is_reviewed = reviews.objects.filter(uname=user_profile, pname=product).exists()
#         except users.DoesNotExist:
#             pass

#     context = {
#         'product': product,
#         'images': images,
#         'cart_product_ids': cart_product_ids,
#         'cart_item_count': cart_item_count,
#         'page_title': f"{product.name} - OPTICFRAMES",
#         'first_image': images[0] if images else None,
#         'related_products': related_products,
#         'reviews': product_reviews,
#         'is_reviewed': is_reviewed,
#     }

#     return render(request, 'user/product_details.html', context)

def product_details(request, pk):
    product = get_object_or_404(Product, id=pk)

    # Track product click
    if request.user.is_authenticated:
        try:
            user_profile = users.objects.get(name=request.user)
            view_history, created = ViewHistory.objects.get_or_create(
                user=user_profile,
                product=product
            )
            if created:
                logger.info(f"ViewHistory created for user {user_profile} and product {product.name}")
            else:
                logger.info(f"ViewHistory already exists for user {user_profile} and product {product.name}")

            # Update user vector
            try:
                user_search = [s.query for s in SearchHistory.objects.filter(user=user_profile)]
                user_products = [p.product.name for p in ViewHistory.objects.filter(user=user_profile)]
                user_data = [{
                    'user_id': request.user.id,
                    'product': ','.join(user_products) if user_products else '',
                    'search': ','.join(user_search) if user_search else ''
                }]
                df = pd.DataFrame(user_data)
                user_vectors = vectorize_user_with_search(df)
                if user_vectors:
                    user_profile.vector_data = json.dumps(user_vectors[0])
                    user_profile.save()
                    logger.info(f"User vector updated for user {user_profile}")
                else:
                    logger.warning(f"Failed to vectorize user {user_profile}")
            except Exception as e:
                logger.error(f"Error updating user vector for {user_profile}: {e}")

        except users.DoesNotExist:
            logger.warning(f"User profile not found for authenticated user {request.user.username}")

    # Store in session
    request.session['last_clicked_product'] = pk
    request.session.modified = True
    logger.info(f"Set last_clicked_product in session: {pk}")

    images = [img for img in [
        product.image, product.image1, product.image2,
        product.image3, product.image4, product.image5
    ] if img]

    cart_product_ids = []
    cart_item_count = 0

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_product_ids = list(cart_items.values_list('product_id', flat=True))
        cart_item_count = cart_items.count()

    related_products = Product.objects.filter(
        categorys=product.categorys
    ).exclude(id=pk)[:4]

    product_reviews = reviews.objects.filter(pname=product)

    is_reviewed = False
    if request.user.is_authenticated:
        try:
            user_profile = users.objects.get(name=request.user)
            is_reviewed = reviews.objects.filter(uname=user_profile, pname=product).exists()
        except users.DoesNotExist:
            pass

    context = {
        'product': product,
        'images': images,
        'cart_product_ids': cart_product_ids,
        'cart_item_count': cart_item_count,
        'page_title': f"{product.name} - OPTICFRAMES",
        'first_image': images[0] if images else None,
        'related_products': related_products,
        'reviews': product_reviews,
        'is_reviewed': is_reviewed,
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

# Admin add product
@login_required
def adminadd(request):
    categories = category.objects.all()
    genders = Gender.objects.all()
    materials = Material.objects.all()
    frame_types = FrameType.objects.all()
    frame_shapes = FrameShape.objects.all()
    frame_styles = FrameStyle.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        color = request.POST.get('color')

        gender_id = request.POST.get('gender')
        material_id = request.POST.get('material')
        frame_type_id = request.POST.get('frame_type')
        frame_shape_id = request.POST.get('frame_shape')
        frame_style_id = request.POST.get('frame_style')
        category_id = request.POST.get('category')

        main_image = request.FILES.get('main_image')
        additional_images = request.FILES.getlist('additional_images')

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
            product = Product(
                name=name,
                price=float(price),
                description=description,
                color=color,
                image=main_image
            )

            if gender_id:
                product.gender = Gender.objects.get(id=gender_id)
            if material_id:
                product.material = Material.objects.get(id=material_id)
            if frame_type_id:
                product.frame_type_id = FrameType.objects.get(id=frame_type_id)
            if frame_shape_id:
                product.frameShape = FrameShape.objects.get(id=frame_shape_id)
            if frame_style_id:
                product.frameStyle = FrameStyle.objects.get(id=frame_style_id)
            if category_id:
                category_obj = category.objects.get(id=category_id)
                product.categorys = category_obj
            else:
                category_obj = None

            product.save()

            for i, img in enumerate(additional_images[:5]):
                setattr(product, f'image{i+1}', img)
            product.save()

            try:
                df = pd.DataFrame([{
                    "id": product.id,
                    "title": product.name,  # Fixed key
                    "rating": 0,
                    "categorys": product.categorys.name if product.categorys else "",  # Fixed key
                    "description": product.description,
                    "reviews": '',
                }])

                product_vector = vectorize_product_with_reviews(df)
                print(f"Product vector: {product_vector}")  # Debug
                if product_vector and len(product_vector) > 0:
                    product.vector_data = json.dumps(product_vector[0])
                else:
                    print(f"Vectorization failed for product {product.id}")
                    product.vector_data = json.dumps([])  # Fallback
                product.save()

            except Exception as ve:
                import traceback
                traceback.print_exc()
                messages.warning(request, f"Product saved but vectorization failed: {str(ve)}")
                product.vector_data = json.dumps([])  # Fallback
                product.save()

            messages.success(request, f"Product '{name}' added successfully!")
            return redirect('adminhome')

        except Exception as e:
            messages.error(request, f"Error adding product: {str(e)}")

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

from django.core.paginator import Paginator

import logging
import pandas as pd
import json
import numpy as np
import torch
from django.shortcuts import render, redirect
from django.db.models import Q, Case, When
from django.core.paginator import Paginator
from sentence_transformers import util
from .models import Product, users, SearchHistory, ViewHistory, Cart, category, Gender, Material

logger = logging.getLogger(__name__)

def types(request):
    return list(Product.objects.values_list('categorys__name', flat=True).distinct())

def search_func(request):
    if request.method == 'GET':
        # Get query parameters
        query = request.GET.get('search', '').strip()
        category_id = request.GET.get('category', '')
        gender_id = request.GET.get('gender', '')
        material_id = request.GET.get('material', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        sort_by = request.GET.get('sort', 'name')  # Default to Name A-Z

        if not query:
            logger.info("Empty search query, redirecting to index")
            return redirect('index')

        # Fetch filter options
        categories = category.objects.all()
        genders = Gender.objects.all()
        materials = Material.objects.all()

        # Initialize context
        context = {
            'query': query,
            'categories': categories,
            'genders': genders,
            'materials': materials,
            'selected_category': category_id,
            'selected_gender': gender_id,
            'selected_material': material_id,
            'min_price': min_price,
            'max_price': max_price,
            'sort_by': sort_by,
            'cart_item_count': 0,
            'wishlist_item_count': 0,  # No Wishlist model; set to 0
            'category': types(request),
            'total_results': 0,
        }

        # Handle authenticated user
        if request.user.is_authenticated:
            try:
                user_obj = users.objects.get(name=request.user)
                SearchHistory.objects.create(query=query, user=user_obj)

                try:
                    user_search = [s.query for s in SearchHistory.objects.filter(user=user_obj)]
                    user_products = [p.product.name for p in ViewHistory.objects.filter(user=user_obj)]
                    user_data = [{
                        'user_id': request.user.id,
                        'product': ','.join(user_products) if user_products else '',
                        'search': ','.join(user_search) if user_search else ''
                    }]
                    df = pd.DataFrame(user_data)
                    user_vectors = vectorize_user_with_search(df)
                    if user_vectors:
                        user_obj.vector_data = json.dumps(user_vectors[0].tolist())
                        user_obj.save()
                        logger.info(f"User vector updated for {user_obj}")
                    else:
                        logger.warning(f"Failed to vectorize user {user_obj}")
                except Exception as e:
                    logger.error(f"Error updating user vector: {e}")

                context['cart_item_count'] = Cart.objects.filter(user=request.user).count()
            except users.DoesNotExist:
                logger.warning(f"No user profile for {request.user.username}")

        # Build the product query
        query_filters = Q()
        if query:
            query_filters &= (Q(name__icontains=query) | Q(categorys__name__icontains=query))

        # Apply filters
        if category_id:
            query_filters &= Q(categorys__id=category_id)
        if gender_id:
            query_filters &= Q(gender__id=gender_id)
        if material_id:
            query_filters &= Q(material__id=material_id)
        if min_price:
            try:
                query_filters &= Q(price__gte=float(min_price))
            except ValueError:
                logger.warning(f"Invalid min_price: {min_price}")
        if max_price:
            try:
                query_filters &= Q(price__lte=float(max_price))
            except ValueError:
                logger.warning(f"Invalid max_price: {max_price}")

        # Search products
        results = Product.objects.filter(query_filters).distinct()
        logger.info(f"Search results: {[p.id for p in results]}")

        # Vector-based ranking for authenticated users (if no sort specified)
        if results and request.user.is_authenticated and sort_by not in ['name', 'price_low', 'price_high', 'newest']:
            try:
                user_obj = users.objects.get(name=request.user)
                if user_obj.vector_data:
                    user_vector = torch.tensor(json.loads(user_obj.vector_data), dtype=torch.float32)
                    product_ids = []
                    product_vectors = []
                    for product in results:
                        if product.vector_data and product.pk:
                            try:
                                vector = json.loads(product.vector_data)
                                product_ids.append(product.pk)
                                product_vectors.append(vector)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid vector_data for product {product.id}")
                                continue

                    if product_vectors:
                        product_vectors = torch.tensor(product_vectors, dtype=torch.float32)
                        similarities = util.cos_sim(user_vector, product_vectors)
                        similarity_scores = similarities[0].numpy()
                        sorted_indices = np.argsort(similarity_scores)[::-1]
                        top_n = min(len(product_ids), 10)
                        top_product_ids = [product_ids[i] for i in sorted_indices[:top_n]]
                        preserved_order = Case(
                            *[When(pk=pk, then=pos) for pos, pk in enumerate(top_product_ids)]
                        )
                        results = Product.objects.filter(pk__in=top_product_ids).order_by(preserved_order)
            except Exception as e:
                logger.error(f"Vector search error for user {request.user.username}: {e}")

        # Apply sorting
        if sort_by == 'name':
            results = results.order_by('name')
        elif sort_by == 'price_low':
            results = results.order_by('price')
        elif sort_by == 'price_high':
            results = results.order_by('-price')
        elif sort_by == 'newest':
            results = results.order_by('-id')

        # Pagination
        paginator = Paginator(results, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['products'] = page_obj  # Use 'products' to match template
        context['total_results'] = results.count()

        return render(request, 'user/search_func.html', context)

    logger.info("Non-GET request to search_func, redirecting to index")
    return redirect('index')

# def search_func(request):
#     if request.method == 'POST':
#         inp = request.POST.get('searched', '').strip()

#         if not inp:
#             return redirect('index')

#         auth_user = None
#         users_data = None

#         if 'username' in request.session:
#             try:
#                 auth_user = User.objects.get(username=request.session['username'])
#                 users_data = users.objects.get(name=auth_user)
#             except (User.DoesNotExist, users.DoesNotExist):
#                 pass

#         if auth_user and users_data:
#             # Save search history
#             SearchHistory.objects.create(query=inp, user=users_data)

#             # Get search history
#             user_search_queries = [search.query for search in SearchHistory.objects.filter(user=users_data)]

#             # Collect previously viewed or purchased product titles
#             user_products = [
#                 view.product.title for view in ViewHistory.objects.filter(user=users_data)
#             ] + [
#                 order.product.title for order in Order.objects.filter(user=auth_user)
#             ]

#             # Prepare data for vectorization
#             user_data = [{
#                 'user_id': auth_user.id,
#                 'product': ','.join(user_products),
#                 'search': ','.join(user_search_queries),
#             }]
#             df = pd.DataFrame(user_data)

#             # Vectorize and save
#             user_vectors = vectorize_user_with_search(df)
#             users_data.vector_data = json.dumps(user_vectors[0].tolist())
#             users_data.save()

#         # Search products using icontains
#         products = Product.objects.filter(
#             Q(title__icontains=inp) | Q(description__icontains=inp) | Q(category__name__icontains=inp)
#         ).distinct()

#         return render(request, 'user/search_func.html', {
#             'category': types(request),
#             'user': getuser(request),
#             'query': inp,
#             'products': products
#         })
#     return redirect('index')

def addReview(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to submit a review.")
        return redirect('signin')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        description = request.POST.get('description')

        if not rating or not description:
            messages.error(request, "Rating and description are required.")
            return redirect('product_details', pk=pk)

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except ValueError:
            messages.error(request, "Rating must be a valid number between 1 and 5.")
            return redirect('product_details', pk=pk)

        product = get_object_or_404(Product, pk=pk)

        try:
            user_profile = users.objects.get(name=request.user)
        except users.DoesNotExist:
            messages.error(request, "User profile not found.")
            return redirect('product_details', pk=pk)

        if reviews.objects.filter(uname=user_profile, pname=product).exists():
            messages.error(request, "You have already reviewed this product.")
            return redirect('product_details', pk=pk)

        review = reviews.objects.create(
            rating=rating,
            description=description,
            uname=user_profile,
            pname=product
        )

        # Update product rating
        all_reviews = reviews.objects.filter(pname=product)
        ratings = [r.rating for r in all_reviews]
        product.rating = round(sum(ratings) / len(ratings), 1) if ratings else float(rating)
        product.save()

        # Vector update if needed
        try:
            comments = [r.description for r in all_reviews]
            df = pd.DataFrame([{
                "id": product.id,
                "name": product.name,
                "rating": product.rating,
                "category": product.categorys.name if product.categorys else "",
                "description": product.description,
                "reviews": ','.join(comments)
            }])
            product_vector = vectorize_product_with_reviews(df)
            product.vector_data = json.dumps(product_vector[0].tolist())
            product.save()
        except Exception as e:
            messages.warning(request, f"Review saved, but vector update failed: {e}")

        messages.success(request, "Review submitted successfully!")
        return redirect('product_details', pk=pk)

    return redirect('product_details', pk=pk)
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

