from io import BytesIO
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import chauffeur, camion, prestataire, Affectation, Utilisateur, EntreeSortie
from .forms import ChauffeurForm, CamionForm, RechercheCamionForm, SortieCamionForm, PrestataireForm, BadgeForm, NouveauPrestataireForm, UserForm
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import get_object_or_404
import base64
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError
from django.conf import settings  # Import pour accéder aux paramètres
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from weasyprint import CSS

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
                return redirect('index')  # ou une autre page utilisateur normal

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
            # Récupérer tous les camions associés à ce chauffeur
            camions = camion.objects.filter(id_chauffeur=chauffeur_obj)
            
            return render(request, 'genere_bdg.html', {
                'form': form,
                'chauffeur': chauffeur_obj,
                'camions': camions,  # Envoyer la liste des camions
                'prestataire': chauffeur_obj.prestataire if hasattr(chauffeur_obj, 'prestataire') else None,
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
    
    # Rendu du contenu du badge
    badge_content = render_to_string('badge_pdf.html', {
        'chauffeur': chauffeur_obj,
        'affectation': affectation,
        'request': request,
        'is_pdf': True  # Ajout d'un flag pour le template si nécessaire
    })
    
    # Configuration de la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="badge_{chauffeur_obj.nom_chauffeur}.pdf"'
    
    # Options de conversion HTML vers PDF
    pdf_options = {
        'encoding': 'UTF-8',
        'presentational_hints': True
    }
    
    # Génération du PDF
    HTML(
        string=badge_content,
        base_url=request.build_absolute_uri()
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
                /* Ajoutez ici d'autres styles spécifiques si nécessaire */
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

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from .models import chauffeur, Affectation

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import chauffeur



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

    # Chercher l'affectation liée au chauffeur
    try:
        affectation = Affectation.objects.get(chauffeur=chauffeur_obj)
    except Affectation.DoesNotExist:
        affectation = None

    # Déterminer le QR code à utiliser
    if affectation and affectation.qr_code:
        qr_image_url = affectation.qr_code.url
        qr_data = f"AFFECTATION: {affectation.id}\n" \
            f"CHAUFFEUR: \n ID : {affectation.chauffeur.id_chauffeur}\n"\
            f"NOM :{affectation.chauffeur.nom_chauffeur} \n"\
            f"PRENOM :{affectation.chauffeur.prenom_chauffeur}\n"\
            f"CAMION :\n MATRICULE :{affectation.camion.matricule_camion}\n"\
            f"NOM SOCIETE : {affectation.camion.nom_societe}\n"\
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
^FO200,500^BQN,2,6^FDQA,{qr_data}^FS

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
def scanner_page(request):
    """Page de scan pour l'interface mobile"""
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'scanner.html')


def test_camera(request):
    """Page de test de la caméra"""
    return render(request, 'test_camera.html')

# app/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

@require_http_methods(["POST"])
@csrf_exempt
def process_qr_scan(request):
    """
    Traite les données d'un QR code scanné.
    """
    # Vérifier si l'utilisateur est authentifié
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentification requise',
            'redirect': '/login/'
        }, status=401)
    
    # Récupérer les données JSON
    try:
        data = json.loads(request.body)
        qr_data = data.get('qr_data', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Données JSON invalides'
        }, status=400)
    
    if not qr_data:
        return JsonResponse({
            'status': 'error',
            'message': 'Aucune donnée QR reçue'
        }, status=400)
    
    # Journaliser le scan pour le débogage
    print(f"[QR SCAN] Données reçues: {qr_data}")
    
    try:
        # Traitement des données du QR code
        
        # 1. Vérifier si c'est une URL
        if qr_data.startswith(('http://', 'https://')):
            # Extraire l'ID de l'objet depuis l'URL si possible
            import re
            match = re.search(r'scan/(\w+)/(\d+)/', qr_data)
            if match:
                object_type = match.group(1)
                object_id = match.group(2)
                print(f"[QR SCAN] Type: {object_type}, ID: {object_id}")
                
                # Rediriger vers la vue de scan appropriée
                return JsonResponse({
                    'status': 'success',
                    'type': 'url',
                    'data': {
                        'type': object_type,
                        'id': object_id,
                        'url': qr_data
                    },
                    'redirect': f'/scan/{object_type}/{object_id}/',
                    'message': 'URL de scan détectée avec succès'
                })
            
            # Si c'est une URL mais pas une URL de scan connue
            return JsonResponse({
                'status': 'success',
                'type': 'url',
                'data': {
                    'url': qr_data,
                    'raw': qr_data
                },
                'message': 'URL détectée dans le QR code'
            })
        
        # 2. Vérifier si c'est un ID de chauffeur (format: chauffeur:123)
        elif qr_data.startswith('chauffeur:'):
            try:
                chauffeur_id = qr_data.split(':')[1]
                from .models import chauffeur
                chauffeur_obj = chauffeur.objects.get(id_chauffeur=chauffeur_id)
                
                return JsonResponse({
                    'status': 'success',
                    'type': 'chauffeur',
                    'data': {
                        'id': chauffeur_obj.id_chauffeur,
                        'nom_complet': f"{chauffeur_obj.prenom} {chauffeur_obj.nom}",
                        'matricule': chauffeur_obj.matricule or 'N/A',
                        'raw': qr_data
                    },
                    'redirect': f'/chauffeur/{chauffeur_id}/',
                    'message': 'Chauffeur identifié avec succès'
                })
                
            except (IndexError, ValueError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Format de QR code invalide pour un chauffeur',
                    'expected_format': 'chauffeur:ID_CHAUFFEUR'
                }, status=400)
                
            except chauffeur.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Chauffeur avec l\'ID {chauffeur_id} non trouvé'
                }, status=404)
        
        # 3. Autre type de données (texte brut)
        else:
            return JsonResponse({
                'status': 'success',
                'type': 'text',
                'data': {
                    'raw': qr_data
                },
                'message': 'Données texte extraites avec succès'
            })
            
    except Exception as e:
        # En cas d'erreur inattendue
        import traceback
        print(f"[QR SCAN] Erreur inattendue: {str(e)}\n{traceback.format_exc()}")
        
        return JsonResponse({
            'status': 'error',
            'message': 'Une erreur est survenue lors du traitement du QR code',
            'error': str(e)
        }, status=500)

