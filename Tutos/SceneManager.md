# SceneManager - Guide d'utilisation

## 📖 Description

Le **SceneManager** gère l'ensemble des scènes du jeu et leurs transitions. Il permet de passer d'une scène à l'autre (menu, jeu, options, etc.) de manière fluide avec des effets de transition optionnels.

**Voir aussi :**
- [📖 Tutoriel des scènes](Scenes.md) - Architecture complète et création
- [🎬 Tutoriel des transitions](Transitions.md) - Effets de transition
- [README.md](README.md) - Plan de navigation générale

## 🎯 Caractéristiques principales

- Gestion centralisée de toutes les scènes
- Système de transitions (fade-in, fade-out)
- Cycle de vie des scènes (init, enter, exit, update, render)
- Historique des scènes (scène précédente)
- États de transition (normal, transition_in, transition_out)

---

## 🏗️ Structure d'une scène

Toutes les scènes héritent de `BaseScene` et doivent implémenter certaines méthodes :

```python
from game_libs.scenes import BaseScene

class MyScene(BaseScene):
    def __init__(self):
        super().__init__("my_scene") # Nom unique de la scène
    
    def init(self):
        """Appelé une seule fois au démarrage du jeu"""
        # Charger les ressources, initialiser les variables
        pass
    
    def on_enter(self):
        """Appelé à chaque fois qu'on entre dans la scène"""
        # Réinitialiser l'état, démarrer la musique, etc.
        pass
    
    def on_exit(self):
        """Appelé à chaque fois qu'on quitte la scène"""
        # Nettoyer, arrêter la musique, etc.
        pass
    
    def handle_events(self):
        """Appelé pour gérer les événements utilisateur"""
        # Vérifier les touches pressées, clics souris, etc.
        pass
    
    def update(self, dt: float):
        """Appelé à chaque frame pour mettre à jour la logique"""
        self.event_manager.update(dt) # Ne pas oublier de mettre a jour l'EventManager
        # Mise à jour des entités, physique, etc.
    
    def render(self, surface):
        """Appelé à chaque frame pour le rendu"""
        # Dessiner tout sur la surface
        pass
```

---

## 🚀 Initialisation

### init()

Initialise le SceneManager et toutes les scènes disponibles. **À appeler une seule fois au démarrage.**

```python
from game_libs.managers.scene import SceneManager

# Initialiser le SceneManager
SceneManager.init()
```

**Ce que fait init() :**

1. Découvre automatiquement toutes les scènes dans `game_libs.scenes`
2. Instancie chaque scène
3. Configure les références aux managers
4. Appelle `init()` sur chaque scène

**Note :** Les scènes doivent être définies dans le module `game_libs.scenes` et listées dans `__all__`.

---

## 🎬 États de transition

Le SceneManager utilise un système d'états pour gérer les transitions :

```python
from game_libs.managers.scene import SceneState

SceneState.NORMAL          # Scène active normale
SceneState.TRANSITION_OUT  # Transition de sortie en cours
SceneState.TRANSITION_IN   # Transition d'entrée en cours
```

**Flux de transition :**

1. État NORMAL → L'utilisateur change de scène
2. État TRANSITION_OUT → Fondu sortant de l'ancienne scène
3. Changement effectif de scène (on_exit → on_enter)
4. État TRANSITION_IN → Fondu entrant de la nouvelle scène
5. État NORMAL → Scène active

---

## 🔄 Changer de scène

### change_scene()

Change la scène actuelle vers une nouvelle scène, avec transitions optionnelles.

```python
# Changement simple (instantané)
SceneManager.change_scene("game")

# Avec transition de sortie uniquement
from game_libs.transitions import FadeTransition

fade_out = FadeTransition(duration=0.5, fade_in=False)
SceneManager.change_scene("menu", transition_out=fade_out)

# Avec transition de sortie ET d'entrée
fade_out = FadeTransition(duration=0.5, fade_in=False)
fade_in = FadeTransition(duration=0.5, fade_in=True)
SceneManager.change_scene(
    name="game",
    transition_out=fade_out,
    transition_in=fade_in
)
```

