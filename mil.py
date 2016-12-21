import numpy as np
import scipy.optimize as opt
from datetime import datetime


def cost(theta, X, y):
    nfeatures = [x.shape[1] for x in X]
    flags = [nfeatures[0], nfeatures[0] + nfeatures[1]]
    X_1, X_2, X_3 = X[0], X[1], X[2]
    theta_1, theta_2, theta_3 = np.matrix(theta[:flags[0]]), np.matrix(theta[flags[0]:flags[1]]), np.matrix(theta[flags[1]:])

    temp1 = np.array(1+np.exp(X_1*theta_1.T))
    temp2 = np.array(1+np.exp(X_2*theta_2.T))
    temp3 = np.array(1+np.exp(X_3*theta_3.T))
    score = - np.sum(np.array(y) * np.array(np.log(temp1*temp2*temp3-1)) - np.log(temp1) - np.log(temp2) - np.log(temp3))
    print score
    return score


def gradient(theta, X, y):
    nfeatures = [x.shape[1] for x in X]
    flags = [nfeatures[0], nfeatures[0] + nfeatures[1]]
    theta_s = [np.matrix(theta[:flags[0]]), np.matrix(theta[flags[0]:flags[1]]), np.matrix(theta[flags[1]:])]

    parameters = len(theta)
    grad = np.zeros(parameters)

    ii = 0

    for L in range(3):  # languages
        l_rest = range(3)
        l_rest.remove(L)
        for j in range(nfeatures[L]):  # features
            temp_parts = [1 + np.exp(X[0] * theta_s[0].T), 1 + np.exp(X[1] * theta_s[1].T), 1 + np.exp(X[2] * theta_s[2].T)]
            temp_parts = [np.array(part) for part in temp_parts]
            temp_1 = np.array(X[L][:, j]) * temp_parts[L] * reduce(lambda _x, _y: temp_parts[_x]*temp_parts[_y], l_rest)
            temp_2 = temp_parts[0]*temp_parts[1]*temp_parts[2] - 1
            temp_3 = np.divide((temp_parts[L] - 1)*np.array(X[L][:, j]), temp_parts[L])
            grad[ii] = np.sum(np.divide(np.array(y) * np.array(temp_1), np.array(temp_2)) - np.array(temp_3))
            ii += 1
    return -grad


def train_mil(X, y):
    theta = np.matrix(np.ones((sum([x.shape[1] for x in X]))))
    # result = opt.fmin_tnc(func=cost, x0=theta, fprime=gradient, args=(X, y))
    result = opt.fmin_l_bfgs_b(func=cost, x0=theta, fprime=gradient, args=(X, y))
    print "final score: " + str(cost(result[0], X, y))
    print result[0]
    return result[0]
