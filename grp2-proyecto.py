import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import shutil

class ImagenologiaMedica:
    def __init__(self, ruta_metadata="./metadata.csv", ruta_dataset="./dataset"):
        self.ruta_metadata = ruta_metadata # Ruta al achivo CSV con la metadata
        self.ruta_dataset  = ruta_dataset # Ruta de la carpeta donde se guardan las imagenes

        # Verificar si el archivo existe y no está vacío antes de cargarlo
        if os.path.exists(ruta_metadata) and os.stat(ruta_metadata).st_size > 0:
            self.metadata = pd.read_csv(ruta_metadata)  # Cargar la metadata desde un archivo CSV
        else:
            new_registro = {'CI': [], 'Nombre': [],'Diagnostico': [],'Ruta': []}
            self.metadata = pd.DataFrame(new_registro)  # DataFrame para almacenar la metadata
            print(f"\nEl archivo {ruta_metadata} no existe o esta vacío.")
        self.metadata['CI'] = self.metadata['CI'].astype(str) # Convertir el CI a String

    def validar_imagen(self, ruta_imagen):
        # Verificar si la ruta es un archivo existente y es una imagen
        if os.path.isfile(ruta_imagen) and any(ruta_imagen.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.gif')):
            # Obtener el nombre del archivo
            nombre_archivo = os.path.basename(ruta_imagen)
            # Crear la ruta completa de destino
            ruta_destino = os.path.join(self.ruta_dataset, nombre_archivo)
            return ruta_destino  # Retorna la ruta completa del archivo copiado
        else:
            return None  # Retorna None si la ruta no es válida o no es una imagen
            
    def contar_metadata(self):
        return self.metadata.shape[0]

    def buscar_diagnostico(self, ci):
        # Filtrar el DataFrame para encontrar el registro con el CI especificado
        resultado = self.metadata[self.metadata['CI'] == ci]

        # Devolver la respuesta
        if not resultado.empty:
            return True
        else:
            return False
        
    def registrar_diagnostico(self, ci, nombre, diagnostico, ruta_imagen):
        if self.buscar_diagnostico(ci):
            print(f"\n >>> No se puede crear este diagnóstico, el CI {ci} YA existe en el DataSet <<<")
        else:
            ruta_destino = self.validar_imagen(ruta_imagen)
            if ruta_destino == None:
                print(f"\n >>> Imagen NO válida, por favor revise la ruta y el tipo de archivo <<<")
            else:
                new_registro = {'CI': [ci], 'Nombre': [nombre],'Diagnostico': [diagnostico],'Ruta': [ruta_destino]}
                df_temp = pd.DataFrame(new_registro)
                self.metadata = pd.concat([self.metadata, df_temp], ignore_index=True)
                self.metadata.to_csv(self.ruta_metadata, index=False)
                # Copiar el archivo a la carpeta de destino
                shutil.copyfile(ruta_imagen, ruta_destino)
                print("\n >>> Registro creado correctamente... <<<")

    def modificar_diagnostico(self, ci, nombre, diagnostico, ruta_imagen):
        if self.buscar_diagnostico(ci):
            ruta_destino = self.validar_imagen(ruta_imagen)
            if ruta_destino == None:
                print(f"\n >>> Imagen NO válida, por favor revise la ruta y el tipo de archivo <<<")
            else:
                # Buscamos la dirección de la imagen para este registo
                resultado = self.metadata[self.metadata['CI'] == ci]
                primer_fila = resultado.iloc[0]
                imagen_antigua = primer_fila['Ruta']

                self.metadata.loc[self.metadata['CI'] == ci, 'Nombre'] = nombre
                self.metadata.loc[self.metadata['CI'] == ci, 'Diagnostico'] = diagnostico
                self.metadata.loc[self.metadata['CI'] == ci, 'Ruta'] = ruta_destino
                self.metadata.to_csv(self.ruta_metadata, index=False)

                os.remove(imagen_antigua) # borramos el anterior archivo
                shutil.copyfile(ruta_imagen, ruta_destino) # copiamos el archivo a la carpeta
                print("\n >>> Registro modificado correctamente... <<<")
        else:
            print(f"\n >>> No se puede modificar el diagnóstico, este CI {ci} NO existe en el DataSet <<<")
            
    def eliminar_diagnostico(self, ci):
        if self.buscar_diagnostico(ci):
            # Buscamos la dirección de la imagen para este registo
            resultado = self.metadata[self.metadata['CI'] == ci]
            primer_fila = resultado.iloc[0]
            imagen_antigua = primer_fila['Ruta']
            # Eliminamos el registro index del DataFrame
            self.metadata = self.metadata.drop(self.metadata[self.metadata['CI'] == ci].index)
            self.metadata.to_csv(self.ruta_metadata, index=False)
            os.remove(imagen_antigua) # borramos el archivo de imagenes
            print("\n >>> Eliminación correcta... <<<")
        else:
            print(f"\n >>> No se puede eliminar este diagnóstico, el CI {ci} NO existe en el DataSet <<<")
        
    def imprimir_diagnostico(self, ci):
        if self.buscar_diagnostico(ci):
            resultado = self.metadata[self.metadata['CI'] == ci]
            primer_fila = resultado.iloc[0]
            print("\n Impresión del Diagnóstico")
            print("=============================")
            for columna, valor in primer_fila.items():
                print(f"{columna}: {valor}")
            print(f"Graficar la imagen desde: {primer_fila['Ruta']}")
            # Lee la imagen
            img = mpimg.imread(primer_fila['Ruta'])
            plt.imshow(img)
            plt.title(f"{primer_fila['CI']} - {primer_fila['Nombre']}, {primer_fila['Diagnostico']}")
            plt.show()
        else:
            print(f"\n >>> No se puede imprimir este diagnóstico, el CI {ci} NO existe en el DataSet <<<")

    def imprimir_todo(self):
        print("\nTodos los Diagnósticos")
        print("----------------------")
        if self.contar_metadata() > 0:
            print(self.metadata)

# Interacción con el usuario
if __name__ == "__main__":
    ruta_metadata = './metadata.csv'
    ruta_dataset = './dataset'

    modulo_imagenes = ImagenologiaMedica(ruta_metadata, ruta_dataset)

    while True:
        contador = modulo_imagenes.contar_metadata()
        print("\n--- Menú ---")
        print(f"\nDiagnósticos registrados => [ {contador} ]\n")
        print("1. Registrar nuevo diagnóstico")
        print("2. Modificar un diagnóstico")
        print("3. Eliminar un diagnóstico")
        print("4. Buscar si existe un diagnóstico")
        print("5. Imprimir un diagnóstico")
        print("6. Imprimir todo.")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            ci = input("Ingrese el CI del paciente: ")
            nombre = input("Ingrese el nombre del paciente: ")
            diagnostico = input("Ingrese el diagnóstico del paciente: ")
            ruta_imagen = input("Ingrese la ruta de la imagen: ")
            modulo_imagenes.registrar_diagnostico(ci, nombre, diagnostico, ruta_imagen)
        elif opcion == '2':
            ci = input("Ingrese el CI del paciente: ")
            nombre = input("Ingrese el nuevo nombre: ")
            diagnostico = input("Ingrese el nuevo diagnóstico: ")
            ruta_imagen = input("Ingrese la ruta de la nueva imagen: ")
            modulo_imagenes.modificar_diagnostico(ci, nombre, diagnostico, ruta_imagen)
        elif opcion == '3':
            ci = input("Ingrese el CI del diagnóstico a eliminar: ")
            modulo_imagenes.eliminar_diagnostico(ci)
        elif opcion == '4':
            ci = input("Ingrese el CI del paciente: ")
            if modulo_imagenes.buscar_diagnostico(ci):
                print(f"\n >>> El CI {ci} SI existe en el DataSet <<<")
            else:
                print(f"\n >>> El CI {ci} NO existe en el DataSet <<<")
        elif opcion == '5':
            ci = input("Ingrese el CI del paciente: ")
            modulo_imagenes.imprimir_diagnostico(ci)
        elif opcion == '6':
            modulo_imagenes.imprimir_todo()
        elif opcion == '7':
            break
        else:
            print("Opción no válida. Intente de nuevo.")
