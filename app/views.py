from io import BytesIO
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import chauffeur, camion, prestataire, Affectation, Utilisateur, EntreeSortie, site, Facture
from .forms import ChauffeurForm, CamionForm, RechercheCamionForm, PrestataireForm, BadgeForm,NouveauPrestataireForm, UserForm ,FactureForm
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import base64
from datetime import datetime, timedelta
import pytz
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from weasyprint import CSS
import json




# Create your views here.   
def afficher_message(request):
    return render(request, 'index.html')


def ajouter_chauffeur(request):
    if request.method == 'POST':
        form = ChauffeurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('success_message')}?chauffeur=true")
    else:
        form = ChauffeurForm()
    return render(request, 'ajouter_chauffeur.html', {'form': form})

def afficher_chauffeurs(request):
    chauffeurs = chauffeur.objects.all()
    return render(request, 'afficher_chauffeur.html', {'chauffeurs': chauffeurs, 'masquer_boutons': True})


def afficher_prestataires(request):   
    prestataires = prestataire.objects.all()
    return render(request, 'afficher_prestataire.html', {'prestataires': prestataires, 'masquer_boutons': True})
def ajouter_camion(request):
    if request.method == 'POST':
        form = CamionForm(request.POST, request.FILES)
        formf = NouveauPrestataireForm(request.POST, request.FILES)
        creer_nouveau = request.POST.get('creer_nouveau_prestataire') == 'on'
        
        if creer_nouveau:
            if formf.is_valid() and form.is_valid():
                nouveau_prestataire = formf.save()
                camion_obj = form.save(commit=False)
                camion_obj.id_prestataire = nouveau_prestataire
                camion_obj.save()
                
                # Création de l'affectation si un chauffeur est spécifié
                if camion_obj.id_chauffeur:
                    affectation = Affectation(
                        chauffeur=camion_obj.id_chauffeur,
                        camion=camion_obj,
                        prestataire=nouveau_prestataire
                    )
                    affectation.save()  # Cela va générer le QR code
                    
                messages.success(request, 'Camion et prestataire ajoutés avec succès !')
                return redirect('afficher_camions')
        else:
            if form.is_valid():
                camion_obj = form.save()
                
                # Création de l'affectation si un chauffeur est spécifié
                if camion_obj.id_chauffeur:
                    affectation = Affectation(
                        chauffeur=camion_obj.id_chauffeur,
                        camion=camion_obj,
                        prestataire=camion_obj.id_prestataire
                    )
                    affectation.save()  # Cela va générer le QR code
                    
                messages.success(request, 'Camion ajouté avec succès !')
                return redirect('afficher_camions')
    else:
        form = CamionForm()
        formf = NouveauPrestataireForm()
    
    return render(request, 'ajouter_camion.html', {
        'form': form,
        'formf': formf,
    })
# def ajouter_camion(request):
#     if request.method == 'POST':
#         form = CamionForm(request.POST)
#         formf = NouveauPrestataireForm(request.POST)
#         if form.is_valid():
#             form.save()
#             if not formf.is_valid():
#                 formf.save()
#             elif formf.is_valid():
#                 formf.save()
#         return redirect(f"{reverse('success_message')}?camion=true")
#     else:
#         form = CamionForm()
#         formf = NouveauPrestataireForm()
#     return render(request, 'ajouter_camion.html', {'form': form, 'prestataire_form': formf})

def afficher_camions(request):
    form = RechercheCamionForm(request.GET)
    
    # Récupérer tous les camions d'abord
    camions = camion.objects.all().select_related('id_chauffeur')
    
    # Récupérer les camions qui ont une entrée de sortie complétée
    camions_avec_sortie = EntreeSortie.objects.filter(
        date_sortie__isnull=False,
        heure_sortie__isnull=False
    ).select_related('affectation__camion')
    
    # Si on a des entrées de sortie, on filtre les camions
    if camions_avec_sortie.exists():
        camions_ids = camions_avec_sortie.values_list('affectation__camion_id', flat=True).distinct()
        camions = camions.filter(id_camion__in=camions_ids)
    
    # Appliquer les filtres si la recherche est valide
    if form.is_valid():
        if form.cleaned_data['id_chauffeur']:
            camions = camions.filter(id_chauffeur_id=form.cleaned_data['id_chauffeur'])
        if form.cleaned_data['matricule_camion']:
            camions = camions.filter(matricule_camion__icontains=form.cleaned_data['matricule_camion'])
    
    return render(request, 'afficher_camion.html', {
        'form': form,
        'camions': camions,
        'masquer_boutons': True,
        'debug': {
            'total_camions': camion.objects.count(),
            'total_entrees_sorties': EntreeSortie.objects.count(),
            'entrees_avec_sortie': camions_avec_sortie.count(),
            'camions_trouves': camions.count()
        }
    })

def afficher_camions_Nsortie(request):
    form = RechercheCamionForm(request.GET)
    
    # Récupérer tous les camions d'abord
    camions = camion.objects.all().select_related('id_chauffeur')
    
    # Récupérer les camions qui ont une entrée sans sortie
    entrees_sans_sortie = EntreeSortie.objects.filter(
        date_sortie__isnull=True,
        heure_sortie__isnull=True
    ).select_related('affectation__camion')
    
    # Si on a des entrées sans sortie, on filtre les camions
    if entrees_sans_sortie.exists():
        camions_ids = entrees_sans_sortie.values_list('affectation__camion_id', flat=True).distinct()
        camions = camions.filter(id_camion__in=camions_ids)
    
    # Appliquer les filtres si la recherche est valide
    if form.is_valid():
        if form.cleaned_data['id_chauffeur']:
            camions = camions.filter(id_chauffeur_id=form.cleaned_data['id_chauffeur'])
        if form.cleaned_data['matricule_camion']:
            camions = camions.filter(matricule_camion__icontains=form.cleaned_data['matricule_camion'])
    
    return render(request, 'afficher_camion_Nsortie.html', {
        'form': form,
        'camions': camions,
        'masquer_boutons': True,
        'debug': {
            'total_camions': camion.objects.count(),
            'total_entrees_sorties': EntreeSortie.objects.count(),
            'entrees_sans_sortie': entrees_sans_sortie.count(),
            'camions_trouves': camions.count()
        }
    })

def interface_admin(request):
    chauffeurs = chauffeur.objects.all()
    camions = camion.objects.all()
    prestataires = prestataire.objects.all()
    utilisateurs = Utilisateur.objects.all()

    return render(request, 'interface_admin.html', {
        'chauffeurs': chauffeurs,
        'camions': camions,
        'prestataires': prestataires,
        'utilisateurs': utilisateurs,
 
    })



def logout_view(request):
    logout(request)
    return redirect('login_couverture')  # à remplacer par ta page d'accueil

