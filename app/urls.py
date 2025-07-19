from django.shortcuts import render
from django.urls import path
from . import views

# app_name = 'app'

urlpatterns = [
    # path('', views.afficher_message, name='afficher_message'),  # URL pour afficher un message
    # path('', views.couverture_view, name='couverture'),  # URL pour la page de couverture
    path('', views.login_couverture, name='login_couverture'),
    path('ajouter_chauffeur/', views.ajouter_chauffeur, name='ajouter_chauffeur'),
    path('success/', lambda request: render(request, 'success.html'), name='success'),
    path('afficher_chauffeur/', views.afficher_chauffeurs, name='afficher_chauffeur'),
    path('ajouter_camion/', views.ajouter_camion, name='ajouter_camion'),
    path('afficher_camions/', views.afficher_camions, name='afficher_camions'),
    path('afficher_camions_Nsortie/', views.afficher_camions_Nsortie, name='afficher_camions_Nsortie'),
    path('sortie_camion/<int:id_camion>/', views.sortie_camion, name='sortie_camion'),
    path('index/', views.afficher_message, name='index'),  # URL pour l
    # path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('acceuil/', views.acceuil_view, name='acceuil'),
    path('interface_admin/', views.interface_admin, name='interface_admin'),
    path('success_message/', views.success, name='success_message'),
    path('modifier_chauffeur/<int:id_chauffeur>/', views.modifier_chauffeur, name='modifier_chauffeur'),
    path('modifier_camion/<int:id_camion>/', views.modifier_camion, name='modifier_camion'),
    path('ajouter_prestataire/', views.ajouter_prestataire, name='ajouter_prestataire'),
    path('afficher_prestataires/', views.afficher_prestataires, name='afficher_prestataires'),
    path('genere_bdg/', views.genere_bdg, name='genere_bdg'),
    path('get_chauffeur_info/', views.get_chauffeur_info, name='get_chauffeur_info'),
    path('chauffeur/<int:chauffeur_id>/download_badge/', views.download_badge_pdf, name='download_badge_pdf'),
    path('badge_pdf/<int:chauffeur_id>/', views.badge_pdf, name='badge_pdf'),
    path('sortie_camion/<int:id_camion>/', views.sortie_camion, name='sortie_camion'),
    path('modifier_prestataire/<int:id_prestataire>/', views.modifier_prestataire, name='modifier_prestataire'),
    path('afficher_affectations/', views.afficher_affectations, name='afficher_affectations'),
    path('ajouter_utilisateur/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path('afficher_utilisateurs/', views.afficher_utilisateurs, name='afficher_utilisateurs'),
    path('modifier_utilisateur/<int:id_user>/', views.modifier_utilisateur, name='modifier_utilisateur'),
    path('download_zpl/<int:chauffeur_id>/', views.download_zpl, name='download_zpl'),
    path('scan/<str:type_objet>/<int:id_objet>/', views.scan_qr_code, name='scan_qr_code'),
    path('scanner/', views.scanner_page, name='scanner_page'),
    path('api/process-scan/', views.process_qr_scan, name='process_qr_scan'),
    path('process-qr-scan/', views.process_qr_scan, name='process_qr_scan'),
    path('test_camera/', views.test_camera, name='test_camera'),


]