**Paramètres :**

- `name` : Nom de la scène de destination
- `transition_out` : Transition lors de la sortie (optionnel)
- `transition_in` : Transition lors de l'entrée (optionnel)

**⚠️ Important :** Si la scène n'existe pas, un message d'erreur est loggué et rien ne se passe.

---

## 📡 Accès aux scènes

### get_scene()

Récupère une scène par son nom.

```python
# Obtenir une scène
menu_scene = SceneManager.get_scene("menu")

if menu_scene:
    print(f"Scène trouvée: {menu_scene.name}")
else:
    print("Scène introuvable")
```

### get_current_scene()

Obtient la scène actuellement active.

```python
current = SceneManager.get_current_scene()

if current:
    print(f"Scène active: {current.name}")
```

### get_previous_scene()

Obtient la scène précédente (avant le dernier changement).

```python
previous = SceneManager.get_previous_scene()

if previous:
    print(f"Scène précédente: {previous.name}")
    
# Utile pour un bouton "Retour"
def go_back():
    if SceneManager.get_previous_scene():
        SceneManager.change_scene(SceneManager.get_previous_scene().name)
```

---

## 🔁 Boucle de jeu

### handle_events()

Transmet les événements à la scène active (seulement en état NORMAL).

```python
# Dans la boucle de jeu
while running:
    DisplayManager.tick()
    dt = DisplayManager.get_delta_time()

    # Gérer les événements pygame
    if pygame.event.peek(pygame.QUIT)
        running = False
    
    # Mettre a jour le SceneManager AVANT de gérer les événements de la scene
    SceneManager.update(dt)
    
    # Transmettre à la scène active
    SceneManager.handle_events()
```

### update()

Met à jour la scène active et les transitions.

```python
# Dans la boucle de jeu
while running:
    DisplayManager.tick()
    dt = DisplayManager.get_delta_time()
    
    # Mettre à jour la scène et transitions
    SceneManager.update(dt)
```

**Ce que fait update(dt) :**

- Met à jour la transition de sortie si en cours
- Change effectivement de scène quand la transition de sortie est terminée
- Met à jour la transition d'entrée si en cours
- Met à jour la scène active

### render()

Rend la scène active avec les transitions éventuelles.

```python
# Dans la boucle de jeu
def render():
    surface = DisplayManager.get_surface()
    
    # Rendre la scène avec transitions
    SceneManager.render(surface)
    
    DisplayManager.flip()
```

**Ce que fait render() :**

- Rend la scène active
- Applique la transition de sortie par-dessus (si active)
- Applique la transition d'entrée par-dessus (si active)

---

## 📋 Exemple complet

### Structure des scènes

