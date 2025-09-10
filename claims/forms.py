from django import forms
from django.core.exceptions import ValidationError


class DataUploadForm(forms.Form):
    """Form for uploading claims data files"""
    
    FILE_FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
    ]
    
    claims_file = forms.FileField(
        label='Claims File',
        help_text='Upload a JSON or CSV file containing claims data (patient names, amounts, etc.)',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': '.json,.csv'
        })
    )
    
    details_file = forms.FileField(
        label='Claim Details File',
        help_text='Upload a JSON or CSV file containing claim details (CPT codes, denial reasons)',
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
            'accept': '.json,.csv'
        })
    )
    
    file_format = forms.ChoiceField(
        choices=FILE_FORMAT_CHOICES,
        label='File Format',
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm'
        })
    )
    
    clear_existing = forms.BooleanField(
        required=False,
        label='Clear existing data',
        help_text='Remove all existing claims before importing new data',
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded'
        })
    )
    
    def clean_claims_file(self):
        file = self.cleaned_data.get('claims_file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('Claims file size cannot exceed 10MB')
            
            # Check file extension
            allowed_extensions = ['.json', '.csv']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Claims file must be a JSON or CSV file')
        
        return file
    
    def clean_details_file(self):
        file = self.cleaned_data.get('details_file')
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('Details file size cannot exceed 10MB')
            
            # Check file extension
            allowed_extensions = ['.json', '.csv']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError('Details file must be a JSON or CSV file')
        
        return file
