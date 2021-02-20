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
                        w, h = draw.textsize(letters[i][j], font=font)
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
        # for each 'variable' in the domains dictionary
        # get all the values mapped to that variable
        # remove all the values whose length does not match
        # the length of the variable required
        for variable in self.domains:
            
            domains = self.domains[variable].copy()
            for value in domains:

                if len(value) != variable.length:
                    self.domains[variable].remove(value)
        
        return
        
    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # for each iteration of AC-3 algorithm to maintain arc consistency
        # check if any revisions have to be made
        # that is if the 'domain of x' has to be shrunk by removing a value
        # since it has no satisfiable corresponding value in the 'domain of y'
        revised = False
        overlap = self.crossword.overlaps[x, y]
        if overlap == None:
            return revised
        
        i, j = overlap
        X = self.domains[x].copy()
        Y = self.domains[y]
        for x_value in X:

            satisfied = False
            for y_value in Y:

                if x_value != y_value and x_value[i] == y_value[j]:
                    satisfied = True
                    break
            
            if not satisfied:
                self.domains[x].remove(x_value)
                revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        X = self.domains[x].copy()mpty.
        """

        # there are two cases:
        # case 1: arcs is empty so enforce arc consistency at the beginning
        # initialize queue set by adding all edges (arcs) to it
        # arc (or edge) is simply a tuple (x, y) where
        # x and y are neighboring variables

        if arcs == None:
            q = set()
            for var in self.crossword.variables:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    q.add((var, neighbor))

            while len(q) != 0:  
                x, y = q.pop()
                if self.revise(x, y):

                    if len(self.domains[x]) == 0:
                        return False

                    for x_neighbor in self.crossword.neighbors(x):
                        if x_neighbor != y:
                            q.add((x_neighbor, x))

            return True

        # case 2: arcs is not None
        # this means ac3 is invoked by the backtrack algorithm
        # so ac3 will now generate inferences given the arcs
        # that is, if a var = value assignment has been done by backtrack
        # retrieve all arcs leading from  neighbors of 'var' to 'var'
        # then, enforce arc consistency on these neighbors
        # if this can be done, then return new assignments
        # that is, those cases where domain(neighbor) = single value
        # in the form of a dictionary
        # also, change the original self.domains
        # if arc consistency cannot be maintained, return None
        # and make no change to the original self.domains

        # the revise function is re-written here so that
        # this 'trial' execution does not disturb the original self.domains

        def inference_revise(domainsY, domainsX, overlap):
            revised = False
            if overlap == None:
                return revised
        
            i, j = overlap
            Y = domainsY.copy()
            for y_value in Y:

                satisfied = False
                for x_value in domainsX:

                    if x_value != y_value and y_value[i] == x_value[j]:
                        satisfied = True
                        break
            
                if not satisfied:
                    domainsY.remove(y_value)
                    revised = True

            return revised
        
        q = set(arcs)
        domains = self.domains.copy()
        while len(q) != 0:  
            y, x = q.pop()
            domainsX = domains[x]
            domainsY = domains[y]
            overlap = self.crossword.overlaps[y, x]
            if inference_revise(domainsY, domainsX, overlap):

                if len(domainsY) == 0:
                    return None

                for y_neighbor in self.crossword.neighbors(y):
                    if y_neighbor != x:
                        q.add((y_neighbor, y))

        # make changes if consistent
        self.domains = domains.copy()
        # get new assigments if domain of y has only 1 value
        new_assignment = dict()
        for y, x in arcs:
            if len(self.domains[y]) == 1:
                new_assignment[y] = [value for value in self.domains[y]][0]

        return new_assignment

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # assignment is complete if
        # each variable in the self.crossword.variables
        # has been assigned to a value in the assigment dictionary
        # assignment dictionary only stores one unique value
        # so conflicts don't have to be tested here
        for variable in self.crossword.variables:

            if variable not in assignment:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # check if each assigned value is distinct
        # that is one unique value per variable
        # that is total no. of distinct values == total no. of variables
        # also check node consistency
        distinct = set()
        for variable in assignment:

            value = assignment[variable]
            distinct.add(value)

            if len(value) != variable.length:
                return False

        if len(distinct) != len(assignment):
            return False

        # check arc consistency, separately
        # because requires more computation
        # for there to be arc consistency:
        # the ith letter of variable1 = jth letter of variable2
        # where (i, j) is the overlap of variable1 and variable2
        for variable1 in assignment:

            for variable2 in assignment:

                if variable1 == variable2:
                    continue
                
                overlaps = self.crossword.overlaps[variable1, variable2]
                if overlaps == None:
                    continue
                    
                i, j = overlaps
                if assignment[variable1][i] != assignment[variable2][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # first get those variables that
        # are not yet present in assignment (unassigned)
        # and are also neighbors to var (the vavriable under consideration)

        unassigned = set()
        neighbors = self.crossword.neighbors(var)
        for variable in self.crossword.variables:

            if variable not in assignment and variable in neighbors:
                unassigned.add(variable)
        
        # then create a dictionary that maps
        # a variable to its least-constraining-value heuristic
        # here, heuristic = 
        # (no. of variables affected) +
        # 90% of
        # how many individual values are affected as a fraction of
        # all the values in the domain
        cnt = dict()
        for value in self.domains[var]:
            
            constraint = 0.0
            for variable in unassigned:
                
                count = 0.0
                i, j = self.crossword.overlaps[var, variable]
                weight = 9.0 / (10.0 * len(self.domains[variable]))
                for option in self.domains[variable]:
                    
                    # affected if the option in neighbor = value
                    if value == option:
                        count += 1 * weight
                        continue
                    
                    # affected if arc consistency rules out the option
                    if value[i] != option[j]:
                        count += 1 * weight
                
                if count > 0.0:
                    constraint = constraint + 1.0 + count
                
            cnt[value] = constraint

        # sort the cnt dictionary in ascending order of constraint and list it            
        cnt = {k: v for k, v in sorted(cnt.items(), key=lambda item: item[1])}
        ordered = list(cnt)

        return ordered

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # first get the set of unassigned variables
        unassigned = set()
        for variable in self.crossword.variables:

            if variable not in assignment:
                unassigned.add(variable)

        order = dict()

        # for sorting puposes, here's the trick
        # the priority must be given to the one with the least domain values
        # second priority must be given to the variable with higher degree
        # so make number of domain values the integer
        # convert no. of degrees to a fraction and add to the previous integer
        # any word can have a max of 50 letters, so 50 neighbors
        # so we scale contribution of degrees as a fraction of 50
        # and then scale that by 90% i.e., 9/10
        # but since we sort according to degrees in descending order(higher 1st)
        # we subtract the fraction from 0.9 (highest being 90%)
        # so that higher the degree, lower the fraction
        # and then the whole thing can be sorted in ascending order
        
        wt = 9 / 500
        for var in unassigned:
            
            neighbors = len(self.crossword.neighbors(var))
            order[var] = len(self.domains[var]) + (0.9 - wt * neighbors)

        order = {k: v for k, v in sorted(order.items(), key=lambda item: item[1])}
        order = list(order)

        return order[0]

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
        inferences = dict()

        for value in self.order_domain_values(var, assignment):
            
            assignment[var] = value
            if self.consistent(assignment):

                arcs = [(y, var) for y in self.crossword.neighbors(var)]
                inferences = self.ac3(arcs=arcs)

                if inferences != None:
                    assignment.update(inferences)

                    result = self.backtrack(assignment)
                    if result != None:
                        return result
            
            # if current assignment leads to inconsistency
            # or
            # if current assignment leads to an unsatisfiable inference
            # remove the assignment and the added inferences
            assignment.pop(var)
            for key in inferences:
                assignment.pop(key)     
                    
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
