# DisplayManager - Guide d'utilisation

## 📖 Description

Le **DisplayManager** gère tout ce qui concerne l'affichage et la fenêtre du jeu : création de la fenêtre, gestion du mode plein écran, VSync, FPS, captures d'écran, et plus encore.

## 🎯 Caractéristiques principales

- Gestion de la fenêtre et de sa surface d'affichage
- Support du mode plein écran
- Gestion du VSync (synchronisation verticale)
- Limitation du framerate (FPS)
- Calcul automatique du delta time
- Captures d'écran
- Gestion du curseur

---

## 🚀 Initialisation

### init()

Initialise la fenêtre de jeu avec les paramètres souhaités.

```python
from game_libs.managers.display import DisplayManager

# Initialisation avec paramètres par défaut (depuis config)
DisplayManager.init()

# Initialisation personnalisée
DisplayManager.init(
    width=1920,
    height=1080,
    caption="Mon Super Jeu",
    fullscreen=False,
    flags=0  # Flags pygame additionnels
)
```

**Paramètres :**
- `width` : Largeur de la fenêtre (défaut : valeur dans config)
- `height` : Hauteur de la fenêtre (défaut : valeur dans config)
- `caption` : Titre de la fenêtre
- `fullscreen` : Démarrer en plein écran
- `flags` : Flags pygame supplémentaires (ex: `pygame.RESIZABLE`)

---

## 🖼️ Accès à la surface d'affichage

### get_surface()

Récupère la surface principale pour effectuer le rendu.

```python
surface = DisplayManager.get_surface()

# Utilisation dans la boucle de rendu
def render():
    surface = DisplayManager.get_surface()
    surface.fill((0, 0, 0))  # Fond noir
    # ... dessiner le jeu ...
    DisplayManager.flip()
```

**⚠️ Important :** Lève une `RuntimeError` si le DisplayManager n'est pas initialisé.

---

## 📏 Informations sur la fenêtre

### Dimensions

```python
# Obtenir la largeur
width = DisplayManager.get_width()

# Obtenir la hauteur
height = DisplayManager.get_height()

# Obtenir les deux en même temps
width, height = DisplayManager.get_size()
```

### État du plein écran

```python
# Vérifier si en plein écran
is_fullscreen = DisplayManager.is_fullscreen()

# Basculer entre fenêtré et plein écran
DisplayManager.toggle_fullscreen()
```

**Exemple d'utilisation :**
```python
# Touche F11 pour basculer le plein écran
def handle_input(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F11:
            DisplayManager.toggle_fullscreen()
```

---

## ⏱️ Gestion du temps et FPS

### tick()

Gère le timing et calcule le delta time. **À appeler une fois par frame au début de la boucle.**

```python
# Boucle de jeu basique
running = True
while running:
    DisplayManager.tick()  # Met à jour le delta time et gère le FPS cap
    dt = DisplayManager.get_delta_time()
    
    # Logique de jeu avec dt
    update(dt)
    render()
    DisplayManager.flip()
```

### get_delta_time()

Retourne le temps écoulé depuis la dernière frame en secondes.

```python
dt = DisplayManager.get_delta_time()

# Utilisation pour un mouvement fluide
player_x += player_speed * dt  # pixels par seconde
```

### Gestion du FPS

```python
# Définir une limite de FPS
DisplayManager.set_fps_cap(60)  # Limiter à 60 FPS

# Pas de limite (attention à la consommation CPU/GPU)
DisplayManager.set_fps_cap(0)

# Obtenir la limite actuelle
fps_cap = DisplayManager.get_fps_cap()

# Obtenir le FPS actuel
current_fps = DisplayManager.get_fps()
print(f"FPS: {current_fps:.2f}")
```

**Exemple d'affichage FPS :**
```python
import pygame

def render_fps():
    surface = DisplayManager.get_surface()
    fps = DisplayManager.get_fps()
    font = pygame.font.Font(None, 36)
    fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
    surface.blit(fps_text, (10, 10))
```

---

## 🔄 VSync (Synchronisation verticale)

Le VSync synchronise le framerate avec le taux de rafraîchissement de l'écran pour éviter le tearing.

```python
# Activer le VSync
DisplayManager.set_vsync(True)

# Désactiver le VSync
DisplayManager.set_vsync(False)

# Vérifier l'état
is_enabled = DisplayManager.is_vsync_enabled()
```

**⚠️ Note :** Changer le VSync nécessite de recréer la fenêtre (peut causer un bref flash).

**Recommandation :**
- VSync ON + FPS cap 0 : Framerate limité par l'écran (60 Hz = 60 FPS)
- VSync OFF + FPS cap 60 : Framerate constant à 60 FPS sans tearing potentiel

---

## 🖱️ Gestion du curseur

```python
# Afficher le curseur
DisplayManager.show_cursor(True)

# Masquer le curseur
DisplayManager.show_cursor(False)

# Exemple : masquer en jeu, afficher dans les menus
def enter_game():
    DisplayManager.show_cursor(False)

def enter_menu():
    DisplayManager.show_cursor(True)
```

---

## 🎨 Personnalisation de la fenêtre

### Changer le titre

```python
# Changer le titre de la fenêtre
DisplayManager.set_caption("Chapitre 2 : La forêt mystérieuse")

# Dynamique selon l'état du jeu
def update_title(level_name):
    DisplayManager.set_caption(f"Mon Jeu - {level_name}")
```

### Définir l'icône

