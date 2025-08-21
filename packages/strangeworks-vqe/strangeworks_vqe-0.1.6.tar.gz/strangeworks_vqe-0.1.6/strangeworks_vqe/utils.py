import networkx as nx
import numpy as np
from qiskit.algorithms import NumPyMinimumEigensolver
from qiskit.opflow import I, X, Y, Z


def get_Heisenberg_PauliSumOp(nqubits, Jz, Jxy):
    Ham = None
    for nn in range(nqubits - 1):
        if nn == 0:
            temp_z = Z
            temp_x = X
            temp_y = Y
        else:
            temp_z = I
            temp_x = I
            temp_y = I

        for pp in range(0, nn - 1):
            temp_z = temp_z ^ I
            temp_x = temp_x ^ I
            temp_y = temp_y ^ I

        if nn != 0:
            temp_z = temp_z ^ Z
            temp_x = temp_x ^ X
            temp_y = temp_y ^ Y
        temp_z = temp_z ^ Z
        temp_x = temp_x ^ X
        temp_y = temp_y ^ Y

        for pp in range(nn + 1, nqubits - 1):
            temp_z = temp_z ^ I
            temp_x = temp_x ^ I
            temp_y = temp_y ^ I

        if Ham is None:
            Ham = Jz * temp_z + Jxy * (temp_x + temp_y)
        else:
            Ham = Ham + Jz * temp_z + Jxy * (temp_x + temp_y)

    return Ham


def get_Ham_from_graph(G):
    Ham = []
    for nn in list(G.nodes()):
        try:
            G.nodes[nn]["weight"]
        except NameError:
            # if not specified, node weights will be considered zero
            G.nodes[nn]["weight"] = 0

        if G.nodes[nn]["weight"] != 0:
            if nn == 0:
                temp = "Z"
            else:
                temp = "I"

            for pp in range(0, nn - 1):
                temp = temp + "I"

            if nn != 0:
                temp = temp + "Z"

            for pp in range(nn, len(G.nodes()) - 1):
                temp = temp + "I"

            Ham.append((G.nodes[nn]["weight"], temp, nn))

    for pair in list(G.edges()):
        try:
            G.edges[pair]["weight"]
        except NameError:
            # if not specified, edge weight will be set equal to 1.0
            G.edges[pair]["weight"] = 1.0

        if pair[0] == 0:
            temp = "Z"
        else:
            temp = "I"

        for pp in range(0, pair[0] - 1):
            temp = temp + "I"

        if pair[0] != 0:
            temp = temp + "Z"

        for pp in range(pair[0], pair[1] - 1):
            temp = temp + "I"

        temp = temp + "Z"

        for pp in range(pair[1], len(G.nodes()) - 1):
            temp = temp + "I"

        Ham.append((G.edges[pair]["weight"], temp, pair))

    return Ham


def get_Ham_from_PauliSumOp(H_pauliSum):
    Ham = []
    for nn in range(len(H_pauliSum._primitive)):
        op_str = str(H_pauliSum._primitive[nn]._pauli_list[0])

        pair = []
        for ll in range(len(op_str)):
            if op_str[ll] == "Z":
                pair.append(ll)

        if len(pair) > 1:
            pair = tuple(pair)
        else:
            pair = pair[0]

        Ham.append((np.real(H_pauliSum._primitive[nn]._coeffs[0]), op_str, pair))

    return Ham


def get_Ham_from_QUBO(QUBO_mat):
    nodes = np.size(QUBO_mat[0])

    Ham = []
    for nn in range(nodes):
        if QUBO_mat[nn][nn] != 0:
            if nn == 0:
                temp = "Z"
            else:
                temp = "I"

            for pp in range(0, nn - 1):
                temp = temp + "I"

            if nn != 0:
                temp = temp + "Z"

            for pp in range(nn, len(QUBO_mat) - 1):
                temp = temp + "I"

            Ham.append((QUBO_mat[nn][nn], temp, nn))

    for p1 in range(nodes):
        for p2 in range(p1 + 1, nodes):
            if np.abs(QUBO_mat[p1][p2]) > 1e-5:
                if p1 == 0:
                    temp = "Z"
                else:
                    temp = "I"

                for pp in range(0, p1 - 1):
                    temp = temp + "I"

                if p1 != 0:
                    temp = temp + "Z"

                for pp in range(p1, p2 - 1):
                    temp = temp + "I"

                temp = temp + "Z"

                for pp in range(p2, nodes - 1):
                    temp = temp + "I"

                pair = tuple([p1, p2])
                Ham.append((QUBO_mat[p1][p2], temp, pair))

    return Ham


def convert_QUBO_to_Ising(QUBO_mat):
    nodes = np.size(QUBO_mat[0])
    Ising_mat = QUBO_mat / 4

    for nn in range(nodes):
        Ising_mat[nn][nn] = QUBO_mat[nn][nn] / 2 + sum(
            QUBO_mat[nn][nn + 1 :] / 4  # noqa: E203
        )

    for nn in range(nodes):
        Ising_mat[nn][nn] += sum(QUBO_mat[:nn, nn] / 4)

    return Ising_mat


def get_graph_from_Ham(H):
    G = nx.Graph()
    for nn in range(len(H)):
        Num_z = H[nn][1].count("Z")
        if Num_z > 2:
            print(
                """Error: cannot create networkX graph.
                Hamiltonian has more than pairwise connections"""
            )
        elif Num_z == 1:
            ind = H[nn][1].find("Z")
            G.add_nodes_from([(ind, {"weight": H[nn][0]})])
        else:
            G.add_edges_from([(H[nn][2][0], H[nn][2][1], {"weight": H[nn][0]})])

    return G


def get_PauliSumOp_from_Ham(H):
    Ham = None

    for nn in range(len(H)):
        if H[nn][1][0] == "Z":
            temp = 2 * Z + I
        else:
            temp = I
        for mm in range(1, len(H[nn][1])):
            if H[nn][1][mm] == "Z":
                temp = temp ^ 2 * Z + I
            else:
                temp = temp ^ I

        if Ham is None:
            Ham = H[nn][0] * temp
        else:
            Ham = Ham + H[nn][0] * temp

    return Ham


def get_exact_en(H, nodes):
    if nodes > 24:
        Egs_exact = "!!problem too big for exact solution!!"
    else:
        Egs_exact = NumPyMinimumEigensolver().compute_minimum_eigenvalue(H).eigenvalue

    return np.real(Egs_exact)
