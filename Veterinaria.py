import random
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox, ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from expediente import Expediente
#_________________________________________________________________
import json
import os

from veterinaria import expediente


class BaseExpedientes:
    archivo_bd = "expedientes.json" #archivo donde se guarda y carga .json

    def __init__(self):
        self.expedientes = self.cargar_expedientes()

    #acciones que realiza la clase BaseExpedientes
    #____________cargar expediente____________
    #____________actualizar expediente____________
    #____________agregar expediente____________
    #____________eliminar expediente___________
    #____________buscar expediente____________
    def cargar_expedientes(self):
        if os.path.exists(self.archivo_bd):
            with open(self.archivo_bd, "r", encoding="utf-8") as f:
                try:
                    datos = json.load(f)
                    return [Expediente.from_dict(d) for d in datos]
                except json.JSONDecodeError:
                    return []
        return []

    def actualizar_expedientes(self):
        with open(self.archivo_bd, "w", encoding="utf-8") as f:
            json.dump([exp.to_dict() for exp in self.base.expedientes], f, indent=4, ensure_ascii=False)

    def agregar_expediente(self, expediente):
        if any(e.id == expediente.id for e in self.expedientes):
            raise ValueError(f"Ya existe un expediente con ID {expediente.id}")
        self.expedientes.append(expediente)
        self.actualizar_expedientes()

    def eliminar_expediente(self, id_exp):
        self.expedientes = [e for e in self.expedientes if e.id != id_exp]
        self.actualizar_expedientes()

    def buscar_expedientes(self, termino):
        termino = str(termino).strip().lower()
        resultados = []
        for exp in self.expedientes:
            for valor in exp.to_dict().values():
                if termino in str(valor).strip().lower():
                    resultados.append(exp)
                    break
        return resultados
