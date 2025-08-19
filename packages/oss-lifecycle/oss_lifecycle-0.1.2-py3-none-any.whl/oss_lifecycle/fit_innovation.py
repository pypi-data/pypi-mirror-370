import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.optimize import curve_fit, minimize
from scipy.integrate import solve_ivp
from .fit_bass import bass, fitBass, forecastL


def polyfit_innovation_timeseries(df, repo_string):
    """
    Fit the innovation model to the data using a second degree polynomial
    """
    # Convert dates to numeric values (days since first date)
    first_date = df['date'].min()
    days = [(d - first_date).days for d in df['date']]

    # Fit quadratic curve
    coefficients = np.polyfit(days, df['cumInnovation'], deg=2)
    a, b, c = coefficients

    # Generate points for the fitted curve
    days_range = np.array(days)
    fitted_values = a * days_range**2 + b * days_range + c
    true_values = np.array(df['cumInnovation'])

    # Plot original data and fitted curve
    plt.figure(figsize=(6, 4))
    plt.plot(df['date'], true_values, 'b.', alpha=0.5, label='Actual Data')
    plt.plot(df['date'], fitted_values, 'r-', label='Quadratic Fit')
    plt.title(f"Cumulative Innovation $A(t)$ with Quadratic Fit [{repo_string}]")
    plt.grid(True)
    plt.legend()

    # Print the equation of the fitted curve
    print(f"Quadratic equation: A(t) = {a:.2e}t² + {b:.2e}t + {c:.2e}")

    # Calculate R-squared
    residuals = true_values - fitted_values
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((true_values - np.mean(true_values))**2)
    r_squared = 1 - (ss_res / ss_tot)
    print(f"R² = {r_squared:.4f}")

    plt.savefig(f"images/{repo_string}_polyfit_innovation.png")
    plt.show()
    return fitted_values, true_values

     
def prepareDF(df):
    """
    Prepare the data frame for the innovation model
    """
    # df.drop("Unnamed: 0", axis=1, inplace=True)
    df = df[['date', 'total_changes', 'contributors']]
    df.loc[:,'date'] = [j.split()[0] for j in df['date']]
    df.loc[:,'date'] = [pd.to_datetime(j) for j in df['date']]
    df['cumInnovation'] = df['total_changes'].cumsum()
    df = df[df['cumInnovation']>0].reset_index(drop=True)
    return df


# Define the differential equation
def dA_dt(A, L, gamma, lam, phi):
    return gamma * L**lam * A**phi

def model(t, gamma, lam, phi, df_AL):
    A = np.zeros(len(t))
    L = np.zeros(len(t))
    A[0] = df_AL['A'].iloc[0]
    L[0] = df_AL['L'].iloc[0]
    for i in range(1, len(t)):
        A[i] = A[i-1] + dA_dt(A[i-1], L[i-1], gamma, lam, phi) * (t[i] - t[i-1])
        L[i] = df_AL['L'].iloc[i]
    return A

def pct_least_squares(params, t, A_fitted_values, df_AL):
    gamma, lam, phi = params
    Ahat = model(t, gamma, lam, phi, df_AL)
    Adiff = (Ahat - A_fitted_values)**2
    return np.sqrt(np.mean(Adiff)) # RMSE


def fitInnovation(df, repo_string, do_plot=True):
    df_AL = pd.DataFrame({'A': list(df['cumInnovation']), 'L': list(df['contributors'])})
    df_AL = df_AL[df_AL.A>0]
    df_AL = df_AL[df_AL.L>0]
    df_AL = df_AL.reset_index(drop=True)

    # Fit the data
    t = np.arange(len(df_AL))
    params = [10, 0.1, 0.1] # initial guess

    # Series to fit
    Atrue = list(df_AL['A'])

    # Get original obj fn value
    res = pct_least_squares(params, t, Atrue, df_AL)
    print("Initial obj fn value =", res)

    # Minimize obj fn
    sol = minimize(pct_least_squares, params, 
                args=(t, Atrue, df_AL), 
                method='Nelder-Mead', tol=1e-6, options={'maxiter':100000})
    print("Final obj fn value =", sol.fun, "(", round(sol.fun/res*100,2), "% )")
    print("Solution success:", sol.success)
    [gamma, lam, phi] = sol.x

    # Fitted series
    Ahat = model(t, gamma, lam, phi, df_AL)

    # Print the best-fit parameters
    print(f"Best-fit parameters:")
    print(f"gamma = {gamma:.3f}")
    print(f"lambda = {lam:.3f}")
    print(f"phi = {phi:.3f}")

    # First subplot
    if do_plot:
        plt.plot(t, Ahat, label="Ahat")
        plt.plot(t, Atrue, label="Atrue")
        plt.title(f"A: Innovation [{repo_string}]")
        plt.xlabel('Time periods')
        plt.legend()
        plt.grid()
        plt.savefig(f"images/{repo_string}_innovation_fit.png")
        plt.show()

    return gamma, lam, phi


