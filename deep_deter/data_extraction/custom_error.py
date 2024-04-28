class NoImagesError(Exception):
    def __init__(self, message='No Images were found with these constraints'):
        self.message = message
        super().__init__(self.message)