def login_couverture(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authentification standard Django
        user = authenticate(request, username=username, password=password)

        # Authentification personnalisée via ta table Utilisateur
        utilisateur = Utilisateur.objects.filter(username=username, password=password).first()

        if user and user.is_staff:
            login(request, user)
            return render(request, 'index.html')

        elif utilisateur:
            # Stocker l'ID de l'utilisateur dans la session
            request.session['utilisateur_id'] = utilisateur.id_user
            request.session['username'] = utilisateur.username
            request.session['is_admin'] = utilisateur.is_admin

            if utilisateur.is_admin:
                return render(request, 'index.html')
            else:
                return redirect('acceuil')  # ou une autre page utilisateur normal

        else:
            # Aucun des deux utilisateurs authentifié
            return render(request, 'login.html', {
                'form': {'errors': True},
                'message': "Nom d'utilisateur ou mot de passe incorrect."
            })

    return render(request, 'login_couverture.html')

def acceuil_view(request):
    camions = camion.objects.all()
    chauffeurs = chauffeur.objects.all()
    prestataires = prestataire.objects.all()
    affectations = Affectation.objects.all()
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'acceuil.html', {
        'camions': camions,
        'chauffeurs': chauffeurs,
        'prestataires': prestataires,
        'affectations': affectations,
        'utilisateurs': utilisateurs,
        })
def afficher_tous_les_camions(request):
    camions = camion.objects.all()
    return render(request, 'afficher_camion.html', {
        'camions': camions,
    })
def couverture_view(request):
    return render(request, 'couverture.html')
def sortie_camion(request, id_camion):
    print(f"\n=== DEBUT sortie_camion pour le camion ID: {id_camion} ===")
    print(f"Méthode HTTP: {request.method}")
    camion_obj = get_object_or_404(camion, id_camion=id_camion)
    print(f"Camion trouvé: {camion_obj.matricule_camion} - {camion_obj.nom_societe}")
    
    if request.method == 'POST':
        print("\n--- Traitement POST ---")
        print(f"Données POST: {request.POST}")
        form = SortieCamionForm(request.POST, instance=camion_obj)
        print(f"Formulaire valide: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"Erreurs de formulaire: {form.errors}")
            
        if form.is_valid():
            print("Formulaire valide, traitement en cours...")
            try:
                # Mettre à jour les champs de sortie
                print("\n--- Mise à jour des champs de sortie ---")
                print(f"Avant - date_sortieC: {camion_obj.date_sortieC}, heure_sortieC: {camion_obj.heure_sortieC}")
                
                camion_obj.date_sortieC = form.cleaned_data['date_sortieC']
                camion_obj.heure_sortieC = form.cleaned_data['heure_sortieC']
                
                print(f"Après - date_sortieC: {camion_obj.date_sortieC}, heure_sortieC: {camion_obj.heure_sortieC}")
                
                # Valider les données avant sauvegarde
                camion_obj.full_clean()
                
                # Sauvegarder les modifications
                print("\n--- Sauvegarde des modifications ---")
                camion_obj.save()
                print("Camion sauvegardé avec succès")
                print(f"Valeurs après sauvegarde - date_sortieC: {camion_obj.date_sortieC}, heure_sortieC: {camion_obj.heure_sortieC}")
                
                # Calculer le temps d'utilisation
                date_sortie = datetime.combine(camion_obj.date_sortieC, camion_obj.heure_sortieC)
                date_entree = datetime.combine(camion_obj.date_entreeC, camion_obj.heure_entreeC)
                temps_utilisation = date_sortie - date_entree
                
                # Formater le message de succès avec le temps d'utilisation
                jours = temps_utilisation.days
                secondes = temps_utilisation.seconds
                heures = secondes // 3600
                minutes = (secondes % 3600) // 60
                
                temps_formatte = []
                if jours > 0:
                    temps_formatte.append(f"{jours} jour{'s' if jours > 1 else ''}")
                if heures > 0:
                    temps_formatte.append(f"{heures} heure{'s' if heures > 1 else ''}")
                if minutes > 0 or not temps_formatte:  # Toujours afficher au moins les minutes
                    temps_formatte.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
                
                message_temps = ', '.join(temps_formatte)
                
                messages.success(
                    request, 
                    f'La sortie du camion {camion_obj.matricule_camion} a été enregistrée avec succès. '
                    f'Temps d\'utilisation : {message_temps}.'
                )
                
                print("\n--- Redirection ---")
                print("Redirection vers afficher_camions")
                response = redirect('afficher_camions')
                print(f"URL de redirection: {response.url}")
                print("=== FIN sortie_camion (redirection) ===\n")
                return response
                
            except ValidationError as e:
                # En cas d'erreur de validation, ajouter les erreurs au formulaire
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"Erreur : {error}")
    else:
        form = SortieCamionForm(instance=camion_obj)
        # Pré-remplir la date et l'heure actuelles
        form.fields['date_sortieC'].initial = timezone.now().date()
        form.fields['heure_sortieC'].initial = timezone.now().time()
    
    print("\n--- Affichage du formulaire ---")
    print(f"Méthode: {request.method}")
    print(f"Formulaire initialisé: {form.initial}")
    print("=== FIN sortie_camion (affichage formulaire) ===\n")
    
    # Ajout de la variable debug au contexte
    return render(request, 'sortie_camion.html', {
        'camion': camion_obj,
        'form': form,
        'debug': settings.DEBUG  # Ajout de la variable debug
    })
def success(request):
    context = {}
    
    # Déterminer le contexte en fonction du referer
    referer = request.META.get('HTTP_REFERER', '')
    if 'ajouter_chauffeur' in referer or 'chauffeur' in request.GET:
        context['chauffeur'] = True
    elif 'ajouter_camion' in referer or 'sortie_camion' in referer or 'camion' in request.GET:
        context['camion'] = True
    elif 'ajouter_prestataire' in referer or 'prestataire' in request.GET:
        context['prestataire'] = True
    
    # Si un message est passé en paramètre GET
    if 'message' in request.GET:
        context['message'] = request.GET.get('message')
    
    return render(request, 'success_message.html', context)
# Les fonctions suivantes sont commentées et ne sont pas utilisées
def generate_pdf_view(request):
    pass

def ticket_pdf(request, chauffeur_id):
    pass

def modifier_chauffeur(request, id_chauffeur):
    chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=id_chauffeur)
    if request.method == 'POST':
        if 'delete' in request.POST:
            chauffeur_obj.delete()
            return redirect('success_message')
        
        form = ChauffeurForm(request.POST, instance=chauffeur_obj)
        if form.is_valid():
            form.save()
            return redirect('success_message')
    else:
        form = ChauffeurForm(instance=chauffeur_obj)
    return render(request, 'modifier_chauffeur.html', {'form': form})

def modifier_camion(request, id_camion):
    camion_obj = get_object_or_404(camion, id_camion=id_camion)
    if request.method == 'POST':
        if 'delete' in request.POST:
            camion_obj.delete()
            return redirect('success_message')
        form = CamionForm(request.POST, instance=camion_obj)
        if form.is_valid():
            form.save()
            return redirect('success_message')
    else:
        form = CamionForm(instance=camion_obj)
    return render(request, 'modifier_camion.html', {'form': form})

