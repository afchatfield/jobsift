from django import forms
from dal import autocomplete
from .models import JobBoard, JobBoardSelector, JobBoardSearchSelector, JobProfile

class JobBoardForm(forms.ModelForm):
    class Meta:
        model = JobBoard
        fields = ['name', 'url']


class JobBoardSelectorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['css_selector'].required = False

    class Meta:
        model = JobBoardSelector
        fields = ['job_field', 'css_selector']


class JobBoardSearchSelectorForm(forms.ModelForm):
    class Meta:
        model = JobBoardSearchSelector
        fields = ['selector_type', 'css_selector']


class JobProfileForm(forms.ModelForm):
    class Meta:
        model = JobProfile
        fields = ('__all__')
        widgets = {
            'job_boards': autocomplete.ModelSelect2Multiple(url='job_board-autocomplete')
        }

