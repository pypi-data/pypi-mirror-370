import pytest
import numpy as np
from unitforge import *
from unitforge.unitforge import DistanceUnit, Force, ForceUnit, StressUnit, ForceDistanceUnit


def test_vector_missmatch():
    with pytest.raises(ValueError, match="The passed values must be of the same quantity."):
        _ = Vector3(1.4, 1.3, Force(9, ForceUnit.N))

def test_vector_zero():
    vec = Vector3.zero()
    assert vec[0] == 0.
    assert vec[1] == 0.
    assert vec[2] == 0.

def test_vector_x():
    vec = Vector3.x()
    assert vec[0] == 1.
    assert vec[1] == 0.
    assert vec[2] == 0.

def test_vector_y():
    vec = Vector3.y()
    assert vec[0] == 0.
    assert vec[1] == 1.
    assert vec[2] == 0.

def test_vector_y():
    vec = Vector3.z()
    assert vec[0] == 0.
    assert vec[1] == 0.
    assert vec[2] == 1.

def test_vector_set():
    vec = Vector3.from_list([0, 0, 0], DistanceUnit.m)
    vec[1] = Distance(12., DistanceUnit.m)
    assert isinstance(vec[0], Distance)
    assert vec[1] == Distance(12., DistanceUnit.m)
    assert isinstance(vec[2], Distance)

def test_vector_set_error():
    vec = Vector3.from_list([0, 0, 0])
    with pytest.raises(ValueError, match="The passed values must be of the same quantity."):
        vec[1] = Distance(12., DistanceUnit.m)

class TestVectorAdd():
    def test_vector_add_ok(self):
        a = Vector3(1., 12., 3.)
        b = Vector3(2., 1., 5.)
        c = a + b
        assert c[0] == 3.
        assert c[1] == 13.
        assert c[2] == 8.

    def test_vector_add_failing(self):
        with pytest.raises(ValueError, match="The passed values must be of the same quantity."):
            a = Vector3(1., 12., 3.)
            b = Vector3(Distance(2., DistanceUnit.mm), Distance(2., DistanceUnit.mm), Distance(2., DistanceUnit.mm))
            _ = a + b

def test_vector_sub():
    a = Vector3(1., 12., 3.)
    b = Vector3(2., 1., 5.)
    c = a - b
    assert c[0] == -1.
    assert c[1] == 11.
    assert c[2] == -2.

def test_vector_shared_unit():
    vec = Vector3(1., 12., 3., ForceUnit.kN)
    assert vec[0].to(ForceUnit.kN) == 1.
    assert vec[1].to(ForceUnit.kN) == 12.
    assert vec[2].to(ForceUnit.kN) == 3.

def test_vector_sub_failing():
    with pytest.raises(ValueError, match="The passed values must be of the same quantity."):
        a = Vector3(1., 12., 3.)
        b = Vector3(Distance(2., DistanceUnit.mm), Distance(2., DistanceUnit.mm), Distance(2., DistanceUnit.mm))
        _ = a - b

def test_vector_str():
    vec = Vector3(Distance(2., DistanceUnit.mm), Distance(2., DistanceUnit.mm), Distance(2., DistanceUnit.mm))
    assert str(vec) == 'Vector3: [DistanceQuantity(2 mm), DistanceQuantity(2 mm), DistanceQuantity(2 mm)]'

