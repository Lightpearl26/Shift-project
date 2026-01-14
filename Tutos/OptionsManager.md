# OptionsManager - Guide d'utilisation

## 📖 Description

Le **OptionsManager** gère toutes les options et paramètres du jeu, avec sauvegarde et chargement automatiques depuis un fichier JSON. Il synchronise automatiquement les paramètres avec les autres managers (AudioManager, DisplayManager, EventManager).

## 🎯 Caractéristiques principales

- Gestion centralisée de tous les paramètres
- Sauvegarde/chargement automatique en JSON
- Synchronisation avec les autres managers
- Validation des valeurs
- Valeurs par défaut depuis la config

---

## 💾 Fichier de sauvegarde

Les options sont sauvegardées dans : `.cache/settings.json`

Structure du fichier :

```json
{
  "master_volume": 1.0,
  "bgm_volume": 1.0,
  "bgs_volume": 1.0,
  "me_volume": 1.0,
  "se_volume": 1.0,
  "fullscreen": false,
  "vsync": true,
  "fps_cap": 0,
  "key_bindings": {
    "UP": [273, 119],
    "DOWN": [274],
    "LEFT": [276],
    "RIGHT": [275],
    "JUMP": [32, 122],
    "PAUSE": [27],
    "SPRINT": [304]
  }
}
```

---

## 🚀 Initialisation

### init()

Charge les options sauvegardées et les applique aux managers. **À appeler au démarrage du jeu.**

```python
from game_libs.managers.options import OptionsManager

# Initialisation (charge et applique les options)
OptionsManager.init()
```

**Ce que fait init() :**

1. Charge le fichier `settings.json` s'il existe
2. Fusionne avec les valeurs par défaut (pour les nouvelles options)
3. Applique les paramètres à AudioManager, DisplayManager et EventManager

---

## 🔊 Gestion des volumes audio

### Getters

```python
# Obtenir les volumes (0.0 à 1.0)
master = OptionsManager.master_volume()
bgm = OptionsManager.bgm_volume()
bgs = OptionsManager.bgs_volume()
me = OptionsManager.me_volume()
se = OptionsManager.se_volume()
```

### Setters

```python
# Définir les volumes
OptionsManager.set_master_volume(0.8)   # 80%
OptionsManager.set_bgm_volume(0.9)      # 90%
OptionsManager.set_bgs_volume(0.7)      # 70%
OptionsManager.set_me_volume(1.0)       # 100%
OptionsManager.set_se_volume(0.85)      # 85%
```

**Note :** Les setters :

- Synchronisent automatiquement avec AudioManager
- Valident les valeurs (clamp entre 0.0 et 1.0)
- Ne sauvegardent pas automatiquement (appelez `save()`)

**Exemple d'interface de réglage :**

```python
def create_volume_slider(label, get_func, set_func):
    current_volume = get_func()
    # ... créer le slider UI ...
    
    def on_slider_change(new_value):
        set_func(new_value)
        OptionsManager.save()  # Sauvegarder immédiatement

# Menu options
create_volume_slider("Master", 
                     OptionsManager.master_volume, 
                     OptionsManager.set_master_volume)
create_volume_slider("Musique", 
                     OptionsManager.bgm_volume, 
                     OptionsManager.set_bgm_volume)
```

---

## 🖥️ Paramètres d'affichage

### Plein écran

```python
# Vérifier l'état
is_fullscreen = OptionsManager.is_fullscreen()

# Activer/désactiver
OptionsManager.set_fullscreen(True)   # Plein écran
OptionsManager.set_fullscreen(False)  # Fenêtré
```

**Note :** Synchronise automatiquement avec DisplayManager et bascule le mode si nécessaire.

### VSync

```python
# Vérifier l'état
is_vsync_on = OptionsManager.is_vsync_enabled()

# Activer/désactiver
OptionsManager.set_vsync(True)   # VSync activé
OptionsManager.set_vsync(False)  # VSync désactivé
```

**⚠️ Important :** Changer le VSync recréé la fenêtre (peut causer un bref flash).

