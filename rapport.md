# GESTION-DE-CAMION



	



RAPPORT DE STAGE D’ETE
	

Application de Gestion des entrées sorties des Camions



         




	                                      Année universitaire 2024-2025 

Remerciement 


















Résumé 
Le projet confié consistait à développer une application web de gestion logistique pour moderniser et automatiser la gestion des flux de camions. Face aux problématiques de suivi inefficace des entrées/sorties, de gestion manuelle génératrice d'erreurs et de manque de traçabilité, une solution informatique s'imposait.
L'application développée avec le framework Django (Python) offre une gestion complète des camions, chauffeurs, prestataires et affectations. Elle intègre un système de QR codes pour l'identification automatique, un suivi en temps réel des entrées/sorties avec horodatage précis, et la génération automatique de badges et factures au format PDF. Le système propose trois niveaux d'accès (utilisateur normal, administrateur et super-administrateur) garantissant une sécurité adaptée aux besoins.
L'architecture technique repose sur le framework Django avec une base de données SQLite, une interface responsive utilisant HTML5, CSS3, JavaScript et Bootstrap. Les fonctionnalités avancées exploitent des bibliothèques spécialisées pour la génération de QR codes (qrcode), leur lecture via webcam (opencv-python, pyzbar), la création de documents PDF (reportlab, xhtml2pdf) et les calculs géographiques (geopy).
Ce projet a permis à la société de moderniser sa gestion logistique, d'automatiser les processus manuels, d'améliorer la traçabilité des opérations et de réduire significativement les erreurs et pertes de temps. Pour le stagiaire, cette expérience a constitué une opportunité d'appliquer les connaissances théoriques dans un contexte industriel réel, tout en développant des compétences en développement web full-stack, conception UML, intégration de technologies et sécurité informatique.




Abstract

The assigned project involved developing a logistics management web application to modernize and automate truck flow management. Faced with issues of ineffective tracking of entries/exits, manual management generating errors, and lack of traceability, a technological solution was imperative.
The application developed with the Django framework (Python) offers comprehensive management of trucks, drivers, service providers and assignments. It integrates a QR code system for automatic identification, real-time tracking of entries/exits with precise timestamps, and automatic generation of badges and invoices in PDF format. The system provides three access levels (regular user, administrator and super-administrator) ensuring security adapted to requirements.
The technical architecture is based on the Django framework with an SQLite database, a responsive interface using HTML5, CSS3, JavaScript and Bootstrap. Advanced features leverage specialized libraries for QR code generation (qrcode), webcam reading (opencv-python, pyzbar), PDF document creation (reportlab, xhtml2pdf) and geographical calculations (geopy).
This project enabled company to modernize its logistics management, automate manual processes, improve operational traceability and significantly reduce errors and time losses. For the intern, this experience provided an opportunity to apply theoretical knowledge in a real industrial context, while developing skills in full-stack web development, UML design, technology integration and computer security.






LISTE DES FIGURES 
-	Figure 1 : logo Super CERAME……………………………………….
-	Figure 2 :  Représentation de la répartition des services……………..
-	Figure 3 :  Diagramme de cas d’utilisation…………………………….
-	Figure 4 :  Diagramme de classe……………………………………….
-	Figure 5 : Diagramme de séquence…………………………………….
-	Figure 6 : Diagramme d’activité……………………………………….
-	Figure 7 :  Logo Visual Studio Code…………………………………....
-	Figure 8 :  Logo DB Browser for SQLite………………………………
-	Figure 9 :  Logo Git & GitHub…………………………………………
-	Figure 10 :  Logo Python…………………………………………..……
-	Figure 11 :  Logo Django……………………………………………..…
-	Figure 12 :  Logo HTML………………………………………….…….
-	Figure 13 :  Logo CSS…………………………………………………..
-	Figure 14 :  Logo Javascript……………………………………………
-	Figure 15 :  Logo Bootstrap………………………………………….…
-	Figure 16 :  Logo SQLite………………………………………………..
-	Figure 18 :  Interface administrateur………………………………….
-	Figure 19 :  Formulaire d’ajout d’une ville interface du mobile.……..
-	Figure 20 :  Formulaire d’ajout d’une d’un chauffeur………………..
-	Figure 21 :  après scan de sortie pour un camion……………..……….