```python
# game_libs/scenes/menu_scene.py
from game_libs.scenes import BaseScene
from game_libs.managers.audio import AudioManager
from game_libs.managers.event import EventManager, KeyState

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__("menu")
    
    def init(self):
        """Chargement des ressources"""
        self.font = pygame.font.Font(None, 72)
        self.options = ["Jouer", "Options", "Quitter"]
        self.selected = 0
    
    def on_enter(self):
        """Entrée dans le menu"""
        AudioManager.play_bgm("menu_theme", fadein_ms=1000)
    
    def on_exit(self):
        """Sortie du menu"""
        AudioManager.stop_bgm(fadeout_ms=500)
    
    def handle_events(self):
        """Gestion des entrées"""
        keys = self.event_manager.get_keys()
        
        if keys["DOWN"] == KeyState.PRESSED:
            self.selected = (self.selected + 1) % len(self.options)
            AudioManager.play_se("menu_move")
        
        if keys["UP"] == KeyState.PRESSED:
            self.selected = (self.selected - 1) % len(self.options)
            AudioManager.play_se("menu_move")
        
        if keys["JUMP"] == KeyState.PRESSED:
            AudioManager.play_se("menu_select")
            
            if self.selected == 0:  # Jouer
                from game_libs.transitions import FadeTransition
                fade_out = FadeTransition(0.5, False)
                fade_in = FadeTransition(0.5, True)
                self.scene_manager.change_scene("game", fade_out, fade_in)
            
            elif self.selected == 1:  # Options
                self.scene_manager.change_scene("options")
            
            elif self.selected == 2:  # Quitter
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def update(self, dt: float):
        """Mise à jour"""
        self.event_manager.update(dt)
    
    def render(self, surface):
        """Rendu"""
        surface.fill((20, 20, 40))
        
        # Titre
        title = self.font.render("MON JEU", True, (255, 255, 255))
        surface.blit(title, (400, 100))
        
        # Options du menu
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            surface.blit(text, (500, 300 + i * 80))


# game_libs/scenes/game_scene.py
class GameScene(BaseScene):
    def __init__(self):
        super().__init__("game")
    
    def init(self):
        """Initialisation des ressources du jeu"""
        # Charger les assets, créer les entités, etc.
        pass
    
    def on_enter(self):
        """Démarrage du jeu"""
        AudioManager.play_bgm("game_theme")
    
    def on_exit(self):
        """Sortie du jeu"""
        AudioManager.stop_all()
    
    def handle_events(self):
        """Gestion des événements"""
        keys = self.event_manager.get_keys()
        
        # Pause
        if keys["PAUSE"] == KeyState.PRESSED:
            self.scene_manager.change_scene("pause")
    
    def update(self, dt: float):
        """Logique du jeu"""
        self.event_manager.update(dt)
        # Mise à jour des entités, physique, collisions, etc.
    
    def render(self, surface):
        """Rendu du jeu"""
        surface.fill((0, 0, 0))
        # Dessiner le niveau, les entités, l'UI, etc.


# game_libs/scenes/__init__.py
from .base_scene import BaseScene
from .menu_scene import MenuScene
from .game_scene import GameScene

__all__ = ["BaseScene", "MenuScene", "GameScene"]
```

### Boucle principale

```python
import pygame
from game_libs.managers.display import DisplayManager
from game_libs.managers.audio import AudioManager
from game_libs.managers.event import EventManager
from game_libs.managers.scene import SceneManager
from game_libs.managers.options import OptionsManager

def main():
    # Initialisation
    pygame.init()
    
    # Charger les options
    OptionsManager.init()
    
    # Initialiser les managers
    DisplayManager.init(width=1280, height=720, caption="Mon Jeu")
    AudioManager.init()
    
    # Initialiser les scènes
    SceneManager.init()
    
    # Démarrer sur le menu
    SceneManager.change_scene("menu")
    
    # Boucle de jeu
    running = True
    while running:
        # Timing
        DisplayManager.tick()
        dt = DisplayManager.get_delta_time()

        # Événements pygame
        if pygame.event.peek(pygame.QUIT):
            running = False
        
        # Déléguer à la scène active
        SceneManager.update(dt)
        SceneManager.handle_events()
        
        # Rendu
        surface = DisplayManager.get_surface()
        surface.fill((0, 0, 0))
        SceneManager.render(surface)
        DisplayManager.flip()
    
    # Nettoyage
    OptionsManager.save()
    AudioManager.stop_all()
    DisplayManager.shutdown()
    pygame.quit()

if __name__ == "__main__":
    main()
```

---

## 🎨 Utilisation avec des transitions

### Créer une transition personnalisée

```python
from game_libs.transitions import BaseTransition
import pygame

class FadeTransition(BaseTransition):
    def __init__(self, duration: float, fade_in: bool = False):
        super().__init__(duration)
        self.fade_in = fade_in
    
    def render(self, surface):
        # Créer un overlay noir semi-transparent
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        alpha = 255 * self.progress if self.fade_in else 255 * (1 - self.progress)
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))

# Utilisation
fade_out = FadeTransition(duration=1.0, fade_in=False)
fade_in = FadeTransition(duration=1.0, fade_in=True)

SceneManager.change_scene("next_scene", fade_out, fade_in)
```

