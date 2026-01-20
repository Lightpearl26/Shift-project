# Managers - Vue d'ensemble

## 📖 Description

Les **Managers** sont des systèmes centralisés qui gèrent différents aspects du jeu. Ils fournissent une interface unique pour accéder aux fonctionnalités importantes et facilitent l'intégration entre les différentes parties du jeu.

**Voir aussi :**
- [README.md](README.md) - Plan de navigation générale
- [SceneManager.md](SceneManager.md) - Gestion des scènes

---

## 🏗️ Architecture des Managers

```
┌─────────────────────────────────────────────────────┐
│         Managers - Système centralisé              │
├──────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐  ┌──────────────────────┐    │
│  │ DisplayManager  │  │  AudioManager        │    │
│  ├─────────────────┤  ├──────────────────────┤    │
│  │ • Fenêtre       │  │ • BGM (musique)      │    │
│  │ • Plein écran   │  │ • BGS (ambiance)     │    │
│  │ • FPS           │  │ • ME (musicaux)      │    │
│  │ • Delta time    │  │ • SE (effets)        │    │
│  │ • Screenshots   │  │ • Volumes            │    │
│  └─────────────────┘  └──────────────────────┘    │
│                                                     │
│  ┌─────────────────┐  ┌──────────────────────┐    │
│  │ EventManager    │  │  OptionsManager      │    │
│  ├─────────────────┤  ├──────────────────────┤    │
│  │ • Clavier       │  │ • Paramètres         │    │
│  │ • Manette       │  │ • Volumes            │    │
│  │ • États (P/H/R) │  │ • Affichage          │    │
│  │ • Timers        │  │ • Sauvegarde JSON    │    │
│  │ • Configurations│  │ • Chargement         │    │
│  └─────────────────┘  └──────────────────────┘    │
│                                                     │
│  ┌──────────────────────────────────────────┐     │
│  │    SceneManager + Transitions            │     │
│  ├──────────────────────────────────────────┤     │
│  │ • Gestion des scènes                     │     │
│  │ • Changement de scène                    │     │
│  │ • Transitions visuelles                  │     │
│  │ • Historique                             │     │
│  └──────────────────────────────────────────┘     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 Ordre d'initialisation

**IMPORTANT : Respectez cet ordre !**

```python
import pygame
from game_libs.managers.options import OptionsManager
from game_libs.managers.display import DisplayManager
from game_libs.managers.audio import AudioManager
from game_libs.managers.scene import SceneManager

def main():
    # 1. Initialisation pygame
    pygame.init()
    
    # 2. OptionsManager en premier (charge les paramètres sauvegardés)
    OptionsManager.init()
    
    # 3. DisplayManager (crée la fenêtre selon les options)
    DisplayManager.init()
    
    # 4. AudioManager (initialise le son)
    AudioManager.init()
    
    # 5. SceneManager (charge les scènes)
    SceneManager.init()
    
    # 6. Démarrer sur la première scène
    SceneManager.change_scene("welcome")
    
    # Boucle principale...
```

---

## 📡 DisplayManager

**Responsabilités :**
- Création et gestion de la fenêtre
- Gestion du fullscreen
- Calcul du delta time
- Limitation de FPS
- Gestion de l'affichage

**Accès :**
```python
from game_libs.managers.display import DisplayManager

DisplayManager.width          # Largeur en pixels
DisplayManager.height         # Hauteur en pixels
DisplayManager.get_surface()  # Surface pour dessiner
DisplayManager.flip()         # Mettre à jour l'écran
DisplayManager.tick()         # Avancer d'une frame
DisplayManager.get_delta_time()  # Temps écoulé (secondes)
```

**Voir aussi :** [DisplayManager.md](DisplayManager.md)

---

## 🔊 AudioManager

**Responsabilités :**
- Gestion de la musique (BGM)
- Gestion des sons d'ambiance (BGS)
- Gestion des effets musicaux (ME)
- Gestion des effets sonores (SE)
- Contrôle des volumes

**Accès :**
```python
from game_libs.managers.audio import AudioManager

# Jouer de la musique
AudioManager.play_bgm("menu_theme")
AudioManager.stop_bgm()

# Jouer un effet sonore
AudioManager.play_se("explosion")

# Volumes
AudioManager.set_master_volume(0.8)
AudioManager.get_master_volume()
```

**Voir aussi :** [AudioManager.md](AudioManager.md)

---

## 🎮 EventManager

**Responsabilités :**
- Gestion des entrées clavier
- Gestion des manettes
- Détection d'états (PRESSED, HELD, RELEASED)
- Gestion des timers
- Configuration des contrôles

**Accès :**
```python
from game_libs.managers.event import EventManager, KeyState

# Obtenir les états des touches
keys = EventManager.get_keys()

# Vérifier une touche
if keys["JUMP"].is_pressed():  # Une seule fois
    player.jump()

if keys["RIGHT"].is_held():    # Continu
    player.move_right(dt)

# Timers
EventManager.set_timer("cooldown", 1.0)  # 1 seconde
if EventManager.is_timer_done("cooldown"):
    print("Cooldown terminé !")
