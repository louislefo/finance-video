# 📈 Finance Video - DCA Investment Simulator

Générateur de vidéos animées pour visualiser l'évolution d'un portefeuille avec la stratégie **DCA (Dollar Cost Averaging)**.

## 🎬 Démonstration

![Simulation DCA S&P 500](video/demo.gif)

> *Animation montrant l'évolution d'un investissement de 100$/mois sur le S&P 500 depuis 2000*

---

## 🎯 À quoi sert ce projet ?

Ce projet permet de :

1. **Simuler un investissement régulier (DCA)** sur n'importe quel actif financier
2. **Visualiser l'évolution** du capital investi vs la valeur du portefeuille
3. **Générer des vidéos animées** au format 9:16 (idéal pour les Reels/TikTok/Shorts)
4. **Inclure les dividendes** dans le calcul avec réinvestissement automatique

---

## 💡 Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 📊 **Simulation DCA** | Investissement mensuel automatisé |
| 💰 **Réinvestissement des dividendes** | Les dividendes sont automatiquement réinvestis |
| 📈 **Animation dynamique** | Axes qui s'adaptent en temps réel |
| 🎨 **Thème moderne** | Design sombre avec couleurs néon |
| 📱 **Format vertical** | Ratio 9:16 pour les réseaux sociaux |

---

## 🚀 Installation

### Prérequis

- Python 3.8+
- FFmpeg (pour la génération vidéo)

### Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Installer les dépendances
pip install yfinance pandas matplotlib seaborn tqdm
```

### Installation de FFmpeg

**Windows** (avec Chocolatey) :
```bash
choco install ffmpeg
```

**Windows** (manuel) :
1. Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html)
2. Ajouter le dossier `bin` au PATH

---

## 📖 Utilisation

### Configuration de base (`dca_simulator.py`)

Modifiez les paramètres en haut du fichier :

```python
# --- 1. SIMULATION PARAMETERS ---
TICKER = "^GSPC"              # Symbole Yahoo Finance (S&P 500)
Name = "sp500"                # Nom personnalisé

# Simulation Period
START_DATE = "2000-01-01"     # Date de début
END_DATE = "2024-12-31"       # Date de fin (ou aujourd'hui par défaut)

# Monthly Investment Amount (in Dollars)
INVESTISSEMENT_MENSUEL = 100  # Montant investi chaque mois

# Video Parameters
FPS = 10                      # Images par seconde
DPI = 120                     # Qualité de l'image
```

### Exemples de tickers populaires

| Ticker | Description |
|--------|-------------|
| `^GSPC` | S&P 500 |
| `^FCHI` | CAC 40 |
| `AAPL` | Apple |
| `MSFT` | Microsoft |
| `BTC-USD` | Bitcoin |
| `GC=F` | Or (Gold Futures) |

### Exécution

```bash
python dca_simulator.py
```

La vidéo sera générée dans le dossier `video/` sous le nom `evolution_capital_{ASSET_NAME}.mp4`.

---

## 📁 Structure du projet

```
finance-video/
├── dca_simulator.py        # Version complète avec dividendes
├── dca_simulator_basic.py  # Version basique (sans dividendes)
├── video/                  # Dossier des vidéos générées
│   ├── demo.gif
│   ├── evolution_capital_S&P 500.mp4
│   └── ...
└── README.md
```

---

## 📊 Comprendre la vidéo générée

La vidéo affiche :

- 🟢 **Ligne verte** : Valeur du portefeuille (valeur marchande)
- 🔵 **Ligne bleue** : Capital investi (argent de poche)
- 🟣 **Ligne magenta** : Dividendes cumulés (si applicable)

### Indicateurs affichés

- **Date** : Date actuelle de la simulation
- **Gain** : Plus-value (Portefeuille - Capital investi)
- **Dividends** : Total des dividendes réinvestis
- **ROI** : Retour sur investissement en pourcentage

---

## 🎨 Personnalisation du thème

Les couleurs peuvent être modifiées dans `dca_simulator.py` :

```python
# Colors
COLOR_BG = '#0A0A0A'         # Background (noir)
COLOR_GRID = '#2E2E2E'       # Grille
COLOR_TEXT = '#F0F0F0'       # Texte
COLOR_PORTFOLIO = '#00FFC0'  # Courbe portefeuille (vert néon)
COLOR_INVESTED = '#00CFFF'   # Courbe capital (bleu néon)
COLOR_DIVIDENDS = '#FF00FF'  # Courbe dividendes (magenta)
```

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. 🍴 Fork le projet
2. 🌿 Créer une branche (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. 📤 Push vers la branche (`git push origin feature/AmazingFeature`)
5. 🔃 Ouvrir une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## ⚠️ Avertissement

Ce projet est à but **éducatif uniquement**. Les performances passées ne préjugent pas des performances futures. Ne prenez pas de décisions d'investissement basées uniquement sur ces simulations.