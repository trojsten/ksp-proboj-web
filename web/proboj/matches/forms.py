from django import forms


class MatchUploadForm(forms.Form):
    successful = forms.BooleanField(required=False)
    scores = forms.JSONField(required=False)
    server_log = forms.FileField(required=False)
    observer_log = forms.FileField(required=False)
    bot_logs = forms.FileField(required=False)
