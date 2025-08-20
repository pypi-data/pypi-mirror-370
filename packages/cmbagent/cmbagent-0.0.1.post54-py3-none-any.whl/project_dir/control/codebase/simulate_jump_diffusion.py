# filename: codebase/simulate_jump_diffusion.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import time


def simulate_jump_diffusion(S0, T, r, sigma, lambda_, mu_j, sigma_j, n_steps, n_sims=1):
    """
    Simulates stock price paths using Merton's jump-diffusion model.

    This model incorporates a continuous geometric Brownian motion component and a
    discontinuous jump component (a compound Poisson process).

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
                       Shape is (n_steps + 1, n_sims).
    """
    dt = T / n_steps
    # The compensator ensures the expected return is consistent with the drift
    k = np.exp(mu_j + 0.5 * sigma_j**2) - 1
    drift = r - 0.5 * sigma**2 - lambda_ * k

    # Generate random numbers for the diffusion and jump components
    Z_diffusion = np.random.normal(0, 1, (n_steps, n_sims))
    Z_jumps = np.random.normal(mu_j, sigma_j, (n_steps, n_sims))
    poisson_process = np.random.poisson(lambda_ * dt, (n_steps, n_sims))

    # Calculate the log returns for each step
    log_returns = (drift * dt +
                   sigma * np.sqrt(dt) * Z_diffusion +
                   poisson_process * Z_jumps)

    # Initialize price array and set the initial price
    prices = np.zeros((n_steps + 1, n_sims))
    prices[0, :] = S0

    # Calculate the cumulative sum of log returns and convert to prices
    cumulative_log_returns = np.cumsum(log_returns, axis=0)
    prices[1:, :] = S0 * np.exp(cumulative_log_returns)

    return prices


def main():
    """
    Main function to run simulations, plot results, and save data.
    """
    # --- Simulation Parameters ---
    # These parameters are chosen to reflect a period of market stress.
    S0 = 100.0       # Initial stock price
    T = 2.0          # Time horizon in years (e.g., 2018-2020)
    r = 0.02         # Risk-free rate (annualized)
    n_steps = int(T * 252) # Number of trading days
    
    # Base Case: Moderate volatility and jump frequency
    base_params = {
        'sigma': 0.30,      # Volatility
        'lambda_': 5.0,     # 5 jumps per year on average
        'mu_j': -0.02,      # Average jump size (log-return) of -2%
        'sigma_j': 0.03     # Volatility of jump size
    }

    # Scenario 2: High Volatility
    high_vol_params = base_params.copy()
    high_vol_params['sigma'] = 0.50

    # Scenario 3: High Jump Intensity
    high_jump_intensity_params = base_params.copy()
    high_jump_intensity_params['lambda_'] = 15.0 # 15 jumps per year

    # Scenario 4: Large Negative Jumps
    large_neg_jump_params = base_params.copy()
    large_neg_jump_params['mu_j'] = -0.08 # Average jump size of -8%

    scenarios = {
        "Base Case": base_params,
        "High Volatility (sigma=0.5)": high_vol_params,
        "High Jump Intensity (lambda=15)": high_jump_intensity_params,
        "Large Negative Jumps (mu_j=-0.08)": large_neg_jump_params
    }

    # --- Run Simulations ---
    np.random.seed(42) # for reproducibility
    simulated_paths = {}
    for name, params in scenarios.items():
        print("Running simulation for: " + name)
        print("Parameters: " + str(params))
        paths = simulate_jump_diffusion(
            S0=S0, T=T, r=r, n_steps=n_steps, **params
        )
        simulated_paths[name] = paths[:, 0] # Take the first simulation path

    # --- Save Data ---
    database_path = "data/"
    if not os.path.exists(database_path):
        os.makedirs(database_path)

    base_case_data = pd.DataFrame({
        'Date': pd.to_datetime(pd.date_range(start='2018-01-01', periods=n_steps + 1)),
        'Price': simulated_paths['Base Case']
    })
    
    data_filename = os.path.join(database_path, "simulated_stock_data_base_case.csv")
    base_case_data.to_csv(data_filename, index=False)
    print("\nSaved base case simulated data to: " + data_filename)

    # --- Plotting ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=True, sharey=True)
    axes = axes.flatten()
    time_axis = np.linspace(0, T, n_steps + 1)
    
    plt.rcParams['text.usetex'] = False

    for i, (name, path) in enumerate(simulated_paths.items()):
        axes[i].plot(time_axis, path, label=name)
        axes[i].set_title(name)
        axes[i].set_ylabel("Stock Price ($)")
        axes[i].grid(True, which='both', linestyle='--', linewidth=0.5)
        if i >= 2:
            axes[i].set_xlabel("Time (Years)")

    fig.suptitle("Simulated Stock Prices under Different Market Conditions", fontsize=16)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # --- Save Plot ---
    timestamp = int(time.time())
    plot_filename = os.path.join(database_path, "stock_simulation_scenarios_1_" + str(timestamp) + ".png")
    plt.savefig(plot_filename, dpi=300)
    print("Plot saved to: " + plot_filename)
    print("Plot description: Comparison of simulated stock price paths under four scenarios: Base Case, High Volatility, High Jump Intensity, and Large Negative Jumps.")


if __name__ == "__main__":
    main()