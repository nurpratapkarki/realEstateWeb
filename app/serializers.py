from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import (
    User, Organization, PropertyType, Property, PropertyImage, Agent,
    PropertyInquiry, PropertyVisit, SavedProperty, Service, HeroSlide,
    JourneyStep, AboutUs, PropertyAlert
)

User = get_user_model()


# Authentication Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'password', 'password_confirm')

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
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')


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

    class Meta:
        model = Property
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class PropertyDetailSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    property_type = PropertyTypeSerializer(read_only=True)

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
    user_details = UserSerializer(source='user', read_only=True)
    specializations = PropertyTypeSerializer(many=True, read_only=True)

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
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff')