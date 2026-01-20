# Transitions - Guide d'utilisation

## 📖 Description

Le système de **transitions** du projet Shift permet de créer des effets visuels élégants lorsqu'on passe d'une scène à une autre. Les transitions gèrent des effets comme les fondus, les dissolutions de particules, ou même la lecture de vidéos.

**Voir aussi :**
- [📡 SceneManager.md](SceneManager.md) - Intégration avec les changements de scène
- [📖 Scenes.md](Scenes.md) - Transitions lors des changements de scène
- [README.md](README.md) - Plan de navigation générale

---

## 🎯 Caractéristiques principales

- **Transitions simples** : FadeIn, FadeOut
- **Transitions visuelles** : Dissolución par particules (droite, gauche, haut, bas)
- **Transitions vidéo** : Lecture de fichiers vidéo
- **Animations fluides** : Fonctions d'easing pour contrôler la vélocité
- **Gestion du timing** : Contrôle précis de la durée et du timing

---

## 🏗️ Architecture des transitions

### Hiérarchie des classes

```
BaseTransition
    ├── FadeIn / FadeOut
    ├── Particletransition
    │   ├── DisintegrateRight / IntegrateRight
    │   ├── DisintegrateLeft / IntegrateLeft
    │   ├── DisintegrateUp / IntegrateUp
    │   └── DisintegrateDown / IntegrateDown
    └── VideoTransition
```

### Propriétés communes

Toutes les transitions héritent de `BaseTransition` avec les propriétés suivantes :

```python
from game_libs.transitions import BaseTransition

transition = BaseTransition(duration=1000)  # durée en millisecondes

# Propriétés
transition.progress      # float entre 0.0 et 1.0
transition.duration      # durée en millisecondes
transition.is_complete   # bool : transition terminée ?
transition.is_playing    # bool : transition en cours ?

# Méthodes
transition.start()       # Démarrer la transition
transition.update(dt)    # Mettre à jour (dt en secondes)
transition.render(surface)  # Dessiner l'effet
```

---

## 🎬 Transitions basiques : Fade

### FadeIn (Fondu entrant)

Une transition qui fond depuis une couleur opaque vers la scène visible.

```python
from game_libs.transitions import FadeIn

# Créer une transition fade in simple
fade_in = FadeIn(duration=1000)  # 1 seconde

# Avec une couleur personnalisée
fade_in = FadeIn(
    duration=800,           # millisecondes
    color=(0, 0, 0),        # noir (RGB)
)

# Avec une fonction d'easing
from game_libs.transitions.easing import ease_in_quad
fade_in = FadeIn(
    duration=1000,
    color=(255, 0, 0),      # rouge
    ease_func=ease_in_quad  # accélération progressive
)
```

**Flux visuel :**
```
[Couleur opaque] -----> [Scène visible]
```

### FadeOut (Fondu sortant)

L'inverse de FadeIn : la scène disparaît progressivement dans une couleur.

```python
from game_libs.transitions import FadeOut

# Fade out simple vers le noir
fade_out = FadeOut(duration=1000)

# Fade out vers le blanc
fade_out = FadeOut(
    duration=1500,
    color=(255, 255, 255),  # blanc
)

# Avec easing
from game_libs.transitions.easing import ease_out_cubic
fade_out = FadeOut(
    duration=800,
    color=(0, 0, 0),
    ease_func=ease_out_cubic
)
```

**Flux visuel :**
```
[Scène visible] -----> [Couleur opaque]
```

---

## ✨ Transitions par particules

Ces transitions divisent l'écran en petites tuiles qui se dispersent dans une direction donnée.

### DisintegrateRight / IntegrateRight

Les tuiles se dispersent vers la droite et disparaissent (Disintegrate), ou se réassemblent depuis la droite (Integrate).

```python
from game_libs.transitions import DisintegrateRight, IntegrateRight
from game_libs.transitions.easing import ease_out_quad

# Les tuiles se dispersent vers la droite
disintegrate_right = DisintegrateRight(
    duration=1500,          # millisecondes
    tile_size=16,           # taille de chaque tuile en pixels
    ease_func=ease_out_quad # fonction d'easing
)

# Les tuiles se réassemblent depuis la droite
integrate_right = IntegrateRight(
    duration=1500,
    tile_size=16
)
```

### DisintegrateLeft / IntegrateLeft

```python
from game_libs.transitions import DisintegrateLeft, IntegrateLeft

disintegrate_left = DisintegrateLeft(duration=1500, tile_size=16)
integrate_left = IntegrateLeft(duration=1500, tile_size=16)
```

### DisintegrateUp / IntegrateUp

```python
from game_libs.transitions import DisintegrateUp, IntegrateUp

disintegrate_up = DisintegrateUp(duration=1500, tile_size=16)
integrate_up = IntegrateUp(duration=1500, tile_size=16)
```

