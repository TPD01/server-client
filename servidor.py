import tkinter as tk
import socket
import multiprocessing

# Função para lidar com a conexão de um cliente
def handle_client(client_socket, client_counter, lock, shared_float_array):
    # Gera um intervalo numérico unico para cada cliente
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
        print(f"----------------------------------------------------------------------------")
        print(f"cliente: {client_counter} \nintervalo: {start} a {end},  \nsoma dos pares: {pairs_sum},  \nsoma dos impares: {odd_sum}, \nleibnz: {pi}")
        print(f"****************************************************************************")
        print(f"Somatorio total dos pares: {int(shared_float_array[0])}")
        print(f"Somatorio total dos impares: {int(shared_float_array[1])}")
        print(f"Pi: {shared_float_array[2]}")
        print(f"----------------------------------------------------------------------------\n\n")

    # Fechar a conexão com o cliente
    client_socket.close()

# Função principal do servidor
def main():
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
    shared_float_array = multiprocessing.Array('f', [0.0, 0.0, 0.0])
    lock = multiprocessing.Lock()

    while True:
        # Aceitar a conexão de um cliente
        client_socket, _ = server_socket.accept()

        client_counter += 1

        # Criar um novo processo para lidar com o cliente
        client_process = multiprocessing.Process(target=handle_client, args=(client_socket, client_counter, lock, shared_float_array))
        client_process.start()

if __name__ == "__main__":
    main()