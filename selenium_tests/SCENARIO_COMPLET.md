# Scénario E2E Complet - Mon Panier Local

## PHASE 1 : Producteur crée son compte et remplit tout

### 1.1 Inscription producteur
1. Aller sur la page d'accueil (clic logo ou /)
2. Cliquer sur "Inscription" dans la navbar
3. Remplir Email : `producer_scenario_XXX@test.com`
4. Remplir Nom d'utilisateur : `producer_scenario_XXX`
5. Remplir Mot de passe : `TestPassword123!`
6. Remplir Confirmer mot de passe : `TestPassword123!`
7. Cocher "Je suis un producteur"
8. Cliquer "S'inscrire"
9. Vérifier redirection vers /login

### 1.2 Connexion producteur
10. Remplir Email
11. Remplir Mot de passe
12. Cliquer "Se connecter"
13. Vérifier redirection vers / (accueil)
14. Vérifier présence "Mon Profil" et "Mon Exploitation" dans la navbar

### 1.3 Création exploitation - Onglet Mon exploitation
15. Cliquer "Mon Exploitation" dans la navbar
16. Remplir "Nom de l'exploitation" : `Ferme Test Scenario`
17. Remplir "Description" : `Description complète de ma ferme de test`
18. Sélectionner "Activité principale" : Maraîchage (ou autre)
19. Cliquer "Enregistrer"
20. Attendre message "Exploitation créée" ou "Sauvegardé"

### 1.4 Onglet Localisation
21. Cliquer onglet "Localisation"
22. Saisir dans "Rechercher une adresse" : `Paris, France`
23. Attendre les suggestions
24. Cliquer sur une suggestion (ex: Paris, France)
25. Vérifier que la carte affiche un marqueur
26. OU cliquer sur "Utiliser ma position GPS" (si autorisé)
27. Vérifier que "Position" s'affiche avec lat/lng
28. Cliquer "Enregistrer"

### 1.5 Onglet Mon exploitation - Photos
29. Revenir à l'onglet "Mon exploitation"
30. Section "Photos de l'exploitation"
31. Cliquer sur le champ fichier / "Ajouter une photo"
32. Sélectionner un fichier image (JPEG/PNG)
33. Vérifier que la photo s'affiche dans la grille
34. (Optionnel) Supprimer une photo : survoler, cliquer "Supprimer", confirmer

