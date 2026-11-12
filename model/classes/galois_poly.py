import numpy as np
from classes.defs import *

class GaloisPoly:
    
    def __init__(self, gf, p):
        """
        Implements a polynomial over GF

        Args:
            gf: Given GF where the coefficient lives
            p: List of coefficient alpha powers, in decending power order
        """
        self._gf        = gf
        self._zero_poly = False
        self._coeff     = self._remove_lead_zeros(p)
        self._degree    = self._get_poly_degree(self._coeff)

    def __call__(self, x):
        """
        Evaluates a poly in a given element x as poly(x)

        Args:
            x: Power of element to valuate

        Returns:
            int: Result of valuation
        """
        # manage zero poly, zero x
        if self._zero_poly:
            ans = 0
        elif x == GFE0:
            ans = self._coeff[::-1][0]
        else:
            for k, ak in enumerate(self._coeff[::-1]):
                if k == 0:
                    ans = self._coeff[::-1][0]
                elif ak != GFE0:
                    # compute powers, multiply by ak, add all
                    x_pow   = self._gf.pow(x, k)[ID_POWER]
                    # print(f"x_pow = self._gf.pow({x}, {k})[ID_POWER] == {x_pow}")
                    term    = self._gf.mul(ak, x_pow)[ID_POWER]
                    # print(f"term = self._gf.mul({ak}, {x_pow})[ID_POWER] == {term}")
                    ans     = self._gf.add(term, ans)[ID_POWER]
                    # print(f"ans = self._gf.add({term}, {ans})[ID_POWER] == {ans}")

        return ans

    def __str__(self):
        info = ""
        # manage zero poly
        if self._zero_poly:
            info += "[0]"
        else:
            for k, ak in enumerate(self._coeff):
                # ommit zero terms
                if ak != GFE0:
                    # manage powers
                    if self._degree-k == 0:
                        info += "1" if ak == GFE1 else f"a^{ak}\n"
                    elif self._degree-k == 1:
                        info += "" if ak == GFE1 else f"a^{ak}*"
                        info += f"x"
                    else: 
                        info += "" if ak == GFE1 else f"a^{ak}*"
                        info += f"x^{self._degree-k}"
                    info += "" if k == self._degree else " + "

        return info

    def __repr__(self):
        return str(self._coeff)

    def __add__(self, other):
        """
        Get the addition f plus g as f + g

        Returns:
            GaloisPoly: Result of addition
        """
        # manage zero poly
        if self._zero_poly:
            ans = self
        elif other._zero_poly:
            ans = other
        else:
            ans = self._add_poly(self._coeff, other._coeff)
            ans = GaloisPoly(self._gf, ans)
        return ans

    def __mul__(self, other):
        """
        Get the multiplication/scale f by g as f * g (if g is constant scale is made)

        Returns:
            GaloisPoly: Result of multiplication/scale
        """
        if isinstance(other, int):
            # manage zero poly
            if self._zero_poly:
                ans = self
            else:
                ans = self._scale_poly(self._coeff, other)
                ans = GaloisPoly(self._gf, ans)
        else:
            # manage zero poly
            if self._zero_poly:
                ans = self
            elif other._zero_poly:
                ans = other
            else:
                ans = self._mul_poly(self._coeff, other._coeff)
                ans = GaloisPoly(self._gf, ans)
        return ans

    def __truediv__(self, other):
        """
        Get the quotient and reminder of the f over g division as f / g

        Raises:
            ZeroDivisionError: Divisor is the zero-poly

        Returns:
            tuple: (quotient, remainder)
        """
        # manage zero poly
        if other._zero_poly:
            raise ZeroDivisionError("ArithmeticError: Divisor Must Not Be Zero Poly")
        elif self._zero_poly:
            q       = self
            r       = self
        else:
            q, r    = self._div_poly(self._coeff, other._coeff)
            q       = GaloisPoly(self._gf, q)
            r       = GaloisPoly(self._gf, r)
        return q, r

    def __floordiv__(self, other):
        """
        Get the quotient of the f over g division as f // g

        Raises:
            ZeroDivisionError: Divisor is the zero-poly

        Returns:
            GaloisPoly: Quotient of division
        """
        # manage zero poly
        if other._zero_poly:
            raise ZeroDivisionError("ArithmeticError: Divisor Must Not Be Zero Poly")
        elif self._zero_poly:
            q       = self
        else:
            q, _    = self._div_poly(self._coeff, other._coeff)
            q       = GaloisPoly(self._gf, q)
        return q

    def __mod__(self, other):
        """
        Get the remainder of the f over g division as f % g

        Raises:
            ZeroDivisionError: Divisor is the zero-poly

        Returns:
            GaloisPoly: Remainder of division
        """
        # manage zero poly
        if other._zero_poly:
            raise ZeroDivisionError("ArithmeticError: Divisor Must Not Be Zero Poly")
        elif self._zero_poly:
            r       = self
        else:
            _, r    = self._div_poly(self._coeff, other._coeff)
            r       = GaloisPoly(self._gf, r)
        return r

    def __matmul__(self, other):
        """
        Get ak coefficient as poly @ k

        Returns:
            int: Field element ak
        """
        ak  = self._coeff[::-1][other]
        return ak

