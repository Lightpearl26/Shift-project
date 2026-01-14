# AudioManager - Guide d'utilisation

## 📖 Description

Le **AudioManager** est responsable de la gestion complète du système audio du jeu. Il gère 4 types de sons différents :

- **BGM** (Background Music) : Musiques de fond
- **BGS** (Background Sounds) : Sons d'ambiance en boucle
- **ME** (Music Effects) : Effets musicaux courts
- **SE** (Sound Effects) : Effets sonores

## 🎯 Caractéristiques principales

- Gestion hiérarchique du volume (Master + volumes individuels)
- Chargement automatique depuis `config.AUDIO_FOLDER` (bgm/bgs/me/se)
- Fonctions `load_*` pour enregistrer dynamiquement des sons
- Support du fade-in/fade-out et des canaux simultanés
- Pause/Reprise/Arrêt global (`pause_all`, `resume_all`, `stop_all`)
- Méthode `update()` pour nettoyer les canaux terminés
- Propriété `busy()` pour savoir si un son joue

---

## 🚀 Initialisation

### init()

Initialise le système audio avec les paramètres souhaités.

```python
from game_libs.managers.audio import AudioManager

# Initialisation avec paramètres par défaut
AudioManager.init()

# Initialisation personnalisée
AudioManager.init(
    frequency=44100,  # Taux d'échantillonnage (Hz)
    size=-16,         # Taille en bits (-16 pour signed 16-bit)
    channels=2,       # Stéréo (1 = mono, 2 = stéréo)
    buffer=512        # Taille du buffer (plus petit = moins de latence)
)
```

**Note :** L'initialisation charge automatiquement tous les fichiers audio (extensions supportées : mp3, ogg, wav, flac, mod, it, xm, s3m) depuis `config.AUDIO_FOLDER` :

- `.../bgm/` pour les BGM
- `.../bgs/` pour les BGS
- `.../me/` pour les ME
- `.../se/` pour les SE

### Chargement manuel

Ajoutez ou remplacez des sons à chaud :

```python
AudioManager.load_bgm("boss", "assets/audio/bgm/boss_theme.ogg")
AudioManager.load_se("click", "assets/audio/se/ui_click.wav")
```

---

## 🔊 Gestion des Volumes

### Getters de volumes

```python
master = AudioManager.get_master_volume()  # 0.0 à 1.0
bgm = AudioManager.get_bgm_volume()
bgs = AudioManager.get_bgs_volume()
me = AudioManager.get_me_volume()
se = AudioManager.get_se_volume()
```

### Setters de volumes

```python
# Définir le volume master (affecte tous les sons)
AudioManager.set_master_volume(0.8)

# Définir les volumes individuels par catégorie
AudioManager.set_bgm_volume(1.0)
AudioManager.set_bgs_volume(0.7)
AudioManager.set_me_volume(0.9)
AudioManager.set_se_volume(0.85)
```

**Important :** Le volume final d'un son est calculé comme : `master_volume × category_volume`

---

## 🎵 Background Music (BGM)

### play_bgm()

Joue une musique de fond.

```python
# Lecture simple en boucle infinie
AudioManager.play_bgm("menu_theme")

# Avec paramètres personnalisés
AudioManager.play_bgm(
    name="battle_theme",
    loops=3,           # Nombre de répétitions (-1 = infini)
    start=5.0,        # Démarrer à 5 secondes
    fadein_ms=2000    # Fade-in de 2 secondes
)
```

### Contrôles de lecture

```python
# Mettre en pause
AudioManager.pause_bgm()

# Reprendre la lecture
AudioManager.resume_bgm()

# Arrêter
AudioManager.stop_bgm()

# Arrêter avec fade-out
AudioManager.stop_bgm(fadeout_ms=3000)  # Fade-out de 3 secondes

# Vérifier si une BGM est en cours
is_playing = AudioManager.is_bgm_playing()
```

**Exemple d'utilisation :**

```python
# Dans le menu principal
AudioManager.play_bgm("menu_theme", fadein_ms=1000)

# Transition vers le jeu
AudioManager.stop_bgm(fadeout_ms=500)
AudioManager.play_bgm("level_1", fadein_ms=1000)
```

---

## 🌊 Background Sounds (BGS)

Les BGS sont des sons d'ambiance qui peuvent se jouer en parallèle de la BGM.

### play_bgs()

```python
# Jouer un son d'ambiance
channel = AudioManager.play_bgs("rain")

# Avec fade-in
channel = AudioManager.play_bgs(
    name="wind",
    loops=-1,         # Boucle infinie
    fadein_ms=1500    # Fade-in de 1.5 secondes
)
```

### Arrêt des BGS

```python
# Arrêter un BGS spécifique
AudioManager.stop_bgs("rain")

# Avec fade-out
AudioManager.stop_bgs("wind", fadeout_ms=2000)

# Arrêter tous les BGS
AudioManager.stop_all_bgs()
AudioManager.stop_all_bgs(fadeout_ms=1000)
```

**Exemple d'utilisation :**

```python
# Entrer dans une forêt
AudioManager.play_bgs("forest_ambience", fadein_ms=2000)
AudioManager.play_bgs("birds_chirping")

# Quitter la forêt
AudioManager.stop_all_bgs(fadeout_ms=1500)
```

