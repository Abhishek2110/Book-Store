from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Books
from user.models import User
from .serializers import BookSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename='bookstore.log')

logger = logging.getLogger(__name__)

class BookApi(APIView):
    
    throttle_scope = "book_api"
     
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    """
    This resource handles the creation of books.

    Methods:
        - POST: Create books.

    Request Body:
        - name - str, required. The details of the books to add.

    Responses:
        - 201: If the book is successfully created. Returns a success message, status code 201, and the created book data.
        - 400: If there is an error during book creation. Returns an error message and status code 400.
    """
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
            'price': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['title', 'author', 'price', 'quantity']
    ),
    responses={
        201: openapi.Response(
            description="Book Added Successfully!",
            examples={"application/json": {'message': 'Book Added Successfully!', 'status': 201, 'data': {}}}
        ),
        400: "Bad Request",
        401: "Unauthorized"
    }
)
    
    def post(self, request):
        try:
            request.data['user'] = request.user.id
            serializer = BookSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Added Successfully!', 'status': 201, 
                            'data': serializer.data}, status = 201)
        except Exception as e:
            logger.error(f"An error occurred while adding book: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status = 400)
    
    """
    This resource handles the fetching of books.

    Methods:
        - GET: Fetch books.

    Request Body:
        - Not required.

    Responses:
        - 200: If the books are successfully retrieved. Returns a success message, status code 200, and the fetched books data.
        - 400: If there is an error during books retrieval. Returns an error message and status code 400.
    """
        
    @swagger_auto_schema(responses={200: openapi.Response(description="Books Fetched Successfully!", examples={
                             "application/json": {'message': 'Books Fetched Successfully!', 'status': 200, 'data': {}}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})
    
    def get(self, request):
        try:
            books = Books.objects.all()
            serializer = BookSerializer(instance=books, many=True)
            return Response({'message': 'Books Fetched Successfully!', 'status': 200, 'books': serializer.data}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while fetching books: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status = 400)
      
    """
    This resource handles the updation of books.

    Methods:
        - PUT: Update books.

    Request Body:
        - name - str, required. The details of the book to update.

    Responses:
        - 200: If the book is successfully updated. Returns a success message, status code 200, and the updated book data.
        - 400: If there is an error during books updation. Returns an error message and status code 400.
        - 404: If book is not found. Returns an error message and status code 404.
    """  
    
    @swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'author': openapi.Schema(type=openapi.TYPE_STRING),
            'price': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
        required=['title', 'author', 'price', 'quantity']
    ),
    responses={
        201: openapi.Response(
            description="Book Updated Successfully!",
            examples={"application/json": {'message': 'Book Updated Successfully!', 'status': 201, 'data': {}}}
        ),
        400: "Bad Request",
        401: "Unauthorized",
        404: "Book Not Found"
    }
)
    
    def put(self, request):
        try:
            request.data['user'] = request.user.id
            book = Books.objects.get(id=request.data['id'])
            if book is None:
                logger.error(f"Book Not Found")
                return Response({'message': 'Book Not Found', 'status': 404}, status=404)
            serializer = BookSerializer(instance=book, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Updated Successfully!', 'status': 200, 
                            'data': serializer.data}, status=200)
        except Exception as e:
            logger.error(f"An error occurred while updating book: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)
      
    """
    This resource handles the deletion of books.

    Methods:
        - DELETE: Delete books.

    Request Body:
        - Not required.

    Responses:
        - 200: If the book is successfully deleted. Returns a success message, status code 200.
        - 400: If there is an error during books deletion. Returns an error message and status code 400.
        - 404: If book is not found. Returns an error message and status code 404.
    """  
    
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)
    ], responses={200: openapi.Response(description="Book Deleted successfully", examples={
                             "application/json": {'message': 'Book Deleted successfully', 'status': 200}
                         }),
                                    400: "Bad Request"})  
    
    def delete(self, request):
        try:
            if request.user.is_superuser:
                book_id = request.query_params.get('id')
                books = Books.objects.get(id = book_id)
                if books is None:
                    logger.error(f"Book Not Found")
                    return Response({'message': 'Book Not Found', 'status': 404}, status=404)
                books.delete()
                return Response({'message': 'Book Deleted Successfully', 'status': 200},status=200)
            raise PermissionDenied("Access denied")
        except Exception as e:
            logger.error(f"An error occurred while deleting book: {str(e)}")
            return Response({'message': str(e), 'status': 400}, status=400)