import tkinter as tk
from tkinter import messagebox
import socket
import multiprocessing
import numpy as np

#soma todos os numeros pares em um intervalo
def pair_adder(start, end):
    if start % 2 != 0:
        min = start + 1
    else:
        min = start

    if end % 2 != 0:
        max = end - 1
    else:
        max = end

    quantity_even_numbers = (max - min) // 2 + 1
    sum_even = (quantity_even_numbers * (min + max)) // 2
    return sum_even

#soma todos os numeros impares em um intervalo
def odd_adder(start, end):
    if start % 2 == 0:
        min = start + 1
    else:
        min = start

    if end % 2 == 0:
        max = end - 1
    else:
        max = end

    quantity_odd_numbers = (max - min) // 2 + 1
    sum_odd = (quantity_odd_numbers * (min + max)) // 2
    return sum_odd

#calcula leibniz em um intervalo
def pi(start, end):
    denominator = np.arange(start, end) * 2 + 1
    terms = (-1) ** np.arange(start, end) / denominator
    sum_pi = np.sum(terms)
    result = 4 * sum_pi
    return result

#cria e executa um cliente
def client_task(client_id, host, port):
    # Conectar ao servidor
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Receber o intervalo numérico do servidor
    interval = client.recv(1024).decode()

    numeros = interval.split()
    numeros = [int(num) for num in numeros]
    start = numeros[0]
    end = numeros[1]

    print(f"Cliente {client_id}: Intervalo numérico recebido do servidor: {start} a {end}")

    # Realizar um cálculo com o intervalo numérico (por exemplo, calcular a soma dos números no intervalo)
    pair_adder_result = pair_adder(start, end)
    odd_adder_result_result = odd_adder(start, end)
    pi_result = pi(start, end)

    result = f"{pair_adder_result} {odd_adder_result_result} {pi_result}"

    # Enviar o resultado para o servidor
    client.send(str(result).encode())
    print(f"Cliente {client_id}: Resultado enviado para o servidor: {result}")

    # Fechar a conexão com o servidor
    client.close()

def generate_clients(num_clients_entry, host, port):
    try:
        num_clients = int(num_clients_entry.get())
    except ValueError:
        messagebox.showerror("Erro", "Digite um número válido de clientes.")
        return

    # Criar processos para cada cliente
    processes = []
    for i in range(num_clients):
        process = multiprocessing.Process(target=client_task, args=(i, host, port))
        processes.append(process)
        process.start()

    # Aguardar todos os processos terminarem
    for process in processes:
        process.join()

def main():
    # Configuração do cliente
    host = '127.0.0.1'
    port = 5555

    # Interface Gráfica
    root = tk.Tk()
    root.title("Gerador de Clientes")
    root.minsize(250, 100)

    num_clients_label = tk.Label(root, text="Número de Clientes:")
    num_clients_label.pack()
    num_clients_entry = tk.Entry(root)
    num_clients_entry.pack()

    generate_button = tk.Button(root, text="Gerar Clientes",
                                command=lambda: generate_clients(num_clients_entry, host, port))
    generate_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()