class TestListInterface:
    def test_vector_to_list(self):
        vec = Vector3(Distance(2., DistanceUnit.mm), Distance(3., DistanceUnit.mm), Distance(4., DistanceUnit.mm))
        lst = vec.to_list()
        assert lst[0] == Distance(2, DistanceUnit.mm)
        assert lst[1] == Distance(3, DistanceUnit.mm)
        assert lst[2] == Distance(4, DistanceUnit.mm)

    def test_vector_from_list_individual_unit(self):
        lst = [Distance(2, DistanceUnit.mm), Distance(3, DistanceUnit.mm), Distance(4, DistanceUnit.mm)]
        vec = Vector3.from_list(lst)
        assert vec[0] == Distance(2, DistanceUnit.mm)
        assert vec[1] == Distance(3, DistanceUnit.mm)
        assert vec[2] == Distance(4, DistanceUnit.mm)

    def test_vector_from_list_shared_unit(self):
        vec = Vector3.from_list([2, 3, 4], DistanceUnit.mm)
        assert vec[0] == Distance(2, DistanceUnit.mm)
        assert vec[1] == Distance(3, DistanceUnit.mm)
        assert vec[2] == Distance(4, DistanceUnit.mm)

    def test_vector_from_list_failing_size(self):
        with pytest.raises(ValueError, match="List must contain exactly 3 elements"):
            lst = [Distance(2, DistanceUnit.mm), Distance(4, DistanceUnit.mm)]
            vec = Vector3.from_list(lst)

    def test_vector_from_list_failing_quantities(self):
        with pytest.raises(ValueError, match="The passed values must be of the same quantity."):
            lst = [Distance(2, DistanceUnit.mm), Force(3, ForceUnit.N), Distance(4, DistanceUnit.mm)]
            vec = Vector3.from_list(lst)

def test_vector_norm():
    from math import isclose
    vec = Vector3(Distance(3., DistanceUnit.mm), Distance(4., DistanceUnit.mm), Distance(12., DistanceUnit.mm))
    norm = vec.norm()
    assert isclose(norm.to(DistanceUnit.mm), 13.)

def test_vector_dot():
    a = Vector3(Distance(3., DistanceUnit.mm), Distance(4., DistanceUnit.mm), Distance(12., DistanceUnit.mm))
    b = Vector3(2., 1., 5.)
    c = a.dot_vec(b)
    assert c == Distance(70., DistanceUnit.mm)

def test_vector_to_unit_vector():
    vec = Vector3(Distance(3., DistanceUnit.mm), Distance(4., DistanceUnit.mm), Distance(12., DistanceUnit.mm))
    uv = vec.to_unit_vector()
    assert uv.norm() - 1. < 1E-15
    assert abs(uv.dot_vec(vec) / vec.norm() - 1) < 1E-10

def test_vector_cross():
    vec_a = Vector3(Distance(10., DistanceUnit.mm), Distance.zero(), Distance.zero())
    vec_b = Vector3(Force.zero(), Force(50., ForceUnit.N), Force.zero())
    res = vec_a.cross(vec_b)
    assert res[0].to(ForceDistanceUnit.Nm) == 0.
    assert res[1].to(ForceDistanceUnit.Nm) == 0.
    assert res[2].to(ForceDistanceUnit.Nm) == 0.5

class TestNumpyInterface:
    def test_vector_from_array(self):
        arr = np.array([1., 2., 3.])
        vec = Vector3.from_array(arr, ForceUnit.N)
        assert vec[0].to(ForceUnit.N) == 1.
        assert vec[1].to(ForceUnit.N) == 2.
        assert vec[2].to(ForceUnit.N) == 3.

    def test_vector_to_array(self):
        vec = Vector3(Distance(3., DistanceUnit.mm), Distance(4., DistanceUnit.mm), Distance(12., DistanceUnit.mm))
        arr = vec.to_array(DistanceUnit.mm)
        assert (arr == np.array([3., 4., 12.])).all()

def test_vector_mul():
    vec = Vector3(Distance(3., DistanceUnit.mm), Distance(4., DistanceUnit.mm), Distance(12., DistanceUnit.mm))
    res = vec * Force(2., ForceUnit.N)
    assert res[0].to(ForceDistanceUnit.Nm) == 0.006
    assert res[1].to(ForceDistanceUnit.Nm) == 0.008
    assert res[2].to(ForceDistanceUnit.Nm) == 0.024