ABREVIATION 	DESIGNATION
GRH 	Gestion des Ressources Humaines
ISO	International Organization for Standardization 
(Système de management de la qualité)
OHSAS	Occupational Health and Safety Assessment Series (Système de management de la santé et sécurité au travail)
HTML5	HyperText Markup Language version 5
CSS3	Cascading Style Sheets version 3
SQL	Structured Query Language
PDF	Portable Document Format
ZPL	Zebra(imprimante) Programming Language
API	Application Programming Interface
SSL	Secure Sockets Layer
http (S)	HyperText Transfer Protocol (Secure)
CSRF	Cross-Site Request Forgery
XSS	Cross-Site Scripting
CORS 	Cross-Origin Resource Sharing
JSON	JavaScript Object Notation
ACID	Atomicity, Consistency, Isolation, Durability
DOM	Document Object Model
REST	Representational State Transfer
ORM	Object-Relational Mapping
MTV	Model-Template-View (architecture Django)
MVC	Model-View-Controller
CRUD	Create, Read, Update, Delete
UML	Unified Modeling Language
GET	Méthode HTTP pour récupérer des données
POST	Méthode HTTP pour envoyer des données
PUT	Méthode HTTP pour mettre à jour des données
DELETE	Méthode HTTP pour supprimer des données
CSV	Comma-Separated Values
PEM	Privacy-Enhanced Mail (format de certificat)
IA	Intelligence Artificielle

Table des Matières
Remerciements…………………………………………………….....
Résumé………………………………………………………………
Abstract………………………………………………………………
Liste des figures……………………………………………………...
Liste des abreviations………………………………………………..
Chapitre 1 : Présentation de projet……………………………….
I.	Introduction générale……………………………………..
1.	Contexte général du projet………………………………. 
2.	Problématique spécifique abordée……………………….
3.	Objectifs précis du projet………………………………....
4.	Annonce du plan du rapport………………………………
II.	Projet et management du projet…………………………. 
1.	Contexte du projet……………………………………...
2.	Problème et besoins……………………………………. 
3.	Cahier des charges……………………………………...
a.	Besoins fonctionnels……………………….......
b.	Besoins non fonctionnels………………….. 
III.	Analyse et Conception…………………………………….
1.	Spécifications fonctionnelles……………………………...
2.	Conception…………………………………………………
a.	Diagrammes de cas d'utilisation……………………
b.	Diagramme de classe………………………………...
c.	Diagramme de séquence……………………………. 
d.	Diagramme d’activité……………………………….. 
IV.	Réalisation et Développement…………………………….
1.	Architecture et Environnement Technique…………...
a.	Architecture Frontend…………………………...
b.	Architecture Backend……………………….......... 
c.	Structure des Applications……………………….
d.	Intégrations……………………………………….
e.	Organisation des Ressources…………………….
2.	Architecture logicielle envisagée………………………
a.	Vue d’ensemble du système……………………...
b.	Sécurité et certification…………………………..
3.	Environnement de développement…………………… 
4.	Technologies Utilisées………………………………….
5.	Bibliothèques et Extensions Python…………………..
6.	Implémentation des Fonctionnalités Principales…….
7.	Capture d’écran de quelque interface………………..
V.	Conclusion…………………………………………………












Introduction

Dans le cadre de ma formation d'ingénieur en informatique et développement à l'École Marocaine des Sciences de l'Ingénieur (EMSI), j'ai effectué un stage technique d'une durée d'un mois au sein de l'entreprise à Casablanca.
Les stages professionnels représentent une composante essentielle de la formation d'ingénieur, offrant aux étudiants l'opportunité unique de découvrir concrètement le monde de l'entreprise et ses mécanismes de fonctionnement. Ils constituent un pont indispensable entre les connaissances théoriques acquises en cours et la pratique professionnelle, permettant de développer une expérience tangible impossible à obtenir dans l'environnement académique traditionnel.
Au-delà de l'acquisition de compétences techniques, les stages favorisent la compréhension des enjeux économiques et organisationnels de l'entreprise, tout en contribuant à la construction d'un réseau professionnel. Cette immersion dans le milieu industriel permet également d'affiner sa vision du métier d'ingénieur et d'orienter ses choix de spécialisation et de carrière future.
Ce stage technique m'a offert l'opportunité d'observer de près le fonctionnement d'une entreprise industrielle, de comprendre les conditions de travail et les processus de production, tout en m'adaptant aux exigences et obligations du milieu professionnel. Cette expérience sociotechnique enrichissante constitue une étape déterminante dans ma préparation à l'entrée dans la vie active.










CHAPITRE 1 :
Présentation du Projet

« Application de Gestion des entrées sorties de Camions »










I.	Introduction générale
1.	Contexte général du projet
Dans le cadre de mon stage au sein de la société , j’ai été chargé de développer une application web de gestion logistique, permettant la gestion des camions, chauffeurs, affectations, entrées/sorties, utilisateurs, et la génération de factures et de badge. Ce projet a été réalisé en un mois, en utilisant le Framework Django.
2.	Problématique spécifique abordée
La société souhaitait moderniser et automatiser la gestion des flux logistiques, notamment :
	Suivi en temps réel des entrées et sorties des camions.
	Attribution efficace des chauffeurs et camions.
	Génération rapide de factures.
	Sécurisation des accès et traçabilité des opérations.
	Intégration de la lecture de QR codes pour simplifier et fiabiliser les contrôles.
