# 📚 Tutoriels Shift Project

Bienvenue dans la documentation complète du **Shift Project** ! Ce dossier contient des guides détaillés pour tous les systèmes du jeu.

## 🗺️ Plan de navigation

```
Shift Project
├── 🔧 Système de Scènes & Transitions
│   ├── 📡 SceneManager (gestion des scènes)
│   ├── 📖 Scenes (architecture et création)
│   └── 🎬 Transitions (effets et création)
├── 🔊 Managers spécialisés
│   ├── 📚 Managers (vue d'ensemble)
│   ├── 🔊 AudioManager
│   ├── 🖥️  DisplayManager
│   ├── 🎮 EventManager
│   └── ⚙️  OptionsManager
```

---

## 📚 Tutoriels - Système de scènes & transitions

### [SceneManager.md](SceneManager.md) - 📡 Gestionnaire de scènes

Gestion centralisée de toutes les scènes et transitions du jeu.

**Quand l'utiliser :**
- Changer de scène (menu → jeu → options)
- Ajouter des transitions visuelles
- Accéder à la scène actuelle
- Revenir à la scène précédente

**Liens connexes :**
- [📖 Tutoriel des scènes](Scenes.md) - Architecture et création
- [🎬 Tutoriel des transitions](Transitions.md) - Effets et création

---

### [Scenes.md](Scenes.md) - 📖 Système de scènes

Guide complet sur le système de scènes : architecture, scènes existantes, et comment créer une nouvelle scène.

**Sections :**
- 📖 **Scènes existantes** : Welcome, MainMenu
- ✨ **Créer une nouvelle scène** : protocole et checklist complète
- 🔗 **Intégration** : comment enregistrer votre scène
- 💡 **Exemples complets** de scènes personnalisées

**Liens connexes :**
- [SceneManager.md](SceneManager.md) - Gestion des changements de scène
- [Transitions.md](Transitions.md) - Transitions lors des changements
- [EventManager.md](EventManager.md) - Gestion des entrées utilisateur

---

### [Transitions.md](Transitions.md) - 🎬 Système de transitions

Guide complet sur les effets de transition : types existants, fonctions d'easing, et comment créer une transition personnalisée.

**Sections :**
- 🎬 **Transitions existantes** : Fade, Particules, Vidéo
- ✨ **Créer une transition personnalisée** : protocole et templates
- ⏱️ **Fonctions d'easing** : liste complète et exemples
- 💡 **Exemples complets** de transitions personnalisées

**Liens connexes :**
- [SceneManager.md](SceneManager.md) - Intégration avec les changements de scène
- [Scenes.md](Scenes.md) - Transitions entre scènes

---

## 📚 Tutoriels - Managers spécialisés

### � [Managers.md](Managers.md)

Vue d'ensemble du système de managers et guide rapide d'utilisation.

**Contient :**
- Architecture générale des managers
- Ordre d'initialisation
- Vue générale de chaque manager
- Conseils d'utilisation
- Dépannage des managers

**Liens connexes :**
- [AudioManager.md](AudioManager.md) - Détails sur la gestion audio
- [DisplayManager.md](DisplayManager.md) - Détails sur l'affichage
- [EventManager.md](EventManager.md) - Détails sur les entrées
- [OptionsManager.md](OptionsManager.md) - Détails sur les paramètres

---

### �🔊 [AudioManager](AudioManager.md)

Gestion complète du système audio du jeu.

**Fonctionnalités :**
- 4 types de sons : BGM, BGS, ME, SE
- Gestion hiérarchique des volumes
- Support fade-in/fade-out
- Gestion multi-canaux
- Chargement automatique des assets

---

### 🖥️ [DisplayManager](DisplayManager.md)

Gestion de la fenêtre et de l'affichage du jeu.

**Fonctionnalités :**
- Création et gestion de la fenêtre
- Mode plein écran
- VSync et limitation de FPS
- Calcul du delta time
- Captures d'écran

---

### 🎮 [EventManager](EventManager.md)

Gestion des entrées utilisateur et du système de timers.

**Fonctionnalités :**
- Mapping configurable des touches
- Support des manettes
- Détection d'états (PRESSED, HELD, RELEASED)
- Système de timers
- Support multi-plateforme

---

### ⚙️ [OptionsManager](OptionsManager.md)

Gestion centralisée des paramètres et options du jeu.

**Fonctionnalités :**
- Sauvegarde/chargement (JSON)
- Gestion des volumes
- Paramètres d'affichage
- Configuration des touches
- Synchronisation avec les autres managers

---

## 🎯 Guides rapides

### Je veux...

**...comprendre l'architecture générale des managers**
→ Allez à [Managers.md](Managers.md) section *"🏗️ Architecture des Managers"*

**...créer une nouvelle scène**
→ Allez à [Scenes.md](Scenes.md) section *"✨ Créer une nouvelle scène"*

**...créer un effet de transition personnalisé**
→ Allez à [Transitions.md](Transitions.md) section *"✨ Créer une transition personnalisée"*

**...changer de scène avec une transition**
→ Allez à [SceneManager.md](SceneManager.md) section *"🔄 Changer de scène"*

