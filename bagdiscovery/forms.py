from django import forms


class URLForm(forms.Form):
    endpoint = forms.CharField()
