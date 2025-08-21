####################################################################################################
# This example creates a QUBO matrix and solves it using the LPU over LightSolver's platform.
# The `solve_qubo` function is used with the following parameters:
# - `matrixData`: A 2D array representing the QUBO problem.
# - `timeout`: The required time limit for the calculation in seconds.
####################################################################################################

import numpy
from laser_mind_client import LaserMind

# Enter your TOKEN here
userToken = "<TOKEN>"

# Create a mock QUBO problem
quboProblemData = numpy.random.randint(-1, 2, (10,10))

# Symmetrize our matrix
quboProblemData = (quboProblemData + quboProblemData.T) // 2

# Connect to the LightSolver Cloud
lsClient = LaserMind(userToken=userToken)

# Request a LPU solution to the QUBO problem
res = lsClient.solve_qubo_lpu(matrixData = quboProblemData)

# Verify response format
assert 'command' in res, "Missing 'command' field"
assert 'data' in res, "Missing 'data' field"
assert 'solutions' in res['data'], "Missing 'solutions' field"

print(f"Test PASSED, response is: \n{res}")
