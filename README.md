# The World Is Ours

Jeu de stratégie au tour par tour en 2D (Pygame), inspiré des jeux de conquête médiévale.

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Modes de jeu

- **Solo** : tu joues le Royaume Rouge contre 4 IA.
- **God Game** : tu contrôles tous les royaumes à tour de rôle, sans brouillard de guerre.

## Objectifs

- Contrôler **toutes les capitales**, ou
- Être le **dernier royaume** encore en vie.

Quand un royaume n’a plus d’armées ni de villes/capitales sur son territoire, il est éliminé : **toutes ses cases** passent à l’attaquant (25 % de son or en prime).

## Contrôles

| Action | Comment |
|--------|---------|
| Unité suivante | **N** / **Tab**, ou le bouton bas-droite tant qu’il reste du mouvement |
| Sélectionner une armée | Clic gauche : la portée s’affiche tout de suite |
| Déplacer | Survole une case **verte** : le fantôme et « Arrêt » montrent où l’armée s’arrête. Clique pour y aller. |
| Attaquer | Clic sur une case **rouge** |
| Tir à distance | Clic sur une case **violette** (arbalétrier ou catapulte) |
| Embarquer | Clic sur une case d’eau **bleue** |
| Débarquer | Clic sur une terre ou une plage **verte** |
| Pont | Case **dorée** (détroit seulement) |
| Annuler l’ordre | Clic droit ou **Échap** |
| Recruter | Clique une ville, puis Lancier / Spadassin / Arbalète / Cavalerie / Catapulte |
| Construire | Case libre : fonder une ville |
| Fortifier | Bouton dans le panneau du bas |
| Recherche tech | Bouton en haut à droite |
| Fin de tour | Le bouton clignote quand plus aucune unité n’a de PM, ou **Espace** |
| Pause / réglages | **Échap** → volume, vitesse IA, difficulté |
| Sauvegarde manuelle | **Ctrl+S** ou menu pause |
| Charger | Menu principal → « Charger une partie » |

En **solo**, le brouillard reste toujours celui du **Royaume Rouge** (pas la vision des tours IA).

L’interface vise un look *Civilization* précoce : bois, or, parchemin. La fenêtre est en **paysage** (1280x776) pour un moniteur normal. Tes PNG dans `assets/` (villes, unités, terrain) remplacent le dessin par défaut. À l’intérieur d’un royaume, une **grille très légère** montre les cases ; la **bordure forte** reste entre les royaumes.

## Mer

Les plages se **marchent à pied**. On n’embarque qu’en cliquant une case d’**eau**. Un navire reste sur l’eau ou un pont ; il débarque sur une terre ou une plage. Un pont ne se construit que sur un **détroit** (eau coincée entre deux terres), pas le long d’une plage.

Plaine, plage, pont et mer coûtent **1 PM**. Forêt et montagne coûtent **2 PM**. L’IA ne construit un pont que si aucune route terrestre n’atteint une capitale ennemie.

## Unités

| Unité | Rôle |
|--------|------|
| Lancier | Bonne défense, fort contre la cavalerie. Garnison des villes. |
| Spadassin | Combat général, bat arbalète et lancier. |
| Arbalétrier | Tir à distance. |
| Cavalerie | Rapide, bon attaquant. |
| Catapulte | Lente et chère. Bonus contre les murs, bombardement. |

Une **ville** ou **capitale** ennemie a des murs et une garnison de lanciers. Marcher dessus, c’est un assaut, pas une promenade.

## Traits des royaumes

| Royaume | Trait |
|---------|--------|
| Rouge | Spadassins moins chers et plus solides |
| Bleu | Ponts et transports moins chers |
| Vert | Meilleure défense en forêt, villes plus rentables |
| Jaune | Capitales plus riches |
| Orange | Cavalerie plus mobile |

## Carte

Chaque **nouvelle partie** génère une carte aléatoire : 5 îles (une par royaume), montagnes, forêts, plages et capitales placées automatiquement.

## Sauvegarde

La partie est enregistrée automatiquement à chaque fin de tour dans `saves/latest.json`.

## Réglages (`data/settings.json`)

- **Volume** — menu pause → Réglages  
- **Vitesse IA** — Instantané / Rapide / Normal / Lent  
- **Difficulté** — Facile / Normal / Difficile (menu « Nouvelle partie » ou pause)

## Assets (optionnel)

Place tes PNG dans `assets/` : le jeu les charge tout seul (plusieurs noms de fichiers marchent, ex. `city.png`, `ville.png`, `capital.png`).

- `assets/terrain/` — plaine, forêt, montagne, eau, plage, pont
- `assets/units/` — spadassin, arbalétrier, cavalerie, lancier, catapulte, **bateau**
- `assets/buildings/` — **capitale**, **ville**

Sans fichier, le jeu dessine le terrain à la main.

## Structure du projet

| Fichier | Rôle |
|---------|------|
| `main.py` | Boucle de jeu, règles, tours |
| `map_generator.py` | Génération procédurale de carte |
| `ai.py` | Intelligence artificielle |
| `save_game.py` | Sauvegarde / chargement JSON |
| `audio.py` | Sons et musique procéduraux |
| `fx.py` | Marche des unités, bannières, fin de partie |
| `tutorial.py` | Tutoriel au premier lancement |
| `pause_menu.py` | Menu pause et réglages |
| `settings.py` | Volume, vitesse IA, difficulté |
| `constants.py` | Équilibrage et énumérations |
| `theme.py` | Bois, or, parchemin, polices, hachures |
| `tiles.py` | Tuiles et figurines style Civilization I |
| `cell.py`, `army.py`, `player.py` | Modèle de jeu |
| `ui.py`, `menu.py` | Interface |

## Tests

```bash
python -m unittest discover -s tests -v
```

## Licence

Projet personnel / éducatif.
