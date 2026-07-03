"""
Excepciones de dominio.

Los servicios lanzan estas excepciones (independientes de HTTP); es la capa
API (app/api/*) la que las traduce a códigos de estado HTTP concretos. Así
la lógica de negocio no depende del framework web.
"""


class DominioError(Exception):
    """Excepción base para errores de reglas de negocio."""


class RecursoNoEncontradoError(DominioError):
    pass


class RecursoDuplicadoError(DominioError):
    pass


class CredencialesInvalidasError(DominioError):
    pass


class ReglaNegocioError(DominioError):
    pass