3.	 Objectifs précis du projet
	Développer une plateforme centralisée pour la gestion logistique.
	Permettre la création, modification et suivi des camions, chauffeurs, affectations et utilisateurs.
	Automatiser la gestion des entrées/sorties avec horodatage précis.
	Générer des factures et des badges personnalisés.
	Intégrer un système de QR code pour l’identification rapide (Entrée / Sortie).
	Assurer la sécurité, la traçabilité et la facilité d’utilisation.
4.	Annonce du plan du rapport
Ce chapitre présente :
•	Le contexte et la gestion du projet.
•	L’analyse des besoins et la conception.
•	L’architecture logicielle et les technologies utilisées.
•	L’implémentation des principales fonctionnalités.

II.	Projet et management du projet
1.	 Contexte du projet
La société gère quotidiennement un flux important de camions et de chauffeurs. L’ancienne gestion manuelle engendrait des erreurs, des pertes de temps et un manque de traçabilité.
2.	 Problème et besoins
	Suivi inefficace des entrées/sorties.
	Difficulté à retrouver l’historique des affectations.
	Génération de factures lente et sujette à erreurs.
	Besoin d’un système sécurisé et accessible à distance.
3.	Cahier des charges
a.	Besoins fonctionnels
	Gestion CRUD des camions, chauffeurs, utilisateurs, prestataires.
	Affectation des chauffeurs aux camions.
	Gestion des entrées/sorties avec horodatage.
	Génération de badges et factures PDF.
	Lecture et génération de QR codes.
	Authentification et gestion des rôles utilisateurs.
	Tableau de bord d’accueil, affichage des listes, recherche et filtres.
	Interface d’administration.
b.	Besoins non fonctionnels
	Application responsive et ergonomique.
	Sécurité des données (authentification, autorisations).
	Rapidité d’exécution.
	Traçabilité des actions.
	Facilité de maintenance et d’évolution.

III.	Analyse et Conception
1.	Spécifications fonctionnelles
Le projet comprend quatre interfaces distinctes :
	Interface de login : la connexion avec le username et le password.
	Interface utilisateur normale (non admin) : Dans cette interface cet utilisateur peut visiter et visualiser les listes des chauffeurs, camions, prestataires, affectations, villes et même le journal des entrée / sortie. 
	Interface utilisateur admin : l’utilisateur admin peut ajouter, modifier, supprimer et même visualiser les listes des chauffeurs, camions, prestataires, affectations, villes et même le journal des entrée / sortie, il a le droit de scanner le code QR d’un camion et générer les badges(format PDF OU ZPL ) et il est capable aussi de créer des factures et les visualiser.
	Interface Administrateur : l’administrateur a le droit de tous faire c’est-à-dire il peut gérer (ajouter, supprimer, modifier, visualiser) les chauffeurs, les camions, les prestataires, les affectations, villes et même les utilisateurs.
Tableau 1 : Récapitulatif des droits d’accès par rôle

Module	
Utilisateur Normal	
Utilisateur Admin	
Administrateur

Chauffeurs	Lecture	CRUD	CRUD
Camions	Lecture	CRUD + Scanner QR	CRUD + Scanner QR
Prestataires	Lecture	CRUD	CRUD
Affectations	Lecture	CRUD	CRUD
Journal E/S	Lecture	CRUD	CRUD
Badges	❌	Générer	Générer
Factures	❌	CRUD	CRUD
Utilisateurs	❌	❌	CRUD
2.	Conception
a.	Diagrammes de cas d’utilisation
                               Figure 3 :  Diagramme de cas d’utilisation
Explication du diagramme de cas d'utilisation :
Le diagramme présente un système de gestion avec trois types d'acteurs ayant des niveaux d'accès hiérarchiques. Voici une description détaillée des acteurs et de leurs interactions :
Acteurs
	Utilisateur (Non Admin) : 
	Acteur avec des permissions limitées de consultation uniquement.
	Utilisateur (Admin) : 
	Acteur héritant des permissions de l'utilisateur non-admin avec des droits étendus de gestion.
	Administrateur : 
	Acteur principal avec tous les privilèges du système, incluant la gestion des utilisateurs.
Cas d'Utilisation
	Pour l'Utilisateur (Non Admin) :
	Consulter les listes : Peut uniquement visualiser les informations concernant : les camions, les chauffeurs, les factures, les entrées et sorties
	S'authentifier : Doit se connecter au système pour accéder aux fonctionnalités
	Pour l'Utilisateur (Admin) :
          Hérite de toutes les permissions de l'utilisateur non- admin,plus :
	Scanner le code QR : Peut numériser les codes QR des camions(affectations).
	Gérer les camions : Peut ajouter, modifier les informations et supprimer des camions.
	Gérer les prestataires : Peut ajouter, modifier les informations et supprimer des prestataires.
	Gérer les chauffeurs : Peut ajouter, modifier les informations et supprimer des chauffeurs.
	Générer les badges : Peut télécharger et visualiser les badges.
	Créer des factures : Peut ajouter des factures.
	Créer des villes : peut ajouter des villes et les visualiser
	Pour l'Administrateur :
                Possède tous les droits des utilisateurs précédents, plus :
	Gérer les utilisateurs : Contrôle total sur la création, modification et suppression des comptes utilisateurs
	Gérer les camions, chauffeurs, prestataires : Accès complet à toutes les fonctionnalités de gestion
	Gérer les badges et les factures. 
	Créer des villes : peut ajouter des villes et les visualiser
