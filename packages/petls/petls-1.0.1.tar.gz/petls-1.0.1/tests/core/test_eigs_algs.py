import petls
import numpy as np
import scipy
import pytest

def compare_spectra(ref, test):
    print(f"compare {ref} to {test}") # only actually prints if assert fails in pytest
    if ref[0] != test[0] or ref[1] != test[1] or ref[2] != test[2]:
        return False
    assert ref[3] == pytest.approx(test[3])

def compare_spectra_multiple(ref, test):
    for i in range(len(ref)):
        compare_spectra(ref[i],test[i])


def get_pl(alg = "eigvalsh"):
    d1 = np.array([[-1,0,-1],
                [1,-1,0],
                [0,1,1]])
    d2 = np.array([[1],[1],[-1]])
    boundaries = [d1,d2]
    filtrations = [[0,1,2],[3,4,5],[5]]

    pl = petls.Complex(boundaries, filtrations, eigs_Algorithm=alg)
    return pl

def test_specific():
    pl = get_pl()
    assert pl.spectra(1,4,5) == pytest.approx([1,3])

    pl2 = get_pl(alg = "bdcsvd")
    assert pl2.spectra(1,4,5) == pytest.approx([1,3])

    pl3 = get_pl(alg = "eigensolver")
    assert pl3.spectra(1,4,5) == pytest.approx([1,3])

def test_all():
    pl = get_pl("selfadjoint")
    s = pl.spectra()
    expected = [
        (0, 0, 3, np.array([0])),
        (1, 0, 3, np.array([])),
        (2, 0, 3, np.array([])),
        (0, 3, 4, np.array([0, 1, 3])),
        (1, 3, 4, np.array([2])),
        (2, 3, 4, np.array([])),
        (0, 4, 5, np.array([0, 3, 3])),
        (1, 4, 5, np.array([1, 3])),
        (2, 4, 5, np.array([])),
        (0, 5, 5, np.array([0, 3, 3])),
        (1, 5, 5, np.array([3, 3, 3])),
        (2, 5, 5, np.array([3]))
    ]
    pl.store_L(1,4,5,"myprefix")
    compare_spectra_multiple(expected, s)
    

if __name__ == "__main__":
    test_all()
    test_specific()