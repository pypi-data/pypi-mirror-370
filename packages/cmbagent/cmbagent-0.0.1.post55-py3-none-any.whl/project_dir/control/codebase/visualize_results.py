# filename: codebase/visualize_results.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from scipy.stats import norm


def simulate_jump_diffusion(S0, T, r, sigma, lambda_, mu_j, sigma_j, n_steps, n_sims=1):
    """
    Simulates stock price paths using Merton's jump-diffusion model.
    This is a helper function copied from the previous step for self-containment.

    Args:
        S0 (float): Initial stock price.
        T (float): Time to maturity in years.
        r (float): Risk-free interest rate (annualized).
        sigma (float): Volatility of the stock price (annualized).
        lambda_ (float): Jump intensity (average number of jumps per year).
        mu_j (float): Mean of the log-jump size.
        sigma_j (float): Standard deviation of the log-jump size.
        n_steps (int): Number of time steps for the simulation.
        n_sims (int): Number of simulation paths to generate.

    Returns:
        numpy.ndarray: A 2D array of simulated stock price paths.
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


def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    """
    Calculates the Black-Scholes price for a European option.
    This is a helper function copied from the previous step for self-containment.

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
    if T <= 0:
        if option_type == 'call':
            return max(0.0, S - K)
        elif option_type == 'put':
            return max(0.0, K - S)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == 'call':
        price = (S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2))
    elif option_type == 'put':
        price = (K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1))
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'.")
        
    return price


def monte_carlo_pricer_with_ci(S0, K, T, r, sigma, lambda_, mu_j, sigma_j, n_sims=2000):
    """
    Prices a European call option using Monte Carlo with jump-diffusion and provides a confidence interval.

    Args:
        S0, K, T, r, sigma, lambda_, mu_j, sigma_j: Model parameters.
        n_sims (int): Number of simulation paths for Monte Carlo.

    Returns:
        tuple: (mean_price, std_err, price_std_dev)
    """
    if T <= 0:
        return max(0.0, S0 - K), 0.0, 0.0
        
    n_steps = int(T * 252)
    if n_steps <= 0:
        n_steps = 1

    paths = simulate_jump_diffusion(S0, T, r, sigma, lambda_, mu_j, sigma_j, n_steps, n_sims)
    terminal_prices = paths[-1, :]
    payoffs = np.maximum(terminal_prices - K, 0)
    discounted_payoffs = np.exp(-r * T) * payoffs
    
    mean_price = np.mean(discounted_payoffs)
    price_std_dev = np.std(discounted_payoffs)
    std_err = price_std_dev / np.sqrt(n_sims)
    
    return mean_price, std_err, price_std_dev


def main():
    """
    Main function to visualize and summarize the results.
    """
    # --- Parameters ---
    S0 = 100.0
    r = 0.02
    model_sigma = 0.30
    lambda_ = 5.0
    mu_j = -0.02
    sigma_j = 0.03
    K = 100.0
    T_option = 1.0 # 1-year option
    
    # --- Load Data ---
    database_path = "data/"
    data_filename = os.path.join(database_path, "simulated_stock_data_base_case.csv")
    if not os.path.exists(data_filename):
        print("Error: Simulated data file not found. Please run step 1 first.")
        return
    data = pd.read_csv(data_filename)
    
    # We analyze the pricing over the first year (the life of the option)
    n_option_days = int(T_option * 252)
    analysis_prices = data['Price'].values[:n_option_days + 1]
    time_axis = np.linspace(0, T_option, n_option_days + 1)

    # --- Calculate Prices and Errors Over Time ---
    results = []
    # Reduce frequency of MC calculation to speed up the process
    calculation_step = 5 
    print("Calculating BS vs. True prices over time... (this may take a moment)")
    np.random.seed(123) # for reproducibility
    for i in range(0, len(analysis_prices), calculation_step):
        current_S = analysis_prices[i]
        time_elapsed = time_axis[i]
        T_rem = T_option - time_elapsed

        # Calculate Black-Scholes Price
        bs_price = black_scholes_price(current_S, K, T_rem, r, model_sigma)

        # Calculate "True" Market Price via Jump-Diffusion MC
        true_price_mean, _, true_price_std = monte_carlo_pricer_with_ci(
            S0=current_S, K=K, T=T_rem, r=r, sigma=model_sigma,
            lambda_=lambda_, mu_j=mu_j, sigma_j=sigma_j
        )
        
        pricing_error = bs_price - true_price_mean
        
        results.append([time_elapsed, current_S, bs_price, true_price_mean, true_price_std, pricing_error])
    print("Calculation complete.")

    # --- Summarize and Save Results ---
    results_df = pd.DataFrame(
        results,
        columns=['Time (Years)', 'Stock Price', 'BS Price', 'True Price (Mean)', 'True Price (Std Dev)', 'Pricing Error']
    )
    
    print("\n--- Summary of Pricing Analysis ---")
    # Configure pandas to display floats with more precision
    pd.set_option('display.float_format', lambda x: '%.4f' % x)
    print(results_df)
    
    summary_filename = os.path.join(database_path, "pricing_analysis_summary.csv")
    results_df.to_csv(summary_filename, index=False)
    print("\nSaved pricing analysis summary to: " + summary_filename)

    # --- Plotting ---
    plt.rcParams['text.usetex'] = False
    fig, axes = plt.subplots(3, 1, figsize=(14, 15), sharex=True)
    
    # Plot 1: Stock Price Path
    axes[0].plot(time_axis, analysis_prices, color='darkgray', label='Simulated Stock Price')
    axes[0].set_title('Simulated Underlying Stock Price Path')
    axes[0].set_ylabel('Stock Price ($)')
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend()

    # Plot 2: Option Prices Comparison
    axes[1].plot(results_df['Time (Years)'], results_df['BS Price'], 'r-', label='Black-Scholes Price')
    axes[1].plot(results_df['Time (Years)'], results_df['True Price (Mean)'], 'b--', label='"True" Price (Jump-Diffusion MC)')
    
    # Confidence Interval for True Price
    ci_upper = results_df['True Price (Mean)'] + 1.96 * results_df['True Price (Std Dev)'] / np.sqrt(2000)
    ci_lower = results_df['True Price (Mean)'] - 1.96 * results_df['True Price (Std Dev)'] / np.sqrt(2000)
    axes[1].fill_between(results_df['Time (Years)'], ci_lower, ci_upper, color='blue', alpha=0.2, label='95% CI for True Price')
    
    axes[1].set_title('Black-Scholes vs. "True" Market Price for a Call Option')
    axes[1].set_ylabel('Option Price ($)')
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend()

    # Plot 3: Pricing Error (Residuals)
    axes[2].plot(results_df['Time (Years)'], results_df['Pricing Error'], 'g-', label='Pricing Error (BS - True)')
    axes[2].axhline(0, color='black', linestyle='--', linewidth=1)
    axes[2].set_title('Black-Scholes Pricing Error Over Time')
    axes[2].set_xlabel('Time (Years)')
    axes[2].set_ylabel('Pricing Error ($)')
    axes[2].grid(True, linestyle='--', alpha=0.6)
    axes[2].legend()

    fig.tight_layout()

    # --- Save Plot ---
    timestamp = int(time.time())
    plot_filename = os.path.join(database_path, "pricing_model_comparison_3_" + str(timestamp) + ".png")
    plt.savefig(plot_filename, dpi=300)
    print("\nPlot saved to: " + plot_filename)
    print("Plot description: Comparison of Black-Scholes and Jump-Diffusion option prices, with stock path and pricing error.")


if __name__ == "__main__":
    main()