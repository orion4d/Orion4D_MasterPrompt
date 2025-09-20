# Orion4D MasterPrompt Suite for ComfyUI

Bienvenue dans la suite **MasterPrompt**, une collection de nodes personnalisés pour ComfyUI conçus pour suralimenter vos workflows de manipulation de texte, de listes et de JSON. Que vous ayez besoin de charger dynamiquement des styles depuis des fichiers, de mixer des concepts de manière pondérée, de formater des prompts complexes ou de manipuler des données JSON, cette suite vous offre les outils nécessaires avec des interfaces utilisateur intuitives et puissantes.

<img width="2082" height="962" alt="image" src="https://github.com/user-attachments/assets/a2624a84-1723-49ef-965a-8e34ab25aa58" />

## ✨ Fonctionnalités Principales

-   **Gestion de Fichiers Avancée** : Naviguez dans vos dossiers, lisez des fichiers `.txt` et `.csv` et fusionnez-les sans effort.
-   **Interfaces Utilisateur Dynamiques** : De nombreux nodes disposent d'interfaces personnalisées qui s'actualisent en temps réel, sans recharger le navigateur.
-   **Mixage Pondéré** : Contrôlez la probabilité de sélection de différents éléments textuels grâce à un système de "température" intuitif.
-   **Boîte à Outils Texte Complète** : Remplacez, formatez, éditez, et enveloppez du texte avec des options précises.
-   **Puissance JSON** : Fusionnez, formatez, extrayez des données et convertissez des structures JSON directement dans vos workflows.
-   **Intégration Transparente** : S'intègre parfaitement à ComfyUI, avec des entrées/sorties standard pour une connexion facile à d'autres nodes.

## ⚙️ Installation

1.  Naviguez jusqu'à votre dossier `custom_nodes` de ComfyUI.
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Clonez ce dépôt.
    ```bash
    git clone https://github.com/orion4d/Orion4D_MasterPrompt.git
    ```
3.  Redémarrez ComfyUI.

Les nodes seront disponibles dans le menu `Add Node > MasterPrompt`.

---

## 📖 Guide des Nodes

Voici une description détaillée de chaque node disponible dans la suite MasterPrompt.

### 🗂️ Section 1 : Gestion de Fichiers et de Listes

Ces nodes sont spécialisés dans la lecture et la manipulation de fichiers texte et CSV.

#### 📂 MP • List Selector Pro
Ce node est un explorateur de fichiers simple et efficace, confiné au dossier `ComfyUI/custom_nodes/Orion4D_MasterPrompt/lists`, pour sélectionner une ligne dans un fichier.

-   **Objectif** : Choisir une ligne spécifique ou aléatoire à partir de listes prédéfinies (`.txt` ou `.csv`). Idéal pour sélectionner des styles, des noms de personnages ou des concepts.
-   **Fonctionnalités Clés** :
    -   Navigation récursive dans les sous-dossiers.
    -   Deux modes : `select` (choix manuel) et `random` (tirage aléatoire basé sur un `seed`).
    -   Ajout facile de préfixes et suffixes.
    -   Mise à jour dynamique des listes déroulantes.
-   **Entrées** :
    -   `folder` : Menu déroulant pour choisir le dossier.
    -   `file` : Menu déroulant pour choisir le fichier dans le dossier sélectionné.
    -   `mode` : `select` ou `random`.
    -   `seed` : Graine pour le mode aléatoire.
    -   `selected_line` : Menu déroulant avec le contenu du fichier pour le mode `select`.
    -   `custom_prefix` / `custom_suffix` : Texte à ajouter avant/après.
-   **Sortie** :
    -   `selected_text` : La ligne choisie avec les ajouts.

#### 🎛️ MP • Multi List Mixer
Ce node permet de sélectionner aléatoirement une ligne à partir de *plusieurs* fichiers, en pondérant la probabilité de choisir chaque fichier.

