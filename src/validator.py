from lark import Token, Tree
from models import ValidationError, Entidad, Atributo, Relacion, IncluyeRelation

class ERSemanticValidator:
	def __init__(self):
		self.errores = []
		self.entidades_definidas = {}
		self.relaciones_definidas = {}

	def validar(self, ast) -> list:
		self.errores.clear()
		self.entidades_definidas.clear()
		self.relaciones_definidas.clear()

		self._recorrer_nodo(ast)
		self._validar_existencias_y_cardinalidades()
		self._validar_entidades_debiles()

		return self.errores

	# --- Funciones Auxiliares para búsqueda de nodos ---
	def _get_token(self, nodo, token_type):
		for child in nodo.children:
			if isinstance(child, Token) and child.type == token_type:
				return child
		return None

	def _get_tree(self, nodo, tree_data):
		for child in nodo.children:
			if isinstance(child, Tree) and child.data == tree_data:
				return child
		return None

	def _extraer_chars(self, nodo_props):
		if nodo_props:
			return [c.children[0].value for c in nodo_props.children if c.children]
		return []

	# --- Motor Principal ---
	def _recorrer_nodo(self, nodo, context_obj=None):
		if not isinstance(nodo, Tree):
			return

		if nodo.data == 'entidad':
			token_nombre = self._get_token(nodo, 'NAME')
			nodo_props = self._get_tree(nodo, 'props_entidad')

			chars = self._extraer_chars(nodo_props)
			nueva_entidad = Entidad(token_nombre, chars)

			# NUEVO: Establecer relación de herencia si está dentro de otra entidad
			if isinstance(context_obj, Entidad):
				nueva_entidad.padre = context_obj
				context_obj.subclases.append(nueva_entidad)

			if token_nombre.value in self.entidades_definidas:
				self.errores.append(ValidationError(token_nombre, f"La entidad '{token_nombre.value}' ya existe."))
			else:
				self.entidades_definidas[token_nombre.value] = nueva_entidad

			for hijo in nodo.children:
				self._recorrer_nodo(hijo, nueva_entidad)
			return

		elif nodo.data == 'atributo':
			token_nombre = self._get_token(nodo, 'NAME')
			nodo_props = self._get_tree(nodo, 'props_atributo')
			nodo_tipo = self._get_tree(nodo, 'tipo_dato_def')
			
			chars = self._extraer_chars(nodo_props)
			tipo_dato = nodo_tipo.children[0].value if nodo_tipo else None
			nuevo_atributo = Atributo(token_nombre, chars, tipo_dato)

			if isinstance(context_obj, Entidad):
				if token_nombre.value in context_obj.atributos:
					self.errores.append(ValidationError(token_nombre, f"Atributo duplicado en entidad."))
				else:
					context_obj.atributos[token_nombre.value] = nuevo_atributo
			elif isinstance(context_obj, Atributo):
				context_obj.sub_atributos.append(nuevo_atributo)
			elif isinstance(context_obj, Relacion):
				context_obj.atributos[token_nombre.value] = nuevo_atributo

			for hijo in nodo.children:
				self._recorrer_nodo(hijo, nuevo_atributo)
			return

		elif nodo.data == 'relacion':
			token_nombre = self._get_token(nodo, 'NAME')
			nodo_props = self._get_tree(nodo, 'props_relacion')
			
			es_id = nodo_props is not None
			nueva_rel = Relacion(token_nombre, es_id)
			self.relaciones_definidas[token_nombre.value] = nueva_rel

			for hijo in nodo.iter_subtrees():
				if hijo.data == 'incluye_stmt':
					token_entidad = self._get_token(hijo, 'NAME')
					nodo_card_def = self._get_tree(hijo, 'card_def')
					card_str = "1:1" # Valor por defecto
					
					if nodo_card_def:
						nc = nodo_card_def.children[0]
						if nc.data == 'card_pair': card_str = f"({nc.children[0]},{nc.children[1]})"
						elif nc.data == 'card_uml': card_str = f"{nc.children[0]}..{nc.children[1]}"
						elif nc.data == 'card_max': card_str = f"{nc.children[0]}"

					nueva_rel.incluye.append(IncluyeRelation(token_entidad, card_str))

			for hijo in nodo.children:
				self._recorrer_nodo(hijo, nueva_rel)
			return

		for hijo in nodo.children:
			self._recorrer_nodo(hijo, context_obj)

	def _validar_existencias_y_cardinalidades(self):
		for rel in self.relaciones_definidas.values():
			for inc in rel.incluye:
				if inc.nombre_entidad not in self.entidades_definidas:
					self.errores.append(ValidationError(inc.token_entidad, f"La entidad '{inc.nombre_entidad}' no existe."))

	def _validar_entidades_debiles(self):
		ents_en_id = set()
		for rel in self.relaciones_definidas.values():
			if rel.es_identificadora:
				for inc in rel.incluye: ents_en_id.add(inc.nombre_entidad)
		
		for nombre, entidad in self.entidades_definidas.items():
			if entidad.es_debil and nombre not in ents_en_id:
				self.errores.append(ValidationError(entidad.token_nombre, f"La entidad débil '{nombre}' no posee relación identificadora."))