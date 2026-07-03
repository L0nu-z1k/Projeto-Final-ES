class ErroNegocio(Exception):
    pass


class IsbnDuplicadoError(ErroNegocio):
    pass


class IsbnNaoEncontradoError(ErroNegocio):
    pass


class AnoInvalidoError(ErroNegocio):
    pass
