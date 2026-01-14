# Tutoriels des Managers - Shift Project

Bienvenue dans la documentation des managers du **Shift Project** ! Ce dossier contient des guides détaillés pour chaque manager du système de jeu.

## 📚 Liste des tutoriels

### 🔊 [AudioManager](AudioManager.md)

Gestion complète du système audio du jeu.

**Fonctionnalités :**

- 4 types de sons : BGM (musique), BGS (ambiance), ME (effets musicaux), SE (effets sonores)
- Gestion hiérarchique des volumes (Master + catégories)
- Support fade-in/fade-out
- Gestion multi-canaux
- Chargement automatique des assets

**À utiliser pour :**

- Jouer de la musique de fond
- Gérer les sons d'ambiance
- Déclencher des effets sonores
- Ajuster les volumes en temps réel

---

### 🖥️ [DisplayManager](DisplayManager.md)

Gestion de la fenêtre et de l'affichage du jeu.

**Fonctionnalités :**

- Création et gestion de la fenêtre
- Mode plein écran
- VSync (synchronisation verticale)
- Limitation de FPS
- Calcul du delta time
- Captures d'écran
- Gestion du curseur

**À utiliser pour :**

- Initialiser la fenêtre de jeu
- Basculer entre modes fenêtré/plein écran
- Gérer le framerate et la fluidité
- Prendre des screenshots
- Obtenir le delta time pour les animations

---

### 🎮 [EventManager](EventManager.md)

Gestion des entrées utilisateur et du système de timers.

**Fonctionnalités :**

- Mapping configurable des touches clavier
- Support des manettes (gamepads)
- Détection d'états : PRESSED, HELD, RELEASED
- Système de timers intégré
- Fusion automatique clavier + manette

**À utiliser pour :**

- Détecter les actions du joueur
- Configurer les contrôles
- Gérer des cooldowns et événements temporisés
- Support multi-plateforme des entrées

---

### ⚙️ [OptionsManager](OptionsManager.md)

Gestion centralisée des paramètres et options du jeu.

**Fonctionnalités :**

- Sauvegarde/chargement automatique (JSON)
- Gestion des volumes audio
- Paramètres d'affichage (plein écran, VSync, FPS)
- Configuration des touches
- Synchronisation avec les autres managers

**À utiliser pour :**

- Créer un menu d'options
- Sauvegarder les préférences du joueur
- Charger les paramètres au démarrage
- Réinitialiser aux valeurs par défaut

---

### 🎬 [SceneManager](SceneManager.md)

Gestion des scènes du jeu et des transitions.

**Fonctionnalités :**

- Système de scènes modulaire
- Transitions fluides (fade, etc.)
- Cycle de vie des scènes
- Historique des scènes
- États de transition

**À utiliser pour :**

- Organiser le jeu en scènes (menu, jeu, pause, etc.)
- Naviguer entre les différentes parties du jeu
- Ajouter des effets de transition
- Gérer le flux du jeu

---

## 🚀 Guide de démarrage rapide

### Initialisation de base

```python
# import built-in modules

# import pygame
import pygame

# import game_libs
from game_libs.managers.audio import AudioManager
from game_libs.managers.scene import SceneManager
from game_libs.managers.display import DisplayManager
from game_libs.managers.options import OptionsManager

# main function
def main():
    """Main function to run the game."""
    # Initialize pygame
    pygame.init()

    # Initialize managers
    OptionsManager.init()
    DisplayManager.init()
    AudioManager.init()
    SceneManager.init()

    # load the first scene
    SceneManager.change_scene("Welcome")

    # Main game loop
    running = True
    while running:
        # tick clock and get delta time
        DisplayManager.tick()
        dt = DisplayManager.get_delta_time()

        # check for QUIT event
        if pygame.event.peek(pygame.QUIT):
            running = False

        # update managers
        AudioManager.cleanup()
        SceneManager.update(dt)

        # handle events
        SceneManager.handle_events()

        # render scene
        SceneManager.render(DisplayManager.get_surface())

        # update display
        DisplayManager.flip()

    # Exit properly
    DisplayManager.shutdown()
    OptionsManager.save()
    pygame.quit()

if __name__ == "__main__":
    main()
```

---

## 📖 Structure recommandée

### Organisation du code

