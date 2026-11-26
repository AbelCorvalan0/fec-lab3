from classes.galois_field import *
from classes.galois_poly import *

class ReedSolomonDecoder:
    
    def __init__(self, n, k, gf, gen_roots):
        self._gf        = gf
        self._gen_roots = gen_roots
        self._code_t    = len(gen_roots) // 2
        self._code_lo   = gen_roots[0]
        self._code_n    = n
        self._code_k    = k

    def do_unpack(self, value, degree):
        # useful: return a x**degree poly
        if value == -1:
            ak      = [GFE0]*degree + [GFE1]
        else:
            mask    = self._gf._order
            ak      = [(value >> i*self._gf._field_m) & mask for i in range(degree+1)]
            ak      = [self._gf._get_power(a) for a in ak]
        return GaloisPoly(self._gf, ak[::-1])

# =======================================================================================
# =======================================================================================
    def _get_syndromes(self, r):
        return [r(a) for a in self._gen_roots]

    def _get_discrepancy(self, mu, syn, Lx):
        disc = syn[mu]
        for i in range(1, Lx._degree+1):
            term    = self._gf.mul(Lx @ i, syn[mu - i])[ID_POWER]
            disc    = self._gf.add(disc, term)[ID_POWER]
        return disc

    def _get_locator_poly(self, syn):
        Lx  = []
        dmu = []

        # step0 initialization: locator == 1, rho == -1
        Lx.append(self.do_unpack(-1, 0))
        rho = -1
        for mu in range(0, 2*self._code_t):
            disc = self._get_discrepancy(mu, syn, Lx[-1])

            # if dicrepancy zero (maybe S0 == 0), locator nor parameters change
            if disc == GFE0:
                poly = Lx[-1]
            else:
                # before first adjust, rho uses disc == locator == 1
                if rho == -1:
                    d_rho   = GFE1
                    L_rho   = self.do_unpack(-1, 0)
                else:
                    d_rho   = dmu[rho]
                    L_rho   = Lx[rho]
                xm      = self.do_unpack(-1, mu-rho)
                xm      = xm * self._gf.div(disc, d_rho)[ID_POWER]
                poly    = Lx[-1] + (xm * L_rho)

                # approach: rho changes when the degree increases, this garantices non-zero discrepancy
                if poly._degree > Lx[-1]._degree:
                    rho = mu

            dmu.append(disc)
            Lx.append(poly)
            # print(dmu, rho)
            # print(poly)
            # print()

        return Lx[-1]

    def _chien_search(self, poly):
        err_pos = []
        for i in range(self._gf._order):
            a_inv = self._gf.inv(i)[ID_POWER]         # alpha^-i (power index)
            if poly(a_inv) == GFE0:               # root of the locator polynomial
                err_pos.append(i)
        if len(err_pos) != poly._degree:
            print(f"Warning: {len(err_pos)} roots found, expected {poly._degree} (uncorrectable)")
        # chien returns only roots
        root    = [self._gf.inv(ek)[ID_POWER] for ek in err_pos]
        return root

    def _get_erasure_locator(self, eras_idx):
        """Gamma(x) = prod (1 + Y_l x)"""
        Gx = GaloisPoly(self._gf, [GFE1])
        # Y_l*x + 1  
        eras_roots = self._build_inv_array(eras_idx)
        Gx.poly_from_roots(eras_roots)
        return Gx

    def _build_inv_array(self, eras_idx):
        return [self._gf.inv(p)[ID_POWER] for p in eras_idx] 

    # add in array the roots locator & pos erasured
    def _get_error_mask(self, syn, Lx, loc_root, eras_pos):
        # get evaluator poly, and locator derivative
        Sx  = GaloisPoly(self._gf, syn[::-1])
      
        if (eras_pos == []): 
            Gx = self.do_unpack(-1, 0)
            Tx = Sx
            print(Gx * Sx)
        else:
            Gx  = self._get_erasure_locator(eras_pos)
            print(Gx * Sx)
            if (Tx._coeff < self.do_unpack(-1, 2*self._code_t)):    
                print(":D1")
                Tx = (Gx * Sx)
                print(Gx * Sx)
                print(":D2")
            else:
                print(Gx * Sx)
                print(":D3")
                Tx = (Gx * Sx) % self.do_unpack(-1, 2*self._code_t)
                print(Gx * Sx)
                print(":D4")

        #Tx  = (Gx * Sx) % GaloisPoly(self._gf, [GFE1] + [GFE0]*len(syn)) #self.do_unpack(-1, 2*self._code_t) 
        Zx  = (Tx * Lx) % GaloisPoly(self._gf, [GFE1] + [GFE0]*len(syn)) #self.do_unpack(-1, 2*self._code_t)
        Fx  =  Lx * Gx
        Fxp = Fx.formal_derivative()
        # print(Sx, Zx, Lx, Lxp)

        ek = []
        for rk in loc_root + eras_pos:
            num = self._gf.mul(Zx(rk), self._gf.pow(rk, self._code_lo-1)[ID_POWER])[ID_POWER]
            den = Fxp(rk)
            ek.append(self._gf.div(num, den)[ID_POWER])
        return ek

    def _error_correction(self, r, error_mask, error_pos):
        ex  = GaloisPoly(self._gf, [GFE0])
        for ek, k in zip(error_mask, error_pos):
            ex  = ex + (self.do_unpack(-1, k) * ek)
        print(ex)
        return r + ex
    
    def decode(self, r, eras_pos):
        syn = self._get_syndromes(r)
        Lx  = self._get_locator_poly(syn)
        # get roots of reciprocal, error position
        Lx          = Lx.get_reciprocal()
        loc_root    = self._chien_search(Lx)
        # to forney we dont use reciprocal locator, evaluator changes with reciprocal locator hence formula must be adjusted
        ek          = self._get_error_mask(syn, Lx.get_reciprocal(), [self._gf.inv(rk)[ID_POWER] for rk in loc_root], eras_pos)
        r = self._error_correction(r, ek, loc_root)
        print(syn)
        print(loc_root)
        return r
