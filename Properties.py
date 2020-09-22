"""

"""
class Temperature():
    def __init__(self,T_C):
        self.C = T_C

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def K(self):
        return self.C - 273.15

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def F(self):
        return (self.C * (9/5)) + 32

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def R(self):
        return (self.C + 273.15) * (9/5)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def C(self):
        return self._C

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @C.setter
    def C(self,val):
        if val < -273.15:
            raise ValueError("Temperature below -273 is not possible")
        self._C = val

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_K(cls, K):
        C = K + 273.15
        return cls(C)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_F(cls, F):
        C = (F - 32) * (5/9)
        return cls(C)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_R(cls, R):
        C = (R - 491.67) * (5 / 9)
        return cls(C)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __add__(self,other):
        if isinstance(other, Temperature):
            K = self.K + other.K
            return Temperature.from_K(K)
        else:
            K = self.K + other
            return Temperature.from_K(K)

    __iadd__ = __add__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __sub__(self,other):
        if isinstance(other, Temperature):
            K = self.K - other.K
            return Temperature.from_K(K)
        else:
            K = self.K - other
            return Temperature.from_K(K)

    __isub__ = __sub__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __mul__(self, other):
        if isinstance(other, Temperature):
            K = self.K * other.K
            return Temperature.from_K(K)
        else:
            K = self.K * other
            return Temperature.from_K(K)

    __imul__ = __mul__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __truediv__(self, other):
        if isinstance(other, Temperature):
            K = self.K / other.K
            return Temperature.from_K(K)
        else:
            K = self.K / other
            return Temperature.from_K(K)

    __itruediv__ = __truediv__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __gt__(self, T):
        if isinstance(T, Temperature):
            return self.C > T.C
        else:
            return self.C > T

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __lt__(self, T):
        if isinstance(T, Temperature):
            return self.C < T.C
        else:
            return self.C < T

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __ge__(self, T):
        if isinstance(T, Temperature):
            return self.C >= T.C
        else:
            return self.C >= T

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __le__(self, T):
        if isinstance(T, Temperature):
            return self.C <= T.C
        else:
            return self.C <= T

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __eq__(self, T):
        if isinstance(T, Temperature):
            return self.C == T.C
        else:
            return self.C == T

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __ne__(self, T):
        if isinstance(T, Temperature):
            return self.C != T.C
        else:
            return self.C != T

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __str__(self):
        temp = "Temperture({}°C, {}°K, {}°F, {}°R)".format(self.C, self.K, self.F, self.R)
        return temp

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __repr__(self):
        temp = "Temperture({}°C, {}°K, {}°F, {}°R)".format(self.C, self.K, self.F, self.R)
        return temp

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __hash__(self):
        return hash("Temperture({}°C, {}°K)".format(self.C, self.K))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def toChild(self):
        return Temperature1(self.C)

#######################################################################################################################

class Temperature1(Temperature):
    def __init__(self, T_C):
        super().__init__(T_C)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __add__(self,other):
        if isinstance(other, Temperature):
            K = self.K + other.K
            return K
        else:
            K = self.K + other
            return K

    __iadd__ = __add__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __sub__(self,other):
        if isinstance(other, Temperature):
            K = self.K - other.K
            return K
        else:
            K = self.K - other
            return K

    __isub__ = __sub__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __mul__(self, other):
        if isinstance(other, Temperature):
            K = self.K * other.K
            return K
        else:
            K = self.K * other
            return K

    __imul__ = __mul__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __truediv__(self, other):
        if isinstance(other, Temperature):
            K = self.K / other.K
            return K
        else:
            K = self.K / other
            return K

    __itruediv__ = __truediv__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def toParent(self):
        return Temperature(self.C)


#######################################################################################################################

