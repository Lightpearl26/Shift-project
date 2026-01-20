# EventManager - Guide d'utilisation

## 📖 Description

Le **EventManager** gère tous les événements d'entrée utilisateur du jeu : clavier, manette (gamepad), et système de timers. Il traduit les entrées physiques en actions de jeu et permet de détecter les états de touches (pressée, maintenue, relâchée).

**Voir aussi :**
- [📚 Managers.md](Managers.md) - Vue d'ensemble des managers
- [📖 Scenes.md](Scenes.md) - Utilisation dans les scènes
- [SceneManager.md](SceneManager.md) - Gestion des scènes
- [README.md](README.md) - Plan de navigation générale

---

## 🎯 Caractéristiques principales

- Mapping des touches clavier configurables
- Support des manettes de jeu (gamepads)
- Détection d'états : PRESSED, HELD, RELEASED (fusion clavier + manette)
- Système de timers intégré avec pause/reprise
- Validation des mappings (codes >= 0)

---

## 🎮 États des touches (KeyState)

Le système utilise un enum `KeyState` pour représenter l'état des touches :

```python
from game_libs.managers.event import KeyState

# États possibles
KeyState.RELEASED  # Touche relâchée (non pressée)
KeyState.PRESSED   # Touche vient d'être pressée (ce frame)
KeyState.HELD      # Touche maintenue (plusieurs frames)
```

**Différence importante :**

- `PRESSED` : Ne se déclenche qu'une seule frame (frame d'appui)
- `HELD` : Se déclenche tant que la touche reste enfoncée après le premier frame
- `RELEASED` : Touche non pressée

---

## ⌨️ Configuration des touches

### Actions disponibles par défaut

Le système définit 7 actions standard :

- `UP` : Déplacement vers le haut
- `DOWN` : Déplacement vers le bas
- `LEFT` : Déplacement vers la gauche
- `RIGHT` : Déplacement vers la droite
- `JUMP` : Saut
- `SPRINT` : Course/Sprint
- `PAUSE` : Pause

### Mapping clavier

Les touches sont définies dans le fichier `config.py` avec des scancodes pygame :

```python
# Dans config.py
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z, K_w, K_SPACE, K_LSHIFT, K_ESCAPE

KEYS_UP = {K_UP, K_z}           # Flèche haut ou Z
KEYS_DOWN = {K_DOWN}            # Flèche bas
KEYS_LEFT = {K_LEFT}            # Flèche gauche
KEYS_RIGHT = {K_RIGHT}          # Flèche droite
KEYS_JUMP = {K_SPACE, K_w}      # Espace ou W
KEYS_SPRINT = {K_LSHIFT}        # Shift gauche
KEYS_PAUSE = {K_ESCAPE}         # Échap
```

### Changer le mapping en cours de jeu

```python
from game_libs.managers.event import EventManager

# Définir un nouveau mapping complet
new_mapping = {
    "UP": [273, 119],      # K_UP, K_w
    "DOWN": [274, 115],    # K_DOWN, K_s
    "LEFT": [276, 97],     # K_LEFT, K_a
    "RIGHT": [275, 100],   # K_RIGHT, K_d
    "JUMP": [32],          # K_SPACE
    "SPRINT": [304],       # K_LSHIFT
    "PAUSE": [27]          # K_ESCAPE
}

EventManager.set_key_mapping(new_mapping)
```

---

## 🎮 Configuration manette (Gamepad)

### Mapping des boutons

Par défaut, le gamepad utilise une disposition standard (Xbox/PlayStation) :

```python
# Boutons par défaut
JUMP   = bouton 0   # A / Croix
SPRINT = bouton 10  # LB / L1
PAUSE  = boutons 5 ou 1  # Start / Options / (selon pad)
```

### Directions

Le gamepad gère les directions via :

1. **D-Pad** (prioritaire) : Boutons directionnels
2. **Stick analogique gauche** (fallback) : Avec seuil de détection

### Personnaliser le mapping gamepad

```python
# Changer le mapping des boutons
gamepad_mapping = {
    "JUMP": [0, 2],      # Boutons A et X
    "SPRINT": [10],      # Bouton RB
    "PAUSE": [7]         # Bouton Start
}

EventManager.set_gamepad_mapping(gamepad_mapping)
```

**Note :** Les directions (UP, DOWN, LEFT, RIGHT) sont gérées automatiquement par le D-Pad/stick et ne nécessitent pas de configuration.

---

## 🔄 Mise à jour et lecture des entrées

### update()

**⚠️ IMPORTANT :** Appelez cette méthode une fois par frame avant de lire les états (après avoir pompé les événements pygame via `pygame.event.get()` ou `pygame.event.pump()`).

```python
# Dans la boucle de jeu
while running:
    # Pomper les événements pygame pour mettre à jour l'état des entrées
    pygame.event.pump()

    dt = DisplayManager.get_delta_time()
    
    # Mettre à jour les entrées (fusion clavier + manette)
    EventManager.update(dt)
    
    # Lire les états
    keys = EventManager.get_keys()
    
    # Logique du jeu...
```

