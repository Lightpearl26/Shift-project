# Système de Scènes - Guide complet

## 📖 Description

Une **scène** est une partie importante du jeu (menu, jeu principal, pause, options, etc.). Le système de scènes gère leur cycle de vie et leurs transitions.

**Voir aussi :**
- [SceneManager.md](SceneManager.md) - Gestion des changements de scène
- [Transitions.md](Transitions.md) - Effets visuels lors des changements
- [EventManager.md](EventManager.md) - Gestion des entrées utilisateur

---

## 🎯 Caractéristiques principales

- **Cycle de vie complet** : init → enter → exit
- **Mise à jour logique** : `update(dt)` à chaque frame
- **Rendu** : `render(surface)` à chaque frame
- **Gestion d'entrées** : `handle_events()` pour les interactions
- **Accès aux managers** : Audio, Events, Display, Options intégrés

---

## 🏗️ Architecture

### Classe de base : BaseScene

Toutes les scènes héritent de `BaseScene` :

```python
from game_libs.scenes import BaseScene

class MyScene(BaseScene):
    def __init__(self):
        super().__init__("my_scene")  # Nom unique
    
    # À implémenter :
    def init(self): pass
    def on_enter(self): pass
    def on_exit(self): pass
    def handle_events(self): pass
    def update(self, dt): pass
    def render(self, surface): pass
```

### Propriétés communes

```python
scene.name           # Nom unique de la scène (str)
scene.event_manager  # Accès à EventManager
scene.display_manager  # Accès à DisplayManager
scene.audio_manager  # Accès à AudioManager
scene.options_manager  # Accès à OptionsManager
```

---

## 📖 Scènes existantes

### 1. Welcome Scene

**Localisation** : `game_libs/scenes/welcome.py`

**Fonction** : Écran de démarrage du jeu (logo, studios, etc.)

**Fonctionnalités :**
- Affichage d'un écran d'accueil
- Transition automatique ou au clic

**Structure** :
```python
from game_libs.scenes import BaseScene

class WelcomeScene(BaseScene):
    def __init__(self):
        super().__init__("welcome")
    
    def init(self):
        # Charger les ressources une seule fois
        pass
    
    def on_enter(self):
        # Appelé à chaque entrée dans la scène
        pass
    
    def on_exit(self):
        # Nettoyage à la sortie
        pass
    
    def handle_events(self):
        # Vérifier les entrées utilisateur
        pass
    
    def update(self, dt):
        # Logique de mise à jour
        self.event_manager.update(dt)  # Important !
    
    def render(self, surface):
        # Dessiner à l'écran
        pass
```

**Utilisée pour :**
- Afficher un logo ou splash screen
- Vérifier les dépendances
- Initialiser le jeu

---

### 2. MainMenu Scene

**Localisation** : `game_libs/scenes/main_menu.py`

**Fonction** : Menu principal du jeu

**Fonctionnalités :**
- Affichage du menu avec options
- Navigation entre les choix
- Démarrage du jeu

**Structure** :
```python
from game_libs.scenes import BaseScene
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeIn, FadeOut

class MainMenuScene(BaseScene):
    def __init__(self):
        super().__init__("main_menu")
        self.selected_option = 0
        self.options = ["Play", "Options", "Exit"]
    
    def init(self):
        # Charger les ressources du menu
        self.font = pygame.font.Font(None, 36)
    
    def on_enter(self):
        # Démarrer la musique du menu
        self.audio_manager.play_bgm("menu_theme")
    
    def on_exit(self):
        # Arrêter la musique
        self.audio_manager.stop_bgm()
    
    def handle_events(self):
        keys = self.event_manager.get_keys()
        
        # Navigation
        if keys["UP"].is_pressed():
            self.selected_option = (self.selected_option - 1) % len(self.options)
        if keys["DOWN"].is_pressed():
            self.selected_option = (self.selected_option + 1) % len(self.options)
        
        # Sélection
        if keys["ACCEPT"].is_pressed():
            if self.selected_option == 0:  # Play
                SceneManager.change_scene(
                    "game",
                    transition_out=FadeOut(800),
                    transition_in=FadeIn(800)
                )
            # ... autres options
    
    def update(self, dt):
        self.event_manager.update(dt)
    
    def render(self, surface):
        surface.fill((0, 0, 0))
        
        # Afficher les options
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = self.font.render(option, True, color)
            surface.blit(text, (100, 100 + i * 50))
```

**Utilisée pour :**
- Point d'accès principal du jeu
- Navigation vers les différentes scènes
- Options et paramètres

