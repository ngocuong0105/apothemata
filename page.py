class Page(object):
    def __init__(self, title:str) -> None:
        self.title = title

    @staticmethod
    def load(title) -> None:
        raise NotImplementedError
