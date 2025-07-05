from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import (
    User, Organization, AboutUs, Achievements, Service, Journey,
    HeroSection, PropertyType, Property, Agent, Contact
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
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
            raise serializers.ValidationError('Must include username and password')
        
        return attrs


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class AboutUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutUs
        fields = '__all__'


class AchievementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievements
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    features_list = serializers.ReadOnlyField(source='get_features_list')
    
    class Meta:
        model = Service
        fields = '__all__'


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = '__all__'


class HeroSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = '__all__'


class PropertyTypeSerializer(serializers.ModelSerializer):
    properties_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PropertyType
        fields = '__all__'
    
    def get_properties_count(self, obj):
        return obj.properties.filter(status='available').count()


class PropertySerializer(serializers.ModelSerializer):
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = Property
        fields = '__all__'


class PropertyListSerializer(serializers.ModelSerializer):
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'location', 'bedrooms', 'bathrooms', 
            'area', 'status', 'image', 'property_type_name', 'is_featured', 'created_at'
        ]


class AgentSerializer(serializers.ModelSerializer):
    specialties_list = serializers.ReadOnlyField(source='get_specialties_list')
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Agent
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField(source='get_full_name')
    assigned_agent_name = serializers.CharField(source='assigned_agent.name', read_only=True)
    
    class Meta:
        model = Contact
        fields = '__all__'
        read_only_fields = ['status', 'assigned_agent', 'created_at', 'updated_at']


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'subject', 
            'message', 'preferred_contact_method'
        ]
    
    def validate_email(self, value):
        # Additional email validation if needed
        return value.lower()


class ContactUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['status', 'assigned_agent']


# Dashboard/Stats Serializers
class PropertyStatsSerializer(serializers.Serializer):
    total_properties = serializers.IntegerField()
    available_properties = serializers.IntegerField()
    sold_properties = serializers.IntegerField()
    pending_properties = serializers.IntegerField()
    featured_properties = serializers.IntegerField()


class ContactStatsSerializer(serializers.Serializer):
    total_contacts = serializers.IntegerField()
    new_contacts = serializers.IntegerField()
    in_progress_contacts = serializers.IntegerField()
    resolved_contacts = serializers.IntegerField()


class DashboardStatsSerializer(serializers.Serializer):
    property_stats = PropertyStatsSerializer()
    contact_stats = ContactStatsSerializer()
    total_agents = serializers.IntegerField()
    total_services = serializers.IntegerField()