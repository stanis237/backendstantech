from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import permissions, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action, api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Application, Category, ContactMessage, CustomInvoice, Order, Product, Realization, Service
from .serializers import (
    ApplicationSerializer,
    CategorySerializer,
    ContactMessageSerializer,
    CustomInvoiceSerializer,
    OrderSerializer,
    ProductSerializer,
    RealizationSerializer,
    ServiceSerializer,
)
from . import admin_views


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
    today = timezone.localdate()
    months = []
    year, month = today.year, today.month
    for _ in range(6):
        months.append((year, month))
        month -= 1
        if month == 0:
            year -= 1
            month = 12
    months.reverse()

    first_year, first_month = months[0]
    monthly_orders = (
        Order.objects.filter(
            status__in=['confirmed', 'shipped', 'delivered'],
            created_at__year__gte=first_year,
        )
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(revenue=Sum('total_amount'), count=Count('id'))
    )
    monthly_lookup = {
        (row['month'].year, row['month'].month): row for row in monthly_orders
    }
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    sales = []
    for year, month in months:
        row = monthly_lookup.get((year, month), {})
        sales.append({
            'label': f'{month_names[month - 1]} {year}',
            'revenue': row.get('revenue') or 0,
            'orders': row.get('count', 0),
        })

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
        'recent_orders': OrderSerializer(Order.objects.all()[:5], many=True).data,
        'recent_messages': ContactMessageSerializer(ContactMessage.objects.filter(is_read=False)[:5], many=True).data,
        'low_stock_products': ProductSerializer(Product.objects.filter(is_active=True, stock__lte=3), many=True).data,
        'sales': sales,
    })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_upload(request):
    uploaded_file = request.FILES.get('file')
    if uploaded_file is None:
        return Response({'detail': 'Aucun fichier reçu.'}, status=status.HTTP_400_BAD_REQUEST)

    kind = request.data.get('kind', 'image')
    allowed_extensions = {
        'image': {'.jpg', '.jpeg', '.png', '.webp', '.gif'},
        'apk': {'.apk'},
    }
    if kind not in allowed_extensions:
        return Response({'detail': 'Type de fichier non autorisé.'}, status=status.HTTP_400_BAD_REQUEST)
    extension = Path(uploaded_file.name).suffix.lower()
    if extension not in allowed_extensions[kind]:
        return Response({'detail': 'Extension de fichier non autorisée.'}, status=status.HTTP_400_BAD_REQUEST)

    max_size = 100 * 1024 * 1024 if kind == 'apk' else 12 * 1024 * 1024
    if uploaded_file.size > max_size:
        return Response({'detail': 'Fichier trop volumineux.'}, status=status.HTTP_400_BAD_REQUEST)

    folder = 'apks' if kind == 'apk' else 'images/admin'
    stored_name = default_storage.save(f'{folder}/{uuid4().hex}{extension}', uploaded_file)
    return Response({'url': request.build_absolute_uri(default_storage.url(stored_name))})


def _run_session_export(request, export_view, **kwargs):
    """Reuse the established export implementation with the authenticated Django request."""
    return export_view(request._request, **kwargs)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_export_orders_csv(request):
    return _run_session_export(request, admin_views.dashboard_export_orders)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_export_orders_excel(request):
    return _run_session_export(request, admin_views.dashboard_export_orders_excel)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_export_orders_pdf(request):
    return _run_session_export(request, admin_views.dashboard_export_orders_pdf)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_export_order_invoice_pdf(request, pk):
    return _run_session_export(request, admin_views.dashboard_export_order_single_pdf, pk=pk)


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

    def get_queryset(self):
        queryset = super().get_queryset()
        category_type = self.request.query_params.get('type')
        if category_type:
            queryset = queryset.filter(type=category_type)
        return queryset


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


class CustomInvoiceAdminViewSet(AdminModelViewSet):
    queryset = CustomInvoice.objects.prefetch_related('items').all()
    serializer_class = CustomInvoiceSerializer
    search_fields = ['invoice_number', 'client_name', 'client_email']


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([SuperuserOnly])
def admin_invoice_pdf(request, pk):
    invoice = get_object_or_404(CustomInvoice.objects.prefetch_related('items'), pk=pk)
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('InvoiceTitle', parent=styles['Title'], textColor=colors.HexColor('#059669'), alignment=0)
    body_style = ParagraphStyle('InvoiceBody', parent=styles['BodyText'], fontSize=9, leading=13)
    story = [
        Paragraph('STANTECH CONSULTING', title_style),
        Paragraph(f'{escape(invoice.get_invoice_type_display())} — {escape(invoice.invoice_number)}', styles['Heading2']),
        Spacer(1, 0.4 * cm),
        Paragraph(f'<b>Client :</b> {escape(invoice.client_name)}', body_style),
        Paragraph(f'<b>Email :</b> {escape(invoice.client_email or "—")} &nbsp;&nbsp; <b>Téléphone :</b> {escape(invoice.client_phone or "—")}', body_style),
        Paragraph(f'<b>Adresse :</b> {escape(invoice.client_address or "—")}, {escape(invoice.city)}', body_style),
        Paragraph(f'<b>Émise le :</b> {invoice.issue_date:%d/%m/%Y} &nbsp;&nbsp; <b>Échéance :</b> {invoice.due_date:%d/%m/%Y}' if invoice.due_date else f'<b>Émise le :</b> {invoice.issue_date:%d/%m/%Y}', body_style),
        Spacer(1, 0.5 * cm),
    ]
    table_data = [['Désignation', 'Qté', 'Prix unitaire', 'Total HT']]
    for item in invoice.items.all():
        table_data.append([
            Paragraph(escape(item.description), body_style),
            str(item.quantity),
            f'{item.unit_price:,.0f} FCFA',
            f'{item.subtotal:,.0f} FCFA',
        ])
    table = Table(table_data, colWidths=[8.5 * cm, 1.5 * cm, 3.2 * cm, 3.2 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.extend([table, Spacer(1, 0.5 * cm)])
    summary = [
        ['Sous-total HT', f'{invoice.subtotal:,.0f} FCFA'],
        [f'TVA ({invoice.tax_rate} %)', f'{invoice.tax_amount:,.0f} FCFA'],
        ['Total TTC', f'{invoice.total_amount:,.0f} FCFA'],
    ]
    totals = Table(summary, colWidths=[12.5 * cm, 3.9 * cm], hAlign='RIGHT')
    totals.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#059669')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#059669')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(totals)
    if invoice.notes:
        story.extend([Spacer(1, 0.5 * cm), Paragraph('<b>Notes</b>', styles['Heading4']), Paragraph(escape(invoice.notes).replace('\n', '<br/>'), body_style)])
    document.build(story)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
    return response