# =======================================================================================
# =======================================================================================
    def _remove_lead_zeros(self, p):
        """
        Removes leading zeros of a given coefficient list, if any

        Args:
            p: Coefficient list of p

        Returns:
            list: Coefficient list with no leading zeros
        """
        # manage zero poly, pass as p = [GFE0]
        if np.all(np.array(p) == GFE0):
            self._zero_poly = True
            first_non_zero  = -1
        else:
            self._zero_poly = False
            first_non_zero  = 0
            for k, ak in enumerate(p):
                if ak == GFE0:
                    continue
                else:
                    first_non_zero = k
                    break
        return p[first_non_zero:]
        
    def _get_poly_degree(self, p):
        """
        Get the degree of poly for the given coefficient list

        Args:
            p: Coefficient list of p

        Returns:
            int: Degree of represented poly
        """
        if np.all(np.array(p) == GFE0):
            degree = 0
        else:
            degree = len(p) - 1
        return degree

    def _align_terms(self, f, g):
        """
        Completes with zero f and g polynomials to align powers

        Args:
            f: Coefficient list of f
            g: Coefficient list of g

        Returns:
            tuple: Lists with aligned f and g powers (f,g)
        """
        diff = self._get_poly_degree(f) - self._get_poly_degree(g)
        if diff > 0:
            g   = [GFE0]*diff + g
        elif diff < 0:
            f   = [GFE0]*(-diff) + f

        return f, g

    def _scale_poly(self, p, alpha):
        """
        Get the coefficient list of scaling p by element alpha

        Args:
            p: Coefficient list of p
            alpha: Power of alpha element

        Returns:
            list: Coefficient list of the scaled poly
        """
        ans = p.copy()
        for i, ak in enumerate(p):
            if ak != GFE0:
                ans[i] = self._gf.mul(ak, alpha)[ID_POWER]
        return ans
    
    def _add_terms(self, term_stack):
        """
        Implement the coefficient summation of several polynomals over GF

        Args:
            term_stack: List stack (2D-matrix). Each row is the coefficients of a poly aligned by powers

        Returns:
            list: Coefficients of the summation in format index == power
        """
        term_stack = np.atleast_2d(term_stack)
        term, power = term_stack.shape

        ans = []
        for p in range(power):
            sum = GFE0
            for t in range(term):
                sum = self._gf.add(term_stack[t,p], sum)[ID_POWER]

            ans += [sum]

        return ans

    def _add_poly(self, f, g):
        """
        Get the coefficient list of f+g addition

        Args:
            f: Coefficient list of f
            g: Coefficient list of g

        Returns:
            list: Coefficient list of the addition
        """
        # complete poly terms
        f, g = self._align_terms(f, g)

        # add same power terms
        term_stack = np.vstack((f,g))
        ans = self._add_terms(term_stack)

        return ans

    def _mul_poly(self, f, g):
        """
        Get the coefficient list of f*g multiplication

        Args:
            f: Coefficient list of f
            g: Coefficient list of g

        Returns:
            list: Coefficient list of the multiplication
        """
        f_degree = self._get_poly_degree(f)
        g_degree = self._get_poly_degree(g)

        # expand size to match f*g final poly, reverse it so power == col index
        if g_degree > f_degree:
            long_poly   = np.array(g[::-1] + [GFE0]*f_degree)
            short_poly  = np.array(f[::-1])
        else:
            long_poly   = np.array(f[::-1] + [GFE0]*g_degree)
            short_poly  = np.array(g[::-1])

        term_stack = None
        for i, ak in enumerate(short_poly):
            if ak != GFE0:
                # manage powers
                rotated = np.roll(long_poly, i)
                # multiply by constant
                rotated     = self._scale_poly(rotated, ak)
                term_stack  = np.array(rotated) if term_stack is None else np.vstack((term_stack, rotated))

        # final reduction, reverse to normal power-order ans[0] = xn
        ans = self._add_terms(term_stack)[::-1]

        return ans

    def _div_poly(self, f, g):
        """
        Get the coefficient list of f/g division

        Args:
            f: Coefficient list of f
            g: Coefficient list of g

        Raises:
            ArithmeticError: The given lists represents polinomials with degree of f less than degree of g

        Returns:
            list: Coefficient list of the division
        """
        diff = self._get_poly_degree(f) - self._get_poly_degree(g)
        if diff < 0:
            raise ArithmeticError("ArithmeticError: Degree of f must >= to degree of g")
        else:
            step    = f
            q       = None
            while diff >= 0:
                # compute new term of q for this step
                ak      = self._gf.div(step[0], g[0])[ID_POWER]
                q_term  = [ak] + diff*[GFE0]
                q       = q_term if q is None else self._add_poly(q, q_term)
                # compute next step to divide
                to_add  = self._mul_poly(q_term, g)
                step    = self._add_poly(to_add, step)
                # remove leading zeros
                while len(step) > 1 and step[0] == GFE0:
                    step.pop(0)

                diff = self._get_poly_degree(step) - self._get_poly_degree(g)

        r = step

        return q, r

# =======================================================================================
# =======================================================================================
    def poly_from_roots(self, roots):
        """
        Get a polynom with specified roots

        Args:
            roots: List with alpha powers of desired roots

        Returns:
            GaloisPoly: Polynom with corresponding roots
        """
        if len(roots) == 1:
            poly = [GFE1] + roots
        else:
            poly = None
            for r in roots:
                factor  = [GFE1, r]
                poly    = factor if poly is None else self._mul_poly(poly, factor)

        return GaloisPoly(self._gf, poly)

    def formal_derivative(self):
        """
        Get the formal derivative of this polynom

        Returns:
            GaloisPoly: Formal derivative polynom
        """
        ans = [ak if k % 2 else GFE0 for k, ak in enumerate(self._coeff[::-1])]
        ans = ans[1::]
        return GaloisPoly(self._gf, ans[::-1])
