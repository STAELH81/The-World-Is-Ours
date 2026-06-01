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
| Sélectionner une case | Clic gauche sur la carte |
| Recruter / construire / pont | Panneau de droite → onglet Actions |
| Déplacer une armée | Sélectionner l’armée → « Déplacer armée » → clic destination |
| Tir à distance | Arbalétrier → « Tir à distance » → clic cible |
| Fortifier | Armée sélectionnée → « Fortifier » |
| Recherche tech | Bouton « Rechercher tech » |
| Fin de tour | « Fin de tour » (autosauvegarde) |
| Pause / réglages | **Échap** → volume, vitesse IA, difficulté |
| Sauvegarde manuelle | **Ctrl+S** ou menu pause |
| Charger | Menu principal → « Charger Partie » |

En **solo**, le brouillard reste toujours celui du **Royaume Rouge** (pas la vision des tours IA).

## Carte

Chaque **nouvelle partie** génère une carte aléatoire : 5 îles (une par royaume), montagnes, forêts, plages et capitales placées automatiquement.

## Sauvegarde

La partie est enregistrée automatiquement à chaque fin de tour dans `saves/latest.json`.

## Réglages (`data/settings.json`)

- **Volume** — menu pause → Réglages  
- **Vitesse IA** — Instantané / Rapide / Normal / Lent  
- **Difficulté** — Facile / Normal / Difficile (menu « Nouvelle partie » ou pause)

## Assets (optionnel)

Place des PNG dans `assets/` pour remplacer le rendu par défaut :

- `assets/terrain/` — plain, forest, mountain, water, beach, bridge
- `assets/overlay/` — bordures par couleur
- `assets/units/` — spadassin, arbalétrier, cavalerie
- `assets/buildings/` — capitale, ville

Sans fichiers, le jeu utilise des formes et couleurs générées.

## Structure du projet

| Fichier | Rôle |
|---------|------|
| `main.py` | Boucle de jeu, règles, tours |
| `map_generator.py` | Génération procédurale de carte |
| `ai.py` | Intelligence artificielle |
| `save_game.py` | Sauvegarde / chargement JSON |
| `audio.py` | Sons procéduraux |
| `tutorial.py` | Tutoriel au premier lancement |
| `pause_menu.py` | Menu pause et réglages |
| `settings.py` | Volume, vitesse IA, difficulté |
| `constants.py` | Équilibrage et énumérations |
| `cell.py`, `army.py`, `player.py` | Modèle de jeu |
| `ui.py`, `menu.py` | Interface |

## Tests

```bash
python -m unittest discover -s tests -v
```

## Licence

Projet personnel / éducatif.
