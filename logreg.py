from numpy import *
import time


# calculate the sigmoid function
def sigmoid(inX):
    return 1.0 / (1 + exp(-inX))


# train a logistic regression model using some optional optimize algorithm
# input: train_x is a mat datatype, each row stands for one sample
#         train_y is mat datatype too, each row is the corresponding label
#         opts is optimize option include step and maximum number of iterations
def trainLogRegres(train_x, train_y, opts):
    # calculate training time
    startTime = time.time()

    numInstances = shape(train_x)[0]
    numSamples = shape(train_x[0])[0]
    numFeatures = [shape(x)[1] for x in train_x]
    alpha = opts['alpha']
    maxIter = opts['maxIter']
    _lambda = opts['lambda']
    weights = [ones((num, 1)) for num in numFeatures] # initial values of weights

    for i in range(numInstances):
        train_x[i] = train_x[i].reset_index()
        del train_x[i]['city']
        del train_x[i]['date']
        train_x[i] = train_x[i].as_matrix()

    # optimize through gradient descent algorithm
    for k in range(maxIter):
        print str(k) + " items"
        for L in range(len(weights)):  # languages
            for j in range(len(weights[L])):  # features
                print j
                start = time.clock()
                grad = 0
                for i in range(numSamples):  # one sample
                    fun1 = lambda _i: 1 + exp(dot(train_x[_i][i], weights[_i]))
                    num_list1 = range(numInstances)
                    num_list1.remove(L)

                    temp1 = reduce(lambda _x, _y: fun1(_x)*fun1(_y), num_list1)

                    num_list2 = range(numInstances)
                    temp2 = 1
                    for i in num_list2:
                        temp2 *= fun1(i)

                    grad += train_y[i]*(train_x[L][i][j] * exp(dot(train_x[L][i], weights[L])) * temp1)/(temp2 - 1) \
                            - exp(dot(train_x[L][i], weights[L])) * train_x[L][i][j] / (1+exp(dot(train_x[L][i], weights[L])))
                weights[L][j] += alpha * grad
                end = time.clock()
                print end - start

    print 'Congratulations, training complete! Took %fs!' % (time.time() - startTime)
    return weights


# test your trained Logistic Regression model given test set
def testLogRegres(weights, test_x, test_y):
    numSamples, numFeatures = shape(test_x)
    matchCount = 0
    for i in xrange(numSamples):
        predict = sigmoid(test_x[i, :] * weights)[0, 0] > 0.5
        if predict == bool(test_y[i, 0]):
            matchCount += 1
    accuracy = float(matchCount) / numSamples
    return accuracy
