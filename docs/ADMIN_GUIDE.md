# Guide d'administration

Ce guide explique comment utiliser le panneau d'administration pour gérer le site.

## Connexion

1. Allez sur `/admin`
2. Entrez votre identifiant et mot de passe (configurés dans les variables d'environnement)
3. Cliquez sur "Connexion"

## Tableau de bord

La page d'accueil admin affiche :

- **Statistiques principales** : nombre de pharmacies, pharmacies de garde, soumissions en attente
- **Graphiques** : fréquentation sur 7 et 30 jours, répartition par ville et par type
- **Pharmacies populaires** : les plus consultées

## Gestion des pharmacies

### Ajouter une pharmacie

1. Cliquez sur "Ajouter une pharmacie"
2. Remplissez les champs :
   - Code (identifiant court, ex: LBV001)
   - Nom
   - Ville
   - Quartier/adresse
   - Téléphone
   - Horaires
   - Services proposés
3. Optionnel : ajoutez les coordonnées GPS
4. Cliquez sur "Enregistrer"

### Modifier une pharmacie

1. Trouvez la pharmacie dans la liste
2. Cliquez sur l'icône crayon
3. Modifiez les champs souhaités
4. Enregistrez

### Supprimer une pharmacie

1. Cliquez sur l'icône poubelle
2. Confirmez la suppression

### Gérer les gardes

**Activation rapide :** Cliquez sur le badge "garde" pour activer/désactiver instantanément.

**Avec période programmée :**
1. Cliquez sur "Gérer la garde"
2. Sélectionnez la date de début
3. Le système propose automatiquement une durée de 7 jours
4. Confirmez

## Soumissions des utilisateurs

Les visiteurs peuvent soumettre des corrections. Vous devez les valider.

### Localisations GPS

Un utilisateur a proposé des coordonnées pour une pharmacie.

1. Allez dans "Localisations en attente"
2. Comparez sur la carte la position actuelle et celle proposée
3. Si correct : cliquez sur "Approuver" (les coordonnées sont mises à jour)
4. Sinon : cliquez sur "Rejeter"

### Corrections d'informations

Un utilisateur signale qu'un numéro ou un horaire est faux.

1. Allez dans "Corrections en attente"
2. Vérifiez l'information (valeur actuelle vs proposée)
3. Approuvez ou refusez

### Suggestions

Un utilisateur envoie une idée ou un commentaire.

1. Lisez le message
2. Répondez si nécessaire
3. Archivez une fois traité

### Nouvelles pharmacies

Un utilisateur propose d'ajouter une pharmacie.

1. Vérifiez qu'elle n'existe pas déjà
2. Contrôlez les informations fournies
3. Si valide : approuvez (la pharmacie est créée automatiquement)
4. Sinon : refusez

## Contacts d'urgence

### Consulter la liste

Menu "Contacts d'urgence" : affiche tous les numéros (nationaux en premier, puis par ville).

### Ajouter un contact

1. Cliquez sur "Ajouter un contact"
2. Choisissez le type de service (police, pompiers, hôpital...)
3. Renseignez le nom, le(s) numéro(s), l'adresse si pertinent
4. Indiquez si c'est un service national ou local (avec ville)
5. Définissez l'ordre d'affichage (1 = premier)
6. Enregistrez

### Modifier ou supprimer

Utilisez les icônes crayon ou poubelle sur chaque ligne.

## Paramètres du site

### Informations générales

- Nom du site
- Description (pour le référencement)
- Email et téléphone de contact

### Apparence

Uploadez vos fichiers :
- Logo (affiché dans l'en-tête)
- Favicon (icône du navigateur)
- Image de partage (pour les réseaux sociaux)

Pour supprimer un fichier : cochez "Supprimer" puis enregistrez.

### Référencement (SEO)

- Titre Open Graph
- Description Open Graph
- Mots-clés
- ID Google Analytics
- Code personnalisé à insérer dans l'en-tête

## Popups

Les popups sont des messages affichés aux visiteurs.

### Créer un popup

1. Menu "Popups" puis "Nouveau popup"
2. Renseignez :
   - Titre
   - Description (texte principal)
   - Avertissement (optionnel, apparaît en encadré jaune)
   - Image (optionnel)
3. Options :
   - Actif : active ou non le popup
   - Afficher une seule fois : le visiteur ne le verra qu'une fois
   - Ordre : si plusieurs popups, lequel s'affiche en premier
4. Enregistrez

### Gérer les popups

- Cliquez sur le badge pour activer/désactiver
- Modifiez ou supprimez avec les icônes

## Publicités

### Créer une publicité

1. Menu "Publicités" puis "Ajouter"
2. Contenu :
   - Titre
   - Description
   - Type de média : image ou vidéo
   - Fichier image OU URL vidéo
3. Appel à l'action :
   - Texte du bouton ("En savoir plus", "Profiter"...)
   - URL de destination
4. Options :
   - Délai avant "Passer" (en secondes)
   - Priorité (plus élevée = plus souvent affichée)
   - Dates de début et fin
   - Actif ou non
5. Enregistrez

### Statistiques

Chaque pub affiche :
- Nombre de vues
- Nombre de clics
- Taux de clic

### Configuration globale

Menu "Réglages pubs" :

**Activation**
- Activer/désactiver toutes les pubs d'un coup

**Déclencheur**
- Temps : la pub s'affiche après X secondes
- Nombre de pages : après X pages visitées
- Rechargement : quand la page est rafraîchie

**Limites**
- Maximum par session : combien de pubs au total
- Pause après "Passer" : combien de secondes avant la prochaine
- Pause après clic : idem après un clic sur le bouton
- Affichage mobile/desktop : activer ou non selon l'appareil

## Bonnes pratiques

### Qualité des données

- Vérifiez toujours avant d'approuver une soumission
- Complétez un maximum de champs quand vous ajoutez une pharmacie
- Validez les GPS sur la carte

### Gestion des gardes

- Planifiez les gardes en début de semaine
- Assurez une couverture géographique équilibrée
- Pensez à désactiver les gardes expirées

### Relations avec les utilisateurs

- Répondez aux suggestions (même brièvement)
- Traitez rapidement les corrections valides
- Utilisez les popups pour les annonces importantes

### Sécurité

- Utilisez un mot de passe fort
- Déconnectez-vous après chaque session
- Ne partagez pas vos identifiants

## Problèmes courants

**Je ne peux pas me connecter**
- Vérifiez les variables ADMIN_USERNAME et ADMIN_PASSWORD
- Effacez les cookies du navigateur

**La carte ne s'affiche pas**
- Vérifiez votre connexion internet
- Rechargez la page

**L'upload d'image échoue**
- Formats acceptés : PNG, JPG, JPEG, GIF, WEBP, SVG, ICO
- Taille maximale : 10 Mo

**Mes modifications n'apparaissent pas**
- Videz le cache du navigateur
- Rechargez la page

**Les pubs ne s'affichent pas**
- Vérifiez que "Activer les publicités" est coché
- Vérifiez qu'au moins une pub est active
- Contrôlez les dates de diffusion
