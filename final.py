"""
Sports Analytics
"""

import numeric
import codeskulptor
from urllib import request
import comp140_module6 as sports

def read_matrix(filename):
    """
    Parse data from the file with the given filename into a matrix.

    input:
        - filename: a string representing the name of the file

    returns: a matrix containing the elements in the given file
    """
    url = codeskulptor.file2url(filename)
    netfile = request.urlopen(url) 
    matrix_data = []
    for line in netfile.readlines():
        strline = line.decode('utf-8')
        fields = strline.split(",")
        row = []
        for num in fields:
            row.append(float(num))
        matrix_data.append(row)
    return numeric.Matrix(matrix_data)  

def mse(result, expected):
    """
    Calculate the mean squared error between two data sets.

    The length of the inputs, result and expected, must be the same.

    inputs:
        - result: a list of integers or floats representing the actual output
        - expected: a list of integers or floats representing the predicted output

    returns: a float that is the mean squared error between the two data sets
    """
    summate = 0
    for idx in range(len(result)):
        diff = (expected[idx] - result[idx]) ** 2
        summate += diff
    mean_squared_error = summate/len(result)
    return mean_squared_error

class LinearModel:
    """
    A class used to represent a Linear statistical
    model of multiple variables. This model takes
    a vector of input variables and predicts that
    the measured variable will be their weighted sum.
    """

    def __init__(self, weights):
        """
        Create a new LinearModel.

        inputs:
            - weights: an m x 1 matrix of weights
        """
        self._weights = weights

    def __str__(self):
        """
        Return: weights as a human readable string.
        """
        return str(self._weights)

    def get_weights(self):
        """
        Return: the weights associated with the model.
        """
        return self._weights

    def generate_predictions(self, inputs):
        """
        Use this model to predict a matrix of
        measured variables given a matrix of input data.

        inputs:
            - inputs: an n x m matrix of explanatory variables

        Returns: an n x 1 matrix of predictions
        """
        prediction_matrix = inputs @ self._weights
        return prediction_matrix

    def prediction_error(self, inputs, actual_result):
        """
        Calculate the MSE between the actual measured
        data and the predictions generated by this model
        based on the input data.

        inputs:
            - inputs: inputs: an n x m matrix of explanatory variables
            - actual_result: an n x 1 matrix of the corresponding
                             actual values for the measured variables

        Returns: a float that is the MSE between the generated
        data and the actual data
        """
        actual_list = []
        expected_list = []
        
        expected_matrix = self.generate_predictions(inputs)
        actual_column = actual_result.getcol(0)
        expected_column = expected_matrix.getcol(0)
        
        ex_column_dim = expected_column.shape()
        
        for loc in range(ex_column_dim[1]):
            element1 = expected_column[0, loc]
            expected_list.append(element1)
            element2 = actual_column[0, loc]
            actual_list.append(element2)
            
        return mse(actual_list, expected_list)
    
obj = LinearModel(numeric.Matrix([[1.0]]))


    
def fit_least_squares(input_data, output_data):
    """
    Create a Linear Model which predicts the output vector
    given the input matrix with minimal Mean-Squared Error.

    inputs:
        - input_data: an n x m matrix
        - output_data: an n x 1 matrix

    returns: a LinearModel object which has been fit to approximately
    match the data
    """
    square_matrix = input_data.transpose() @ input_data
    some_matrix = output_data.transpose() @ input_data @ square_matrix.inverse()

    return LinearModel(some_matrix.transpose())

def soft_threshold(exe, tee):
    """
    Intuitively, this function moves exe closer to zero by the distance tee.
    If this would move exe past zero, the value is simply zero.
    
    Inputs:
    x: some number
    tee: some number
    
    Return:
    some output
    """
    if exe >= tee:
        ans = exe - tee
    
    elif abs(exe) <= tee:
        ans = 0

    elif exe < (0-tee):
        ans = exe + tee
    return ans