def test_vector_div():
    vec = Vector3(Force(3., ForceUnit.N), Force(4., ForceUnit.N), Force(12., ForceUnit.N))
    res = vec / Area(2., AreaUnit.mmsq)
    assert res[0].to(StressUnit.MPa) == 1.5
    assert res[1].to(StressUnit.MPa) == 2.
    assert res[2].to(StressUnit.MPa) == 6.

def test_vector_matrix_zero():
    mat = Matrix3.zero()
    for i in range(3):
        for j in range(3):
            assert mat[0, 0] == 0.

def test_matrix_set():
    mat = Matrix3.from_list([[0, 0, 0], [0, 0, 0], [0, 0, 0]], ForceUnit.N)
    mat[0, 1] = Force(12, ForceUnit.N)
    assert mat[0, 0].to(ForceUnit.N) == 0.
    assert mat[0, 1].to(ForceUnit.N) == 12.
    assert mat[0, 2].to(ForceUnit.N) == 0.
    assert mat[1, 0].to(ForceUnit.N) == 0.
    assert mat[1, 1].to(ForceUnit.N) == 0.
    assert mat[1, 2].to(ForceUnit.N) == 0.
    assert mat[2, 0].to(ForceUnit.N) == 0.
    assert mat[2, 1].to(ForceUnit.N) == 0.
    assert mat[2, 2].to(ForceUnit.N) == 0.

def test_matrix_set_error():
    mat = Matrix3.from_list([[0, 0, 0], [0, 0, 0], [0, 0, 0]], ForceUnit.N)
    with pytest.raises(ValueError, match="The passed values must be of the same quantity."):
        mat[1, 2] = Distance(12., DistanceUnit.m)

def test_matrix_identity():
    mat = Matrix3.identity()
    for i in range(3):
        for j in range(3):
            if i == j:
                assert mat[i, j] == 1.
            else:
                assert mat[i, j] == 0.

def test_matrix_str():
    mat = Matrix3.from_list([[1, 3, 4], [5, 7, 3], [7, 8, 9]], ForceUnit.N)
    assert str(mat) == 'Matrix3: [\n[ForceQuantity(1 N), ForceQuantity(3 N), ForceQuantity(4 N)]\n[ForceQuantity(5 N), ForceQuantity(7 N), ForceQuantity(3 N)]\n[ForceQuantity(7 N), ForceQuantity(8 N), ForceQuantity(9 N)]]'


class TestMatrixListInterface:
    def test_matrix_from_list(self):
        mat = Matrix3.from_list([[1, 3, 4], [5, 7, 3], [7, 8, 9]], ForceUnit.N)
        assert mat[0, 0].to(ForceUnit.N) == 1.
        assert mat[1, 0].to(ForceUnit.N) == 5.
        assert mat[0, 1].to(ForceUnit.N) == 3.
        assert mat[2, 2].to(ForceUnit.N) == 9.

    def test_matrix_to_list_with_unit(self):
        lst = [[1, 3, 4], [5, 7, 3], [7, 8, 9]]
        mat = Matrix3.from_list(lst, ForceUnit.N)
        assert lst == mat.to_list(ForceUnit.N)

    def test_matrix_to_list_without_unit(self):
        lst = [[1, 3, 4], [5, 7, 3], [7, 8, 9]]
        mat = Matrix3.from_list(lst, ForceUnit.N)
        read_lst = mat.to_list()
        for i in range(3):
            for j in range(3):
                assert read_lst[i][j].to(ForceUnit.N) == lst[i][j]

class TestMatrixArrayInterface:
    def test_matrix_from_array(self):
        mat = Matrix3.from_array(np.array([[1., 3., 4.], [5., 7., 3.], [7., 8., 9.]]), ForceUnit.N)
        assert mat[0, 0].to(ForceUnit.N) == 1.
        assert mat[1, 0].to(ForceUnit.N) == 5.
        assert mat[0, 1].to(ForceUnit.N) == 3.
        assert mat[2, 2].to(ForceUnit.N) == 9.

    def test_matrix_to_array(self):
        array_in = np.array([[1., 3., 4.], [5., 7., 3.], [7., 8., 9.]])
        mat = Matrix3.from_array(array_in, ForceUnit.N)
        array_out = mat.to_array(ForceUnit.N)
        assert (array_in == array_out).all()

