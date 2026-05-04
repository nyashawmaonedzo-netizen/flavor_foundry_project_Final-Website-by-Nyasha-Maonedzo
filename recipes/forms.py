from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image_url', 'available', 'stock']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120, label='Full name')
    email = forms.EmailField(label='Email')
    shipping_address = forms.CharField(max_length=250, label='Shipping address')
    city = forms.CharField(max_length=100, label='City')
    postal_code = forms.CharField(max_length=30, label='Postal code')