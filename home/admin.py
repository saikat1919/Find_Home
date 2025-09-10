from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'created_at']
    list_filter = ['user_type', 'created_at']

class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1

@admin.register(HouseListing)
class HouseListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'house_type', 'area', 'rent', 'status', 'created_at']
    list_filter = ['house_type', 'status', 'created_at']
    search_fields = ['title', 'area', 'address']
    inlines = [HouseImageInline]

@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['renter', 'listing', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['listing', 'reporter', 'created_at', 'is_resolved']
    list_filter = ['is_resolved', 'created_at']