import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Copy a new word domains
        new_domains = {
            var: self.domains[var].copy()
            for var in self.crossword.variables
        }
        for var in self.crossword.variables:
            for word in self.domains[var]:
                if len(word) != var.length:
                    new_domains[var].remove(word)
        self.domains = new_domains

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        i, j = self.crossword.overlaps[x, y]
        
        # Create a copy of the domain to avoid modifying while iterating
        to_remove = set()
        
        # Check each word in x's domain
        for x_word in self.domains[x]:
            # Check if there's any word in y's domain that satisfies the constraint
            if not any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                to_remove.add(x_word)
                revised = True
        
        # Remove incompatible words after iteration is complete
        self.domains[x] -= to_remove
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Initialize arcs
        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))
        while arcs:
            x, y = arcs.pop()
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arcs.append((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all words have correct lengths
        for var in assignment:
            if len(assignment[var]) != var.length:
                return False
        
        # Check if all words are different
        if len(set(assignment.values())) != len(assignment):
            return False
        
        # Check if there are no conflicts between neighboring variables
        for var in assignment:
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if assignment[var][i] != assignment[neighbor][j]:
                        return False
        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        return sorted(self.domains[var], key=lambda x: self.num_conflicts(x, var, assignment))

    def num_conflicts(self, word, var, assignment):
        """
        Return the number of values ruled out for neighboring variables if word
        is assigned to var.
        """
        conflicts = 0
        
        # Look at all neighbors of this variable
        for neighbor in self.crossword.neighbors(var):
            # Skip neighbors that are already assigned
            if neighbor not in assignment:
                # Get the overlap between the variables
                i, j = self.crossword.overlaps[var, neighbor]
                
                # Count how many values in neighbor's domain would be ruled out
                for neighbor_word in self.domains[neighbor]:
                    if word[i] != neighbor_word[j]:
                        conflicts += 1
                
        return conflicts

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Get the variable not in assignment
        unassigned = [var for var in self.crossword.variables if var not in assignment]
        
        # First, find all variables with minimum remaining values
        min_remaining = min(len(self.domains[var]) for var in unassigned)
        min_vars = [var for var in unassigned if len(self.domains[var]) == min_remaining]
        
        # If there's only one, return it
        if len(min_vars) == 1:
            return min_vars[0]
        
        # If there's a tie, return variable with highest degree (most neighbors)
        return max(min_vars, key=lambda var: len(self.crossword.neighbors(var)))

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var, assignment):
            assignment[var] = word
            if self.consistent(assignment):
                # Create arcs for AC-3 with the newly assigned variable
                arcs = []
                for neighbor in self.crossword.neighbors(var):
                    if neighbor not in assignment:
                        arcs.append((neighbor, var))
                    
                # Save domain copy in case we need to backtrack
                domains_copy = {v: self.domains[v].copy() for v in self.domains}
                
                # Run AC-3 for inference
                if self.ac3(arcs):
                    result = self.backtrack(assignment)
                    if result is not None:
                        return result
                    
                # If inference fails or no solution found, restore domains
                self.domains = domains_copy
            
            assignment.pop(var)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
