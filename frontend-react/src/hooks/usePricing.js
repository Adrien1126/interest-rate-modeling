import { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Hook personnalisé pour le pricing d'options
 */
export function usePricing() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  /**
   * Construit la requête de pricing à partir des données du formulaire
   */
  const buildPricingRequest = (formData) => {
    const today = new Date().toISOString().split('T')[0];
    const expirationDate = new Date();
    expirationDate.setFullYear(expirationDate.getFullYear() + parseFloat(formData.maturity));
    
    return {
      trade: {
        trade_id: `OPT-${Date.now()}`,
        trade_date: today,
        product_type: "Option",
        option: {
          option_type: formData.optionType === 'call' ? 'Call' : 'Put',
          exercise_type: "European",
          underlying: {
            asset_type: "Equity",
            isin: "US0000000000",
            description: "Generic Asset"
          },
          strike: parseFloat(formData.strike),
          expiration_date: expirationDate.toISOString().split('T')[0],
          notional: {
            amount: 1.0,
            currency: "USD"
          },
          settlement: {
            settlement_type: "Cash"
          }
        },
        parties: {
          buyer: { id: "user", name: "User" },
          seller: { id: "market", name: "Market" }
        }
      },
      spot_price: parseFloat(formData.spot),
      model_type: "BlackScholes",
      volatility: parseFloat(formData.volatility),
      risk_free_rate: parseFloat(formData.rate),
      dividend_yield: parseFloat(formData.dividendYield),
      compute_greeks: true,
      compute_implied_vol: false
    };
  };

  /**
   * Formate les résultats de l'API
   */
  const formatResult = (data) => ({
    price: data.price,
    delta: data.greeks?.delta || 0,
    gamma: data.greeks?.gamma || 0,
    vega: data.greeks?.vega || 0,
    theta: data.greeks?.theta || 0,
    rho: data.greeks?.rho || 0,
    computation_time: data.computation_time_ms
  });

  /**
   * Effectue le pricing d'une option
   */
  const priceOption = async (formData) => {
    setLoading(true);
    setError(null);
    
    try {
      const pricingRequest = buildPricingRequest(formData);
      
      const response = await fetch(`${API_BASE_URL}/pricing/option`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pricingRequest)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors du pricing');
      }

      const data = await response.json();
      const formattedResult = formatResult(data);
      
      setResult(formattedResult);
      return formattedResult;
      
    } catch (err) {
      console.error('Erreur:', err);
      const errorMessage = err.message || 'Erreur de connexion au backend';
      setError(errorMessage);
      setResult(null);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Réinitialise les résultats et erreurs
   */
  const reset = () => {
    setResult(null);
    setError(null);
    setLoading(false);
  };

  return {
    loading,
    error,
    result,
    priceOption,
    reset
  };
}

/**
 * Hook pour vérifier la santé du backend
 */
export function useHealthCheck() {
  const [healthy, setHealthy] = useState(null);

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/pricing/health`);
      const data = await response.json();
      setHealthy(data.status === 'healthy');
      return data;
    } catch (err) {
      setHealthy(false);
      return null;
    }
  };

  return { healthy, checkHealth };
}