### Limitation FPS

```python
# Obtenir la limite actuelle
fps_cap = OptionsManager.get_fps_cap()  # 0 = illimité

# Définir une limite
OptionsManager.set_fps_cap(60)   # Limiter à 60 FPS
OptionsManager.set_fps_cap(144)  # Limiter à 144 FPS
OptionsManager.set_fps_cap(0)    # Illimité
```

**Valeurs recommandées :**

- `60` : Standard pour la plupart des jeux
- `144` : Pour les écrans haute fréquence
- `0` : Illimité (avec VSync pour éviter le tearing)

---

## ⌨️ Configuration des touches

### Obtenir les mappings

```python
# Tous les mappings
all_bindings = OptionsManager.get_key_bindings()
# Retourne: {"UP": [273, 119], "DOWN": [274], ...}

# Mapping d'une action spécifique
jump_keys = OptionsManager.get_action_keys("JUMP")
# Retourne: [32, 122]  (Space, Z)
```

### Modifier les mappings

```python
# Changer les touches d'une action
OptionsManager.set_action_keys("JUMP", [32, 119])  # Space + W

# Exemple : permettre au joueur de reconfigurer les touches
def rebind_key(action_name):
    print(f"Pressez une touche pour {action_name}...")
    new_key = wait_for_key_press()
    
    # Définir le nouveau mapping (remplace l'ancien)
    OptionsManager.set_action_keys(action_name, [new_key])
    
    # Sauvegarder
    OptionsManager.save()
```

**Actions disponibles :**

- `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`
- `"JUMP"`, `"SPRINT"`, `"PAUSE"`

---

## 💾 Sauvegarde et chargement

### save()

Sauvegarde toutes les options actuelles dans le fichier JSON.

```python
# Sauvegarder les options
OptionsManager.save()
```

**Quand sauvegarder :**

- Après chaque modification d'option par l'utilisateur
- À la fermeture du jeu
- Après validation d'un menu d'options

### load()

Charge les options depuis le fichier (appelé automatiquement par `init()`).

```python
# Recharger les options (rare, généralement fait par init())
OptionsManager.load()
```

---

## 🔍 Accès global aux options

### get_options()

Retourne toutes les options sous forme de dictionnaire.

```python
all_options = OptionsManager.get_options()
print(all_options)
# {
#   "master_volume": 0.8,
#   "bgm_volume": 0.9,
#   ...
# }
```

Utile pour :

- Afficher toutes les options dans un menu
- Exporter les paramètres
- Debugging

---

## 📋 Exemple complet : Menu d'options

