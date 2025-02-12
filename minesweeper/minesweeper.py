import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If number of cells equals count and count is not 0, all cells are mines
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If count is 0, all cells are safe
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        # 1) Mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) Mark the cell as safe
        self.mark_safe(cell)

        # 3) Add a new sentence to the AI's knowledge base
        # Get all neighboring cells
        neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue
                # Add cell if it's in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))

        # Remove cells that are already known to be safe or mines
        unknown_neighbors = set()
        mine_count = 0
        for neighbor in neighbors:
            if neighbor in self.mines:
                mine_count += 1
            elif neighbor not in self.safes:
                unknown_neighbors.add(neighbor)

        # Add new sentence with remaining unknown cells and adjusted count
        new_sentence = Sentence(unknown_neighbors, count - mine_count)
        self.knowledge.append(new_sentence)

        # Keep checking for new inferences until no more can be made
        while True:
            # Track if we made any changes in this iteration
            progress = False

            # 4) Mark additional cells as safe or mines if possible
            mines_marked = set()
            safes_marked = set()

            # Check each sentence for mines and safes
            for sentence in self.knowledge:
                for mine in sentence.known_mines() - self.mines:
                    mines_marked.add(mine)
                    progress = True
                for safe in sentence.known_safes() - self.safes:
                    safes_marked.add(safe)
                    progress = True

            # Mark all the mines and safes found
            for mine in mines_marked:
                self.mark_mine(mine)
            for safe in safes_marked:
                self.mark_safe(safe)

            # 5) Add new sentences through inference
            new_sentences = []

            # Compare each pair of sentences for subset inference
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1.cells and sentence2.cells and sentence1 != sentence2:
                        if sentence1.cells.issubset(sentence2.cells):
                            new_cells = sentence2.cells - sentence1.cells
                            new_count = sentence2.count - sentence1.count
                            new_sentence = Sentence(new_cells, new_count)
                            
                            # Only add if it's actually new
                            if new_sentence not in self.knowledge and new_cells and new_count >= 0:
                                new_sentences.append(new_sentence)
                                progress = True

            # Add the new sentences to knowledge base
            for sentence in new_sentences:
                self.knowledge.append(sentence)

            # Remove any empty sentences from knowledge base
            self.knowledge = [s for s in self.knowledge if s.cells]

            # If no progress was made, we're done
            if not progress:
                break

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        """
        # Get all possible moves
        possible_moves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    possible_moves.append((i, j))
        
        # Return random move if any exist
        if possible_moves:
            return random.choice(possible_moves)
        return None
