from django.contrib.auth import login, logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status, generics, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    User, Organization, PropertyType, Property, PropertyImage, Agent,
    PropertyInquiry, PropertyVisit, SavedProperty, Service, HeroSlide,
    JourneyStep, AboutUs, PropertyAlert, Gallery, GalleryImage,
    NewsCategory, News, Team, Contact, CustomerMessage, CustomerDocument
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    PropertySerializer, PropertyDetailSerializer, PropertyCreateUpdateSerializer,
    PropertyImageSerializer, SavedPropertySerializer, SavedPropertyCreateSerializer,
    PropertyInquirySerializer, PropertyInquiryCreateSerializer,
    PropertyVisitSerializer, PropertyVisitCreateSerializer,
    AdminAnalyticsSerializer, UserManagementSerializer, UserCreateSerializer, UserUpdateSerializer,
    PropertyTypeSerializer, OrganizationSerializer, ServiceSerializer,
    AgentSerializer, HeroSlideSerializer, JourneyStepSerializer, AboutUsSerializer,
    PropertyAlertSerializer, PropertyAlertCreateSerializer,
    GallerySerializer, GalleryImageSerializer, NewsCategorySerializer, NewsSerializer,
    TeamSerializer, ContactSerializer, ContactCreateSerializer,
    CustomerMessageSerializer, CustomerMessageCreateSerializer, CustomerDocumentSerializer
)

User = get_user_model()