```python
import pygame
from game_libs.managers.options import OptionsManager
from game_libs.managers.display import DisplayManager

class OptionsMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.selected = 0
        self.options = [
            ("Master Volume", "volume", "master"),
            ("Music Volume", "volume", "bgm"),
            ("Sound Effects", "volume", "se"),
            ("Fullscreen", "bool", "fullscreen"),
            ("VSync", "bool", "vsync"),
            ("FPS Cap", "fps", None),
        ]
    
    def render(self, surface):
        y = 100
        for i, (label, opt_type, key) in enumerate(self.options):
            # Obtenir la valeur actuelle
            if opt_type == "volume":
                if key == "master":
                    value = f"{OptionsManager.master_volume() * 100:.0f}%"
                elif key == "bgm":
                    value = f"{OptionsManager.bgm_volume() * 100:.0f}%"
                elif key == "se":
                    value = f"{OptionsManager.se_volume() * 100:.0f}%"
            elif opt_type == "bool":
                if key == "fullscreen":
                    value = "ON" if OptionsManager.is_fullscreen() else "OFF"
                elif key == "vsync":
                    value = "ON" if OptionsManager.is_vsync_enabled() else "OFF"
            elif opt_type == "fps":
                fps_cap = OptionsManager.get_fps_cap()
                value = "Unlimited" if fps_cap == 0 else f"{fps_cap}"
            
            # Afficher
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(f"{label}: {value}", True, color)
            surface.blit(text, (100, y))
            y += 50
    
    def handle_input(self, keys):
        from game_libs.managers.event import KeyState
        
        # Navigation
        if keys["DOWN"] == KeyState.PRESSED:
            self.selected = (self.selected + 1) % len(self.options)
        elif keys["UP"] == KeyState.PRESSED:
            self.selected = (self.selected - 1) % len(self.options)
        
        # Modification
        label, opt_type, key = self.options[self.selected]
        
        if keys["RIGHT"] == KeyState.PRESSED:
            self.increase_option(opt_type, key)
        elif keys["LEFT"] == KeyState.PRESSED:
            self.decrease_option(opt_type, key)
    
    def increase_option(self, opt_type, key):
        if opt_type == "volume":
            if key == "master":
                vol = min(1.0, OptionsManager.master_volume() + 0.1)
                OptionsManager.set_master_volume(vol)
            elif key == "bgm":
                vol = min(1.0, OptionsManager.bgm_volume() + 0.1)
                OptionsManager.set_bgm_volume(vol)
            elif key == "se":
                vol = min(1.0, OptionsManager.se_volume() + 0.1)
                OptionsManager.set_se_volume(vol)
        elif opt_type == "bool":
            if key == "fullscreen":
                OptionsManager.set_fullscreen(True)
            elif key == "vsync":
                OptionsManager.set_vsync(True)
        elif opt_type == "fps":
            caps = [0, 30, 60, 120, 144, 240]
            current = OptionsManager.get_fps_cap()
            idx = caps.index(current) if current in caps else 0
            next_idx = (idx + 1) % len(caps)
            OptionsManager.set_fps_cap(caps[next_idx])
        
        # Sauvegarder immédiatement
        OptionsManager.save()
    
    def decrease_option(self, opt_type, key):
        if opt_type == "volume":
            if key == "master":
                vol = max(0.0, OptionsManager.master_volume() - 0.1)
                OptionsManager.set_master_volume(vol)
            elif key == "bgm":
                vol = max(0.0, OptionsManager.bgm_volume() - 0.1)
                OptionsManager.set_bgm_volume(vol)
            elif key == "se":
                vol = max(0.0, OptionsManager.se_volume() - 0.1)
                OptionsManager.set_se_volume(vol)
        elif opt_type == "bool":
            if key == "fullscreen":
                OptionsManager.set_fullscreen(False)
            elif key == "vsync":
                OptionsManager.set_vsync(False)
        elif opt_type == "fps":
            caps = [0, 30, 60, 120, 144, 240]
            current = OptionsManager.get_fps_cap()
            idx = caps.index(current) if current in caps else 0
            prev_idx = (idx - 1) % len(caps)
            OptionsManager.set_fps_cap(caps[prev_idx])
        
        OptionsManager.save()

# Utilisation
menu = OptionsMenu()
# Dans la boucle : menu.handle_input(keys) et menu.render(surface)
```

---

## 📋 Exemple complet : Initialisation du jeu

```python
import pygame
from game_libs.managers.options import OptionsManager
from game_libs.managers.display import DisplayManager
from game_libs.managers.audio import AudioManager
from game_libs.managers.event import EventManager

def init_game():
    """Initialisation complète du jeu avec gestion des options"""
    
    # 1. Initialiser pygame
    pygame.init()
    
    # 2. Charger les options (AVANT les autres managers)
    OptionsManager.init()
    
    # 3. Initialiser le DisplayManager
    # (il récupère ses paramètres via OptionsManager)
    DisplayManager.init(
        width=1280,
        height=720,
        caption="Mon Jeu"
    )
    
    # 4. Initialiser l'AudioManager
    AudioManager.init()
    
    # Les volumes sont déjà configurés par OptionsManager.init()
    
    # 5. EventManager est prêt (les key bindings sont chargés)
    
    print("Jeu initialisé avec les options sauvegardées")
    print(f"Fullscreen: {OptionsManager.is_fullscreen()}")
    print(f"VSync: {OptionsManager.is_vsync_enabled()}")
    print(f"FPS Cap: {OptionsManager.get_fps_cap()}")
    print(f"Master Volume: {OptionsManager.master_volume()}")

def shutdown_game():
    """Fermeture propre du jeu"""
    
    # Sauvegarder les options actuelles
    OptionsManager.save()
    
    # Fermer les managers
    AudioManager.stop_all()
    DisplayManager.shutdown()
    
    pygame.quit()

# Point d'entrée
if __name__ == "__main__":
    init_game()
    
    # ... boucle de jeu ...
    
    shutdown_game()
```