b.	Diagramme de classe
 
                                   Figure 4 : Diagramme de classe 
Explication du Diagramme de Classes :
Le diagramme de classes présente la structure d'un système de gestion de transport avec différentes entités métier, leurs attributs et leurs méthodes. Voici une description détaillée des classes et de leurs relations :
	Classes
	 Chauffeur
o	Attributs :
•	id_chauffeur : AutoField - Identifiant unique du chauffeur
•	nom_chauffeur : CharField - Nom du chauffeur
•	prenom_chauffeur : CharField - Prénom du chauffeur
•	permis_chauffeur : CharField - Numéro de permis de conduire
•	qr_code : ImageField - Code QR du chauffeur
o	Méthodes :
•	get_id_chauffeur() : Retourne l'identifiant du chauffeur
•	get_nom_chauffeur() : Retourne le nom du chauffeur
•	get_permis_chauffeur() : Retourne le numéro de permis
•	generate_qrcode() : Génère le code QR
•	save() : Sauvegarde les données
•	__str__() : Représentation textuelle de l'objet

	 Camion
o	Attributs :
•	id_camion : AutoField - Identifiant unique du camion
•	immatriculation : AutoField - Numéro d'immatriculation
•	id_chauffeur : AutoField - Référence au chauffeur assigné
•	matricule_camion : CharField - Matricule du camion
•	capacite : DecimalField - Capacité de charge du camion
o	Méthodes :
•	clean() : Validation des données
•	save() : Sauvegarde avec validation
•	calculer_temps_utilisateur() : Calcule le temps d'utilisation
•	__str__() : Représentation textuelle

	 Utilisateur
o	Attributs :
•	id_user : AutoField - Identifiant unique de l'utilisateur
•	username : CharField - Nom d'utilisateur
•	password : CharField - Mot de passe
•	is_admin : BooleanField - Statut administrateur
o	Méthodes :
•	get_is_admin() : Vérifie le statut admin
•	get_username() : Retourne le nom d'utilisateur
•	__str__() : Représentation textuelle

	 Affectation
o	Attributs :
•	id : AutoField - Identifiant unique de l'affectation
•	chauffeur : FK Chauffeur - Référence au chauffeur
•	camion : FK Camion - Référence au camion
•	prestataire : FK Prestataire - Référence au prestataire
•	qr_code : ImageField - Code QR de l'affectation
o	Méthodes :
•	save() : Sauvegarde les données
•	__str__() : Représentation textuelle
	 Prestataire
o	Attributs :
•	id_prestataire : AutoField - Identifiant unique du prestataire
•	nom_prestataire : CharField - Nom du prestataire
•	adresse_prestataire : CharField - Adresse du prestataire
•	fax_prestataire : CharField - Numéro de fax
•	telephone_prestataire : CharField - Numéro de téléphone
•	qr_code : ImageField - Code QR du prestataire
o	Méthodes :
•	get_prestataire() : Retourne les informations du prestataire
•	save() : Sauvegarde les données
•	__str__() : Représentation textuelle

	 Site
o	Attributs :
•	id_site : AutoField - Identifiant unique du site
•	nom_site : CharField - Nom du site
•	adresse : CharField - Adresse du site
•	telephone_site : CharField - Numéro de téléphone du site
o	Méthodes :
•	__str__() : Représentation textuelle

	 Facture
o	Attributs :
•	id_facture : AutoField - Identifiant unique de la facture
•	affectation : FK Affectation - Référence à l'affectation
•	poids_marchandise : FloatField - Poids de la marchandise
•	destination : CharField - Destination de livraison
•	localisation : CharField - Localisation actuelle
•	longitude_depart/destination : FloatField - Coordonnées GPS
•	latitude_depart/destination : FloatField - Coordonnées GPS
•	distance_km : FloatField - Distance parcourue
•	frais_marchandise : DecimalField - Frais de transport
•	prix_par_km/tonne : DecimalField - Tarification
•	montant_total : DecimalField - Montant total de la facture
o	Méthodes :
•	clean() : Validation des données
•	encoder_destination() : Encode la destination
•	calculer_distance() : Calcule la distance
•	save() : Sauvegarde avec calculs automatiques
•	calculer_frais() : Calcule les frais de transport
•	__str__() : Représentation textuelle

	 EntreeSortie
o	Attributs :
•	id_entree_sortie : AutoField - Identifiant unique
•	affectation : FK Affectation - Référence à l'affectation
•	date_entree/sortie : DateField - Dates d'entrée et sortie
•	heure_entree/sortie : TimeField - Heures d'entrée et sortie
o	Méthodes :
•	clean() : Validation des données

	Villle
