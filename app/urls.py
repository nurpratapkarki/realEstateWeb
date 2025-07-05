from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'organizations', views.OrganizationViewSet)
router.register(r'about-us', views.AboutUsViewSet)
router.register(r'achievements', views.AchievementsViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'journey', views.JourneyViewSet)
router.register(r'hero-sections', views.HeroSectionViewSet)
router.register(r'property-types', views.PropertyTypeViewSet)
router.register(r'properties', views.PropertyViewSet)
router.register(r'agents', views.AgentViewSet)
router.register(r'contacts', views.ContactViewSet)

# Define URL patterns
urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('auth/login/', views.UserLoginView.as_view(), name='user-login'),
    path('auth/logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # Dashboard URLs
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Search URLs
    path('search/', views.GlobalSearchView.as_view(), name='global-search'),
    
    # Public API URLs for Frontend
    path('public/home/', views.home_page_data, name='home-page-data'),
    path('public/about/', views.about_page_data, name='about-page-data'),
    path('public/property-filters/', views.property_filters, name='property-filters'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# URL patterns for main project urls.py
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('your_app.urls')),  # Replace 'your_app' with your actual app name
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""