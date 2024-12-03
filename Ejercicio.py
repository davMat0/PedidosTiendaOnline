import queue
import threading
import time
from random import randint

# Cola de pedidos con capacidad de 5
colaPedidos = queue.Queue(maxsize=5)
# Condicion para sincronizar los hilos
cond = threading.Condition()

# variables para contar el numero de pedidos generados y procesados
numPedidosTotales = 0
numPedidosProcesados = 0

# Limite de pedidos
maxPedidos = 15

class Cliente(threading.Thread):
    def __init__(self, idCLiente, colaPedidos, maxPedidos, cond):
        super().__init__()
        self.idCliente = idCLiente
        self.colaPedidos = colaPedidos
        self.maxPedidos = maxPedidos
        self.cond = cond

    # Se generan los pedidos y se agregan a la cola
    def run(self):
        global numPedidosTotales
        while True:
            with self.cond:  # Bloqueo de la condition
                # Se verifica si se han alcanzado los el máximo de pedidos
                if numPedidosTotales >= self.maxPedidos:
                    return  # sale si se alcanzo el limite de pedidos

                # Espera hasta que la cola tenga espacio
                cond.wait_for(lambda: not self.colaPedidos.full())

                # Genera un nuevo pedido si no se alcanzo el limite
                if numPedidosTotales < self.maxPedidos:
                    numPedidosTotales += 1
                    pedido = f"Pedido - {numPedidosTotales}"
                    self.colaPedidos.put(pedido)
                    print(f"Cliente {self.idCliente}: Generó {pedido}")
                    self.cond.notify_all()

            time.sleep(randint(1, 2))


class Empleado(threading.Thread):
    def __init__(self, idEmpleado, colaPedidos, maxPedidos, cond):
        super().__init__()
        self.idEmpleado = idEmpleado
        self.colaPedidos = colaPedidos
        self.maxPedidos = maxPedidos
        self.cond = cond

    def run(self):
        global numPedidosProcesados
        while True:
            with self.cond:  # Bloqueo de la condition
                # Se comprueba si se procesaron todos los pedidos
                if numPedidosProcesados >= self.maxPedidos:
                    return # sale si se procesaron todos los pedidos

                # Espera hasta que la cola tenga pedidos
                self.cond.wait_for(lambda: not self.colaPedidos.empty())

                # Procesa un pedido de la cola
                pedido = self.colaPedidos.get()
                numPedidosProcesados += 1
                print(f"Empleado {self.idEmpleado}: Procesó {pedido}")
                self.cond.notify_all()
            time.sleep(randint(2, 3))

# Listas para almacenar los hilos clientes y empleados
clientes = []
empleados = []

# Se crean e inician los hilos de clientes
for i in range(1, 4):
    c = Cliente(i, colaPedidos, maxPedidos, cond)
    c.start()
    clientes.append(c)

# Se crean e inician los hilos de empleados
for i in range(1, 3):
    e = Empleado(i, colaPedidos, maxPedidos, cond)
    e.start()
    empleados.append(e)

# Espera que todos los hilos clientes terminen
for cliente in clientes:
    cliente.join()

# Espera que todos los hilos empleados terminen
for empleado in empleados:
    empleado.join()

print("Todos los pedidos han sido procesados.")