from django import forms
class MyForm(forms.Form):
    start_time = forms.DateTimeField(label='起始时间', widget=forms.DateTimeInput(attrs={'type': 'datetime-local','class': 'form-control datetime-input'}))
    end_time = forms.DateTimeField(label='结束时间', widget=forms.DateTimeInput(attrs={'type': 'datetime-local','class': 'form-control datetime-input'}))