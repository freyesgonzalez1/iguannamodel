"""Datos del lenguaje del editor."""

RESERVED_WORDS = ["entidad", "atributo", "relacion", "además"]





# IguannaModel
class ValidationError:
	def __init__(self, token, mensaje: str):
		self.linea = token.line
		self.columna = token.column
		self.mensaje = mensaje

	def __str__(self):
		return f"Error Semántico (línea {self.linea}, columna {self.columna}): {self.mensaje}"


class Atributo:
	def __init__(self, token_nombre, caracteristicas: list, tipo_dato: str = None):
		self.nombre = token_nombre.value
		self.caracteristicas = caracteristicas
		self.es_pk = any(c.lower() in [x.lower() for x in ["pk", "clave primaria", "primary key"]] for c in caracteristicas)
		self.tipo_dato = tipo_dato
		self.sub_atributos = []


class Entidad:
	def __init__(self, token_nombre, caracteristicas: list):
		self.nombre = token_nombre.value
		self.linea = token_nombre.line
		self.token_nombre = token_nombre
		self.caracteristicas = [c.lower() for c in caracteristicas]

		self.es_debil = "débil" in self.caracteristicas or "debil" in self.caracteristicas
		self.atributos = {}

		self.padre = None 
		self.subclases = []

		# NUEVO: Propiedades de la jerarquía EER
		# Puedes establecerlas en 'o' (solapada) o 'total' mediante el validador más adelante
		self.jerarquia_tipo = 'd' # 'd' (disjunto) u 'o' (solapado)
		self.jerarquia_cobertura = 'parcial' # 'total' o 'parcial'


class IncluyeRelation:
	def __init__(self, token_entidad, cardinalidad_str="1:1"):
		self.nombre_entidad = token_entidad.value
		self.token_entidad = token_entidad
		# Si cardinalidad_str viene vacío desde el parser, se asume "1:1"
		self.cardinalidad_str = cardinalidad_str if cardinalidad_str else "1:1"


class Relacion:
	def __init__(self, token_nombre, es_identificadora: bool):
		self.nombre = token_nombre.value
		self.es_identificadora = es_identificadora
		self.incluye = []
		self.atributos = {}