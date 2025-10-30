import React from 'react';

function Profile() {
  return (
    <div style={{ padding: '40px', maxWidth: '900px', margin: '0 auto' }}>
      <h1>👤 Profil</h1>
      
      <div style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '40px',
        borderRadius: '12px',
        color: 'white',
        marginBottom: '30px'
      }}>
        <h2 style={{ margin: '0 0 10px 0' }}>Adrien</h2>
        <p style={{ margin: '0', fontSize: '18px', opacity: 0.9 }}>
          Ingénieur Quantitatif & Développeur
        </p>
      </div>

      <div style={{ 
        background: '#f5f5f5', 
        padding: '30px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3>🎓 Formation</h3>
        <ul style={{ lineHeight: '1.8' }}>
          <li><strong>Master en Finance Quantitative</strong></li>
          <li>Spécialisation en modélisation des taux d'intérêt</li>
          <li>Modèles stochastiques et produits dérivés</li>
        </ul>
      </div>

      <div style={{ 
        background: '#f5f5f5', 
        padding: '30px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3>💼 Compétences</h3>
        
        <div style={{ marginBottom: '20px' }}>
          <h4>Modélisation Quantitative</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {['Black-Scholes', 'Heston', 'SABR', 'Hull-White', 'CIR', 'LMM'].map(skill => (
              <span key={skill} style={{
                background: '#2196f3',
                color: 'white',
                padding: '5px 15px',
                borderRadius: '20px',
                fontSize: '14px'
              }}>
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <h4>Développement</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {['Python', 'NumPy', 'SciPy', 'FastAPI', 'React', 'JavaScript'].map(skill => (
              <span key={skill} style={{
                background: '#4caf50',
                color: 'white',
                padding: '5px 15px',
                borderRadius: '20px',
                fontSize: '14px'
              }}>
                {skill}
              </span>
            ))}
          </div>
        </div>

        <div>
          <h4>Finance</h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {['Produits dérivés', 'Calibration', 'Risk Management', 'Monte Carlo'].map(skill => (
              <span key={skill} style={{
                background: '#ff9800',
                color: 'white',
                padding: '5px 15px',
                borderRadius: '20px',
                fontSize: '14px'
              }}>
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div style={{ 
        background: '#f5f5f5', 
        padding: '30px', 
        borderRadius: '8px',
        marginBottom: '20px'
      }}>
        <h3>📚 Projet Actuel</h3>
        <p>
          Cette plateforme pédagogique vise à implémenter les concepts avancés 
          de pricing quantitatif présentés dans le livre de référence 
          <strong> "Interest Rate Modeling" d'Andersen & Piterbarg</strong>.
        </p>
        <p>
          L'objectif est de créer un outil éducatif complet permettant de :
        </p>
        <ul>
          <li>Pricer des produits dérivés avec différents modèles</li>
          <li>Calibrer les modèles sur des données réelles</li>
          <li>Visualiser les surfaces de volatilité et courbes de taux</li>
          <li>Calculer les sensibilités (Greeks) en temps réel</li>
        </ul>
      </div>

      <div style={{ 
        background: '#e3f2fd', 
        padding: '20px', 
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <h3>🔗 Contact</h3>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '15px' }}>
          <a 
            href="https://github.com/Adrien1126" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              padding: '10px 20px',
              background: '#333',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: 'bold'
            }}
          >
            GitHub
          </a>
          <a 
            href="https://linkedin.com" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              padding: '10px 20px',
              background: '#0077b5',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: 'bold'
            }}
          >
            LinkedIn
          </a>
          <a 
            href="mailto:votre.email@example.com"
            style={{
              padding: '10px 20px',
              background: '#d93025',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: 'bold'
            }}
          >
            Email
          </a>
        </div>
      </div>
    </div>
  );
}

export default Profile;
