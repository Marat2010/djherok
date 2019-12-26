from django.forms import ModelForm

from .models import Recruits


class RecruitsForm(ModelForm):
    class Meta:
        model = Recruits
        fields = ('name', 'planet', 'age', 'email')