---

## 🎼 Music Effects (ME)

Les ME sont des effets musicaux courts (fanfares, jingles).

### play_me()

```python
# Jouer un effet musical
channel = AudioManager.play_me("victory_fanfare")

# Sans mettre en pause la BGM
channel = AudioManager.play_me(
    name="level_up",
    pause_bgm=False  # Par défaut = True
)
```

**Comportement par défaut :** Si `pause_bgm=True`, la BGM est mise en pause pendant le ME **mais ne reprend pas automatiquement**. Reprenez-la explicitement si besoin : `AudioManager.resume_bgm()` ou `AudioManager.resume_all()`.

### Arrêt des ME

```python
# Arrêter un ME spécifique
AudioManager.stop_me("victory_fanfare")

# Arrêter tous les ME
AudioManager.stop_all_me()
```

**Exemple d'utilisation :**

```python
# Game Over
AudioManager.play_me("game_over")  # BGM en pause automatiquement

# Victoire
AudioManager.play_me("victory_fanfare")
```

---

## 💥 Sound Effects (SE)

Les SE sont des effets sonores courts (bruits de pas, coups, etc.).

### play_se()

```python
# Jouer un effet sonore
channel = AudioManager.play_se("jump")

# Avec modificateur de volume
channel = AudioManager.play_se(
    name="explosion",
    volume_modifier=1.5  # 150% du volume normal (plafonné à 1.0)
)

# Son plus faible
channel = AudioManager.play_se(
    name="footstep",
    volume_modifier=0.5  # 50% du volume normal
)
```

### Arrêt des SE

```python
# Arrêter un SE spécifique
AudioManager.stop_se("explosion")

# Arrêter tous les SE
AudioManager.stop_all_se()
```

**Exemple d'utilisation :**

```python
# Dans la boucle de jeu
def on_player_jump():
    AudioManager.play_se("jump")

def on_enemy_hit():
    AudioManager.play_se("hit", volume_modifier=0.8)

def on_explosion():
    AudioManager.play_se("explosion")
```

---

## 🧹 Utilitaires

### Pause / reprise / arrêt global

```python
AudioManager.pause_all()          # Pause BGM + tous les canaux
AudioManager.resume_all()         # Reprise globale
AudioManager.stop_all()           # Stop global (option fadeout_ms)
AudioManager.busy()               # True si quelque chose joue
```

### Nettoyage des canaux

```python
# Nettoyer automatiquement les canaux terminés
AudioManager.update()
```

**Conseil :** Appelez `AudioManager.update()` dans votre boucle principale (ou à intervalle régulier) pour libérer les canaux terminés.

---

## 📋 Exemple complet

```python
from game_libs.managers.audio import AudioManager

# Initialisation au démarrage du jeu
AudioManager.init()

# Configuration des volumes
AudioManager.set_master_volume(0.8)
AudioManager.set_bgm_volume(0.9)
AudioManager.set_se_volume(1.0)

# Menu principal
AudioManager.play_bgm("main_menu", fadein_ms=2000)

# Clic sur le bouton "Jouer"
def on_play_button_click():
    AudioManager.play_se("button_click")
    AudioManager.stop_bgm(fadeout_ms=500)
    # Chargement du niveau...
    AudioManager.play_bgm("level_1_music", fadein_ms=1000)
    AudioManager.play_bgs("forest_ambience")

# En jeu
def on_player_action():
    AudioManager.play_se("jump")
    
def on_level_complete():
    AudioManager.stop_all_bgs(fadeout_ms=1000)
    AudioManager.play_me("victory")  # BGM mise en pause auto (ne reprend pas seule)
    AudioManager.resume_bgm()        # Reprise manuelle si nécessaire

# Nettoyage en fin de jeu
AudioManager.stop_all(fadeout_ms=2000)
```

---

## ⚠️ Notes importantes

1. **Noms de fichiers** : Les noms utilisés dans les méthodes correspondent aux noms de fichiers sans extension
   - Fichier : `assets/audio/bgm/menu_theme.ogg`
   - Utilisation : `AudioManager.play_bgm("menu_theme")`

2. **Formats supportés** : Le manager supporte les formats audio compatibles avec Pygame (MP3, OGG, WAV, FLAC, MOD, IT, XM, S3M)

3. **Limitations de canaux** : Par défaut, 32 canaux simultanés sont disponibles pour les sons (BGS, ME, SE)

4. **BGM vs BGS** : Une seule BGM peut jouer à la fois, mais plusieurs BGS peuvent être actifs simultanément

5. **ME & BGM** : `play_me(pause_bgm=True)` met la BGM en pause mais ne la reprend pas. Reprenez-la explicitement (`resume_bgm` ou `resume_all`).

6. **Nettoyage** : Appelez `AudioManager.update()` régulièrement pour libérer les canaux terminés.

---

## 🔧 Débogage

Le AudioManager utilise le système de logging du jeu. Activez les logs de debug pour voir les détails :

```python
from game_libs import config

config.LOG_DEBUG = True
```

Vous verrez alors des messages comme :

```text
[AudioManager] Playing BGM: menu_theme
[AudioManager] SE stopped: explosion
[AudioManager] Cleaned up finished channels
```