# Custom Permission Classes
class IsAdminRole(BasePermission):
    """
    Custom permission to check if user has admin role.
    Checks both the custom role field and Django's is_staff/is_superuser.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check custom role field
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Fallback to Django's built-in admin checks
        return request.user.is_staff or request.user.is_superuser


# Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            logout(request)
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'message': 'User was not logged in'}, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# Property Views
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateUpdateSerializer
        return PropertySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminRole]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]



    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True).select_related('property_type').prefetch_related('images')
        
        # Filter parameters
        property_type = self.request.query_params.get('property_type')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        location = self.request.query_params.get('location')
        bedrooms = self.request.query_params.get('bedrooms')
        bathrooms = self.request.query_params.get('bathrooms')
        is_featured = self.request.query_params.get('is_featured')

        if property_type:
            queryset = queryset.filter(property_type_id=property_type)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if bedrooms:
            queryset = queryset.filter(bedrooms=bedrooms)
        if bathrooms:
            queryset = queryset.filter(bathrooms=bathrooms)
        if is_featured:
            queryset = queryset.filter(is_featured=True)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured properties"""
        featured_properties = self.get_queryset().filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured_properties, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent properties"""
        recent_properties = self.get_queryset()[:10]
        serializer = self.get_serializer(recent_properties, many=True)
        return Response(serializer.data)


# Customer Dashboard Views
class CustomerSavedPropertiesView(generics.ListAPIView):
    serializer_class = SavedPropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedProperty.objects.filter(customer=self.request.user).select_related('property')


class CustomerSavedPropertyCreateView(generics.CreateAPIView):
    serializer_class = SavedPropertyCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if 'unique constraint' in str(e).lower():
                return Response({'message': 'Property already saved'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Error saving property'}, status=status.HTTP_400_BAD_REQUEST)


class CustomerSavedPropertyDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        property_id = self.kwargs['property_id']
        try:
            return SavedProperty.objects.get(
                customer=self.request.user,
                property_id=property_id
            )
        except SavedProperty.DoesNotExist:
            from django.http import Http404
            raise Http404("Saved property not found")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Property removed from saved list'}, status=status.HTTP_200_OK)


class CustomerInquiriesView(generics.ListAPIView):
    serializer_class = PropertyInquirySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyInquiry.objects.filter(customer=self.request.user).select_related('property', 'agent').order_by('-created_at')


class CustomerInquiryCreateView(generics.CreateAPIView):
    serializer_class = PropertyInquiryCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CustomerVisitsView(generics.ListAPIView):
    serializer_class = PropertyVisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyVisit.objects.filter(customer=self.request.user).select_related('property', 'agent').order_by('-scheduled_date')


class CustomerVisitCreateView(generics.CreateAPIView):
    serializer_class = PropertyVisitCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CustomerMessagesView(generics.ListAPIView):
    serializer_class = CustomerMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerMessage.objects.filter(customer=self.request.user).select_related('agent', 'property').order_by('-created_at')


class CustomerMessageCreateView(generics.CreateAPIView):
    serializer_class = CustomerMessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CustomerDocumentsView(generics.ListAPIView):
    serializer_class = CustomerDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerDocument.objects.filter(customer=self.request.user, is_active=True).select_related('property').order_by('-created_at')


class CustomerDocumentDownloadView(generics.RetrieveAPIView):
    serializer_class = CustomerDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomerDocument.objects.filter(customer=self.request.user, is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment download count
        instance.download_count += 1
        instance.save()

        # Return file download response
        if instance.file:
            from django.http import HttpResponse
            response = HttpResponse(instance.file.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{instance.title}"'
            return response
        else:
            return Response({'message': 'File not found'}, status=status.HTTP_404_NOT_FOUND)


# Admin Dashboard Views
class AdminAnalyticsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        # Calculate analytics data
        total_properties = Property.objects.count()
        active_properties = Property.objects.filter(is_active=True).count()
        total_users = User.objects.count()
        total_agents = Agent.objects.count()
        total_inquiries = PropertyInquiry.objects.count()
        pending_inquiries = PropertyInquiry.objects.filter(status='pending').count()
        
        # Get scheduled visits for next 7 days
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        scheduled_visits = PropertyVisit.objects.filter(
            scheduled_date__range=[today, next_week],
            status='scheduled'
        ).count()
        
        # Get recent properties and inquiries
        recent_properties = Property.objects.filter(is_active=True).order_by('-created_at')[:5]
        recent_inquiries = PropertyInquiry.objects.select_related('customer', 'property').order_by('-created_at')[:5]
        
        analytics_data = {
            'total_properties': total_properties,
            'active_properties': active_properties,
            'total_users': total_users,
            'total_agents': total_agents,
            'total_inquiries': total_inquiries,
            'pending_inquiries': pending_inquiries,
            'scheduled_visits': scheduled_visits,
            'recent_properties': PropertySerializer(recent_properties, many=True).data,
            'recent_inquiries': PropertyInquirySerializer(recent_inquiries, many=True).data,
        }
        
        return Response(analytics_data)


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAdminRole]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserManagementSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter parameters
        is_active = self.request.query_params.get('is_active')
        is_staff = self.request.query_params.get('is_staff')
        search = self.request.query_params.get('search')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset.order_by('-date_joined')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': 'User updated successfully'
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Don't allow deletion of superuser accounts
        if instance.is_superuser:
            return Response(
                {'message': 'Cannot delete superuser account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # Don't allow users to delete themselves
        if instance == request.user:
            return Response(
                {'message': 'Cannot delete your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_destroy(instance)
        return Response(
            {'message': 'User deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle user active status"""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'message': 'Cannot deactivate your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = not user.is_active
        user.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully'
        })

    @action(detail=True, methods=['post'])
    def toggle_staff(self, request, pk=None):
        """Toggle user staff status"""
        user = self.get_object()
        if user == request.user:
            return Response(
                {'message': 'Cannot modify your own staff status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_staff = not user.is_staff
        user.save()
        return Response({
            'user': UserManagementSerializer(user).data,
            'message': f'User staff status {"granted" if user.is_staff else "revoked"} successfully'
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        recent_users = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'recent_users': recent_users,
            'inactive_users': total_users - active_users,
        })


# Additional Views for better API functionality
class PropertyTypeListView(generics.ListAPIView):
    """Get all property types for filtering"""
    queryset = PropertyType.objects.filter(is_active=True)
    serializer_class = PropertyTypeSerializer
    permission_classes = [permissions.AllowAny]


class OrganizationDetailView(generics.RetrieveAPIView):
    """Get organization details for about page"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        return Organization.objects.first()


class ServiceListView(generics.ListAPIView):
    """Get all active services"""
    queryset = Service.objects.filter(is_active=True).order_by('order')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.AllowAny]


class HeroSlideListView(generics.ListAPIView):
    """Get all active hero slides"""
    queryset = HeroSlide.objects.filter(is_active=True).order_by('order')
    serializer_class = HeroSlideSerializer
    permission_classes = [permissions.AllowAny]


class JourneyStepListView(generics.ListAPIView):
    """Get all active journey steps"""
    queryset = JourneyStep.objects.filter(is_active=True).order_by('order')
    serializer_class = JourneyStepSerializer
    permission_classes = [permissions.AllowAny]


class AgentListView(generics.ListAPIView):
    """Get all active agents (team page)"""
    queryset = Agent.objects.filter(is_active=True)
    serializer_class = AgentSerializer
    permission_classes = [permissions.AllowAny]


class AboutUsDetailView(generics.RetrieveAPIView):
    """Get about us information"""
    queryset = AboutUs.objects.filter(is_active=True)
    serializer_class = AboutUsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_object(self):
        return AboutUs.objects.filter(is_active=True).first()


# Admin Management Views for CRUD operations
class AdminServiceManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for services"""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminUser]


class AdminHeroSlideManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for hero slides"""
    queryset = HeroSlide.objects.all()
    serializer_class = HeroSlideSerializer
    permission_classes = [IsAdminUser]


class AdminJourneyStepManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for journey steps"""
    queryset = JourneyStep.objects.all()
    serializer_class = JourneyStepSerializer
    permission_classes = [IsAdminUser]


class AdminAgentManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for agents"""
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = [IsAdminUser]


class AdminPropertyTypeManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for property types"""
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeSerializer
    permission_classes = [IsAdminUser]


class AdminOrganizationManagementView(generics.RetrieveUpdateAPIView):
    """Admin management for organization settings"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        # Get or create the first organization
        org, created = Organization.objects.get_or_create(
            id=1,
            defaults={'name': 'Real Estate Company', 'description': 'Your trusted real estate partner'}
        )
        return org


class AdminAboutUsManagementViewSet(viewsets.ModelViewSet):
    """Admin management for about us content"""
    queryset = AboutUs.objects.all()
    serializer_class = AboutUsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]

    def get_object(self):
        # Get or create the first about us entry
        about, created = AboutUs.objects.get_or_create(
            id=1,
            defaults={
                'title': 'About Us',
                'content': 'We are a leading real estate company.',
                'vision': 'To be the most trusted real estate partner.',
                'mission': 'Helping people find their dream homes.',
                'is_active': True
            }
        )
        return about


# Missing endpoints that admin dashboard needs
class AdminContactsView(APIView):
    """Get contact inquiries for admin dashboard"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Use the real Contact model
        from django.db.models import Q

        queryset = Contact.objects.all().order_by('-created_at')

        # Filter parameters
        status_filter = request.query_params.get('status')
        subject_filter = request.query_params.get('subject')
        search = request.query_params.get('search')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if subject_filter:
            queryset = queryset.filter(subject=subject_filter)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(message__icontains=search)
            )

        # Serialize the data
        contacts = []
        for contact in queryset:
            contacts.append({
                'id': contact.id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'full_name': contact.full_name,
                'email': contact.email,
                'phone': contact.phone,
                'subject': contact.subject,
                'message': contact.message,
                'preferred_contact': contact.preferred_contact,
                'status': contact.status,
                'created_at': contact.created_at.isoformat(),
                'updated_at': contact.updated_at.isoformat(),
                'customer_details': UserSerializer(contact.customer).data if contact.customer else None
            })

        return Response(contacts)


