from django import forms
from .models import Post, User, Community


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'community', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 10,
                'placeholder': 'Введите текст публикации...'
            }),
            'community': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'content': 'Содержание',
            'community': 'Сообщество (необязательно)',
            'is_published': 'Опубликовать'
        }
        help_texts = {
            'content': 'Напишите что-нибудь интересное',
            'community': 'Выберите сообщество, если хотите опубликовать пост в нем',
            'is_published': 'Снимите галочку, чтобы сохранить как черновик'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['community'].required = False
        self.fields['community'].empty_label = "Без сообщества"
