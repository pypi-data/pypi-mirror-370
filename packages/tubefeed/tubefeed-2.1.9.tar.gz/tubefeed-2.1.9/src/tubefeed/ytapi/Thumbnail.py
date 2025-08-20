class Thumbnail:
    def __init__(self, name: str, thumbnail: dict):
        self.name: str = name
        self.url: str = thumbnail['url']
        self.width: int = thumbnail['width']
        self.height: int = thumbnail['height']