-   **Objectif** : Créer des prompts variés en piochant dans différentes listes de concepts (ex: 70% de chance de piocher un style artistique, 30% un style de caméra).
-   **Fonctionnalités Clés** :
    -   Interface dynamique pour ajouter/supprimer des sources de fichiers.
    -   Contrôle de la "température" (poids) pour chaque fichier (0 à 10).
    -   Le tirage est en deux étapes : 1) choix du fichier selon les poids, 2) choix d'une ligne au hasard dans ce fichier.
    -   Tirage reproductible grâce au `seed`.
-   **Entrées** :
    -   `config_json` (caché) : Géré automatiquement par l'interface.
    -   `seed` : Graine pour le tirage aléatoire.
    -   `custom_prefix` / `custom_suffix` : Texte à ajouter.
-   **Sortie** :
    -   `mixed_text` : La ligne unique sélectionnée.

#### 🗃️ MP • Folder → Merge Lines
Parcourt un dossier (et ses sous-dossiers) pour fusionner le contenu de tous les fichiers `.txt` et `.csv` en une seule grande liste.

-   **Objectif** : Consolider de multiples fichiers de mots-clés, de styles ou de prompts négatifs en un seul texte, prêt à être utilisé ou sauvegardé.
-   **Fonctionnalités Clés** :
    -   Lecture récursive des dossiers.
    -   Options de nettoyage puissantes : suppression des doublons, des lignes vides, etc.
    -   Support CSV avancé : sélection d'une colonne spécifique et gestion de l'en-tête.
    -   Possibilité de sauvegarder le résultat dans un nouveau fichier.
-   **Entrées** :
    -   `folder` : Chemin du dossier à analyser.
    -   `recursive` : Inclure les sous-dossiers.
    -   `csv_column` : Index de la colonne à extraire des CSV (-1 pour la ligne entière).
    -   `deduplicate`, `skip_empty`... : Options de nettoyage.
    -   `save_output`, `save_folder`, `file_name` : Pour enregistrer le fichier fusionné.
-   **Sorties** :
    -   `merged_text` : Le texte contenant toutes les lignes fusionnées.
    -   `lines_count` : Le nombre total de lignes après traitement.
    -   `saved_path` : Le chemin complet du fichier sauvegardé.

#### 📜 MP • File TXT (Pro)
Un explorateur de fichiers complet et puissant pour naviguer sur votre disque, filtrer les fichiers et charger le contenu d'un fichier `.txt` ou `.csv`.

-   **Objectif** : Offrir une expérience de type "explorateur de fichiers" directement dans ComfyUI pour charger du texte, avec des outils de recherche et de tri.
-   **Fonctionnalités Clés** :
    -   Interface inspirée de navigateurs de fichiers.
    -   Navigation dans les dossiers (monter/descendre).
    -   Filtrage par expression régulière (regex) sur les noms de fichiers.
    -   Tri par nom ou par date de modification.
    -   Aperçu en double-cliquant, ouverture de l'explorateur système.
