from django.core.files import File
from io import BytesIO
from django.db import models
from django.contrib.auth import get_user_model
import qrcode
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
import requests
from geopy.distance import geodesic




# Create your models here.


class prestataire(models.Model):
    id_prestataire = models.AutoField(primary_key=True)
    nom_prestataire = models.CharField(max_length=100)
    adresse_prestataire = models.CharField(max_length=255)
    frais_prestataire = models.DecimalField(max_digits=10, decimal_places=2)
    telephone_prestataire = models.CharField(max_length=15, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    def save(self, *args, **kwargs):
        # Génère les données à encoder
        data = f"ID: {self.id_prestataire}\n" \
           f"Nom: {self.nom_prestataire}\n" \
           f"Adresse: {self.adresse_prestataire}\n" \
           f"Téléphone: {self.telephone_prestataire}\n" \
           f"Frais: {self.frais_prestataire}\n" \
    #        "Chauffeurs:\n"
    
        # Récupère tous les chauffeurs associés à ce prestataire
        #     from .models import chauffeur
        #     chauffeurs = chauffeur.objects.filter(prestataire=self)
    
        #     for ch in chauffeurs:
        #         data += f"- {ch.nom_chauffeur} {ch.prenom_chauffeur}\n"
    
        # Crée le QR code
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        file_name = f"qr_{self.nom_prestataire}.png"
        self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)
    
    @property
    def get_prestataire(self):
        return self.prestataire
    
    def __str__(self):
        return self.nom_prestataire

