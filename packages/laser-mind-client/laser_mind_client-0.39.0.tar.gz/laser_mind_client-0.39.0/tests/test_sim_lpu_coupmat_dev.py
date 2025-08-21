import numpy
from laser_mind_client import LaserMind

userToken = "<TOKEN>"
size4 = 4
coupMat4 = 0.5 * numpy.eye( size4 ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size4 - 1):
    coupMat4[i,i+1] = coupling
    coupMat4[i+1,i] = coupling

size6 = 6
coupMat6 = 0.5 * numpy.eye( size6 ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size6 - 1):
    coupMat6[i,i+1] = coupling
    coupMat6[i+1,i] = coupling

size25 = 25
coupMat25 = 0.5 * numpy.eye( size25 ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size25 - 1):
    coupMat25[i,i+1] = coupling
    coupMat25[i+1,i] = coupling


size50 = 50
coupMat50 = 0.5 * numpy.eye( size50 ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size50 - 1):
    coupMat50[i,i+1] = coupling
    coupMat50[i+1,i] = coupling

size300 = 300
coupMat300 = 0.5 * numpy.eye( size300 ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size300 - 1):
    coupMat300[i,i+1] = coupling
    coupMat300[i+1,i] = coupling

size1000 = 1000
coupMat1000 = 0.5 * numpy.eye( size1000 ,dtype=numpy.complex64)
coupling = (1-0.5)/(2)
for i in range(size1000 - 1):
    coupMat1000[i,i+1] = coupling
    coupMat1000[i+1,i] = coupling

def test_solve_coupmat_sanity_sim_lpu_spin_unlimited():
    # matrix in range , but not allowed for default user
    lsClient = LaserMind(userToken)
    res = lsClient.solve_coupling_matrix_sim_lpu(matrix_data = coupMat6, num_runs=3, num_iterations=10,rounds_per_record=5)
    print(res)

    assert 'data' in res
    assert  'result' in res['data']
    assert  'start_states'   in res['data']['result']
    assert  'final_states' in res['data']['result']
    assert  'record_states' in res['data']['result']
    assert  'record_gains' in res['data']['result']


def test_solve_coupmat_sanity_1000_sim_lpu_spin_unlimited():
    # matrix in range , but not allowed for default user
    lsClient = LaserMind(userToken)
    res = lsClient.solve_coupling_matrix_sim_lpu(matrix_data = coupMat1000, num_runs=1, num_iterations=100, rounds_per_record=10)
    print(res)

    assert 'data' in res
    assert  'result' in res['data']
    assert  'start_states'   in res['data']['result']
    assert  'final_states' in res['data']['result']
    assert  'record_states' in res['data']['result']
    assert  'record_gains' in res['data']['result']


def test_solve_coupmat_sanity_sim_lpu_spin_unlimited_start_state():
    # matrix in range , but not allowed for default user
    lsClient = LaserMind(userToken)
    start_states =  [[ 1.0000000e+00+0.0000000e+00j,  3.1520671e-05-6.6747067e-05j,
         3.2637545e-04+1.3825409e-05j,  6.6705397e-04+5.1987998e-04j,
        -1.7934688e-04-9.9081466e-05j, -7.9448699e-05+2.8152767e-04j],
       [ 1.0000000e+00+0.0000000e+00j, -1.3137888e-05-8.1989256e-06j,
         4.2760934e-04+7.6702039e-04j, -3.0936502e-04+3.0431763e-04j,
        -4.6269799e-04-6.0939678e-04j,  4.1850499e-04+4.3996374e-04j],
       [ 1.0000000e+00+0.0000000e+00j,  3.3563105e-04+2.8073095e-04j,
         5.0876173e-04+2.1346097e-04j, -6.1887660e-04+6.3852035e-04j,
        -2.2033586e-04+6.9595524e-04j,  3.9103298e-04+8.9563327e-05j]]

    # Convert it
    start_states_array = numpy.array(start_states, dtype=numpy.complex64)

    res = lsClient.solve_coupling_matrix_sim_lpu(matrix_data = coupMat6, initial_states_vector=start_states_array, num_iterations=10,rounds_per_record=5)
    print(res)

    assert 'data' in res
    assert  'result' in res['data']
    assert  'start_states'   in res['data']['result']
    assert  'final_states' in res['data']['result']
    assert  'record_states' in res['data']['result']
    assert  'record_gains' in res['data']['result']

def test_solve_coupmat_sanity_sim_lpu_spin_unlimited_gain_info():
    # matrix in range , but not allowed for default user
    lsClient = LaserMind(userToken)
    res = lsClient.solve_coupling_matrix_sim_lpu(matrix_data = coupMat6,
                                                 num_runs=1,
                                                 num_iterations=2,
                                                 rounds_per_record=1,
                                                 gain_info_initial_gain = 1.9 ,
                                                 gain_info_pump_max = 3 ,
                                                 gain_info_pump_tau = 700.0 ,
                                                 gain_info_pump_treshold = 1.8 ,
                                                 gain_info_amplification_saturation = 1.0 )
    print(res)

    assert 'data' in res
    assert  'result' in res['data']
    assert  'start_states'   in res['data']['result']
    assert  'final_states' in res['data']['result']
    assert  'record_states' in res['data']['result']
    assert  'record_gains' in res['data']['result']