### get_keys()

Retourne un dictionnaire avec les états de toutes les actions.

```python
keys = EventManager.get_keys()

# Accès aux états
if keys["JUMP"] == KeyState.PRESSED:
    player_jump()  # Saut une seule fois

# Déplacements continus : PRESSED ou HELD
if keys["RIGHT"] & (KeyState.PRESSED | KeyState.HELD):
    player_move_right()

if keys["LEFT"] & (KeyState.PRESSED | KeyState.HELD):
    player_start_moving_left()
```

---

## 🎯 Utilisation pratique

### Déplacement du joueur

```python
def update_player_movement(dt):
    keys = EventManager.get_keys()
    
    # Déplacement horizontal (maintenu)
    if keys["RIGHT"] & (KeyState.PRESSED | KeyState.HELD):
        player.move_right(dt)
    elif keys["LEFT"] & (KeyState.PRESSED | KeyState.HELD):
        player.move_left(dt)
    else:
        player.stop_moving()
    
    # Sprint (combinaison)
    if keys["SPRINT"] & (KeyState.PRESSED | KeyState.HELD):
        player.set_sprinting(True)
    else:
        player.set_sprinting(False)
```

### Actions ponctuelles

```python
def handle_actions():
    keys = EventManager.get_keys()
    
    # Saut : une seule fois à l'appui
    if keys["JUMP"] == KeyState.PRESSED:
        if player.is_on_ground():
            player.jump()
    
    # Pause : ouvrir le menu
    if keys["PAUSE"] == KeyState.PRESSED:
        toggle_pause_menu()
```

### Interactions contextuelles

```python
def update_game():
    keys = EventManager.get_keys()
    
    # Interaction avec un objet
    if keys["UP"] == KeyState.PRESSED:
        if player.is_near_door():
            open_door()
        elif player.is_near_npc():
            start_dialogue()
        elif player.is_near_chest():
            open_chest()
```

---

## ⏲️ Système de Timers

Le EventManager inclut un système de timers très pratique pour gérer des événements temporisés.

### Ajouter un timer

```python
# Timer simple (une fois)
EventManager.add_timer(
    name="explosion_delay",
    duration=3.0,        # 3 secondes
    repeat=False         # Ne se répète pas
)

# Timer répétitif
EventManager.add_timer(
    name="spawn_enemy",
    duration=5.0,        # Toutes les 5 secondes
    repeat=True          # Se répète indéfiniment
)
```

### Vérifier si un timer est déclenché

```python
# Dans la boucle de jeu
def update():
    # Les timers sont mis à jour automatiquement dans EventManager.update(dt)
    
    # Vérifier si le timer s'est déclenché ce frame
    if EventManager.get_timer("explosion_delay"):
        create_explosion()
    
    if EventManager.get_timer("spawn_enemy"):
        spawn_random_enemy()
```

### Gérer les timers

```python
# Vérifier si un timer existe
if EventManager.has_timer("my_timer"):
    print("Timer existe")

# Obtenir le temps restant
remaining = EventManager.get_timer_remaining("my_timer")
print(f"Temps restant: {remaining:.2f}s")

# Supprimer un timer
EventManager.kill_timer("my_timer")
```

### Pause des timers

```python
# Mettre en pause tous les timers
EventManager.pause_timers()

# Reprendre tous les timers
EventManager.resume_timers()

# Pause d'un timer spécifique
EventManager.pause_timer("spawn_enemy")

# Reprendre un timer spécifique
EventManager.resume_timer("spawn_enemy")
```

### Exemples d'utilisation des timers

**Cooldown de compétence :**

```python
def use_special_attack():
    if not EventManager.has_timer("special_attack_cooldown"):
        # Effectuer l'attaque
        perform_special_attack()
        
        # Démarrer le cooldown
        EventManager.add_timer("special_attack_cooldown", duration=2.0)
    else:
        # Afficher le temps restant
        remaining = EventManager.get_timer_remaining("special_attack_cooldown")
        show_message(f"Cooldown: {remaining:.1f}s")
```

**Spawn d'ennemis périodique :**

```python
def init_wave_system():
    # Spawn toutes les 10 secondes
    EventManager.add_timer("enemy_spawn", duration=10.0, repeat=True)

def update_wave_system():
    if EventManager.get_timer("enemy_spawn"):
        spawn_enemy_wave()
        wave_number += 1
```

**Effet temporaire :**

```python
def activate_power_up():
    player.speed *= 2
    EventManager.add_timer("power_up_duration", duration=5.0)

def update_power_ups():
    if EventManager.get_timer("power_up_duration"):
        # Fin du power-up
        player.speed /= 2
        show_message("Power-up terminé!")
```

---

