#!/bin/bash

# Script de démarrage complet pour tester l'intégration Monte Carlo

echo "🚀 Démarrage de l'intégration Monte Carlo"
echo "=========================================="
echo ""

# Vérifier Python
echo "📦 Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi
echo "✅ Python 3 : $(python3 --version)"
echo ""

# Vérifier les dépendances backend
echo "📦 Vérification des dépendances backend..."
if ! python3 -c "import fastapi, uvicorn, numpy, scipy" &> /dev/null; then
    echo "⚠️  Certaines dépendances manquent. Installation..."
    pip3 install -r requirements.txt
    echo "✅ Dépendances installées"
else
    echo "✅ Toutes les dépendances sont présentes"
fi
echo ""

# Tester les 292 tests backend
echo "🧪 Lancement des tests backend (292 tests)..."
pytest tests/ -v --tb=short
if [ $? -eq 0 ]; then
    echo "✅ Tous les tests backend passent"
else
    echo "❌ Certains tests backend échouent"
    exit 1
fi
echo ""

# Démarrer le backend
echo "🔥 Démarrage du serveur FastAPI sur http://localhost:8000"
echo "   - API disponible sur http://localhost:8000/docs"
echo "   - Health check: http://localhost:8000/api/pricing/health"
echo ""
echo "Pour tester l'API Monte Carlo :"
echo "  python3 test_montecarlo_api.py"
echo ""
echo "Pour démarrer le frontend React :"
echo "  cd frontend-react && npm run dev"
echo ""

# Démarrer uvicorn
python3 -m uvicorn backend.main:app --reload --port 8000
