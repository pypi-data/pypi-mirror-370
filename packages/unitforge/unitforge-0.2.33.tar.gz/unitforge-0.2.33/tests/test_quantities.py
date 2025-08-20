from math import isclose

import unitforge


class TestCommon:
    def test_conversion(self):
        f = unitforge.Force(12., unitforge.ForceUnit.N)
        assert f.to(unitforge.ForceUnit.mN) == 12000.0

    def test_rep(self):
        f = unitforge.Force(12., unitforge.ForceUnit.N)
        assert str(f) == '12 N'

    def test_add(self):
        f_a = unitforge.Force(12., unitforge.ForceUnit.N)
        f_b = unitforge.Force(1., unitforge.ForceUnit.N)
        f_c = f_a + f_b
        assert f_c.to(unitforge.ForceUnit.N) == 13.

    def test_sub(self):
        f_a = unitforge.Force(12., unitforge.ForceUnit.N)
        f_b = unitforge.Force(1., unitforge.ForceUnit.N)
        f_c = f_a - f_b
        assert f_c.to(unitforge.ForceUnit.N) == 11.

    def test_f64_mul(self):
        f = unitforge.Force(12., unitforge.ForceUnit.N)
        res_a = f * 2
        assert isclose(res_a.to(unitforge.ForceUnit.N), 24.)
        res_b = 2 * f
        assert isclose(res_b.to(unitforge.ForceUnit.N), 24.)

    def test_f64_div(self):
        f = unitforge.Force(12., unitforge.ForceUnit.N)
        res_a = f / 2
        assert isclose(res_a.to(unitforge.ForceUnit.N), 6.)

    def test_mul_quantity(self):
        f = unitforge.Force(12., unitforge.ForceUnit.N)
        d = unitforge.Distance(2., unitforge.DistanceUnit.m)
        res_a = f * d
        assert isclose(res_a.to(unitforge.ForceDistanceUnit.Nm), 24.)
        res_b = f * d
        assert isclose(res_b.to(unitforge.ForceDistanceUnit.Nm), 24.)

    def test_div_quantity(self):
        m = unitforge.ForceDistance(12., unitforge.ForceDistanceUnit.Nm)
        d = unitforge.Distance(2., unitforge.DistanceUnit.m)
        res = m / d
        assert isclose(res.to(unitforge.ForceUnit.N), 6.)

    def test_div_with_self_to_f64(self):
        f_1 = unitforge.Force(12., unitforge.ForceUnit.N)
        f_2 = unitforge.Force(2., unitforge.ForceUnit.N)
        res = f_1 / f_2
        assert isclose(res, 6.)

def test_sqrt():
    a = unitforge.Area(16., unitforge.AreaUnit.msq)
    assert isclose(a.sqrt().to(unitforge.DistanceUnit.m), 4.)

def test_const():
    c = unitforge.Velocity.c()
    assert isclose(c.to(unitforge.VelocityUnit.m_s), 299792458.0)

def test_mul_with_self():
    a = unitforge.Area(4., unitforge.AreaUnit.msq)
    i = a * a
    assert isclose(i.to(unitforge.AreaOfMomentUnit.mhc), 16.)