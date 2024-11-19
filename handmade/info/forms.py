from django import forms


class MailForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    subject = forms.CharField(max_length=300, required=True)
    email = forms.EmailField(required=True)
    message = forms.TextInput()
