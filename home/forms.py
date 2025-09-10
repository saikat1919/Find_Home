from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, HouseListing, HouseImage, Comment, Report

class UserRegistrationForm(UserCreationForm):
    USER_TYPES = (
        ('renter', 'Renter'),
        ('owner', 'Owner'),
    )
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    user_type = forms.ChoiceField(choices=USER_TYPES)
    phone = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', 'phone')

class HouseListingForm(forms.ModelForm):
    class Meta:
        model = HouseListing
        fields = ['title', 'description', 'house_type', 'address', 'area', 'rent', 'contact_phone', 'contact_email']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class HouseImageForm(forms.ModelForm):
    class Meta:
        model = HouseImage
        fields = ['image']

class SearchForm(forms.Form):
    HOUSE_TYPES = (
        ('', 'All Types'),
        ('bachelor_male', 'Bachelor Male'),
        ('bachelor_female', 'Bachelor Female'),
        ('family', 'Family'),
    )
    
    query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Search by area...'}))
    house_type = forms.ChoiceField(choices=HOUSE_TYPES, required=False)
    min_rent = forms.DecimalField(max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'placeholder': 'Min. Rent'}))
    max_rent = forms.DecimalField(max_digits=10, decimal_places=2, required=False,  widget=forms.NumberInput(attrs={'placeholder': 'Max. Rent'}))

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment...'})
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Please describe why you think this is a false advertisement...'})
        }