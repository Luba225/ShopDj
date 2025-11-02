from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }