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
    CustomerMessagesView, CustomerMessageCreateView,
    CustomerDocumentsView, CustomerDocumentDownloadView,

    # Admin Dashboard Views
    AdminAnalyticsView, AdminUserManagementViewSet,
    AdminServiceManagementViewSet, AdminHeroSlideManagementViewSet,
    AdminJourneyStepManagementViewSet, AdminAgentManagementViewSet,
    AdminPropertyTypeManagementViewSet, AdminOrganizationManagementView,
    AdminAboutUsManagementViewSet, AdminContactsView, AdminAchievementsView,
    AdminGalleryManagementViewSet, AdminNewsManagementViewSet, AdminNewsCategoryManagementViewSet,
    AdminTeamManagementViewSet, AdminContactManagementViewSet,
    AdminTeamManagementViewSet,

    # Additional Views
    PropertyTypeListView, OrganizationDetailView, ServiceListView,
    HeroSlideListView, JourneyStepListView, AboutUsDetailView, AgentListView,
    PropertyAlertListCreateView, PropertyAlertDetailView,

    # Gallery and News Views
    GalleryListView, GalleryDetailView, NewsCategoryListView, NewsListView, NewsDetailView,

    # Team Views
    TeamListView,

    # Contact Views
    ContactCreateView
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'admin/users', AdminUserManagementViewSet, basename='admin-users')
router.register(r'admin/services', AdminServiceManagementViewSet, basename='admin-services')
router.register(r'admin/hero-slides', AdminHeroSlideManagementViewSet, basename='admin-hero-slides')
router.register(r'admin/journey-steps', AdminJourneyStepManagementViewSet, basename='admin-journey-steps')
router.register(r'admin/agents', AdminAgentManagementViewSet, basename='admin-agents')
router.register(r'admin/property-types', AdminPropertyTypeManagementViewSet, basename='admin-property-types')
router.register(r'admin/about-us', AdminAboutUsManagementViewSet, basename='admin-about-us')
router.register(r'admin/gallery', AdminGalleryManagementViewSet, basename='admin-gallery')
router.register(r'admin/news', AdminNewsManagementViewSet, basename='admin-news')
router.register(r'admin/news-categories', AdminNewsCategoryManagementViewSet, basename='admin-news-categories')
router.register(r'admin/team', AdminTeamManagementViewSet, basename='admin-team')
router.register(r'admin/contacts', AdminContactManagementViewSet, basename='admin-contacts')

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
    path('api/customer/messages/', CustomerMessagesView.as_view(), name='customer-messages'),
    path('api/customer/messages/create/', CustomerMessageCreateView.as_view(), name='customer-messages-create'),
    path('api/customer/documents/', CustomerDocumentsView.as_view(), name='customer-documents'),
    path('api/customer/documents/<int:pk>/download/', CustomerDocumentDownloadView.as_view(), name='customer-document-download'),

    # Property Alerts URLs
    path('api/customer/alerts/', PropertyAlertListCreateView.as_view(), name='property-alerts'),
    path('api/customer/alerts/<int:pk>/', PropertyAlertDetailView.as_view(), name='property-alert-detail'),
    
    # Admin Dashboard URLs
    path('api/admin/analytics/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('api/admin/organization/', AdminOrganizationManagementView.as_view(), name='admin-organization'),
    path('api/admin/contacts/', AdminContactsView.as_view(), name='admin-contacts'),
    path('api/admin/achievements/', AdminAchievementsView.as_view(), name='admin-achievements'),
    
    # Content Management URLs
    path('api/property-types/', PropertyTypeListView.as_view(), name='property-types'),
    path('api/organization/', OrganizationDetailView.as_view(), name='organization-detail'),
    path('api/services/', ServiceListView.as_view(), name='services'),
    path('api/hero-slides/', HeroSlideListView.as_view(), name='hero-slides'),
    path('api/journey-steps/', JourneyStepListView.as_view(), name='journey-steps'),
    path('api/about-us/', AboutUsDetailView.as_view(), name='about-us'),
    path('api/about/', AboutUsDetailView.as_view(), name='about'),
    path('api/team/', TeamListView.as_view(), name='team'),
    path('api/agents/', AgentListView.as_view(), name='agents'),

    # Gallery URLs
    path('api/gallery/', GalleryListView.as_view(), name='gallery-list'),
    path('api/gallery/<int:pk>/', GalleryDetailView.as_view(), name='gallery-detail'),

    # News URLs
    path('api/news/categories/', NewsCategoryListView.as_view(), name='news-categories'),
    path('api/news/', NewsListView.as_view(), name='news-list'),
    path('api/news/<slug:slug>/', NewsDetailView.as_view(), name='news-detail'),

    # Contact URLs
    path('api/contact/', ContactCreateView.as_view(), name='contact-create'),

    # Include router URLs
    path('api/', include(router.urls)),
]