o	Attributs :
•	id_ville : AutoField - Identifiant unique de la ville 
•	nom_ville : CharField - Nom de la ville 
•	latitude_ville : DecimalField - Coordonnée GPS latitude 
•	longitude_ville : DecimalField - Coordonnée GPS longitude
o	Méthodes :
•	__str__() : Représentation textuelle

	 Relations
	Clés étrangères (FK) :
•	Affectation est liée à Chauffeur, Camion et Prestataire (relation 1 vers plusieurs)
•	Facture est liée à Affectation (relation 1 vers 1)
•	EntreeSortie est liée à Affectation (relation 1 vers plusieurs)
•	Ville : FK Ville dans la classe Prestataire signifie que chaque prestataire est associé à une ville spécifique
	Cardinalités :
•	Un Chauffeur peut avoir plusieurs Affectations (1:*)
•	Un Camion peut avoir plusieurs Affectations (1:*)
•	Un Prestataire peut avoir plusieurs Affectations (1:*)
•	Une Affectation peut générer plusieurs Factures et EntreeSorties (1:*)
•	Une ville peut être ville de destination pour plusieurs factures(1:*)

c.	Diagramme de séquence (création de facture )
                                  Figure 5 : Diagramme de séquence
Explication du Diagramme de Séquence :
Le diagramme de séquence illustre le processus de création d'une facture dans le système de gestion de transport. Il montre les interactions entre les différents composants du système lors de la génération d'une facture. Voici une description détaillée du flux :
	Acteurs et Objets
	Administrateur : Utilisateur qui initie la création de la facture
	Formulaire Facture : Interface utilisateur pour la saisie des données
	Système Django : Framework backend qui traite les requêtes
	Modèle Facture : Classe métier contenant la logique de calcul
	API Nomination : Service externe pour la géolocalisation
	Flux de Séquence
1. Saisie des Informations
•	L'Administrateur (admin ou user admin) saisit les informations de base dans le Formulaire Facture : 
o	Informations du camion
o	Poids de la marchandise
o	Destination de livraison
o	Autres détails nécessaires
2. Soumission du Formulaire
•	Le Formulaire Facture envoie une requête POST /facture/ au Système Django
•	Cette requête contient toutes les données saisies par l'administrateur
3. Création de l'Instance Facture
•	Le Système Django instancie un nouvel objet Modèle Facture avec new Facture()
•	Les données du formulaire sont transférées vers le modèle
4. Géocodage de la Destination
•	Le Modèle Facture appelle la méthode geocoder_destination()
•	Cette méthode fait appel à l'API Nomination pour obtenir les coordonnées GPS de la destination
•	L'API Nomination retourne les coordonnées (latitude/longitude)
5. Calculs Automatiques
•	Le Modèle Facture effectue plusieurs calculs en séquence : 
o	calculer_distance() : Calcule la distance entre le point de départ et la destination
o	calculer_frais() : Calcule les frais de transport basés sur la distance et le poids
6. Sauvegarde
•	Le Modèle Facture exécute la méthode save() pour enregistrer la facture en base de données
•	Une confirmation "Facture enregistrée" est retournée au Système Django
Points Clés du Processus
•	Automatisation : Les calculs de distance et de frais sont automatiques
•	Intégration externe : Utilisation d'une API de géolocalisation pour la précision
•	Validation : Le système valide les données avant la sauvegarde
•	Feedback utilisateur : Confirmation visuelle de la création de la facture

d.	Diagramme d’activité (Scan code Qr) 
                              Figure 6 : Diagramme d’activité
Explication du Diagramme d'Activité - Système de Scan QR : 
Le diagramme d'activité illustre le processus complet de gestion des entrées et sorties de camions via la lecture de codes QR. Il représente un flux de contrôle d'accès automatisé avec validation des données.
	Initialisation
o	État initial : Système en attente.
o	Scanner activé et prêt pour lecture du QR code.
	Scan & Validation
o	Scan déclenché par l'utilisateur.
•	QR détecté ?
o	Oui → Vérification des données.
o	Non → Message d'erreur, retour à l'attente.
•	Données valides ?
o	Oui → Enregistrement.
o	Non → Erreur, retour au début.
	Enregistrement Entrée
•	Stockage de :
o	Date et heure d’entrée.
o	Données enregistrées en base.
	Attente de Sortie
•	Attente d’un nouveau scan de sortie.
	Gestion de Sortie
•	Nouveau scan QR pour sortie.
•	QR correspond à l’entrée ?
o	Oui → Sortie enregistrée.
o	Non → Erreur, retour au début.
•	Stockage de :
o	Date et heure de sortie.
o	Durée de stationnement calculée automatiquement
	Gestion des Erreurs
•	Messages d’erreur en cas de :
o	QR non détecté.
o	QR invalide ou incohérent.
o	QR différent à la sortie.

	Fonctionnalités Clés
