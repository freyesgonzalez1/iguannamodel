import flet as ft
from views.editor import EditorView

import os
from lark import Lark
from validator import ERSemanticValidator
from generator import ERGraphvizGenerator
import requests





grammar = r"""
?start: program
program: object*
?object: entidad | atributo | relacion | agregacion

// Las propiedades ahora van antes del nombre. La "i" indica Case-Insensitive (acepta ENTIDAD, entidad, etc.)
entidad: "entidad"i props_entidad? NAME ["{" entidad_content* "}"]
props_entidad: "<" entidad_char ("," entidad_char)* ">"
!entidad_char: "débil"i | "debil"i | "fuerte"i | "total"i | "parcial"i | "disjunto"i | "solapado"i
?entidad_content: entidad | atributo

atributo: "atributo"i props_atributo? NAME [tipo_dato_def] ["{" atributo_content* "}"]
props_atributo: "<" atributo_char ("," atributo_char)* ">"
!atributo_char: "pk"i | "clave primaria"i | "primary key"i | "multivalorado"i | "derivado"i | "nulo"i | "discriminante"i
tipo_dato_def: ":" TIPO_DATO
TIPO_DATO: "NUMÉRICO"i | "NUMERICO"i | "PALABRA"i | "FECHA"i
?atributo_content: atributo

relacion: "relacion"i props_relacion? NAME ["{" relacion_content* "}"]
props_relacion: "<" "identificador"i ">"
?relacion_content: incluye_stmt | atributo

incluye_stmt: "incluye"i NAME [card_def]
card_def: ":" cardinalidad
cardinalidad: "(" CARD_VAL "," CARD_VAL ")" -> card_pair
            | CARD_VAL ".." CARD_VAL       -> card_uml
            | CARD_VAL                     -> card_max

agregacion: "agregacion"i NAME "{" agregacion_content* "}"
?agregacion_content: entidad | relacion

CARD_VAL: /[0-9a-zA-Z\*]+/
NAME: /[a-zA-Z_áéíóúÁÉÍÓÚñÑ][a-zA-Z0-9_\-áéíóúÁÉÍÓÚñÑ]*/

// REGLAS DE COMENTARIOS
COMMENT: /#[^\n]*/
MULTILINE_COMMENT: /"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3}/

%import common.WS
%ignore WS
%ignore COMMENT
%ignore MULTILINE_COMMENT"""
def ejecutar_interprete(ruta_codigo: str, ruta_gramatica: str, ruta_grafico: str):
	#if not os.path.exists(ruta_codigo) or not os.path.exists(ruta_gramatica):
	#   print("Faltan archivos esenciales para arrancar.")
	#   return
	#print( f"GRAMÁTICA : {ruta_gramatica}" )
	#with open(ruta_gramatica, 'r', encoding='utf-8') as f:
	#   gramatica = f.read()
	try:
		f = open(ruta_gramatica, 'r', encoding='utf-8').read()
	except:
		gramatica = grammar
	
	#with open(ruta_codigo, 'r', encoding='utf-8') as f:
	#   codigo = f.read()
	codigo = ruta_codigo
	parser = Lark(gramatica, parser='lalr')


	# https://quickchart.io/documentation/graphviz-api/
	# https://quickchart.io/graphviz?format=png&width=100&height=150&graph=graph{a--b}
	try:
		ast = parser.parse(codigo)
		validador = ERSemanticValidator()
		errores = validador.validar(ast)

		if errores:
			print(f"❌ No se puede generar la imagen debido a {len(errores)} errores semánticos:")
			for e in errores: print(f"  {e}")
		else:
			print("🎉 Código semánticamente correcto.")
			img = ERGraphvizGenerator.generar_dot(
				entidades=validador.entidades_definidas,
				relaciones=validador.relaciones_definidas,
				#ruta_salida=ruta_grafico
			)
			#print( f"GRAFO :{img}" )
			# Configure API parameters
			payload = {
				"graph": img,
				"format": "svg",  # Options: 'png' or 'svg'
				"width": 400,
				"height": 300
			}
			response = requests.post("https://quickchart.io/graphviz", json=payload)
			#print( response.text )
			return True, response.content

	except Exception as e:
		#print(f"🚨 Error de Sintaxis:\n{e}")
		return False, f"🚨 Error de Sintaxis:\n{e}"

#if __name__ == "__main__":
#   ejecutar_interprete("mer/arriendo.mer", "grammar.lark", "output_diagrama.dot")

