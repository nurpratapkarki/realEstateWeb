from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication Views
    UserRegistrationView, UserLoginView, UserLogoutView, UserDetailView,
    
    # Property Views
    PropertyViewSet,
    
    # Customer Dashboard Views
    CustomerSavedPropertiesView, CustomerSavedPropertyCreateView,
    CustomerInquiriesView, CustomerInquiryCreateView,
    CustomerVisitsView, CustomerVisitCreateView,
    
    # Admin Dashboard Views
    AdminAnalyticsView, AdminUserManagementViewSet,
    
    # Additional Views
    PropertyTypeListView, OrganizationDetailView, ServiceListView,
    HeroSlideListView, JourneyStepListView, AboutUsDetailView, AgentListView,
    PropertyAlertListCreateView, PropertyAlertDetailView
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'admin/users', AdminUserManagementViewSet, basename='admin-users')

urlpatterns = [
    # Authentication URLs
    path('api/auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('api/auth/login/', UserLoginView.as_view(), name='user-login'),
    path('api/auth/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('api/auth/user/', UserDetailView.as_view(), name='user-detail'),
    
    # Customer Dashboard URLs
    path('api/customer/saved-properties/', CustomerSavedPropertiesView.as_view(), name='customer-saved-properties'),
    path('api/customer/saved-properties/create/', CustomerSavedPropertyCreateView.as_view(), name='customer-saved-properties-create'),
    path('api/customer/inquiries/', CustomerInquiriesView.as_view(), name='customer-inquiries'),
    path('api/customer/inquiries/create/', CustomerInquiryCreateView.as_view(), name='customer-inquiries-create'),
    path('api/customer/visits/', CustomerVisitsView.as_view(), name='customer-visits'),
    path('api/customer/visits/create/', CustomerVisitCreateView.as_view(), name='customer-visits-create'),
    
    # Property Alerts URLs
    path('api/customer/alerts/', PropertyAlertListCreateView.as_view(), name='property-alerts'),
    path('api/customer/alerts/<int:pk>/', PropertyAlertDetailView.as_view(), name='property-alert-detail'),
    
    # Admin Dashboard URLs
    path('api/admin/analytics/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    
    # Content Management URLs
    path('api/property-types/', PropertyTypeListView.as_view(), name='property-types'),
    path('api/organization/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('api/services/', ServiceListView.as_view(), name='services'),
    path('api/hero-slides/', HeroSlideListView.as_view(), name='hero-slides'),
    path('api/journey-steps/', JourneyStepListView.as_view(), name='journey-steps'),
    path('api/about-us/', AboutUsDetailView.as_view(), name='about-us'),
    path('api/about/', AboutUsDetailView.as_view(), name='about'),
    path('api/team/', AgentListView.as_view(), name='team'),
    path('api/agents/', AgentListView.as_view(), name='agents'),
    
    # Include router URLs
    path('api/', include(router.urls)),
]