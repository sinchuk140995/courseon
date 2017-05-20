from django import forms


class CabinetForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)


class SubscribeForm(CabinetForm):
    pass


class UnsubscribeForm(CabinetForm):
    pass


class CertificateUpload(CabinetForm):
    certificate = forms.ImageField()