def ajouter_prestataire(request):
    if request.method == 'POST':
        form = PrestataireForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('success_message')}?prestataire=true")
    else:
        form = PrestataireForm()
    return render(request, 'ajouter_prestataire.html', {'form': form})

def modifier_prestataire(request, id_prestataire):
    prestataire_obj = get_object_or_404(prestataire, id_prestataire=id_prestataire)
    if request.method == 'POST':
        if 'delete' in request.POST:
            prestataire_obj.delete()
            return redirect('success_message')
        form = PrestataireForm(request.POST, instance=prestataire_obj)
        if form.is_valid():
            form.save()
            return redirect('success_message')
    else:
        form = PrestataireForm(instance=prestataire_obj)
    return render(request, 'modifier_prestataire.html', {'form': form})

def genere_bdg(request):
    if request.method == 'POST':
        form = BadgeForm(request.POST)
        if form.is_valid():
            chauffeur_obj = form.cleaned_data['chauffeur']
            affectation = Affectation.objects.filter(chauffeur=chauffeur_obj).first()
            # Récupérer tous les camions associés à ce chauffeur
            camions = camion.objects.filter(id_chauffeur=chauffeur_obj)
            
            return render(request, 'genere_bdg.html', {
                'form': form,
                'chauffeur': chauffeur_obj,
                'camions': camions,  # Envoyer la liste des camions
                'prestataire': chauffeur_obj.prestataire if hasattr(chauffeur_obj, 'prestataire') else None,
                'affectation': affectation,
                'show_badge': True
            })
    else:
        form = BadgeForm()
    return render(request, 'genere_bdg.html', {'form': form, 'show_badge': False})
    
# def badge_pdf(request, chauffeur_id):
#     chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)
#     camions = camion.objects.filter(id_chauffeur=chauffeur_obj)
#     prestataire = chauffeur_obj.prestataire if hasattr(chauffeur_obj, 'prestataire') else None
    
#     return render(request, 'badge_pdf.html', {
#         'chauffeur': chauffeur_obj,
#         'camions': camions,
#         'prestataire': prestataire,
#         'request': request  # Important pour les URLs absolues
#     })

def badge_pdf(request, chauffeur_id):
    chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)
    # Récupérer la dernière affectation du chauffeur
    affectation = Affectation.objects.filter(chauffeur=chauffeur_obj).order_by('-id').first()
    
    return render(request, 'badge_pdf.html', {
        'chauffeur': chauffeur_obj,
        'affectation': affectation,
        'request': request  # Important pour les URLs absolues
        

    })
def download_badge_pdf(request, chauffeur_id):
    # Récupération des données
    chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)
    affectation = Affectation.objects.filter(chauffeur=chauffeur_obj).order_by('-id').first()
    
    import base64
    import os
    from django.conf import settings

    # Encoder le logo en base64
    logo_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'app', 'images', 'logo.png')
    logo_base64 = ''
    try:
        with open(logo_path, 'rb') as f:
            logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    except Exception:
        logo_base64 = ''

    # Encoder le QR code en base64
    qr_code_base64 = ''
    if affectation and affectation.qr_code and affectation.qr_code.path:
        try:
            with open(affectation.qr_code.path, 'rb') as f:
                qr_code_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            qr_code_base64 = ''

    # Rendu du contenu du badge avec images base64
    badge_content = render_to_string('badge_pdf.html', {
        'chauffeur': chauffeur_obj,
        'affectation': affectation,
        'request': request,
        'is_pdf': True,
        'logo_base64': logo_base64,
        'qr_code_base64': qr_code_base64
    })
    
    # Configuration de la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="badge_{chauffeur_obj.nom_chauffeur}.pdf"'
    
    # Options de conversion HTML vers PDF
    pdf_options = {
        'encoding': 'UTF-8',
        'presentational_hints': True
    }
    
    # Configuration de base_url pour résoudre les URLs statiques
    base_url = request.build_absolute_uri('/')[:-1]  # Retire le slash final
    
    # Génération du PDF
    HTML(
        string=badge_content,
        base_url=base_url
    ).write_pdf(
        response,
        stylesheets=[
            CSS(string='''
                @page {
                    size: A4;
                    margin: 15mm 10mm;
                }
                body {
                    margin: 0;
                    padding: 0;
                    -webkit-print-color-adjust: exact;
                }
                .badge-container {
                    margin: 0 auto;
                    width: 100%;
                    height: 100%;
                    page-break-inside: avoid;
                }
            ''')
        ],
        **pdf_options
    )
    
    return response

# def download_badge_pdf(request, chauffeur_id):
#     chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)
#     # Récupérer la dernière affectation du chauffeur
#     affectation = Affectation.objects.filter(chauffeur=chauffeur_obj).order_by('-id').first()
    
#     # Rendu du template
#     html_string = render_to_string('badge_pdf.html', {
#         'chauffeur': chauffeur_obj,
#         'affectation': affectation,
#         'static': 'app/static'  # Chemin vers les fichiers statiques si nécessaire
#     })
    
#     # Création du PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="badge_{chauffeur_obj.nom_chauffeur}.pdf"'
    
#     # Génération du PDF avec WeasyPrint
#     HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    
#     return response

# awel vue dia download_badge_pdf
# def download_badge_pdf(request, chauffeur_id):
#     chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)
#     camions = camion.objects.filter(id_chauffeur=chauffeur_obj)
#     prestataire = chauffeur_obj.prestataire if hasattr(chauffeur_obj, 'prestataire') else None
    
#     # Rendu du template
#     html_string = render_to_string('badge_pdf.html', {
#         'chauffeur': chauffeur_obj,
#         'camions': camions,
#         'prestataire': prestataire,
#         'static': 'app/static'  # Chemin vers les fichiers statiques si nécessaire
#     })
    
#     # Création du PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="badge_{chauffeur_obj.nom_chauffeur}.pdf"'
    
#     # Génération du PDF avec WeasyPrint
#     HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    
#     return response

def get_chauffeur_info(request):
    if request.method == 'GET' and 'chauffeur_id' in request.GET:
        try:
            chauffeur_obj = chauffeur.objects.get(id_chauffeur=request.GET['chauffeur_id'])
            data = {
                'success': True,
                'nom_chauffeur': chauffeur_obj.nom_chauffeur,
                'prenom_chauffeur': chauffeur_obj.prenom_chauffeur,
                'qr_code_url': chauffeur_obj.qr_code.url if chauffeur_obj.qr_code else None
            }
            return JsonResponse(data)
        except chauffeur.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Chauffeur non trouvé'})
    return JsonResponse({'success': False, 'error': 'Requête invalide'})


def afficher_affectations(request):
    # Récupérer toutes les affectations avec les relations nécessaires
    affectations = Affectation.objects.select_related('chauffeur', 'camion', 'prestataire').all()
    
    # Trier par date de création (la plus récente en premier)
    affectations = affectations.order_by('-id')
    
    return render(request, 'afficher_affectation.html', {
        'affectations': affectations,
        'masquer_boutons': True
    })

