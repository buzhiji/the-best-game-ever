
DIRECTIONS = {
    "U": (0, -1),
    "D": (0, 1),
    "L": (-1, 0),
    "R": (1, 0)
}


class MarkovPredictor:
    def __init__(self):

        self.counts = {}

        for direction in DIRECTIONS:
            self.counts[direction] = {
                "U": 0, "D": 0, "L": 0, "R": 0
            }

        self.last_direction = None
        self.transitions_seen = 0
        self.predictions_checked = 0
        self.predictions_correct = 0

    def record(self, dx, dy):
        direction = None

        for name, movement in DIRECTIONS.items():
            if movement == (dx, dy):
                direction = name
                break

        if direction is None:
            return

        if self.last_direction is not None:
            row = self.counts[self.last_direction]

            if sum(row.values()) >= 3:
                guess = max(row, key=row.get)
                self.predictions_checked += 1

                if guess == direction:
                    self.predictions_correct += 1

            # Record the movement
            row[direction] += 1
            self.transitions_seen += 1

        self.last_direction = direction

    def probabilities(self, direction=None):
        if direction is None:
            direction = self.last_direction

        if direction is None:
            return {d: 0.25 for d in DIRECTIONS}

        row = self.counts[direction]
        total = sum(row.values())

        if total == 0:
            return {d: 0.25 for d in DIRECTIONS}

        probabilities = {}

        for d in DIRECTIONS:
            probabilities[d] = row[d] / total

        return probabilities

    def matrix(self):
        result = {}

        for direction in DIRECTIONS:
            result[direction] = self.probabilities(direction)

        return result
