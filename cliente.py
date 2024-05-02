import tkinter as tk
from tkinter import ttk
from multiprocessing import Process, Queue
import socket
import numpy as np

#soma todos os numeros pares em um intervalo
def pair_adder(start, end, result_queue):
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
    result_queue.put(('pair', sum_even))

#soma todos os numeros impares em um intervalo
def odd_adder(start, end, result_queue):
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
    result_queue.put(('odd', sum_odd))

#calcula leibniz em um intervalo
def pi(start, end, result_queue):
    denominator = np.arange(start, end) * 2 + 1
    terms = (-1) ** np.arange(start, end) / denominator
    sum_pi = np.sum(terms)
    result = 4 * sum_pi
    result_queue.put(('pi', result))

def connect_to_server(host, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        result_queue = Queue()

        interval = client.recv(1024).decode()

        numeros = interval.split()
        numeros = [int(num) for num in numeros]
        start = numeros[0]
        end = numeros[1]

        # Executar as funções em threads separadas
        sum_pair_process = Process(target=pair_adder, args=(start, end, result_queue))
        sum_odd_process = Process(target=odd_adder, args=(start, end, result_queue))
        pi_process = Process(target=pi, args=(start, end, result_queue))

        sum_pair_process.start()
        sum_odd_process.start()
        pi_process.start()

        # Obter os resultados das funções
        pair_adder_result = None
        odd_adder_result = None
        pi_result = None

        while True:
            result_type, result = result_queue.get()
            if result_type == 'pair':
                pair_adder_result = result
            elif result_type == 'odd':
                odd_adder_result = result
            elif result_type == 'pi':
                pi_result = result
            if pair_adder_result is not None and odd_adder_result is not None and pi_result is not None:
                break

        result = f"{pair_adder_result} {odd_adder_result} {pi_result}"
        client.send(str(result).encode())

        # Enviar resultados para a interface gráfica
        update_results(pair_adder_result, odd_adder_result, pi_result)

        client.close()
    except Exception as e:
        print("Erro ao conectar ao servidor:", e)

#Atualiza interface gráfica
def update_results(pair_adder_result, odd_adder_result_result, pi_result):
    even_result_label.config(text="Soma dos pares: " + str(pair_adder_result))
    odd_result_label.config(text="Soma dos impares: " + str(odd_adder_result_result))
    pi_result_label.config(text="Pi: " + str(pi_result))

#Conecta ao servidor
def on_submit():
    host = '127.0.0.1'
    port = 5555

    connect_to_server(host, port)

# Interface Gráfica
root = tk.Tk()
root.title("Conectar ao Servidor")

root.minsize(200, 100)

frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

submit_button = ttk.Button(frame, text="Conectar", command=on_submit)
submit_button.grid(row=4, column=0, columnspan=2, pady=10)

even_result_label = ttk.Label(frame, text="Soma dos pares: ")
even_result_label.grid(row=6, column=0, columnspan=2)

odd_result_label = ttk.Label(frame, text="Soma dos impares: ")
odd_result_label.grid(row=7, column=0, columnspan=2)

pi_result_label = ttk.Label(frame, text="pi: ")
pi_result_label.grid(row=8, column=0, columnspan=2)

if __name__ == '__main__':
    root.mainloop()