def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('success_message')}?user=true")
    else:
        form = UserForm()
    return render(request, 'ajouter_utilisateur.html', {'form': form})

def afficher_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'afficher_utilisateur.html', {'utilisateurs': utilisateurs, 'masquer_boutons': True})

def modifier_utilisateur(request, id_user):
    utilisateur_obj = get_object_or_404(Utilisateur, id_user=id_user)
    
    if request.method == 'POST':
        if 'delete' in request.POST:
            utilisateur_obj.delete()
            return redirect('success_message')
        form = UserForm(request.POST, instance=utilisateur_obj)
        if form.is_valid():
            form.save()
            return redirect('success_message')
    else:
        form = UserForm(instance=utilisateur_obj)
    return render(request, 'modifier_utilisateur.html', {'form': form})



# def download_zpl(request, chauffeur_id): 
#     chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)

#     # Données QR code
#     qr_data = f"NOM: {chauffeur_obj.nom_chauffeur}\n PRENOM: {chauffeur_obj.prenom_chauffeur}\n ID: {chauffeur_obj.id_chauffeur}"

#     # Contenu ZPL
#     zpl_content = f"""^XA
# ^CI28
# ^MMT
# ^PW609
# ^LL0600
# ^LS0

# ^FX Logo Super Cerame (centré en haut)
# ^FO-350,30
# ^GFA,6525,6525,29,,:::::::::::::::::::::::::::::::::::gT03,gS01F8,gS0FF8,gR03FFC,gQ01IFC,gQ0JFC,gP03JFE,gO01KFE,gO07LF,gO0MF,gN01MF,gN03MF04,gN0NF04,gM01NF06,gM03NF06,gM07NF07,gM0OF07,gL01OF078,gL03NFE0F8,gL0OFE0FC,gK01OFE0FC,gK03OFE0FE,gK07OFE0FE,gK0PFE0FF,gJ01PFE0FF,gJ03PFE0FF8,gJ0QFE0FF8,gI01QFE0FF8,gI03QFE0FFC,gI07QF80FFE,gI0QFI07FE,gH01PFJ07FE,gH03OFI0183FF,gH07NFJ0383FF,gG01MFEK07C3FF8,gG03LFEK01FC1FF8,g01LFEL03FE1FFC,g07KFEM0FFE0FFC,Y01KFEM01IF0FFE,Y07JFCN03IF0FFE,X03JFEO0JF87FE,X0JFCO01JF87FE,W03IF8P07JFC3FE,W0IFCQ0KFC3FE,V07FFCQ01KFC1FE,U01FF8R07KFE1FE,U07F8S0LFE1FE,T01F8S01MF0FE,T0FU07MF0FE,S038U0NF87E,S04U03NF87F,gO07NFC3F,gO0OFC3F,gN03OFC3F,gN07OFE1F,R0FT01PFE1F,R07FS03QF0F,R07FFR07QF0F,R07IF8O01RF8F,R03JF8N03RF87,R03KFCM0SFC7,R03LFCK01SFC3,R01MFCJ03SFE3,R01NFEI0TFE1,R01OFE00TFE18,S0OFEI03SF18,S0OFCK0RF08,S0OF0701I03PF88,S07MFE0F8L07NF8,S07MF81FCM01MFC,S03MF07FFO07KFC,S03LFC0IF8O01JFE,S03LF83IFCQ03FFE,S01KFE07IFES0FE,S01KFC0KFT03,S01KF83KF8,T0JFE07KFC,T0JFC1LFE,T0JF03MF,T07FFE07MFC,T07FF81NFE,T07FF03OF,T03FC0PF8,T03F81PFC,T03F03PFE,T01C0RF,T0181RF8,V07RFE,V0TF,U01TF8,U03TFC,U01TFE,V0UF,V07TF8,V03TFC,W0UF,W07TF8,W03TFC,W01TFE,X0UF,X03TF8,X01TFC,Y0TFE,Y07TF8,Y03TFC,g0TFE,g07TF,g03TF8,g01TFC,gG07SFE,gG03TF,gG01TFC,gV04,,::::::::X03E,W01FFE,W03C0E,W07,W06,:W06I018030DFC01FC0CE,W07I018030F9E038F0FC,W0380018030E0706030F,W01F8018030C030C018E,X07F818030C018C018C,Y03E18030C018C018C,g0718030C0198018C,g0318030C019IF8C,g0318030C018CI0C,::W0E0071C070E0306I0C,W07C1E0E1F0F0707830C,W01FF807FB0DFC01FE0C,X01CI0C00C7I03,gL0C,:::X03FEK0C,X0F8FK0C,W01C,W038,W03,W06J03F819C1F808F87E00FE,W06J07FE1BC7FE0FFCFF01FF,W06J0E061E04060E0F8383018,W06I01C031CI030C07018600C,W06I0180318I030C0700C600C,W06I018011800E30C0300C400C,W06I018031807FF0C0300CC00C,W06I01IF180E070C0300CIFC,W06I01800180C030C0300CE,W03I018001818030C0300C6,W0380018001818030C0300C6,W01C001C00180C030C0300C7,X0F070E06180E0F0C0300C3818,X07FE07FE1807FB0C0300C1FF8,Y0F800FJ01EO03C,,:::::::::::::::::::::^FS

# ^FX Titre centré
# ^FO180,160^A0N,40,40^FB300,1,0,L^FDBADGE^FS

# ^FX QR Code
# ^FO350,300^BQN,2,6^FDQA,{qr_data}^FS

# ^FX Infos chauffeur
# ^FO50,360^A0N,28,28^FD{chauffeur_obj.nom_chauffeur} {chauffeur_obj.prenom_chauffeur}^FS
# ^FO50,400^A0N,20,20^FDID: {chauffeur_obj.id_chauffeur}^FS
# ^FO50,430^A0N,20,20^FDPermis: {chauffeur_obj.permis_chauffeur}^FS

# ^XZ"""

#     filename = f"badge_{chauffeur_obj.id_chauffeur}.zpl"
#     response = HttpResponse(zpl_content, content_type='application/octet-stream')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     return response


