class ImageIOError(Exception):
    """Erro base do módulo de I/O de imagem."""

class ImageReadError(ImageIOError):
    pass

class ImageWriteError(ImageIOError):
    pass

class ImageShapeError(ImageIOError):
    pass