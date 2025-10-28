from datetime import datetime

class Expediente:
    def __init__(self, id, nombre, edad, peso, raza, tamano, tipo, fecha=None, historial_clinico=None):
        self.id = id
        self.nombre = nombre
        self.edad = edad
        self.peso = peso
        self.raza = raza
        self.tamano = tamano
        self.tipo = tipo
        self.fecha = fecha if fecha else datetime.now().strftime("%d/%m/%Y")
        self.historial_clinico = historial_clinico if historial_clinico else []

    def agregar_historial(self, enfermedad, tratamiento):
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.historial_clinico.append({
            "fecha": fecha,
            "enfermedad": enfermedad,
            "tratamiento": tratamiento
        })
        self.enfermedad = enfermedad  # Última enfermedad

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "edad": self.edad,
            "peso": self.peso,
            "raza": self.raza,
            "tamano": self.tamano,
            "tipo": self.tipo,
            "fecha": self.fecha,
            "enfermedad": getattr(self, 'enfermedad', ''),
            "historial_clinico": self.historial_clinico
        }

    @staticmethod
    def from_dict(data):
        return Expediente(
            id=data["id"],
            nombre=data["nombre"],
            edad=data["edad"],
            peso=data["peso"],
            raza=data["raza"],
            tamano=data["tamano"],
            tipo=data["tipo"],
            fecha=data.get("fecha"),
            historial_clinico=data.get("historial_clinico", [])
        )
