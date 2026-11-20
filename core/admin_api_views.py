from django.contrib.auth import authenticate
from django.db.models import Sum
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Application, Category, ContactMessage, Order, Product, Realization, Service
from .serializers import (
    ApplicationSerializer,
    CategorySerializer,
    ContactMessageSerializer,
    OrderSerializer,
    ProductSerializer,
    RealizationSerializer,
    ServiceSerializer,
)


class SuperuserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class AdminModelViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [SuperuserOnly]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_login(request):
    username = str(request.data.get('username', '')).strip()
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)

    if not user or not user.is_active or not user.is_superuser:
        return Response(
            {'detail': 'Identifiants invalides ou accès réservé aux super-administrateurs.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'username': user.get_username()})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_logout(request):
    if isinstance(request.auth, Token):
        request.auth.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_dashboard(request):
    return Response({
        'products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True).count(),
        'services': Service.objects.count(),
        'realisations': Realization.objects.count(),
        'applications': Application.objects.count(),
        'orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'revenue': Order.objects.filter(status__in=['confirmed', 'shipped', 'delivered']).aggregate(total=Sum('total_amount'))['total'] or 0,
    })


class ProductAdminViewSet(AdminModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    search_fields = ['name', 'short_description']


class ServiceAdminViewSet(AdminModelViewSet):
    queryset = Service.objects.select_related('category').all()
    serializer_class = ServiceSerializer
    search_fields = ['title', 'short_description']


class RealizationAdminViewSet(AdminModelViewSet):
    queryset = Realization.objects.select_related('category').all()
    serializer_class = RealizationSerializer
    search_fields = ['title', 'client_name', 'short_description']


class ApplicationAdminViewSet(AdminModelViewSet):
    queryset = Application.objects.select_related('category').all()
    serializer_class = ApplicationSerializer
    search_fields = ['title', 'short_description']


class CategoryAdminViewSet(AdminModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name']


class OrderAdminViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.prefetch_related('items').all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [SuperuserOnly]
    search_fields = ['order_number', 'customer_name', 'customer_phone']

    @action(detail=True, methods=['patch'])
    def status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = {choice[0] for choice in Order.STATUS_CHOICES}
        if new_status not in valid_statuses:
            return Response({'detail': 'Statut de commande invalide.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save(update_fields=['status'])
        return Response(OrderSerializer(order).data)


class ContactMessageAdminViewSet(AdminModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    search_fields = ['name', 'email', 'subject']