o	Automatisation : Scan, validation, horodatage, calculs.
o	Traçabilité : Historique complet.
o	Sécurité : Double vérification QR, détection fraude.

IV.	Réalisation et Développement
1.	Architecture et Environnement Technique
a.	Architecture Frontend
	Langages utilisés :
o	HTML5 pour la structure sémantique des pages.
o	CSS3 pour le style et la mise en page responsive
o	Javascript Vanilla pour l’interactivité côté client
	 Frameworks : 
o	Utilisation de Bootstrap(v3.1.4) pour interface moderne et responsive.
	Moteur de templates : 
o	Django Templates pour la génération dynamique des page HTML et l’intégration des données Python.
b.	Architecture Backend
	Framework Python :
o	Django (Python) avec l’architecture MTV (Modèle-Template-Vue).
	Gestion des routes : 
o	Urls.py pour le routage des requêtes HTTP
	Logique métier : 
o	Views.py et forms.py 
	ORM :
o	Django ORM pour la gestion de la base de données
	API REST :
o	Interface de communication via HTTP (méthodes,GET,POST,PUT,DELETE)

c.	Structure des Applications
•	Application principale : app
•	Modèles : models.py
•	Vues : views.py
•	Formulaires : forms.py
•	Templates : nombreux fichiers HTML organisés par fonctionnalité (afficher_chauffeur.html, générer_bdg.html…).
•	Migrations : gestion de l’évolution du schéma de la base.
•	Modèle MTV (spécifique à Django) : 
o	Modèle (Model) : gestion des données et de la base. 
o	Template : rendu des pages HTML. 
o	Vue (View) : logique métier et gestion des requêtes. 

d.	Intégrations
•	Génération et lecture de QR codes (qrcode, opencv-python, pyzbar).
•	Génération de PDF (reportlab, xhtml2pdf).
•	Utilisation de certificats SSL (cert.pem, key.pem) pour sécuriser les échanges.
•	Intégration de Bootstrap pour l’UI.
•	SQLite (relationnelle, légère, stockage fichier unique, transactions ACID). 
e.	Organisation des Ressources
•	Dossiers media et static pour les fichiers utilisateurs et ressources statiques.
•	Dossier qr_codes pour les images QR générées.
•	Dossier facture dans templates pour la gestion des factures.
2.	Architecture logicielle envisagée
a.	Vue d’ensemble du système
Le projet consiste en une application web Django conçue pour la gestion d'une flotte de camions, incluant le suivi des chauffeurs, des véhicules et des prestataires. L'application intègre un système de badges avec QR codes pour l'identification et le suivi automatisé des entrées/sorties.
b.	Sécurité et certification
•	Certificats SSL (cert.pem/key.pem) pour l'activation du HTTPS
•	runserver_plus avec support SSL pour le développement sécurisé
•	Protection CSRF intégrée dans Django
•	Authentification obligatoire pour l'accès aux fonctionnalités
•	Gestion des rôles et contrôle d'accès
3.	Environnement de développement 
a.	Visual Studio Code (éditeur principal) 
Visual Studio Code (VS Code) est un éditeur de code source léger et puissant, développé par Microsoft.
	Extensions Python & Django 
	Terminal intégré pour commandes      (migrations, runserver…) 
	Débogueur, linters, formatters 

b.	DB Browser for SQLite 
DB Browser for SQLite est un outil open source qui permet aux utilisateurs de créer, concevoir et éditer des fichiers de base de données SQLite. Il offre une interface graphique intuitive qui facilite l'interaction avec les bases de données sans nécessiter de connaissances approfondies en SQL.
•	Exploration des données : Visualiser et modifier les tables et les enregistrements.
•	Conception de bases de données : Créer de nouvelles bases de données et définir des tables, des champs et des relations.
•	Exécution de requêtes SQL : Écrire et exécuter des requêtes SQL pour interroger les données.
•	Importation/Exportation : Importer et exporter des données dans divers formats, comme CSV ou SQL.
c.	Git & GitHub 
Git est un outil de gestion de versions permettant de suivre les modifications du code, de créer des branches et de revenir à des versions précédentes.
GitHub est une plateforme en ligne pour héberger les dépôts Git et faciliter la collaboration (pull requests, issues, sauvegarde).
Dans le projet :
•	Dépôt Git local initialisé dans le dossier du projet
•	Commits réguliers et descriptifs
•	Synchronisation avec GitHub pour partager et collaborer
•	Travail en équipe via des branches pour les fonctionnalités et corrections
•	Historique complet du projet pour un bon suivi et une maintenance simplifiée

4.	Technologies Utilisées
a.	Framework et Langages
	Python
Python est un langage de programmation interprété, simple et polyvalent. Il est utilisé dans plusieurs domaines comme le développement web, l’analyse de données, l’IA et l’automatisation.
•	Caractéristiques principales :
•	Syntaxe claire : facile à lire et écrire.  
•	Grande bibliothèque standard : pour de 
nombreuses tâches.
•	Communauté active : riche en ressources et bibliothèques externes.
•	Multiplateforme : fonctionne sur Windows, macOS, Linux.
Sa simplicité en fait un langage idéal pour débutants et professionnels.
	Django
