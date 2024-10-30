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
        for cliente in self.clientes:
            if cliente != _cliente:
                cliente.send(mensaje)

    def manejarMensaje(self, cliente):
        while True:
            try:
                message = cliente.recv(self.BUFFER_SIZE)
                self.transmitirMensaje(message, cliente)
            except:
                self.desconectarCliente(cliente)
                break

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
