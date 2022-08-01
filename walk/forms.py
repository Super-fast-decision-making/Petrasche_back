from django import forms
from .models import WalkingMate

# 만약 모델 기반이 아니라면 forms.Form
class WalkingMate(forms.ModelForm):
    class Meta:
        model = WalkingMate
        fields = ['contents']