Framework web open source écrit en Python, utilisant une architecture MVC (Modèle-Vue-Contrôleur) :
•	Rapidité de développement : Structure bien définie et outils intégrés
•	Sécurité : Protections contre injections SQL et attaques CSRF
•	Administration automatique : Interface d'administration générée automatiquement
•	Évolutivité : Convient aux projets de petite à grande envergure
	HTML / CSS / JAVASCRIPT
•	HTML5
Langage de balisage pour structurer le contenu des pages web.
•	Balises sémantiques : <article>, <section>, etc.
•	Support multimédia : images, vidéos, formulaires
•	Base de tout site web
o	CSS3
Langage de style pour l’apparence des pages HTML.
•	Séparation contenu/style
•	Animations, transitions, effets visuels
•	Responsive design (media queries, flexbox)
o	JavaScript (Vanilla)
Langage de script côté client pour l’interactivité.
•	Interprété dans le navigateur
•	Dynamique & asynchrone
•	Utilisé avec ou sans frameworks (React, Vue...)
•	Utilisable aussi côté serveur (Node.js)
	Bootstrap (3.1.4)
Framework CSS responsive pour créer rapidement des interfaces modernes.
•	Composants préconçus (boutons, alertes, modals…)
•	Grille responsive
•	Design mobile-first
	SQLITE 
SQLite est un système de gestion de base de données relationnelle léger qui est intégré par défaut dans Django. Voici quelques caractéristiques clés de SQLite dans le contexte de Django :
•	Configuration simple : Nécessite peu de configuration pour commencer, ce qui le rend idéal pour le développement et les tests.
•	Fichier unique : Stocke toutes les données dans un seul fichier, facilitant la gestion et le déploiement.
•	Transactions ACID : Assure que les opérations sur la base de données sont atomiques, cohérentes, isolées et durables.
•	Support SQL : Utilise le langage SQL pour les requêtes, permettant d'interagir facilement avec les données.
•	Multiplateforme : Fonctionne sur tous les systèmes d'exploitation pris en charge par Django.








5.	Bibliothèques et Extensions Python
a.	Extensions Django
•	django : Framework principal avec modules standards (admin, auth, contenttypes, sessions, messages, staticfiles)
•	django_extensions : Outils et commandes avancées pour Django
•	corsheaders : Gestion des CORS (Cross-Origin Resource Sharing)
•	django-crispy-forms : Gestion avancée des formulaires (optionnel)

b.	Bibliothèques externes spécialisées
•	qrcode : Génération de QR codes pour les badges d'identification
•	opencv-python et pyzbar : Lecture de QR codes via la caméra
•	reportlab et xhtml2pdf : Génération de fichiers PDF
•	weasyprint : Génération de PDF à partir de HTML/CSS
•	pytz : Gestion avancée des fuseaux horaires
•	Pillow : Manipulation et traitement d'images
•	requests : Requêtes HTTP
•	geopy.distance : Calcul de distances géographiques

c.	Modules Python standards utilisés
•	os : Manipulation du système de fichiers
•	pathlib : Manipulation avancée des chemins de fichiers
•	base64 : Encodage/décodage en base64 pour les images
•	io et BytesIO : Manipulation de flux de données binaires
•	datetime et timedelta : Gestion des dates et durées
•	json : Manipulation de données JSON
•	re : Expressions régulières
•	ssl : Sécurisation HTTPS via certificats

d.	Modules Django spécifiques
•	django.core.files,django.core.validators,django.core.exceptions : Manipulation de fichiers, validation et gestion des erreurs
•	django.db.models : Modélisation des données et gestion des migrations
•	django.shortcuts, django.urls, django.http : Fonctions utilitaires pour vues, URLs et réponses HTTP
•	django.template.loader : Rendu de templates
•	django.views.decorators.csrf, django.contrib.auth.decorators : Sécurité et gestion des accès
•	django.contrib.auth : Authentification et gestion des utilisateurs

e.	Extensions et outils front-end
•	Bootstrap : Framework CSS pour interface moderne et responsive
•	jQuery : Facilitation du DOM scripting (optionnel)
•	FontAwesome : Bibliothèque d'icônes

f.	Autres outils
•	Certificats SSL pour le HTTPS
•	Outils de migration (makemigrations, migrate)
•	Interface d'administration Django pour la gestion avancée

6.	Implémentation des Fonctionnalités Principales
a.	Gestion des entités
	CRUD complet (Créer, Lire, Mettre à jour, Supprimer) pour :
•	Camions
•	Chauffeurs
•	Utilisateurs
•	Prestataires
	Interface d'administration Django :
