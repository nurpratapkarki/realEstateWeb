from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Organization, AboutUs, Achievements, Service, Journey,
    HeroSection, PropertyType, Property, Agent, Contact
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'created_at']
    search_fields = ['name', 'email', 'phone']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Social Media', {
            'fields': ('whatsapp', 'facebook', 'instagram', 'linkedin', 'twitter')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Achievements)
class AchievementsAdmin(admin.ModelAdmin):
    list_display = ['properties_sold', 'sales_volume', 'experience_years', 'clients_served', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'title', 'features']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'created_at']
    list_filter = ['year', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['-year']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'properties_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def properties_count(self, obj):
        return obj.properties.count()
    properties_count.short_description = 'Properties Count'


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'location', 'property_type', 'status', 'is_featured', 'created_at']
    list_filter = ['property_type', 'status', 'is_featured', 'bedrooms', 'bathrooms', 'created_at']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'image')
        }),
        ('Property Details', {
            'fields': ('price', 'location', 'bedrooms', 'bathrooms', 'area')
        }),
        ('Status & Features', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property_type')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone', 'specialties']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone')
        }),
        ('Professional Details', {
            'fields': ('specialties', 'bio', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'phone', 'subject', 'status', 'preferred_contact_method', 'created_at']
    list_filter = ['status', 'preferred_contact_method', 'created_at', 'assigned_agent']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'subject']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Contact Details', {
            'fields': ('subject', 'message', 'preferred_contact_method')
        }),
        ('Management', {
            'fields': ('status', 'assigned_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'
    
    actions = ['mark_as_in_progress', 'mark_as_resolved', 'mark_as_closed']
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f'{queryset.count()} contacts marked as in progress.')
    mark_as_in_progress.short_description = 'Mark selected contacts as in progress'
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(status='resolved')
        self.message_user(request, f'{queryset.count()} contacts marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected contacts as resolved'
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f'{queryset.count()} contacts marked as closed.')
    mark_as_closed.short_description = 'Mark selected contacts as closed'


# Customize admin site
admin.site.site_header = 'Real Estate Admin'
admin.site.site_title = 'Real Estate Admin'
admin.site.index_title = 'Welcome to Real Estate Administration'