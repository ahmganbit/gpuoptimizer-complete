import React, { useState, useEffect } from 'react';
import './PaymentGatewaySelector.css';

const PaymentGatewaySelector = ({ onGatewaySelect, customerEmail, selectedPlan, country }) => {
  const [gateways, setGateways] = useState([]);
  const [selectedGateway, setSelectedGateway] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAvailableGateways();
  }, [country]);

  const fetchAvailableGateways = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/payment/gateways?country=${country || ''}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setGateways(data.gateways);
        // Auto-select recommended gateway
        if (data.recommended) {
          setSelectedGateway(data.recommended.id);
          onGatewaySelect(data.recommended.id);
        }
      } else {
        setError('Failed to load payment methods');
      }
    } catch (err) {
      setError('Failed to load payment methods');
      console.error('Gateway fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGatewaySelect = (gatewayId) => {
    setSelectedGateway(gatewayId);
    onGatewaySelect(gatewayId);
  };

  const getGatewayIcon = (gatewayId) => {
    const icons = {
      nowpayments: '₿',
      flutterwave: '🌊',
      paddle: '🏓'
    };
    return icons[gatewayId] || '💳';
  };

  const getGatewayDescription = (gateway) => {
    const descriptions = {
      nowpayments: 'Pay with Bitcoin, Ethereum, USDT and 100+ cryptocurrencies worldwide',
      flutterwave: 'Cards, mobile money, Apple Pay, Google Pay, and bank transfers',
      paddle: 'Professional SaaS billing with automatic tax handling worldwide'
    };
    return descriptions[gateway.id] || 'Secure payment processing';
  };

  if (loading) {
    return (
      <div className="payment-gateway-selector loading">
        <div className="loading-spinner"></div>
        <p>Loading payment methods...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="payment-gateway-selector error">
        <p className="error-message">{error}</p>
        <button onClick={fetchAvailableGateways} className="retry-button">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="payment-gateway-selector">
      <h3>Choose Your Payment Method</h3>
      <p className="subtitle">Select how you'd like to pay for your {selectedPlan} plan</p>
      
      <div className="gateways-grid">
        {gateways.map((gateway) => (
          <div
            key={gateway.id}
            className={`gateway-option ${selectedGateway === gateway.id ? 'selected' : ''} ${gateway.recommended ? 'recommended' : ''}`}
            onClick={() => handleGatewaySelect(gateway.id)}
          >
            {gateway.recommended && (
              <div className="recommended-badge">Recommended</div>
            )}
            
            <div className="gateway-icon">
              {getGatewayIcon(gateway.id)}
            </div>
            
            <div className="gateway-info">
              <h4>{gateway.name}</h4>
              <p className="gateway-description">
                {getGatewayDescription(gateway)}
              </p>
              <div className="gateway-details">
                <span className="fees">Fees: {gateway.fees}</span>
                {gateway.currencies && (
                  <span className="currencies">
                    Supports: {gateway.currencies.slice(0, 3).join(', ')}
                    {gateway.currencies.length > 3 && ` +${gateway.currencies.length - 3} more`}
                  </span>
                )}
              </div>
            </div>
            
            <div className="selection-indicator">
              {selectedGateway === gateway.id && <span className="checkmark">✓</span>}
            </div>
          </div>
        ))}
      </div>
      
      {gateways.length === 0 && (
        <div className="no-gateways">
          <p>No payment methods available for your region.</p>
          <p>Please contact support for assistance.</p>
        </div>
      )}
      
      <div className="security-notice">
        <span className="security-icon">🔒</span>
        <span>All payments are secured with enterprise-grade encryption</span>
      </div>
    </div>
  );
};

export default PaymentGatewaySelector;
