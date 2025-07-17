from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, Organization, PropertyType, Property, PropertyImage, Agent,
    PropertyInquiry, PropertyVisit, SavedProperty, Service, HeroSlide,
    JourneyStep, AboutUs, PropertyAlert, Gallery, GalleryImage,
    NewsCategory, News, CustomerMessage, CustomerDocument
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'role', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'logo')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Social Media', {
            'fields': ('whatsapp', 'facebook', 'instagram', 'linkedin', 'twitter')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('is_active',)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'is_primary', 'order')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'property_type', 'price', 'bedrooms', 'bathrooms', 'location', 'formatted_area', 'is_featured', 'is_active')
    list_filter = ('property_type', 'area_unit', 'is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'location', 'address')
    list_editable = ('is_featured', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PropertyImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'property_type', 'price')
        }),
        ('Details', {
            'fields': ('bedrooms', 'bathrooms', 'area', 'area_unit')
        }),
        ('Location', {
            'fields': ('location', 'address', 'latitude', 'longitude')
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'is_primary', 'order')
    list_filter = ('is_primary',)
    search_fields = ('property__title',)
    list_editable = ('is_primary', 'order')


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'title', 'experience_years', 'is_active')
    list_filter = ('is_active', 'experience_years', 'specializations')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'license_number')
    list_editable = ('is_active',)
    filter_horizontal = ('specializations',)
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'photo')
        }),
        ('Professional Information', {
            'fields': ('title', 'bio', 'experience_years', 'license_number', 'specializations')
        }),
        ('Contact & Social', {
            'fields': ('whatsapp', 'linkedin', 'facebook', 'instagram')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(PropertyInquiry)
class PropertyInquiryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'property', 'agent', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'property__title')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'property', 'agent')


@admin.register(PropertyVisit)
class PropertyVisitAdmin(admin.ModelAdmin):
    list_display = ('customer', 'property', 'agent', 'scheduled_date', 'scheduled_time', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('customer__username', 'property__title')
    date_hierarchy = 'scheduled_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'property', 'agent')


@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ('customer', 'property', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__username', 'property__title')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'property')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('is_active', 'order')


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('is_active', 'order')


@admin.register(JourneyStep)
class JourneyStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('is_active', 'order')


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)
    list_editable = ('is_active',)


@admin.register(PropertyAlert)
class PropertyAlertAdmin(admin.ModelAdmin):
    list_display = ('customer', 'property_type', 'min_price', 'max_price', 'location', 'is_active', 'created_at')
    list_filter = ('is_active', 'property_type', 'created_at')
    search_fields = ('customer__username', 'location')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer', 'property_type')


# Gallery Admin
class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ('image', 'title', 'description', 'order', 'is_active')


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active', 'order')
    inlines = [GalleryImageInline]


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('gallery', 'title', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'gallery', 'created_at')
    search_fields = ('title', 'description', 'gallery__title')
    list_editable = ('order', 'is_active')


# News Admin
@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'is_published', 'published_at')
    list_filter = ('is_featured', 'is_published', 'category', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    list_editable = ('is_featured', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'excerpt', 'content', 'featured_image', 'category')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_featured', 'is_published', 'published_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CustomerMessage)
class CustomerMessageAdmin(admin.ModelAdmin):
    list_display = ('customer', 'agent', 'subject', 'is_from_customer', 'is_read', 'created_at')
    list_filter = ('is_from_customer', 'is_read', 'created_at')
    search_fields = ('customer__username', 'agent__first_name', 'agent__last_name', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_read',)

    fieldsets = (
        ('Message Details', {
            'fields': ('customer', 'agent', 'property', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('is_from_customer', 'is_read')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CustomerDocument)
class CustomerDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'document_type', 'download_count', 'is_active', 'created_at')
    list_filter = ('document_type', 'is_active', 'created_at')
    search_fields = ('title', 'customer__username', 'description')
    readonly_fields = ('download_count', 'created_at', 'updated_at')
    list_editable = ('is_active',)

    fieldsets = (
        ('Document Details', {
            'fields': ('customer', 'property', 'title', 'description', 'document_type', 'file')
        }),
        ('Status', {
            'fields': ('is_active', 'download_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )