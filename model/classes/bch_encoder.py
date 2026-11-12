from classes.galois_field import *
from classes.galois_poly import *

class BchEncoder:

    def __init__(self):
        print(flush=True)
        print("BchEncoder.init begin", flush=True)
        self._n         = 15
        self._gf_base   = GaloisField(1, 0b11)
        self._gen_poly  = GaloisPoly(self._gf_base, [0, -1, 0, -1, -1, 0, 0, -1, 0, 0, 0])
        self._k         = self._n - self._gen_poly._degree
        print("BchEncoder.init end", flush=True)
        print(vars(self), flush=True)

# =======================================================================================
# =======================================================================================
    def do_unpack(self, v, bit_width):
        v   = self._gf_base.do_unpack(v, bit_width=bit_width)
        ak  = [GFE0 if e == 0 else GFE1 for e in v]
        return GaloisPoly(self._gf_base, ak)

    def do_pack(self, p, bit_width):
        if p._zero_poly:
            v   = 0
        else:
            p   = [GFE0]*(bit_width-1 - p._degree) + p._coeff
            v   = [0 if ak == GFE0 else 1 for ak in p]
            v   = self._gf_base.do_pack(v)
        return v

    def encode(self, u):
        xp  = [GFE1] + [GFE0]*(self._gen_poly._degree)
        xp  = GaloisPoly(self._gf_base, xp)
        v   = u*xp + (u*xp) % self._gen_poly
        return v

    def get_output(self, w):
        u   = self.do_unpack(w, bit_width=self._k)
        v   = self.encode(u)
        print(flush=True)
        print(f"From Python: self.encode({u}) = {v}", flush=True)
        cw  = self.do_pack(v, bit_width=self._n)
        return cw

# from pysv import sv, DataType

# class dut_model:
#     @sv()
#     def __init__(self):
#         self.model = None

#     @sv(w=DataType.Int, return_type=DataType.Int)
#     def get_output(self, w):
#         return w + 1
#         # return self.model.get_output(w)
