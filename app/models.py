from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')  # Set role to admin for superusers

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class Organization(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    
    # Contact Information
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # Social Media
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'

    def __str__(self):
        return self.name


# Property Management Models
class PropertyType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Property Type'
        verbose_name_plural = 'Property Types'

    def __str__(self):
        return self.name


class Property(models.Model):
    AREA_UNIT_CHOICES = [
        ('aana', 'Aana (आना)'),
        ('ropani', 'Ropani (रोपनी)'),
        ('dhur', 'Dhur (धुर)'),
        ('bigha', 'Bigha (बिघा)'),
        ('kattha', 'Kattha (कट्ठा)'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in selected unit")
    area_unit = models.CharField(max_length=10, choices=AREA_UNIT_CHOICES, default='aana', help_text="Unit of area measurement")
    location = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return self.title

    @property
    def formatted_area(self):
        """Return formatted area with unit"""
        unit_display = dict(self.AREA_UNIT_CHOICES).get(self.area_unit, self.area_unit)
        return f"{self.area} {unit_display}"

    @property
    def area_in_sqft(self):
        """Convert area to square feet for calculations"""
        conversion_rates = {
            'aana': 342.25,
            'ropani': 5476,  # 16 aana
            'dhur': 273.8,   # 1/20 ropani
            'bigha': 72900,  # 20 kattha
            'kattha': 3645,  # 20 dhur
        }
        return float(self.area) * conversion_rates.get(self.area_unit, 1)


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='properties/')
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.property.title}"


# Agent Management
class Agent(models.Model):
    # Personal Information
    first_name = models.CharField(max_length=100, default='Agent')
    last_name = models.CharField(max_length=100, default='Name')
    email = models.EmailField(default='agent@example.com')
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='agents/', blank=True, null=True)

    # Professional Information
    title = models.CharField(max_length=200, default="Real Estate Agent")
    bio = models.TextField(blank=True)
    specializations = models.ManyToManyField(PropertyType, blank=True)
    experience_years = models.IntegerField(default=0)
    license_number = models.CharField(max_length=100, blank=True)

    # Contact & Social
    whatsapp = models.CharField(max_length=20, blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def specialization_names(self):
        return ", ".join([spec.name for spec in self.specializations.all()])


# Customer Interactions
class PropertyInquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('responded', 'Responded'),
        ('closed', 'Closed')
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Inquiry'
        verbose_name_plural = 'Property Inquiries'

    def __str__(self):
        return f"Inquiry for {self.property.title} by {self.customer.username}"


class PropertyVisit(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Property Visit'
        verbose_name_plural = 'Property Visits'

    def __str__(self):
        return f"Visit to {self.property.title} on {self.scheduled_date}"


class SavedProperty(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['customer', 'property']
        verbose_name = 'Saved Property'
        verbose_name_plural = 'Saved Properties'

    def __str__(self):
        return f"{self.customer.username} saved {self.property.title}"


# Content Management
class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['order']

    def __str__(self):
        return self.title


class HeroSlide(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    link_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Hero Slide'
        verbose_name_plural = 'Hero Slides'
        ordering = ['order']

    def __str__(self):
        return self.title


class JourneyStep(models.Model):
    year = models.CharField(max_length=4, help_text="Year of the milestone (e.g., 2020)")
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Journey Step'
        verbose_name_plural = 'Journey Steps'
        ordering = ['order']

    def __str__(self):
        return self.title


class AboutUs(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    vision = models.TextField()
    mission = models.TextField()
    image1 = models.ImageField(upload_to='about/', blank=True)
    image2 = models.ImageField(upload_to='about/', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'About Us'
        verbose_name_plural = 'About Us'

    def __str__(self):
        return self.title


# Property Alerts
class PropertyAlert(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE, null=True, blank=True)
    min_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    min_bedrooms = models.IntegerField(null=True, blank=True)
    max_bedrooms = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Alert'
        verbose_name_plural = 'Property Alerts'

    def __str__(self):
        return f"Alert for {self.customer.username}"


# Gallery Management
class Gallery(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.gallery.title} - {self.title or 'Image'}"


# News/Blog Management
class NewsCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'News Category'
        verbose_name_plural = 'News Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    excerpt = models.TextField(max_length=500, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, blank=True)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    # Status
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Team(models.Model):
    """Team member model for company staff"""
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    image = models.ImageField(upload_to='team/', blank=True, null=True)

    # Social media links
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)

    # Display order and status
    order = models.PositiveIntegerField(default=0, help_text="Order of display (lower numbers first)")
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position}"


class Contact(models.Model):
    """Contact form submissions"""
    SUBJECT_CHOICES = [
        ('buying', 'I\'m interested in buying'),
        ('selling', 'I want to sell my property'),
        ('investment', 'Investment opportunities'),
        ('consultation', 'Schedule a consultation'),
        ('other', 'Other inquiry'),
    ]

    PREFERRED_CONTACT_CHOICES = [
        ('email', 'Email'),
        ('phone', 'Phone'),
        ('text', 'Text Message'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # Contact Details
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES)
    message = models.TextField()
    preferred_contact = models.CharField(max_length=10, choices=PREFERRED_CONTACT_CHOICES)

    # System Fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Submission'
        verbose_name_plural = 'Contact Submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_subject_display()}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CustomerMessage(models.Model):
    """Messages between customers and agents"""
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_messages')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='agent_messages', null=True, blank=True)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_from_customer = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer Message'
        verbose_name_plural = 'Customer Messages'
        ordering = ['-created_at']

    def __str__(self):
        sender = self.customer.get_full_name() if self.is_from_customer else (self.agent.full_name if self.agent else 'System')
        return f"{sender}: {self.subject[:50]}"


class CustomerDocument(models.Model):
    """Documents available to customers"""
    DOCUMENT_TYPE_CHOICES = [
        ('brochure', 'Property Brochure'),
        ('contract', 'Contract'),
        ('guide', 'Guide'),
        ('report', 'Report'),
        ('other', 'Other'),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other')
    file = models.FileField(upload_to='customer_documents/', null=True, blank=True)
    download_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Customer Document'
        verbose_name_plural = 'Customer Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.customer.get_full_name()}"