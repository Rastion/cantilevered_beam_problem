import math
import random
from qubots.base_problem import BaseProblem

class CantileveredBeamProblem(BaseProblem):
    """
    Cantilevered Beam Problem

    Design the cross-section of a cantilevered I-beam to minimize its volume 
    subject to constraints on bending stress and tip deflection.

    The volume of the beam is defined as:
      V = (2 * fh1 * b1 + (H - 2 * fh1) * b2) * L

    where:
      - H is the overall beam height.
      - fh1 is the flange height, selected from a predefined list.
      - b1 is the width of the upper flange.
      - b2 is the width of the web.
      - L is the beam length.

    The moment of inertia is computed as:
      I = (1/12) * b2 * (H - 2*fh1)^3 + 2 * ( (1/12) * b1 * fh1^3 + (b1 * fh1 * (H - fh1)^2)/4 )

    Constraint functions:
      - Bending stress: g1 = P * L * H / (2 * I)   ≤ 5000
      - Tip deflection: g2 = P * L^3 / (3 * E * I)  ≤ 0.10

    Constants:
      P = 1000
      E = 10e6
      L = 36
      possibleValues = [0.1, 0.26, 0.35, 0.5, 0.65, 0.75, 0.9, 1.0]

    Decision variables:
      - H ∈ [3.0, 7.0] (float)
      - h1 ∈ {0,1,...,7} (integer index into possibleValues for flange height fh1)
      - b1 ∈ [2.0, 12.0] (float)
      - b2 ∈ [0.1, 2.0] (float)
    """

    def __init__(self):
        # Constants
        self.P = 1000
        self.E = 10e6
        self.L = 36
        self.possibleValues = [0.1, 0.26, 0.35, 0.5, 0.65, 0.75, 0.9, 1.0]
        # Define variable bounds
        self.bounds = {
            "H": (3.0, 7.0),
            "h1": (0, len(self.possibleValues) - 1),  # h1 is an index into possibleValues
            "b1": (2.0, 12.0),
            "b2": (0.1, 2.0)
        }
    
    def evaluate_solution(self, solution) -> float:
        """
        Evaluate a candidate solution.

        The candidate solution should be a list of four numbers: [H, h1, b1, b2],
        where H, b1, b2 are continuous and h1 is a (possibly non-integer) value 
        that is rounded to the nearest integer and used to index the possibleValues list.

        Returns the beam volume if the design satisfies:
          - Bending stress constraint: g1 ≤ 5000
          - Deflection constraint:      g2 ≤ 0.10

        Otherwise, returns a high penalty value.
        """
        PENALTY = 1e9
        if not isinstance(solution, (list, tuple)) or len(solution) != 4:
            return PENALTY
        
        H = solution[0]
        # Round h1 to the nearest integer
        h1 = int(round(solution[1]))
        if h1 < self.bounds["h1"][0] or h1 > self.bounds["h1"][1]:
            return PENALTY
        fh1 = self.possibleValues[h1]
        b1 = solution[2]
        b2 = solution[3]
        
        # Check continuous bounds
        if not (self.bounds["H"][0] <= H <= self.bounds["H"][1]):
            return PENALTY
        if not (self.bounds["b1"][0] <= b1 <= self.bounds["b1"][1]):
            return PENALTY
        if not (self.bounds["b2"][0] <= b2 <= self.bounds["b2"][1]):
            return PENALTY
        
        # Compute moment of inertia I
        try:
            term1 = (1/12.0) * b2 * (H - 2 * fh1) ** 3
            term2 = 2 * ((1/12.0) * b1 * fh1 ** 3 + (b1 * fh1 * (H - fh1) ** 2) / 4.0)
            I = term1 + term2
        except Exception:
            return PENALTY
        if I <= 0:
            return PENALTY
        
        # Compute constraint functions:
        g1 = self.P * self.L * H / (2 * I)       # bending stress
        g2 = self.P * self.L**3 / (3 * self.E * I) # deflection
        
        # Check constraints: if any violated, return penalty.
        if g1 > 5000 or g2 > 0.10:
            return PENALTY
        
        # Compute the beam volume (objective)
        volume = (2 * fh1 * b1 + (H - 2 * fh1) * b2) * self.L
        return volume

    def random_solution(self):
        """
        Generate a random candidate solution.
        
        H is chosen uniformly in [3.0, 7.0],
        h1 is a random integer between 0 and 7,
        b1 is chosen uniformly in [2.0, 12.0],
        b2 is chosen uniformly in [0.1, 2.0].
        """
        H = random.uniform(self.bounds["H"][0], self.bounds["H"][1])
        h1 = random.randint(self.bounds["h1"][0], self.bounds["h1"][1])
        b1 = random.uniform(self.bounds["b1"][0], self.bounds["b1"][1])
        b2 = random.uniform(self.bounds["b2"][0], self.bounds["b2"][1])
        return [H, h1, b1, b2]
