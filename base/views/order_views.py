from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from base.models import Product, Order, OrderItem, ShippingAddress
from base.serializers import ProductSerializer, OrderSerializer

from rest_framework import status
from datetime import datetime


def send_order_confirmation_email(order, user, order_items, shipping):
    """Send order confirmation email to the customer."""
    try:
        subject = f'Order Confirmed - Digital Edge (#{ order._id })'

        # Build items list for email
        items_text = '\n'.join([
            f"  - {item.name} x{item.qty}  @ ${item.price} each"
            for item in order_items
        ])

        message = f"""
Hi {user.first_name or user.username},

Thank you for your order! Your order has been placed successfully.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORDER CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Order ID   : #{order._id}
Date       : {order.createdAt.strftime('%B %d, %Y at %I:%M %p')}
Payment    : {order.paymentMethod}

ITEMS ORDERED:
{items_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICE BREAKDOWN:
  Subtotal   : ${float(order.totalPrice) - float(order.shippingPrice) - float(order.taxPrice):.2f}
  Shipping   : ${float(order.shippingPrice):.2f}
  Tax        : ${float(order.taxPrice):.2f}
  ─────────────────────────
  TOTAL      : ${float(order.totalPrice):.2f}

SHIPPING ADDRESS:
  {shipping.address}
  {shipping.city}, {shipping.postalCode}
  {shipping.country}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{'Your order will be paid on delivery (COD).' if order.paymentMethod == 'COD' else 'Please complete your payment to process the order.'}

Thank you for shopping with Digital Edge!
Team Digital Edge
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,  # Don't crash if email fails
        )
        print(f"[ORDER] Confirmation email sent to {user.email} for order #{order._id}")
    except Exception as e:
        print(f"[ORDER] Email sending failed: {e}")


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
    else:

        # (1) Create order
        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice=data['taxPrice'],
            shippingPrice=data['shippingPrice'],
            totalPrice=data['totalPrice']
        )

        # (2) Create shipping address
        shipping = ShippingAddress.objects.create(
            order=order,
            address=data['shippingAddress']['address'],
            city=data['shippingAddress']['city'],
            postalCode=data['shippingAddress']['postalCode'],
            country=data['shippingAddress']['country'],
        )

        # (3) Create order items and set order to orderItem relationship
        created_items = []
        for i in orderItems:
            product = Product.objects.get(_id=i['product'])

            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                qty=i['qty'],
                price=i['price'],
                image=product.image.url,
            )
            created_items.append(item)

            # (4) Update stock
            product.countInStock -= item.qty
            product.save()

        # (5) Send confirmation email
        send_order_confirmation_email(order, user, created_items, shipping)

        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):

    user = request.user

    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail': 'Not authorized to view this order'},
                     status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()

    return Response('Order was paid')


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.get(_id=pk)

    order.isDelivered = True
    order.deliveredAt = datetime.now()
    order.save()

    return Response('Order was delivered')