def download_zpl(request, chauffeur_id): 
    chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)

    # Récupérer la dernière affectation du chauffeur (la plus récente)
    affectation = Affectation.objects.filter(chauffeur=chauffeur_obj).order_by('-id').first()

    # Déterminer le QR code à utiliser
    if affectation and affectation.qr_code:
        qr_image_url = affectation.qr_code.url
        qr_data = f"AFFECTATION: {affectation.id}\n" \
            f"CHAUFFEUR: \n ID : {affectation.chauffeur.id_chauffeur}\n"\
            f"NOM :{affectation.chauffeur.nom_chauffeur} \n"\
            f"PRENOM :{affectation.chauffeur.prenom_chauffeur}\n"\
            f"CAMION :\n MATRICULE :{affectation.camion.matricule_camion}\n"\
            f"PRESTATAIRE : \n ID : {affectation.prestataire.id_prestataire}\n"\
            f"NOM : {affectation.prestataire.nom_prestataire}\n"\
            f"ADRESSE : {affectation.prestataire.adresse_prestataire}\n"\
            f"TELEPHONE : {affectation.prestataire.telephone_prestataire}\r\n"\
            f"FRAIS : {affectation.prestataire.frais_prestataire}\r\n"  # ou autre info pertinente
    elif chauffeur_obj.qr_code:
        qr_image_url = chauffeur_obj.qr_code.url
        qr_data = f"NOM: {chauffeur_obj.nom_chauffeur}\r\nPRENOM: {chauffeur_obj.prenom_chauffeur}\r\nID: {chauffeur_obj.id_chauffeur}"
    else:
        qr_data = "Aucun code QR d'affectation disponible"

    # ZPL avec les données choisies
    zpl_content = f"""^XA
^CI28
^MMT
^PW609
^LL0600
^LS0

^FX Logo Super Cerame
^FO-350,30
^GFA,6525,6525,29,,:::::::::::::::::::::::::::::::::::gT03,gS01F8,gS0FF8,gR03FFC,gQ01IFC,gQ0JFC,gP03JFE,gO01KFE,gO07LF,gO0MF,gN01MF,gN03MF04,gN0NF04,gM01NF06,gM03NF06,gM07NF07,gM0OF07,gL01OF078,gL03NFE0F8,gL0OFE0FC,gK01OFE0FC,gK03OFE0FE,gK07OFE0FE,gK0PFE0FF,gJ01PFE0FF,gJ03PFE0FF8,gJ0QFE0FF8,gI01QFE0FF8,gI03QFE0FFC,gI07QF80FFE,gI0QFI07FE,gH01PFJ07FE,gH03OFI0183FF,gH07NFJ0383FF,gG01MFEK07C3FF8,gG03LFEK01FC1FF8,g01LFEL03FE1FFC,g07KFEM0FFE0FFC,Y01KFEM01IF0FFE,Y07JFCN03IF0FFE,X03JFEO0JF87FE,X0JFCO01JF87FE,W03IF8P07JFC3FE,W0IFCQ0KFC3FE,V07FFCQ01KFC1FE,U01FF8R07KFE1FE,U07F8S0LFE1FE,T01F8S01MF0FE,T0FU07MF0FE,S038U0NF87E,S04U03NF87F,gO07NFC3F,gO0OFC3F,gN03OFC3F,gN07OFE1F,R0FT01PFE1F,R07FS03QF0F,R07FFR07QF0F,R07IF8O01RF8F,R03JF8N03RF87,R03KFCM0SFC7,R03LFCK01SFC3,R01MFCJ03SFE3,R01NFEI0TFE1,R01OFE00TFE18,S0OFEI03SF18,S0OFCK0RF08,S0OF0701I03PF88,S07MFE0F8L07NF8,S07MF81FCM01MFC,S03MF07FFO07KFC,S03LFC0IF8O01JFE,S03LF83IFCQ03FFE,S01KFE07IFES0FE,S01KFC0KFT03,S01KF83KF8,T0JFE07KFC,T0JFC1LFE,T0JF03MF,T07FFE07MFC,T07FF81NFE,T07FF03OF,T03FC0PF8,T03F81PFC,T03F03PFE,T01C0RF,T0181RF8,V07RFE,V0TF,U01TF8,U03TFC,U01TFE,V0UF,V07TF8,V03TFC,W0UF,W07TF8,W03TFC,W01TFE,X0UF,X03TF8,X01TFC,Y0TFE,Y07TF8,Y03TFC,g0TFE,g07TF,g03TF8,g01TFC,gG07SFE,gG03TF,gG01TFC,gV04,,::::::::X03E,W01FFE,W03C0E,W07,W06,:W06I018030DFC01FC0CE,W07I018030F9E038F0FC,W0380018030E0706030F,W01F8018030C030C018E,X07F818030C018C018C,Y03E18030C018C018C,g0718030C0198018C,g0318030C019IF8C,g0318030C018CI0C,::W0E0071C070E0306I0C,W07C1E0E1F0F0707830C,W01FF807FB0DFC01FE0C,X01CI0C00C7I03,gL0C,:::X03FEK0C,X0F8FK0C,W01C,W038,W03,W06J03F819C1F808F87E00FE,W06J07FE1BC7FE0FFCFF01FF,W06J0E061E04060E0F8383018,W06I01C031CI030C07018600C,W06I0180318I030C0700C600C,W06I018011800E30C0300C400C,W06I018031807FF0C0300CC00C,W06I01IF180E070C0300CIFC,W06I01800180C030C0300CE,W03I018001818030C0300C6,W0380018001818030C0300C6,W01C001C00180C030C0300C7,X0F070E06180E0F0C0300C3818,X07FE07FE1807FB0C0300C1FF8,Y0F800FJ01EO03C,,:::::::::::::::::::::^FS

^FX Titre centré
^FO80,160^A0N,40,40^FB300,1,0,L^FDBADGE^FS

^FX QR Code
^FO150,500^BQN,2,6^FDQA,{qr_data}^FS

^FX Infos chauffeur
^FO150,360^A0N,28,28^FD{chauffeur_obj.nom_chauffeur} {chauffeur_obj.prenom_chauffeur}^FS
^FO150,400^A0N,20,20^FDID: {chauffeur_obj.id_chauffeur}^FS
^FO150,430^A0N,20,20^FDPermis: {chauffeur_obj.permis_chauffeur}^FS

^XZ"""

    filename = f"badge_{chauffeur_obj.id_chauffeur}.zpl"
    response = HttpResponse(zpl_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


# def download_zpl(request, chauffeur_id): 
#     chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)

#     # Données QR code
#     qr_data = f"NOM: {chauffeur_obj.nom_chauffeur}\n PRENOM: {chauffeur_obj.prenom_chauffeur}\n ID: {chauffeur_obj.id_chauffeur}"

#     # Contenu ZPL
#     zpl_content = f"""^XA
# ^CI28
# ^MMT
# ^PW609
# ^LL0600
# ^LS0

# ^FX Logo Super Cerame (centré en haut)
# ^FO-350,30
# ^GFA,6525,6525,29,,:::::::::::::::::::::::::::::::::::gT03,gS01F8,gS0FF8,gR03FFC,gQ01IFC,gQ0JFC,gP03JFE,gO01KFE,gO07LF,gO0MF,gN01MF,gN03MF04,gN0NF04,gM01NF06,gM03NF06,gM07NF07,gM0OF07,gL01OF078,gL03NFE0F8,gL0OFE0FC,gK01OFE0FC,gK03OFE0FE,gK07OFE0FE,gK0PFE0FF,gJ01PFE0FF,gJ03PFE0FF8,gJ0QFE0FF8,gI01QFE0FF8,gI03QFE0FFC,gI07QF80FFE,gI0QFI07FE,gH01PFJ07FE,gH03OFI0183FF,gH07NFJ0383FF,gG01MFEK07C3FF8,gG03LFEK01FC1FF8,g01LFEL03FE1FFC,g07KFEM0FFE0FFC,Y01KFEM01IF0FFE,Y07JFCN03IF0FFE,X03JFEO0JF87FE,X0JFCO01JF87FE,W03IF8P07JFC3FE,W0IFCQ0KFC3FE,V07FFCQ01KFC1FE,U01FF8R07KFE1FE,U07F8S0LFE1FE,T01F8S01MF0FE,T0FU07MF0FE,S038U0NF87E,S04U03NF87F,gO07NFC3F,gO0OFC3F,gN03OFC3F,gN07OFE1F,R0FT01PFE1F,R07FS03QF0F,R07FFR07QF0F,R07IF8O01RF8F,R03JF8N03RF87,R03KFCM0SFC7,R03LFCK01SFC3,R01MFCJ03SFE3,R01NFEI0TFE1,R01OFE00TFE18,S0OFEI03SF18,S0OFCK0RF08,S0OF0701I03PF88,S07MFE0F8L07NF8,S07MF81FCM01MFC,S03MF07FFO07KFC,S03LFC0IF8O01JFE,S03LF83IFCQ03FFE,S01KFE07IFES0FE,S01KFC0KFT03,S01KF83KF8,T0JFE07KFC,T0JFC1LFE,T0JF03MF,T07FFE07MFC,T07FF81NFE,T07FF03OF,T03FC0PF8,T03F81PFC,T03F03PFE,T01C0RF,T0181RF8,V07RFE,V0TF,U01TF8,U03TFC,U01TFE,V0UF,V07TF8,V03TFC,W0UF,W07TF8,W03TFC,W01TFE,X0UF,X03TF8,X01TFC,Y0TFE,Y07TF8,Y03TFC,g0TFE,g07TF,g03TF8,g01TFC,gG07SFE,gG03TF,gG01TFC,gV04,,::::::::X03E,W01FFE,W03C0E,W07,W06,:W06I018030DFC01FC0CE,W07I018030F9E038F0FC,W0380018030E0706030F,W01F8018030C030C018E,X07F818030C018C018C,Y03E18030C018C018C,g0718030C0198018C,g0318030C019IF8C,g0318030C018CI0C,::W0E0071C070E0306I0C,W07C1E0E1F0F0707830C,W01FF807FB0DFC01FE0C,X01CI0C00C7I03,gL0C,:::X03FEK0C,X0F8FK0C,W01C,W038,W03,W06J03F819C1F808F87E00FE,W06J07FE1BC7FE0FFCFF01FF,W06J0E061E04060E0F8383018,W06I01C031CI030C07018600C,W06I0180318I030C0700C600C,W06I018011800E30C0300C400C,W06I018031807FF0C0300CC00C,W06I01IF180E070C0300CIFC,W06I01800180C030C0300CE,W03I018001818030C0300C6,W0380018001818030C0300C6,W01C001C00180C030C0300C7,X0F070E06180E0F0C0300C3818,X07FE07FE1807FB0C0300C1FF8,Y0F800FJ01EO03C,,:::::::::::::::::::::^FS

# ^FX Titre centré
# ^FO180,160^A0N,40,40^FB300,1,0,L^FDBADGE^FS

# ^FX QR Code
# ^FO300,300^BQN,2,6^FDQA,{qr_data}^FS

# ^FX Infos chauffeur
# ^FO50,360^A0N,28,28^FD{chauffeur_obj.nom_chauffeur} {chauffeur_obj.prenom_chauffeur}^FS
# ^FO50,400^A0N,20,20^FDID: {chauffeur_obj.id_chauffeur}^FS
# ^FO50,430^A0N,20,20^FDPermis: {chauffeur_obj.permis_chauffeur}^FS

# ^XZ"""

#     filename = f"badge_{chauffeur_obj.id_chauffeur}.zpl"
#     response = HttpResponse(zpl_content, content_type='application/octet-stream')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     return response



# def download_zpl(request, chauffeur_id): 
#     # Utilisation de l'alias pour le modèle
#     chauffeur_obj = get_object_or_404(chauffeur, id_chauffeur=chauffeur_id)
    
#     # Données pour le QR code
#     qr_data = f"NOM: {chauffeur_obj.nom_chauffeur}\n PRENOM: {chauffeur_obj.prenom_chauffeur}\n ID: {chauffeur_obj.id_chauffeur}"
    
#     # Génération du ZPL
#     zpl_content = f"""^XA
# ^CI28
# ^MMT
# ^PW609
# ^LL0406
# ^LS0

# ^FX Entête
# ^FO30,40^A0N,28,28^FH\\^FD{chauffeur_obj.nom_chauffeur} {chauffeur_obj.prenom_chauffeur}^FS
# ^FO30,80^A0N,20,20^FH\\^FDID: {chauffeur_obj.id_chauffeur}^FS

# ^FX QR Code
# ^FO400,50^BQN,2,6^FDQA,{qr_data}^FS

# ^FX Code-barres
# ^FO400,200^BCN,100,Y,N,N^FD{chauffeur_obj.id_chauffeur}^FS

# ^XZ"""
    
#     # Réponse avec en-têtes pour le téléchargement
#     filename = f"badge_{chauffeur_obj.id_chauffeur}.zpl"
#     response = HttpResponse(zpl_content, content_type='application/octet-stream')
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     return response

def extract_chauffeur_id(qr_text):
    """Extrait l'ID du chauffeur à partir du texte du QR code"""
    
    # Si c'est juste un nombre, c'est probablement l'ID directement
    if qr_text.isdigit():
        return int(qr_text)
    
    # Sinon, essayons d'extraire l'ID du texte formaté
    lines = qr_text.split('\n')
    for line in lines:
        if line.startswith('ID:'):
            try:
                return int(line.replace('ID:', '').strip())
            except (ValueError, AttributeError):
                continue
    return None


def extract_affectation_id(qr_text):
    """Extrait l'ID de l'affectation à partir du texte du QR code"""
    
    # Si c'est juste un nombre, c'est probablement l'ID directement
    if qr_text.isdigit():
        return int(qr_text)
    
    # Nettoyer le texte des caractères de contrôle ZPL si nécessaire
    clean_text = qr_text.replace('^FD', '').replace('^FS', '').strip()
    
    # Essayer d'extraire l'ID de différents formats de texte
    lines = clean_text.split('\n')
    for line in lines:
        # Format standard
        if 'ID:' in line:
            try:
                return int(line.split('ID:')[-1].strip())
            except (ValueError, AttributeError):
                continue
        # Format ZPL simplifié
        elif '^FD' in line and 'ID' in line:
            try:
                return int(line.split('ID')[-1].replace('^FS', '').strip())
            except (ValueError, AttributeError):
                continue
    
    # Si on arrive ici, essayer de trouver un nombre dans le texte
    import re
    numbers = re.findall(r'\d+', clean_text)
    if numbers:
        try:
            return int(numbers[0])  # Retourne le premier nombre trouvé
        except (ValueError, AttributeError):
            pass
            
    return None

@csrf_exempt
def scan_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            qr_data = data.get('qr_data', '')
            
            # Journalisation du contenu brut du QR code pour le débogage
            print(f"QR Code brut reçu: {qr_data[:100]}..." if len(qr_data) > 100 else f"QR Code brut reçu: {qr_data}")
            
            # Extraire l'ID de l'affectation du texte du QR code
            affectation_id = extract_affectation_id(qr_data)
            
            if not affectation_id:
                # Essayer d'extraire un ID de chauffeur si l'extraction d'affectation échoue
                chauffeur_id_match = re.search(r'CHAUFFEUR[^\d]*(\d+)', qr_data, re.IGNORECASE)
                if chauffeur_id_match:
                    try:
                        chauffeur_id = int(chauffeur_id_match.group(1))
                        # Récupérer la dernière affectation de ce chauffeur
                        affectation = Affectation.objects.filter(chauffeur_id=chauffeur_id).order_by('-id').first()
                        if affectation:
                            affectation_id = affectation.id
                    except (ValueError, AttributeError):
                        pass
            
            if not affectation_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Format de QR code non reconnu. Impossible d\'extraire un identifiant valide.',
                    'qr_data_received': qr_data[:200]  # Retourne un aperçu des données reçues pour le débogage
                }, status=400)
            
            # Essayer de trouver l'affectation avec cet ID
            try:
                affectation = Affectation.objects.get(id=affectation_id)
                chauffeur_obj = affectation.chauffeur
                camion_obj = affectation.camion
            except Affectation.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Affectation non trouvée'
                }, status=404)
            
            # Vérifier s'il y a déjà une entrée non fermée pour cette affectation
            entree_ouverte = EntreeSortie.objects.filter(
                affectation=affectation,
                date_sortie__isnull=True,
                heure_sortie__isnull=True
            ).order_by('-date_entree', '-heure_entree').first()
            
            # Obtenir l'heure actuelle dans le fuseau horaire de Casablanca
            casablanca_tz = pytz.timezone('Africa/Casablanca')
            now = timezone.now().astimezone(casablanca_tz)
            
            if entree_ouverte:
                # Mettre à jour la sortie avec l'heure locale du serveur
                entree_ouverte.date_sortie = now.date()
                entree_ouverte.heure_sortie = now.time()
                entree_ouverte.save()
                
                # Créer des objets datetime conscients du fuseau horaire pour le calcul de la durée
                debut_naive = datetime.combine(entree_ouverte.date_entree, entree_ouverte.heure_entree)
                debut = casablanca_tz.localize(debut_naive)
                duree = now - debut
                
                return JsonResponse({
                    'status': 'success',
                    'action': 'sortie',
                    'chauffeur': f"{chauffeur_obj.nom_chauffeur} {chauffeur_obj.prenom_chauffeur}",
                    'matricule': camion_obj.matricule_camion if camion_obj else 'Inconnu',
                    'date_entree': entree_ouverte.date_entree.strftime('%d/%m/%Y'),
                    'heure_entree': entree_ouverte.heure_entree.strftime('%H:%M'),
                    'date_sortie': now.strftime('%d/%m/%Y'),
                    'heure_sortie': now.strftime('%H:%M'),
                    'duree': str(duree).split('.')[0],  # Enlever les microsecondes
                    'prestataire': affectation.prestataire.nom_prestataire if affectation.prestataire else 'Non spécifié'
                })
            else:
                # Créer une nouvelle entrée avec l'heure locale
                entree = EntreeSortie.objects.create(
                    affectation=affectation,
                    date_entree=now.date(),
                    heure_entree=now.time()
                )
                
                return JsonResponse({
                    'status': 'success',
                    'action': 'entree',
                    'chauffeur': f"{chauffeur_obj.nom_chauffeur} {chauffeur_obj.prenom_chauffeur}",
                    'matricule': camion_obj.matricule_camion if camion_obj else 'Inconnu',
                    'date_entree': now.strftime('%d/%m/%Y'),
                    'heure_entree': now.strftime('%H:%M')
                })
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    # Si ce n'est pas une requête POST, afficher la page de scan
    return render(request, 'scan_qr.html')