---

## ✨ Créer une nouvelle scène

### 📋 Checklist complète

- [ ] Créer le fichier Python
- [ ] Définir la classe héritant de `BaseScene`
- [ ] Implémenter les 6 méthodes requises
- [ ] Enregistrer dans `__init__.py`
- [ ] Tester le changement de scène

### 📝 Protocole étape par étape

#### Étape 1 : Créer le fichier

Créer un nouveau fichier dans `game_libs/scenes/` :

```
game_libs/scenes/my_scene.py
```

#### Étape 2 : Implémenter la classe

```python
# -*- coding: utf-8 -*-

"""
game_libs.scenes.my_scene
_________________________________________
Description brève de votre scène
_________________________________________
@copyright: [Votre nom] 2026
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .base import BaseScene
from .. import logger

if TYPE_CHECKING:
    from pygame import Surface

class MyScene(BaseScene):
    """
    Description détaillée de votre scène.
    """
    def __init__(self) -> None:
        """Initialize the scene."""
        super().__init__("my_scene")  # Nom unique !
        # Variables d'instance
        self.background = None
        logger.info(f"[{self.__class__.__name__}] Scene initialized")
    
    def init(self) -> None:
        """
        Appelé UNE SEULE FOIS au démarrage du jeu.
        Charger les ressources lourdes ici.
        """
        logger.info(f"[{self.__class__.__name__}] Resources loaded")
        # Charger images, sons, données, etc.
        # self.background = load_image("background.png")
    
    def on_enter(self) -> None:
        """
        Appelé À CHAQUE FOIS qu'on entre dans la scène.
        Réinitialiser l'état, démarrer la musique, etc.
        """
        logger.info(f"[{self.__class__.__name__}] Scene entered")
        # Réinitialiser variables
        # self.audio_manager.play_bgm("scene_music")
    
    def on_exit(self) -> None:
        """
        Appelé À CHAQUE FOIS qu'on quitte la scène.
        Nettoyer et préparer la sortie.
        """
        logger.info(f"[{self.__class__.__name__}] Scene exited")
        # Arrêter la musique
        # self.audio_manager.stop_bgm()
    
    def handle_events(self) -> None:
        """
        Gérer les événements et entrées utilisateur.
        Appelé avant update().
        """
        keys = self.event_manager.get_keys()
        
        # Exemple : appuyer sur ESC pour quitter
        # if keys["CANCEL"].is_pressed():
        #     SceneManager.change_scene("menu")
    
    def update(self, dt: float) -> None:
        """
        Mettre à jour la logique (physique, IA, etc.).
        
        Args:
            dt (float): Delta time en secondes
        """
        # IMPORTANT : Mettre à jour l'EventManager
        self.event_manager.update(dt)
        
        # Votre logique ici
        # self.player.update(dt)
        # self.enemies.update(dt)
    
    def render(self, surface: Surface) -> None:
        """
        Dessiner tout sur la surface.
        Appelé après update().
        
        Args:
            surface (Surface): Surface pygame à remplir
        """
        # Effacer l'écran
        surface.fill((0, 0, 0))
        
        # Dessiner
        # if self.background:
        #     surface.blit(self.background, (0, 0))
        # self.player.draw(surface)
        # self.enemies.draw(surface)
```

#### Étape 3 : Enregistrer la scène

Éditer `game_libs/scenes/__init__.py` :

```python
from .base import BaseScene
from .welcome import WelcomeScene
from .main_menu import MainMenuScene
from .my_scene import MyScene  # 👈 Ajouter cette ligne

__all__ = [
    "BaseScene",
    "WelcomeScene",
    "MainMenuScene",
    "MyScene",  # 👈 Ajouter ici aussi
]
```

#### Étape 4 : Tester

```python
from game_libs.managers.scene import SceneManager

# Dans votre code
SceneManager.change_scene("my_scene")
```

---

## 🔗 Intégration avec SceneManager

### Changer vers votre scène

```python
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeIn, FadeOut

# Changement simple
SceneManager.change_scene("my_scene")

# Avec transitions
SceneManager.change_scene(
    "my_scene",
    transition_out=FadeOut(duration=800),
    transition_in=FadeIn(duration=800)
)
```

### Accéder aux managers

Depuis votre scène, vous pouvez accéder aux managers :

