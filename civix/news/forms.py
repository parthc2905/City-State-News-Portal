from django import forms
from .models import News_article, ArticleMedia

class ArticleWriteForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-input large",
            "placeholder": "Enter your article headline...",
            "maxlength": "150",
            "oninput":"updateWordCount()"
        })
    )

    excerpt = forms.CharField(
        required=True,
        max_length=300,
        widget=forms.Textarea(attrs={
            "class": "form-input",
            "rows": 3,
            "placeholder": "Write a brief summary of your article (2-3 sentences)...",
            "style": "min-height: 80px; font-family: 'Inter', sans-serif; font-size: 15px;"
        })
    )

    content = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": "form-textarea",
            "placeholder": """Start writing your article here...
                Use clear paragraphs and structure your article well.
                Write in a journalistic style with facts, quotes, and proper attribution.""",
            "oninput": "updateWordCount()"
        })
    )

    visibility_choice =(
        ("public", "Public"),
        ("subscriber", "Subscribers Only"),
        ("private", "Private"),
    )
    visibility = forms.ChoiceField(
        choices=visibility_choice,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'name' : 'visibility'
        }),
        required=True
    )

    PUBLICATION_STATUS = (
    ("draft", "Save as Draft"),
    ("published", "Publish Immediately"),
    )
    publication_status = forms.ChoiceField(
        choices=PUBLICATION_STATUS,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'name' : 'status'
        }),
        required=True
    )

    class Meta:
        model = News_article
        fields = ("title", "excerpt", "content", "category_id", "city_id", 'visibility', )

        widgets = {
            "category_id": forms.Select(attrs={"class":"form-select"}),
            "city_id": forms.Select(attrs={"class":"form-select"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category_id"].empty_label = "Select Category"
        self.fields["city_id"].empty_label = "Select City"
    
class ArticleMediaForm(forms.ModelForm):

    file = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "file-input",
            "id": "featuredImage",
            "accept": "image/*",
            "onchange": "handleImageUpload(event)"
        })
    )

    class Meta:
        model = ArticleMedia

        fields = ('file',)