####################################################################################################
# This example solves a QUBO matrix using the dLPU over LightSolver's platform.
# The `solve_qubo_lpu` function is used with the following parameters:
# - `matrixData`: A 2D array representing the QUBO problem.
# - `num_runs`: The required number or calculation runs, default 1.
####################################################################################################
import numpy
from laser_mind_client_meta import MessageKeys
from laser_mind_client import LaserMind

# Enter your TOKEN here
userToken = "<TOKEN>"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize the matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=userToken)

res = lsClient.solve_qubo(matrixData = quboProblemData, timeout=1)

assert MessageKeys.SOLUTION in res, "Test FAILED, response is not in expected format"

print(f"Test PASSED, response is: \n{res}")