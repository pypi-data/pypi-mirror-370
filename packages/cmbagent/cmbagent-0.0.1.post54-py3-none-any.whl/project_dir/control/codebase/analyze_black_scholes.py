# filename: codebase/analyze_black_scholes.py
import pandas as pd
import numpy as np
from scipy.stats import norm, shapiro
from scipy.optimize import brentq
import matplotlib.pyplot as plt
import os
import time

# Assuming the simulation script is in the same directory or accessible
try:
    from codebase.simulate_jump_diffusion import simulate_jump_diffusion
except ImportError:
    # Fallback for standalone execution if the module structure is not set up
    def simulate_jump_diffusion(S0, T, r, sigma, lambda_, mu_j, sigma_j, n_steps, n_sims=1):
        """
        Simulates stock price paths using Merton's jump-diffusion model.
        This is a fallback implementation.
        """
        dt = T / n_steps
        k = np.exp(mu_j + 0.5 * sigma_j**2) - 1
        drift = r - 0.5 * sigma**2 - lambda_ * k
        Z_diffusion = np.random.normal(0, 1, (n_steps, n_sims))
        Z_jumps = np.random.normal(mu_j, sigma_j, (n_steps, n_sims))
        poisson_process = np.random.poisson(lambda_ * dt, (n_steps, n_sims))
        log_returns = (drift * dt +
                       sigma * np.sqrt(dt) * Z_diffusion +
                       poisson_process * Z_jumps)
        prices = np.zeros((n_steps + 1, n_sims))
        prices[0, :] = S0
        cumulative_log_returns = np.cumsum(log_returns, axis=0)
        prices[1:, :] = S0 * np.exp(cumulative_log_returns)
        return prices


def check_log_normality(prices, database_path):
    """
    Checks if the log-returns of the price series are normally distributed.

    Args:
        prices (np.ndarray): Array of stock prices.
        database_path (str): Path to save the plot.
    """
    log_returns = np.log(prices[1:] / prices[:-1])
    
    # Shapiro-Wilk test for normality
    stat, p_value = shapiro(log_returns)
    print("--- Log-Normality Assumption Check ---")
    print("Shapiro-Wilk Test Statistic: " + str(stat))
    print("P-value: " + str(p_value))
    if p_value > 0.05:
        print("Conclusion: The log-returns appear to be normally distributed (fail to reject H0).")
    else:
        print("Conclusion: The log-returns do not appear to be normally distributed (reject H0).")
        print("This is expected for a jump-diffusion process.")

    # Plotting the histogram of log-returns vs. normal distribution
    plt.figure(figsize=(10, 6))
    plt.hist(log_returns, bins=50, density=True, alpha=0.6, color='g', label='Log-Return Distribution')
    
    mu, std = norm.fit(log_returns)
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2, label='Normal Distribution Fit')
    
    plt.title('Distribution of Daily Log-Returns vs. Normal Distribution')
    plt.xlabel('Log-Return')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    timestamp = int(time.time())
    plot_filename = os.path.join(database_path, "log_return_normality_check_2_" + str(timestamp) + ".png")
    plt.savefig(plot_filename, dpi=300)
    print("\nPlot saved to: " + plot_filename)
    print("Plot description: Histogram of simulated daily log-returns compared with a fitted normal distribution curve.")
    print("--------------------------------------\n")


def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    """
    Calculates the Black-Scholes price for a European option.

    Args:
        S (float): Current stock price.
        K (float): Strike price.
        T (float): Time to maturity in years.
        r (float): Risk-free interest rate.
        sigma (float): Volatility of the stock.
        option_type (str): 'call' or 'put'.

    Returns:
        float: The Black-Scholes option price.
    """
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        price = (S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))
    elif option_type == 'put':
        price = (K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1))
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'.")
        
    return price


