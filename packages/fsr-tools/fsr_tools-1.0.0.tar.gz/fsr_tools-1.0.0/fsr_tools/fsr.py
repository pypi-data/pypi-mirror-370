from abc import ABC, abstractmethod

class FSR(ABC):
    """
    Abstract base class for Linear Feedback/Feedforward Shift Registers.

    An LFSR is a shift register where the new input bit is computed as a 
    linear function (XOR) of selected bits from the current state, 
    as defined by a characteristic polynomial.

    This class provides:
      - Storage and manipulation of the register state
      - Polynomial-to-tap mask conversion
      - Bitwise indexing for state inspection/modification
      - Abstract interface for different LFSR update schemes (e.g., Fibonacci, Galois)

    Args:
        poly (int): Characteristic polynomial in integer form.
                    The binary representation indicates taps, with the MSB
                    corresponding to the highest degree term (register width).
        state (int): Initial seed state of the register.

    Attributes:
        state (int): Current state of the shift register.
        poly (int): Polynomial in integer form.
        field_order (int): Register length in bits (degree of polynomial).
        tap_mask (list[int]): Tap positions as a list of 0/1 flags, LSB-first.

    Notes:
        - Subclasses must implement `round()` to define one shift/update step.
        - The polynomial should be primitive for maximum-length sequences.
    """
    def __init__(self, poly: int, state: int):
        self.state = state
        self.poly = poly
        self.__init_state = state
        self.build_poly()

    def build_poly(self):
        """
        Build the tap mask from the characteristic polynomial.

        This method calculates:
          - The field order (register length in bits) from the polynomial.
          - The tap mask, a list of bits (LSB-first) indicating which positions
            in the register are taps for feedback/feeding.

        The polynomial is interpreted in binary form, with the most significant bit
        corresponding to the highest degree term.

        Example:
            poly = 0b10011  # x^4 + x + 1
            field_order = 5
            tap_mask = [1, 1, 0, 0, 1]  # LSB first

        Args:
            None

        Returns:
            None
        """
        self.field_order = self.poly.bit_length()
        self.tap_mask = [
            int(b) for b in f'{self.poly:0{self.field_order}b}'
        ][::-1]

    @abstractmethod
    def round(self, serial_in=0, tap_in=0) -> int:
        """
        Perform one LFSR shift/update step.

        This method updates the register state by shifting and applying feedback 
        or feedforward logic as defined in subclasses (e.g., Fibonacci, Galois).

        Args:
            serial_in (int, optional): Bit to shift into the register's MSB or LSB 
                (depending on implementation). Defaults to 0.
            tap_in (int, optional): Feedback bit computed from tap positions or 
                previous state output. Defaults to 0.

        Returns:
            int: The updated register state as an integer.
        """
        pass

    def __getitem__(self, reg: int) -> int:
        bits = [int(x) for x in f'{self.state:0{self.field_order}b}'][::-1]
        return bits[reg]

    def __setitem__(self, reg: int, val: int):
        bits = [int(x) for x in f'{self.state:0{self.field_order}b}'][::-1]
        bits[reg] = val
        self.state = int(''.join(str(b) for b in bits), 2)

    @property
    def algebraic(self):
        """
        Get the algebraic form of the characteristic polynomial.

        The polynomial is constructed from the tap mask, with the most 
        significant bit representing the highest degree term. Terms with 
        a coefficient of 1 are included in the output, followed by the 
        constant term `1`.

        Example:
            poly = 0b10011  # x^4 + x + 1
            algebraic = "x^5 + x^2 + 1"

        Returns:
            str: The polynomial in human-readable algebraic form.
        """
        terms = []
        for i, bit in enumerate(self.tap_mask):
            if bit:
                power = self.field_order - i
                terms.append(f'x^{power}' if power > 1 else 'x')
        terms.append('1')
        return ' + '.join(terms)

    @property
    def state_table(self):
        """
        Generate the complete state table for the LFSR.

        Iterates through all possible states of the register (2^n cycles, 
        where n is the register length) by repeatedly calling `round()`.  
        Each cycle records:
          - The cycle index
          - The current state as an integer
          - The current register state as a binary string

        The register is reset to its initial state after generation.

        Returns:
            dict: A dictionary with keys:
                - "Cycle" (list[int]): Cycle numbers from 0 to 2^n - 1.
                - "State" (list[int]): Integer representation of the state.
                - "Register State" (list[str]): Binary string of the state.
        """
        state_table = {'Cycle': [], 'State': [], 'Register State': []}
        for x in range(0, 2 ** self.field_order):
            state_table['Cycle'].append(x)
            state_table['State'].append(self.state)
            state_table['Register State'].append(
                f'{self.state:0{self.field_order}b}'
            )
            self.round(serial_in=0, tap_in=self[0])
        self.reset()
        return state_table

    def cycle(self, rounds: int, serial_in: int, tap_in: int) ->  int:
        """
        Advance the LFSR by a specified number of rounds.

        Repeatedly calls `round()` to update the register state.

        Args:
            rounds (int): Number of shift/update operations to perform.
            serial_in (int): Bit to shift into the register each round.
            tap_in (int): Feedback bit to use each round.

        Returns:
            int: The final register state as an integer after all rounds.
        """
        for _ in range(rounds):
            self.round(serial_in, tap_in)
        return self.state

    def reset(self):
        """
        Reset the register to its initial seed state.

        Sets the current state back to the value provided during initialization.
        """
        self.state = self.__init_state

    def load(self, state: int):
        """
        Load a new state into the register.

        Args:
            state (int): The new register state as an integer.
        """
        self.state = state


