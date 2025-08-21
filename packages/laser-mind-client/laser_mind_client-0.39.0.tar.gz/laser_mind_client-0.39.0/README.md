## LightSolver Client
The LightSolver Client is a Python package designed to interface with the LightSolver Cloud Platform to facilitate solving problems on LightSolver's LPU (Laser Processing Unit) and dLPU (digital-LPU) solvers.

This package is designated for early access to features during the development process and serves as a prototype for future versions of the production LightSolver Client.

## Features
- **QUBO DLPU Problem Solving:** The `solve_qubo` function accepts a QUBO problem, represented either as a 2D array (matrix) or an adjacency list, and returns the solution using the dLPU.
- **Synchronous and Asynchronous Operation:** Users can choose between blocking (synchronous) and non-blocking (asynchronous) modes during problem solving.
- **Fetching Account Details:** Account information is available through this client. Includes: email, dLPU solve time remaining, dLPU variable count ("spin") limit and the user's expiration date.
- **Flexible Installation:** Compatible with both Windows and MacOS systems.
- **LPU Solvers:** Dedicated methods for solving problems on the Laser Processing Unit (LPU):
  - `solve_qubo_lpu`: Solves QUBO problems on the LPU
  - `solve_coupling_matrix_lpu`: Solves coupling matrix problems on the LPU

### Solve QUBO DLPU
The `solve_qubo` function solves QUBO problems, either represented by a 2D array (matrix) or by an adjacency list, over the dLPU. For code samples, see the /tests directory.

#### Input Matrix Validity
- The matrix must be square.
- The matrix supports int or float cell values.

#### Return Value
A dictionary with the following fields:
```
- 'id': Unique identifier of the solution.
- 'solution': The solution as a Python list() of 1s and 0s.
- 'objval: The objective value of the solution.
- 'solverRunningTime': Time spent by the solver to calculate the problem.
- 'receivedTime': Timestamp when the request was received by the server.
```

### Solve QUBO LPU
The `solve_qubo_lpu` function solves QUBO problems on the Laser Processing Unit (LPU).

#### Input Requirements
- Matrix dimensions must be between 5x5 and 100x100
- Problem can be specified using one of these parameters:
  - `matrixData`: A 2D array (matrix) of int or float values
  - `edgeList`: An adjacency list in the format `[[i, j, value], ...]` where:
    - `i`, `j`: Node indices (1-based)
    - `value`: Weight of the connection between nodes i and j
- The matrix must be symmetric (will be symmetrized if not)

#### Additional Parameters
- `num_runs`: Number of times to run the solver (default: 1)
- `waitForSolution`: Whether to wait for the solution (default: True). When False, the function will return immediately with a token object, allowing the script to continue while the server processes the QUBO problem.

#### Return Value
A dictionary containing:
```
- 'command': The solver command type ('LPU')
- 'data': A dictionary containing:
  - 'solutions': A list of solution dictionaries, one per run, each containing:
    - 'solution': The solution as a list of binary values
    - 'objval': The objective value of the solution
    - 'solverRunningTime': Time spent calculating the solution on the LPU
  - 'solution_warnings': (optional) Warning message, for example, if the problem is at the performance boundary of the LPU
- 'creation_time': Timestamp when the result was created
- 'reqTime': Timestamp when the request arrived at the server
- 'id': Unique identifier for this request
- 'userId': ID of the requesting user
- 'receivedTime': Timestamp when the request was received by the server
```

### Solve Coupling Matrix LPU
The `solve_coupling_matrix_lpu` function solves coupling matrix problems on the LPU.

#### Input Matrix Requirements
- Must be a numpy array of type `numpy.complex64`
- Matrix dimensions must be between 5x5 and 100x100
- The matrix represents coupling strengths between lasers

#### Return Value
A dictionary containing:
```
- 'command': The solver command type ('LPU')
- 'data': A dictionary containing:
  - 'solutions': A list of solution dictionaries, one per run, each containing:
    - 'phase_problem': List of phase differences between nodes
    - 'energy_problem': List of energy values for the solution
    - 'contrast_problem': List of contrast measures for the solution
    - 'solverRunningTime': Time spent calculating the solution on the LPU
  - 'warnings': (optional) Dictionary containing measurements that could indicate a problematic solution, for example:
    - 'Contrast reference': Contrast of laser pairs in the reference run
    - 'Energy reference': List of laser pair energy values in the reference run
    - 'Contrast problem': Contrast of laser pairs in the problem run
    - 'Energy problem': List of laser pair energy values in the problem run
- 'creation_time': Timestamp when the result was created
- 'reqTime': Timestamp when the request arrived at the server
- 'id': Unique identifier for this request
- 'userId': ID of the requesting user
- 'receivedTime': Timestamp when the request was received by the server
```


