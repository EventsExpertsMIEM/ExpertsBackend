class Error(Exception):
    pass


class QuestionNotFound(Error):

    def __init__(self, id):
        self.id = id
