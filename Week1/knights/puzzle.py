from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
Aclaim0 = And(AKnight, AKnave)
# a person can be a knight or a knave but not both(XOR = not(biconditional))
# if the person is a knight, then the claim must be true and vice-versa
# if the person is a knave, then the claim must be false and vice-versa
knowledge0 = And(
    Not(Biconditional(AKnave, AKnight)),
    Or(Biconditional(AKnight, Aclaim0),
        Biconditional(AKnave, Not(Aclaim0)))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
Aclaim1 = And(AKnave, BKnave)
knowledge1 = And(
    Not(Biconditional(AKnave, AKnight)),
    Not(Biconditional(BKnave, BKnight)),
    Or(Biconditional(AKnight, Aclaim1)),
    Biconditional(AKnave, Not(Aclaim1))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
# AKnave and BKnave or AKnight and BKnight (but not both)
# AKnave and BKnight or AKnight and BKnave
Aclaim2 = Or(And(AKnave, BKnave), And(AKnight, BKnight))
Bclaim2 = Or(And(AKnave, BKnight), And(AKnight, BKnave))
knowledge2 = And(
    Not(Biconditional(AKnave, AKnight)),
    Not(Biconditional(BKnave, BKnight)),
    Or(Biconditional(AKnight, Aclaim2),
        Biconditional(AKnave, Not(Aclaim2))),
    Or(Biconditional(BKnight, Bclaim2),
        Biconditional(BKnave, Not(Bclaim2)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
Aclaim3 = Or(AKnight, AKnave)
Bclaim3 = Or(Biconditional(AKnight, AKnave),
             Biconditional(AKnave, Not(AKnave)))
Bclaim4 = CKnave
Cclaim3 = AKnight
knowledge3 = And(
    Not(Biconditional(AKnave, AKnight)),
    Not(Biconditional(BKnave, BKnight)),
    Not(Biconditional(CKnave, CKnight)),
    Or(Biconditional(AKnight, Aclaim3),
        Biconditional(AKnave, Not(Aclaim3))),
    Or(Biconditional(BKnight, Bclaim3),
        Biconditional(BKnave, Not(Bclaim3))),
    Or(Biconditional(BKnight, Bclaim4),
        Biconditional(BKnave, Not(Bclaim4))),
    Or(Biconditional(CKnight, Cclaim3),
        Biconditional(CKnave, Not(Cclaim3)))
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
