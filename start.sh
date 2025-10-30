#!/bin/bash

# Script pour lancer le backend FastAPI et le frontend React

echo "🚀 Lancement du système Interest Rate Modeling"
echo "=============================================="
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "backend/main.py" ]; then
    echo "❌ Erreur: Ce script doit être lancé depuis la racine du projet"
    exit 1
fi

# Fonction pour nettoyer les processus à la fin
cleanup() {
    echo ""
    echo "🛑 Arrêt des services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Lancer le backend FastAPI
echo "📡 Lancement du backend FastAPI sur http://localhost:8000"
python -m uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "   PID du backend: $BACKEND_PID"

# Attendre que le backend soit prêt
sleep 3

# Lancer le frontend React
echo ""
echo "🎨 Lancement du frontend React sur http://localhost:3000"
cd frontend-react
npm run dev &
FRONTEND_PID=$!
echo "   PID du frontend: $FRONTEND_PID"

echo ""
echo "✅ Services lancés avec succès!"
echo ""
echo "📌 URLs disponibles:"
echo "   - Frontend React:    http://localhost:3000"
echo "   - Backend API:       http://localhost:8000"
echo "   - API Docs (Swagger): http://localhost:8000/docs"
echo "   - API Docs (ReDoc):   http://localhost:8000/redoc"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter les services"
echo ""

# Attendre que les processus se terminent
wait
