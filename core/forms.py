from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': "I'm shopping for ...", 'class': 'form-control rounded-pill search-input'}))
