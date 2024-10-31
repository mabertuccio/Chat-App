import socket
import threading

class Servidor:

    def __init__(self, host = "127.0.0.1", port = 5000):
        self.host = host
        self.port = port
        self.BUFFER_SIZE = 1024
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((self.host, self.port))
        self.servidor.listen()
        print(f"\033[94m[SERVIDOR]: Corriendo en {self.host}:{self.port}.\033[0m")

        self.clientes = []
        self.nicknames = []

    def transmitirMensaje(self, mensaje, _cliente):
        mensaje_decodificado = mensaje.decode("utf-8")
        
        if "@" in mensaje_decodificado:
            partes = mensaje_decodificado.split()
            nombreDestino = partes[1][1:]

            if nombreDestino in self.nicknames:
                indiceDestino = self.nicknames.index(nombreDestino)
                clienteDestino = self.clientes[indiceDestino]
                
                indiceRemitente = self.clientes.index(_cliente)
                nombreRemitente = self.nicknames[indiceRemitente]
                
                mensajePrivado = f"{nombreRemitente} (Privado): {' '.join(partes[2:])}"
                clienteDestino.send(mensajePrivado.encode("utf-8"))
            else:
                _cliente.send(f"\033[91m[SERVIDOR]: El usuario '{nombreDestino}' no existe.\033[0m".encode("utf-8"))
        else:
            for cliente in self.clientes:
                if cliente != _cliente:
                    cliente.send(mensaje)

    def manejarMensaje(self, cliente):
        while True:
            try:
                mensaje = cliente.recv(self.BUFFER_SIZE)
                
                if mensaje.decode("utf-8") == "/listar":
                    self.listarUsuariosConectados(cliente)
                elif mensaje.decode("utf-8") == "/desconectar":
                    self.desconectarClientes()
                    break
                elif mensaje.decode("utf-8") == "/salir":
                    self.desconectarCliente(cliente)
                else:
                    self.transmitirMensaje(mensaje, cliente)
            except:
                self.desconectarCliente(cliente)
                break

    def listarUsuariosConectados(self, cliente):
        listaUsuariosConectados = f"\033[94m[SERVIDOR] - Usuarios Conectados:\n" + "\n".join(self.nicknames) + "\033[0m"
        cliente.send(listaUsuariosConectados.encode("utf-8"))

    def desconectarClientes(self):
        clientesConectados = self.clientes[:]

        for cliente in clientesConectados:
            cliente.send("Desconectando a todos los usuarios...".encode("utf-8"))
            self.desconectarCliente(cliente)
        self.clientes = []
        self.nicknames = []

    def desconectarCliente(self, cliente):
        if cliente in self.clientes:
            index = self.clientes.index(cliente)
            username = self.nicknames[index]
            self.transmitirMensaje(f"\033[91m[SERVIDOR]: {username} se desconectó.\033[0m".encode('utf-8'), cliente)
            self.clientes.remove(cliente)
            self.nicknames.remove(username)
            cliente.close()
            print(f"\033[91m[SERVIDOR]: {username} se desconectó.\033[0m")

    def recibirConexion(self):
        while True:
            cliente, address = self.servidor.accept()
            cliente.send("@nickname".encode('utf-8'))
            username = cliente.recv(self.BUFFER_SIZE).decode('utf-8')

            self.clientes.append(cliente)
            self.nicknames.append(username)

            print(f"\033[92m[SERVIDOR]: {username} está conectado con {str(address)}.\033[0m")

            message = f"\033[92m[SERVIDOR]: {username} se unió a ChatApp.\033[0m".encode('utf-8')
            self.transmitirMensaje(message, cliente)
            cliente.send("Conectado al servidor.".encode('utf-8'))

            thread = threading.Thread(target=self.manejarMensaje, args=(cliente,))
            thread.start()

    def iniciar(self):
        self.recibirConexion()

if __name__ == "__main__":
    servidor = Servidor()
    servidor.iniciar()
