from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views
from . import api_views
from . import admin_api_views

admin_api_router = DefaultRouter()
admin_api_router.register('products', admin_api_views.ProductAdminViewSet, basename='admin-products')
admin_api_router.register('services', admin_api_views.ServiceAdminViewSet, basename='admin-services')
admin_api_router.register('realisations', admin_api_views.RealizationAdminViewSet, basename='admin-realisations')
admin_api_router.register('applications', admin_api_views.ApplicationAdminViewSet, basename='admin-applications')
admin_api_router.register('categories', admin_api_views.CategoryAdminViewSet, basename='admin-categories')
admin_api_router.register('orders', admin_api_views.OrderAdminViewSet, basename='admin-orders')
admin_api_router.register('messages', admin_api_views.ContactMessageAdminViewSet, basename='admin-messages')

urlpatterns = [
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
    path('api/admin/', include(admin_api_router.urls)),

    # Téléchargement direct APK Android
    path('telecharger-apk/', views.download_apk_view, name='download_apk'),

    # Endpoints cart conservés pour compatibilité
    path('api/cart/add/', views.api_cart_add, name='api_cart_add'),
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('api/product/<int:product_id>/', views.api_product_detail, name='api_product_detail'),
]

