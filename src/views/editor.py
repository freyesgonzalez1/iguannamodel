"""Pantalla principal del editor de documentos."""

import flet as ft
from flet_code_editor import CodeEditor, CodeLanguage, CodeTheme

from models import RESERVED_WORDS

class EditorView:
	def __init__(self, page: ft.Page):
		self._page = page
		self._file_picker = ft.FilePicker()
		self._page.services.append(self._file_picker)
		self._file_name = "sin_titulo.mer"

		self._status = ft.Text(value=self._file_name, color="#49454F")
		self._editor = CodeEditor(
			expand=True,
			#padding=ft.Padding.only(bottom=10), # Agrega 30 píxeles de espacio abajo
			language=CodeLanguage.PLAINTEXT,
			autocomplete=True,
			autocomplete_words=RESERVED_WORDS,
			code_theme=CodeTheme.ATOM_ONE_LIGHT,
			text_style=ft.TextStyle(
				color="#49454F",
				font_family="Roboto",
				size=14
			)
		)
		#print( f"{type(self._editor)}" )

		toolbar = ft.Row(
			controls=[
				ft.Button(
					content="Abrir",
					icon=ft.Icons.FOLDER_OPEN,
					on_click=self._open_document,
					bgcolor=ft.Colors.BLUE_100,
					style=ft.ButtonStyle(
						color="#49454F"
					)
				),
				ft.Button(
					content="Guardar",
					icon=ft.Icons.SAVE,
					on_click=self._save_document,
					bgcolor=ft.Colors.BLUE_100,
					style=ft.ButtonStyle(
						color="#49454F"
					)
				),
				self._status,
			]
		)
		button = ft.PopupMenuButton(
			icon=ft.Icons.POST_ADD,
			key="popup",
			icon_size=32,
			#shape=ft.CircleBorder(),
			bgcolor="#009688",
			icon_color="#009688",
			items=[
				#ft.FloatingActionButton(icon=ft.Icons.ADD),
				#ft.FloatingActionButton(icon=ft.Icons.ADD),
				#ft.FloatingActionButton(icon=ft.Icons.ADD),
				#ft.PopupMenuItem(content="Entidad"),
				#ft.PopupMenuItem(content="Atributo"),
				#ft.PopupMenuItem(content="Relación"),
				ft.PopupMenuItem(
					content=ft.Row([
						ft.IconButton(icon=ft.Icons.FOLDER, icon_color="blue"),
						ft.Text("Test 1")
					]),
					on_click=lambda e: print("Entidad")
				),
				ft.PopupMenuItem(
					content=ft.Row([
						ft.IconButton(icon=ft.Icons.SHARE_ROUNDED, icon_color="grey"),
						ft.Text("Test 2")
					]),
					on_click=lambda e: print("Relación")
				),
				ft.PopupMenuItem(
					content=ft.Row([
						ft.IconButton(icon=ft.Icons.EDIT_ATTRIBUTES, icon_color="grey"),
						ft.Text("Test 3")
					]),
					on_click=lambda e: print("Atributo")
				),
			],
			menu_position=ft.PopupMenuPosition.OVER,
		)
		self.control = ft.SafeArea(
			content=ft.Column(
				controls=[toolbar, self._editor, button],
				expand=True,
			)
		)

	async def _open_document(self, _event):
		selected_files = await self._file_picker.pick_files(
			dialog_title="Abrir documento de texto",
			allow_multiple=False,
			with_data=True,
			file_type=ft.FilePickerFileType.ANY,
		)
		if not selected_files:
			return

		selected = selected_files[0]
		if selected.bytes is None:
			self._status.value = "No se pudo leer el documento seleccionado."
			self._status.update()
			return

		self._editor.value = selected.bytes.decode("utf-8", errors="replace")
		self._file_name = selected.name
		self._status.value = self._file_name
		self._editor.update()
		self._status.update()

	async def _save_document(self, _event):
		destination = await self._file_picker.save_file(
			dialog_title="Guardar documento",
			file_name=self._file_name,
			file_type=ft.FilePickerFileType.ANY,
			src_bytes=(self._editor.value or "").encode("utf-8"),
		)
		if destination:
			self._file_name = destination.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
			self._status.value = self._file_name
			self._status.update()