```text
projet/
├── game_libs/
│   ├── managers/          # Les 5 managers
│   │   ├── audio.py
│   │   ├── display.py
│   │   ├── event.py
│   │   ├── options.py
│   │   └── scene.py
│   ├── scenes/            # Vos scènes de jeu
│   │   ├── __init__.py
│   │   ├── base_scene.py
│   │   ├── menu_scene.py
│   │   ├── game_scene.py
│   │   └── pause_scene.py
│   └── transitions/       # Effets de transition
│       ├── __init__.py
│       ├── base_transition.py
│       └── fade_transition.py
├── assets/
│   └── audio/
│       ├── bgm/           # Musiques de fond
│       ├── bgs/           # Sons d'ambiance
│       ├── me/            # Effets musicaux
│       └── se/            # Effets sonores
├── config.py              # Configuration du jeu
└── main.py                # Point d'entrée
```

---

## 🔄 Ordre d'initialisation

**IMPORTANT : Respectez cet ordre pour éviter les problèmes !**

1. **pygame.init()** - Initialisation de pygame
2. **OptionsManager.init()** - Charge les options sauvegardées
3. **DisplayManager.init()** - Crée la fenêtre
4. **AudioManager.init()** - Initialise le système audio
5. **SceneManager.init()** - Charge toutes les scènes
6. **SceneManager.change_scene()** - Démarre sur une scène

---

## 💡 Bonnes pratiques

### 1. Gestion des ressources

```python
# ✅ BON - Charger dans init()
class GameScene(BaseScene):
    def init(self):
        self.player_sprite = load_image("player.png")
        self.level_data = load_level("level1.json")
    
    def on_enter(self):
        self.player.reset()
        AudioManager.play_bgm("level_theme")

# ❌ MAUVAIS - Charger dans on_enter()
class GameScene(BaseScene):
    def on_enter(self):
        self.player_sprite = load_image("player.png")  # Lent !
```

### 2. Utilisation du delta time

```python
# ✅ BON - Utiliser le delta time
def update(self, dt):
    self.player.x += self.player.speed * dt  # pixels/seconde

# ❌ MAUVAIS - Ignorer le delta time
def update(self, dt):
    self.player.x += self.player.speed  # Dépend du framerate !
```

### 3. Vérification des états

```python
from game_libs.managers.event import KeyState

# ✅ BON - Utiliser les états appropriés
keys = EventManager.get_keys()

if keys["JUMP"] == KeyState.PRESSED:
    player.jump()  # Une seule fois

if keys["RIGHT"] & (KeyState.PRESSED | KeyState.HELD):
    player.move_right(dt)  # Continu

# ❌ MAUVAIS - Utiliser HELD pour une action ponctuelle
if keys["JUMP"] & KeyState.HELD:
    player.jump()  # Saute à chaque frame !
```

### 4. Sauvegarde des options

```python
# ✅ BON - Sauvegarder après validation
def apply_options():
    OptionsManager.set_master_volume(new_volume)
    OptionsManager.set_fullscreen(new_fullscreen)
    OptionsManager.save()  # Une seule fois à la fin

# ❌ MAUVAIS - Sauvegarder à chaque changement
def on_volume_slider_change(value):
    OptionsManager.set_master_volume(value)
    OptionsManager.save()  # Trop fréquent !
```

---

## 🐛 Débogage

### Activer les logs

Pour voir ce qui se passe dans les managers :

```python
from game_libs import config

# set log debug to True
config.LOG_DEBUG = True
```

### Messages de log typiques

```text
[OptionsManager] Options loaded from .cache/settings.json
[DisplayManager] Display initialized: 1280x720, fullscreen=False
[AudioManager] Playing BGM: menu_theme
[EventManager] Timer 'cooldown' triggered
[SceneManager] Loaded scene: game
```

---

## 🆘 Problèmes courants

### La fenêtre ne s'affiche pas

- Vérifiez que `pygame.init()` est appelé en premier
- Assurez-vous d'appeler `DisplayManager.flip()` après le rendu

### Pas de son

- Vérifiez que les fichiers audio sont dans les bons dossiers
- Vérifiez les volumes (master et catégorie)
- Activez les logs pour voir les erreurs

### Les touches ne répondent pas

- Appelez `EventManager.update(dt)` dans `Scene.update(dt)`
- Appelez `SceneManager.update(dt)` dans la boucle de jeu principale

### Les changements d'options ne sont pas sauvegardés

- Appelez `OptionsManager.save()` après les modifications
- Vérifiez que le dossier `cache` est accessible en écriture

### Les scènes ne changent pas

- Vérifiez que la scène existe et est dans `__all__`
- Appelez `SceneManager.update(dt)` dans la boucle
- Vérifiez les logs pour voir les erreurs

---

## 📞 Support et contributions

Pour toute question ou suggestion d'amélioration :

1. Consultez d'abord les tutoriels détaillés
2. Activez les logs en mode DEBUG
3. Vérifiez les exemples de code fournis

---

## 📄 Licence

© Lafiteau Franck - Shift Project

---

### Bon développement ! 🚀
