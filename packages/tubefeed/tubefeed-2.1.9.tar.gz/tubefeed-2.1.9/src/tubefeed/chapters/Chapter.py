class Chapter:
    def __init__(self, start: int, end: int, title: str):
        self.start: int = start
        self.end: int = end
        self.title: str = title

    def __repr__(self) -> str:
        return f'{self.start}-{self.end}: {self.title}'
