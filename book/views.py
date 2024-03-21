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

class BookApi(APIView):
    
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    @swagger_auto_schema(request_body=BookSerializer, responses={201: openapi.Response(description="Book Added", examples={
                             "application/json": {'message': 'Book Added Successfully', 'status': 201, 'data': {}}
                         }),
                                    400: "Bad Request"})
    
    def post(self, request):
        try:
            request.data['user'] = request.user.id
            serializer = BookSerializer(data = request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Added Successfully!', 'status': 201, 
                            'data': serializer.data}, status = 201)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status = 400)
        
    @swagger_auto_schema(responses={200: openapi.Response(description="Books Fetched Successfully!", examples={
                             "application/json": {'message': 'Books Fetched Successfully!', 'status': 200}
                         }),
                                    400: "Bad Request", 401: "Unauthorized"})
    
    def get(self, request):
        try:
            books = Books.objects.all()
            serializer = BookSerializer(instance=books, many=True)
            return Response({'message': 'Books Fetched Successfully!', 'status': 200, 'books': serializer.data}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status = 400)
        
    @swagger_auto_schema(request_body=BookSerializer, responses={200: openapi.Response(description="Book Updated", examples={
                             "application/json": {'message': 'Book Updated Successfully', 'status': 200, 'data': {}}
                         }),
                                    400: "Bad Request"})
    
    def put(self, request):
        try:
            request.data['user'] = request.user.id
            book = Books.objects.get(id=request.data['id'])
            serializer = BookSerializer(instance=book, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Book Updated Successfully!', 'status': 200, 
                            'data': serializer.data}, status=200)
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)
        
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
    ], responses={200: openapi.Response(description="Book Deleted successfully", examples={
                             "application/json": {'message': 'Book Deleted successfully', 'status': 200}
                         }),
                                    400: "Bad Request"})  
    
    def delete(self, request):
        try:
            if request.user.is_superuser:
                book_id = request.query_params.get('id')
                books = Books.objects.get(id = book_id)
                books.delete()
                return Response({'message': 'Book Deleted Successfully', 'status': 200},status=200)
            raise PermissionDenied("Access denied")
        except Exception as e:
            return Response({'message': str(e), 'status': 400}, status=400)