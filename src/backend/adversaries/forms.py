from django import forms


class AdversaryCreateForm(forms.Form):
    name = forms.CharField(max_length=120)

    def clean_name(self):
        return self.cleaned_data["name"].strip()
