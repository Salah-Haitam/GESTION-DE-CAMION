from django.contrib import admin
from .models import chauffeur, camion, Affectation, prestataire , Utilisateur, EntreeSortie

admin.site.register(EntreeSortie)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('id_user','username','password', 'is_admin')  # colonnes visibles
    search_fields = ('id_user','username','password', 'is_admin' )  # barre de recherche
    list_filter = ('is_admin',)  # filtre par statut admin
admin.site.register(Utilisateur, UtilisateurAdmin)
class ChauffeurAdmin(admin.ModelAdmin):

    list_display  = ('id_chauffeur','nom_chauffeur', 'prenom_chauffeur', 'permis_chauffeur', 'qr_code')  # colonnes visibles
    search_fields = ('id_chauffeur','nom_chauffeur', 'prenom_chauffeur', 'permis_chauffeur', 'qr_code')  # barre de recherche
    list_filter   = ('id_chauffeur','nom_chauffeur', 'prenom_chauffeur', 'permis_chauffeur', 'qr_code')  # filtre par nom

admin.site.register(chauffeur, ChauffeurAdmin)

class CamionAdmin(admin.ModelAdmin):

    list_display  = ('id_camion', 'id_chauffeur', 'matricule_camion', 'capacite')  # colonnes visibles
    search_fields = ('id_camion', 'id_chauffeur__nom_chauffeur', 'matricule_camion')  # barre de recherche
    list_filter   = ('id_chauffeur__nom_chauffeur', 'matricule_camion')  

admin.site.register(camion, CamionAdmin)

class prestataireAdmin(admin.ModelAdmin):
    list_display  = ('id_prestataire', 'nom_prestataire', 'adresse_prestataire', 'frais_prestataire', 'telephone_prestataire', 'qr_code')  # colonnes visibles
    search_fields = ('id_prestataire', 'nom_prestataire', 'adresse_prestataire', 'frais_prestataire', 'telephone_prestataire', 'qr_code')  # barre de recherche
    list_filter   = ('id_prestataire', 'nom_prestataire', 'adresse_prestataire', 'frais_prestataire', 'telephone_prestataire', 'qr_code')  # filtre par nom

admin.site.register(prestataire, prestataireAdmin)

class AffectationAdmin(admin.ModelAdmin):
    list_display = ('id', 'chauffeur_info', 'camion_info', 'prestataire_info', 'qr_code_preview')
    list_filter = ('chauffeur', 'camion', 'prestataire')
    search_fields = ('chauffeur__nom_chauffeur', 'camion__matricule_camion', 'prestataire__nom_prestataire')
    readonly_fields = ('qr_code_preview',)

    def chauffeur_info(self, obj):
        return f"{obj.chauffeur.nom_chauffeur} {obj.chauffeur.prenom_chauffeur}"
    chauffeur_info.short_description = 'Chauffeur'  
    def camion_info(self, obj):
        return f"{obj.camion.matricule_camion}"
    camion_info.short_description = 'Camion'
    def prestataire_info(self, obj):
        return obj.prestataire.nom_prestataire if obj.prestataire else "-"
    prestataire_info.short_description = 'Prestataire'
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return f'<img src="{obj.qr_code.url}" style="max-width: 100px; max-height: 100px;" />'
        return "-"
    qr_code_preview.allow_tags = True
    qr_code_preview.short_description = 'QR Code'

admin.site.register(Affectation, AffectationAdmin)