```python
# Définir l'icône de la fenêtre
DisplayManager.set_icon("assets/icon.png")

# L'icône est automatiquement chargée depuis config.ICON_PATH lors de init()
```

---

## 📸 Captures d'écran

### save_screenshot()

Sauvegarde l'état actuel de l'écran en PNG.

```python
# Nom automatique avec timestamp
DisplayManager.save_screenshot()
# Crée : cache/screenshots/screenshot_20260114_153045.png

# Nom personnalisé
DisplayManager.save_screenshot("victoire_niveau_1.png")
```

**Configuration :** Le dossier de destination est défini par `config.SCREENSHOTS_FOLDER`.

**Exemple d'utilisation :**
```python
# Touche F12 pour screenshot
def handle_input(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F12:
            DisplayManager.save_screenshot()
            print("Screenshot sauvegardée !")
```

---

## 🎞️ Rendu et affichage

### flip()

Met à jour l'affichage (swap des buffers). **À appeler après chaque rendu complet.**

```python
def render():
    surface = DisplayManager.get_surface()
    
    # Dessiner le fond
    surface.fill((20, 20, 40))
    
    # Dessiner les sprites, UI, etc.
    draw_game_objects(surface)
    draw_ui(surface)
    
    # Afficher à l'écran
    DisplayManager.flip()
```

---

## 🛑 Fermeture

### shutdown()

Ferme proprement le DisplayManager. **À appeler avant de quitter le jeu.**

```python
# À la fin du jeu
def cleanup():
    DisplayManager.shutdown()
    pygame.quit()
```

---

## 📋 Exemple complet

```python
import pygame
from game_libs.managers.display import DisplayManager

# Initialisation de pygame
pygame.init()

# Configuration du DisplayManager
DisplayManager.init(
    width=1280,
    height=720,
    caption="Mon Jeu Génial",
    fullscreen=False
)

# Configuration VSync et FPS
DisplayManager.set_vsync(True)
DisplayManager.set_fps_cap(60)

# Masquer le curseur en jeu
DisplayManager.show_cursor(False)

# Boucle de jeu
running = True
clock_counter = 0

while running:
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                DisplayManager.toggle_fullscreen()
            elif event.key == pygame.K_F12:
                DisplayManager.save_screenshot()
    
    # Mise à jour du timing
    DisplayManager.tick()
    dt = DisplayManager.get_delta_time()
    
    # Logique du jeu
    update_game(dt)
    
    # Rendu
    surface = DisplayManager.get_surface()
    surface.fill((30, 30, 50))
    
    render_game(surface)
    
    # Afficher FPS (toutes les 30 frames)
    clock_counter += 1
    if clock_counter % 30 == 0:
        fps = DisplayManager.get_fps()
        print(f"FPS: {fps:.1f}")
    
    DisplayManager.flip()

# Nettoyage
DisplayManager.shutdown()
pygame.quit()
```

---

## 🔧 Intégration avec OptionsManager

Le DisplayManager fonctionne main dans la main avec l'OptionsManager pour gérer les paramètres :

```python
from game_libs.managers.options import OptionsManager
from game_libs.managers.display import DisplayManager

# L'OptionsManager synchronise automatiquement les paramètres
OptionsManager.init()  # Charge et applique les options sauvegardées

# Changer les options (synchronisé automatiquement)
OptionsManager.set_fullscreen(True)
OptionsManager.set_vsync(True)
OptionsManager.set_fps_cap(144)

# Sauvegarder les changements
OptionsManager.save()
```

---

## ⚠️ Notes importantes

1. **Ordre d'initialisation** : Appelez `pygame.init()` avant `DisplayManager.init()`

2. **tick() obligatoire** : Sans appeler `tick()`, le delta time reste à 0 et le FPS n'est pas géré

3. **Recréation de fenêtre** : Les opérations suivantes recréent la fenêtre :
   - `toggle_fullscreen()`
   - `set_vsync()`
   
   Cela peut causer un bref flash ou perdre le contexte OpenGL si utilisé.

4. **Performance** : 
   - VSync limite naturellement le FPS au taux de rafraîchissement de l'écran
   - Sans VSync, utilisez `set_fps_cap()` pour limiter la consommation CPU/GPU

5. **Screenshots** : Les screenshots sont en format PNG et incluent tout ce qui est affiché à l'écran

---

## 🐛 Débogage

Activez les logs pour voir les opérations du DisplayManager :

```python
import logging
from game_libs import logger

logger.setLevel(logging.DEBUG)
```

Messages de log typiques :
```
[DisplayManager] Display initialized: 1920x1080, fullscreen=False
[DisplayManager] VSync enabled
[DisplayManager] FPS cap set to: 60
[DisplayManager] Screenshot saved to: cache/screenshots/screenshot_20260114_153045.png
```

---

## 💡 Conseils d'utilisation

1. **Mode plein écran** : Proposez toujours un raccourci clavier (ex: F11) pour entrer/sortir du plein écran

2. **FPS cap** : Pour un jeu 2D, 60 FPS est généralement suffisant et économise de l'énergie

3. **Delta time** : Utilisez toujours le delta time pour les mouvements et animations pour assurer une fluidité constante

4. **VSync vs FPS cap** :
   - Jeu compétitif : VSync OFF, FPS cap élevé (120-144)
   - Jeu casual : VSync ON, pas de FPS cap
   - Économie d'énergie : VSync ON ou FPS cap 60

5. **Debug** : Affichez le FPS pendant le développement pour détecter les problèmes de performance
