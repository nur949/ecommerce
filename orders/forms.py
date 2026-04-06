from django import forms

from .models import Address, Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'phone', 'country', 'city', 'area', 'postcode', 'address_line', 'delivery_type']
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'full_name': 'Recipient Name',
            'phone': 'Contact Number',
            'city': 'District / City',
            'area': 'Area / Thana / Upazilla',
            'postcode': 'Post Code',
            'address_line': 'Address',
            'delivery_type': 'Effective Delivery',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{existing} form-control'.strip()


class PaymentSelectionForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=Order.PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial='cod',
    )
    mobile_number = forms.CharField(required=False, max_length=20)
    transaction_id = forms.CharField(required=False, max_length=50)
    cardholder_name = forms.CharField(required=False, max_length=120)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'payment_method':
                continue
            field.widget.attrs['class'] = 'form-control'
