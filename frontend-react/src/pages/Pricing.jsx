import { useState } from 'react';
import '../styles/pricing.css';

export default function Pricing() {
  const today = new Date().toISOString().split('T')[0];
  const oneYearFromNow = new Date();
  oneYearFromNow.setFullYear(oneYearFromNow.getFullYear() + 1);
  const defaultExpiration = oneYearFromNow.toISOString().split('T')[0];

  const [formData, setFormData] = useState({
    productType: 'option',
    pricingMethod: 'analytic',
    model: 'black-scholes',
    spot: 100,
    strike: 100,
    tradeDate: today,
    expirationDate: defaultExpiration,
    dayCountConvention: 'ACT/365',
    businessDayConvention: 'ModifiedFollowing',
    calendar: 'TARGET',
    volatility: 0.2,
    rate: 0.05,
    dividendYield: 0.0,
    optionType: 'call',
    nSimulations: 50000,
    nSteps: 100,
    useAntithetic: true,
    randomSeed: 42,
    computeConfidenceInterval: true,
    confidenceLevel: 0.95
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        product_type: formData.productType,
        product_params: {
          option_type: formData.optionType,
          strike: parseFloat(formData.strike),
          trade_date: formData.tradeDate,
          expiration_date: formData.expirationDate,
          day_count_convention: formData.dayCountConvention,
          business_day_convention: formData.businessDayConvention,
          calendar: formData.calendar
        },
        pricing_method: formData.pricingMethod,
        pricing_params: formData.pricingMethod === 'montecarlo' ? {
          n_simulations: parseInt(formData.nSimulations),
          n_steps: parseInt(formData.nSteps),
          use_antithetic: formData.useAntithetic,
          random_seed: parseInt(formData.randomSeed),
          compute_confidence_interval: formData.computeConfidenceInterval,
          confidence_level: parseFloat(formData.confidenceLevel)
        } : {},
        market_data: {
          spot: parseFloat(formData.spot),
          rate: parseFloat(formData.rate),
          dividend_yield: parseFloat(formData.dividendYield),
          volatility: parseFloat(formData.volatility)
        },
        model: formData.model
      };

      const response = await fetch('http://localhost:8000/api/pricing/price', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pricing-container">
      <div className="pricing-wrapper">
        <header className="pricing-header">
          <h1 className="pricing-title">Pricing de Produits Dérivés</h1>
          <p className="pricing-subtitle">Valorisation quantitative avec modèles stochastiques</p>
        </header>

        <div className="status-bar">
          <div className={`status-indicator ${loading ? 'loading' : error ? 'error' : result ? 'success' : ''}`}></div>
          <span>{loading ? 'Calcul en cours...' : error ? 'Erreur' : result ? 'Calcul terminé' : 'Prêt'}</span>
        </div>

        <form onSubmit={handleSubmit} className="pricing-form">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Type de Produit</label>
              <select
                name="productType"
                value={formData.productType}
                onChange={handleChange}
                className="form-select"
              >
                <option value="option">Option Européenne</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Méthode de Pricing</label>
              <select
                name="pricingMethod"
                value={formData.pricingMethod}
                onChange={handleChange}
                className="form-select"
              >
                <option value="analytic">Analytique</option>
                <option value="montecarlo">Monte Carlo</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Modèle</label>
              <select
                name="model"
                value={formData.model}
                onChange={handleChange}
                className="form-select"
              >
                <option value="black-scholes">Black-Scholes</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Type d'Option</label>
              <select
                name="optionType"
                value={formData.optionType}
                onChange={handleChange}
                className="form-select"
              >
                <option value="call">Call</option>
                <option value="put">Put</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Spot (S₀)</label>
              <input
                type="number"
                name="spot"
                value={formData.spot}
                onChange={handleChange}
                step="0.01"
                className="form-input"
              />
              <span className="form-help">Prix actuel du sous-jacent</span>
            </div>

            <div className="form-group">
              <label className="form-label">Strike (K)</label>
              <input
                type="number"
                name="strike"
                value={formData.strike}
                onChange={handleChange}
                step="0.01"
                className="form-input"
              />
              <span className="form-help">Prix d'exercice</span>
            </div>

            <div className="form-group">
              <label className="form-label">Volatilité (σ)</label>
              <input
                type="number"
                name="volatility"
                value={formData.volatility}
                onChange={handleChange}
                step="0.001"
                min="0.001"
                className="form-input"
              />
              <span className="form-help">Volatilité annualisée (0.2 = 20%)</span>
            </div>

            <div className="form-group">
              <label className="form-label">Taux sans Risque (r)</label>
              <input
                type="number"
                name="rate"
                value={formData.rate}
                onChange={handleChange}
                step="0.001"
                className="form-input"
              />
              <span className="form-help">Taux annuel (0.05 = 5%)</span>
            </div>

            <div className="form-group">
              <label className="form-label">Dividend Yield (q)</label>
              <input
                type="number"
                name="dividendYield"
                value={formData.dividendYield}
                onChange={handleChange}
                step="0.001"
                className="form-input"
              />
              <span className="form-help">Rendement dividende annuel</span>
            </div>

            <div className="form-group">
              <label className="form-label">Date de Trade</label>
              <input
                type="date"
                name="tradeDate"
                value={formData.tradeDate}
                onChange={handleChange}
                className="form-input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Date d'Expiration</label>
              <input
                type="date"
                name="expirationDate"
                value={formData.expirationDate}
                onChange={handleChange}
                className="form-input"
              />
            </div>
          </div>

          {formData.pricingMethod === 'montecarlo' && (
            <div className="form-section monte-carlo">
              <h3 className="section-title">Paramètres Monte Carlo</h3>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Nombre de Simulations</label>
                  <input
                    type="number"
                    name="nSimulations"
                    value={formData.nSimulations}
                    onChange={handleChange}
                    min="1"
                    step="1"
                    className="form-input"
                  />
                  <span className="form-help">Recommandé: 10,000 - 100,000. Plus élevé = plus précis mais plus lent</span>
                </div>

                <div className="form-group">
                  <label className="form-label">Nombre de Pas de Temps</label>
                  <input
                    type="number"
                    name="nSteps"
                    value={formData.nSteps}
                    onChange={handleChange}
                    min="1"
                    step="1"
                    className="form-input"
                  />
                  <span className="form-help">Recommandé: 50 - 250. Plus élevé = plus de précision dans la discrétisation</span>
                </div>

                <div className="form-group">
                  <label className="form-label">Random Seed</label>
                  <input
                    type="number"
                    name="randomSeed"
                    value={formData.randomSeed}
                    onChange={handleChange}
                    className="form-input"
                  />
                  <span className="form-help">Pour reproductibilité (0 = aléatoire)</span>
                </div>

                <div className="form-group">
                  <label className="form-label">Niveau de Confiance</label>
                  <input
                    type="number"
                    name="confidenceLevel"
                    value={formData.confidenceLevel}
                    onChange={handleChange}
                    min="0.01"
                    max="0.9999"
                    step="0.01"
                    className="form-input"
                    disabled={!formData.computeConfidenceInterval}
                  />
                  <span className="form-help">Typique: 0.90, 0.95, 0.99 (intervalle de confiance)</span>
                </div>
              </div>

              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="useAntithetic"
                  checked={formData.useAntithetic}
                  onChange={handleChange}
                  className="checkbox-input"
                  id="useAntithetic"
                />
                <label htmlFor="useAntithetic">Variables antithétiques (réduction de variance)</label>
              </div>

              <div className="checkbox-group">
                <input
                  type="checkbox"
                  name="computeConfidenceInterval"
                  checked={formData.computeConfidenceInterval}
                  onChange={handleChange}
                  className="checkbox-input"
                  id="computeConfidenceInterval"
                />
                <label htmlFor="computeConfidenceInterval">Calculer l'intervalle de confiance</label>
              </div>
            </div>
          )}

          <div className="form-section conventions">
            <h3 className="section-title">Conventions de Marché</h3>
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">Day Count Convention</label>
                <select
                  name="dayCountConvention"
                  value={formData.dayCountConvention}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="ACT/365">ACT/365</option>
                  <option value="ACT/360">ACT/360</option>
                  <option value="30/360">30/360</option>
                  <option value="ACT/ACT">ACT/ACT</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Business Day Convention</label>
                <select
                  name="businessDayConvention"
                  value={formData.businessDayConvention}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="ModifiedFollowing">Modified Following</option>
                  <option value="Following">Following</option>
                  <option value="Preceding">Preceding</option>
                  <option value="Unadjusted">Unadjusted</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Calendrier</label>
                <select
                  name="calendar"
                  value={formData.calendar}
                  onChange={handleChange}
                  className="form-select"
                >
                  <option value="TARGET">TARGET (Zone Euro)</option>
                  <option value="UnitedStates">United States</option>
                  <option value="UnitedKingdom">United Kingdom</option>
                  <option value="Japan">Japan</option>
                </select>
              </div>
            </div>
          </div>

          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Calcul en cours...' : 'Calculer le Prix'}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: '30px', padding: '20px', background: '#fee2e2', borderRadius: '12px', border: '2px solid #ef4444' }}>
            <h3 style={{ color: '#991b1b', margin: '0 0 10px 0' }}>Erreur</h3>
            <p style={{ color: '#7f1d1d', margin: 0 }}>{error}</p>
          </div>
        )}

        {result && (
          <div className="results-container">
            <h2 className="results-title">
              <span>✓</span>
              Résultats du Pricing
            </h2>
            <p className="computation-time">
              Calculé en {result.computation_time_ms?.toFixed(2) || 'N/A'} ms
            </p>

            {result.confidence_interval && (
              <div className="confidence-interval">
                <h3 className="ci-title">Intervalle de Confiance ({(formData.confidenceLevel * 100).toFixed(0)}%)</h3>
                <div className="ci-grid">
                  <div className="ci-item">
                    <div className="ci-label">Borne Inférieure</div>
                    <div className="ci-value">{result.confidence_interval.lower_bound?.toFixed(4)}</div>
                  </div>
                  <div className="ci-item">
                    <div className="ci-label">Prix</div>
                    <div className="ci-value">{result.confidence_interval.price?.toFixed(4)}</div>
                  </div>
                  <div className="ci-item">
                    <div className="ci-label">Borne Supérieure</div>
                    <div className="ci-value">{result.confidence_interval.upper_bound?.toFixed(4)}</div>
                  </div>
                  <div className="ci-item">
                    <div className="ci-label">Erreur Standard</div>
                    <div className="ci-value">{result.confidence_interval.std_error?.toFixed(6)}</div>
                  </div>
                </div>
              </div>
            )}

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-label">Prix de l'Option</div>
                <div className="metric-value">{result.price?.toFixed(4)}</div>
              </div>
              {result.intrinsic_value !== undefined && (
                <div className="metric-card">
                  <div className="metric-label">Valeur Intrinsèque</div>
                  <div className="metric-value">{result.intrinsic_value?.toFixed(4)}</div>
                </div>
              )}
              {result.time_value !== undefined && (
                <div className="metric-card">
                  <div className="metric-label">Valeur Temps</div>
                  <div className="metric-value">{result.time_value?.toFixed(4)}</div>
                </div>
              )}
              {result.method && (
                <div className="metric-card">
                  <div className="metric-label">Méthode</div>
                  <div className="metric-value" style={{ fontSize: '1.25rem' }}>{result.method}</div>
                </div>
              )}
            </div>

            {result.greeks && (
              <div className="greeks-section">
                <h3 className="greeks-title">Sensibilités (Greeks)</h3>
                <div className="greeks-grid">
                  {result.greeks.delta !== undefined && (
                    <div className="greek-card">
                      <div className="greek-name">Delta (Δ)</div>
                      <div className="greek-value">{result.greeks.delta?.toFixed(4)}</div>
                    </div>
                  )}
                  {result.greeks.gamma !== undefined && (
                    <div className="greek-card">
                      <div className="greek-name">Gamma (Γ)</div>
                      <div className="greek-value">{result.greeks.gamma?.toFixed(4)}</div>
                    </div>
                  )}
                  {result.greeks.vega !== undefined && (
                    <div className="greek-card">
                      <div className="greek-name">Vega (ν)</div>
                      <div className="greek-value">{result.greeks.vega?.toFixed(4)}</div>
                    </div>
                  )}
                  {result.greeks.theta !== undefined && (
                    <div className="greek-card">
                      <div className="greek-name">Theta (Θ)</div>
                      <div className="greek-value">{result.greeks.theta?.toFixed(4)}</div>
                    </div>
                  )}
                  {result.greeks.rho !== undefined && (
                    <div className="greek-card">
                      <div className="greek-name">Rho (ρ)</div>
                      <div className="greek-value">{result.greeks.rho?.toFixed(4)}</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
