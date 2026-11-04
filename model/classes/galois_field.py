import numpy as np
from .defs import *

class GaloisField:

    def __init__(self, m_order, primitive_poly):
        """
        Elements and operations to work in Galois fields. The zero element always is indexed as -1

        Args:
            m_order: Field order M
            primitive_poly: Bitfield representation of primitive poly powers. Ex: X**4 + X + 1 == 0b10011
        """
        self._m_order           = m_order
        self._primitive_poly    = primitive_poly
        self._cycle             = 2**self._m_order - 1
        self._elements          = []
        self._generate_field()

    def __call__(self, n):
        """
        Get an element by using calling method (). Returns tuple with binary value and power
        Ex: gf(ELEMENT_ONE), gives (1,0)
        
        Args:
            n: Power of element

        Returns:
            tuple: (value, power)
        """
        if n == ELEMENT_ZERO:
            i = ELEMENT_ZERO
        else:
            i = abs(n) % self._cycle

        return self._elements[i], i

    def __str__(self):
        info = f"{'='*128}\n"
        for e in self._elements: info += f"{e:0{self._m_order}b} -- {self._elements.index(e) if e!=0 else ELEMENT_ZERO}\n"
        info += f"{'='*128}\n"

        return info

# =======================================================================================
# =======================================================================================
    def _get_power(self, e):
        """
        Get the power of a given element value
        Ex: _get_power(1), gives 0

        Args:
            e: Value of element

        Returns:
            int: Power of given element value
        """
        if e == 0:
            ans = ELEMENT_ZERO
        else:
            ans = self._elements.index(e)
        return ans

    def _get_poly(self,e):
        """
        Get polynomial representation of a element
        Ex: _get_poly(0b0110), gives [0,1,1,0]
        
        Args:
            e: Field element

        Returns:
            list: Poly representation of element
        """
        return [(e>>b) & 1 for b in range(self._m_order+1)]

    def _generate_field(self):
        """
        Generate all the field elements for the given order and primitive poly. Zero element always added last
        Ex: For a GF8 field, gives [1, alpha, alpha2, alpha3, alpha4, alpha5, alpha6, 0]
        """

        for i in range(2**self._m_order):
            # get all primitive elements (1, alpha, alpha**2..)
            if i < self._m_order:
                alpha_n_final = 1<<i
            # get the m element (alpha**m)
            elif i == self._m_order:
                alpha_n_final = self._primitive_poly & (2**self._m_order)-1
            # get the remaining elements
            else:
                # multiply last one by alpha (LRL), get polynomial representation, simplify
                alpha_n         = self._elements[-1]<<1
                alpha_n_poly    = self._get_poly(alpha_n)

                # simplify using known elements
                alpha_n_final = 0
                for i in range(len(alpha_n_poly)):
                    if alpha_n_poly[i]:
                        alpha_n_final ^= self._elements[i]

            if i > 0 and alpha_n_final==1:
                # print(f"Field Closed Succesfully!, {len(self._elements)} Non-Zero Elements")
                break
            else:
                self._elements += [alpha_n_final]

        # complete the field with zero element
        self._elements += [0]
    
    def add(self, a, b, id_power=True):
        """
        Add two elements of the field

        Args:
            a: Power of 1st element
            b: Power of 2nd element
            id_power: True to input power of elements, False to input direct value of elements. Defaults to True.

        Returns:
            tuple: (result, power)
        """
        if id_power:
            a = self(a)[ID_BIN]
            b = self(b)[ID_BIN]

        ans = a ^ b
        i   = ELEMENT_ZERO if ans==0 else self._elements.index(ans)
        return self(i)

    def mul(self, a, b, id_power=True):
        """
        Multiply two elements of the field

        Args:
            a: Power of 1st factor
            b: Power of 2nd factor
            id_power: True to input power of elements, False to input direct value of elements. Defaults to True.

        Returns:
            tuple: (result, power)
        """
        if not id_power:
            a = self._get_power(a)
            b = self._get_power(b)

        i   = ELEMENT_ZERO if a==ELEMENT_ZERO or b==ELEMENT_ZERO else (a+b) % self._cycle
        return self(i)

    def inv(self, a, id_power=True):
        """
        Get inverse of element

        Args:
            a: Power of element to invert
            id_power: True to input power of element, False to input direct value of element. Defaults to True.

        Raises:
            ZeroDivisionError: When a == -1 == ZERO_ELEMENT

        Returns:
            tuple: (result, power)
        """
        if not id_power:
            a = self._get_power(a)

        if a == ELEMENT_ZERO:
            raise ZeroDivisionError
        else:
            i   = (self._cycle - a) % self._cycle

        return self(i)

    def div(self, a, b, id_power=True):
        """
        Divide elements of the field

        Args:
            a: Power of numerator
            b: Power of denominator
            id_power: True to input power of elements, False to input direct value of elements. Defaults to True.

        Returns:
            tuple: (result, power)
        """
        if not id_power:
            a = self._get_power(a)
            b = self._get_power(b)

        return self.mul(a, self.inv(b)[ID_POWER])

    def pow(self, a, b, id_power=True):
        """
        Powers one elements to the given exponent (0**0 = 1 always)
        
        Args:
            a: Power of the base
            b: Exponent
            id_power: True to input power of base, False to input direct value of base. Defaults to True.

        Returns:
            tuple: (result, power)
        """
        if not id_power:
            a = self._get_power(a)

        if a == ELEMENT_ZERO and b == 0:
            i = ELEMENT_ONE
        elif a == ELEMENT_ZERO:
            i = ELEMENT_ZERO
        elif a == ELEMENT_ONE:
            i = ELEMENT_ONE
        elif b == 0:
            i = ELEMENT_ONE
        else:
            i = (a*abs(b)) % self._cycle

        return self(i)

    def do_pack(self, bits):
        """
        Get a integer value from a bit-vector
        Ex: do_pack([1,0,1,1]), gives 11

        Args:
            bits: Bit-vector to convert

        Returns:
            int: Value of given bit-vector
        """
        value = sum([int(bi) << i for i, bi in enumerate(bits[::-1])])
        return int(value)

    def do_unpack(self, value, bit_width=12):
        """
        Get a bit-vector representation of a given value.
        Ex: do_unpack(0b0011, 4), gives [0,0,1,1]

        Args:
            value: Value to get bit-vector
            bit_width: Number of bits of the given vector. Defaults to 12.

        Returns:
            np.array: Bit-vector of given value
        """
        bits = [(value >> i) & 1 for i in range(bit_width)]
        return np.array(bits[::-1], dtype=np.uint8)

    def mat_mul(self, a, b):
        """
        Multiply vector-matrix/matrix-matrix over GF2. Implements the "addition of rows" approach 

        Args:
            a: Vector/Matrix to multiply
            b: Matrix to multiply (cannot be a vector)

        Returns:
            np.array: Result of multiplication
        """
        if np.all(a == 0) or np.all(b == 0):
            ans = np.zeros_like(b[0,:])
        else:
            ans = None
            for ar in np.atleast_2d(a):
                ans_row = None
                for i, ac in enumerate(ar):
                    if ac == 1:
                        ans_row = b[i] if ans_row is None else ans_row ^ b[i]
                ans = ans_row if ans is None else np.vstack((ans, ans_row))

        return ans

    def hamming_weight(self, a):
        """
        Get hamming weight of a given element. Input can be a value or bit-vector
        Ex: hamming_weight(0b1101), gives 3
        
        Args:
            a: Given value or bit-vector

        Returns:
            int: Weight of given element
        """
        if isinstance(a, int):
            a = self.do_unpack(a)
        return np.sum(a)