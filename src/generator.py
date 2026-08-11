import os
import requests

class ERGraphvizGenerator:
	"""Generador que transforma el modelo a DOT y genera SVG vía QuickChart API."""
	
	@staticmethod
	def generar_dot(entidades: dict, relaciones: dict) -> str:
		dot = []
		dot.append("graph G {")
		dot.append("\tlayout=neato; overlap=false; splines=true;bgcolor=\"transparent\";truecolor=true;")
		dot.append("\tnode [fontname=\"Arial\"];")
		
		for ent in entidades.values():
			# 1. Dibujar Entidad
			shape = "box"
			peripheries = 2 if ent.es_debil else 1
			dot.append(f"\t\"{ent.nombre}\" [shape={shape}, peripheries={peripheries}, style=filled, fillcolor=\"#829CAE\"];") #E3F2FD
			
			# Dibujar Atributos
			ERGraphvizGenerator._generar_atributos_dot(ent.nombre, ent.atributos, dot)

			# 2. Dibujar Relación de Herencia (Jerarquía Centralizada)
			if hasattr(ent, 'subclases') and ent.subclases:
				is_total = "total" in ent.caracteristicas
				is_solapado = "solapado" in ent.caracteristicas
				
				label_jerarquia = "o" if is_solapado else "d"
				nodo_jerarquia = f"jerarquia_{ent.nombre}"
				
				# Nodo círculo para jerarquía (d / o)
				dot.append(f"\t\"{nodo_jerarquia}\" [shape=circle, label=\"{label_jerarquia}\", style=filled, fillcolor=\"#829CAE\", fixedsize=true, width=0.4];") #FFE082
				
				# Conexión Superclase -> Círculo (Línea doble si es total)
				# color="black:invis:black" dibuja una línea negra, un espacio invisible y otra negra, logrando la doble línea.
				edge_style = 'color="black:invis:black"' if is_total else 'color="black"'
				dot.append(f"\t\"{ent.nombre}\" -- \"{nodo_jerarquia}\" [{edge_style}];")
				
				# Conexión Círculo -> Subclases
				for sub in ent.subclases:
					dot.append(f"\t\"{nodo_jerarquia}\" -- \"{sub.nombre}\" [color=\"black\"];")

		for rel in relaciones.values():
			peripheries = 2 if rel.es_identificadora else 1
			dot.append(f"\t\"{rel.nombre}\" [shape=diamond, peripheries={peripheries}, style=filled, fillcolor=\"#87A96B\"];") #84A98C
			ERGraphvizGenerator._generar_atributos_dot(rel.nombre, rel.atributos, dot)
			
			for inc in rel.incluye:
				label = f" [label=\"{inc.cardinalidad_str}\"]" if inc.cardinalidad_str else ""
				dot.append(f"\t\"{rel.nombre}\" -- \"{inc.nombre_entidad}\"{label};")

		dot.append("}")
		return "\n".join(dot)

	@staticmethod
	def _generar_atributos_dot(padre_nombre: str, atributos: dict, dot: list):
		for atr in atributos.values():
			texto = atr.nombre
			
			is_pk = atr.es_pk
			is_parcial = any(c in atr.caracteristicas for c in ["parcial", "discriminante"])
			
			# Subrayado normal para Claves Primarias
			if is_pk:
				label = f"<<U>{texto}</U>>"
			# Subrayado + Cursiva para Claves Parciales / Discriminantes
			elif is_parcial:
				label = f"<<U><I>{texto}</I></U>>"
			# Texto regular para el resto
			else:
				label = f"\"{texto}\""
				
			dot.append(f"\t\"{padre_nombre}_{atr.nombre}\" [label={label}, shape=ellipse, style=filled, fillcolor=\"#C9867A\"];") #F5F5F5
			dot.append(f"\t\"{padre_nombre}\" -- \"{padre_nombre}_{atr.nombre}\";")
			
			if atr.sub_atributos:
				sub_dict = {sa.nombre: sa for sa in atr.sub_atributos}
				ERGraphvizGenerator._generar_atributos_dot(f"{padre_nombre}_{atr.nombre}", sub_dict, dot)

	@staticmethod
	def generar_svg_via_quickchart(dot_content: str, ruta_salida_svg: str):
		print("☁️ Enviando modelo a QuickChart API para generación SVG...")
		# Pasamos el formato por URL en lugar de en el JSON para evitar conflictos
		url = 'https://quickchart.io/graphviz?format=svg'
		
		try:
			# Enviamos el contenido como texto plano (utf-8) en la variable 'data' en lugar de 'json'
			# Esto evita que la API intente parsear JSON y caiga en errores de sintaxis
			response = requests.post(url, data=dot_content.encode('utf-8'))
			
			if response.status_code == 200:
				with open(ruta_salida_svg, 'w', encoding='utf-8') as f:
					f.write(response.text)
				print(f"🎉 ¡Imagen SVG vectorial generada con éxito en: '{ruta_salida_svg}'!")
			else:
				print(f"❌ Error devuelto por la API de QuickChart: {response.text}")
		except Exception as e:
			print(f"❌ Error de red al intentar conectar con QuickChart: {e}")