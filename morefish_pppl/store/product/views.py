import logging
from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http.response import HttpResponseBadRequest
from store.product.models import Product, ProductCategory, ProductCompany
from store.product.serializers import (
    CategorySerializer,
    ProductDetailsSerializer,
    ProductListSerializer,
    ProductSerializer,
    ProductCompanySerializer
)

from django.core.paginator import Paginator
from rest_framework.response import Response


logger = logging.getLogger("__name__")
logger.setLevel(logging.ERROR)


class CategoryList(APIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    def get(self, request: HttpRequest):
        category_list = ProductCategory.objects.all()

        return Response(
            {
                "data": CategorySerializer(category_list, many=True).data,
                "status_code": status.HTTP_200_OK,
                "success": "True",
            }
        )


class ProductList(APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer

    def get(self, request: HttpRequest):
        """
        Retrieve Product List

        Parameters:
        - page_number
        - name
        description: optional search query param
        - size
        """

        page_number = int(request.GET.get("page_number", 1))
        size = int(request.GET.get("size", 30))
        name = request.GET.get("name", "")
        product_list_query = Product.objects.prefetch_related(
            "productimage_set"
        ).filter(is_deleted=False, name__icontains=name)

        paginated_list = Paginator(product_list_query, per_page=size)

        product_list = ProductSerializer(
            paginated_list.page(number=page_number).object_list, many=True
        )

        paginated_product_list = ProductListSerializer(
            data={
                "page_number": page_number,
                "total_items": paginated_list.count,
                "total_pages": paginated_list.num_pages,
                "has_next": paginated_list.page(number=page_number).has_next(),
                "has_prev": paginated_list.page(number=page_number).has_previous(),
                "page_size": size,
                "data": product_list.data,
            }
        )
        try:
            paginated_product_list.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Error {e}")
        return Response(
            {
                "data": paginated_product_list.data,
                "status_code": status.HTTP_200_OK,
                "message": "Product List",
                "success": "True",
            }
        )


class SearchProductByCategory(APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer

    def get(self, request: HttpRequest):
        """
        Retrieve Categorized Product List

        Parameters:
        - page_number
        - category_guid
        - size
        """

        page_number = int(request.GET.get("page_number", 1))
        size = int(request.GET.get("size", 30))
        category_guid = request.GET.get("category_guid", "")
        try:
            category = ProductCategory.objects.get(guid=category_guid)
        except ProductCategory.DoesNotExist:
            return Response(
                {
                    "data": [],
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "success": "True",
                    "message": "Invalid Category",
                }
            )
        product_list_query = (
            Product.objects.prefetch_related("productimage_set")
            .select_related("category")
            .filter(is_deleted=False, category__id=category.id)
        )

        paginated_list = Paginator(product_list_query, per_page=size)

        product_list = ProductSerializer(
            paginated_list.page(number=page_number).object_list, many=True
        )

        paginated_product_list = ProductListSerializer(
            data={
                "page_number": page_number,
                "total_items": paginated_list.count,
                "total_pages": paginated_list.num_pages,
                "has_next": paginated_list.page(number=page_number).has_next(),
                "has_prev": paginated_list.page(number=page_number).has_previous(),
                "page_size": size,
                "data": product_list.data,
            }
        )
        try:
            paginated_product_list.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Error {e}")
        return Response(
            {
                "data": paginated_product_list.data,
                "status_code": status.HTTP_200_OK,
                "message": "Product List",
                "success": "True",
            }
        )


class ProductDetails(APIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailsSerializer

    def get(self, request: HttpRequest):
        """
        Get Product Details

        Parameters:
            - product_guid
        """

        product_guid = request.GET.get("product_guid", None)
        # print(product_guid)
        try:
            product = (
                Product.objects.prefetch_related(
                    "productimage_set", "productspecifications_set"
                )
                .select_related("category")
                .get(guid=product_guid)
            )
        except Product.DoesNotExist:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "success": "True",
                    "message": "Invalid Product",
                    "data": {},
                }
            )

        return Response(
            {
                "data": ProductDetailsSerializer(product).data,
                "status_code": status.HTTP_200_OK,
                "success": "True",
            }
        )


#
# class ProductCompanyByCategoryAPIView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request, format=None):
#         category_id = request.query_params.get('category')
#         if not category_id:
#             return Response({
#                 "status_code": status.HTTP_400_BAD_REQUEST,
#                 "success": "False",
#                 "message": "Category parameter is required.",
#                 "data": {}
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         companies = ProductCompany.objects.filter(category_id=category_id)
#         if not companies.exists():
#             # Response format as provided in your sample
#             return Response({
#                 "status_code": status.HTTP_404_NOT_FOUND,
#                 "success": "True",
#                 "message": "No Company Found!",
#                 "data": {}
#             }, status=status.HTTP_404_NOT_FOUND)
#
#         serializer = ProductCompanySerializer(companies, many=True)
#         return Response({
#             "status_code": status.HTTP_200_OK,
#             "success": "True",
#             "message": "Companies retrieved successfully.",
#             "data": serializer.data,
#         }, status=status.HTTP_200_OK)



class ProductCompanyByCategoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        # Expect category_guid as the query parameter
        category_guid = request.query_params.get('category_guid')
        if not category_guid:
            return Response({
                "status_code": status.HTTP_400_BAD_REQUEST,
                "success": "False",
                "message": "Category GUID parameter is required.",
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the category by its GUID
            category = ProductCategory.objects.get(guid=category_guid)
        except ProductCategory.DoesNotExist:
            return Response({
                "status_code": status.HTTP_404_NOT_FOUND,
                "success": "True",
                "message": "Invalid Category GUID.",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        # Filter companies by the retrieved category
        companies = ProductCompany.objects.filter(category=category)
        if not companies.exists():
            return Response({
                "status_code": status.HTTP_404_NOT_FOUND,
                "success": "True",
                "message": "No Company Found!",
                "data": {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductCompanySerializer(companies, many=True)
        return Response({
            "status_code": status.HTTP_200_OK,
            "success": "True",
            "message": "Companies retrieved successfully.",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)



class SearchProductByCompany(APIView):
    permission_classes = []  # e.g., [AllowAny] if no auth is required
    serializer_class = ProductListSerializer

    def get(self, request: HttpRequest):
        """
        Retrieve Product List by Product Company

        Query Parameters:
            - page_number: int (default: 1)
            - product_company_guid: str (GUID for the ProductCompany)
            - size: int (default: 30)
        """
        page_number = int(request.GET.get("page_number", 1))
        size = int(request.GET.get("size", 30))
        product_company_guid = request.GET.get("product_company_guid", "")

        try:
            company = ProductCompany.objects.get(guid=product_company_guid)
        except ProductCompany.DoesNotExist:
            return Response({
                "data": [],
                "status_code": status.HTTP_404_NOT_FOUND,
                "success": "True",
                "message": "Invalid Product Company",
            }, status=status.HTTP_404_NOT_FOUND)

        product_list_query = (
            Product.objects.prefetch_related("productimage_set")
            .select_related("product_company")
            .filter(is_deleted=False, product_company__id=company.id)
        )

        paginated_list = Paginator(product_list_query, per_page=size)
        product_list = ProductSerializer(
            paginated_list.page(number=page_number).object_list, many=True
        )
        paginated_product_list = ProductListSerializer(data={
            "page_number": page_number,
            "total_items": paginated_list.count,
            "total_pages": paginated_list.num_pages,
            "has_next": paginated_list.page(number=page_number).has_next(),
            "has_prev": paginated_list.page(number=page_number).has_previous(),
            "page_size": size,
            "data": product_list.data,
        })

        try:
            paginated_product_list.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Error in paginating product list: {e}")

        return Response({
            "data": paginated_product_list.data,
            "status_code": status.HTTP_200_OK,
            "message": "Product List",
            "success": "True",
        }, status=status.HTTP_200_OK)
