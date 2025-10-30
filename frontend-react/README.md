# Frontend React - Quant Platform

Interface utilisateur moderne pour la plateforme de pricing quantitatif.

## 🚀 Démarrage rapide

### Installation des dépendances

```bash
npm install
```

### Lancement en mode développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:3000`

### Build pour production

```bash
npm run build
```

Les fichiers optimisés seront dans le dossier `dist/`.

## 📁 Structure du projet

```
src/
├── api/                    # Services API
│   ├── pricingAPI.js
│   ├── marketAPI.js
│   └── calibrationAPI.js
├── components/             # Composants réutilisables
│   ├── Layout/
│   │   ├── Header.jsx
│   │   └── Footer.jsx
│   ├── PricingForm.jsx
│   └── GreeksChart.jsx
├── pages/                  # Pages de l'application
│   ├── Home.jsx
│   ├── PricingPage.jsx
│   ├── CalibrationPage.jsx
│   ├── MarketPage.jsx
│   └── About.jsx
├── styles/                 # Styles globaux
│   ├── global.css
│   └── theme.js
├── App.jsx                 # Composant racine
└── index.jsx              # Point d'entrée
```

## 🛠️ Technologies

- **React 18** - Framework JavaScript
- **Material-UI (MUI)** - Composants UI
- **React Router** - Navigation
- **Axios** - Requêtes HTTP
- **Recharts** - Graphiques
- **Vite** - Build tool

## 🔌 Configuration API

Par défaut, l'API backend est accessible sur `http://localhost:8000`.

Pour changer l'URL, créez un fichier `.env` :

```env
VITE_API_URL=http://your-api-url:8000
```

## 📝 Scripts disponibles

- `npm run dev` - Lance le serveur de développement
- `npm run build` - Build pour production
- `npm run preview` - Prévisualise le build de production
- `npm run lint` - Vérifie le code avec ESLint

## 🎨 Personnalisation du thème

Le thème Material-UI est configurable dans `src/styles/theme.js`.

## 📦 Dépendances principales

```json
{
  "react": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "@mui/material": "^5.14.20",
  "axios": "^1.6.2",
  "recharts": "^2.10.3"
}
```
