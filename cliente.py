import socket
import threading

class Cliente:

    def __init__(self, host = "127.0.0.1", port = 5000):
        self.host = host
        self.port = port
        self.BUFFER_SIZE = 1024
        self.nickname = input("Ingresa tu 'Nickname': ")
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectarConServidor()

    def conectarConServidor(self):
        try:
            self.cliente.connect((self.host, self.port))
            print("\033[92m[CLIENTE]: Conectado al servidor.\033[0m")
            self.iniciar_hilos()
        except:
            print("\033[91m[CLIENTE]: Error al conectar al servidor.\033[0m")

    def iniciarHilos(self):
        recibirThread = threading.Thread(target=self.recibirMensaje)
        recibirThread.start()

        escribirThread = threading.Thread(target=self.escribirMensaje)
        escribirThread.start()

    def recibirMensaje(self):
        while True:
            try:
                mensaje = self.cliente.recv(self.BUFFER_SIZE)
                if mensaje == b"@nickname":
                    self.cliente.send(self.nickname.encode("utf-8"))
                else:
                    print(f"\n\033[94m{mensaje.decode('utf-8')}\033[0m")
            except:
                print("\033[91m[CLIENTE]: Ocurrió un error en la conexión.\033[0m")
                self.cliente.close()
                break

    def escribirMensaje(self):
        while True:
            mensaje = f"{self.nickname}: {input('')}"
            try:
                self.cliente.send(mensaje.encode("utf-8"))
            except:
                print("\033[91m[CLIENTE]: Error al enviar el mensaje.\033[0m")
                break

if __name__ == "__main__":
    cliente = Cliente()
