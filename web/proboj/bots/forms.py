from django import forms

from proboj.bots.models import BotVersion


class BotUploadForm(forms.ModelForm):
    class Meta:
        model = BotVersion
        fields = ["sources", "language"]

        labels = {
            "sources": "Zdrojáky",
            "language": "Jazyk",
        }

        help_texts = {
            "sources": "Vo formáte ZIP.",
        }


class CompileUploadForm(forms.Form):
    successful = forms.BooleanField(required=False)
    log = forms.CharField(required=False)
    output = forms.FileField(required=False)
