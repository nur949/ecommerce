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
            if field.required:
                field.widget.attrs['required'] = 'required'

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        normalized = phone.replace('+', '', 1).replace('-', '').replace(' ', '')
        if not normalized.isdigit() or len(normalized) < 8:
            raise forms.ValidationError('Enter a valid contact number.')
        return phone

    def clean_address_line(self):
        address = self.cleaned_data['address_line'].strip()
        if len(address) < 8:
            raise forms.ValidationError('Please enter a complete delivery address.')
        return address


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
            field.widget.attrs['maxlength'] = str(field.max_length)

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        if method == 'bkash':
            if not cleaned_data.get('mobile_number'):
                self.add_error('mobile_number', 'Mobile number is required for bKash payments.')
            if not cleaned_data.get('transaction_id'):
                self.add_error('transaction_id', 'Transaction ID is required for bKash payments.')
        if method == 'stripe' and not cleaned_data.get('cardholder_name'):
            self.add_error('cardholder_name', 'Cardholder name is required for card payments.')
        return cleaned_data
