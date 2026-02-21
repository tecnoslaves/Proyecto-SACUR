import sqlite3
from datetime import datetime
import sys
import os
from colorama import Fore, Back, Style, init

class SistemaVentas:
    def __init__(self):
        self.logo = fr"""
{Fore.YELLOW}╔═══════════════════════════════════════════════════════╗
{Fore.YELLOW}║{Fore.RED}    _____      __       ______   __     __   ______    {Fore.YELLOW}║
{Fore.YELLOW}║{Fore.RED}   / ____|    /  \     /  ____| |  |   |  | |      |   {Fore.YELLOW}║
{Fore.YELLOW}║{Fore.RED}  | (___     / /\ \   |  |      |  |   |  | |   #  |   {Fore.YELLOW}║
{Fore.YELLOW}║{Fore.RED}   \___ \   / /__\ \  |  |      |  |   |  | |  __ <    {Fore.YELLOW}║
{Fore.YELLOW}║{Fore.RED}   ____) | /  ____  \ |  |____  |  |___|  | | |  \ \   {Fore.YELLOW}║
{Fore.YELLOW}║{Fore.RED}  |_____/ /__/    \__\ \______|  \_______/  |_|   \_\  {Fore.YELLOW}║
{Fore.YELLOW}║                                                       {Fore.YELLOW}║
{Fore.YELLOW}║{Fore.BLUE}                     RESTO BAR                         {Fore.YELLOW}║
{Fore.YELLOW}╚═══════════════════════════════════════════════════════╝
{Style.RESET_ALL}"""
        self.periodo_activo = None
        self.venta_actual = []
        self.total_venta = 0.0
        self.delivery_cost = 0.0
        self.tipo_servicio = ""

        # Configuración de la base de datos SQLite
        self.db_path = "sistema_ventas.db"

        self.menu = {
            "pizzas": {
                1: {"nombre": "Pizza Común", "precio": 55},
                2: {"nombre": "Pizza Salchicha", "precio": 65},
                3: {"nombre": "Pizza Pollo", "precio": 70},
                4: {"nombre": "Pizza Choclo", "precio": 70},
                5: {"nombre": "Pizza Champiñones", "precio": 70},
                6: {"nombre": "Pizza Hawaiana", "precio": 70},
                7: {"nombre": "Pizza Pollo y Choclo", "precio": 75},
                8: {"nombre": "Pizza Papa y Huevo", "precio": 70},
                9: {"nombre": "Pizza Huevo", "precio": 60},
                10: {"nombre": "Pizza Muzarella", "precio": 75},
                11: {"nombre": "Pizza Napolitana", "precio": 70},
                12: {"nombre": "Pizza Calabresa", "precio": 75},
                13: {"nombre": "Pizza Especial", "precio": 80},
                14: {"nombre": "Pizza 3 Quesos", "precio": 75},
                15: {"nombre": "Pizza 4 Quesos", "precio": 80},
                16: {"nombre": "Pizza Fugazzeta", "precio": 60},
                17: {"nombre": "Pizza Carne", "precio": 80}
            },
            "sandwiches": {
                1: {"nombre": "Milanesa de Carne", "precio": 28},
                2: {"nombre": "Milanesa de Pollo", "precio": 28},
                3: {"nombre": "Napolitano", "precio": 35},
                4: {"nombre": "Lomito", "precio": 28},
                5: {"nombre": "Lomito Montado", "precio": 30},
                6: {"nombre": "Chacarero Personal", "precio": 35},
                7: {"nombre": "Chacarero Familiar", "precio": 60}
            },
            "hamburguesas": {
                1: {"nombre": "Hamburguesa Simple", "precio": 18},
                2: {"nombre": "Hamburguesa Especial", "precio": 22},
                3: {"nombre": "Hamburguesa Hawaiana", "precio": 25},
                4: {"nombre": "Cheddar Burger", "precio": 35},
                5: {"nombre": "Tocino Burger", "precio": 30},
                6: {"nombre": "Hamburguesa Doble", "precio": 35}
            },
            "platos": {
                1: {"nombre": "Milanesa al plato", "precio": 40},
                2: {"nombre": "Lomito al plato", "precio": 40},
                3: {"nombre": "Milanesa Napolitana", "precio": 50},
                4: {"nombre": "Milanesa Americana", "precio": 60},
                5: {"nombre": "Milanesa a Caballo", "precio": 50},
                6: {"nombre": "Costeleta", "precio": 40}
            },
            "bebidas": {
                1: {"nombre": "Coca Cola MINI", "precio": 2.5},
                2: {"nombre": "Fanta MINI", "precio": 2.5},
                3: {"nombre": "Sprite MINI", "precio": 2.5},
                4: {"nombre": "Coca Cola 750ml POPULAR", "precio": 10},
                5: {"nombre": "Fanta 750ml POPULAR", "precio": 10},
                6: {"nombre": "Sprite 750ml POPULAR", "precio": 10},
                7: {"nombre": "Coca Cola 1L", "precio": 12},
                8: {"nombre": "Fanta 1L", "precio": 12},
                9: {"nombre": "Sprite 1L", "precio": 12},
                10: {"nombre": "Coca Cola 1.5L", "precio": 15},
                11: {"nombre": "Fanta 1.5L", "precio": 15},
                12: {"nombre": "Sprite 1.5L", "precio": 15},
                13: {"nombre": "Coca Cola 2L", "precio": 20},
                14: {"nombre": "Fanta 2L", "precio": 20},
                15: {"nombre": "Sprite 2L", "precio": 20},
                16: {"nombre": "Aquarius 2L POMELO ROSADO", "precio": 20},
                17: {"nombre": "Aquarius 2L PERA", "precio": 20},
                18: {"nombre": "Simba 2L DURAZNO", "precio": 20},
                19: {"nombre": "Simba 2L MANZANA", "precio": 20},
                20: {"nombre": "Jugo PELÓN", "precio": 18},
                21: {"nombre": "Jugo LINAZA", "precio": 18},
                22: {"nombre": "Jugo NÉCTAR", "precio": 18},
                23: {"nombre": "Jugo ADES MANZANA", "precio": 18},
                24: {"nombre": "Jugo ADES DURAZNO", "precio": 18},
                25: {"nombre": "Jugo VALLE MANZANA", "precio": 18},
                26: {"nombre": "Jugo VALLE DURAZNO", "precio": 18},
                27: {"nombre": "Cerveza PACEÑA", "precio": 30}
            }
        }

        self.inicializar_base_datos()
        self.verificar_periodo_activo()

    def inicializar_base_datos(self):
        """Crear la base de datos SQLite y las tablas necesarias"""
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Crear tabla de periodos de venta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS periodos_venta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_inicio DATETIME NOT NULL,
                    fecha_fin DATETIME,
                    activo BOOLEAN DEFAULT 1,
                    total_ventas REAL DEFAULT 0.00
                )
            """)

            # Crear tabla de ventas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    periodo_id INTEGER,
                    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo_servicio TEXT,
                    subtotal REAL,
                    delivery REAL DEFAULT 0.00,
                    total REAL,
                    FOREIGN KEY (periodo_id) REFERENCES periodos_venta(id)
                )
            """)

            # Crear tabla de detalles de venta
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER,
                    categoria TEXT,
                    producto TEXT,
                    cantidad INTEGER,
                    precio_unitario REAL,
                    subtotal REAL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id)
                )
            """)

            connection.commit()
            cursor.close()
            connection.close()
            print("Base de datos SQLite inicializada correctamente.")
            print(f"Archivo de base de datos: {os.path.abspath(self.db_path)}")

        except sqlite3.Error as err:
            print(f"Error al inicializar base de datos: {err}")

    def verificar_periodo_activo(self):
        """Verificar si hay un período activo al iniciar el sistema"""
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            cursor.execute("SELECT id FROM periodos_venta WHERE activo = 1")
            resultado = cursor.fetchone()

            if resultado:
                self.periodo_activo = resultado[0]
                print(f"Se encontró un período activo (ID: {self.periodo_activo})")

            cursor.close()
            connection.close()

        except sqlite3.Error as err:
            print(f"Error al verificar período activo: {err}")

    def menu_principal(self):
        """Mostrar el menú principal del sistema"""
        while True:
            print(self.logo)
            print("\n" + "="*50)
            print("        SISTEMA DE REGISTRO DE VENTAS")
            print("="*50)
            print("1. Realizar una venta")
            print("2. Crear un nuevo periodo de ventas")
            print("3. Finalizar el periodo de venta actual")
            print("4. Realizar cierre de caja")
            print("5. Cerrar el programa")
            print("-"*50)

            try:
                opcion = int(input("Seleccione una opción: "))

                if opcion == 1:
                    if self.periodo_activo is None:
                        print("\n¡ERROR! No hay un periodo de venta activo.")
                        print("Debe crear un periodo de venta primero (opción 2).")
                    else:
                        self.realizar_venta()

                elif opcion == 2:
                    self.crear_periodo_venta()

                elif opcion == 3:
                    self.finalizar_periodo_venta()

                elif opcion == 4:
                    self.cierre_caja()

                elif opcion == 5:
                    print("\n¡Gracias por usar el sistema!")
                    sys.exit()

                else:
                    print("\nOpción no válida. Intente nuevamente.")

            except ValueError:
                print("\nPor favor, ingrese un número válido.")

    def crear_periodo_venta(self):
        """Crear un nuevo periodo de ventas"""
        if self.periodo_activo is not None:
            print("\n¡ADVERTENCIA! Ya existe un periodo de venta activo.")
            print("Debe finalizar el periodo actual antes de crear uno nuevo.")
            return

        print("\n--- CREAR NUEVO PERIODO DE VENTAS ---")
        fecha_str = input("Ingrese la fecha del periodo (DD/MM/YYYY) o presione Enter para usar la fecha actual: ")

        if fecha_str.strip() == "":
            fecha_inicio = datetime.now()
        else:
            try:
                fecha_inicio = datetime.strptime(fecha_str, "%d/%m/%Y")
            except ValueError:
                print("Formato de fecha inválido. Usando fecha actual.")
                fecha_inicio = datetime.now()

        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO periodos_venta (fecha_inicio, activo)
                VALUES (?, 1)
            """, (fecha_inicio,))

            self.periodo_activo = cursor.lastrowid
            connection.commit()
            cursor.close()
            connection.close()

            print(f"\n✓ Periodo de venta creado exitosamente!")
            print(f"Fecha de inicio: {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
            print(f"ID del periodo: {self.periodo_activo}")
            print("\n*** Ahora puede realizar ventas en este período ***")

        except sqlite3.Error as err:
            print(f"Error al crear periodo: {err}")

    def finalizar_periodo_venta(self):
        """Finalizar el periodo de venta actual"""
        if self.periodo_activo is None:
            print("\nNo hay un periodo de venta activo para finalizar.")
            return

        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Calcular total de ventas del periodo
            cursor.execute("""
                SELECT COALESCE(SUM(total), 0) FROM ventas WHERE periodo_id = ?
            """, (self.periodo_activo,))

            total_ventas = cursor.fetchone()[0]

            # Actualizar periodo
            cursor.execute("""
                UPDATE periodos_venta
                SET fecha_fin = ?, activo = 0, total_ventas = ?
                WHERE id = ?
            """, (datetime.now(), total_ventas, self.periodo_activo))

            connection.commit()
            cursor.close()
            connection.close()

            print(f"\n✓ Periodo de venta finalizado exitosamente!")
            print(f"Total de ventas del periodo: ${total_ventas:.2f}")

            self.periodo_activo = None

        except sqlite3.Error as err:
            print(f"Error al finalizar periodo: {err}")

    def cierre_caja(self):
        """Realizar cierre de caja con información detallada"""
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Verificar si hay periodos
            cursor.execute("SELECT COUNT(*) FROM periodos_venta")
            if cursor.fetchone()[0] == 0:
                print("\nNo hay periodos de venta registrados.")
                return

            print("\n¿Qué cierre de caja desea realizar?")
            print("1. Cierre del último período creado")
            print("2. Cierre de período específico por fecha")

            opcion = input("Seleccione una opción (1 o 2): ")

            if opcion == "1":
                # Buscar período activo
                cursor.execute("""
                    SELECT id, fecha_inicio, fecha_fin, total_ventas, activo
                    FROM periodos_venta
                    WHERE activo = 1
                """)
                periodo = cursor.fetchone()

                if not periodo:
                    print("\nNo hay período activo. Mostrando último período finalizado.")
                    cursor.execute("""
                        SELECT id, fecha_inicio, fecha_fin, total_ventas, activo
                        FROM periodos_venta
                        ORDER BY fecha_inicio DESC
                        LIMIT 1
                    """)
                    periodo = cursor.fetchone()

            elif opcion == "2":
                # Mostrar periodos disponibles
                cursor.execute("""
                    SELECT id, fecha_inicio, fecha_fin, total_ventas, activo
                    FROM periodos_venta
                    ORDER BY fecha_inicio DESC
                """)
                periodos = cursor.fetchall()

                print("\nPERIODOS DISPONIBLES:")
                print("-" * 70)
                print(f"{'ID':<5} {'Fecha':<12} {'Estado':<12} {'Total':<10} {'Ventas':<8}")
                print("-" * 70)

                for p in periodos:
                    fecha_inicio = datetime.fromisoformat(p[1])
                    estado = "Activo" if p[4] else "Finalizado"

                    # Contar ventas de este periodo
                    cursor.execute("SELECT COUNT(*) FROM ventas WHERE periodo_id = ?", (p[0],))
                    cant_ventas = cursor.fetchone()[0]

                    print(f"{p[0]:<5} {fecha_inicio.strftime('%d/%m/%Y'):<12} {estado:<12} ${p[3]:<9.2f} {cant_ventas:<8}")

                periodo_id = input("\nIngrese el ID del período: ")
                cursor.execute("""
                    SELECT id, fecha_inicio, fecha_fin, total_ventas, activo
                    FROM periodos_venta
                    WHERE id = ?
                """, (periodo_id,))
                periodo = cursor.fetchone()

            else:
                print("Opción no válida.")
                return

            if not periodo:
                print("\nPeriodo no encontrado.")
                return

            # Procesar información del período
            periodo_id, fecha_inicio, fecha_fin, total_ventas, activo = periodo
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            if fecha_fin:
                fecha_fin = datetime.fromisoformat(fecha_fin)

            print("\n" + "="*80)
            print("                           CIERRE DE CAJA")
            print("="*80)
            print(f"Período: {periodo_id} | {fecha_inicio.strftime('%d/%m/%Y %H:%M')}", end="")
            if fecha_fin:
                print(f" - {fecha_fin.strftime('%d/%m/%Y %H:%M')}")
            else:
                print(" (ACTIVO)")

            print("="*80)

            # 1. RESUMEN GENERAL
            cursor.execute("SELECT COUNT(*) FROM ventas WHERE periodo_id = ?", (periodo_id,))
            total_ventas_count = cursor.fetchone()[0]

            cursor.execute("SELECT AVG(total) FROM ventas WHERE periodo_id = ?", (periodo_id,))
            ticket_promedio = cursor.fetchone()[0] or 0

            print(f"TOTAL DE VENTAS: {total_ventas_count:>8}")
            print(f"TICKET PROMEDIO: ${ticket_promedio:>7.2f}")
            print(f"TOTAL EN EFECTIVO: ${total_ventas:>6.2f}")
            print("-"*80)

            # 2. VENTAS POR TIPO DE SERVICIO
            cursor.execute("""
                SELECT tipo_servicio, COUNT(*), SUM(total), SUM(delivery)
                FROM ventas
                WHERE periodo_id = ?
                GROUP BY tipo_servicio
            """, (periodo_id,))

            servicios = cursor.fetchall()
            print("DESGLOSE POR SERVICIO:")
            for servicio, cantidad, total, delivery in servicios:
                print(f"{servicio:<15} {cantidad:>3} ventas  ${total:>8.2f}  (Delivery: ${delivery:>6.2f})")
            print("-"*80)

            # 3. VENTAS POR CATEGORÍA
            cursor.execute("""
                SELECT dv.categoria, COUNT(*) as cantidad, SUM(dv.subtotal) as total
                FROM detalle_ventas dv
                JOIN ventas v ON dv.venta_id = v.id
                WHERE v.periodo_id = ?
                GROUP BY dv.categoria
                ORDER BY total DESC
            """, (periodo_id,))

            categorias = cursor.fetchall()
            print("VENTAS POR CATEGORÍA:")
            for categoria, cantidad, total in categorias:
                porcentaje = (total / total_ventas * 100) if total_ventas > 0 else 0
                print(f"{categoria.capitalize():<18} {cantidad:>4} items  ${total:>8.2f}  ({porcentaje:>5.1f}%)")
            print("-"*80)

            # 4. TOP 10 PRODUCTOS MÁS VENDIDOS
            cursor.execute("""
                SELECT dv.producto, SUM(dv.cantidad) as total_cantidad, SUM(dv.subtotal) as total_dinero
                FROM detalle_ventas dv
                JOIN ventas v ON dv.venta_id = v.id
                WHERE v.periodo_id = ?
                GROUP BY dv.producto
                ORDER BY total_cantidad DESC
                LIMIT 10
            """, (periodo_id,))

            productos = cursor.fetchall()
            print("TOP 10 PRODUCTOS MÁS VENDIDOS:")
            for i, (producto, cantidad, dinero) in enumerate(productos, 1):
                print(f"{i:>2}. {producto:<35} {cantidad:>3} unid.  ${dinero:>7.2f}")
            print("-"*80)

            # 5. VENTAS POR HORA (si hay ventas del día)
            if activo or (fecha_fin and fecha_fin.date() == datetime.now().date()):
                cursor.execute("""
                    SELECT strftime('%H', fecha_venta) as hora, COUNT(*), SUM(total)
                    FROM ventas
                    WHERE periodo_id = ?
                    AND date(fecha_venta) = date('now')
                    GROUP BY hora
                    ORDER BY hora
                """, (periodo_id,))

                ventas_hora = cursor.fetchall()
                if ventas_hora:
                    print("VENTAS POR HORA (HOY):")
                    for hora, cantidad, total in ventas_hora:
                        print(f"{hora}:00 - {hora}:59    {cantidad:>2} ventas    ${total:>7.2f}")
                    print("-"*80)

            # 6. INFORMACIÓN ADICIONAL
            cursor.execute("""
                SELECT SUM(delivery) FROM ventas WHERE periodo_id = ?
            """, (periodo_id,))
            total_delivery = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT MAX(total), MIN(total) FROM ventas WHERE periodo_id = ?
            """, (periodo_id,))
            max_venta, min_venta = cursor.fetchone()

            print("INFORMACIÓN ADICIONAL:")
            print(f"Total en delivery: ${total_delivery:.2f}")
            if max_venta:
                print(f"Venta más alta: ${max_venta:.2f}")
                print(f"Venta más baja: ${min_venta:.2f}")

            print("="*80)
            print("                      FIN DEL CIERRE DE CAJA")
            print("="*80)

            # Opción para imprimir cierre
            imprimir = input("\n¿Desea imprimir este cierre de caja? (s/n): ")
            if imprimir.lower() == 's':
                self.imprimir_cierre_caja(periodo_id, fecha_inicio, fecha_fin, total_ventas)

            cursor.close()
            connection.close()

        except sqlite3.Error as err:
            print(f"Error al realizar cierre de caja: {err}")
        except ValueError:
            print("Por favor, ingrese un ID válido.")

    def imprimir_cierre_caja(self, periodo_id, fecha_inicio, fecha_fin, total_ventas):
        """Imprimir el cierre de caja"""
        try:
            import tempfile
            import subprocess
            import platform

            # Generar contenido resumido para impresión
            content = []
            content.append("="*50)
            content.append("           CIERRE DE CAJA")
            content.append("="*50)
            content.append(f"Periodo: {periodo_id}")
            content.append(f"Fecha: {fecha_inicio.strftime('%d/%m/%Y %H:%M')}")
            if fecha_fin:
                content.append(f"Hasta: {fecha_fin.strftime('%d/%m/%Y %H:%M')}")
            content.append(f"Total recaudado: ${total_ventas:.2f}")
            content.append("="*50)
            content.append(f"Impreso: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            content.append("="*50)
            content.append("\n")

            ticket_content = "\n".join(content)

            # Mostrar en pantalla
            print("\n" + ticket_content)

            # Intentar imprimir
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(ticket_content)
                temp_filename = temp_file.name

            sistema_operativo = platform.system()

            if sistema_operativo == "Windows":
                try:
                    subprocess.run(['print', temp_filename], shell=True, check=True)
                    print("\n✓ Cierre de caja enviado a impresora")
                except subprocess.CalledProcessError:
                    print("\n⚠ No se pudo imprimir automáticamente")
            else:
                try:
                    subprocess.run(['lp', temp_filename], check=True)
                    print("\n✓ Cierre de caja enviado a impresora")
                except subprocess.CalledProcessError:
                    print("\n⚠ No se pudo imprimir automáticamente")

            # Limpiar archivo temporal
            import os
            try:
                os.unlink(temp_filename)
            except:
                pass

        except Exception as e:
            print(f"Error al imprimir: {e}")

    def realizar_venta(self):
        """Realizar una nueva venta"""
        self.venta_actual = []
        self.total_venta = 0.0
        self.delivery_cost = 0.0

        print("\n" + "="*50)
        print("              NUEVA VENTA")
        print("="*50)

        while True:
            print("\nSeleccione una categoría:")
            print("1. Pizzas")
            print("2. Pizzas por mitades")
            print("3. Sandwiches")
            print("4. Hamburguesas")
            print("5. Al plato")
            print("6. Bebidas")
            print("7. Finalizar pedido")

            try:
                categoria = int(input("Opción: "))

                if categoria == 1:
                    resultado = self.seleccionar_productos("pizzas", "Pizzas")
                    if resultado == "finalizar":
                        break
                elif categoria == 2:
                    resultado = self.pizza_mitades()
                    if resultado == "finalizar":
                        break
                elif categoria == 3:
                    resultado = self.seleccionar_productos("sandwiches", "Sandwiches")
                    if resultado == "finalizar":
                        break
                elif categoria == 4:
                    resultado = self.seleccionar_productos("hamburguesas", "Hamburguesas")
                    if resultado == "finalizar":
                        break
                elif categoria == 5:
                    resultado = self.seleccionar_productos("platos", "Al plato")
                    if resultado == "finalizar":
                        break
                elif categoria == 6:
                    resultado = self.seleccionar_productos("bebidas", "Bebidas")
                    if resultado == "finalizar":
                        break
                elif categoria == 7:
                    break
                else:
                    print("Opción no válida.")

            except ValueError:
                print("Por favor, ingrese un número válido.")

        if self.venta_actual:
            self.procesar_venta()
        else:
            print("\nNo se agregaron productos a la venta.")

    def pizza_mitades(self):
        """Manejar pizzas por mitades"""
        print("\n--- PIZZA POR MITADES ---")
        print("Seleccione el primer sabor:")
        self.mostrar_menu("pizzas")

        try:
            opcion1 = int(input("Primera mitad: "))
            if opcion1 not in self.menu["pizzas"]:
                print("Opción no válida.")
                return

            print("\nSeleccione el segundo sabor:")
            self.mostrar_menu("pizzas")

            opcion2 = int(input("Segunda mitad: "))
            if opcion2 not in self.menu["pizzas"]:
                print("Opción no válida.")
                return

            pizza1 = self.menu["pizzas"][opcion1]
            pizza2 = self.menu["pizzas"][opcion2]

            # El precio de la pizza mitad: cada mitad es precio/2 + 5
            precio_mitad1 = (pizza1["precio"] / 2) + 5
            precio_mitad2 = (pizza2["precio"] / 2) + 5
            precio_total_mitades = precio_mitad1 + precio_mitad2

            cantidad = int(input("Cantidad: "))

            nombre_producto = f"{pizza1['nombre']} / {pizza2['nombre']} (Mitades)"

            item = {
                "categoria": "pizzas_mitades",
                "nombre": nombre_producto,
                "cantidad": cantidad,
                "precio_unitario": precio_total_mitades,
                "subtotal": precio_total_mitades * cantidad
            }

            self.venta_actual.append(item)
            self.total_venta += item["subtotal"]

            print(f"\n✓ Agregado: {cantidad}x {nombre_producto} - ${item['subtotal']:.2f}")
            print(f"   (${pizza1['precio']}/2 + $5) + (${pizza2['precio']}/2 + $5) = ${precio_total_mitades:.2f}")

            # Preguntar por bebidas
            agregar_bebidas = input("\n¿Desea agregar bebidas? (s/n): ")
            if agregar_bebidas.lower() == 's':
                self.seleccionar_productos("bebidas", "Bebidas")

            # Preguntar si desea finalizar pedido
            finalizar = input("\n¿Desea finalizar el pedido? (s/n): ")
            if finalizar.lower() == 's':
                return "finalizar"

        except ValueError:
            print("Por favor, ingrese números válidos.")

    def seleccionar_productos(self, categoria, nombre_categoria):
        """Seleccionar productos de una categoría específica"""
        while True:
            print(f"\n--- {nombre_categoria.upper()} ---")
            self.mostrar_menu(categoria)
            print("0. Volver al menú anterior")
            print("99. Eliminar artículo del pedido")

            try:
                opcion = int(input("Seleccione una opción: "))

                if opcion == 0:
                    break
                elif opcion == 99:
                    self.eliminar_articulo()
                elif opcion in self.menu[categoria]:
                    producto = self.menu[categoria][opcion]
                    cantidad = int(input(f"Cantidad de {producto['nombre']}: "))

                    if cantidad <= 0:
                        print("La cantidad debe ser mayor a 0.")
                        continue

                    item = {
                        "categoria": categoria,
                        "nombre": producto["nombre"],
                        "cantidad": cantidad,
                        "precio_unitario": producto["precio"],
                        "subtotal": producto["precio"] * cantidad
                    }

                    self.venta_actual.append(item)
                    self.total_venta += item["subtotal"]

                    print(f"\n✓ Agregado: {cantidad}x {producto['nombre']} - ${item['subtotal']:.2f}")

                    # Preguntar por bebidas (excepto si ya estamos en bebidas)
                    if categoria != "bebidas":
                        agregar_bebidas = input("\n¿Desea agregar bebidas? (s/n): ")
                        if agregar_bebidas.lower() == 's':
                            self.seleccionar_productos("bebidas", "Bebidas")

                    # Preguntar si desea finalizar pedido
                    finalizar = input("\n¿Desea finalizar el pedido? (s/n): ")
                    if finalizar.lower() == 's':
                        return "finalizar"

                else:
                    print("Opción no válida.")

            except ValueError:
                print("Por favor, ingrese números válidos.")

    def mostrar_menu(self, categoria):
        """Mostrar el menú de una categoría"""
        for id_item, item in self.menu[categoria].items():
            print(f"{id_item:2d}. {item['nombre']:<35} ${item['precio']:>6.2f}")

    def eliminar_articulo(self):
        """Eliminar un artículo del pedido actual"""
        if not self.venta_actual:
            print("\nNo hay artículos en el pedido actual.")
            return

        print("\nARTÍCULOS EN EL PEDIDO:")
        for i, item in enumerate(self.venta_actual, 1):
            print(f"{i}. {item['cantidad']}x {item['nombre']} - ${item['subtotal']:.2f}")

        try:
            indice = int(input("\nNúmero del artículo a eliminar: ")) - 1

            if 0 <= indice < len(self.venta_actual):
                item_eliminado = self.venta_actual.pop(indice)
                self.total_venta -= item_eliminado["subtotal"]
                print(f"\n✓ Eliminado: {item_eliminado['nombre']}")
            else:
                print("Número de artículo no válido.")

        except ValueError:
            print("Por favor, ingrese un número válido.")

    def procesar_venta(self):
        """Procesar la venta actual sin doble confirmación"""
        print("\n" + "="*60)
        print("                    RESUMEN DE VENTA")
        print("="*60)

        for item in self.venta_actual:
            print(f"{item['cantidad']}x {item['nombre']:<35} ${item['subtotal']:>8.2f}")

        print("-" * 60)
        print(f"Subtotal: ${self.total_venta:>51.2f}")

        # Tipo de servicio
        while True:
            print("\nTipo de servicio:")
            print("1. Para llevar")
            print("2. Para comer en el local")
            


            try:
                tipo = int(input("Seleccione: "))
                if tipo == 1:
                    self.tipo_servicio = "Para llevar"
                    delivery = float(input("Ingrese el costo de delivery: $"))
                    self.delivery_cost = delivery
                    break
                elif tipo == 2:
                    self.tipo_servicio = "En el local"
                    self.delivery_cost = 0
                    break
                
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, ingrese un valor válido.")

        total_final = self.total_venta + self.delivery_cost

        if self.delivery_cost > 0:
            print(f"Delivery: ${self.delivery_cost:>52.2f}")
            print("-" * 60)

        print(f"TOTAL: ${total_final:>54.2f}")
        print("=" * 60)

        # UNA SOLA confirmación
        confirmar = input("\n¿Confirmar la venta? (s/n): ")
        if confirmar.lower() == 's':
            self.guardar_venta(total_final)

            # Preguntar por ticket e imprimir automáticamente
            ticket = input("¿Desea imprimir el ticket de venta? (s/n): ")
            if ticket.lower() == 's':
                self.imprimir_ticket_real(total_final)
        else:
            print("\nVenta cancelada.")

    def guardar_venta(self, total_final):
        """Guardar la venta en la base de datos"""
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()

            # Insertar venta
            cursor.execute("""
                INSERT INTO ventas (periodo_id, tipo_servicio, subtotal, delivery, total)
                VALUES (?, ?, ?, ?, ?)
            """, (self.periodo_activo, self.tipo_servicio, self.total_venta, self.delivery_cost, total_final))

            venta_id = cursor.lastrowid

            # Insertar detalles de venta
            for item in self.venta_actual:
                cursor.execute("""
                    INSERT INTO detalle_ventas (venta_id, categoria, producto, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (venta_id, item['categoria'], item['nombre'], item['cantidad'], item['precio_unitario'], item['subtotal']))

            connection.commit()
            cursor.close()
            connection.close()

            print(f"\n✓ Venta guardada exitosamente! (ID: {venta_id})")

        except sqlite3.Error as err:
            print(f"Error al guardar venta: {err}")

    def imprimir_ticket_real(self, total_final):
        """Imprimir ticket real en impresora y mostrar en pantalla"""
        # Contenido del ticket
        ticket_content = self.generar_contenido_ticket(total_final)

        # Mostrar en pantalla
        print(ticket_content)

        # Intentar imprimir en impresora real
        try:
            import tempfile
            import subprocess
            import platform

            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(ticket_content)
                temp_filename = temp_file.name

            sistema_operativo = platform.system()

            if sistema_operativo == "Windows":
                # En Windows - enviar a impresora predeterminada
                try:
                    subprocess.run(['notepad', '/p', temp_filename], check=True)
                    print("\n✓ Ticket enviado a la impresora predeterminada")
                except subprocess.CalledProcessError:
                    # Alternativa: usar comando print
                    try:
                        subprocess.run(['print', temp_filename], shell=True, check=True)
                        print("\n✓ Ticket enviado a la impresora")
                    except subprocess.CalledProcessError:
                        print("\n⚠ No se pudo imprimir automáticamente. Ticket mostrado en pantalla.")

            elif sistema_operativo == "Linux":
                # En Linux - usar lp (Line Printer)
                try:
                    subprocess.run(['lp', temp_filename], check=True)
                    print("\n✓ Ticket enviado a la impresora predeterminada")
                except subprocess.CalledProcessError:
                    try:
                        # Alternativa con lpr
                        subprocess.run(['lpr', temp_filename], check=True)
                        print("\n✓ Ticket enviado a la impresora")
                    except subprocess.CalledProcessError:
                        print("\n⚠ No se pudo imprimir automáticamente. Ticket mostrado en pantalla.")

            elif sistema_operativo == "Darwin":  # macOS
                # En macOS - usar lp
                try:
                    subprocess.run(['lp', temp_filename], check=True)
                    print("\n✓ Ticket enviado a la impresora predeterminada")
                except subprocess.CalledProcessError:
                    print("\n⚠ No se pudo imprimir automáticamente. Ticket mostrado en pantalla.")

            # Limpiar archivo temporal
            import os
            try:
                os.unlink(temp_filename)
            except:
                pass

        except ImportError:
            print("\n⚠ Módulos de impresión no disponibles. Ticket mostrado en pantalla.")
        except Exception as e:
            print(f"\n⚠ Error al imprimir: {e}")
            print("Ticket mostrado en pantalla.")

    def generar_contenido_ticket(self, total_final):
        """Generar el contenido del ticket de venta"""
        content = []
        content.append("="*50)
        content.append("                  TICKET DE VENTA")
        content.append("="*50)
        content.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        content.append(f"Tipo de servicio: {self.tipo_servicio}")
        content.append("-" * 50)

        for item in self.venta_actual:
            content.append(f"{item['cantidad']}x {item['nombre']}")
            content.append(f"    ${item['precio_unitario']:.2f} c/u = ${item['subtotal']:.2f}")

        content.append("-" * 50)
        content.append(f"Subtotal: ${self.total_venta:.2f}")

        if self.delivery_cost > 0:
            content.append(f"Delivery: ${self.delivery_cost:.2f}")

        content.append(f"TOTAL: ${total_final:.2f}")
        content.append("="*50)
        content.append("        ¡Gracias por su compra!")
        content.append("="*50)
        content.append("\n")  # Línea extra para corte de papel

        return "\n".join(content)

# Ejecutar el sistema
if __name__ == "__main__":
    sistema = SistemaVentas()
    sistema.menu_principal()