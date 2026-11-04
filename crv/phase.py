from .txn import DEPTH, FILL, DRAIN, WR_ONLY, RD_ONLY


class Phase:
    def __init__(self, depth=DEPTH, dwell=3, burst_every=2):
        self.depth, self.dwell, self.burst_every = depth, dwell, burst_every
        self.phase, self.held = FILL, 0
        self.turns = 0
        self.bursts = 0
        self.queue = []

    def _burst(self):
        if self.bursts % 2 == 0:
            one_way = WR_ONLY if self.phase == FILL else RD_ONLY
            queue = [one_way] * (self.depth + 2)
        else:
            queue = [WR_ONLY, RD_ONLY] * self.depth
        self.bursts += 1
        return queue

    def update(self, count):
        if self.queue:
            return self.queue.pop(0)
        target = self.depth if self.phase == FILL else 0
        self.held = self.held + 1 if count == target else 0
        if self.held > self.dwell:
            self.phase = DRAIN if self.phase == FILL else FILL
            self.held = 0
            self.turns += 1
            if self.burst_every and self.turns % self.burst_every == 0:
                self.queue = self._burst()
                return self.queue.pop(0)
        return self.phase