#_________________________________________________________________
class Veterinaria():

    def __init__(self):
        # ________________Crear ventana principal__________________

        self.root = tk.Tk()  # Creo ventana principal
        self.root.title("Veterinaria")
        self.root.config(bg="#FCBBE8")
        self.root.geometry('300x500')  # Tamaño de la ventana 400px por 250px
        self.base = BaseExpedientes()  # Instancia del gestor de expedientes
        self.expedientes = self.base.expedientes
        self.tipo_animal_seleccionado = None

        # ------------------ Cargar imágenes ------------------
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        def cargar_img(nombre):
            try:
                ruta = os.path.join(BASE_DIR, nombre)
                img = Image.open(ruta).resize((100, 95))
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"⚠️ No se pudo cargar {nombre}: {e}")
                return None

        self.img_canino = cargar_img("imagenes_vet/canino.png")
        self.img_felino = cargar_img("imagenes_vet/felino.png")
        self.img_ave = cargar_img("imagenes_vet/ave.png")
        self.img_default = cargar_img("imagenes_vet/default.png")

        # ------------------ Panel principal ------------------

        # crear Contenedores
        # Panel principal blanco
        self.panel_informativo = tk.Frame(self.root, bg="white", height=490, width=290, )
        self.panel_informativo.pack(padx=10, pady=10)
        self.panel_informativo.pack_propagate(False)

        #_________________ Panel imagen de ventana principal________________
        self.panel_imagen = tk.Frame(self.panel_informativo, bg="white", height=200, width=270)
        self.panel_imagen.place(relx=0.5, rely=0.26, anchor="center")
        self.panel_imagen.pack_propagate(False)

        # ___________Panel para botones de opciones en ventana principal_______
        self.panel_opciones = tk.Frame(self.panel_informativo, bg="white", height=240, width=270)
        self.panel_opciones.place(relx=0.5, rely=0.7, anchor="center")
        self.panel_opciones.pack_propagate(False)

        # Botónes de panel principal new expediente / buscar
        #________Boton new expediente______
        self.imagen_new_expediente = Image.open("imagenes_vet/new-expediente.png")
        self.imagen_new_expediente = self.imagen_new_expediente.resize((130, 130))
        self.imagen_new_expediente = ImageTk.PhotoImage(self.imagen_new_expediente)

        self.boton_new_expediente = tk.Button(self.panel_opciones, image=self.imagen_new_expediente,
                                        command=lambda:RegistroExpediente(self), borderwidth=0, bg="white",
                                        activebackground="white")
        self.boton_new_expediente.pack(side="left", padx=10)

        #________Boton buscar expediente____________
        self.imagen_buscar = Image.open("imagenes_vet/buscar.png")
        self.imagen_buscar = self.imagen_buscar.resize((150, 150))
        self.imagen_buscar = ImageTk.PhotoImage(self.imagen_buscar)

        self.boton_buscar = tk.Button(
            self.panel_opciones,
            image=self.imagen_buscar,
            command=lambda:BuscarExpediente(self),
            borderwidth=0,
            bg="white",
            activebackground="white"
        )
        self.boton_buscar.pack(side="left")


        # __________________________Etiquetas panel principal______________________
        # Etiqueta de título principal
        self.etiqueta_titulo = tk.Label(self.panel_informativo, text='Pet´s Clinic', fg="#CC27F5",
                                        wraplength=200, bg="white",
                                        font=('Arial Rounded MT Bold', 20))
        self.etiqueta_titulo.place(relx=0.5, rely=0.08, anchor="center")

        # Etiqueta de pregunta
        self.etiqueta_pregunta = tk.Label(self.panel_informativo, text='¡Bienvenido!, selecciona una opción...',
                                          wraplength=300,
                                          bg="white",
                                          font=('Arial', 16))
        self.etiqueta_pregunta.place(relx=0.5, rely=0.5, anchor="center")

        # Imagen de panel principal

        self.imagen_logo = Image.open("imagenes_vet/logo.png")
        self.imagen_logo = self.imagen_logo.resize((150, 150))
        self.imagen_logo = ImageTk.PhotoImage(self.imagen_logo)

        self.etiqueta_imagen = tk.Label(self.panel_imagen, image=self.imagen_logo,
                                        bg="white")
        self.etiqueta_imagen.place(relx=0.5, rely=0.55, anchor="center")

        # Ejecutar la ventana
        self.root.mainloop()
#_________________________________________________________________
class RegistroExpediente:

    def crear_boton_redondeado(self, canvas, x1, y1, x2, y2, r, texto, comando, bg_color, fg_color):
        puntos = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]

        boton_id = canvas.create_polygon(puntos, smooth=True, fill=bg_color, outline="")
        texto_id = canvas.create_text(
            (x1 + x2) // 2,
            (y1 + y2) // 2,
            text=texto,
            fill=fg_color,
            font=('Arial', 12, 'bold'),
            width=(x2 - x1) - 10,
            justify="center"
        )

        def on_click(event):
            if comando:
                comando()

        canvas.tag_bind(boton_id, "<Button-1>", on_click)
        canvas.tag_bind(texto_id, "<Button-1>", on_click)
    def __init__(self, master):

        self.base = master.base
        self.ventana_exp = tk.Toplevel(master.root)
        self.ventana_exp.title("Registrar expediente")
        self.ventana_exp.config(bg="#FCBBE8")
        self.ventana_exp.geometry("600x360")

        self.expedientes = master.expedientes
        self.img_canino = master.img_canino
        self.img_felino = master.img_felino
        self.img_ave = master.img_ave
        self.tipo_animal_seleccionado = None

