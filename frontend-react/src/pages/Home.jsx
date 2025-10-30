import React from 'react';

function Home() {
  return (
    <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>🎓 Plateforme de Pricing Quantitatif</h1>
      
      <div style={{ 
        background: '#f5f5f5', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '30px' 
      }}>
        <h2>Bienvenue sur cette plateforme pédagogique</h2>
        <p>
          Ce projet est une plateforme éducative dédiée au pricing quantitatif 
          des produits dérivés de taux d'intérêt, inspirée des travaux de 
          <strong> Andersen & Piterbarg</strong>.
        </p>
      </div>

      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
        marginTop: '40px'
      }}>
        <div style={{ 
          background: '#e3f2fd', 
          padding: '20px', 
          borderRadius: '8px',
          border: '2px solid #2196f3'
        }}>
          <h3>📊 Pricing</h3>
          <p>
            Calculez le prix d'options et produits dérivés avec différents modèles :
            Black-Scholes, Heston, SABR, Hull-White, CIR.
          </p>
        </div>

        <div style={{ 
          background: '#f3e5f5', 
          padding: '20px', 
          borderRadius: '8px',
          border: '2px solid #9c27b0'
        }}>
          <h3>📈 Calibration</h3>
          <p>
            Calibrez les paramètres des modèles sur des données de marché réelles.
          </p>
        </div>

        <div style={{ 
          background: '#e8f5e9', 
          padding: '20px', 
          borderRadius: '8px',
          border: '2px solid #4caf50'
        }}>
          <h3>💹 Marché</h3>
          <p>
            Accédez aux courbes de taux, surfaces de volatilité et données de marché.
          </p>
        </div>
      </div>

      <div style={{ marginTop: '40px', padding: '20px', background: '#fff3e0', borderRadius: '8px' }}>
        <h3>🎯 Technologies utilisées</h3>
        <ul>
          <li><strong>Backend :</strong> Python, FastAPI, NumPy, SciPy</li>
          <li><strong>Frontend :</strong> React, JavaScript</li>
          <li><strong>Modèles :</strong> Black-Scholes, Heston, SABR, Hull-White, CIR, LMM</li>
        </ul>
      </div>
    </div>
  );
}

export default Home;