### DisintegrateDown / IntegrateDown

```python
from game_libs.transitions import DisintegrateDown, IntegrateDown

disintegrate_down = DisintegrateDown(duration=1500, tile_size=16)
integrate_down = IntegrateDown(duration=1500, tile_size=16)
```

### Paramètres des transitions par particules

```python
Particletransition(
    direction=Direction.RIGHT,   # Direction : RIGHT, LEFT, UP, DOWN
    mode="out",                  # "out" = Disintegrate, "in" = Integrate
    duration=1500,               # millisecondes
    tile_size=10,                # taille des tuiles (pixels)
    easing_func=lambda t: t      # fonction d'easing
)
```

---

## 🎥 Transitions vidéo

Lisez un fichier vidéo comme transition entre deux scènes.

```python
from game_libs.transitions import VideoTransition
from pathlib import Path

# Créer une transition vidéo
video_transition = VideoTransition(
    video_path=Path("assets/video/transition.mp4"),
    loop=False  # Ne pas boucler
)

# Avec boucle activée
video_transition = VideoTransition(
    video_path=Path("assets/video/transition.mp4"),
    loop=True   # Boucler jusqu'à ce que la durée soit atteinte
)
```

**Formats supportés :** .mp4, .avi, .mov, .webm

---

## ⏱️ Fonctions d'easing

Les fonctions d'easing contrôlent comment la transition progresse dans le temps.

```python
from game_libs.transitions.easing import (
    linear,
    ease_in_quad, ease_out_quad, ease_in_out_quad,
    ease_in_cubic, ease_out_cubic, ease_in_out_cubic,
    ease_in_quart, ease_out_quart, ease_in_out_quart,
    ease_in_quint, ease_out_quint, ease_in_out_quint,
    ease_in_sine, ease_out_sine, ease_in_out_sine,
    ease_in_expo, ease_out_expo, ease_in_out_expo,
    ease_in_circ, ease_out_circ, ease_in_out_circ,
    ease_in_elastic, ease_out_elastic, ease_in_out_elastic,
    ease_out_bounce, ease_in_bounce, ease_in_out_bounce
)
```

### Exemples d'utilisation

```python
from game_libs.transitions import FadeOut
from game_libs.transitions.easing import ease_out_quad

# Fade out avec accélération progressive
fade_out = FadeOut(
    duration=1000,
    ease_func=ease_out_quad
)

# Custom easing : accélération rapide
fade_in = FadeIn(
    duration=1000,
    ease_func=lambda t: t ** 3  # fonction personnalisée
)
```

---

## 🎮 Utiliser les transitions avec SceneManager

### Changer de scène avec une transition

```python
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeOut, FadeIn

# Créer les transitions
fade_out = FadeOut(duration=800, color=(0, 0, 0))
fade_in = FadeIn(duration=800, color=(0, 0, 0))

# Changer de scène avec transitions
SceneManager.change_scene(
    "menu",                 # Nom de la scène destination
    transition_out=fade_out,  # Transition de sortie (optionnel)
    transition_in=fade_in     # Transition d'entrée (optionnel)
)
```

### Transition simple (sortie uniquement)

```python
from game_libs.transitions import FadeOut

fade_out = FadeOut(duration=1000)
SceneManager.change_scene("game", transition_out=fade_out)
```

### Transition simple (entrée uniquement)

```python
from game_libs.transitions import FadeIn

fade_in = FadeIn(duration=1000)
SceneManager.change_scene("game", transition_in=fade_in)
```

### Sans transition (changement instantané)

```python
SceneManager.change_scene("game")
```

---

## 🔄 Cycle de vie des transitions

### États du SceneManager

```python
from game_libs.managers.scene import SceneState

SceneState.NORMAL          # Pas de transition
SceneState.TRANSITION_OUT  # Transition de sortie en cours
SceneState.TRANSITION_IN   # Transition d'entrée en cours
```

### Séquence d'une transition

```
[Scène A - NORMAL]
         ↓
[Transition OUT démarre]
         ↓
[État : TRANSITION_OUT]
         ↓
[Transition OUT terminée]
         ↓
[Scène A appelée : on_exit()]
[Scène B appelée : on_enter()]
         ↓
[Transition IN démarre (optionnel)]
         ↓
[État : TRANSITION_IN]
         ↓
[Transition IN terminée]
         ↓
[Scène B - NORMAL]
```

---

## 💡 Exemples complets

### Exemple 1 : Transition fade simple

```python
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeOut, FadeIn

class MenuScene(BaseScene):
    def handle_events(self):
        # Au clic sur "Play"
        SceneManager.change_scene(
            "game",
            transition_out=FadeOut(duration=600, color=(0, 0, 0)),
            transition_in=FadeIn(duration=600, color=(0, 0, 0))
        )
```