class AdminContactResolveView(APIView):
    """Mark contact as resolved"""
    permission_classes = [IsAdminUser]

    def put(self, request, contact_id):
        try:
            contact = Contact.objects.get(id=contact_id)
            contact.status = 'resolved'
            contact.save()

            return Response({
                'message': 'Contact marked as resolved',
                'contact': {
                    'id': contact.id,
                    'status': contact.status,
                    'full_name': contact.full_name
                }
            })
        except Contact.DoesNotExist:
            return Response(
                {'message': 'Contact not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class AdminAchievementsView(APIView):
    """Get achievements data for admin dashboard"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Return achievements/statistics data
        achievements = {
            'properties_sold': Property.objects.filter(is_active=True).count(),
            'happy_customers': User.objects.filter(is_active=True, is_staff=False).count(),
            'years_experience': 15,
            'awards_won': 8
        }
        return Response(achievements)


# Property Alert Views
class PropertyAlertListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertyAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyAlert.objects.filter(customer=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PropertyAlertCreateSerializer
        return PropertyAlertSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PropertyAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PropertyAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PropertyAlert.objects.filter(customer=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {'message': 'Property alert deactivated successfully'},
            status=status.HTTP_204_NO_CONTENT
        )


# Gallery Views
class GalleryListView(generics.ListAPIView):
    queryset = Gallery.objects.filter(is_active=True)
    serializer_class = GallerySerializer
    permission_classes = [permissions.AllowAny]


class GalleryDetailView(generics.RetrieveAPIView):
    queryset = Gallery.objects.filter(is_active=True)
    serializer_class = GallerySerializer
    permission_classes = [permissions.AllowAny]


# News Views
class NewsCategoryListView(generics.ListAPIView):
    queryset = NewsCategory.objects.filter(is_active=True)
    serializer_class = NewsCategorySerializer
    permission_classes = [permissions.AllowAny]


class NewsListView(generics.ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)
        category = self.request.query_params.get('category', None)
        featured = self.request.query_params.get('featured', None)

        if category:
            queryset = queryset.filter(category__id=category)
        if featured:
            queryset = queryset.filter(is_featured=True)

        return queryset.order_by('-published_at')


class NewsDetailView(generics.RetrieveAPIView):
    queryset = News.objects.filter(is_published=True)
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'


# Admin Management ViewSets for Gallery and News
class AdminGalleryManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for galleries"""
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [IsAdminUser]


@method_decorator(csrf_exempt, name='dispatch')
class AdminGalleryImageManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for gallery images"""
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]


@method_decorator(csrf_exempt, name='dispatch')
class AdminPropertyImageManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for property images"""
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        """Handle order assignment and primary image logic"""
        property_instance = serializer.validated_data.get('property')

        # Get the next order number for this property
        existing_images = PropertyImage.objects.filter(property=property_instance)
        next_order = existing_images.count()

        # If order is not provided or is 0, use the next available order
        if 'order' not in serializer.validated_data or serializer.validated_data['order'] == 0:
            serializer.validated_data['order'] = next_order

        # If this is the first image for the property, make it primary
        if existing_images.count() == 0:
            serializer.validated_data['is_primary'] = True

        # If setting as primary, unset other primary images for this property
        if serializer.validated_data.get('is_primary', False):
            existing_images.update(is_primary=False)

        serializer.save()

    def perform_update(self, serializer):
        """Handle primary image logic on update"""
        # If setting as primary, unset other primary images for this property
        if serializer.validated_data.get('is_primary', False):
            property_instance = serializer.instance.property
            PropertyImage.objects.filter(property=property_instance).exclude(
                id=serializer.instance.id
            ).update(is_primary=False)

        serializer.save()


class AdminNewsManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for news"""
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAdminUser]


class AdminNewsCategoryManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for news categories"""
    queryset = NewsCategory.objects.all()
    serializer_class = NewsCategorySerializer
    permission_classes = [IsAdminUser]


# Team Views
class TeamListView(generics.ListAPIView):
    """Get all active team members"""
    queryset = Team.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = TeamSerializer
    permission_classes = [permissions.AllowAny]


class AdminTeamManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for team members"""
    queryset = Team.objects.all().order_by('order', 'name')
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser]


# Contact Views
class ContactCreateView(generics.CreateAPIView):
    """Create a new contact submission (public endpoint)"""
    serializer_class = ContactCreateSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()

        return Response({
            'message': 'Thank you for your message. We\'ll get back to you soon!',
            'contact_id': contact.id
        }, status=status.HTTP_201_CREATED)


class AdminContactManagementViewSet(viewsets.ModelViewSet):
    """Admin CRUD for contact submissions"""
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Contact.objects.all().order_by('-created_at')

        # Filter parameters
        status_filter = self.request.query_params.get('status')
        subject_filter = self.request.query_params.get('subject')
        search = self.request.query_params.get('search')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if subject_filter:
            queryset = queryset.filter(subject=subject_filter)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(message__icontains=search)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Mark contact as resolved"""
        contact = self.get_object()
        contact.status = 'resolved'
        contact.save()

        return Response({
            'message': 'Contact marked as resolved',
            'contact': ContactSerializer(contact).data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get contact statistics"""
        total_contacts = Contact.objects.count()
        new_contacts = Contact.objects.filter(status='new').count()
        in_progress_contacts = Contact.objects.filter(status='in_progress').count()
        resolved_contacts = Contact.objects.filter(status='resolved').count()

        # Recent contacts (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_contacts = Contact.objects.filter(created_at__gte=thirty_days_ago).count()

        return Response({
            'total_contacts': total_contacts,
            'new_contacts': new_contacts,
            'in_progress_contacts': in_progress_contacts,
            'resolved_contacts': resolved_contacts,
            'recent_contacts': recent_contacts,
        })