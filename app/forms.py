from django import forms
from django.utils import timezone
from datetime import datetime

import qrcode
from .models import chauffeur, camion, prestataire, Utilisateur, EntreeSortie

class RechercheCamionForm(forms.Form):
    id_chauffeur = forms.IntegerField(
        label='ID Chauffeur',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    matricule_camion = forms.CharField(
        label='Matricule Camion',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class ChauffeurForm(forms.ModelForm):
    class Meta:
        model = chauffeur
        fields = ['nom_chauffeur', 'prenom_chauffeur', 'permis_chauffeur']


class CamionForm(forms.ModelForm):
    # Champs pour nouveau prestataire


    class Meta:
        model = camion
        fields = ['id_camion', 'id_chauffeur', 'id_prestataire', 'matricule_camion', 
                  'capacite']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_prestataire'].required = False

    def clean(self):
        cleaned_data = super().clean()
        creer_nouveau = self.data.get('creer_nouveau_prestataire') == 'on'
        id_prestataire = cleaned_data.get('id_prestataire')
        
        # if not creer_nouveau and not id_prestataire:
        #     raise forms.ValidationError(
        #         "Veuillez sélectionner un prestataire existant ou cocher 'Créer un nouveau prestataire'."
        #     )
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('creer_nouveau_prestataire'):
            # Créer un nouveau prestataire
            nouveau_prestataire = prestataire.objects.create(
                nom_prestataire=self.cleaned_data['nouveau_nom_prestataire'],
                adresse_prestataire=self.cleaned_data['nouvelle_adresse_prestataire'],
                frais_prestataire=self.cleaned_data['nouveau_frais_prestataire'],
                telephone_prestataire=self.cleaned_data['nouveau_telephone_prestataire']
            )
            instance.id_prestataire = nouveau_prestataire
        
        if commit:
            instance.save()
        return instance

class PrestataireForm(forms.ModelForm):
    class Meta:
        model = prestataire
        fields = [
            'nom_prestataire',
            'adresse_prestataire',
            'frais_prestataire',
            'telephone_prestataire'
        ]

class UserForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['id_user','username', 'password', 'is_admin']

class NouveauPrestataireForm(forms.ModelForm):
    class Meta:
        model = prestataire
        fields = ['nom_prestataire', 'adresse_prestataire', 'frais_prestataire', 'telephone_prestataire']
        widgets = {
            'nom_prestataire': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du prestataire'
            }),
            'adresse_prestataire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse'
            }),
            'frais_prestataire': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Frais'
            }),
            'telephone_prestataire': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Téléphone'
            }),
        }

class BadgeForm(forms.Form):
    chauffeur = forms.ModelChoiceField(
        queryset=chauffeur.objects.all(),
        label='Sélectionner un chauffeur',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        fields = ['chauffeur']














# class ChauffeurForm(forms.ModelForm):
#     class Meta:
#         model = chauffeur 
#         fields = ['id_chauffeur', 'nom_chauffeur', 'prenom_chauffeur', 'permis_chauffeur','prestataire']

# class CamionForm(forms.ModelForm):
#     date_entreeC = forms.DateField(
#         widget=forms.DateInput(attrs={'type': 'date'})
#     )
#     date_sortieC = forms.DateField(
#         required=False,
#         widget=forms.DateInput(attrs={'type': 'date'})
#     )
#     heure_sortieC = forms.TimeField(
#         required=False,
#         widget=forms.TimeInput(attrs={'type': 'time'})
#     )
#     heure_entreeC = forms.TimeField(
#         widget=forms.TimeInput(attrs={'type': 'time'})
#     )
#     class Meta:
#         model = camion
#         fields = ['id_camion', 'id_chauffeur', 'matricule_camion', 'nom_societe', 'capacite', 'date_entreeC', 'date_sortieC', 'heure_entreeC', 'heure_sortieC']
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if not instance.id_chauffeur:
#             instance.id_chauffeur = chauffeur.objects.create(
#                 nom_chauffeur=instance.nom_chauffeur,
#                 prenom_chauffeur=instance.prenom_chauffeur,
#                 permis_chauffeur=instance.permis_chauffeur
#             )
#         if commit:
#             instance.save()
#         return instance

class SortieCamionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("\n--- Initialisation du formulaire SortieCamionForm ---")
        print(f"Données initiales: {self.initial}")
        print(f"Données: {self.data if self.data else 'Aucune donnée'}")
        
        # Configurer les champs avec des valeurs par défaut si nécessaire
        if not self.initial.get('date_sortie'):
            self.initial['date_sortie'] = timezone.now().date()
        if not self.initial.get('heure_sortie'):
            self.initial['heure_sortie'] = timezone.now().time()
            
        print(f"Valeurs initiales après traitement: {self.initial}")
    
    class Meta:
        model = EntreeSortie
        fields = ['date_sortie', 'heure_sortie']
        widgets = {
            'date_sortie': forms.DateInput(
                format='%Y-%m-%d',
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),
            'heure_sortie': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                    'step': '60'  # Pas de 1 minute
                }
            )
        }

    def clean(self):
        print("\n--- Nettoyage des données du formulaire ---")
        cleaned_data = super().clean()
        print(f"Données nettoyées: {cleaned_data}")
        
        date_sortie = cleaned_data.get('date_sortie')
        heure_sortie = cleaned_data.get('heure_sortie')
        instance = getattr(self, 'instance', None)
        
        print(f"Instance: {instance}")
        print(f"Date entrée: {getattr(instance, 'date_entree', None)}")
        print(f"Heure entrée: {getattr(instance, 'heure_entree', None)}")
        print(f"Date sortie: {date_sortie}")
        print(f"Heure sortie: {heure_sortie}")
        
        if date_sortie is None or heure_sortie is None:
            error_msg = 'Les champs date et heure de sortie sont obligatoires'
            print(f"Erreur de validation: {error_msg}")
            self.add_error('date_sortie', error_msg)
            self.add_error('heure_sortie', '')
            
        print("Fin du nettoyage des données")
        return cleaned_data