```

**Voir aussi :** [EventManager.md](EventManager.md)

---

## ⚙️ OptionsManager

**Responsabilités :**
- Gestion des paramètres du jeu
- Sauvegarde/chargement (JSON)
- Synchronisation avec les autres managers
- Gestion des volumes
- Gestion des paramètres d'affichage

**Accès :**
```python
from game_libs.managers.options import OptionsManager

# Volumes
OptionsManager.set_master_volume(0.8)
OptionsManager.get_master_volume()

# Affichage
OptionsManager.set_fullscreen(True)
OptionsManager.get_fullscreen()

# Sauvegarde
OptionsManager.set_option("custom_setting", "value")
OptionsManager.save()  # Écrire dans cache/settings.json
```

**Voir aussi :** [OptionsManager.md](OptionsManager.md)

---

## 📡 SceneManager

**Responsabilités :**
- Gestion des scènes
- Changement de scène
- Gestion des transitions
- Cycle de vie des scènes
- Historique des scènes

**Accès :**
```python
from game_libs.managers.scene import SceneManager
from game_libs.transitions import FadeIn, FadeOut

# Changer de scène
SceneManager.change_scene("game")

# Avec transitions
SceneManager.change_scene(
    "game",
    transition_out=FadeOut(800),
    transition_in=FadeIn(800)
)

# Accès aux scènes
current = SceneManager.get_current_scene()
previous = SceneManager.get_previous_scene()
```

**Voir aussi :**
- [SceneManager.md](SceneManager.md)
- [Scenes.md](Scenes.md)
- [Transitions.md](Transitions.md)

---

## 🔗 Accès depuis une scène

Depuis n'importe quelle scène, vous avez accès aux managers :

```python
from game_libs.scenes import BaseScene

class MyScene(BaseScene):
    def my_method(self):
        # Display
        width = self.display_manager.width
        
        # Audio
        self.audio_manager.play_se("click")
        
        # Events
        keys = self.event_manager.get_keys()
        if keys["JUMP"].is_pressed():
            pass
        
        # Options
        volume = self.options_manager.master_volume
```

---

## 💡 Conseils d'utilisation

### 1. Utiliser les managers dès que possible

```python
# ❌ MAUVAIS - Code spécialisé pour chaque cas
if keyboard.is_pressed("space"):
    player.jump()

# ✅ CORRECT - Utiliser EventManager
keys = self.event_manager.get_keys()
if keys["JUMP"].is_pressed():
    player.jump()
```

### 2. Respecter l'ordre d'initialisation

```python
# ❌ MAUVAIS - Ordre incorrect
AudioManager.init()  # Pas d'options encore !
OptionsManager.init()

# ✅ CORRECT
OptionsManager.init()
DisplayManager.init()
AudioManager.init()
SceneManager.init()
```

### 3. Appeler les mises à jour

```python
# ❌ MAUVAIS - Oublier les updates
while running:
    SceneManager.render(surface)
    DisplayManager.flip()

# ✅ CORRECT
while running:
    DisplayManager.tick()
    dt = DisplayManager.get_delta_time()
    
    SceneManager.update(dt)  # Important !
    SceneManager.handle_events()
    SceneManager.render(surface)
    DisplayManager.flip()
```

### 4. Sauvegarder les options avant de quitter

```python
# ❌ MAUVAIS - Options perdues
pygame.quit()

# ✅ CORRECT
OptionsManager.save()
pygame.quit()
```

---

## 🐛 Dépannage

### "Manager non initialisé"

```
AttributeError: NoneType object has no attribute...
```

**Solutions :**
1. Vérifier que `Manager.init()` est appelé
2. Vérifier l'ordre d'initialisation
3. Vérifier que les dépendances sont initialisées

### Les paramètres ne se sauvegardent pas

**Solutions :**
1. Appeler `OptionsManager.save()` après les modifications
2. Vérifier les permissions du dossier `cache`
3. Vérifier que les paramètres sont correctement définis

### Les entrées ne fonctionnent pas

**Solutions :**
1. Appeler `EventManager.update(dt)` dans `Scene.update()`
2. Vérifier que `SceneManager.handle_events()` est appelé
3. Vérifier la configuration des touches

### Pas de son

**Solutions :**
1. Vérifier que `AudioManager.init()` est appelé
2. Vérifier que les fichiers audio existent
3. Vérifier les volumes (Master et catégories)
4. Vérifier que `AudioManager.cleanup()` est appelé dans la boucle

---

## 📚 Références complétes

| Manager | Responsabilité | Fichier |
|---------|----------------|---------|
| DisplayManager | Fenêtre et affichage | [DisplayManager.md](DisplayManager.md) |
| AudioManager | Son et musique | [AudioManager.md](AudioManager.md) |
| EventManager | Entrées et timers | [EventManager.md](EventManager.md) |
| OptionsManager | Paramètres | [OptionsManager.md](OptionsManager.md) |
| SceneManager | Scènes et transitions | [SceneManager.md](SceneManager.md) |

---

**Version** : 1.0  
**Dernière mise à jour** : 20 janvier 2026  
**Auteur** : Franck Lafiteau
