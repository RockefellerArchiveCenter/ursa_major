from django import forms


class URLForm(forms.Form):
    endpoint = forms.CharField()


class ZIPForm(forms.Form):
    zip = forms.FileField()