## 🔄 Reset

### reset()

Réinitialise complètement l'EventManager (utile lors des changements de scène).

```python
# Au changement de niveau
def load_new_level():
    EventManager.reset()  # Efface tous les timers et états
    # ... charger le niveau ...
```

---

## 📋 Exemple complet

```python
import pygame
from game_libs.managers.display import DisplayManager
from game_libs.managers.event import EventManager, KeyState

# Initialisation
pygame.init()
DisplayManager.init(width=1280, height=720)

# Classe joueur simplifiée
class Player:
    def __init__(self):
        self.x = 640
        self.y = 360
        self.speed = 200
        self.can_dash = True
    
    def update(self, dt):
        keys = EventManager.get_keys()
        
        # Déplacement de base
        dx = 0
        dy = 0
        
        if keys["RIGHT"] & (KeyState.PRESSED | KeyState.HELD):
            dx += self.speed * dt
        if keys["LEFT"] & (KeyState.PRESSED | KeyState.HELD):
            dx -= self.speed * dt
        if keys["DOWN"] & (KeyState.PRESSED | KeyState.HELD):
            dy += self.speed * dt
        if keys["UP"] & (KeyState.PRESSED | KeyState.HELD):
            dy -= self.speed * dt
        
        # Sprint
        if keys["SPRINT"] & (KeyState.PRESSED | KeyState.HELD):
            dx *= 2
            dy *= 2
        
        # Dash avec cooldown
        if keys["JUMP"] == KeyState.PRESSED and self.can_dash:
            self.dash(dx, dy)
            self.can_dash = False
            EventManager.add_timer("dash_cooldown", duration=1.0)
        
        # Vérifier le cooldown
        if EventManager.get_timer("dash_cooldown"):
            self.can_dash = True
        
        self.x += dx
        self.y += dy
    
    def dash(self, dx, dy):
        # Dash rapide
        self.x += dx * 3
        self.y += dy * 3

# Boucle de jeu
player = Player()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Mise à jour
    DisplayManager.tick()
    dt = DisplayManager.get_delta_time()
    
    EventManager.update(dt)  # ⚠️ IMPORTANT : Appeler avant de lire les touches
    
    # Pause
    keys = EventManager.get_keys()
    if keys["PAUSE"] == KeyState.PRESSED:
        print("Jeu en pause")
    
    player.update(dt)
    
    # Rendu
    surface = DisplayManager.get_surface()
    surface.fill((20, 20, 40))
    
    # Dessiner le joueur
    pygame.draw.circle(surface, (255, 100, 100), (int(player.x), int(player.y)), 20)
    
    DisplayManager.flip()

# Nettoyage
DisplayManager.shutdown()
pygame.quit()
```

---

## 🔧 Intégration avec OptionsManager

Les mappings de touches peuvent être sauvegardés et chargés via l'OptionsManager :

```python
from game_libs.managers.options import OptionsManager

# Charger les mappings sauvegardés
OptionsManager.init()  # Charge et applique automatiquement les mappings

# Changer un mapping
OptionsManager.set_action_keys("JUMP", [32, 119])  # Space + W

# Sauvegarder
OptionsManager.save()
```

---

## ⚠️ Notes importantes

1. **update() obligatoire** : Appelez `EventManager.update(dt)` une fois par frame, après avoir pompé les événements pygame.

2. **Fusion clavier/manette** : Précedence `PRESSED` > `HELD` > `RELEASED` pour chaque action.

3. **Manette** : La détection du premier gamepad est automatique lors du premier `update()`.

4. **Timers** : Les timers stockent `time_left`, `duration`, `repeat`, `paused`. Ils respectent les pauses globales ou ciblées.

5. **Scancodes** : Utilisez les constantes pygame (`pygame.K_*`). Les mappings acceptent tout code entier >= 0.

---

## 🐛 Débogage

Activez les logs pour voir les événements :

```python
from game_libs import config

config.LOG_DEBUG = True
```

Messages typiques :

```text
[EventManager] Key mapping updated
[GamepadMapping] Gamepad detected: Xbox Controller
[EventManager] Timer 'explosion_delay' added: duration 3.0s, repeat=False
[EventManager] Timer 'explosion_delay' triggered
[EventManager] Updated key states and timers with dt=0.016s
```

---

## 💡 Conseils d'utilisation

1. **PRESSED vs HELD** : Utilisez `PRESSED` pour les actions ponctuelles (saut, tir) et `PRESSED | HELD` pour les actions continues (déplacement)

2. **Combinaisons** : Testez plusieurs touches ensemble pour des combos (ex: SPRINT + JUMP)

3. **Feedback utilisateur** : Affichez les cooldowns et états des timers pour informer le joueur

4. **Configuration** : Permettez aux joueurs de reconfigurer les touches via un menu d'options

5. **Timers** : Préférez les timers du EventManager plutôt que de gérer le temps manuellement avec `dt`