class chauffeur(models.Model):
    id_chauffeur = models.AutoField(primary_key=True)
    nom_chauffeur = models.CharField(max_length=50)
    prenom_chauffeur = models.CharField(max_length=50)
    permis_chauffeur = models.CharField(max_length=20, unique=True)
    prestataire = models.ForeignKey('prestataire', on_delete=models.CASCADE, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    @property
    def get_id_chauffeur(self):
        return self.id_chauffeur    
    @property
    def get_nom_chauffeur(self):
        return self.nom_chauffeur    
    @property
    def get_prenom_chauffeur(self):
        return self.prenom_chauffeur   
    @property
    def get_permis_chauffeur(self):
        return self.permis_chauffeur 
    def camion_actuel(self):
        affectation = self.affectation_set.filter(date_fin__isnull=True).first()
        return affectation.camion if affectation else None
    @property
    def get_chauffeur(self):
        return self.chauffeur
    def __str__(self):
        return f"{self.nom_chauffeur} {self.prenom_chauffeur}"
    

class camion(models.Model):
    id_camion = models.AutoField(primary_key=True)
    id_chauffeur = models.ForeignKey('chauffeur', on_delete=models.CASCADE)
    id_prestataire = models.ForeignKey('prestataire', on_delete=models.SET_NULL, null=True, blank=True)
    matricule_camion = models.CharField(max_length=20, unique=True)
    capacite = models.DecimalField(max_digits=10, decimal_places=2)
    
    
    
    def clean(self):
        pass
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def calculer_temps_utilisation(self):
        if not self.date_sortieC or not self.heure_sortieC:
            return 'En attente'
        
        # Calculer la durée en combinant date et heure
        entree = datetime.combine(self.date_entreeC, self.heure_entreeC)
        sortie = datetime.combine(self.date_sortieC, self.heure_sortieC)
        
        # Calculer la différence
        duree = sortie - entree
        
        # Calculer les composants du temps
        total_seconds = duree.total_seconds()
        jours = int(total_seconds // (24 * 3600))
        heures = int((total_seconds % (24 * 3600)) // 3600)
        minutes = int((total_seconds % 3600) // 60)
        secondes = int(total_seconds % 60)
        
        # Assurer que toutes les valeurs sont positives
        if jours < 0: jours = 0
        if heures < 0: heures = 0
        if minutes < 0: minutes = 0
        if secondes < 0: secondes = 0
        
        return {
            'jours': jours,
            'heures': heures,
            'minutes': minutes,
            'secondes': secondes,
            'total_heures': int(total_seconds // 3600),
            'duree_totale': str(duree)
        }
    def __str__(self):
        return f"{self.matricule_camion} - {self.id_prestataire}"



class Affectation(models.Model):
    id = models.AutoField(primary_key=True)
    chauffeur = models.ForeignKey('chauffeur', on_delete=models.CASCADE)
    camion = models.ForeignKey('camion', on_delete=models.CASCADE)
    prestataire = models.ForeignKey('prestataire', on_delete=models.CASCADE, null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Sauvegarde initiale pour générer un ID
        if is_new:
            super().save(*args, **kwargs)

        # Affecte automatiquement le prestataire si non défini
        if not self.prestataire and hasattr(self.camion, 'id_prestataire'):
            self.prestataire = self.camion.id_prestataire

        # Génération du QR code
        data = f"ID: {self.id}\n" \
           f"Chauffeur: {getattr(self.chauffeur, 'nom_chauffeur', '')} {getattr(self.chauffeur, 'prenom_chauffeur', '')}\n" \
           f"Permis: {getattr(self.chauffeur, 'permis_chauffeur', '')}\n" \
           f"Camion: {getattr(self.camion, 'matricule_camion', '')}\n" \
           f"Capacité: {getattr(self.camion, 'capacite', '')}\n"\
           

        if self.prestataire:
            data += (
                f"\nPrestataire: {self.prestataire.nom_prestataire}\n"
                f"Adresse: {self.prestataire.adresse_prestataire}\n"
                f"Téléphone: {self.prestataire.telephone_prestataire}\n"
                f"Frais: {self.prestataire.frais_prestataire}"
        )

        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Supprime l'ancien QR code
        if self.qr_code:
            self.qr_code.delete(save=False)

        filename = f'qr_affectation_{self.chauffeur.nom_chauffeur}_{self.chauffeur.prenom_chauffeur}_{self.camion.matricule_camion}.png'
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

        # Sauvegarde finale avec le QR code
        super().save(*args, **kwargs) 
    def __str__(self):
        return f"{self.chauffeur} -> {self.camion} ({self.prestataire or 'Aucun prestataire'})"


class Utilisateur(models.Model):
    id_user = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    is_admin = models.BooleanField(default=False)
    site = models.ForeignKey('site', on_delete=models.CASCADE, null=True, blank=True)
    def get_is_admin(self):
        return self.is_admin
    def get_username(self):
        return self.username
    def __str__(self):
        return self.username

class EntreeSortie(models.Model):
    id_entreeSortie = models.AutoField(primary_key=True)
    affectation = models.ForeignKey('Affectation', on_delete=models.CASCADE)
    date_entree = models.DateField()
    date_sortie = models.DateField(blank=True, null=True)
    heure_entree = models.TimeField()
    heure_sortie = models.TimeField(blank=True, null=True)
    def clean(self):
        super().clean()
        # Vérifier que toutes les dates et heures nécessaires sont présentes
        if not self.date_entree or not self.heure_entree:
            raise ValidationError('Les dates et heures d\'entrée sont requises')
            
        if self.date_sortie is not None and self.heure_sortie is not None:
            # Vérifier si la date de sortie est antérieure à la date d'entrée
            if self.date_sortie < self.date_entree:
                raise ValidationError('La date de sortie ne peut pas être antérieure à la date d\'entrée')
            
            # Vérifier si la date de sortie est égale mais l'heure de sortie est antérieure
            elif self.date_sortie == self.date_entree and self.heure_sortie < self.heure_entree:
                raise ValidationError('L\'heure de sortie ne peut pas être antérieure à l\'heure d\'entrée')
            
            # Vérifier si la date de sortie est la même mais l'heure est égale
            elif self.date_sortie == self.date_entree and self.heure_sortie == self.heure_entree:
                raise ValidationError('La date et l\'heure de sortie ne peuvent pas être identiques à la date et l\'heure d\'entrée')

class site(models.Model):
    id_site = models.AutoField(primary_key=True)
    nom_site = models.CharField(max_length=150)
    adresse_site = models.CharField(max_length=150)
    telephone_site = models.CharField(max_length=11)

    def __str__(self):
        return self.nom_site
    

class Facture(models.Model):
    id_facture = models.AutoField(primary_key=True)
    affectation = models.ForeignKey('Affectation', on_delete=models.CASCADE, related_name='factures')
    poids_marchandise = models.FloatField(validators=[MinValueValidator(0.1)], help_text="Poids en tonnes")
    destination = models.CharField(max_length=200)
    
    # Coordonnées de départ (position actuelle GPS)
    latitude_depart = models.FloatField(null=True, blank=True, help_text="Laisser vide pour utiliser la position GPS actuelle")
    longitude_depart = models.FloatField(null=True, blank=True, help_text="Laisser vide pour utiliser la position GPS actuelle")
    
    # Coordonnées de destination (automatiquement calculées)
    latitude_destination = models.FloatField(null=True, blank=True, help_text="Rempli automatiquement à partir de l'adresse de destination")
    longitude_destination = models.FloatField(null=True, blank=True, help_text="Rempli automatiquement à partir de l'adresse de destination")
    
    # Distance calculée automatiquement
    distance_km = models.FloatField(null=True, blank=True, default=0, help_text="Distance en kilomètres, calculée automatiquement")
    
    frais_marchandise = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    prix_par_km = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    prix_par_tonne = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    date_facture = models.DateField(auto_now_add=True)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        ordering = ['-date_facture']
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'

    def __str__(self):
        return f"Facture {self.id_facture} - {self.affectation} - {self.date_facture}"

    def clean(self):
        super().clean()
        if self.poids_marchandise > self.affectation.camion.capacite:
            raise ValidationError({
                'poids_marchandise': f"Le poids ({self.poids_marchandise} t) dépasse la capacité du camion ({self.affectation.camion.capacite} t)"
            })

    def geocoder_destination(self):
        """Géocode l'adresse de destination pour obtenir les coordonnées"""
        if not self.destination:
            return None, None
            
        try:
            # Utilisation de l'API Nominatim (OpenStreetMap) - gratuite
            url = f"https://nominatim.openstreetmap.org/search?q={self.destination}&format=json&limit=1"
            headers = {'User-Agent': 'YourAppName/1.0'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    lat = float(data[0]['lat'])
                    lon = float(data[0]['lon'])
                    return lat, lon
        except Exception as e:
            print(f"Erreur géocodage: {e}")
        
        return None, None

    def calculer_distance(self):
        """Calcule la distance entre les coordonnées de départ et de destination"""
        if all([self.latitude_depart, self.longitude_depart, 
                self.latitude_destination, self.longitude_destination]):
            
            depart = (self.latitude_depart, self.longitude_depart)
            destination = (self.latitude_destination, self.longitude_destination)
            
            # Calcul de la distance en kilomètres
            distance = geodesic(depart, destination).kilometers
            return round(distance, 2)
        
        return 0

    def save(self, *args, **kwargs):
        # Géocoder la destination si pas encore fait
        if self.destination and not (self.latitude_destination and self.longitude_destination):
            try:
                lat, lon = self.geocoder_destination()
                if lat and lon:
                    self.latitude_destination = lat
                    self.longitude_destination = lon
            except Exception as e:
                print(f"Erreur lors du géocodage: {e}")

        # Calculer la distance si les coordonnées sont disponibles
        try:
            if all([self.latitude_depart, self.longitude_depart, 
                   self.latitude_destination, self.longitude_destination]):
                self.distance_km = self.calculer_distance()
            else:
                self.distance_km = 0
        except Exception as e:
            print(f"Erreur lors du calcul de la distance: {e}")
            self.distance_km = 0

        # Calculer les frais même si la distance est 0
        try:
            self.calculer_frais()
        except Exception as e:
            print(f"Erreur lors du calcul des frais: {e}")
            self.frais_marchandise = 0
            self.montant_total = 0

        try:
            self.full_clean()
        except ValidationError as e:
            print(f"Erreur de validation: {e}")
            raise

        super().save(*args, **kwargs)

    def calculer_frais(self):
        """Calcule automatiquement les frais et le montant total de la facture."""
        if not all([self.poids_marchandise, self.prix_par_tonne, self.prix_par_km]):
            return

        # Calcul des frais de transport basé sur la distance GPS
        distance = self.distance_km or 0
        frais_transport = distance * float(self.prix_par_km)

        # Calcul des frais de marchandise
        frais_marchandise = float(self.poids_marchandise) * float(self.prix_par_tonne)

        from decimal import Decimal, ROUND_HALF_UP
        self.frais_marchandise = Decimal(frais_marchandise).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        montant_total = Decimal(frais_marchandise + frais_transport).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.montant_total = montant_total