**...configurer les contrôles du joueur**
→ Allez à [EventManager.md](EventManager.md)

**...gérer la musique et les sons**
→ Allez à [AudioManager.md](AudioManager.md)

**...ajuster l'affichage (fenêtre, FPS)**
→ Allez à [DisplayManager.md](DisplayManager.md)

**...créer un menu d'options**
→ Allez à [OptionsManager.md](OptionsManager.md)

---

## 📖 Ordre de lecture recommandé

### Pour débuter
1. [SceneManager.md](SceneManager.md) - Comprendre le système de base
2. [Scenes.md](Scenes.md) - Architecture et scènes existantes
3. [Transitions.md](Transitions.md) - Ajouter des effets visuels

### Pour les managers
4. [EventManager.md](EventManager.md) - Gestion des entrées
5. [DisplayManager.md](DisplayManager.md) - Gestion de l'affichage
6. [AudioManager.md](AudioManager.md) - Gestion du son
7. [OptionsManager.md](OptionsManager.md) - Gestion des paramètres

---

## 🔗 Références croisées

### Par concept

**Gestion du cycle de vie :**
- [Scenes.md](Scenes.md) - Cycle de vie des scènes (init, enter, exit, update, render)
- [SceneManager.md](SceneManager.md) - Gestion des états de transition

**Interactions utilisateur :**
- [EventManager.md](EventManager.md) - Capturer les entrées
- [Scenes.md](Scenes.md) - `handle_events()` dans les scènes

**Transitions visuelles :**
- [Transitions.md](Transitions.md) - Tous les types de transitions
- [SceneManager.md](SceneManager.md) - Intégration des transitions
- [Scenes.md](Scenes.md) - Transitions lors des changements

**Audio :**
- [AudioManager.md](AudioManager.md) - Gestion du son
- [OptionsManager.md](OptionsManager.md) - Gestion des volumes
- [Scenes.md](Scenes.md) - `on_enter()`/`on_exit()` pour la musique

**Paramètres du jeu :**
- [OptionsManager.md](OptionsManager.md) - Sauvegarde/chargement
- [DisplayManager.md](DisplayManager.md) - Paramètres d'affichage
- [AudioManager.md](AudioManager.md) - Paramètres audio

---

## 🚀 Initialisation rapide

```python
# import built-in modules
import pygame
from game_libs.managers.audio import AudioManager
from game_libs.managers.scene import SceneManager
from game_libs.managers.display import DisplayManager
from game_libs.managers.options import OptionsManager

def main():
    """Main function to run the game."""
    # Initialize pygame
    pygame.init()

    # Initialize managers (dans cet ordre!)
    OptionsManager.init()
    DisplayManager.init()
    AudioManager.init()
    SceneManager.init()

    # Load the first scene
    SceneManager.change_scene("Welcome")

    # Main game loop
    running = True
    while running:
        # Tick and get delta time
        DisplayManager.tick()
        dt = DisplayManager.get_delta_time()

        # Check for QUIT event
        if pygame.event.peek(pygame.QUIT):
            running = False

        # Update managers
        AudioManager.cleanup()
        SceneManager.update(dt)

        # Handle events
        SceneManager.handle_events()

        # Render
        SceneManager.render(DisplayManager.get_surface())

        # Update display
        DisplayManager.flip()

    # Exit
    DisplayManager.shutdown()
    OptionsManager.save()
    pygame.quit()

if __name__ == "__main__":
    main()
```

Pour plus de détails, consultez [SceneManager.md](SceneManager.md) section *"🚀 Initialisation"*.

---

## 💡 Conseils

- 📖 Lisez les sections "Description" en premier pour une vue d'ensemble
- 💻 Testez les exemples de code au fur et à mesure
- 🔍 Utilisez les liens pour naviguer entre concepts liés
- ⚠️ Consultez "🐛 Dépannage" en cas de problème

---

## 🐛 Problèmes courants

**La scène ne change pas**
→ Voir [SceneManager.md](SceneManager.md#🐛-dépannage)

**La transition ne s'affiche pas**
→ Voir [Transitions.md](Transitions.md#🐛-dépannage)

**Les touches ne répondent pas**
→ Voir [EventManager.md](EventManager.md#🐛-dépannage)

**Pas de son**
→ Voir [AudioManager.md](AudioManager.md#🐛-dépannage)

**Fenêtre ne s'affiche pas**
→ Voir [DisplayManager.md](DisplayManager.md#🐛-dépannage)

---

## 📝 Conventions

- `CamelCase` : Classes, méthodes
- `snake_case` : Variables, fonctions
- `UPPERCASE` : Constantes
- `"quoted"` : Noms de scènes, fichiers
- [Lien](file.md) : Références vers autres tutoriels

---

## 📞 Support

Pour toute question ou problème :

1. Consultez d'abord les tutoriels détaillés
2. Vérifiez les exemples de code fournis
3. Activez les logs en mode DEBUG (voir [SceneManager.md](SceneManager.md#🐛-dépannage))

---

## 📄 Licence

© Lafiteau Franck - Shift Project

---

**Version** : 2.0  
**Dernière mise à jour** : 20 janvier 2026  
**Auteur** : Franck Lafiteau

### Bon développement ! 🚀
