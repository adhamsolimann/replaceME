from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Customer, Item, ContactMessage , Usecase
from django.contrib.postgres.forms import RangeWidget
from django.contrib.postgres.forms import DecimalRangeField

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Passwort', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Passwort wiederholen', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class PreferencesForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('height', 'width', 'depth', 'inStock', 'material')
        widgets = { 
        'height': forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'}),
        'width': forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'}),
        'depth': forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'}),
        'inStock': forms.NumberInput(attrs={'type': 'number','min': '0','step':'1'})
        }

    
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('Email', 'Titel','Beschreibung')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name','email')


class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']


class UseCaseForm(forms.ModelForm):
    usecase = forms.ModelChoiceField(queryset=Usecase.objects.all(),required=False)
    class Meta:
        model = Usecase
        fields = ('usecase',)



class AddUseCaseForm(forms.ModelForm):
    class Meta:
        model = Usecase
        fields =  ('name', 'description', 'heat_conductivity', 'tensile_strength', 'hardness', 'heat_capacity', 'electric_conductivity', 'magnetism', 'density')
        widgets = { 
        'heat_conductivity': RangeWidget(base_widget=forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'})),
        'tensile_strength': RangeWidget(base_widget=forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'})),
        'hardness': RangeWidget(base_widget=forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'})),
        'electric_conductivity': RangeWidget(base_widget=forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'})),
        'density': RangeWidget(base_widget=forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'})),
        'heat_capacity': RangeWidget(base_widget=forms.TextInput(attrs={'type': 'number','min': '0','step':'0.01'}))
        }

        labels = {
        'name' : 'Usecase Name',
        'description': 'Beschreibung',
        'heat_conductivity': 'Wärmeleitfähigkeit (W/m*K)',
        'tensile_strength':  'Zugfestigkeit (N/mm^2)',
        'hardness': 'Härte (HV)',
        'electric_conductivity':  'Elektrische Leitfähigkeit (S/m)',
        'density': 'Dichte (g/cm^3)',
        'magnetism': 'Magnetisch ja/nein',
        'heat_capacity': 'Spezifische Wärmekapazität (kJ/K*kg)',

        }