### Synchronous and Asynchronous Usage
- **Synchronous Mode (Default):** The `waitForSolution` flag is set to **True** by default. The function blocks operations until a result is received.
- **Asynchronous Mode:** Set `waitForSolution` to **False**. The function returns immediately with a token object, allowing the script to continue while the server processes the QUBO problem.

### Fetching Account Details
The `get_account_details()` function returns a python dictionary containing the following keys:
```
- 'dlpu_spin_limit': an int indicating the largest matrix size the user can send to the dlpu (dimensions of dlpu_spin_limit X dlpu_spin_limit).
- 'username': the username / email associated with this user. String.
- 'expiration_date: an Epoch timestamp indicating when the user expires. Int.
- 'dlpu_credit_seconds': solve time remaining for the user. Float.
```

## Setting Up

### Prerequisites
- Operating System: MacOS or Windows 11.
- Valid token for connecting to the LightSolver Cloud (provided separately).
- Python 3.10 or higher ([Download Here](https://www.python.org/downloads/release/python-31011/)).
    - Select the appropriate MacOS/Windows version at the bottom.
    - Note: for Windows installation, switch on the "Add to Path" option in the wizard.
- Highly Recommended: Use a virtual environment before installing laser-mind-client (Please see detailed action further below under the relevant OS).

### Installation
Complete the installation on Windows or MacOS as described below.
For further assistance with setup or connection issues, contact support@lightsolver.com.

#### Windows
1. Press the windows key, type "cmd", and select "Command Prompt".

2. Navigate to the root folder of the project where you plan to use the LightSolver Client:
```sh
    cd <your project folder>
```

3. (Recommended) Create and activate the virtual environment:
```sh
    python -m venv .venv
    .venv\Scripts\activate
```

4. Install the laser-mind-client package:
```sh
    pip install laser-mind-client
```

5. (Recommended) Test using one of the provided test examples. Under the above project folder unzip "lightsolver_onboarding.zip."
```sh
    cd lightsolver_onboarding
    open test_solve_qubo_matrix.py file for edit
    enter the provided TOKEN in line 6 (userToken = "<my_token>")
    python ./tests/test_solve_qubo_matrix.py
```


#### MacOS
1. Open new terminal window.

2. Navigate to the root folder of the project where you plan to use the LightSolver Client:
```sh
    cd <your project folder>
```

3. (Recommended) Create and activate the virtual environment:
```sh
    python3 -m venv .venv
    chmod 755  .venv/bin/activate
    source .venv/bin/activate
```

4. Install the laser-mind-client package.
```sh
    pip install laser-mind-client
```

8. (Recommended) Test using one of the provided test examples. Under the above project folder unzip "lightsolver_onboarding.zip."
```sh
    cd lightsolver_onboarding
    open test_solve_qubo_matrix.py file for edit
    enter the provided TOKEN in line 6 (userToken = "<my_token>")
    python3 ./tests/test_solve_qubo_matrix.py
```

***
## Authentication
Initialization of the `LaserMind` class automatically forms a secure and authenticated connection with the LightSolver Cloud.
Subsequent calls by the same user are similarly secure and authenticated.

## Usage
To begin solving any QUBO problem:
1. Create an instance of the ```LaserMind``` class. This class represents the client that requests solutions from the LightSolver Cloud.
2. By default, all logs are printed to laser-mind.log file in current directory and to console. Output to console can be disabled by setting ```logToConsole=False```
3. Call the ```solve_qubo``` function using either a matrix or an adjacency list.
**Note:** You may either provide a value for ```matrixData``` or for ```edgeList```, but not both.

### Error Handling
All functions in the LightSolver Client will raise exceptions when errors occur. These exceptions include:
- Connection errors (e.g., "No access to LightSolver Cloud")
- Input validation errors (e.g., invalid matrix dimensions)
- Internal server errors

It's recommended to wrap API calls in try-except blocks to handle potential errors gracefully:
```python
try:
    result = client.solve_coupling_matrix_lpu(matrixData=coupling_matrix)
except Exception as e:
    print(f"Error solving problem: {str(e)}")
```

## Examples
Find examples of every feature in laser-mind-client under the "tests/" directory.
