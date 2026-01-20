# SceneManager - Guide d'utilisation

## 📖 Description

Le **SceneManager** gère l'ensemble des scènes du jeu et leurs transitions. Il permet de passer d'une scène à l'autre (menu, jeu, options, etc.) de manière fluide avec des effets de transition optionnels.

**Voir aussi :**
- [📖 Tutoriel des scènes](Scenes.md) - Architecture complète et création
- [🎬 Tutoriel des transitions](Transitions.md) - Effets de transition
- [README.md](README.md) - Plan de navigation générale

## 🎯 Caractéristiques principales

- Gestion centralisée de toutes les scènes
- Système de transitions (fade-in, fade-out, particules, vidéo)
- Cycle de vie des scènes (init, enter, exit, update, render)
- Historique des scènes (scène précédente)
- États de transition (normal, transition_in, transition_out)

---

## 🏗️ Architecture

**Pour une description complète de l'architecture des scènes, consultez [Scenes.md](Scenes.md).**

Le SceneManager gère le cycle de vie complet des scènes :
- **Initialisation** (`init()`) : Une seule fois au démarrage
- **Entrée** (`on_enter()`) : À chaque activation de la scène
- **Mise à jour** (`update(dt)`) : À chaque frame
- **Gestion des événements** (`handle_events()`) : À chaque frame
- **Rendu** (`render(surface)`) : À chaque frame
- **Sortie** (`on_exit()`) : À chaque désactivation de la scène

**Pour créer une nouvelle scène, consultez [Scenes.md](Scenes.md) section "✨ Créer une nouvelle scène".**

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

## 📋 Exemples

**Pour des exemples complets de scènes, consultez [Scenes.md](Scenes.md) section "💡 Exemples complets".**

**Pour la boucle principale du jeu, consultez [README.md](README.md) section "🚀 Initialisation rapide".**

### Exemple rapide : Changer de scène

```python
from game_libs.managers.scene import SceneManager
from game_libs.managers.event import KeyState
from game_libs.transitions import FadeOut, FadeIn

class MyScene(BaseScene):
    def handle_events(self):
        keys = self.event_manager.get_keys()
        
        if keys.get("ACCEPT") == KeyState.PRESSED:
            SceneManager.change_scene(
                "game",
                transition_out=FadeOut(duration=500),
                transition_in=FadeIn(duration=500)
            )
```

---

## 🎨 Utilisation avec des transitions

**Pour créer des transitions personnalisées, consultez [Transitions.md](Transitions.md) section "✨ Créer une transition personnalisée".**

### Exemples d'utilisation

```python
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeIn, FadeOut, DisintegrateRight

# Transition simple
fade_out = FadeOut(duration=800)
SceneManager.change_scene("menu", transition_out=fade_out)

# Transition entrée + sortie
fade_out = FadeOut(duration=800)
fade_in = FadeIn(duration=800)
SceneManager.change_scene("game", transition_out=fade_out, transition_in=fade_in)

# Transition avec particules
disintegrate = DisintegrateRight(duration=1500, tile_size=16)
SceneManager.change_scene("next_level", transition_out=disintegrate)
```

**Pour tous les types de transitions disponibles, consultez [Transitions.md](Transitions.md).**

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
