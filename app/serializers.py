from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    User, Organization, PropertyType, Property, PropertyImage, Agent,
    PropertyInquiry, PropertyVisit, SavedProperty, Service, HeroSlide,
    JourneyStep, AboutUs, PropertyAlert, Gallery, GalleryImage,
    NewsCategory, News, Team, Contact, CustomerMessage, CustomerDocument
)

User = get_user_model()


# Authentication Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide username and password')
        return attrs


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'roles')
        read_only_fields = ('id', 'date_joined', 'roles')

    def get_roles(self, obj):
        """Return user role from the role field, with fallback to staff/superuser check"""
        if hasattr(obj, 'role') and obj.role:
            return obj.role
        # Fallback for existing users without role field
        if obj.is_superuser or obj.is_staff:
            return 'admin'
        return 'customer'


# Organization Serializers
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


# Property Serializers
class PropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyType
        fields = '__all__'


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ('id', 'image', 'is_primary', 'order')


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    formatted_area = serializers.ReadOnlyField()
    area_in_sqft = serializers.ReadOnlyField()

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    property_type = PropertyTypeSerializer(read_only=True)
    formatted_area = serializers.ReadOnlyField()
    area_in_sqft = serializers.ReadOnlyField()

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Agent Serializers
class AgentSerializer(serializers.ModelSerializer):
    specializations = PropertyTypeSerializer(many=True, read_only=True)
    full_name = serializers.ReadOnlyField()
    specialization_names = serializers.ReadOnlyField()

    class Meta:
        model = Agent
        fields = '__all__'


# Customer Interaction Serializers
class PropertyInquirySerializer(serializers.ModelSerializer):
    customer_details = UserSerializer(source='customer', read_only=True)
    property_details = PropertySerializer(source='property', read_only=True)
    agent_details = AgentSerializer(source='agent', read_only=True)

    class Meta:
        model = PropertyInquiry
        fields = '__all__'
        read_only_fields = ('created_at',)


class PropertyInquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyInquiry
        fields = ('property', 'agent', 'message')

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class PropertyVisitSerializer(serializers.ModelSerializer):
    customer_details = UserSerializer(source='customer', read_only=True)
    property_details = PropertySerializer(source='property', read_only=True)
    agent_details = AgentSerializer(source='agent', read_only=True)

    class Meta:
        model = PropertyVisit
        fields = '__all__'


class PropertyVisitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVisit
        fields = ('property', 'agent', 'scheduled_date', 'scheduled_time', 'notes')

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        validated_data['status'] = 'scheduled'
        return super().create(validated_data)


class SavedPropertySerializer(serializers.ModelSerializer):
    property_details = PropertySerializer(source='property', read_only=True)

    class Meta:
        model = SavedProperty
        fields = '__all__'
        read_only_fields = ('customer', 'created_at')


class SavedPropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedProperty
        fields = ('property',)

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


# Content Management Serializers
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = '__all__'


class JourneyStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = JourneyStep
        fields = '__all__'


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'


# Property Alert Serializers
class PropertyAlertSerializer(serializers.ModelSerializer):
    customer_details = UserSerializer(source='customer', read_only=True)
    property_type_details = PropertyTypeSerializer(source='property_type', read_only=True)

    class Meta:
        model = PropertyAlert
        fields = '__all__'
        read_only_fields = ('customer', 'created_at')


class PropertyAlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyAlert
        fields = ('property_type', 'min_price', 'max_price', 'location', 'min_bedrooms', 'max_bedrooms')

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


# Admin Analytics Serializers
class AdminAnalyticsSerializer(serializers.Serializer):
    total_properties = serializers.IntegerField()
    active_properties = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_agents = serializers.IntegerField()
    total_inquiries = serializers.IntegerField()
    pending_inquiries = serializers.IntegerField()
    scheduled_visits = serializers.IntegerField()
    recent_properties = PropertySerializer(many=True)
    recent_inquiries = PropertyInquirySerializer(many=True)


# User Management Serializers (for admin)
class UserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password', 'is_active', 'is_staff')

    def create(self, validated_data):
        password = validated_data.pop('password')

        # Set role based on is_staff flag
        if validated_data.get('is_staff', False):
            validated_data['role'] = 'admin'
        else:
            validated_data['role'] = 'customer'

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff')

    def update(self, instance, validated_data):
        # Update role based on is_staff flag if it's being changed
        if 'is_staff' in validated_data:
            if validated_data['is_staff']:
                validated_data['role'] = 'admin'
            else:
                validated_data['role'] = 'customer'

        return super().update(instance, validated_data)


# Gallery Serializers
class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'
        read_only_fields = ('created_at',)


class GallerySerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Gallery
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# News Serializers
class NewsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsCategory
        fields = '__all__'
        read_only_fields = ('created_at',)


class NewsSerializer(serializers.ModelSerializer):
    category_details = NewsCategorySerializer(source='category', read_only=True)

    class Meta:
        model = News
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Team Serializers
class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Contact Serializers
class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    customer_details = UserSerializer(source='customer', read_only=True)

    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ('customer', 'created_at', 'updated_at')


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('first_name', 'last_name', 'email', 'phone', 'subject', 'message', 'preferred_contact')

    def create(self, validated_data):
        # If user is authenticated, associate the contact with the user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['customer'] = request.user

        return super().create(validated_data)


# Customer Messages Serializers
class CustomerMessageSerializer(serializers.ModelSerializer):
    agent_details = AgentSerializer(source='agent', read_only=True)
    property_details = PropertySerializer(source='property', read_only=True)
    sender_name = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = CustomerMessage
        fields = '__all__'
        read_only_fields = ('customer', 'created_at', 'updated_at')

    def get_sender_name(self, obj):
        if obj.is_from_customer:
            return 'You'
        elif obj.agent:
            return f"{obj.agent.full_name} (Agent)"
        else:
            return 'System'

    def get_time_ago(self, obj):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        diff = now - obj.created_at

        if diff < timedelta(minutes=1):
            return 'Just now'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = diff.days
            return f"{days} day{'s' if days != 1 else ''} ago"
        else:
            return obj.created_at.strftime('%b %d, %Y')


class CustomerMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMessage
        fields = ('agent', 'property', 'subject', 'message')

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        validated_data['is_from_customer'] = True
        return super().create(validated_data)


# Customer Documents Serializers
class CustomerDocumentSerializer(serializers.ModelSerializer):
    property_details = PropertySerializer(source='property', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    downloaded_at = serializers.SerializerMethodField()

    class Meta:
        model = CustomerDocument
        fields = '__all__'
        read_only_fields = ('customer', 'download_count', 'created_at', 'updated_at')

    def get_downloaded_at(self, obj):
        return obj.updated_at.strftime('%b %d, %Y')