def scan_qr_code(request, id_objet, type_objet):
    """
    Vue appelée lors du scan d'un QR code.
    type_objet peut être 'prestataire', 'chauffeur' ou 'affectation'
    id_objet est l'identifiant de l'objet dans la base de données
    """
    try:
        if type_objet == 'affectation':
            # Récupérer l'affectation correspondante
            affectation = get_object_or_404(Affectation, id=id_objet)
            
            # Vérifier s'il existe déjà une entrée non fermée pour cette affectation
            entree_existante = EntreeSortie.objects.filter(
                affectation=affectation,
                date_sortie__isnull=True,
                heure_sortie__isnull=True
            ).first()
            
            if entree_existante:
                # Mettre à jour l'entrée existante avec la date et l'heure de sortie
                entree_existante.date_sortie = timezone.now().date()
                entree_existante.heure_sortie = timezone.now().time()
                entree_existante.save()
                action = "sortie"
            else:
                # Créer une nouvelle entrée
                EntreeSortie.objects.create(
                    affectation=affectation,
                    date_entree=timezone.now().date(),
                    heure_entree=timezone.now().time()
                )
                action = "entrée"
            
            return JsonResponse({
                'status': 'success',
                'message': f'Enregistrement d\'une {action} pour l\'affectation {affectation.id}',
                'data': {
                    'id': id_objet,
                    'type': type_objet,
                    'action': action,
                    'timestamp': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            })
            
        # Ajoutez ici d'autres types d'objets si nécessaire
        # elif type_objet == 'chauffeur':
        #     ...
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

from django.shortcuts import render
# Temporarily commenting out pyzbar import to fix server startup
# from pyzbar.pyzbar import decode
# from PIL import Image

def scanner(request):
    # Temporarily disabled barcode scanning functionality
    return JsonResponse({'status': 'error', 'message': 'Barcode scanning is currently disabled. Please check the server configuration.'}, status=503)
    
    # Original scanner code (commented out)
    # if request.method == 'POST' and 'image' in request.FILES:
    #     image = request.FILES['image']
    #     try:
    #         # Open the image using PIL
    #         pil_image = Image.open(image)
    #         # Decode the barcode from the image
    #         decoded_objects = decode(pil_image)
    #         
    #         if decoded_objects:
    #             # Return the first barcode data found
    #             barcode_data = decoded_objects[0].data.decode('utf-8')
    #             return JsonResponse({'status': 'success', 'data': barcode_data})
    #         else:
    #             return JsonResponse({'status': 'error', 'message': 'No barcode found'}, status=400)
    #             
    #     except Exception as e:
    #         return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    # 
    # return render(request, 'scanner.html')