def afficher_entree_sortie(request):
    sort = request.GET.get('sort')
    entrees_sorties = EntreeSortie.objects.select_related(
        'affectation__chauffeur',
        'affectation__camion',
        'affectation__prestataire'
    ).order_by('-date_entree', '-heure_entree')

    # Préparer les données pour le template
    donnees = []
    for es in entrees_sorties:
        duree = None
        if es.date_sortie and es.heure_sortie:
            debut = datetime.combine(es.date_entree, es.heure_entree)
            fin = datetime.combine(es.date_sortie, es.heure_sortie)
            duree = fin - debut
            jours = duree.days
            heures, reste = divmod(duree.seconds, 3600)
            minutes, secondes = divmod(reste, 60)
            duree = f"{jours}j {heures}h {minutes}m"
        donnees.append({
            'id': es.id_entreeSortie,
            'camion': es.affectation.camion.matricule_camion if es.affectation.camion else 'N/A',
            'chauffeur': f"{es.affectation.chauffeur.nom_chauffeur} {es.affectation.chauffeur.prenom_chauffeur}",
            'prestataire': es.affectation.prestataire.nom_prestataire if es.affectation.prestataire else 'N/A',
            'date_entree': es.date_entree,
            'heure_entree': es.heure_entree,
            'date_sortie': es.date_sortie,
            'heure_sortie': es.heure_sortie,
            'duree': duree or 'En cours...',
            'statut': 'Sorti' if es.date_sortie and es.heure_sortie else 'En cours'
        })

    if sort == 'statut':
        # Trie d'abord par statut (En cours en haut), puis par date d'entrée/heure
        donnees = sorted(donnees, key=lambda x: (0 if x['statut'] == 'En cours' else 1, -x['date_entree'].toordinal(), -x['heure_entree'].hour, -x['heure_entree'].minute))

    return render(request, 'afficher-entree_sortie.html', {'entrees_sorties': donnees, 'sort': sort})