class Pressure():
    a = 100000
    b = 101325
    c = 760
    d = 13.5951
    e = 9.80665

    def __init__(self,Pa):
        self.Pa = Pa

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def kPa(self):
        return self.Pa / 1000

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def MPa(self):
        return self.Pa / 1000000

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def bar(self):
        return self.Pa / self.a

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def atm(self):
        return self.Pa / self.b

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def Torr(self):
        return self.Pa * (self.c / self.b)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @property
    def mmHg(self):
        return self.Pa / (self.d * self.e)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_kPa(cls, kPa):
        Pa = kPa * 1000
        return cls(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_MPa(cls, MPa):
        Pa = MPa * 1000000
        return cls(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_bar(cls, bar):
        Pa = bar * cls.a
        return cls(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_atm(cls, atm):
        Pa = atm * cls.b
        return cls(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_Torr(cls, torr):
        Pa = torr * (cls.b / cls.c)
        return cls(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    @classmethod
    def from_mmHg(cls, mmHg):
        Pa = mmHg * cls.d * cls.e
        return cls(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __add__(self,other):
        if isinstance(other, Pressure):
            Pa = self.Pa + other.Pa
            return Pressure(Pa)
        else:
            raise ValueError("Cannot add a Pressure and non pressure")

    __iadd__ = __add__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __sub__(self,other):
        if isinstance(other, Pressure):
            Pa = self.Pa - other.Pa
            return Pressure(Pa)
        else:
            raise ValueError("Cannot subtract a Pressure and non pressure")

    __isub__ = __sub__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __mul__(self, other):
        if not isinstance(other, Pressure):
            Pa = self.Pa * other
            return Pressure(Pa)
        else:
            raise ValueError("Cannot multiply two Pressures")

    __imul__ = __mul__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __truediv__(self, other):
        if not isinstance(other, Pressure):
            Pa = self.Pa / other
            return Pressure(Pa)
        else:
            raise ValueError("Cannot divide two Pressures")

    __itruediv__ = __truediv__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __gt__(self, P):
        if isinstance(P, Pressure):
            return self.kPa > P.kPa
        else:
            return self.kPa > P

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __lt__(self, P):
        if isinstance(P, Pressure):
            return self.kPa < P.kPa
        else:
            return self.kPa < P

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __ge__(self, P):
        if isinstance(P, Pressure):
            return self.kPa >= P.kPa
        else:
            return self.kPa >= P

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __le__(self, P):
        if isinstance(P, Pressure):
            return self.kPa <= P.kPa
        else:
            return self.kPa <= P

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __eq__(self, P):
        if isinstance(P, Pressure):
            return self.kPa == P.kPa
        else:
            return self.kPa == P

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __ne__(self, P):
        if isinstance(P, Pressure):
            return self.kPa != P.kPa
        else:
            return self.kPa != P

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __str__(self):
        press = "Pressure({}Pa, {}kPa, {}MPa, {}bar, {}atm, {}Torr, {}mmHg)".format(self.Pa,
                                                                                     self.kPa,
                                                                                     self.MPa,
                                                                                     self.bar,
                                                                                     self.atm,
                                                                                     self.Torr,
                                                                                     self.mmHg)
        return press

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __repr__(self):
        press = "Pressure({}Pa, {}kPa, {}MPa, {}bar, {}atm, {}Torr, {}mmHg)".format(self.Pa,
                                                                                      self.kPa,
                                                                                      self.MPa,
                                                                                      self.bar,
                                                                                      self.atm,
                                                                                      self.Torr,
                                                                                      self.mmHg)
        return press

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __hash__(self):
        return hash("Pressure({}°bar, {}°MPa)".format(self.bar, self.MPa))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def toChild(self):
        return Pressure1(self.Pa)

#######################################################################################################################

class Pressure1(Pressure):
    def __init__(self, Pa):
        super().__init__(Pa)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __add__(self,other):
        if isinstance(other, Pressure):
            Pa = self.Pa + other.Pa
            return Pa
        else:
            raise ValueError("Cannot add a Pressure and non pressure")

    __iadd__ = __add__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __sub__(self,other):
        if isinstance(other, Pressure):
            Pa = self.Pa - other.Pa
            return Pa
        else:
            raise ValueError("Cannot subtract a Pressure and non pressure")

    __isub__ = __sub__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __mul__(self, other):
        if not isinstance(other, Pressure):
            Pa = self.Pa * other
            return Pa
        else:
            raise ValueError("Cannot multiply two Pressures")

    __imul__ = __mul__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def __truediv__(self, other):
        if not isinstance(other, Pressure):
            Pa = self.Pa / other
            return Pa
        else:
            raise ValueError("Cannot divide two Pressures")

    __itruediv__ = __truediv__

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def toParent(self):
        return Pressure(self.Pa)

if __name__ == "__main__":
    a = Pressure.from_bar(90)
    b = Temperature(600)
    print(b)