---

## 🔄 Réinitialisation aux valeurs par défaut

Pour réinitialiser toutes les options aux valeurs par défaut :

```python
def reset_to_defaults():
    """Réinitialiser toutes les options aux valeurs par défaut"""
    
    # Volumes
    OptionsManager.set_master_volume(1.0)
    OptionsManager.set_bgm_volume(1.0)
    OptionsManager.set_bgs_volume(1.0)
    OptionsManager.set_me_volume(1.0)
    OptionsManager.set_se_volume(1.0)
    
    # Affichage
    OptionsManager.set_fullscreen(False)
    OptionsManager.set_vsync(True)
    OptionsManager.set_fps_cap(0)
    
    # Key bindings (depuis config)
    from game_libs import config
    default_bindings = {
        "UP": list(config.KEYS_UP),
        "DOWN": list(config.KEYS_DOWN),
        "LEFT": list(config.KEYS_LEFT),
        "RIGHT": list(config.KEYS_RIGHT),
        "JUMP": list(config.KEYS_JUMP),
        "PAUSE": list(config.KEYS_PAUSE),
        "SPRINT": list(config.KEYS_SPRINT)
    }
    
    for action, keys in default_bindings.items():
        OptionsManager.set_action_keys(action, keys)
    
    # Sauvegarder
    OptionsManager.save()
    
    print("Options réinitialisées aux valeurs par défaut")
```

---

## ⚠️ Notes importantes

1. **Ordre d'initialisation** : Appelez `OptionsManager.init()` AVANT les autres managers pour que les paramètres soient appliqués correctement

2. **Sauvegarde manuelle** : Les changements d'options ne sont PAS sauvegardés automatiquement. Appelez `save()` après chaque modification

3. **Synchronisation** : Les setters synchronisent automatiquement avec les managers concernés, pas besoin de le faire manuellement

4. **Validation** : Les volumes sont automatiquement clampés entre 0.0 et 1.0

5. **Fichier manquant** : Si `settings.json` n'existe pas, les valeurs par défaut du config sont utilisées

6. **Fusion des options** : Au chargement, les nouvelles options sont fusionnées avec les anciennes (permet d'ajouter de nouvelles options sans casser les sauvegardes)

---

## 🐛 Débogage

Activez les logs pour suivre les opérations :

```python
from game_libs import config

config.LOG_DEBUG = True
```

Messages typiques :

```text
[OptionsManager] Initializing...
[OptionsManager] Options loaded from .cache/settings.json
[OptionsManager] Synchronized audio settings
[OptionsManager] Synchronized display settings
[OptionsManager] Synchronized key bindings
[OptionsManager] Options saved to .cache/settings.json
```

---

## 💡 Conseils d'utilisation

1. **Feedback immédiat** : Appliquez les changements immédiatement (avant la sauvegarde) pour que l'utilisateur voie l'effet

2. **Bouton "Appliquer"** : Pour les options coûteuses (VSync, fullscreen), proposez un bouton "Appliquer" plutôt qu'une application immédiate

3. **Confirmation** : Pour le plein écran, proposez une confirmation avec timeout (cas d'écran noir)

4. **Valeurs limites** : Affichez clairement les valeurs min/max dans votre UI

5. **Son de preview** : Jouez un son test lors du réglage des volumes pour feedback immédiat

6. **Sauvegarde sur validation** : Dans un menu d'options, sauvegardez quand l'utilisateur valide ("OK"), pas à chaque changement