---

## 📋 Exemple : Scène de pause

```python
class PauseScene(BaseScene):
    def __init__(self):
        super().__init__("pause")
    
    def init(self):
        self.font = pygame.font.Font(None, 72)
        self.options = ["Reprendre", "Menu"]
        self.selected = 0
    
    def on_enter(self):
        """Mettre le jeu en pause"""
        AudioManager.pause_bgm()
        EventManager.pause_timers()
    
    def on_exit(self):
        """Reprendre le jeu"""
        # Reprendre seulement si on retourne au jeu
        if self.scene_manager.get_current_scene().name == "game":
            AudioManager.resume_bgm()
            EventManager.resume_timers()
    
    def handle_events(self):
        keys = self.event_manager.get_keys()
        
        # Navigation
        if keys["DOWN"] == KeyState.PRESSED:
            self.selected = (self.selected + 1) % len(self.options)
        if keys["UP"] == KeyState.PRESSED:
            self.selected = (self.selected - 1) % len(self.options)
        
        # Sélection ou Échap pour reprendre
        if keys["JUMP"] == KeyState.PRESSED or keys["PAUSE"] == KeyState.PRESSED:
            if self.selected == 0 or keys["PAUSE"] == KeyState.PRESSED:
                # Reprendre
                self.scene_manager.change_scene("game")
            else:
                # Retour au menu
                self.scene_manager.change_scene("menu")
    
    def update(self, dt: float):
        self.event_manager.update(dt)
    
    def render(self, surface):
        # Rendre la scène de jeu en arrière-plan (floutée/sombre)
        game_scene = self.scene_manager.get_previous_scene()
        if game_scene:
            game_scene.render(surface)
        
        # Overlay semi-transparent
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        surface.blit(overlay, (0, 0))
        
        # Menu de pause
        title = self.font.render("PAUSE", True, (255, 255, 255))
        surface.blit(title, (500, 200))
        
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (200, 200, 200)
            text = self.font.render(option, True, color)
            surface.blit(text, (500, 350 + i * 70))
```

---

## ⚠️ Notes importantes

1. **init() vs on_enter()** :
   - `init()` : Appelé une seule fois au démarrage, charger les ressources lourdes
   - `on_enter()` : Appelé à chaque entrée dans la scène, réinitialiser l'état

2. **Transitions bloquantes** : Pendant une transition, `handle_events()` n'est pas appelé sur la scène

3. **Références circulaires** : Les scènes ont accès à `self.scene_manager` et `self.event_manager` automatiquement

4. **Nom unique** : Chaque scène doit avoir un `name` unique pour être accessible

5. **Module \_\_all\_\_** : N'oubliez pas d'ajouter vos nouvelles scènes dans `game_libs/scenes/__init__.py`

---

## 🐛 Débogage

Activez les logs :

```python
from game_libs import config

config.LOG_DEBUG = True
```

Messages typiques :

```text
[SceneManager] Available scene: MenuScene
[SceneManager] Initialized scene: menu
[SceneManager] Unloaded scene: menu
[SceneManager] Loaded scene: game
```

---

## 💡 Conseils d'utilisation

1. **Scènes légères** : Chargez les ressources dans `init()`, pas dans `__init__()`

2. **Nettoyage** : Libérez les ressources dans `on_exit()` si nécessaire

3. **Transitions** : Utilisez des transitions courtes (0.3-0.5s) pour une meilleure réactivité

4. **État partagé** : Pour partager des données entre scènes, utilisez un singleton ou passez par les managers

5. **Scène de chargement** : Créez une scène dédiée pour charger les assets lourds avec une barre de progression