def monte_carlo_jump_diffusion_pricer(S0, K, T, r, sigma, lambda_, mu_j, sigma_j, n_steps, n_sims=10000):
    """
    Prices a European call option using Monte Carlo simulation with a jump-diffusion model.

    Args:
        S0, K, T, r, sigma, lambda_, mu_j, sigma_j: Model parameters.
        n_steps (int): Number of time steps for simulation.
        n_sims (int): Number of simulation paths for Monte Carlo.

    Returns:
        float: The estimated option price.
    """
    paths = simulate_jump_diffusion(S0, T, r, sigma, lambda_, mu_j, sigma_j, n_steps, n_sims)
    terminal_prices = paths[-1, :]
    payoffs = np.maximum(terminal_prices - K, 0)
    discounted_payoff = np.exp(-r * T) * np.mean(payoffs)
    return discounted_payoff


def implied_volatility(true_price, S, K, T, r):
    """
    Calculates the implied volatility using the Brentq root-finding algorithm.
    """
    def objective_function(sigma):
        return black_scholes_price(S, K, T, r, sigma, 'call') - true_price
    
    try:
        # Brentq is a robust root-finding algorithm
        return brentq(objective_function, 1e-6, 2.0) # Search between 0.01% and 200% vol
    except ValueError:
        return np.nan


def main():
    """
    Main function to run the Black-Scholes analysis.
    """
    # --- Parameters from the simulation (Base Case) ---
    S0 = 100.0
    T = 2.0
    r = 0.02
    n_steps = int(T * 252)
    model_sigma = 0.30
    lambda_ = 5.0
    mu_j = -0.02
    sigma_j = 0.03
    
    # --- Option Parameters ---
    K = 100.0  # At-the-money option
    T_option = 1.0 # 1-year to maturity

    # --- Load Data ---
    database_path = "data/"
    data_filename = os.path.join(database_path, "simulated_stock_data_base_case.csv")
    if not os.path.exists(data_filename):
        print("Error: Simulated data file not found. Please run the simulation step first.")
        return
        
    data = pd.read_csv(data_filename)
    prices = data['Price'].values

    # 1. Verify Black-Scholes Assumptions
    check_log_normality(prices, database_path)

    # 2. Price option with Black-Scholes using the model's input volatility
    bs_price = black_scholes_price(S0, K, T_option, r, model_sigma, 'call')
    
    # 3. Calculate "true" price with Monte Carlo under jump-diffusion
    print("Calculating 'true' option price via Monte Carlo (Jump-Diffusion)...")
    np.random.seed(42) # for reproducibility
    true_market_price = monte_carlo_jump_diffusion_pricer(
        S0, K, T_option, r, model_sigma, lambda_, mu_j, sigma_j, int(T_option * 252)
    )
    print("Calculation complete.")

    # 4. Calculate Pricing Errors
    pricing_error = bs_price - true_market_price
    rmse = np.sqrt(np.mean(pricing_error**2))

    print("\n--- Option Pricing Analysis ---")
    print("Option Type: European Call")
    print("Strike Price (K): " + str(K))
    print("Time to Maturity (T): " + str(T_option) + " years")
    print("\nBlack-Scholes Price (using model sigma=" + str(model_sigma) + "): " + str(bs_price))
    print("'True' Market Price (from Jump-Diffusion MC): " + str(true_market_price))
    print("\nPricing Error (BS - True): " + str(pricing_error))
    print("Root Mean Squared Error (RMSE): " + str(rmse))
    print("---------------------------------\n")

    # 5. Compare Volatilities
    # Realized volatility from the full 2-year path
    log_returns = np.log(prices[1:] / prices[:-1])
    realized_volatility = np.std(log_returns) * np.sqrt(252) # Annualized

    # Implied volatility from the "true" market price
    imp_vol = implied_volatility(true_market_price, S0, K, T_option, r)

    print("--- Volatility Comparison ---")
    print("Model Input Volatility (sigma for simulation): " + str(model_sigma))
    print("Annualized Realized Volatility (from data): " + str(realized_volatility))
    print("Implied Volatility (from 'true' price): " + str(imp_vol))
    print("-----------------------------")


if __name__ == "__main__":
    main()