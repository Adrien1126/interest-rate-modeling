import React from 'react';

/**
 * Composant de champ de formulaire réutilisable
 */
export function FormField({ 
  label, 
  name, 
  type = 'text', 
  value, 
  onChange, 
  disabled = false,
  helpText = null,
  min = null,
  max = null,
  step = null,
  children = null
}) {
  return (
    <div>
      <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
        {label}
      </label>
      {children || (
        <input 
          type={type}
          name={name}
          value={value}
          onChange={onChange}
          disabled={disabled}
          min={min}
          max={max}
          step={step}
          style={{ 
            width: '100%', 
            padding: '8px', 
            borderRadius: '4px', 
            border: '1px solid #ccc',
            opacity: disabled ? 0.6 : 1,
            cursor: disabled ? 'not-allowed' : 'auto'
          }}
        />
      )}
      {helpText && (
        <small style={{ color: '#666', fontSize: '12px', display: 'block', marginTop: '3px' }}>
          {helpText}
        </small>
      )}
    </div>
  );
}

/**
 * Composant de sélection réutilisable
 */
export function SelectField({ 
  label, 
  name, 
  value, 
  onChange, 
  options,
  disabled = false,
  helpText = null
}) {
  return (
    <FormField 
      label={label} 
      name={name} 
      helpText={helpText}
      disabled={disabled}
    >
      <select 
        name={name}
        value={value}
        onChange={onChange}
        disabled={disabled}
        style={{ 
          width: '100%', 
          padding: '8px', 
          borderRadius: '4px', 
          border: '1px solid #ccc',
          opacity: disabled ? 0.6 : 1,
          cursor: disabled ? 'not-allowed' : 'pointer'
        }}
      >
        {options.map(opt => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </FormField>
  );
}

/**
 * Bannière de statut (info/erreur/chargement)
 */
export function StatusBanner({ status, message, onRetry = null }) {
  const configs = {
    loading: {
      bg: '#fff9c4',
      border: '#fbc02d',
      icon: '⏳',
      title: 'Calcul en cours...'
    },
    error: {
      bg: '#ffebee',
      border: '#f44336',
      icon: '❌',
      title: 'Erreur'
    },
    success: {
      bg: '#e8f5e9',
      border: '#4caf50',
      icon: '✅',
      title: 'Succès'
    },
    info: {
      bg: '#e3f2fd',
      border: '#2196f3',
      icon: '🔗',
      title: 'Information'
    }
  };

  const config = configs[status] || configs.info;

  return (
    <div style={{ 
      background: config.bg, 
      padding: '15px', 
      borderRadius: '8px',
      marginBottom: '30px',
      borderLeft: `4px solid ${config.border}`
    }}>
      <p style={{ margin: 0 }}>
        <strong>{config.icon} {config.title}:</strong> {message}
      </p>
      {onRetry && status === 'error' && (
        <button 
          onClick={onRetry}
          style={{
            marginTop: '10px',
            padding: '5px 15px',
            background: '#f44336',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Réessayer
        </button>
      )}
    </div>
  );
}

/**
 * Carte de résultat (Greeks, prix, etc.)
 */
export function ResultCard({ title, items }) {
  return (
    <div style={{ 
      background: 'white', 
      padding: '20px', 
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      <h3 style={{ marginTop: 0, color: '#1976d2' }}>{title}</h3>
      {items.map((item, idx) => (
        <div key={idx} style={{ 
          display: 'flex', 
          justifyContent: 'space-between',
          padding: '8px 0',
          borderBottom: idx < items.length - 1 ? '1px solid #eee' : 'none'
        }}>
          <span style={{ fontWeight: 'bold' }}>{item.label}:</span>
          <span style={{ 
            fontFamily: 'monospace',
            color: item.highlight ? '#2196f3' : '#333'
          }}>
            {item.value}
          </span>
        </div>
      ))}
    </div>
  );
}

/**
 * Grille de formulaire à 2 colonnes
 */
export function FormGrid({ children }) {
  return (
    <div style={{ 
      display: 'grid', 
      gridTemplateColumns: '1fr 1fr', 
      gap: '20px' 
    }}>
      {children}
    </div>
  );
}