```python
def my_method(self):
    # Audio
    self.audio_manager.play_se("explosion")
    
    # Events
    keys = self.event_manager.get_keys()
    if keys["JUMP"].is_pressed():
        self.player.jump()
    
    # Display
    screen_width = self.display_manager.width
    screen_height = self.display_manager.height
    
    # Options
    master_volume = self.options_manager.master_volume
```

---

## 💡 Exemples complets

### Exemple 1 : Scène de gameplay simple

```python
from game_libs.scenes import BaseScene
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeOut

class GameScene(BaseScene):
    def __init__(self):
        super().__init__("game")
        self.player_x = 0
        self.player_y = 0
        self.player_speed = 200
    
    def init(self):
        # Charger le niveau
        self.level_data = load_level("level1.json")
        # Charger les sprites
        self.player_sprite = load_image("player.png")
    
    def on_enter(self):
        # Réinitialiser la position du joueur
        self.player_x = 100
        self.player_y = 100
        # Démarrer la musique
        self.audio_manager.play_bgm("gameplay_theme")
    
    def on_exit(self):
        self.audio_manager.stop_bgm()
    
    def handle_events(self):
        keys = self.event_manager.get_keys()
        
        # Pause
        if keys["PAUSE"].is_pressed():
            SceneManager.change_scene("pause", transition_out=FadeOut(300))
    
    def update(self, dt):
        self.event_manager.update(dt)
        
        # Mouvement du joueur
        keys = self.event_manager.get_keys()
        if keys["LEFT"].is_held():
            self.player_x -= self.player_speed * dt
        if keys["RIGHT"].is_held():
            self.player_x += self.player_speed * dt
        if keys["UP"].is_held():
            self.player_y -= self.player_speed * dt
        if keys["DOWN"].is_held():
            self.player_y += self.player_speed * dt
    
    def render(self, surface):
        surface.fill((50, 50, 50))  # Fond gris
        
        # Dessiner le joueur
        surface.blit(
            self.player_sprite,
            (self.player_x, self.player_y)
        )
```

### Exemple 2 : Scène de pause

```python
from game_libs.scenes import BaseScene
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeIn, FadeOut

class PauseScene(BaseScene):
    def __init__(self):
        super().__init__("pause")
        self.options = ["Resume", "Menu"]
        self.selected = 0
        self.background = None
    
    def init(self):
        self.font = pygame.font.Font(None, 48)
    
    def on_enter(self):
        # Capturer la scène précédente pour le rendu
        # (dans un vrai jeu, vous voudriez sauvegarder un screenshot)
        pass
    
    def handle_events(self):
        keys = self.event_manager.get_keys()
        
        if keys["UP"].is_pressed():
            self.selected = (self.selected - 1) % len(self.options)
        if keys["DOWN"].is_pressed():
            self.selected = (self.selected + 1) % len(self.options)
        
        if keys["ACCEPT"].is_pressed():
            if self.selected == 0:  # Resume
                SceneManager.change_scene(
                    "game",
                    transition_in=FadeIn(300)
                )
            else:  # Menu
                SceneManager.change_scene(
                    "main_menu",
                    transition_out=FadeOut(800),
                    transition_in=FadeIn(800)
                )
    
    def update(self, dt):
        self.event_manager.update(dt)
    
    def render(self, surface):
        # Assombrir l'écran
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Afficher le texte
        title = self.font.render("PAUSE", True, (255, 255, 255))
        surface.blit(title, (self.display_manager.width//2 - 50, 100))
        
        # Afficher les options
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            y = 200 + i * 50
            surface.blit(text, (self.display_manager.width//2 - 50, y))
```

### Exemple 3 : Scène avec animations

```python
from game_libs.scenes import BaseScene
import math

class AnimatedScene(BaseScene):
    def __init__(self):
        super().__init__("animated")
        self.elapsed_time = 0
        self.animation_speed = 2  # radians/second
    
    def update(self, dt):
        self.event_manager.update(dt)
        self.elapsed_time += dt
    
    def render(self, surface):
        surface.fill((20, 20, 40))
        
        # Calculer une position animée
        center_x = self.display_manager.width // 2
        center_y = self.display_manager.height // 2
        radius = 100
        
        # Mouvement circulaire
        angle = self.elapsed_time * self.animation_speed
        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius
        
        # Dessiner un cercle animé
        pygame.draw.circle(surface, (255, 100, 100), (int(x), int(y)), 20)
```

---

## 🔄 Cycle de vie détaillé

