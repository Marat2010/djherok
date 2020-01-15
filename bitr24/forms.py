from django import forms
from .models import Chat, Bitr
from django.core.exceptions import ValidationError


class BitrForm(forms.ModelForm):
    class Meta:
        model = Bitr
        fields = ['bx24_id', 'bx24_name', 'slug']

        widgets = {
            'bx24_id': forms.TextInput(attrs={'class': 'form-control'}),
            'bx24_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bx24_slug': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()  # new_slug = self.cleaned_data.get('slug')
        if new_slug == 'create':
            raise ValidationError('Не может быть "Create"!!!')
        if Bitr.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('Слаг "{}" уже существует!'.format(new_slug))
        return new_slug


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['chat_id', 'first_name', 'slug', 'username', 'lang_code', 'bitrs']

        widgets ={
            'chat_id': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.Textarea(attrs={'class': 'form-control'}),
            'lang_code': forms.TextInput(attrs={'class': 'form-control'}),
            'bitrs': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()

        if new_slug == 'create':
            raise ValidationError('Не может быть "Create"!!!')
        return new_slug

    # bx24_id = forms.IntegerField()
    # bx24_name = forms.CharField(max_length=100)
    # slug = forms.CharField(max_length=100)
    #
    # bx24_id.widget.attrs.update({'class': 'form-control'})
    # bx24_name.widget.attrs.update({'class': 'form-control'})
    # slug.widget.attrs.update({'class': 'form-control'})

    # def save(self):
    #     new_bitr = Bitr.objects.create(bx24_id=self.cleaned_data['bx24_id'],
    #                                    bx24_name=self.cleaned_data['bx24_name'],
    #                                    slug=self.cleaned_data['slug'])
    #     return new_bitr