### 1.6 Onglet Produits
35. Cliquer onglet "Produits"
36. Remplir "Nom du produit" : `Tomates bio`
37. Sélectionner "Catégorie" : Légumes
38. Remplir "Description" : `Belles tomates`
39. Sélectionner "Période" : Période personnalisée
40. Sélectionner "Mois de début" : Juin
41. Sélectionner "Mois de fin" : Octobre
42. Cliquer "Ajouter le produit"
43. Vérifier que le produit apparaît dans la liste
44. Sur le produit : cliquer "Modifier", modifier le nom, cliquer "Enregistrer"
45. Sur le produit : cliquer "+ Ajouter photo", sélectionner image
46. Vérifier la photo du produit
47. (Optionnel) Supprimer une photo produit : survoler, cliquer ×
48. Ajouter un 2e produit "Salades" (tout l'année)
49. Cliquer "Enregistrer" si visible

### 1.7 Onglet Points de vente
50. Cliquer onglet "Points de vente"
51. Cliquer "Ajouter un mode de vente" (ou équivalent)
52. Sélectionner type : "Vente sur place / point de vente"
53. Remplir "Titre" : `Vente à la ferme`
54. Remplir "Consignes" : `Paiement CB accepté`
55. Remplir les horaires (Lundi fermé, Mardi 9h-18h, etc.)
56. Cliquer "Enregistrer" / "Sauvegarder"
57. Vérifier le mode apparaît
58. Ajouter un 2e mode : "Commande par téléphone"
59. Remplir "Téléphone" : `0612345678`
60. Remplir titre et consignes
61. Sauvegarder
62. (Optionnel) Modifier ou supprimer un mode

### 1.8 Onglet Contact
63. Cliquer onglet "Contact"
64. Remplir "Téléphone" : `06 12 34 56 78`
65. Remplir "Email de contact" : `contact@fermetest.fr`
66. Remplir "Site web" : `https://www.fermetest.fr`
67. Remplir "Horaires d'ouverture" : `Lundi-Vendredi 9h-18h`
68. Cliquer "Enregistrer"

---

## PHASE 2 : Utilisateur crée son compte et consulte

### 2.1 Déconnexion producteur
69. Cliquer "Mon Profil" dans la navbar
70. Cliquer "Se déconnecter"

### 2.2 Inscription utilisateur
71. Cliquer "Inscription" dans la navbar
72. Remplir Email : `user_scenario_XXX@test.com`
73. Remplir Nom d'utilisateur : `user_scenario_XXX`
74. Remplir Mot de passe : `TestPassword123!`
75. Confirmer mot de passe
76. NE PAS cocher "Je suis un producteur"
77. Cliquer "S'inscrire"
78. Vérifier redirection vers /login

### 2.3 Connexion utilisateur
79. Se connecter avec les identifiants utilisateur
80. Vérifier accueil - pas de "Mon Exploitation" (utilisateur simple)

### 2.4 Navigation accueil - Carte et liste
81. Sur la page d'accueil : vérifier que la carte s'affiche
82. Cliquer sur le toggle "Liste" pour passer en vue liste
83. Vérifier que les producteurs s'affichent en liste
84. Cliquer sur "Carte" pour revenir à la vue carte
85. Vérifier la sidebar (filtres, recherche)

### 2.5 Recherche et filtres
86. Saisir dans la barre de recherche (si présente) un nom de ville ex: `Paris`
87. Cliquer "Rechercher" ou équivalent
88. Vérifier les résultats
89. Cocher une catégorie dans la sidebar (ex: Maraîchage)
90. Vérifier le filtrage
91. Décocher ou sélectionner "Tous"

### 2.6 Consultation exploitation
92. Cliquer sur un producteur sur la carte ou dans la liste
93. Ou aller directement sur /producers/[id] si lien visible
94. Vérifier la page détail : nom, catégorie, description, photos
95. Vérifier la section Produits
96. Vérifier la section Points de vente / Modes de vente
97. Vérifier les horaires
98. Cliquer "Retour à la carte"
99. Vérifier retour à l'accueil

### 2.7 Navigation footer et pages
100. Cliquer "À propos" dans le footer
101. Vérifier page /about
102. Cliquer sur le logo pour revenir à l'accueil
103. Cliquer "Nous contacter" ou "Contact"
104. Vérifier page /contact
105. Revenir à l'accueil

### 2.8 Profil utilisateur
106. Cliquer "Mon Profil"
107. Vérifier affichage email, username, type "Utilisateur"
108. Cliquer "Modifier mon profil"
109. Modifier le nom d'utilisateur
110. Cliquer "Enregistrer"
111. Vérifier la mise à jour
112. Cliquer "Annuler" si en mode édition

---

## PHASE 3 : Producteur supprime son compte et exploitation

### 3.1 Reconnexion producteur
113. Se déconnecter (si connecté en tant qu'utilisateur)
114. Se connecter avec le compte producteur

### 3.2 Suppression exploitation (optionnel si suppression compte inclut)
115. Aller sur "Mon Exploitation"
116. (Si bouton "Supprimer mon exploitation" existe) Cliquer et confirmer
117. OU : la suppression du compte supprimera l'exploitation

### 3.3 Suppression compte producteur
118. Aller sur "Mon Profil"
119. Faire défiler jusqu'à la section "Supprimer mon compte"
120. Cliquer "Supprimer mon compte"
121. Remplir le mot de passe de confirmation
122. Cliquer "Confirmer la suppression"
123. Vérifier redirection vers / ou /login
124. Vérifier que le compte n'existe plus (tentative de connexion échoue)

---

## PHASE 4 : Utilisateur supprime son compte

### 4.1 Reconnexion utilisateur
125. Se connecter avec le compte utilisateur

### 4.2 Suppression compte utilisateur
126. Aller sur "Mon Profil"
127. Section "Supprimer mon compte"
128. Cliquer "Supprimer mon compte"
129. Remplir mot de passe de confirmation
130. Confirmer la suppression
131. Vérifier déconnexion et impossibilité de se reconnecter

---

## Fonctionnalités implémentées

- [x] API POST /api/auth/delete-account/ (backend)
- [x] Bouton "Supprimer mon compte" dans la page Profil (frontend)
- [x] Formulaire de confirmation avec mot de passe
- [x] Suppression en cascade : User delete -> ProducerProfile, Products, Photos, SaleModes

## Lancer les tests

```bash
# 1. Démarrer l'application (Docker ou dev)
cd infra && docker compose -f docker-compose.prod.yml --env-file ../.env up -d
# OU: backend (manage.py runserver) + frontend (npm run dev)

# 2. Exécuter le scénario complet
cd selenium_tests
pip install -r requirements.txt
# TEST_BASE_URL et TEST_API_URL selon votre setup (ex: http://localhost:3000 ou http://localhost)
TEST_BASE_URL=http://localhost:3000 TEST_API_URL=http://localhost:3000 pytest test_scenario_complet.py -v
```
