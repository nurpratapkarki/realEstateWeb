from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    # Authentication Views
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserDetailView,
    # Property Views
    PropertyViewSet,
    # Customer Dashboard Views
    CustomerSavedPropertiesView,
    CustomerSavedPropertyCreateView,
    CustomerInquiriesView,
    CustomerInquiryCreateView,
    CustomerVisitsView,
    CustomerVisitCreateView,
    # Admin Dashboard Views
    AdminAnalyticsView,
    AdminUserManagementViewSet,
    # Additional Views
    PropertyTypeListView,
    OrganizationDetailView,
    ServiceListView,
    HeroSlideListView,
    JourneyStepListView,
    AboutUsDetailView,
    PropertyAlertListCreateView,
    PropertyAlertDetailView,
    TeamViewSet,
)

# Router for ViewSets
router = DefaultRouter()
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"admin/users", AdminUserManagementViewSet, basename="admin-users")

urlpatterns = [
    # Authentication URLs
    path("auth/register/", UserRegistrationView.as_view(), name="user-register"),
    path("auth/login/", UserLoginView.as_view(), name="user-login"),
    path("auth/logout/", UserLogoutView.as_view(), name="user-logout"),
    path("auth/user/", UserDetailView.as_view(), name="user-detail"),
    # Customer Dashboard URLs
    path(
        "customer/saved-properties/",
        CustomerSavedPropertiesView.as_view(),
        name="customer-saved-properties",
    ),
    path(
        "customer/saved-properties/create/",
        CustomerSavedPropertyCreateView.as_view(),
        name="customer-saved-properties-create",
    ),
    path(
        "customer/inquiries/",
        CustomerInquiriesView.as_view(),
        name="customer-inquiries",
    ),
    path(
        "customer/inquiries/create/",
        CustomerInquiryCreateView.as_view(),
        name="customer-inquiries-create",
    ),
    path("customer/visits/", CustomerVisitsView.as_view(), name="customer-visits"),
    path(
        "customer/visits/create/",
        CustomerVisitCreateView.as_view(),
        name="customer-visits-create",
    ),
    # Property Alerts URLs
    path(
        "customer/alerts/",
        PropertyAlertListCreateView.as_view(),
        name="property-alerts",
    ),
    path(
        "customer/alerts/<int:pk>/",
        PropertyAlertDetailView.as_view(),
        name="property-alert-detail",
    ),
    # Admin Dashboard URLs
    path("admin/analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
    # Content Management URLs
    path("property-types/", PropertyTypeListView.as_view(), name="property-types"),
    path("organization/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("services/", ServiceListView.as_view(), name="services"),
    path("hero-slides/", HeroSlideListView.as_view(), name="hero-slides"),
    path("journey-steps/", JourneyStepListView.as_view(), name="journey-steps"),
    path("about-us/", AboutUsDetailView.as_view(), name="about-us"),
    path("team/", TeamViewSet.as_view(), name="team"),
    # Include router URLs
    path("", include(router.urls)),
]
