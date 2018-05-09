"""
April 2018
Simulates the trajectory implementing a CZ gate.
"""
import numpy as np
import qutip as qtp

alpha_q0 = 250e6 * 2*np.pi
w_q0 = 6e9  * 2 * np.pi  # Lower frequency qubit
w_q1 = 7e9  * 2 * np.pi  # Upper frequency (fluxing) qubit

J  = 2.5e6 * 2 * np.pi  # coupling strength

tlist = np.arange(0, 250e-9, .05e-9)
# operators
b  = qtp.tensor(qtp.destroy(2), qtp.qeye(3))  # LSB is static qubit
a = qtp.tensor(qtp.qeye(2), qtp.destroy(3))

n_q0 = a.dag() * a
n_q1 = b.dag() * b

# Hamiltonian
def coupled_transmons_hamiltonian(w_q0, w_q1, alpha_q0, J):
    """
    Hamiltonian of two coupled anharmonic resonators.
    Because the intention is to tune one qubit into resonance with the other,
    the number of levels is limited.
        q1 -> fluxing qubit, 2-levels
        q0 -> static qubit, 3-levels

    intended avoided crossing:
        11 <-> 02

    N.B. the frequency of q1 is expected to be larger than that of q0
        w_q1 > w_q1
    """

    H_0 =   w_q0 * n_q0 + w_q1 * n_q1 +  \
       1/2*alpha_q0*(a.dag()*a.dag()*a*a) +\
        J * (a.dag() + a) * (b + b.dag())
    return H_0

H_0 = coupled_transmons_hamiltonian(w_q0 =w_q0, w_q1=w_q1, alpha_q0=alpha_q0,
                                    J=J)

#
U_target = qtp.Qobj([[1, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0],
                                [0, 0, -1, 0, 0, 0],
                                [0, 0, 0, 1, 0, 0],
                                [0, 0, 0, 0, -1, 0],
                                [0, 0, 0, 0, 0, 1]],
                               type='oper',
                               dims=[[2, 3], [3, 2]])
U_target._type = 'oper'

def rotating_frame_transformation(U, t: float,
                                  w_q0: float=0, w_q1:float =0):
    """
    Transforms the frame of the unitary according to
        U' = U_{RF}*U*U_{RF}^dag
    with
        U_{RF} = e^{-i w_q0 a^dag a t } otimes e^{-i w_q1 b^dag b t }

    Args:
        U (QObj): Unitary to be transformed
        t (float): time at which to transform
        w_q0 (float): freq of frame for q0
        w_q1 (float): freq of frame for q1

    """
    U_RF =   (1j*w_q0*n_q0*t).expm() * (1j*w_q1*n_q1*t).expm()

    U_prime = U_RF * U #* U_RF(t=0).dag()
    return  U_prime

def phases_from_unitary(U):
    """
    Returns the phases from the unitary
    """
    phi_00 = np.rad2deg(np.angle(U[0, 0])) # expected to equal 0
    phi_01 = np.rad2deg(np.angle(U[1, 1]))
    phi_10 = np.rad2deg(np.angle(U[3, 3]))
    phi_11 = np.rad2deg(np.angle(U[4, 4]))

    phi_cond = (phi_11 - phi_01 - phi_10 - phi_00)%360

    return phi_00, phi_01, phi_10, phi_11, phi_cond




def pro_fid_unitary_compsubspace(U, U_target):
    # TODO: verify if this is correct (it seems correct)
    """
    Process fidelity in the computational subspace for a qubit and qutrit


    """
    inner = U.dag()*U_target
    part_idx = [0, 1, 3, 4]  # only computational subspace
    ptrace = 0
    for i in part_idx:
        ptrace += inner[i, i]
    dim = 4  # 2 qubits comp subspace

    return ptrace/dim

def leakage_from_unitary(U):
    """
    Calculates leakage by summing over all in and output states in the
    computational subspace.
        L1 = 1- sum_i sum_j abs(|<phi_i|U|phi_j>|)**2
    """
    sump = 0
    for i in range(4):
        for j in range(4):
            bra_i = qtp.tensor(qtp.ket([i//2], dim=[2]),
                               qtp.ket([i%2], dim=[3])).dag()
            ket_j = qtp.tensor(qtp.ket([j//2], dim=[2]),
                               qtp.ket([j%2], dim=[3]))
            p = np.abs((bra_i*U*ket_j).data[0,0])**2
            sump += p
    sump/=4 # divide by dimension of comp subspace
    L1 = 1-sump
    return L1

def seepage_from_unitary(U):
    """
    Calculates leakage by summing over all in and output states in the
    computational subspace.
        L1 = 1- sum_i sum_j abs(|<phi_i|U|phi_j>|)**2
    """
    sump = 0
    for i in range(2):
        for j in range(2):
            bra_i = qtp.tensor(qtp.ket([i], dim=[2]),
                               qtp.ket([2], dim=[3])).dag()
            ket_j = qtp.tensor(qtp.ket([j], dim=[2]),
                               qtp.ket([2], dim=[3]))
            p = np.abs((bra_i*U*ket_j).data[0,0])**2
            sump += p
    sump/=2 # divide by dimension of comp subspace
    L1 = 1-sump
    return L1

def pro_fid__from_unitary(U, U_target):
    """
    i and j sum over the states that span the full computation subspace.
        F = sum_i sum_j abs(|<phi_i| U^dag * U_t |phi_j>|)**2

    """

    psi_0 = qtp.ket([0])
    psi_1 = qtp.ket([1])
    psi_x = 1/np.sqrt(2)*(psi_0+psi_1)
    psi_mx = -1/np.sqrt(2)*(psi_0+psi_1)
    psi_y = 1/np.sqrt(2)*(psi_0-psi_1)
    psi_my = -1/np.sqrt(2)*(psi_0-psi_1)



    inner = U.dag()*U_target

    # part_idx = [0, 1, 3, 4]  # only computational subspace
    # ptrace = 0
    # for i in part_idx:
    #     ptrace += inner[i, i]
    # dim = 4  # 2 qubits comp subspace

    # return ptrace/dim



# Plts the output unitary
# qtp.hinton(U_outp)
