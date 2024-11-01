import socket # Importa el módulo socket para manejar conexiones de red
import threading # Importa el módulo threading para manejar múltiples clientes
import pymysql # Importa pymysql para conectarme y manipular la base de datos
from datetime import datetime # Importa datetime para gestionar fechas

class Servidor: # Crea la clase servidor

    # Inicializa el servidor con la dirección y el puerto
    def __init__(self, host = "127.0.0.1", port = 5000):
        self.host = host # Dirección IP del servidor
        self.port = port # Puerto en el que el servidor va a escuchar conexiones
        self.BUFFER_SIZE = 1024 # Tamaño del buffer para recibir datos
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Crea un socket TCP, AF_INET para IPv4 y SOCK_STREAM para que sea TCP
        self.servidor.bind((self.host, self.port)) # Asocia el socket con la dirección y el puerto
        self.servidor.listen() # Comienza a escuchar conexiones entrantes

        print(f"\033[94m[SERVIDOR]: Corriendo en {self.host}:{self.port}.\033[0m") # Mensaje de inicio del servidor

        self.clientes = [] # Lista para almacenar los clientes conectados
        self.nicknames = [] # Lista para almacenar los apodos de los clientes

        # Conexión a la base de datos MySQL
        self.db = pymysql.connect(
            host = "127.0.0.1",
            user = "root",
            password = "",
            database = "chat_db"
        )
        self.cursor = self.db.cursor() # Crea un cursor para ejecutar consultas SQL
        print("\033[92m[SERVIDOR]: Conexión a la base de datos exitosa.\033[0m") # Mensaje de conexión exitosa

    # Método para transmitir un mensaje a los clientes
    def transmitirMensaje(self, mensaje, _cliente):
        mensajeDecodificado = mensaje.decode("utf-8") # Decodifica el mensaje recibido

        # Verifica si el mensaje es privada (es decir, contiene '@' al principio)
        if "@" in mensajeDecodificado:
            partes = mensajeDecodificado.split() # Divide el mensaje en partes
            nombreDestino = partes[1][1:] # Obtiene el nombre del destinatario (sin el '@')

            # Comprueba si el destinatario está en la lista de nicknames
            if nombreDestino in self.nicknames:
                indiceDestino = self.nicknames.index(nombreDestino) # Encuentra el índice del destinatario
                clienteDestino = self.clientes[indiceDestino] # Obtiene el socket del destinatario
                
                indiceRemitente = self.clientes.index(_cliente) # Encuentra el índice del remitente
                nombreRemitente = self.nicknames[indiceRemitente] # Obtiene el nickname del remitente
                
                # Crea el mensaje privado y lo envía al destinatario
                mensajePrivado = f"{nombreRemitente} (Privado): {' '.join(partes[2:])}"
                clienteDestino.send(mensajePrivado.encode("utf-8"))
            else:
                # Envía un mensaje de error si el destinatario no existe
                _cliente.send(f"\033[91m[SERVIDOR]: El usuario '{nombreDestino}' no existe.\033[0m".encode("utf-8"))
        else:
            # Transmite el mensaje a todos los clientes conectados excepto al remitente
            for cliente in self.clientes:
                if cliente != _cliente:
                    cliente.send(mensaje)

    # Método para manejar los mensajes de un cliente
    def manejarMensaje(self, cliente):
        while True:
            try:
                mensaje = cliente.recv(self.BUFFER_SIZE) # Recibe un mensaje del cliente (tipo bytes)
                if not mensaje:
                    break # Sale del bucle si el cliente se desconecta
                    
                mensajeDecodificado = mensaje.decode("utf-8") # Decodifica el mensaje aquí

                # Comprobaciones para comandos especiales
                if mensajeDecodificado == "/listar":
                    self.listarUsuariosConectados(cliente) # Lista los usuarios conectados
                elif mensajeDecodificado == "/desconectar":
                    self.desconectarClientes() # Desconecta a todos los clientes
                    break
                elif mensajeDecodificado == "/perfil":
                    self.obtenerPerfil(cliente) # Muestra la información del usuario
                elif mensajeDecodificado == "/salir":
                    self.desconectarCliente(cliente)  # Desconecta al cliente actual
                else:
                    self.transmitirMensaje(mensaje, cliente) # Transmite el mensaje a otros clientes
            except Exception as e:
                print(f"\033[91m[ERROR]: Ocurrió un error: {e}\033[0m") # Imprime el error
                self.desconectarCliente(cliente) # Desconecta al cliente en caso de error
                break

    # Método para listar los usuarios y enviar la lista al cliente 
    def listarUsuariosConectados(self, cliente):
        listaUsuariosConectados = f"\033[94m[SERVIDOR] - Usuarios Conectados:\n" + "\n".join(self.nicknames) + "\033[0m"
        cliente.send(listaUsuariosConectados.encode("utf-8")) # Envía la lista de usuarios al cliente

    # Método para desonectar a todos los clientes
    def desconectarClientes(self):
        clientesConectados = self.clientes[:] # Copia la lista de clientes conectados

        for cliente in clientesConectados:
            cliente.send("Desconectando a todos los usuarios...".encode("utf-8")) # Informa a cada cliente
            self.desconectarCliente(cliente) # Desconecta al cliente
        self.clientes = [] # Reinicia la lista de clientes
        self.nicknames = [] # Reinicia la lista de nicknames

    # Método para obtener la información del usuario
    def obtenerPerfil(self, cliente):
        indice = self.clientes.index(cliente) # Obtener el índice del cliente en la lista de clientes
        nickname = self.nicknames[indice] # Obtener el nickname del cliente usando el índice encontrado

        cursor = self.db.cursor() # Crear un cursor para realizar consultas en la base de datos
        cursor.execute("SELECT id, created_at, connected_at FROM usuarios WHERE nickname = %s", (nickname,)) # Ejecutar una consulta SQL para obtener el id, fecha de creación y última conexión del usuario
        perfil = cursor.fetchone() # Obtener el primer resultado de la consulta
        
        # Si se encontró un perfil en la base de datos
        if perfil:
            idUsuario, createdAt, connectedAt = perfil # Asignar cada valor de la tupla a variables individuales
            mensajePerfil = f" - ID: {idUsuario}\n - Fecha de Creación: {createdAt}\n - Última Conexión: {connectedAt}" # Formatear el mensaje de perfil con la información obtenida
            cliente.send(mensajePerfil.encode("utf-8"))  # Enviar el mensaje formateado al cliente

    # Método para desconectar un cliente específico
    def desconectarCliente(self, cliente):
        if cliente in self.clientes:
            index = self.clientes.index(cliente) # Obtiene el índice del cliente 
            username = self.nicknames[index] # Obtiene el nickname del cliente
            # Informa a los demás clientes sobre la desconexión
            self.transmitirMensaje(f"\033[91m[SERVIDOR]: {username} se desconectó.\033[0m".encode("utf-8"), cliente)
            self.clientes.remove(cliente) # Elimina al cliente de la lista
            self.nicknames.remove(username) # Elimina al nickname de la lista
            cliente.close() # Cierra el socket del cliente
            print(f"\033[91m[SERVIDOR]: {username} se desconectó.\033[0m") # Mensaje de la desconexión

    # Método para aceptar conexiones entrantes de clientes
    def recibirConexion(self):
        while True:
            cliente, address = self.servidor.accept() # Acepta la conexión del cliente
            cliente.send("@nickname".encode('utf-8')) # Solicita el nickname del cliente
            nickname = cliente.recv(self.BUFFER_SIZE).decode('utf-8') # Recibe el nickname del cliente

            estadoUsuario = self.verificarUsuario(nickname) # Verifica el estado del usuario

            # Si el usuario ya está conectado, cierra la conexión
            if estadoUsuario == "Conectado":
                cliente.send(f"\033[91m[SERVIDOR]: El usuario '{nickname}' ya está conectado desde otra consola.\033[0m".encode("utf-8"))
                cliente.close()
            else:
                self.clientes.append(cliente) # Agrega el cliente a la lista de clientes conectados
                self.nicknames.append(nickname) # Agrega el nickname a la lista
                print(f"\033[92m[SERVIDOR]: {nickname} está conectado con {str(address)}.\033[0m") # Mensaje sobre la dirección en la que se conecta el cliente

                mensaje = f"\033[92m[SERVIDOR]: {nickname} se unió a ChatApp.\033[0m".encode("utf-8")
                self.transmitirMensaje(mensaje, cliente) # Informa a otros usuarios sobre la nueva conexión
                cliente.send("Conectado al servidor.".encode("utf-8")) # Confirma la conexión al cliente

                # Inicia un hilo para manejar los mensajes del cliente
                thread = threading.Thread(target=self.manejarMensaje, args=(cliente,))
                thread.start()

    # Método para verificar el estado de un usuario en la base de datos
    def verificarUsuario(self, nickname):
        self.cursor.execute("SELECT * FROM usuarios WHERE nickname = %s", (nickname,))
        usuario = self.cursor.fetchone() # Obtiene el resultado de la búsqueda

        # Si el usuario ya existe en la base de datos
        if usuario:
            if nickname in self.nicknames: # Verifica si ya está conectado
                return "Conectado"
            else:
                # Actualiza la fecha y hora de la última conexión
                self.cursor.execute("UPDATE usuarios SET connected_at = %s WHERE nickname = %s", (datetime.now(), nickname))
                self.db.commit() # Confirma los cambios en la base de datos
                return "Existe" # Usuario existe pero no está conectado
        else:
            # Si el usuario no existe, lo inserta en la base de datos
            self.cursor.execute("INSERT INTO usuarios (nickname, connected_at) VALUES (%s, %s)", (nickname, datetime.now()))
            self.db.commit() # Confirma los cambios en la base de datos
            return "Nuevo" # Usuario nuevo

    # Método para iniciar el servidor y aceptar las conexiones
    def iniciar(self):
        self.recibirConexion() # LLama al método para recibir conexiones

# Código para ejecutar al servidor
if __name__ == "__main__":
    servidor = Servidor() # Crea una instancia del servidor
    servidor.iniciar() # Inicia el servidor