def test_camera(request):
    """Page de test de la caméra"""
    return render(request, 'test_camera.html')


def creer_facture(request):
    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save(commit=False)
            
            # Récupérer les coordonnées GPS depuis le formulaire
            facture.latitude_depart = form.cleaned_data.get('latitude_depart')
            facture.longitude_depart = form.cleaned_data.get('longitude_depart')
            
            try:
                facture.save()  # Le modèle calculera automatiquement la distance
                messages.success(request, 'Facture créée avec succès!')
                return redirect('facture_detail', pk=facture.pk)
            except Exception as e:
                messages.error(request, f'Erreur lors de la création: {str(e)}')
        else:
            # Afficher les erreurs de validation du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = FactureForm()
    
    # Rendre le template avec le formulaire
    return render(request, 'facture/creer_facture.html', {'form': form})

def detail_facture(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'facture/detail_facture.html', {'facture': facture})

def liste_factures(request):
    factures = Facture.objects.all()
    return render(request, 'factures/liste_factures.html', {'factures': factures})

def liste_factures(request):
    factures = Facture.objects.select_related('affectation', 'affectation__camion', 'affectation__chauffeur').all()
    return render(request, 'facture/liste_factures.html', {
        'factures': factures,
        'title': 'Liste des factures'
    })

@csrf_exempt
def calculer_distance_ajax(request):
    """Vue AJAX pour calculer la distance en temps réel"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            lat_depart = data.get('lat_depart')
            lng_depart = data.get('lng_depart')
            destination = data.get('destination')
            
            if not all([lat_depart, lng_depart, destination]):
                return JsonResponse({'error': 'Données manquantes'}, status=400)
            
            # Créer une instance temporaire pour utiliser les méthodes de géocodage
            facture_temp = Facture()
            facture_temp.destination = destination
            facture_temp.latitude_depart = lat_depart
            facture_temp.longitude_depart = lng_depart
            
            # Géocoder la destination
            lat_dest, lng_dest = facture_temp.geocoder_destination()
            
            if lat_dest and lng_dest:
                facture_temp.latitude_destination = lat_dest
                facture_temp.longitude_destination = lng_dest
                distance = facture_temp.calculer_distance()
                
                return JsonResponse({
                    'distance': distance,
                    'lat_destination': lat_dest,
                    'lng_destination': lng_dest
                })
            else:
                return JsonResponse({'error': 'Impossible de géocoder la destination'}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


def calculer_montants(request):
    """Vue HTMX pour calculer les montants en temps réel"""
    if request.method == 'GET':
        form = FactureForm(request.GET)
        
        if form.is_valid():
            affectation = form.cleaned_data.get('affectation')
            poids = form.cleaned_data.get('poids_marchandise', 0)
            prix_km = form.cleaned_data.get('prix_par_km', 0)
            prix_tonne = form.cleaned_data.get('prix_par_tonne', 0)
            
            if affectation:
                distance = affectation.distance
                frais_transport = distance * float(prix_km)
                frais_marchandise = float(poids) * float(prix_tonne)
                total = frais_transport + frais_marchandise
                
                # Calculer le total pour ce camion
                factures_camion = Facture.objects.filter(affectation__camion=affectation.camion)
                total_camion = factures_camion.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
                nombre_factures = factures_camion.count()
                
                context = {
                    'frais_transport': round(frais_transport, 2),
                    'frais_marchandise': round(frais_marchandise, 2),
                    'total': round(total, 2),
                    'total_camion': round(total_camion, 2),
                    'distance': distance,
                    'affectation': affectation,
                    'nombre_factures': nombre_factures,
                    'valid': True
                }
                return render(request, 'facture/partials/montants.html', context)
    
    # En cas d'erreur ou de formulaire invalide
    return render(request, 'facture/partials/montants.html', {'valid': False})


def get_total_camion(request):
    """Vue HTMX pour récupérer le total d'un camion spécifique"""
    if request.method == 'GET' and 'affectation' in request.GET:
        try:
            affectation_id = request.GET.get('affectation')
            affectation = Affectation.objects.get(id=affectation_id)
            
            # Calculer le total pour ce camion
            factures_camion = Facture.objects.filter(affectation__camion=affectation.camion)
            total_camion = factures_camion.aggregate(Sum('montant_total'))['montant_total__sum'] or 0
            nombre_factures = factures_camion.count()
            
            context = {
                'affectation': affectation,
                'total_camion': round(total_camion, 2),
                'nombre_factures': nombre_factures,
                'valid': True
            }
            return render(request, 'facture/partials/total_camion.html', context)
        except (ValueError, Affectation.DoesNotExist):
            pass
    
    return render(request, 'facture/partials/total_camion.html', {'valid': False})


