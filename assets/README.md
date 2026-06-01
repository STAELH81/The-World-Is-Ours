# Assets

Place tes PNG ici (le jeu les charge automatiquement via `asset_loader.py`).
Sans fichier manquant, le rendu de secours (couleurs) est utilisé pour ce sprite.

Structure attendue :

```
assets/
  terrain/terrain_plain.png
  terrain/terrain_forest.png
  terrain/terrain_mountain.png
  terrain/terrain_water.png
  terrain/terrain_beach.png
  terrain/terrain_bridge.png
  overlay/border_red.png
  overlay/border_blue.png
  overlay/border_green.png
  overlay/border_yellow.png
  overlay/border_orange.png
  units/unit_swordsman.png
  units/unit_crossbowman.png
  units/unit_cavalry.png
  buildings/capital.png
  buildings/city.png
```

Taille recommandée : **34×34** pour le terrain, plus petit pour unités/bâtiments (voir `asset_loader.py`).
