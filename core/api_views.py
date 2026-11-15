from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Category, Service, Realization, Product, Order, OrderItem, ContactMessage, Application
from .serializers import (
    CategorySerializer,
    ServiceSerializer,
    RealizationSerializer,
    ApplicationSerializer,
    ProductSerializer,
    OrderSerializer,
    ContactMessageSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_home_data(request):
    """
    Endpoint agrégé pour la page d'accueil.
    Permet au frontend de charger tous les éléments phares en une seule requête HTTP.
    """
    featured_services = Service.objects.filter(is_active=True, is_featured=True)[:3]
    featured_realizations = Realization.objects.filter(is_active=True, is_featured=True)[:3]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    featured_applications = Application.objects.filter(is_active=True, is_featured=True)[:3]

    return Response({
        'featured_services': ServiceSerializer(featured_services, many=True).data,
        'featured_realizations': RealizationSerializer(featured_realizations, many=True).data,
        'featured_products': ProductSerializer(featured_products, many=True).data,
        'featured_applications': ApplicationSerializer(featured_applications, many=True).data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def api_categories_list(request):
    """
    Liste des catégories, avec filtre optionnel ?type=product|service|realization|application
    """
    cat_type = request.GET.get('type')
    queryset = Category.objects.all()
    if cat_type:
        queryset = queryset.filter(type=cat_type)
    serializer = CategorySerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_services_list(request):
    """
    Liste de tous les services actifs, avec filtre optionnel par catégorie.
    """
    queryset = Service.objects.filter(is_active=True)
    cat_slug = request.GET.get('category')
    if cat_slug:
        queryset = queryset.filter(category__slug=cat_slug)
    serializer = ServiceSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_service_detail(request, slug):
    """
    Détail d'un service par son slug ou son ID.
    """
    try:
        if slug.isdigit():
            service = Service.objects.get(id=int(slug), is_active=True)
        else:
            service = Service.objects.get(slug=slug, is_active=True)
        return Response(ServiceSerializer(service).data)
    except Service.DoesNotExist:
        return Response({'detail': 'Service introuvable.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_realisations_list(request):
    """
    Liste des réalisations actives.
    """
    queryset = Realization.objects.filter(is_active=True)
    cat_slug = request.GET.get('category')
    if cat_slug:
        queryset = queryset.filter(category__slug=cat_slug)
    serializer = RealizationSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_realisation_detail(request, slug):
    try:
        if slug.isdigit():
            realization = Realization.objects.get(id=int(slug), is_active=True)
        else:
            realization = Realization.objects.get(slug=slug, is_active=True)
        return Response(RealizationSerializer(realization).data)
    except Realization.DoesNotExist:
        return Response({'detail': 'Réalisation introuvable.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_applications_list(request):
    """
    Liste des applications avec filtres optionnels ?category=... et ?platform=...
    """
    queryset = Application.objects.filter(is_active=True)
    cat_slug = request.GET.get('category')
    platform = request.GET.get('platform')

    if cat_slug:
        queryset = queryset.filter(category__slug=cat_slug)
    if platform:
        queryset = queryset.filter(platform=platform)

    serializer = ApplicationSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_application_detail(request, slug):
    try:
        if slug.isdigit():
            app = Application.objects.get(id=int(slug), is_active=True)
        else:
            app = Application.objects.get(slug=slug, is_active=True)
        return Response(ApplicationSerializer(app).data)
    except Application.DoesNotExist:
        return Response({'detail': 'Application introuvable.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_products_list(request):
    """
    Catalogue des produits avec filtres :
    - ?category=slug
    - ?search=texte
    - ?sort=price_asc|price_desc|newest
    - ?featured=true
    """
    queryset = Product.objects.filter(is_active=True)
    cat_slug = request.GET.get('category')
    search = request.GET.get('search')
    sort = request.GET.get('sort')
    featured = request.GET.get('featured')

    if cat_slug:
        queryset = queryset.filter(category__slug=cat_slug)
    if search:
        queryset = queryset.filter(name__icontains=search)
    if featured == 'true':
        queryset = queryset.filter(is_featured=True)

    if sort == 'price_asc':
        queryset = queryset.order_by('price')
    elif sort == 'price_desc':
        queryset = queryset.order_by('-price')
    else:
        queryset = queryset.order_by('-created_at')

    serializer = ProductSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_product_detail_view(request, slug):
    try:
        if slug.isdigit():
            product = Product.objects.get(id=int(slug), is_active=True)
        else:
            product = Product.objects.get(slug=slug, is_active=True)
        return Response(ProductSerializer(product).data)
    except Product.DoesNotExist:
        return Response({'detail': 'Produit introuvable.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_checkout_view(request):
    """
    Passer une commande directement depuis le Frontend (Vercel).
    Accepte le panier dans le payload :
    {
      "customer_name": "...",
      "customer_email": "...",
      "customer_phone": "...",
      "delivery_address": "...",
      "city": "...",
      "notes": "...",
      "items": [
         { "product_id": 1, "quantity": 2 }
      ]
    }
    """
    data = request.data
    customer_name = data.get('customer_name')
    customer_email = data.get('customer_email', '')
    customer_phone = data.get('customer_phone')
    delivery_address = data.get('delivery_address')
    city = data.get('city', 'Abidjan')
    notes = data.get('notes', '')
    items_data = data.get('items', [])

    if not customer_name or not customer_phone or not delivery_address:
        return Response({
            'success': False,
            'message': 'Veuillez renseigner le nom, téléphone et adresse de livraison.'
        }, status=status.HTTP_400_BAD_REQUEST)

    if not items_data or len(items_data) == 0:
        return Response({
            'success': False,
            'message': 'Le panier est vide.'
        }, status=status.HTTP_400_BAD_REQUEST)

    total_amount = Decimal('0.00')
    validated_items = []

    for item in items_data:
        p_id = item.get('product_id') or item.get('id')
        qty = int(item.get('quantity', 1))
        if qty <= 0:
            continue
        try:
            prod = Product.objects.get(id=p_id, is_active=True)
            unit_price = prod.current_price
            subtotal = Decimal(str(unit_price)) * qty
            total_amount += subtotal
            validated_items.append({
                'product': prod,
                'product_name': prod.name,
                'price': unit_price,
                'quantity': qty,
                'subtotal': subtotal,
                'product_image_url': prod.image_url or '',
                'product_category': prod.category.name if prod.category else '',
                'product_short_description': prod.short_description or '',
                'product_specs': prod.specs or '',
                'product_badge': prod.badge or ''
            })
        except Product.DoesNotExist:
            continue

    if not validated_items:
        return Response({
            'success': False,
            'message': 'Aucun produit valide trouvé dans la commande.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Création de la commande
    order = Order.objects.create(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        delivery_address=delivery_address,
        city=city,
        total_amount=total_amount,
        notes=notes,
        status='pending'
    )

    for item_val in validated_items:
        OrderItem.objects.create(
            order=order,
            product=item_val['product'],
            product_name=item_val['product_name'],
            price=item_val['price'],
            quantity=item_val['quantity'],
            subtotal=item_val['subtotal'],
            product_image_url=item_val['product_image_url'],
            product_category=item_val['product_category'],
            product_short_description=item_val['product_short_description'],
            product_specs=item_val['product_specs'],
            product_badge=item_val['product_badge']
        )

    return Response({
        'success': True,
        'message': f'Commande {order.order_number} enregistrée avec succès !',
        'order_number': order.order_number,
        'total_amount': float(order.total_amount),
        'status': order.status,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def api_track_order_view(request):
    """
    Suivre une commande par son numéro ST-XXXXXXXX
    """
    order_number = request.data.get('order_number') if request.method == 'POST' else request.GET.get('order_number')
    if not order_number:
        return Response({
            'success': False,
            'message': 'Veuillez fournir un numéro de commande.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(order_number__iexact=order_number.strip())
        items = [{
            'product_name': it.product_name,
            'quantity': it.quantity,
            'price': float(it.price),
            'subtotal': float(it.subtotal),
            'image_url': it.product_image_url,
        } for it in order.items.all()]

        return Response({
            'success': True,
            'order_number': order.order_number,
            'customer_name': order.customer_name,
            'status': order.status,
            'status_display': order.get_status_display(),
            'total_amount': float(order.total_amount),
            'created_at': order.created_at.strftime('%d/%m/%Y à %H:%M'),
            'delivery_address': order.delivery_address,
            'city': order.city,
            'items': items
        })
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': f"Aucune commande trouvée avec la référence {order_number}."
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_contact_view(request):
    """
    Réception d'un message du formulaire de contact.
    """
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Votre message a bien été envoyé ! Notre équipe vous répondra rapidement.'
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_app_info_view(request):
    """
    Informations pour la Web App (PWA) et le téléchargement du fichier APK mobile.
    """
    import os
    from django.conf import settings
    apk_path = os.path.join(settings.BASE_DIR, 'media', 'apks', 'app-debug.apk')
    apk_exists = os.path.exists(apk_path)
    apk_size = round(os.path.getsize(apk_path) / (1024 * 1024), 1) if apk_exists else 0

    return Response({
        'name': 'STANTECH Enterprise',
        'short_name': 'STANTECH',
        'version': '1.0.0',
        'apk_available': apk_exists,
        'apk_size_mb': apk_size,
        'apk_download_url': '/telecharger-apk/' if apk_exists else None,
        'description': 'Application officielle STANTECH : boutique informatique, devis en ligne et suivi de commandes.'
    })