def forecastA(gamma, lam, phi, t, A0, L_actual, L_forecast):
    """
    Forecast the innovation A through t
    gamma, lam, phi are the innovation model parameters (scalars)
    A0 is the initial innovation
    L_actual is the number of developers over time (vector), use for A forecast first
    L_forecast is num developers forecasted for post current life A forecasts
    """
    A = np.zeros(len(L_forecast))
    A[0] = A0
    for i in range(1, len(L_actual)):
        A[i] = A[i-1] + dA_dt(A[i-1], L_actual[i-1], gamma, lam, phi) * (t[i] - t[i-1])    
    for i in range(len(L_actual), len(L_forecast)):
        A[i] = A[i-1] + dA_dt(A[i-1], L_forecast[i-1], gamma, lam, phi) * (t[i] - t[i-1])    
    return A


def plotForecast(A, L, forecast_length, repo_string):
    """
    Plot the forecasted innovation and the number of developers
    `forecast_length` is the number of months to forecast
    """
    t = np.arange(len(A))
    # Create plots
    plt.figure(figsize=(15, 5))

    # Plot A(t)
    plt.subplot(131)
    plt.plot(t[:-forecast_length], A[:-forecast_length], 'b-', linewidth=2.5, label='A(t)')
    plt.plot(t[-forecast_length:], A[-forecast_length:], 'b--', linewidth=2.5, label='Forecast')
    plt.xlabel('Time')
    plt.ylabel('Innovation Level A')
    plt.title('Innovation Level vs Time')
    plt.grid(True)
    plt.legend()

    # Plot L(t)
    plt.subplot(132)
    plt.plot(t[:-forecast_length], L[:-forecast_length], 'r-', linewidth=2.5, label='L(t)')
    plt.plot(t[-forecast_length:], L[-forecast_length:], 'r--', linewidth=2.5, label='Forecast')
    plt.xlabel('Time')
    plt.ylabel('Labor L')
    plt.title(f'Labor vs Time [{repo_string}]')
    plt.grid(True)
    plt.legend()

    # Plot phase diagram (A vs L)
    plt.subplot(133)
    plt.plot(L[:-forecast_length], A[:-forecast_length], 'g-', linewidth=2.5, label='Phase Path')
    plt.plot(L[-forecast_length:], A[-forecast_length:], 'g--', linewidth=2.5, label='Forecast')
    plt.plot(L[0], A[0], 'ko', label='Initial Point')
    plt.xlabel('Labor L')
    plt.ylabel('Innovation Level A')
    plt.title('Phase Diagram')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"images/{repo_string}_forecasts.png")
    plt.show()


def growth(repo_name):
    """
    Fit the growth model to the lines of code and number of developers in a project
    """
    if not "/" in repo_name:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
    else:
        owner, repo = repo_name.split('/')
        repo_string = owner + '-' + repo
        df = pd.read_csv("data/" + repo_string + "-monthly.csv")

        # Fit contributor data
        num_devs_df = df[['contributors']]
        p, q, m = fitBass(num_devs_df, repo_string)
        t = np.arange(0, len(num_devs_df))
        fitted_contributors = bass(p, q, t)[0]*m
        df.loc[:,'contributors'] = fitted_contributors.astype(np.int64) # replace contributors with fitted values

        # Fit innovation data
        df = prepareDF(df)
        fitted_values, true_values = polyfit_innovation_timeseries(df, repo_string)
        gamma, lam, phi = fitInnovation(df, repo_string)
        
        # get forecasts
        forecast_length = 12 # for no forecast, set to 1 month
        t = np.arange(len(df)+forecast_length) # added 120 months to forecast, i.e., 10 years
        L = forecastL(p, q, m, t)
        # A = forecastA(gamma, lam, phi, t, df['cumInnovation'][0], L)
        A = forecastA(gamma, lam, phi, t, df['cumInnovation'][0], df['contributors'], L)
        plotForecast(A, L, forecast_length, repo_string)


# Main run
if __name__ == "__main__":
    """
    To run: 
    python oss_lifecycle/fit_innovation.py "<owner>/<repo>" (from root folder)
    """
    if len(sys.argv) < 2:
        print("Please provide a GitHub repository name in format '<owner>/<repo>'.")
        # EXAMPLES
        # repo_name = 'jupyterlab/jupyter-ai'
        # repo_name = 'jupyter-server/jupyter-scheduler'
        # repo_name = 'pandas-dev/pandas'
        # repo_name = 'jupyterlab/jupyterlab'
        # repo_name = 'langchain-ai/langchain'
        # repo_name = 'langchain-ai/langchain-aws'        
    else:  
        repo_name = sys.argv[1]
        growth(repo_name)
