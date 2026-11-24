from django.conf import settings
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views
from . import admin_api_views
from . import admin_views

admin_api_router = DefaultRouter()
admin_api_router.register('products', admin_api_views.ProductAdminViewSet, basename='admin-products')
admin_api_router.register('services', admin_api_views.ServiceAdminViewSet, basename='admin-services')
admin_api_router.register('realisations', admin_api_views.RealizationAdminViewSet, basename='admin-realisations')
admin_api_router.register('applications', admin_api_views.ApplicationAdminViewSet, basename='admin-applications')
admin_api_router.register('categories', admin_api_views.CategoryAdminViewSet, basename='admin-categories')
admin_api_router.register('orders', admin_api_views.OrderAdminViewSet, basename='admin-orders')
admin_api_router.register('messages', admin_api_views.ContactMessageAdminViewSet, basename='admin-messages')
admin_api_router.register('invoices', admin_api_views.CustomInvoiceAdminViewSet, basename='admin-invoices')

urlpatterns = [
    # Retour vers le site statique hébergé par Vercel
    path('', RedirectView.as_view(url=settings.FRONTEND_URL, permanent=False), name='index'),

    # API et téléchargement utilisés par le frontend statique Vercel
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('telecharger-apk/', views.download_apk_view, name='download_apk'),

    # REST API publique pour le frontend découpé
    path('api/home/', api_views.api_home_data, name='api_home_data'),
    path('api/categories/', api_views.api_categories_list, name='api_categories_list'),
    path('api/services/', api_views.api_services_list, name='api_services_list'),
    path('api/services/<slug:slug>/', api_views.api_service_detail, name='api_service_detail'),
    path('api/realisations/', api_views.api_realisations_list, name='api_realisations_list'),
    path('api/realisations/<slug:slug>/', api_views.api_realisation_detail, name='api_realisation_detail'),
    path('api/applications/', api_views.api_applications_list, name='api_applications_list'),
    path('api/applications/<slug:slug>/', api_views.api_application_detail, name='api_application_detail'),
    path('api/products/', api_views.api_products_list, name='api_products_list'),
    path('api/products/<slug:slug>/', api_views.api_product_detail_view, name='api_product_detail_view'),
    path('api/checkout/', api_views.api_checkout_view, name='api_checkout_view'),
    path('api/track-order/', api_views.api_track_order_view, name='api_track_order_view'),
    path('api/contact/', api_views.api_contact_view, name='api_contact_view'),
    path('api/app-info/', api_views.api_app_info_view, name='api_app_info'),

    # API d'administration protégée pour frontend/admin.html
    path('api/admin/login/', admin_api_views.admin_login, name='api_admin_login'),
    path('api/admin/logout/', admin_api_views.admin_logout, name='api_admin_logout'),
    path('api/admin/dashboard/', admin_api_views.admin_dashboard, name='api_admin_dashboard'),
    path('api/admin/upload/', admin_api_views.admin_upload, name='api_admin_upload'),
    path('api/admin/invoices/<int:pk>/pdf/', admin_api_views.admin_invoice_pdf, name='api_admin_invoice_pdf'),
    path('api/admin/exports/orders.csv', admin_api_views.admin_export_orders_csv, name='api_admin_export_orders_csv'),
    path('api/admin/exports/orders.xlsx', admin_api_views.admin_export_orders_excel, name='api_admin_export_orders_excel'),
    path('api/admin/exports/orders.pdf', admin_api_views.admin_export_orders_pdf, name='api_admin_export_orders_pdf'),
    path('api/admin/exports/orders/<int:pk>.pdf', admin_api_views.admin_export_order_invoice_pdf, name='api_admin_export_order_invoice_pdf'),
    path('api/admin/', include(admin_api_router.urls)),

    # Endpoints cart conservés pour compatibilité
    path('api/cart/add/', views.api_cart_add, name='api_cart_add'),
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('api/product/<int:product_id>/', views.api_product_detail, name='api_product_detail'),

    # Dashboard complet Django : templates, formulaires, commandes et factures
    path('dashboard/login/', admin_views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', admin_views.dashboard_logout, name='dashboard_logout'),
    path('dashboard/', admin_views.dashboard_home, name='dashboard_home'),
    path('dashboard/produits/', admin_views.dashboard_products, name='dashboard_products'),
    path('dashboard/produits/ajouter/', admin_views.dashboard_product_add, name='dashboard_product_add'),
    path('dashboard/produits/<int:pk>/modifier/', admin_views.dashboard_product_edit, name='dashboard_product_edit'),
    path('dashboard/produits/<int:pk>/supprimer/', admin_views.dashboard_product_delete, name='dashboard_product_delete'),
    path('dashboard/services/', admin_views.dashboard_services, name='dashboard_services'),
    path('dashboard/services/ajouter/', admin_views.dashboard_service_add, name='dashboard_service_add'),
    path('dashboard/services/<int:pk>/modifier/', admin_views.dashboard_service_edit, name='dashboard_service_edit'),
    path('dashboard/services/<int:pk>/supprimer/', admin_views.dashboard_service_delete, name='dashboard_service_delete'),
    path('dashboard/realisations/', admin_views.dashboard_realisations, name='dashboard_realisations'),
    path('dashboard/realisations/ajouter/', admin_views.dashboard_realisation_add, name='dashboard_realisation_add'),
    path('dashboard/realisations/<int:pk>/modifier/', admin_views.dashboard_realisation_edit, name='dashboard_realisation_edit'),
    path('dashboard/realisations/<int:pk>/supprimer/', admin_views.dashboard_realisation_delete, name='dashboard_realisation_delete'),
    path('dashboard/applications/', admin_views.dashboard_applications, name='dashboard_applications'),
    path('dashboard/applications/ajouter/', admin_views.dashboard_application_add, name='dashboard_application_add'),
    path('dashboard/applications/<int:pk>/modifier/', admin_views.dashboard_application_edit, name='dashboard_application_edit'),
    path('dashboard/applications/<int:pk>/supprimer/', admin_views.dashboard_application_delete, name='dashboard_application_delete'),
    path('dashboard/commandes/', admin_views.dashboard_orders, name='dashboard_orders'),
    path('dashboard/commandes/export/', admin_views.dashboard_export_orders, name='dashboard_export_orders'),
    path('dashboard/commandes/export/excel/', admin_views.dashboard_export_orders_excel, name='dashboard_export_orders_excel'),
    path('dashboard/commandes/export/pdf/', admin_views.dashboard_export_orders_pdf, name='dashboard_export_orders_pdf'),
    path('dashboard/commandes/<int:pk>/', admin_views.dashboard_order_detail, name='dashboard_order_detail'),
    path('dashboard/commandes/<int:pk>/pdf/', admin_views.dashboard_export_order_single_pdf, name='dashboard_export_order_single_pdf'),
    path('dashboard/messages/', admin_views.dashboard_messages, name='dashboard_messages'),
    path('dashboard/messages/<int:pk>/', admin_views.dashboard_message_read, name='dashboard_message_read'),
    path('dashboard/messages/<int:pk>/supprimer/', admin_views.dashboard_message_delete, name='dashboard_message_delete'),

]

