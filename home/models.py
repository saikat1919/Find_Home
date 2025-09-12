from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.urls import reverse
from cloudinary.models import CloudinaryField

class UserProfile(models.Model):
    USER_TYPES = (
        ('renter', 'Renter'),
        ('owner', 'Owner'),
        ('admin', 'Admin'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class HouseListing(models.Model):
    HOUSE_TYPES = (
        ('bachelor_male', 'Bachelor Male'),
        ('bachelor_female', 'Bachelor Female'),
        ('family', 'Family'),
    )
    
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('booked', 'Booked'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    house_type = models.CharField(max_length=15, choices=HOUSE_TYPES)
    address = models.TextField()
    area = models.CharField(max_length=100)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_reported = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('listing_detail', kwargs={'pk': self.pk})

class HouseImage(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.listing.title}"

class SavedListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'listing')

class Interest(models.Model):
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('renter', 'listing')

class Comment(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class ChatMessage(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']

class Report(models.Model):
    listing = models.ForeignKey(HouseListing, on_delete=models.CASCADE)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