model_example = '''"""
Ejemplo Maestro ER:
- Herencia total y disjunta (doble línea, círculo con 'd')
- Entidades débiles y atributos discriminantes
- Todos los formatos de cardinalidad
"""

ENTIDAD<fuerte, total, disjunto> Persona {
    atributo<pk> rut : PALABRA
    atributo nombre : PALABRA
    atributo fechaNacimiento : FECHA

    # Subclases anidadas (Herencia)
    ENTIDAD Profesor {
        atributo especialidad : PALABRA
    }
    
    ENTIDAD Estudiante {
        atributo matricula : NUMERICO
    }
}

entidad<debil> CargaFamiliar {
    # Clave parcial o discriminante (Se dibujará con borde de nodo discontinuo)
    atributo<discriminante> numeroCorrelativo : NUMERICO
    atributo nombre : PALABRA
}

relacion<identificador> Posee_Carga {
    # 1. Cardinalidad formato UML (min..max)
    incluye Persona : 1..1
    # 2. Cardinalidad formato de tuplas (min, max)
    incluye CargaFamiliar : (1, *)
}

relacion Imparte {
    # 3. Cardinalidad formato numérico único (maximo)
    incluye Profesor : 1
    # 4. Cardinalidad implícita (No definida, el validador asume 1:1)
    incluye Curso
}

ENTIDAD Curso {
    atributo<pk> codigo : NUMERICO
    atributo titulo : PALABRA
}'''

def main(page: ft.Page):
	page.padding = 0
	page.title = "Iguanna Model"
	page.theme_mode = ft.ThemeMode.DARK

	background = ft.Container(expand=True, bgcolor="#FEFFF8")

	def update_background(e):
		colors = [ft.Colors.INDIGO_400, ft.Colors.PINK_300, ft.Colors.TEAL_300]
		background.bgcolor = colors[int(e.data)]
		if page_view.selected_index == 0:
			pass
		if page_view.selected_index == 1:
			pass
		if page_view.selected_index == 2:
			pass
			print( "Actualizar pantalla 2" )
			#model = page_view.controls[1].content.content.controls[1].value if page_view.controls[1].content.content.controls[1].value else "No hay texto"
			#correcto, res = ejecutar_interprete(model, "grammar.lark", "output_diagrama.dot") # "mer/arriendo.mer"
			#if correcto:
			#	page_view.controls[2].content = ft.Image(src=res, width=200, height=200,)
			#else:
			#	print( res )
			#	page_view.controls[2].content = ft.Text(str(res), color="#424242"),
		page.update()


	page_view = ft.PageView(
		expand=True,
		viewport_fraction=0.9,
		on_change=update_background,
		selected_index=1,
		horizontal=True,
	)

	wheel_locked = True

	async def change_with_wheel(e):
		nonlocal wheel_locked

		if wheel_locked or e.scroll_delta.y == 0:
			return

		wheel_locked = True
		if e.scroll_delta.y > 0:
			await page_view.next_page(animation_duration=150)
		else:
			await page_view.previous_page(animation_duration=150)
		wheel_locked = False

	async def show_first_page(e):
		await page_view.go_to_page(index=0, animation_duration=150)

	async def show_second_page(e):
		await page_view.go_to_page(index=1, animation_duration=150)

	async def show_third_page(e):
		await page_view.go_to_page(index=2, animation_duration=150)
		response = page_view.controls[1].content.content.controls[1].value if page_view.controls[1].content.content.controls[1].value else None
		if response is not None:
			correcto, response = ejecutar_interprete(response, "grammar.lark", "output_diagrama.dot") # "mer/arriendo.mer"
			if correcto:
				response = ft.Image(src=response, width=200, height=200,)
			else:
				response = ft.Text(str(response), color="#424242")
		else:
			correcto, response = False, ft.Text(str("No hay modelo"), color="#424242")
		page_view.controls[2].content = response
		page_view.controls[2].update()

	editor = EditorView(page)

	page_view.controls = [
		ft.Container(
			bgcolor="#F3F4EE",
			ink=True,
			on_click=show_first_page,
			content=ft.Column(
				alignment=ft.MainAxisAlignment.CENTER,
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				controls=[
					ft.Text("Ejemplo", text_align=ft.TextAlign.LEFT, size=40, weight=ft.FontWeight.BOLD, color="#49454F"),
					ft.Text(model_example, text_align=ft.TextAlign.LEFT, color="#49454F", size=12),
				],
			),
		),
		ft.Container(
			bgcolor="#FFFFFF",
			ink=True,
			padding=12,
			on_click=show_second_page,
			content=editor.control,
		),
		ft.Container(
			bgcolor="#F7F9F2",
			ink=True,
			on_click=show_third_page,
			content=ft.Text("Initial Text"),
			#content = ft.Image(
			#	#src="https://raw.githubusercontent.com/dnfield/flutter_svg/master/packages/flutter_svg/example/assets/wikimedia/Firefox_Logo_2017.svg",
			#	src="metroid.svg",
			#	width=200,
			#	height=200,
			#),
		),
	]

	background.content = ft.GestureDetector(
		content=page_view,
		on_scroll=change_with_wheel,
	)
	page.add(ft.SafeArea(expand=True, content=background))


#if __name__ == "__main__":
#	ft.run(main)
ft.run(main, export_asgi_app=True)