def test_matrix_transpose():
    mat = Matrix3.from_list([[1, 3, 4], [5, 7, 3], [7, 8, 9]])
    mat_t = mat.transpose()
    for i in range(3):
        for j in range(3):
            assert mat[i, j] == mat_t[j, i]

class TestMatrixFromRows:
    def test_from_rows_different_quantities(self):
        with pytest.raises(ValueError, match="All vectors must have the same Quantity."):
            Matrix3.from_rows([Vector3.from_list([1., 0., 1.], ForceUnit.N), Vector3.y(), Vector3.z()])

    def test_from_rows(self):
        mat = Matrix3.from_rows([Vector3.from_list([1., 0., 1.]), Vector3.y(), Vector3.z()])
        assert mat[0, 0] == 1.
        assert mat[0, 1] == 0.
        assert mat[0, 2] == 1.
        assert mat[1, 0] == 0.
        assert mat[1, 1] == 1.
        assert mat[1, 2] == 0.
        assert mat[2, 0] == 0.
        assert mat[2, 1] == 0.
        assert mat[2, 2] == 1.

def test_from_columns():
    mat = Matrix3.from_columns([Vector3.from_list([1., 0., 1.]), Vector3.y(), Vector3.z()]).transpose()
    assert mat[0, 0] == 1.
    assert mat[0, 1] == 0.
    assert mat[0, 2] == 1.
    assert mat[1, 0] == 0.
    assert mat[1, 1] == 1.
    assert mat[1, 2] == 0.
    assert mat[2, 0] == 0.
    assert mat[2, 1] == 0.
    assert mat[2, 2] == 1.

class TestMatrixRowInterface:
    def test_matrix_get_row(self):
        mat = Matrix3.from_columns([Vector3.from_list([1., 0., 1.]), Vector3.y(), Vector3.z()]).transpose()
        row = mat.get_row(2)
        assert row[0] == 0.
        assert row[1] == 0.
        assert row[2] == 1.

    def test_matrix_set_row(self):
        mat = Matrix3.from_columns([Vector3.x(), Vector3.y(), Vector3.z()]).transpose()
        mat.set_row(1, Vector3.from_list([1., 0., 1.]))
        assert mat[1, 0] == 1.
        assert mat[1, 1] == 0.
        assert mat[1, 2] == 1.

class TestMatrixColumnInterface:
    def test_matrix_get_column(self):
        mat = Matrix3.from_columns([Vector3.from_list([1., 0., 1.]), Vector3.y(), Vector3.z()]).transpose()
        column = mat.get_column(2)
        assert column[0] == 1.
        assert column[1] == 0.
        assert column[2] == 1.

    def test_matrix_set_column(self):
        mat = Matrix3.from_columns([Vector3.x(), Vector3.y(), Vector3.z()]).transpose()
        mat.set_column(1, Vector3.from_list([1., 0., 1.]))
        assert mat[0, 1] == 1.
        assert mat[1, 1] == 0.
        assert mat[2, 1] == 1.

class TestMatrixConstructor:
    def test_matrix_constructor_no_args(self):
        mat = Matrix3()
        assert mat == Matrix3.zero()

    def test_matrix_constructor_list(self):
        mat = Matrix3([[1, 3, 4], [5, 7, 3], [7, 8, 9]], ForceUnit.N)
        assert mat == Matrix3.from_list([[1, 3, 4], [5, 7, 3], [7, 8, 9]], ForceUnit.N)

    def test_matrix_constructor_array(self):
        mat = Matrix3(np.array([[1., 3., 4.], [5., 7., 3.], [7., 8., 9.]]), ForceUnit.N)
        assert mat == Matrix3.from_array(np.array([[1., 3., 4.], [5., 7., 3.], [7., 8., 9.]]), ForceUnit.N)