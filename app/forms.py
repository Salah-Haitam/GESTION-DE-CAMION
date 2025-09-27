from django import forms
from django.utils import timezone
from datetime import datetime

import qrcode
from .models import chauffeur, camion, prestataire, Utilisateur, EntreeSortie,site,Facture

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
    site = forms.ModelChoiceField(
        queryset=site.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Site de rattachement",
        required=True
    )

    class Meta:
        model = Utilisateur
        fields = ['id_user','username', 'password', 'site', 'is_admin']

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



class FactureForm(forms.ModelForm):
    VILLES_MAROC = [
        ("", ""),
        ("Agadir", "Agadir"),
        ("Ain Harrouda", "Ain Harrouda"),
        ("Ain Sebaa", "Ain Sebaa"),
        ("Ait Melloul", "Ait Melloul"),
        ("Akhfenir", "Akhfenir"),
        ("Al Hoceima", "Al Hoceima"),
        ("Aourir", "Aourir"),
        ("Arfoud", "Arfoud"),
        ("Asilah", "Asilah"),
        ("Azemmour", "Azemmour"),
        ("Azrou", "Azrou"),
        ("Ben Guerir", "Ben Guerir"),
        ("Beni Mellal", "Béni Mellal"),
        ("Berkane", "Berkane"),
        ("Berrechid", "Berrechid"),
        ("Biougra", "Biougra"),
        ("Bni Hadifa", "Bni Hadifa"),
        ("Bouarfa", "Bouarfa"),
        ("Boulemane", "Boulemane"),
        ("Bouskoura", "Bouskoura"),
        ("Bouznika", "Bouznika"),
        ("Casablanca", "Casablanca"),
        ("Chefchaouen", "Chefchaouen"),
        ("Dcheira El Jihadia", "Dcheira El Jihadia"),
        ("Demnate", "Demnate"),
        ("El Aioun Sidi Mellouk", "El Aioun Sidi Mellouk"),
        ("El Jadida", "El Jadida"),
        ("El Kelaa des Sraghna", "El Kelaa des Sraghna"),
        ("Errachidia", "Errachidia"),
        ("Essaouira", "Essaouira"),
        ("Fnideq", "Fnideq"),
        ("Fquih Ben Salah", "Fquih Ben Salah"),
        ("Fès", "Fès"),
        ("Guelmim", "Guelmim"),
        ("Guercif", "Guercif"),
        ("Had Soualem", "Had Soualem"),
        ("Ifrane", "Ifrane"),
        ("Imzouren", "Imzouren"),
        ("Jerada", "Jerada"),
        ("Kalaat Mgouna", "Kalaat Mgouna"),
        ("Kenitra", "Kenitra"),
        ("Khemisset", "Khemisset"),
        ("Khouribga", "Khouribga"),
        ("Ksar El Kebir", "Ksar El Kebir"),
        ("Larache", "Larache"),
        ("Marrakech", "Marrakech"),
        ("Martil", "Martil"),
        ("Mechra Bel Ksiri", "Mechra Bel Ksiri"),
        ("Meknès", "Meknès"),
        ("Midelt", "Midelt"),
        ("Missour", "Missour"),
        ("Mohammedia", "Mohammedia"),
        ("Nador", "Nador"),
        ("Ouarzazate", "Ouarzazate"),
        ("Ouazzane", "Ouazzane"),
        ("Oued Zem", "Oued Zem"),
        ("Oujda", "Oujda"),
        ("Oulad Teima", "Oulad Teima"),
        ("Rabat", "Rabat"),
        ("Safi", "Safi"),
        ("Salé", "Salé"),
        ("Sefrou", "Sefrou"),
        ("Settat", "Settat"),
        ("Sidi Bennour", "Sidi Bennour"),
        ("Sidi Ifni", "Sidi Ifni"),
        ("Sidi Kacem", "Sidi Kacem"),
        ("Sidi Slimane", "Sidi Slimane"),
        ("Sidi Taibi", "Sidi Taibi"),
        ("Sidi Yahya El Gharb", "Sidi Yahya El Gharb"),
        ("Skhirat", "Skhirat"),
        ("Souk El Arbaa", "Souk El Arbaa"),
        ("Talsint", "Talsint"),
        ("Tan-Tan", "Tan-Tan"),
        ("Tanant", "Tanant"),
        ("Tanger", "Tanger"),
        ("Taourirt", "Taourirt"),
        ("Taroudant", "Taroudant"),
        ("Taza", "Taza"),
        ("Temara", "Temara"),
        ("Tichla", "Tichla"),
        ("Tiflet", "Tiflet"),
        ("Tinghir", "Tinghir"),
        ("Tiznit", "Tiznit"),
        ("Tétouan", "Tétouan"),
        ("Youssoufia", "Youssoufia"),
        ("Zagora", "Zagora"),
        ("Zemmoura", "Zemmoura")
    ]

    destination = forms.ChoiceField(
        choices=VILLES_MAROC,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Ville de destination"
    )
    latitude_depart = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude_depart = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Facture
        fields = [
            'affectation',
            'poids_marchandise',
            'destination',
            'prix_par_km',
            'prix_par_tonne',
        ]
        widgets = {
            'affectation': forms.Select(attrs={'class': 'form-control'}),
            'poids_marchandise': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Poids en tonnes'
            }),
            'prix_par_km': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Prix par kilomètre'
            }),
            'prix_par_tonne': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Prix par tonne'
            }),
        }


# class SortieCamionForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         print("\n--- Initialisation du formulaire SortieCamionForm ---")
#         print(f"Données initiales: {self.initial}")
#         print(f"Données: {self.data if self.data else 'Aucune donnée'}")
        
#         # Configurer les champs avec des valeurs par défaut si nécessaire
#         if not self.initial.get('date_sortieC'):
#             self.initial['date_sortieC'] = timezone.now().date()
#         if not self.initial.get('heure_sortieC'):
#             self.initial['heure_sortieC'] = timezone.now().time()
            
#         print(f"Valeurs initiales après traitement: {self.initial}")
    
#     class Meta:
#         model = camion
#         fields = ['date_sortieC', 'heure_sortieC']
#         widgets = {
#             'date_sortieC': forms.DateInput(
#                 format='%Y-%m-%d',
#                 attrs={
#                     'type': 'date',
#                     'class': 'form-control',
#                 }
#             ),
#             'heure_sortieC': forms.TimeInput(
#                 format='%H:%M',
#                 attrs={
#                     'type': 'time',
#                     'class': 'form-control',
#                     'step': '60'  # Pas de 1 minute
#                 }
#             )
#         }

#     def clean(self):
#         print("\n--- Nettoyage des données du formulaire ---")
#         cleaned_data = super().clean()
#         print(f"Données nettoyées: {cleaned_data}")
        
#         date_sortieC = cleaned_data.get('date_sortieC')
#         heure_sortieC = cleaned_data.get('heure_sortieC')
#         instance = getattr(self, 'instance', None)
        
#         print(f"Instance: {instance}")
#         print(f"Date entrée: {getattr(instance, 'date_entreeC', None)}")
#         print(f"Heure entrée: {getattr(instance, 'heure_entreeC', None)}")
#         print(f"Date sortie: {date_sortieC}")
#         print(f"Heure sortie: {heure_sortieC}")
        
#         if date_sortieC is None or heure_sortieC is None:
#             error_msg = 'Les champs date et heure de sortie sont obligatoires'
#             print(f"Erreur de validation: {error_msg}")
#             self.add_error('date_sortieC', error_msg)
#             self.add_error('heure_sortieC', '')
            
#         print("Fin du nettoyage des données")
#         return cleaned_data


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
