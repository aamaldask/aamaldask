from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from cart.models import Cart,payment,Order_details
from shop.models import products
from django.contrib.auth.models import User
from django.contrib.auth import login
import razorpay
@login_required
def add_to_cart(request,i):
    p=products.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(p.stock>0):
            c.quantity+=1
            c.save()
            p.stock-=1
            p.save()
    except:
        if(p.stock>0):
            c=Cart.objects.create(product=p,user=u,quantity=1)
            c.save()
            p.stock-=1
            p.save()

    return redirect('cart:cartview')

@login_required
def cart_view(request):
    u=request.user
    total=0
    c=Cart.objects.filter(user=u)
    for i in c:
        total+=i.quantity*i.product.price
    context={'cart':c,'total':total}
    return render(request,'cart.html',context)



@login_required
def cart_remove(request,i):
    p=products.objects.get(id=i)
    u=request.user
    try:
        c=Cart.objects.get(user=u,product=p)
        if(c.quantity>1):
            c.quantity-=1
            c.save()
            p.stock+=1
            p.save()
        else:
            c.delete()
            p.stock+=1
            p.save()
    except:
        pass

    return redirect('cart:cartview')


@login_required
def cart_delete(request,i):
    u=request.user
    p=products.objects.get(id=i)
    try:
        c=Cart.objects.get(user=u,product=p)
        c.delete()
        p.stock+=c.quantity
        p.save()
    except:
        pass
    return redirect('cart:cartview')

@login_required
def orderform(request):
    if(request.method=="POST"):
        address=request.POST['a']
        phone=request.POST['p']
        pin=request.POST['pi']
        u=request.user
        c=Cart.objects.filter(user=u)
        total=0
        for i in c:
            total+=i.quantity*i.product.price
        total=int(total*100)
        client=razorpay.Client(auth=('rzp_test_Sbay48BwRsl3R4','Q4RFUM2PbVtZ00VKOU9BZvwb'))
        response_payment=client.order.create(dict(amount=total,currency="INR"))
        # print(response_payment)
        order_id=response_payment['id']
        order_status=response_payment['status']
        if(order_status=="created"):
            p=payment.objects.create(name=u.username,amount=total,order_id=order_id)
            p.save()
            for i in c:
                o=Order_details.objects.create(product=i.product,user=u,no_of_items=i.quantity,address=address,phone_no=phone,pin=pin,order_id=order_id)
                o.save()
        else:
            pass
        response_payment['name']=u.username
        context={'payment':response_payment}
        return render(request, 'payment.html',context)

    return render(request,'orderform.html')


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def payment_status(request, u):
    status = "failed"  # Default to failed status
    if not request.user.is_authenticated:  # if user is not authenticated
        user = get_object_or_404(User, username=u)
        login(request, user)  # Allowing request user to login

    if request.method == "POST":
        response = request.POST
        print("Response from Razorpay:", response)

        param_dict = {
            'razorpay_order_id': response['razorpay_order_id'],
            'razorpay_payment_id': response['razorpay_payment_id'],
            'razorpay_signature': response['razorpay_signature'],
        }
        print("Param dict for verification:", param_dict)

        client = razorpay.Client(auth=('rzp_test_Sbay48BwRsl3R4', 'Q4RFUM2PbVtZ00VKOU9BZvwb'))

        try:
            # Verify the payment signature
            status=client.utility.verify_payment_signature(param_dict)
              # Payment verification was successful

            # Update payment record
            p = payment.objects.get(order_id=response['razorpay_order_id'])
            p.razorpay_payment_id = response['razorpay_payment_id']
            p.paid = True
            p.save()

            # Update order details
            user = User.objects.get(username=u)
            orders = Order_details.objects.filter(user=user, order_id=response['razorpay_order_id'])
            for order in orders:
                order.payment_status = "paid"
                order.save()

            # Clear the cart
            Cart.objects.filter(user=user).delete()

        except razorpay.errors.SignatureVerificationError as e:
            print(f"Signature verification failed: {e}")
            status = "failed"
        except Exception as e:
            print(f"Error processing payment: {e}")
            status = "failed"

    return render(request, 'payment_status.html', {'status': status})


def orders(request):
    u=request.user
    o=Order_details.objects.filter(user=u,payment_status="paid")
    context={'orders':o}
    return render(request,'your_orders.html',context)


