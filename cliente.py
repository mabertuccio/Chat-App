import socket # Importa el módulo socket para manejar conexiones de red
import threading # Importa el módulo threading para manejar hilos

class Cliente:

    # Inicializa la clase Cliente
    def __init__(self, host = "127.0.0.1", port = 5000):
        self.host = host # Dirección del servidor
        self.port = port # Puerto del servidor
        self.BUFFER_SIZE = 1024 # Tamaño del buffer para recibir datos
        self.nickname = input("Ingresa tu 'Nickname': ") # Solicita al cliente su apodo
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #  Crea un socket TCP, AF_INET para IPv4 y SOCK_STREAM para que sea TCP
        self.conectarConServidor() # Intenta conectarse al servidor

    # Método para conectarse al servidor
    def conectarConServidor(self):
        try:
            # Intenta conectarse al servidor utiliznado la dirección y el puerto
            self.cliente.connect((self.host, self.port))
            print("\033[92m[CLIENTE]: Conectado al servidor.\033[0m") # Mensaje de conexión exitosa
            self.iniciarHilos() # Llama al método para inicar los hilos
        except:
            # Manejo de errores en caso de fallo de la conexión
            print("\033[91m[CLIENTE]: Error al conectar al servidor.\033[0m")

    # Método para inicar los hilos para recibir y enviar mensajes
    def iniciarHilos(self):
        recibirThread = threading.Thread(target=self.recibirMensaje) # Crea un hilo para recibir mensajes
        recibirThread.start() # Inicia el hilo de la recepción

        escribirThread = threading.Thread(target=self.escribirMensaje) # Crea un hilo para enviar mensajes
        escribirThread.start() # Inicia el hilo de envío

    # Método para recibir mensajes del servidor
    def recibirMensaje(self):
        while True:
            try:
                mensaje = self.cliente.recv(self.BUFFER_SIZE) # Recibe un mensaje del servidor
                # Si el servidor envía el comando para pedir el apodo
                if mensaje == b"@nickname":
                    self.cliente.send(self.nickname.encode("utf-8")) # Envía el apodo al servidor
                else:
                    # De lo contrario, imprime el mensaje recibido
                    print(f"\n\033[94m{mensaje.decode('utf-8')}\033[0m") # Imprime el mensaje en azul
            except:
                # Manejo de errores en caso de problemas en la conexión
                print("\033[91m[CLIENTE]: Ocurrió un error en la conexión.\033[0m") # Mnesaje de error
                self.cliente.close() # Cierra el socket del cliente
                break # Sale del bucle infinito

    # Método para enviar mensajes al servidor
    def escribirMensaje(self):
        while True: 
            mensaje = input('') # Espera a que el usuario ingrese un mensaje

            # Si el usuario recibe un comando para listar usuarios
            if mensaje == "/listar":
                self.cliente.send(mensaje.encode("utf-8")) # Envía el comando al servidor
            # Si el usuario escribe el comando para desconectar
            elif mensaje == "/desconectar":
                self.cliente.send(mensaje.encode("utf-8")) # Envía el comando de desconexión al servidor
                print("\033[91m[CLIENTE]: Desconectando a todos los usuarios.\033[0m") # Mensaje de desconexión
                break # Sale del bucle infinito del envío
            #
            elif mensaje == "/perfil":
                self.cliente.send(mensaje.encode("utf-8"))  # Envía el comando de perfil al servidor
            # Si el usuario escribe el comando para salir
            elif mensaje == "/salir":
                self.cliente.send(mensaje.encode("utf-8")) # Envía el comando de salida
                print("\033[91m[CLIENTE]: Desconectándote del servidor.\033[0m") # Mensaje de salida
                break # Sale del bucle infinito del envío
            # Para cualquier otro mensaje, lo formatea y lo envía
            else:
                mensajeFormateado = f"{self.nickname}: {mensaje}" # Formatea el mensaje con el apodo
                self.cliente.send(mensajeFormateado.encode("utf-8")) # Envía el mensaje formateado al servidor

# Punto de entrada del programa
if __name__ == "__main__":
    cliente = Cliente() # Crea una instancia de la clase Cliente, iniciando el programa