•	Permet la gestion avancée de toutes les entités via l’admin intégré.
•	Possibilité de filtrer, trier et rechercher les enregistrements.
	Systèmes de recherche et de filtres :
•	Recherche par critères (nom, matricule, société, etc.)
•	Filtres dynamiques sur les listes pour une navigation rapide.
b.	 Affectations
	Interface dédiée pour associer un chauffeur à un camion.
	Historique des affectations :
•	Conservation de toutes les associations passées (traçabilité totale).
•	Visualisation des affectations en cours et passées.
	Suivi en temps réel :
•	Mise à jour instantanée des associations véhicule-conducteur.
c.	 Entrées/Sorties
	Enregistrement automatique :
•	Scan du QR code du badge pour valider l’entrée ou la sortie d’un véhicule.
	Saisie manuelle :
•	Alternative pour gérer les cas où le QR code n’est pas disponible.
	Horodatage précis :
•	Prise en compte du fuseau horaire (Afrique/Casablanca).
	Gestion avancée :
•	Suivi des entrées non fermées, validation stricte des sorties.
•	Contrôles de cohérence pour éviter les erreurs de saisie 
d.	 Facturation
	Génération de factures PDF à partir des affectations et des temps d’utilisation.
	Calcul automatique :
•	Tarification basée sur la durée d’affectation, les tarifs définis, et les prestations associées.
	Visualisation, export et impression des factures depuis l’interface.
	Historique et suivi des paiements :
•	Statut payé/non payé, relances, archivage.
e.	 Badges et QR codes
	Génération automatique de badges PDF :
•	Chaque affectation génère un badge unique avec QR code.
	Lecture du QR code via webcam :
•	Automatisation de l’enregistrement des entrées/sorties.
	Identification unique et sécurisée :
•	Chaque badge correspond à une affectation précise.
	Personnalisation :
•	Possibilité d’adapter le design ou les informations affichées sur le badge.
f.	 Authentification et rôles
	Gestion des utilisateurs avec profils personnalisés.
	Système de rôles :
•	Administrateur, utilisateur standard, etc.
	Sécurisation des pages sensibles :
•	Accès restreint par authentification obligatoire.
	Contrôle d’accès granulaire :
•	Permissions spécifiques selon le rôle et les fonctionnalités.
g.	Tableau de bord et recherche
	Page d’accueil synthétique :
•	Accès rapide aux principales fonctionnalités.
	Tableaux de bord en temps réel :
•	Suivi des affectations, entrées/sorties, facturation, etc.
	Recherche avancée et filtres :
•	Recherche multi-critères sur toutes les entités.
	Statistiques et indicateurs :
•	Visualisation de la performance, alertes, synthèses.
h.	 Sécurité et traçabilité
	Authentification obligatoire pour toutes les fonctionnalités sensibles.
	Journalisation des actions critiques :
•	Audit des modifications importantes (affectations, factures, créations/suppressions…).
	Utilisation du HTTPS pour toutes les communications.
	Gestion des sessions et protection contre les attaques (CSRF, XSS, etc.).
	Sauvegarde et restauration des données :
•	Procédures régulières pour garantir l’intégrité et la disponibilité des données.

7.	 Capture d’écran de quelque interface
 
 

  
	 
V.	Conclusion
Ce chapitre a présenté de manière exhaustive la conception et la réalisation de l'application de gestion des entrées-sorties de camions pour la société. L'analyse approfondie des besoins a permis d'identifier les problématiques clés de l'entreprise et de définir des solutions technologiques adaptées.
La démarche méthodologique adoptée, allant de l'analyse des besoins fonctionnels et non fonctionnels à la conception détaillée via les diagrammes UML (cas d'utilisation, classes, séquence et activité), a garanti une approche structurée et rigoureuse du développement. Cette phase de conception a notamment mis en évidence la complexité des interactions entre les différentes entités du système et l'importance de la traçabilité dans les processus logistiques.
L'architecture technique retenue, basée sur le framework Django et son modèle MTV, s'est révélée particulièrement adaptée aux exigences du projet. L'intégration de technologies complémentaires (QR codes, génération PDF, géolocalisation) a permis d'automatiser et de moderniser les processus manuels existants. L'utilisation de SQLite comme système de gestion de base de données, couplée aux outils de développement modernes (VS Code, Git/GitHub), a facilité le développement rapide et efficace de l'application.
L'implémentation des fonctionnalités principales démontre la capacité du système à répondre aux objectifs fixés : centralisation de la gestion logistique, automatisation des processus, amélioration de la traçabilité et renforcement de la sécurité. Le système de gestion des rôles et d'authentification garantit un contrôle d'accès approprié selon les responsabilités de chaque utilisateur.
Cette réalisation constitue une base solide pour la modernisation des processus logistiques de la société, offrant un système évolutif capable de s'adapter aux besoins futurs de l'entreprise. Les technologies utilisées et l'architecture modulaire mise en place facilitent la maintenance et permettent d'envisager sereinement les évolutions futures du système.

