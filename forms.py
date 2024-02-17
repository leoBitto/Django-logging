from django import forms

class ConsentForm(forms.Form):
    consent_given = forms.BooleanField(label="consenti alla registrazione dell'indirizzo ip?", required=False)