```
┌─────────────────────────────────────────────────────────────┐
│                    Démarrage du jeu                         │
│                 pygame.init() → OptionsManager...           │
│                    SceneManager.init()                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │   Pour chaque scène :                │
        │   scene.init() appelé UNE FOIS      │
        └──────────────────┬───────────────────┘
                           │
                    ▼──────────────────────▼
        ┌──────────────────┐        ┌────────────────────┐
        │  Scène courante  │        │  Autres scènes     │
        │  on_enter()      │        │  (en attente)      │
        └──────────┬───────┘        └────────────────────┘
                   │
        ┌──────────▼──────────────────────┐
        │   Boucle principale              │
        │  ┌────────────────────────────┐ │
        │  │ 1. handle_events()         │ │
        │  │ 2. update(dt)              │ │
        │  │ 3. render(surface)         │ │
        │  │ (répété à 60 FPS)          │ │
        │  └────────────────────────────┘ │
        │   Jusqu'à change_scene()        │
        └──────────┬───────────────────────┘
                   │
        ┌──────────▼──────────────────────┐
        │   Changement de scène            │
        │   current.on_exit()             │
        │   next.on_enter()               │
        │   (transitions optionnelles)    │
        └──────────┬───────────────────────┘
                   │
                   ▼
        ┌──────────────────────────────────┐
        │   Reprise de la boucle avec      │
        │   la nouvelle scène              │
        └──────────────────────────────────┘
```

---

## ⚠️ Erreurs courantes

### 1. Oublier `self.event_manager.update(dt)`

```python
# ❌ MAUVAIS
def update(self, dt):
    # Les entrées ne fonctionnent pas !
    pass

# ✅ CORRECT
def update(self, dt):
    self.event_manager.update(dt)  # IMPORTANT !
    # ... votre code
```

### 2. Ne pas enregistrer la scène

```python
# Si vous oubliez dans __init__.py :
# AttributeError: Scene 'my_scene' not found!
```

### 3. Utiliser le même nom pour deux scènes

```python
# ❌ MAUVAIS - deux scènes "menu"
class MenuScene(BaseScene):
    def __init__(self):
        super().__init__("menu")  # Déjà utilisé !

# ✅ CORRECT - noms uniques
class MainMenuScene(BaseScene):
    def __init__(self):
        super().__init__("main_menu")

class OptionsMenuScene(BaseScene):
    def __init__(self):
        super().__init__("options_menu")
```

### 4. Charger des ressources lourdes dans on_enter()

```python
# ❌ MAUVAIS - ralentit le changement de scène
def on_enter(self):
    self.map_sprite = load_huge_image("map.png")

# ✅ CORRECT - charger dans init()
def init(self):
    self.map_sprite = load_huge_image("map.png")

def on_enter(self):
    self.position.reset()
```

---

## 🐛 Dépannage

### La scène n'est pas trouvée

```
AttributeError: Scene 'my_scene' not found!
```

**Solutions :**
1. Vérifier que la scène est enregistrée dans `__init__.py`
2. Vérifier que le nom passé à `super().__init__()` est correct
3. Vérifier l'orthographe du nom dans `change_scene()`

### Les entrées ne fonctionnent pas

**Solutions :**
1. Vérifier que `self.event_manager.update(dt)` est appelé dans `update()`
2. Vérifier que `handle_events()` est appelé par SceneManager
3. Vérifier la configuration de EventManager

### L'écran reste noir

**Solutions :**
1. Vérifier que `render()` appelle `surface.fill()` ou dessine quelque chose
2. Vérifier que `DisplayManager.flip()` est appelé
3. Vérifier que la scène est correctement activée

### Musique ne s'arrête pas en quittant

**Solutions :**
1. Implémenter `on_exit()` et appeler `self.audio_manager.stop_bgm()`
2. Vérifier que `on_exit()` est appelé

---

## 📚 Références

- [SceneManager.md](SceneManager.md) - Gestion des changements
- [Transitions.md](Transitions.md) - Effets de transition
- [EventManager.md](EventManager.md) - Entrées utilisateur
- [AudioManager.md](AudioManager.md) - Gestion du son

---

## 💡 Conseils de design

1. **Une scène = une partie cohérente du jeu**
2. **Charger les ressources lourdes dans `init()`, pas dans `on_enter()`**
3. **Toujours appeler `event_manager.update(dt)` dans `update()`**
4. **Utiliser des noms explicites pour les scènes**
5. **Utiliser `on_exit()` pour nettoyer (musique, timers, etc.)**

---

**Version** : 1.0  
**Dernière mise à jour** : 20 janvier 2026  
**Auteur** : Franck Lafiteau
