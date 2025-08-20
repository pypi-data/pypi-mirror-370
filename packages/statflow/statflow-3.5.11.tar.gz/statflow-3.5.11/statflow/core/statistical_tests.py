#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np
import scipy.stats as ss

#------------------#
# Define functions #
#------------------#

# Hypothesis tests #
#------------------#

def z_test_two_means(data1: np.ndarray, data2: np.ndarray, alpha: float = 0.05) -> tuple[float, float, str]:
    """
    Performs a Z-test for comparing the means of two independent samples.
    
    The Z-test is used when the population variances are known or the sample sizes are large.
    
    Parameters
    ----------
    data1 : array-like
        First sample of data.
    data2 : array-like
        Second sample of data.
    alpha : float, optional, default=0.05
        Significance level for the test. Default is 0.05 for a 95% confidence interval.
        
    Returns
    -------
    z_stat : float
        The computed Z-statistic.
    p_value : float
        The two-tailed p-value associated with the Z-statistic.
    result : str
        The conclusion of the hypothesis test (reject or fail to reject the null hypothesis).
    
    Notes
    -----
    This test assumes that the data follows a normal distribution. For smaller sample sizes,
    it may be preferable to use a T-test instead.
    """
    
    mean1 = np.mean(data1)
    mean2 = np.mean(data2)
    n1, n2 = len(data1), len(data2)
    
    # Standard deviations
    std1 = np.std(data1, ddof=1)
    std2 = np.std(data2, ddof=1)
    
    # Pooled standard error
    se = np.sqrt((std1**2 / n1) + (std2**2 / n2))
    
    # Z-statistic
    z_stat = (mean1 - mean2) / se
    
    # Two-tailed p-value
    p_value = 2 * (1 - ss.norm.cdf(abs(z_stat)))
    
    # Hypothesis test conclusion
    if p_value < alpha:
        result = "Reject the null hypothesis (means are significantly different)"
    else:
        result = "Fail to reject the null hypothesis (means are not significantly different)"
    
    return z_stat, p_value, result



def chi_squared_test(contingency_table: np.ndarray, alpha: float = 0.05) -> tuple[float, float, int, np.ndarray, str]:
    """
    Performs a Chi-squared test for independence on a contingency table.
    
    This test checks if two categorical variables are independent of each other.
    
    Parameters
    ----------
    contingency_table : array-like
        A 2D table containing the observed frequencies for the categories of the variables.
    alpha : float, optional, default=0.05
        Significance level for the test. Default is 0.05.
        
    Returns
    -------
    chi2 : float
        The computed Chi-squared statistic.
    p_value : float
        The p-value for the test.
    dof : int
        Degrees of freedom for the test.
    expected : np.ndarray
        The expected frequencies based on the marginal totals.
    result : str
        Conclusion of the hypothesis test (reject or fail to reject the null hypothesis).
    
    Notes
    -----
    The Chi-squared test is used to determine whether there is a significant association
    between two categorical variables.
    """
    
    chi2, p_value, dof, expected = ss.chi2_contingency(contingency_table)
    
    # Hypothesis test conclusion
    if p_value < alpha:
        result = "Reject the null hypothesis (variables are dependent)"
    else:
        result = "Fail to reject the null hypothesis (variables are independent)"
    
    return chi2, p_value, dof, expected, result