### Exemple 2 : Transition avec particules

```python
from game_libs.transitions import DisintegrateRight, IntegrateLeft
from game_libs.transitions.easing import ease_out_cubic

# Transition de sortie : particules se dispersent à droite
# Transition d'entrée : particules se réassemblent depuis la gauche
SceneManager.change_scene(
    "boss_level",
    transition_out=DisintegrateRight(
        duration=800,
        tile_size=20,
        ease_func=ease_out_cubic
    ),
    transition_in=IntegrateLeft(
        duration=800,
        tile_size=20,
        ease_func=ease_out_cubic
    )
)
```

### Exemple 3 : Transition personnalisée

```python
from game_libs.transitions import FadeOut

class CinematicFadeOut(FadeOut):
    """Fade out personnalisé pour cinématiques"""
    def __init__(self):
        super().__init__(
            duration=2000,  # 2 secondes
            color=(10, 10, 10),  # Très légèrement grisé
            ease_func=lambda t: t ** 0.5  # Easing personnalisé
        )

# Utilisation
SceneManager.change_scene(
    "ending",
    transition_out=CinematicFadeOut()
)
```

### Exemple 4 : Créer une transition personnalisée

```python
from game_libs.transitions import BaseTransition
from pygame import Surface, SRCALPHA

class CustomCircleTransition(BaseTransition):
    """Transition avec un cercle qui s'agrandit depuis le centre"""
    
    def __init__(self, duration: float = 1000):
        super().__init__(duration)
        self._radius_max = 0
    
    def render(self, surface: Surface) -> None:
        # Calculer le rayon en fonction de la progression
        width, height = surface.get_size()
        max_dist = ((width/2)**2 + (height/2)**2) ** 0.5
        self._radius_max = self.progress * max_dist
        
        # Dessiner un cercle qui s'agrandit
        overlay = Surface(surface.get_size(), SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fond transparent
        
        center = (width // 2, height // 2)
        radius = int(self._radius_max)
        
        # Créer l'effet circulaire
        import pygame
        pygame.draw.circle(overlay, (0, 0, 0, 128), center, radius)
        
        surface.blit(overlay, (0, 0))

# Utilisation
custom_transition = CustomCircleTransition(duration=1500)
SceneManager.change_scene("game", transition_out=custom_transition)
```

---

## 🐛 Dépannage

### La transition ne s'affiche pas

1. **Vérifier que `SceneManager.update()` et `SceneManager.render()` sont appelés dans la boucle principale**

```python
# Dans la boucle de jeu
dt = clock.tick(60) / 1000.0  # Delta time en secondes
SceneManager.update(dt)       # Mettre à jour les transitions
SceneManager.render(surface)  # Dessiner les transitions
```

2. **Vérifier que la transition est créée correctement**

```python
# ❌ Mauvais
transition = FadeOut()  # Pas de durée
transition = FadeIn(duration=0)  # Durée nulle

# ✅ Correct
transition = FadeOut(duration=1000)
transition = FadeIn(duration=1000)
```

### La transition est trop rapide/lente

Ajuster le paramètre `duration` en millisecondes :

```python
# Trop rapide (100ms)
transition = FadeOut(duration=100)

# Plus lent (3 secondes)
transition = FadeOut(duration=3000)

# Tempo rapide (500ms)
transition = FadeOut(duration=500)
```

### L'easing ne fonctionne pas

Vérifier que la fonction d'easing prend un float entre 0.0 et 1.0 et retourne un float :

```python
# ❌ Mauvais
ease_func = lambda: t  # Pas d'argument

# ✅ Correct
ease_func = lambda t: t ** 2
```

---

## 📚 Références

- **BaseTransition** : Classe de base pour toutes les transitions
- **FadeIn / FadeOut** : Transitions par fondu
- **Particletransition** : Transitions par particules
- **VideoTransition** : Transitions vidéo
- **easing** : Fonctions d'animation fluide

---

## 📝 Notes importantes

- Les transitions ne bloquent pas l'exécution du jeu (non-blocking)
- Plusieurs transitions peuvent être en cours simultanément
- Les transitions sont gérées automatiquement par le `SceneManager`
- Toujours appeler `transition.start()` avant de l'utiliser
- Le `progress` de la transition est entre 0.0 (début) et 1.0 (fin)

---

## 🎨 Conseils de design

1. **Durée** : 300-800ms pour des transitions rapides, 1000-2000ms pour cinématiques
2. **Couleurs** : Utiliser des couleurs cohérentes avec l'ambiance du jeu
3. **Easing** : `ease_out_*` pour des transitions naturelles
4. **Particules** : Tile size petit (10-16px) pour plus de fluidité
5. **Vidéo** : Utiliser des vidéos courtes et compressées pour les transitions