class Galois_LFSR(LFSR):
    """
    Galois form Linear Feedforward Shift Register.

    In the Galois configuration, feedback is applied to selected taps
    along the shift path rather than combined before input. This often
    allows for faster updates in hardware.

    Args:
        poly (int): Characteristic polynomial in integer form.
        state (int): Initial seed state of the register.
    """
    def round(self, serial_in=0, tap_in=0) -> int:
        """
        Perform one Galois LFSR shift step.

        Feedback is applied at tap positions as bits are shifted
        toward the output. The leftmost bit (MSB) is replaced with
        the XOR of `serial_in` and `tap_in`.

        Args:
            serial_in (int, optional): Bit to shift into the MSB. Defaults to 0.
            tap_in (int, optional): Feedback bit from the previous state. Defaults to 0.

        Returns:
            int: The updated register state as an integer.
        """
        bits = [int(x) for x in f'{self.state:0{self.field_order}b}'][::-1]
        next_bits = [0] * self.field_order
        next_bits[self.field_order-1] = serial_in ^ tap_in
        for i in range(1, self.field_order):
            if self.tap_mask[i]:
                next_bits[i-1] = bits[i] ^ tap_in;
            else:
                next_bits[i-1] = bits[i]
        self.state = int(''.join(str(b) for b in next_bits[::-1]), 2)
        return self.state


class Fibonacci_LFSR(LFSR):
    """
    Fibonacci form Linear Feedback Shift Register.

    In the Fibonacci configuration, the feedback bit is computed
    by XORing selected taps from the current state and then shifting
    it into the register.

    Args:
        poly (int): Characteristic polynomial in integer form.
        state (int): Initial seed state of the register.
    """
    def round(self, serial_in=0, tap_in=0) -> int:
        """
        Perform one Fibonacci LFSR shift step.

        Feedback is computed from tap positions in the current state,
        XORed with `serial_in`, and shifted into the register's LSB.

        Args:
            serial_in (int, optional): Bit to shift into the LSB. Defaults to 0.
            tap_in (int, optional): Initial feedback value, often the output bit. Defaults to 0.

        Returns:
            int: The updated register state as an integer.
        """
        bits = [int(x) for x in f'{self.state:0{self.field_order}b}'][::-1]
        next_bits = [0] * self.field_order
        feedback = tap_in
        for i in range(0, self.field_order-1):
            next_bits[i+1] = bits[i];
            if self.tap_mask[i]:
                feedback ^= bits[i]
        next_bits[0] = serial_in ^ feedback
        self.state = int(''.join(str(b) for b in next_bits[::-1]), 2)
        return self.state
