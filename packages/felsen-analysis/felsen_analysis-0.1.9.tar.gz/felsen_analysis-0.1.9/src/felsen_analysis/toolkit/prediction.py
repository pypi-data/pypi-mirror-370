from felsen_analysis.toolkit.process import AnalysisObject
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from scipy import stats

def predictSaccadeMetrics(trialsToAnalyze, z, sacMetrics):
    """
    This function uses linear regression to predict trial-by-trial saccade metrics based on activity of a given population
    You give it a list of trials (for example, all contralateral saccades in a session) and arrays with firing rate (from your population) and saccade metric info
    It returns an array with the predicted values for each trial based on the population activity, as well as a score for prediction accuracy
    """
    idxs = np.random.permutation(range(0, len(trialsToAnalyze)))
    train_half = idxs[:len(trialsToAnalyze)//2]
    test_half = idxs[len(trialsToAnalyze)//2:]
    sacMetrics[np.isnan(sacMetrics)] = 0
    model = LinearRegression()
    model.fit(z[:, train_half].T, sacMetrics[train_half, :])
    predicted = model.predict(z[:, test_half].T)
    scoreTrain = model.score(z[:, train_half].T, sacMetrics[train_half, :])
    scoreTest = model.score(z[:, test_half].T, sacMetrics[test_half, :])
    return predicted, scoreTrain, scoreTest, test_half

def predictSingleUnitActivity(trialsToAnalyze, sacMetrics, unitActivity):
    """
    This functions uses linear regression to predict trial-by-trial activity of a single unit using the saccade metrics on each trial
    """
    idxs = np.random.permutation(range(0, len(trialsToAnalyze)))
    train_half = idxs[:len(trialsToAnalyze)//2]
    test_half = idxs[len(trialsToAnalyze)//2:]
    print(len(train_half))
    print(len(test_half))
    sacMetrics[np.isnan(sacMetrics)] = 0
    model = LinearRegression()
    model.fit(sacMetrics[train_half, :], unitActivity[train_half])
    predicted = model.predict(sacMetrics[test_half, :])
    weights = model.coef_
    scoreTrain = model.score(sacMetrics[train_half, :], unitActivity[train_half])
    scoreTest = model.score(sacMetrics[test_half, :], unitActivity[test_half])
    lowerCI, upperCI = calculate_confidence_interval(sacMetrics[test_half, :], unitActivity[test_half], model)
    return predicted, weights, lowerCI, upperCI, scoreTrain, scoreTest, test_half


def plotPredictedVSActual(predicted, actual, metric, color, min, max, fig=None, ax=None):
    """
    This makes a scatter plot of predicted vs actual values to visually evaluate prediction results
    """
    params = {'legend.fontsize': 15,
         'axes.labelsize': 20,
         'axes.titlesize':15,
         'xtick.labelsize':15,
         'ytick.labelsize':15}
    plt.rcParams.update(params)
    if fig is None:
        fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    if metric == 'amplitude':
        index = 0
    elif metric == 'start':
        index = 1
    elif metric == 'end':
        index = 2
    else:
        print("enter a real metric u silly person. check generateSaccadeMetric function if confused")
    ax.scatter(np.array(actual), predicted[:, index], color=color, alpha=0.5, s=7)
    ax.plot([min, max], [min, max], color='k')
    return fig, ax

def calculate_confidence_interval(X, y, model, alpha=0.05):
    """
    Calculates the confidence interval for linear regression coefficients.

    Args:
        X (numpy.ndarray): Feature matrix.
        y (numpy.ndarray): Target vector.
        model (sklearn.linear_model.LinearRegression): Fitted linear regression model.
        alpha (float, optional): Significance level. Defaults to 0.05.

    Returns:
        tuple: A tuple containing the lower and upper bounds of the confidence interval.
    """
    n = X.shape[0]
    p = X.shape[1]
    y_pred = model.predict(X)
    residuals = y - y_pred
    
    # Calculate the degrees of freedom
    df = n - p - 1
    
    # Calculate the mean squared error (MSE)
    mse = np.sum(residuals**2) / df
    
    # Calculate the standard errors of the coefficients
    xtx_inv = np.linalg.pinv(X.T @ X)
    se_coefficients = np.sqrt(np.diag(xtx_inv) * mse)
    
    # Calculate the t-value
    t_value = stats.t.ppf(1 - alpha/2, df)
    
    # Calculate the confidence intervals
    lower_bound = model.coef_ - t_value * se_coefficients
    upper_bound = model.coef_ + t_value * se_coefficients
    
    return lower_bound, upper_bound
    
