class recursive_queue(object):
    def __init__(self, qsize:int = 200 ):
        self.queue = [ None for _ in range(qsize) ]
        self.qsize = qsize
        self.frontidx = 0
        self.endidx = 0
    def empty(self):
        return (self.frontidx == self.endidx) and (self.front() == None)
    def full(self):
        return (self.frontidx == self.endidx) and (self.front() != None)
    def front(self):
        return self.queue[self.frontidx]
    def end(self):
        return self.queue[self.endidx]
    def size(self):
        dist = self.endidx - self.frontidx
        if dist < 0 :
            dist += self.qsize
        return dist
    def max(self):
        if self.empty():
            return None
        return max([i for i in self.queue if i != None])
    def push(self , num):
        if self.full():
            self.frontidx = (self.frontidx + 1) % self.qsize
        self.queue[self.endidx] = num
        self.endidx = (self.endidx + 1) % self.qsize
        return True
    def pop(self):
        if self.empty():
            return None
        out = self.front()
        self.queue[self.frontidx] = None
        self.frontidx = (self.frontidx + 1) % self.qsize
        return out
    def at(self, idx:int):
        relativeidx = (self.frontidx + idx) % self.qsize
        return self.queue[relativeidx]