def total_camion(request):
    """Vue pour afficher le total de tous les camions avec les détails des affectations"""
    # Récupérer tous les camions avec le total des factures
    camions = camion.objects.annotate(
        total_factures=Sum('affectation__factures__montant_total'),
        nombre_factures=Count('affectation__factures', distinct=True)
    ).filter(total_factures__gt=0).order_by('-total_factures')

    # Préparer les données pour le template
    camions_data = []
    for cam in camions:
        # Récupérer toutes les affectations pour ce camion (les plus récentes en premier)
        affectations = Affectation.objects.filter(camion=cam).order_by('-id')
        derniere_affectation = affectations.first()
        
        # Préparer les détails des affectations
        affectations_details = []
        for aff in affectations:
            # Compter le nombre de factures pour cette affectation
            nb_factures_aff = aff.factures.count()
            # Calculer le total des factures pour cette affectation
            total_aff = aff.factures.aggregate(total=Sum('montant_total'))['total'] or 0
            
            # Récupérer la destination et la distance de la première facture si elle existe
            premiere_facture = aff.factures.first()
            destination = premiere_facture.destination if premiere_facture else "Non spécifiée"
            distance = premiere_facture.distance_km if premiere_facture and hasattr(premiere_facture, 'distance_km') else 0
            
            affectations_details.append({
                'id': aff.id,
                'chauffeur': aff.chauffeur,
                'date_entree': cam.date_entreeC,
                'date_sortie': cam.date_sortieC,
                'nb_factures': nb_factures_aff,
                'total': total_aff,
                'statut': 'Terminée' if cam.date_sortieC else 'En cours',
                'destination': destination,
                'distance': distance
            })
        
        camions_data.append({
            'id': cam.id_camion,  # Using id_camion instead of id
            'matricule': cam.matricule_camion,
            'marque': cam.marque if hasattr(cam, 'marque') else '',
            'modele': cam.modele if hasattr(cam, 'modele') else '',
            'nb_factures': cam.nombre_factures,
            'total': cam.total_factures or 0,
            'affectations': affectations_details,
            'dernier_chauffeur': derniere_affectation.chauffeur if derniere_affectation else None,
            'derniere_maj': derniere_affectation.date_creation if derniere_affectation and hasattr(derniere_affectation, 'date_creation') else None
        })
    
    # Trier par montant total décroissant
    camions_data.sort(key=lambda x: x['total'], reverse=True)
    
    # Calculer le total général
    total_general = sum(cam['total'] for cam in camions_data)
    
    context = {
        'camions_data': camions_data,
        'total_general': round(total_general, 2),
        'title': 'Totaux par camion'
    }
    
    return render(request, 'facture/total_camion.html', context)


def liste_factures(request):
    factures = Facture.objects.select_related('affectation', 'affectation__camion', 'affectation__chauffeur').all()
    return render(request, 'facture/liste_factures.html', {
        'factures': factures,
        'title': 'Liste des factures'
    })