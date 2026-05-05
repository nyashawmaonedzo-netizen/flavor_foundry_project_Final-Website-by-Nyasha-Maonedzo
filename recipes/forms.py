from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image_url', 'image', 'category', 'available', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label='Full name')
    email = forms.EmailField(label='Email')
    shipping_address = forms.CharField(max_length=250, label='Shipping address')
    city = forms.CharField(max_length=100, label='City')
    postal_code = forms.CharField(max_length=30, label='Postal code')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your experience with this product...'}),
        }


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='A valid email address.')
    first_name = forms.CharField(max_length=30, required=False, label='First Name')
    last_name = forms.CharField(max_length=30, required=False, label='Last Name')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email