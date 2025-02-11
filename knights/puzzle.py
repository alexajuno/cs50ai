from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")


# Define a function simulate Xor for the sentence with the meaning of either A or B but not both
def Xor(A, B):
    return And(Or(A, B), Not(And(A, B)))

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A is either a knight or a knave (but not both)
    Xor(AKnight, AKnave),
    
    # If A is a knight, then what they said is true
    # If A is a knave, then what they said is false
    Biconditional(AKnight, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A is either a knight or a knave (but not both)
    Xor(AKnight, AKnave),
    # B is either a knight or a knave (but not both)
    Xor(BKnight, BKnave),
    
    # If A is a knight, then what they said is true
    # If A is a knave, then what they said is false
    Biconditional(AKnight, And(AKnave, BKnave))
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A is either a knight or a knave (but not both)
    Xor(AKnight, AKnave),
    # B is either a knight or a knave (but not both)
    Xor(BKnight, BKnave),
    
    # If A is a knight, then what they said is true (same kind)
    # If A is a knave, then what they said is false (different kind)
    Biconditional(AKnight, Or(And(AKnight, BKnight), And(AKnave, BKnave))),
    
    # If B is a knight, then what they said is true (different kind)
    # If B is a knave, then what they said is false (same kind)
    Biconditional(BKnight, Or(And(AKnight, BKnave), And(AKnave, BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave.'"
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # Each character is either a knight or a knave (but not both)
    Xor(AKnight, AKnave),
    Xor(BKnight, BKnave),
    Xor(CKnight, CKnave),
    
    # B's first statement about what A said
    Biconditional(BKnight, Biconditional(AKnight, AKnave)),
    
    # B's second statement that C is a knave
    Biconditional(BKnight, CKnave),
    
    # C's statement that A is a knight
    Biconditional(CKnight, AKnight)
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