def fit_lasso(param, iterations, input_data, output_data):
    """
    Create a Linear Model which predicts the output vector
    given the input matrix using the LASSO method.

    inputs:
        - param: a float representing the lambda parameter
        - iterations: an integer representing the number of iterations
        - input_data: an n x m matrix
        - output_data: an n x 1 matrix

    returns: a LinearModel object which has been fit to approximately
    match the data
    """
    weight = fit_least_squares(input_data, output_data).get_weights()
    x_inp = input_data
    x_trp = input_data.transpose()
    y_out = output_data
    xtx = x_trp @ x_inp
    itr = 0
    
    while itr < iterations:
        weight_old = weight.copy()
        for jth in range(x_inp.shape()[1]):
            a_j = ((x_trp @ y_out)[(jth, 0)] - ((xtx).getrow(jth) @ weight)[(0,0)])/(xtx)[(jth,jth)]
            b_j = param / (2*(xtx)[(jth,jth)])
            weight[(jth,0)] = soft_threshold((weight[(jth,0)] + a_j), b_j)
        if (weight - weight_old).abs().summation() < 1 / (10 **5):
            break
        itr = itr + 1
    return LinearModel(weight)

def run_experiment(iterations):
    """
    Using some historical data from 1954-2000, as
    training data, generate weights for a Linear Model
    using both the Least-Squares method and the
    LASSO method (with several different lambda values).

    Test each of these models using the historical
    data from 2001-2012 as test data.

    inputs:
        - iterations: an integer representing the number of iterations to use

    Print out the model's prediction error on the two data sets
    """
    #Converts files into matrices
    stats_1954 = read_matrix("comp140_analytics_baseball.txt")
    wins_1954 = read_matrix("comp140_analytics_wins.txt")
    stats_2001 = read_matrix("comp140_analytics_baseball_test.txt")
    wins_2001 = read_matrix("comp140_analytics_wins_test.txt")
    
    #Computes least_squares estimate for the weights
    least_squares_model_1954 = fit_least_squares(stats_1954, wins_1954)

 
    
    #Generates prediction errors using stats, weights, and actual results
    print("1954 Least-Squares Prediction Error for 1954: ")
    print(least_squares_model_1954.prediction_error(stats_1954, wins_1954))
    print("1954 Least-Squares Prediction Error for 2001: ")
    print(least_squares_model_1954.prediction_error(stats_2001, wins_2001))
    
    lambda1 = 5000
    lambda2 = 2500
    lambda3 = 7500
    
    #Computes LASSO estimate for the weights
    lasso_1_1954 = fit_lasso(lambda1, iterations, stats_1954, wins_1954)
    lasso_2_1954 = fit_lasso(lambda2, iterations, stats_1954, wins_1954)
    lasso_3_1954 = fit_lasso(lambda3, iterations, stats_1954, wins_1954)    
    
    
    #Generates prediction errors using stats, weights, and actual results
    print("1954 LASSO Prediction Error when lambda = 5000 for 1954: ")
    print(lasso_1_1954.prediction_error(stats_1954, wins_1954))
    print("1954 LASSO Prediction Error when lambda = 2500 for 1954: ")
    print(lasso_2_1954.prediction_error(stats_1954, wins_1954)) 
    print("1954 LASSO Prediction Error when lambda = 7500 for 1954: ")
    print(lasso_3_1954.prediction_error(stats_1954, wins_1954))
    print("1954 LASSO Prediction Error when lambda = 5000 for 2001: ")
    print(lasso_1_1954.prediction_error(stats_2001, wins_2001))
    print("1954 LASSO Prediction Error when lambda = 2500 for 2001: ")
    print(lasso_2_1954.prediction_error(stats_2001, wins_2001))
    print("1954 LASSO Prediction Error when lambda = 7500 for 2001: ")
    print(lasso_3_1954.prediction_error(stats_2001, wins_2001))
    
run_experiment(49)    
    
    
    
