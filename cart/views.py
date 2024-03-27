from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer, ItemSerializer
from .models import Cart, CartItems
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='bookstore.log')

logger = logging.getLogger(__name__)

# Create your views here.
class CartApi(APIView):
    
    throttle_scope = "cart_api"
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    """
    This resource handles the creation of cart.

    Methods:
        - POST: Create cart.

    Request Body:
        - name - str, required. The details of the cart items to add to cart.

    Responses:
        - 201: If the cart is successfully created. Returns a success message, status code 201, and the created cart data.
        - 400: If there is an error during cart creation. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'book': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['book', 'quantity']
    ),
    responses={
        201: openapi.Response(
            description="Added Item to Cart",
            examples={"application/json": {'message': 'Added Item to Cart', 'status': 201, 'data': {}}}
        ),
        400: "Bad Request",
        401: "Unauthorized"
    }
)
    
    def post(self, request):
        try:
            request.data["user"] = request.user.id
            serializer = CartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Added Item to Cart', 'status': 201, 'data': serializer.data}, status=201)
        except Exception as e:
            logger.error(f"An error occurred while creating cart: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
  
    """
    This resource handles the fetching of cart.

    Methods:
        - GET: Fetch cart.

    Request Body:
        - Not required.

    Responses:
        - 200: If the cart is successfully retrieved. Returns a success message, status code 200, and the fetched cart data.
        - 400: If there is an error during cart retrieval. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(responses={200: openapi.Response(description="Successfully Fetched Cart Items", examples={
                             "application/json": {'message': 'Successfully Fetched Cart Items', 'status': 200, 'data': {}}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})  
    
    def get(self, request):
        try:
            user_id = request.user.id
            cart = Cart.objects.filter(user_id=user_id, is_ordered=False).first()
            if cart:
                cart_items = CartItems.objects.filter(cart=cart)
                serializer = ItemSerializer(cart_items, many=True)
                return Response({'message': 'Successfully Fetched Cart Items', 'status': 200, 'Cart Items': serializer.data}, status=200)
            else:
                return Response({'message': 'Cart not found', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while fetching cart: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
    
    """
    This resource handles the deletion of cart.

    Methods:
        - DELETE: Delete cart.

    Request Body:
        - Not required.

    Responses:
        - 200: If the cart is successfully deleted. Returns a success message, status code 200.
        - 400: If there is an error during cart deletion. Returns an error message and status code 400.
    """  
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ],responses={200: openapi.Response(description="Cart Deleted Successfully!", examples={
                             "application/json": {'message': 'Cart Deleted Successfully!', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})       
             
    def delete(self, request):
        try:
            user_id = request.user.id
            cart_id = request.query_params.get('id')
            if cart_id is None:
                return Response({'message': 'Cart ID is not provided', 'status': 400}, status=400)
            cart = Cart.objects.get(user_id = user_id, id=cart_id)
            cart.delete()
            return Response({'message': 'Cart Deleted Successfully!', 'status': 200}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while deleting cart: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)

class OrderApi(APIView):
    
    throttle_scope = "order_api"
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    """
    This resource handles the placing of order.

    Methods:
        - POST: Place order.

    Request Body:
        - name - str, required. The cart id to place order.

    Responses:
        - 200: If the order is successfully placed. Returns a success message, status code 200.
        - 400: If there is an error during placing order. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['id']
    ),
    responses={
        200: openapi.Response(
            description="Order Placed Successfully!",
            examples={"application/json": {'message': 'Order Placed Successfully!', 'status': 200}}
        ),
        400: "Bad Request",
        401: "Unauthorized"
    }
)
        
    def post(self, request):
        try:
            cart = Cart.objects.filter(user_id=request.user.id, id=request.data['id'], is_ordered=False).first()
            if cart is not None:
                cart_items = CartItems.objects.filter(cart=cart)
                for cart_item in cart_items:
                    book = cart_item.book
                    if book.quantity <= cart_item.quantity:
                        raise ValueError('Insufficient quantity for book: {}'.format(book.title))
                    for cart_item in cart_items:
                        book = cart_item.book
                        book.quantity -= cart_item.quantity
                        book.save()
                    cart.is_ordered = True
                    cart.save()
                    return Response({'message': 'Order Placed Successfully!', 'status': 200}, status=200)
            return Response({'message':'Cart does not exist', 'status': 200}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while placing order: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
      
    """
    This resource handles the fetching of order details.

    Methods:
        - GET: Fetch order details.

    Request Body:
        - Not required.

    Responses:
        - 200: If the order details is successfully retrieved. Returns a success message, status code 200, and the fetched order details.
        - 400: If there is an error during order details retrieval. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(responses={200: openapi.Response(description="Successfully Fetched Order Details", examples={
                             "application/json": {'message': 'Successfully Fetched Order Details', 'status': 200, 'data':{}}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})    
    
    def get(self, request):
        try:
            cart = Cart.objects.filter(user_id=request.user.id, is_ordered=True).first()
            if cart:
                cart_items = CartItems.objects.filter(cart=cart)
                serializer = ItemSerializer(cart_items, many=True)
                return Response({'message': 'Successfully Fetched Order Details', 'status': 200, 'Ordered Items': serializer.data}, status=200)
            else:
                return Response({'message': 'Order not found', 'status': 404}, status=404)
        except Exception as e:
            logger.error(f"An error occurred while fetching order details: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
    
    """
    This resource handles the cancellation of the order.

    Methods:
        - DELETE: Cancel Order.

    Request Body:
        - Not required.

    Responses:
        - 200: If the order is successfully cancelled. Returns a success message, status code 200.
        - 400: If there is an error during order cancellation. Returns an error message and status code 400.
    """  
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ],responses={200: openapi.Response(description="Order Cancelled Successfully!", examples={
                             "application/json": {'message': 'Order Cancelled Successfully!', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized", 404: "Cart does not exist or is not ordered"})       
        
    def delete(self, request):
        try:
            cart_id = request.query_params.get('id')
            if cart_id is None:
                logger.error(f"Cart ID is not provided")
                return Response({'message': 'Cart ID is not provided', 'status': 400}, status=400)
            cart = Cart.objects.filter(user_id=request.user.id, id=cart_id, is_ordered=True).first()
            if cart is None:
                return Response({'message': 'Cart does not exist or is not ordered', 'status': 404}, status=404)
            cart_items = CartItems.objects.filter(cart=cart)
            for cart_item in cart_items:
                book = cart_item.book
                book.quantity += cart_item.quantity
                book.save()
            cart.delete()
            return Response({'message': 'Order Cancelled Successfully!', 'status': 200}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while cancelling order: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)   