-   **Entrées** :
    -   `directory` : Le dossier de départ (peut être modifié via l'UI).
    -   `name_regex`, `sort_by`... (cachés) : Pilotés par l'interface graphique.
-   **Sorties** :
    -   `Txt` : Le contenu texte du fichier sélectionné.
    -   `file_path` : Le chemin absolu du fichier sélectionné.

---
### ✍️ Section 2 : Manipulation de Texte

Ces nodes sont votre couteau suisse pour transformer et nettoyer des chaînes de caractères.

#### 🔄 MP • Replace (Simple/Regex)
Un outil de recherche et remplacement simple mais puissant, avec un support pour les expressions régulières (regex) et les remplacements en masse via JSON.

-   **Objectif** : Effectuer des substitutions de texte, que ce soit pour corriger des erreurs, changer des mots-clés ou appliquer des transformations complexes.
-   **Fonctionnalités Clés** :
    -   Mode `simple` : Remplacement de texte littéral.
    -   Mode `regex` : Utilise des expressions régulières pour des remplacements avancés.
    -   Contrôle de la portée (`all` ou `first` occurrence).
    -   Options de sensibilité à la casse, `multiline` et `dotall` pour les regex.
    -   Mode `table_json` pour appliquer une série de remplacements en une seule fois.
-   **Entrées** :
    -   `text` : Le texte source.
    -   `find` / `replace` : Les chaînes à chercher et par quoi remplacer.
    -   `table_json` : Un objet JSON de type `{"mot_a_trouver": "remplacement", ...}`.
-   **Sorties** :
    -   `text_out` : Le texte après remplacement.
    -   `replacements` : Le nombre de substitutions effectuées.

#### 📝 MP • List Editor
Un pipeline complet pour nettoyer et restructurer des listes de texte (une ligne par item).

-   **Objectif** : Prendre un bloc de texte multiligne, le traiter comme une liste, et appliquer une série d'opérations de nettoyage, de tri et de modification.
-   **Fonctionnalités Clés** :
    -   Recherche/remplacement en début de pipeline.
    -   Suppression de préfixes/suffixes par nombre de caractères.
    -   Ajout de préfixes/suffixes à chaque ligne.
    -   Nettoyage : suppression des lignes vides et des doublons.
    -   Tri alphabétique (croissant/décroissant, sensible à la casse ou non).
    -   Sauvegarde optionnelle du résultat dans un fichier `.txt` ou `.csv`.
-   **Entrées** :
    -   `text_in` : La liste en entrée (séparée par des sauts de ligne).
    -   Toutes les options de traitement (find/replace, remove/add, sort, etc.).
-   **Sorties** :
    -   `text_out` : La liste finale, formatée en une seule chaîne de texte.
    -   `saved_path` : Le chemin du fichier sauvegardé, si l'option est activée.

#### 🔗 MP • Format (Named/Indexed)
Formate une chaîne de caractères en utilisant des arguments positionnels (`{0}`, `{1}`) et/ou nommés (`{name}`).

-   **Objectif** : Construire dynamiquement des prompts complexes en insérant des morceaux de texte à des endroits précis d'un modèle.
-   **Fonctionnalités Clés** :
    -   Supporte à la fois les placeholders comme `{0}` et `{nom}`.
    -   Jusqu'à 10 entrées positionnelles (`arg_0` à `arg_9`).
    -   Les arguments nommés peuvent être fournis via une chaîne JSON ou un dictionnaire Python.
    -   Politiques de gestion des clés manquantes (`strict`, `skip-missing`, `default-empty`).
-   **Entrées** :
    -   `format_string` : Le modèle de texte (ex: `photo of a {0}, in the style of {artist}`).
    -   `arg_0`...`arg_9` : Les entrées pour les placeholders positionnels.
    -   `kwargs_json` : Une chaîne JSON (`{"artist": "Van Gogh"}`) pour les placeholders nommés.
-   **Sorties** :
    -   `text_out` : Le texte final formaté.
    -   `diagnostic` : Informations sur le processus de formatage.

#### 🛀 MP • Wrap (Pairs/Custom)
Enveloppe un texte (ou chaque ligne d'un texte) avec des paires de caractères prédéfinies ou personnalisées.

-   **Objectif** : Ajouter rapidement des parenthèses, des guillemets ou tout autre délimiteur à un texte, utile pour ajuster l'emphase (poids) dans un prompt.
-   **Fonctionnalités Clés** :
    -   Nombreux styles prédéfinis : `()`, `[]`, `{}`, `""`, `« »`, etc.
    -   Mode `Custom` pour définir vos propres préfixe et suffixe.
    -   Option `per_line` pour appliquer l'enveloppement à chaque ligne individuellement.
    -   Options de nettoyage (`trim_lines`, `skip_if_empty`).
-   **Entrées** :
    -   `text` : Le texte à envelopper.
    -   `style` : Le style de paire à utiliser.
    -   `per_line` : Appliquer à chaque ligne ou au bloc entier.
-   **Sortie** :
    -   `wrapped_text` : Le texte enveloppé.

#### 📺 MP • Super Show Text
Un node d'affichage amélioré qui montre un aperçu du texte, peut numéroter les lignes et extraire des sélections spécifiques.

-   **Objectif** : Visualiser et déboguer facilement le contenu textuel à n'importe quelle étape d'un workflow, et extraire des parties d'une liste pour un traitement ultérieur.
-   **Fonctionnalités Clés** :
    -   Aperçu du texte directement dans le node.
    -   Peut lire directement un chemin de fichier `.txt` ou `.csv`.
    -   Numérotation optionnelle des lignes avec préfixe/suffixe personnalisables.
    -   Extraction de lignes par numéro ou plage (ex: `1-5`, `8`, `10-12`).
-   **Entrées** :
    -   `text` : Le texte à afficher (ou un chemin de fichier).
    -   `show_numbers` : Active la numérotation.
    -   `line_selector` : La chaîne de sélection de lignes.
-   **Sorties** :
    -   `text_out` : Le texte complet (numéroté si activé).
    -   `selected_text` : Uniquement les lignes sélectionnées.

---
### 🎭 Section 3 : Mixers Dynamiques

Ces nodes combinent plusieurs entrées de texte en une seule sortie, soit par assemblage, soit par tirage aléatoire.

#### 🎲 MP • Text Field Mixer
Combine plusieurs champs de texte en en choisissant un au hasard, pondéré par une "température". Similaire à `Multi List Mixer`, mais avec des champs de texte internes.

-   **Objectif** : Créer de la variété en choisissant aléatoirement parmi une liste de prompts ou de fragments de prompt que vous écrivez directement dans le node.
-   **Fonctionnalités Clés** :
    -   Interface dynamique pour ajouter/supprimer jusqu'à 12 champs de texte.
    -   Chaque champ a sa propre "température" (poids) de 0 à 10.
    -   Les champs peuvent être remplacés par des entrées externes (`ext_text_1`...).
    -   Si une entrée externe est connectée, le champ correspondant est verrouillé ("linked").
-   **Entrées** :
    -   `config_json` (caché) : Géré par l'UI.
    -   `seed` : Graine pour le tirage aléatoire.
    -   `ext_text_1`...`ext_text_12` (optionnel) : Pour connecter du texte depuis d'autres nodes.
-   **Sortie** :
    -   `mixed_text` : Le champ de texte unique sélectionné.

#### 🧩 MP • Text Prompt Mixer
Assemble de manière déterministe plusieurs champs de texte en utilisant des séparateurs personnalisés entre chaque champ.

-   **Objectif** : Construire un prompt final en concaténant plusieurs parties (ex: sujet, action, style, composition) avec un contrôle total sur les séparateurs.
-   **Fonctionnalités Clés** :
    -   Interface dynamique pour ajouter/supprimer jusqu'à 12 champs.
    -   Chaque champ possède son propre séparateur qui sera inséré *après* lui.
    -   Les champs peuvent être activés/désactivés ou remplacés par des entrées externes.
    -   Options de nettoyage (`trim`, `skip_empty`).
-   **Entrées** :
    -   `config_json` (caché) : Géré par l'UI.
    -   `ext_text_1`...`ext_text_12` (optionnel) : Entrées externes.
-   **Sorties** :
    -   `prompt_text` : Le texte final assemblé.
    -   `parts_used` : Le nombre de champs qui ont été utilisés.

---
### 📑 Section 4 : Boîte à Outils JSON

Une suite de nodes puissants pour manipuler des données structurées au format JSON.

#### 💅 MP • JSON Format (Prompt)
Prend une chaîne JSON brute et la formate joliment, la minifie ou l'échappe pour une utilisation sûre dans un prompt.

-   **Objectif** : Nettoyer ou préparer des données JSON pour qu'elles soient lisibles par un humain ou interprétables par un modèle de langage (LLM).
-   **Fonctionnalités Clés** :
    -   Analyseur tolérant (accepte les dictionnaires Python).
    -   Options de formatage : `pretty` (indenté), `sort_keys`, `compact_one_line`.
    -   Options d'échappement pour les prompts (`escape_newlines`, `escape_quotes`).
    -   Peut envelopper le résultat dans un bloc de code Markdown (```json...```).
-   **Entrée** :
    -   `json_in` : La chaîne JSON ou dictionnaire Python.
-   **Sortie** :
    -   `json_out` : Le JSON formaté.

#### 🤝 MP • JSON Merge (Deep)
Fusionne en profondeur (deep merge) de 2 à 5 objets JSON en un seul.

-   **Objectif** : Combiner plusieurs configurations ou structures de données. Par exemple, fusionner un JSON de base avec un JSON de patch.
-   **Fonctionnalités Clés** :
    -   Fusion récursive des dictionnaires.
    -   Politiques de fusion pour les listes : `replace` (remplacer), `concat` (concaténer), `unique` (concaténer en supprimant les doublons).
    -   Option pour supprimer les clés avec des valeurs `null` du résultat final.
-   **Entrées** :
    -   `json_1`...`json_5` : Les chaînes JSON à fusionner.
-   **Sortie** :
    -   `json_merged` : L'objet JSON résultant de la fusion.

#### 👉 MP • JSON Pick (Paths → Text)
Extrait une ou plusieurs valeurs d'un objet JSON en utilisant des chemins d'accès (ex: `user.name`, `items[0].price`).

-   **Objectif** : Récupérer des informations spécifiques d'une structure de données complexe pour les utiliser comme texte dans un prompt.
-   **Fonctionnalités Clés** :
    -   Syntaxe de chemin simple et intuitive (`key.subkey[index]`).
    -   Extraction de plusieurs valeurs en une seule fois (un chemin par ligne).
    -   Les valeurs extraites sont jointes avec un séparateur personnalisable.
-   **Entrées** :
    -   `json_in` : L'objet JSON source.
    -   `paths` : La liste des chemins à extraire, un par ligne.
    -   `joiner` : Le séparateur à utiliser entre les valeurs trouvées.
-   **Sorties** :
    -   `picked_text` : Le texte contenant les valeurs extraites.
    -   `hits_count` : Le nombre de chemins qui ont retourné une valeur.

#### ↔️ MP • JSON ↔︎ KV Lines
Convertit un objet JSON en une liste de lignes `clé: valeur` et vice-versa.

-   **Objectif** : Faciliter l'édition de données structurées dans un format texte simple ou convertir des fichiers de configuration de type `.ini` en JSON.
-   **Fonctionnalités Clés** :
    -   **KV to JSON** : Parse des lignes `clé: valeur`, supporte les chemins imbriqués (`a.b[0]: val`), les commentaires et la conversion de types (booléens, nombres).
    -   **JSON to KV** : Aplatit une structure JSON en une liste de lignes `chemin: valeur`.
-   **Entrées/Options** :
    -   `mode` : `kv_to_json` ou `json_to_kv`.
    -   De nombreuses options pour personnaliser les séparateurs, la gestion des commentaires, etc.
-   **Sortie** :
    -   `text_out` : Le résultat de la conversion.

---

<div align="center">

<h3>🌟 <strong>Montrez Votre Soutien</strong></h3>

<p>Si ce projet vous a aidé, n'hésitez pas à lui donner une ⭐ sur GitHub !</p>

<p><strong>Fait avec ❤️ pour la communauté ComfyUI</strong></p>

<p><strong>par Orion4D</strong></p>

<a href="https://ko-fi.com/orion4d">
<img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Buy Me A Coffee" height="41" width="174">
</a>

</div>