#______________________________________________________________________________


        # Panel formulario
        self.panel_form = tk.Frame(self.ventana_exp, bg="white", height=350, width=300)
        self.panel_form.place(relx=0.725, rely=0.5, anchor="center")

        # Panel de selección (izquierda)
        self.panel_sel = tk.Frame(self.ventana_exp, bg="white", height=250, width=250)
        self.panel_sel.place(relx=0.23, rely=0.55, anchor="center")

        if self.img_canino:
            lbl = tk.Label(self.panel_sel, image=self.img_canino, bg="white")

            lbl.image = self.img_canino
            lbl.place(relx=0.2, rely=0.3, anchor="center")
            lbl.bind("<Button-1>", lambda e: self.seleccionar_tipo("Canino"))

        if self.img_felino:
            lbl = tk.Label(self.panel_sel, image=self.img_felino, bg="white")
            lbl.image = self.img_felino
            lbl.place(relx=0.7, rely=0.3, anchor="center")
            lbl.bind("<Button-1>", lambda e: self.seleccionar_tipo("Felino"))

        if self.img_ave:
            lbl = tk.Label(self.panel_sel, image=self.img_ave, bg="white")
            lbl.image = self.img_ave
            lbl.place(relx=0.45, rely=0.7, anchor="center")
            lbl.bind("<Button-1>", lambda e: self.seleccionar_tipo("Ave"))

        tk.Label(self.ventana_exp, text="Registro de Expediente", bg="white",
                 font=("Arial Rounded MT Bold", 14), fg="#4A5C5A").place(relx=0.25, rely=0.1, anchor="center")
        self.etiqueta_tipo_titulo = tk.Label(
            self.panel_form,
            text="",
            bg="white",
            font=("Arial Rounded MT Bold", 14),
            fg="#4A5C5A"
        )
        self.etiqueta_tipo_titulo.place(relx=0.5, rely=0.05, anchor="center")


        # Etiquetas
        self.etiqueta_fecha = tk.Label(self.panel_form, text='Fecha: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_fecha.place(relx=0.62, rely=0.1)

        self.etiqueta_name = tk.Label(self.panel_form, text='ID: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_name.place(relx=0.02, rely=0.1)

        self.etiqueta_name = tk.Label(self.panel_form, text='Nombre: ',
                                          wraplength=300,
                                          bg="white",
                                          font=('Arial', 8))
        self.etiqueta_name.place(relx=0.02, rely=0.2)

        self.etiqueta_edad = tk.Label(self.panel_form, text='Edad: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_edad.place(relx=0.02, rely=0.3)

        self.etiqueta_peso = tk.Label(self.panel_form, text='Peso: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_peso.place(relx=0.02, rely=0.4)

        self.etiqueta_tipo = tk.Label(self.panel_form, text='Tipo: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_tipo.place(relx=0.65, rely=0.3)

        self.etiqueta_raza = tk.Label(self.panel_form, text='Raza: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_raza.place(relx=0.45, rely=0.4)

        self.etiqueta_tamano = tk.Label(self.panel_form, text='Tamano: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_tamano.place(relx=0.02, rely=0.5)

        self.etiqueta_enf = tk.Label(self.panel_form, text='Enfermedad: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_enf.place(relx=0.02, rely=0.6)

        self.etiqueta_tra = tk.Label(self.panel_form, text='Tratamiento: ',
                                      wraplength=300,
                                      bg="white",
                                      font=('Arial', 8))
        self.etiqueta_tra.place(relx=0.02, rely=0.73)

        # Campos de formulario
        self.caja_name = tk.Entry(self.panel_form, width=38)
        self.caja_name.place(relx=0.18, rely=0.2, )


        self.caja_age = tk.Entry(self.panel_form, width=10)
        self.caja_age.place(relx=0.18, rely=0.3)


        self.caja_peso = tk.Entry(self.panel_form, width=10)
        self.caja_peso.place(relx=0.18, rely=0.4)


        self.caja_raza = tk.Entry(self.panel_form, width=20)
        self.caja_raza.place(relx=0.6, rely=0.4)


        self.caja_tamano = tk.Entry(self.panel_form, width=20)
        self.caja_tamano.place(relx=0.18, rely=0.5)


        self.caja_enf = tk.Entry(self.panel_form, width=40)
        self.caja_enf.place(relx=0.02, rely=0.66)


        self.caja_trat = tk.Entry(self.panel_form, width=40)
        self.caja_trat.place(relx=0.02, rely=0.8)


        self.caja_fecha = tk.Entry(self.panel_form, width=10)
        self.caja_fecha.place(relx=0.75, rely=0.1)
        self.caja_fecha.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.caja_fecha.config(state="readonly")  # para que no se pueda editar

        self.caja_id = tk.Entry(self.panel_form, width=10, state="readonly")
        self.caja_id.place(relx=0.18, rely=0.1)

        self.caja_tipo = tk.Entry(self.panel_form, width=10, state="readonly")
        self.caja_tipo.place(relx=0.75, rely=0.3)

               # Canvas para el botón "guardar"
        self.boton_canvas_guardarexp = tk.Canvas(self.panel_form, width=160, height=40, bg="white",
                                               highlightthickness=0)
        self.boton_canvas_guardarexp.place(relx=0.6, rely=0.95, anchor="center")

        # Botón redondeado con tu función
        self.crear_boton_redondeado(
            canvas=self.boton_canvas_guardarexp,
            x1=0, y1=0, x2=130, y2=30, r=20,
            texto="Guardar",
            comando=self.guardar_expediente,
            bg_color="#F665A1",
            fg_color="white"
        )

    # -------------------------metodos generales----------------------------
    #_________guardar_expediente

    #_________sirve para seleccionar la imagen y corresponda al tipo de anima (diseñp)
    def seleccionar_tipo(self, tipo):
        self.tipo_animal_seleccionado = tipo

        # Actualizar etiqueta del tipo
        self.etiqueta_tipo_titulo.config(text=f"Nuevo expediente {tipo.lower()}")

        # Actualizar entrada tipo
        self.caja_tipo.config(state="normal")
        self.caja_tipo.delete(0, tk.END)
        self.caja_tipo.insert(0, tipo)
        self.caja_tipo.config(state="readonly")

        # Asignar un ID aleatorio
        nuevo_id = random.randint(1000, 9999)
        self.caja_id.config(state="normal")
        self.caja_id.delete(0, tk.END)
        self.caja_id.insert(0, nuevo_id)
        self.caja_id.config(state="readonly")

        self.etiqueta_tipo_titulo.config(text=f"Nuevo expediente {tipo.lower()}")

    # ---------------------guardar los datos de expediente--------------------------------
    def guardar_expediente(self):
        try:  # (intenta)
            nombre = self.caja_name.get()
            edad = float(self.caja_age.get())
            peso = float(self.caja_peso.get())
            raza = self.caja_raza.get()
            tamano = self.caja_tamano.get()
            enfermedad = self.caja_enf.get()
            tratamiento = self.caja_trat.get()
            fecha = datetime.now().strftime("%d/%m/%Y")  # Fecha automática (día/mes/año)
            tipo = self.tipo_animal_seleccionado or self.caja_tipo.get()
            id_exp = int(self.caja_id.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, selecciona la imagen de acuerdo al animal.")
            return

        # Verificar que no exista expediente con el mismo ID
        for e in self.expedientes:
            if int(e.id) == int(id_exp):
                messagebox.showwarning("Advertencia", f"Ya existe un expediente con ID {id_exp}.")
                return



        expediente_obj = Expediente(
            id=id_exp,
            nombre=nombre,
            edad=edad,
            peso=peso,
            raza=raza,
            tamano=tamano,
            tipo=tipo,
            historial_clinico=[{"fecha": fecha, "enfermedad": enfermedad, "tratamiento": tratamiento}]
        )
        # Cargar los datos existentes del archivo JSON
        try:
            self.base.agregar_expediente(expediente_obj)
            self.expedientes = self.base.expedientes
            messagebox.showinfo("Registro exitoso", f"Expediente de {tipo} guardado correctamente.")
        except ValueError as e:
            messagebox.showwarning("Advertencia", str(e))
#_________________________________________________________________
class BuscarExpediente:

    def __init__(self, master):
        self.master = master
        self.ventana_busca = tk.Toplevel(master.root)
        self.ventana_busca.title("Buscar Expediente")
        self.ventana_busca.config(bg="#FCBBE8")
        self.ventana_busca.geometry("900x500")
        self.ventana_busca.resizable(width=False, height=False)  # Permite cambio de tamaño o no

        self.base = master.base
        self.expedientes = self.base.expedientes
        self.img_canino = master.img_canino
        self.img_felino = master.img_felino
        self.img_ave = master.img_ave
        self.img_default = master.img_default
        self.tipo_animal_seleccionado = None

        #__________________________________________________________________



        # Panel búsqueda PRINCIPAL(diseño)
        self.panel_busqueda = tk.Frame(self.ventana_busca, bg="#F45CFF", height=50, width=900)
        self.panel_busqueda.pack_propagate(False)
        self.panel_busqueda.pack(side="top", fill="x")
        #Panel donde se diseña busqueda (diseño)
        self.caja_busqueda = tk.Entry(self.panel_busqueda, width=30)
        self.caja_busqueda.pack(side="left", padx=10, ipady=3)
        self.boton_busqueda = tk.Button(self.panel_busqueda, text="🔍", command=self.buscar)
        self.boton_busqueda.pack(side="left")

        # Panel Treeview (lista de expedientes)(diseño)
        self.panel_expedientes = tk.Frame(self.ventana_busca, bg="#FCBBE8", height=400, width=600)
        self.panel_expedientes.pack_propagate(False)
        self.panel_expedientes.pack(side="left", fill="both", padx=10, pady=10)

        self.columnas = ("ID", "Nombre", "Tipo", "Edad", "Raza")
        self.tree = ttk.Treeview(self.panel_expedientes, columns=self.columnas, show="headings")
        for col in self.columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=50, anchor="center")  # ancho columnas
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<ButtonRelease-1>", self.seleccionar_expediente)

        # Panel detalle (diseño)
        self.panel_detalle = tk.Frame(self.ventana_busca, bg="#F45CFF", height=400, width=280)
        self.panel_detalle.pack_propagate(False)
        self.panel_detalle.pack(side="right", padx=10, pady=10)

        # Panel botones (diseño)
        self.panel_botones_detalle = tk.Frame(self.panel_detalle, bg="#F45CFF", height=40, width=160, )
        self.panel_botones_detalle.pack_propagate(False)
        self.panel_botones_detalle.place(relx=0.5, rely=0.9, anchor="center")

        # Imagen por defecto (diseño)
        self.img_default = Image.open("imagenes_vet/default.png").resize((200, 200))
        self.img_default = ImageTk.PhotoImage(self.img_default)
        self.etiqueta_foto = tk.Label(self.panel_detalle, image=self.img_default, bg="#F45CFF")
        self.etiqueta_foto.image = self.img_default  # mantener referencia
        self.etiqueta_foto.pack(pady=10)

        # Etiquetas de detalle (diseño)
        self.etiqueta_nombre = tk.Label(self.panel_detalle, text="", bg="#F45CFF", font=('bold', 10))
        self.etiqueta_nombre.pack()
        self.etiqueta_tipo = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_tipo.pack()
        self.etiqueta_edad = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_edad.pack()
        self.etiqueta_raza = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_raza.pack()
        self.etiqueta_tamano = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_tamano.pack()
        self.etiqueta_fecha = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_fecha.pack()
        self.etiqueta_enfermedad = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_enfermedad.pack()
        self.etiqueta_tratamiento = tk.Label(self.panel_detalle, text="", bg="#F45CFF")
        self.etiqueta_tratamiento.pack()

        # Botones actualizar / eliminar/ PDF (diseño)

        self.imagen_actualizar = Image.open("imagenes_vet/actualizar.png")
        self.imagen_actualizar = self.imagen_actualizar.resize((20, 20))
        self.imagen_actualizar = ImageTk.PhotoImage(self.imagen_actualizar)

        self.boton_actualizar = tk.Button(
            self.panel_botones_detalle,
            image=self.imagen_actualizar,
            command=lambda: ActualizarExpediente(self),
            borderwidth=0,
            bg="white",
            activebackground="white"
        )
        self.boton_actualizar.pack(side="left")

        self.imagen_eliminar = Image.open("imagenes_vet/eliminar.png")
        self.imagen_eliminar = self.imagen_eliminar.resize((20, 20))
        self.imagen_eliminar = ImageTk.PhotoImage(self.imagen_eliminar)

        self.boton_eliminar = tk.Button(self.panel_botones_detalle, image=self.imagen_eliminar,
                                        command=self.eliminar_expediente, borderwidth=0, bg="white",
                                        activebackground="white")
        self.boton_eliminar.pack(side="left", padx=40)

        self.imagen_pdf = Image.open("imagenes_vet/PDF.png")
        self.imagen_pdf = self.imagen_pdf.resize((20, 20))
        self.imagen_pdf = ImageTk.PhotoImage(self.imagen_pdf)

        self.boton_pdf = tk.Button(self.panel_botones_detalle, image=self.imagen_pdf,
                                   command=self.exportar_pdf, borderwidth=0, bg="white",
                                   activebackground="white")
        self.boton_pdf.pack(side="left")

        # Cargar expedientes desde archivo
        self.expedientes = self.base.expedientes
        self.mostrar_expedientes()

        # _____________________metodos en general____________________

        ##______________actualiza expediente______________
        ##______________muestra los detalles del expedientes______________
        # ______________elimina expediente______________
        #______________exporta PDF______________

    #____________metodos en general__________
    #____________busca expedientes por cualquier caracter_________
    # ____________selecciona expediente_________
    # ____________muestra expedientes_________
    #_________elimina el expediente seleccionado y confirma con mensajes________
    #________mensajes de confirmación de la exportacion y seleccion__________

    def mostrar_expedientes(self, filtrados=None):
        for item in self.tree.get_children():
            self.tree.delete(item)
        lista = filtrados if filtrados is not None else self.base.expedientes
        for exp in lista:
            self.tree.insert("", "end", values=(exp.id, exp.nombre, exp.tipo, exp.edad, exp.raza))
    def buscar(self):
        termino = self.caja_busqueda.get()
        resultados = self.base.buscar_expedientes(termino)
        self.mostrar_expedientes(filtrados=resultados)
    def seleccionar_expediente(self, event=None):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        id_exp = int(values[0])
        expediente = next((e for e in self.expedientes if e.id == id_exp), None)
        if not expediente:
            return

        # Actualizar etiquetas

        self.etiqueta_nombre.config(text=f"Nombre: {expediente.nombre}")
        self.etiqueta_tipo.config(text=f"Tipo: {expediente.tipo}")
        self.etiqueta_edad.config(text=f"Edad: {expediente.edad}")
        self.etiqueta_raza.config(text=f"Raza: {expediente.raza}")
        self.etiqueta_tamano.config(text=f"Tamaño: {expediente.tamano}")
        if expediente.historial_clinico:
            ultimo = expediente.historial_clinico[-1]
            self.etiqueta_fecha.config(text=f"Fecha: {ultimo['fecha']}")
            self.etiqueta_enfermedad.config(text=f"Enfermedad: {ultimo['enfermedad']}")

        else:
            self.etiqueta_fecha.config(text="Fecha: Sin registro")
            self.etiqueta_enfermedad.config(text="Enfermedad: Sin registro")


        # Historial clínico
        historial_texto = ""
        for h in expediente.historial_clinico:  # accediendo directamente a la lista del objeto
            historial_texto += f"{h['fecha']} | {h['enfermedad']} | {h['tratamiento']}\n"
        self.etiqueta_tratamiento.config(text=historial_texto or "Sin registros")

        # Imagen según tipo
        tipo = getattr(expediente, 'tipo', '').lower()
        if tipo == "canino":
            img = self.img_canino
        elif tipo == "felino":
            img = self.img_felino
        elif tipo == "ave":
            img = self.img_ave
        else:
            img = self.img_default

        self.etiqueta_foto.config(image=img)
        self.etiqueta_foto.image = img
    def eliminar_expediente(self):
        seleccionado = self.tree.selection()
        if not seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un expediente para eliminar")
            return

        item = self.tree.item(seleccionado)
        valores = item["values"]
        id_exp = int(valores[0])

        confirmar = messagebox.askyesno("Confirmar", "¿Desea eliminar este expediente?")
        if not confirmar:
            return

        # Eliminar de la base
        self.base.eliminar_expediente(id_exp)
        self.expedientes = self.base.expedientes

        # Actualizar lista visual
        self.mostrar_expedientes()

        messagebox.showinfo("Éxito", "Expediente eliminado correctamente")
    def exportar_pdf(self):
        sel = self.tree.focus()
        if not sel:
            return messagebox.showerror("Error", "Selecciona un expediente primero")

        id_exp = int(self.tree.item(sel, "values")[0])
        exp = next((e for e in self.expedientes if e.id == id_exp), None)
        if not exp:
            return messagebox.showerror("Error", "No se encontró el expediente.")

        # 📁 Guardar en Descargas
        ruta = os.path.join(os.path.expanduser("~"), "Downloads", f"Expediente_{exp.nombre}.pdf")

        c = canvas.Canvas(ruta, pagesize=letter)
        y = 750
        for k, v in exp.__dict__.items():
            c.drawString(80, y, f"{k.capitalize()}: {v}")
            y -= 25
        c.save()
        messagebox.showinfo("PDF Exportado", f"✅ Guardado en:\n{ruta}")
#_________________________________________________________________
class ActualizarExpediente():

    def crear_boton_redondeado(self, canvas, x1, y1, x2, y2, r, texto, comando, bg_color, fg_color):
        puntos = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]

        boton_id = canvas.create_polygon(puntos, smooth=True, fill=bg_color, outline="")
        texto_id = canvas.create_text(
            (x1 + x2) // 2,
            (y1 + y2) // 2,
            text=texto,
            fill=fg_color,
            font=('Arial', 12, 'bold'),
            width=(x2 - x1) - 10,
            justify="center"
        )

        def on_click(event):
            if comando:
                comando()

        canvas.tag_bind(boton_id, "<Button-1>", on_click)
        canvas.tag_bind(texto_id, "<Button-1>", on_click)
    def __init__(self,master):

        self.base = master.base
        selected = master.tree.focus()
        if not selected:
            messagebox.showerror("Error", "Selecciona un expediente primero")
            return

        values = master.tree.item(selected, "values")
        id_exp = int(values[0])
        expediente = next((e for e in master.expedientes if e.id == id_exp), None)
        if not expediente:
            messagebox.showerror("Error", "No se encontró el expediente.")
            return


        # ---- Ventana de actualización ----(diseño)
        self.ventana_act = tk.Toplevel(master.master.root)
        self.ventana_act.title("Actualizar padecimiento")
        self.ventana_act.config(bg="#FCBBE8")
        self.ventana_act.geometry("400x350")

        self.panel_actualizar = tk.Frame(self.ventana_act, bg="white", height=340, width=390)
        self.panel_actualizar.pack_propagate(False)
        self.panel_actualizar.pack(side="left", fill="both", padx=10, pady=10)

        self.expedientes = master.expedientes
        self.img_canino = master.img_canino
        self.img_felino = master.img_felino
        self.img_ave = master.img_ave
        self.tipo_animal_seleccionado = None

        tk.Label(self.panel_actualizar, text="Actualizar Expediente", bg="white",
                 font=("Arial Rounded MT Bold", 14), fg="white").pack(pady=10)

        tk.Label(self.panel_actualizar, text=f"ID: {expediente.id}", bg="white").pack()
        tk.Label(self.panel_actualizar, text=f"Nombre: {expediente.nombre}", bg="white").pack()

        if expediente.historial_clinico:
            ultimo = expediente.historial_clinico[-1]
            fecha_actual = ultimo.get("fecha", "Sin fecha")
            enfermedad_actual = ultimo.get("enfermedad", "")
            tratamiento_actual = ultimo.get("tratamiento", "")
        else:
            fecha_actual = "Sin fecha"
            enfermedad_actual = ""
            tratamiento_actual = ""

        tk.Label(self.panel_actualizar, text=f"Fecha actual: {fecha_actual}", bg="white").pack(pady=5)

        # ---- Campos editables ----
        tk.Label(self.panel_actualizar, text="Enfermedad:", bg="white").pack()
        caja_enf = tk.Entry(self.panel_actualizar, width=30)
        caja_enf.insert(0, enfermedad_actual)
        caja_enf.pack(pady=3)

        tk.Label(self.panel_actualizar, text="Tratamiento:", bg="white").pack()
        caja_trat = tk.Entry(self.panel_actualizar, width=30)
        caja_trat.insert(0, tratamiento_actual)
        caja_trat.pack(pady=3)

        #_____________metodos en general___________

        def guardar_cambios():
            nueva_enf = caja_enf.get().strip()
            nuevo_trat = caja_trat.get().strip()
            if not nueva_enf or not nuevo_trat:
                messagebox.showerror("Error", "Enfermedad y tratamiento son obligatorios")
                return

            fecha = datetime.now().strftime("%d/%m/%Y")

            # Crear lista de historial_clinico si no existe
            if not hasattr(expediente, "historial_clinico"):
                expediente.historial_clinico = []

            # Agregar nuevo tratamiento
            expediente.historial_clinico.append({
                "fecha": fecha,
                "enfermedad": nueva_enf,
                "tratamiento": nuevo_trat
            })

            # Actualizar atributo si existe
            expediente.enfermedad = nueva_enf

            # Guardar en archivo
            self.base.actualizar_expedientes()
            self.expedientes = self.base.expedientes
            master.expedientes = self.base.expedientes  # ← sincroniza también en el panel principal
            master.mostrar_expedientes()
            master.seleccionar_expediente(None)
            messagebox.showinfo("Actualizado", "Tratamiento agregado correctamente.")
            self.ventana_act.destroy()


        ##_________________diseño____________
        # Canvas para el botón "Guardar"
        self.boton_canvas_guardar = tk.Canvas(self.panel_actualizar, width=160, height=40, bg="white",
                                              highlightthickness=0)
        self.boton_canvas_guardar.place(relx=0.35, rely=0.8, anchor="center")

        # Botón redondeado de guardar con tu función
        self.crear_boton_redondeado(
            canvas=self.boton_canvas_guardar,
            x1=0, y1=0, x2=130, y2=30, r=20,
            texto="Guardar",
            comando=guardar_cambios,
            bg_color="#F665A1",
            fg_color="white"
        )

        # Canvas para el botón "Cancelar"
        self.boton_canvas_cancelar = tk.Canvas(self.panel_actualizar, width=160, height=40, bg="white",
                                               highlightthickness=0)
        self.boton_canvas_cancelar.place(relx=0.75, rely=0.8, anchor="center")

        # Botón redondeado cancelar con tu función
        self.crear_boton_redondeado(
            canvas=self.boton_canvas_cancelar,
            x1=0, y1=0, x2=130, y2=30, r=20,
            texto="Cancelar",
            comando=lambda :self.ventana_act.destroy(),
            bg_color="#F665A1",
            fg_color="white"
        )


from datetime import datetime
# ____________________________________________________________
# Ejecutar aplicación
veterinaria = Veterinaria()
##esto espara ver el historial de cambios en github

