from django import forms
from .models import Review, RATING_CHOICES

class ReviewForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4, 
            'placeholder': 'Ваш відгук про товар...',
            'class': 'review-text-input'
        }),
        label="Текст відгуку",
    )
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio-input'}),
        label="Оцінка (зірок)",
        initial=5,
    )

    class Meta:
        model = Review
        fields = ['rating', 'content']