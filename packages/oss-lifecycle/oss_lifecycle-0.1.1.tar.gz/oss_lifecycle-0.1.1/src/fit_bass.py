# Fitting the growth in developers to the Bass model

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime   
import sys
from sklearn.linear_model import LinearRegression
from scipy.optimize import fsolve
pd.options.mode.chained_assignment = None  # default='warn'


def bass(p, q, t):
    """
    Bass model for the growth of developers
    t: time
    p: coefficient of innovation
    q: coefficient of imitation
    Returns:
        f(t), is intensity of developer engagement in month t
        F(t), integrated f(t), f(t)=dF/dt
    Related to computing:
        m: total number of developer-months through the life of the project
    """
    f = (np.exp((p+q)*t)*p*(p+q)**2)/(p*np.exp((p+q)*t)+q)**2
    F = p*(np.exp((p+q)*t)-1)/(p*np.exp((p+q)*t)+q)
    return f, F

def fitBass(df, repo_string, do_plot=True):
    """
    Fit the Bass model to the data
    """
    df["x"] = df["contributors"].cumsum()
    df["x2"] = df["x"]**2
    X = pd.concat([df["x"], df["x2"]], axis=1)
    y = df["contributors"]
    print("Number of periods:", len(df))

    model = LinearRegression()
    model.fit(X, y)

    b0 = model.intercept_
    b1 = model.coef_[0]
    b2 = model.coef_[1]

    m1 = (-b1 + np.sqrt(b1**2 - 4*b2*b0))/(2*b2)
    m2 = (-b1 - np.sqrt(b1**2 - 4*b2*b0))/(2*b2)
    m = np.max([m1, m2])

    p = b0/m
    q = -m*b2

    # Plot the fitted contributors per month
    if do_plot:
        t = np.arange(0, len(df))
        plt.plot(t, bass(p, q, t)[0]*m, color='red', linewidth=2)
        plt.scatter(t, df['contributors'])
        plt.title(f"Number of Developers per month [{repo_string}]")
        plt.xlabel("Months since project start")
        plt.grid(True)
        plt.savefig(f"images/{repo_string}_fit_contributors.png")
        plt.show()

    return p, q, m


def forecastL(p, q, m, t):
    """
    Forecast the number of developers at through t
    p,q,m are the Bass model parameters (scalars)
    t is the time period (vector) through the forecast horizon
    """
    return bass(p, q, t)[0]*m


# Function to solve for f=0 in bass(p,q,t)
def solve_for_zero(t, p, q, m):
    """
    Solve for f=0 in bass(p, q, t)
    """
    f, _ = bass(p, q, t)
    return f*m - 0.5 # no full time developer on the project

def find_zero(t_initial_guess, p, q, m):
    """
    Find the value of t at which the function f value is zero
    """
    t_zero = fsolve(solve_for_zero, t_initial_guess, args=(p, q, m))
    if t_zero<0:
        t_zero = fsolve(solve_for_zero, t_initial_guess*2, args=(p, q, m)) # in case guess too low initially
    return t_zero[0]


def get_project_developer_model_stats(repo_string):
    """
    Get the project data
    """
    print("Project:", repo_string)
    df = pd.read_csv("data/" + repo_string + "-monthly.csv")
    start_date = df['date'].iloc[0].split()[0]
    end_date = df['date'].iloc[-1].split()[0]
    # Fit the Bass model
    num_devs_df = df[['contributors']]
    p, q, m = fitBass(num_devs_df, repo_string)
    print(f"p={p}, q={q}, m={m}")
    # Time to end of growth
    t = len(df)
    T = find_zero(t, p, q, m)
    print(f"Time of zero growth: {T} months")
    yrs = (T-t)/12
    print("Remaining months =", T-t, " =", yrs, "years")
    return start_date, end_date, p, q, m, t, T, yrs

# Main run
if __name__ == "__main__":
    """
    To run: 
    python src/fit_bass.py "<owner>/<repo>" (from root folder)
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
        print("Repo name:", repo_name)
        owner, repo = repo_name.split('/')
        repo_string = owner + '-' + repo
        df = pd.read_csv("data/" + repo_string + "-monthly.csv")

        # Fit the Bass model
        num_devs_df = df[['contributors']]
        p, q, m = fitBass(num_devs_df, repo_string)
        print(f"p={p}, q={q}, m={m}")

        # Time to end of growth
        t = len(df)
        T = find_zero(t, p, q, m)
        print(f"Time of zero growth: {T} months")
        print("Remaining months =", T-t, " =", (T-t)/12, "years")
        
        # Plot the fitted contributors per month
        t_list = np.arange(0, t)
        f, _ = bass(p, q, t_list)
        plt.plot(t_list, f*m, linewidth=2)
        plt.title(f"Number of Developers per month [{repo_string}]")
        plt.xlabel("Months since project start")
        plt.grid(True)
        t_list = np.arange(t, T)
        f, _ = bass(p, q, t_list)
        plt.plot(t_list, f*m, linewidth=2, color='red')
        plt.savefig(f"images/{repo_string}_contributors_to_end.png")
        plt.show()