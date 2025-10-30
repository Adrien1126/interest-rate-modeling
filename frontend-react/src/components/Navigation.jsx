import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation() {
  const location = useLocation();
  
  const navStyle = {
    background: '#1976d2',
    padding: '15px 0',
    marginBottom: '0'
  };

  const containerStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const logoStyle = {
    color: 'white',
    fontSize: '24px',
    fontWeight: 'bold',
    textDecoration: 'none'
  };

  const navLinksStyle = {
    display: 'flex',
    gap: '20px',
    listStyle: 'none',
    margin: 0,
    padding: 0
  };

  const getLinkStyle = (path) => ({
    color: 'white',
    textDecoration: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    fontWeight: location.pathname === path ? 'bold' : 'normal',
    background: location.pathname === path ? 'rgba(255,255,255,0.2)' : 'transparent',
    transition: 'background 0.3s'
  });

  return (
    <nav style={navStyle}>
      <div style={containerStyle}>
        <Link to="/" style={logoStyle}>
          📊 Quant Platform
        </Link>
        
        <ul style={navLinksStyle}>
          <li>
            <Link to="/" style={getLinkStyle('/')}>
              Accueil
            </Link>
          </li>
          <li>
            <Link to="/pricing" style={getLinkStyle('/pricing')}>
              Pricing
            </Link>
          </li>
          <li>
            <Link to="/profile" style={getLinkStyle('/profile')}>
              Profil
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navigation;
