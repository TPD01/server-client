import tkinter as tk
import socket
import threading

# Classe para a GUI
class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server GUI")

        self.results_label = tk.Label(root, text="Resultados:")
        self.results_label.pack()

        self.results_text = tk.Text(root, height=10, width=50)
        self.results_text.pack()

        self.clients_label = tk.Label(root, text="Clientes conectados: 0")
        self.clients_label.pack()

    def update_results(self, shared_float_array):
        self.results_text.delete("1.0", tk.END)
        self.results_text.insert(tk.END, f"Somatório total dos pares: {int(shared_float_array[0])}\n")
        self.results_text.insert(tk.END, f"Somatório total dos ímpares: {int(shared_float_array[1])}\n")
        self.results_text.insert(tk.END, f"Pi: {shared_float_array[2]}\n\n")

    def update_clients_count(self, count):
        self.clients_label.config(text=f"Clientes conectados: {count}")

# Função para lidar com a conexão de um cliente
def handle_client(client_socket, client_counter, lock, shared_float_array, gui):
    try:
        # Gera um intervalo numérico único para cada cliente
        start = (client_counter * 1000)
        end = (client_counter * 1000) + 999
        interval = f"{start} {end}"

        # Enviar o intervalo para o cliente
        client_socket.sendall(interval.encode())

        client_response = client_socket.recv(1024).decode()

        values = client_response.split()
        values = [float(val) for val in values]
        pairs_sum = int(values[0])
        odd_sum = int(values[1])
        pi = values[2]

        # Atualizar os resultados no vetor compartilhado
        with lock:
            shared_float_array[0] += pairs_sum
            shared_float_array[1] += odd_sum
            if client_counter % 2 == 0:
                shared_float_array[2] += pi
            else:
                shared_float_array[2] -= pi

            # Atualizar a GUI
            gui.update_results(shared_float_array)

        # Fechar a conexão com o cliente
        client_socket.close()
    except Exception as e:
        print(f"Erro ao lidar com a conexão do cliente {client_counter}: {e}")
    finally:
        gui.update_clients_count(threading.active_count() - 2)  # Atualizar a contagem de clientes conectados

# Função principal do servidor
def server_thread(gui):
    # Configurações do servidor
    host = '127.0.0.1'
    port = 5555
    max_connections = 100

    # Inicializar o socket do servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(max_connections)

    print(f"Servidor escutando em {host}:{port}...")

    client_counter = -1
    shared_float_array = [0.0, 0.0, 0.0]
    lock = threading.Lock()

    while True:
        try:
            # Aceitar a conexão de um cliente
            client_socket, _ = server_socket.accept()

            client_counter += 1

            # Criar uma nova thread para lidar com o cliente
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_counter, lock, shared_float_array, gui))
            client_thread.start()
        except Exception as e:
            print(f"Erro ao aceitar conexão de cliente: {e}")

# Função principal
def main():
    # Iniciar a thread do servidor antes de iniciar a GUI
    root = tk.Tk()
    gui = GUI(root)
    threading.Thread(target=server_thread, args=(gui,)).start()
    root.mainloop()

if __name__ == "__main__":
    main()
