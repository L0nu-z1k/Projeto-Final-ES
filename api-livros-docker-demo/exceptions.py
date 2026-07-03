"""Exceções personalizadas para erros de negócio da aplicação."""


class ErroNegocio(Exception):
    """Classe base para todos os erros de negócio."""
    pass


class IsbnDuplicadoError(ErroNegocio):
    """Levantada quando tenta-se cadastrar um livro com ISBN já existente."""
    pass


class IsbnNaoEncontradoError(ErroNegocio):
    """Levantada quando o ISBN não é encontrado na API OpenLibrary."""
    pass


class AnoInvalidoError(ErroNegocio):
    """Levantada quando o ano de publicação é inválido ou diverge muito da OpenLibrary."""
    pass
