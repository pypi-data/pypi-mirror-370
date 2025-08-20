class Segment:
    def __init__(self, segment: dict):
        self.category: str = segment['category']
        self.action: str = segment['actionType']
        self.start: float = segment['segment'][0]
        self.end: float = segment['segment'][1]
