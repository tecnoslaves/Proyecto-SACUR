import sys
import os
import hashlib
import secrets
import base64
import shutil
from datetime import datetime
import platform
import subprocess
import tempfile

# Intentamos importar sqlcipher, si falla para pruebas gráficas usamos sqlite3 estándar
try:
    from sqlcipher3 import dbapi2 as sqlite3
except ImportError:
    import sqlite3 

# IMPORTANTE: Aseguramos que QDoubleSpinBox esté importado
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGridLayout, QGroupBox, QInputDialog, QDialog,
                             QComboBox, QDateEdit, QTextEdit, QFrame, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QSize, QDate
from PyQt6.QtGui import QFont, QColor, QIcon

# =============================================================================
# BACKEND (Lógica y Base de Datos)
# =============================================================================

class SistemaVentasBackend:
    def __init__(self):
        self.periodo_activo = None
        self.db_path = "stella_sacur.db"
        self.key_file = ".db_key"
        self.db_password = None
        
        self.venta_actual = [] 
        self.total_venta = 0.0
        
        # Menú Completo
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
                1: {"nombre": "Milanesa de Carne", "precio": 30},
                2: {"nombre": "Milanesa de Pollo", "precio": 30},
                3: {"nombre": "Napolitano", "precio": 38},
                4: {"nombre": "Lomito", "precio": 30},
                5: {"nombre": "Lomito Montado", "precio": 38},
                6: {"nombre": "Chacarero Personal", "precio": 38},
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
            },
            "tragos": {
                1: {"nombre": "Mojito", "precio": 45},
                2: {"nombre": "Piña colada", "precio": 45},
                3: {"nombre": "Garibaldi", "precio": 45},
                4: {"nombre": "Pantera rosa", "precio": 45},
                5: {"nombre": "Esperma de pitufo", "precio": 45},
                6: {"nombre": "Sex on the beach", "precio": 45},
                7: {"nombre": "Atomic Green", "precio": 45},
                8: {"nombre": "Kriptonita", "precio": 45},
                9: {"nombre": "Caipirinha", "precio": 45},
                10: {"nombre": "Caipirisma", "precio": 45},
                11: {"nombre": "Piel de igüana", "precio": 40},
                12: {"nombre": "Destornillador", "precio": 40},
                13: {"nombre": "Daiquiri", "precio": 40},
                14: {"nombre": "Charro negro", "precio": 40},
                15: {"nombre": "Cuba Libre", "precio": 40},
                16: {"nombre": "Chuflay", "precio": 40},
                17: {"nombre": "Tekila Sunrise", "precio": 40},
                18: {"nombre": "Fernet", "precio": 40},
                19: {"nombre": "Ruso negro", "precio": 40},
                20: {"nombre": "Caipirosca", "precio": 40},
                21: {"nombre": "Frozen de FRUTILLA", "precio": 45},
                22: {"nombre": "Frozen de DURAZNO", "precio": 45},
                23: {"nombre": "Frozen de PIÑA", "precio": 45},
                24: {"nombre": "Gin Tonic", "precio": 50},
                25: {"nombre": "Whisky", "precio": 50},
                26: {"nombre": "Amarula", "precio": 50},
                27: {"nombre": "Pecera", "precio": 50},
            }
        }

    # --- MÉTODOS DE CIFRADO Y ACCESO ---
    def existe_clave(self):
        return os.path.exists(self.key_file)

    def crear_clave(self, password):
        salt = secrets.token_bytes(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        key_data = base64.b64encode(salt).decode() + '\n' + base64.b64encode(key).decode()
        with open(self.key_file, 'w') as f:
            f.write(key_data)
        if os.name == 'nt':
            os.system(f'attrib +h {self.key_file}')
        self.db_password = password
        self.inicializar_base_datos()
        return True

    def verificar_clave(self, password):
        try:
            with open(self.key_file, 'r') as f:
                lines = f.read().strip().split('\n')
                salt = base64.b64decode(lines[0])
                stored_key = lines[1]
            derived_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            derived_key_b64 = base64.b64encode(derived_key).decode()
            if derived_key_b64 == stored_key:
                self.db_password = password
                self.inicializar_base_datos() # Verificar migraciones
                self.verificar_periodo_activo()
                return True
            return False
        except Exception:
            return False

    def obtener_conexion(self):
        conn = sqlite3.connect(self.db_path)
        if hasattr(conn, 'execute'): 
            try:
                conn.execute(f"PRAGMA key = '{self.db_password}'")
            except:
                pass 
        return conn

    def inicializar_base_datos(self):
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS periodos_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_inicio DATETIME NOT NULL,
                fecha_fin DATETIME,
                activo BOOLEAN DEFAULT 1,
                total_ventas REAL DEFAULT 0.00
            )
        """)
        
        # Tabla Ventas con metodo_pago
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                periodo_id INTEGER,
                fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo_servicio TEXT,
                subtotal REAL,
                delivery REAL DEFAULT 0.00,
                total REAL,
                telefono_cliente TEXT,
                metodo_pago TEXT DEFAULT 'Efectivo',
                FOREIGN KEY (periodo_id) REFERENCES periodos_venta(id)
            )
        """)
        
        # Migración automática si falta la columna (para no romper tu DB actual)
        try:
            cursor.execute("ALTER TABLE ventas ADD COLUMN metodo_pago TEXT DEFAULT 'Efectivo'")
        except:
            pass 

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
        conn.commit()
        conn.close()

    def verificar_periodo_activo(self):
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM periodos_venta WHERE activo = 1")
        res = cursor.fetchone()
        self.periodo_activo = res[0] if res else None
        conn.close()

    def crear_periodo(self, fecha_inicio=None):
        if self.periodo_activo:
            return False, "Ya existe un periodo activo."
        if not fecha_inicio:
            fecha_inicio = datetime.now()
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO periodos_venta (fecha_inicio, activo) VALUES (?, 1)", (fecha_inicio,))
        self.periodo_activo = cursor.lastrowid
        conn.commit()
        conn.close()
        return True, self.periodo_activo

    def finalizar_periodo(self):
        if not self.periodo_activo:
            return False, "No hay periodo activo."
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE periodo_id = ?", (self.periodo_activo,))
        total = cursor.fetchone()[0]
        cursor.execute("UPDATE periodos_venta SET fecha_fin = ?, activo = 0, total_ventas = ? WHERE id = ?", 
                       (datetime.now(), total, self.periodo_activo))
        conn.commit()
        conn.close()
        self.periodo_activo = None
        return True, total

    def registrar_venta(self, tipo_servicio, delivery, telefono, metodo_pago):
        if not self.periodo_activo:
            return False, "No hay periodo activo."
        
        total_final = self.total_venta + delivery
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ventas (periodo_id, tipo_servicio, subtotal, delivery, total, telefono_cliente, metodo_pago)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.periodo_activo, tipo_servicio, self.total_venta, delivery, total_final, telefono, metodo_pago))
        venta_id = cursor.lastrowid
        
        for item in self.venta_actual:
            cursor.execute("""
                INSERT INTO detalle_ventas (venta_id, categoria, producto, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (venta_id, item['categoria'], item['nombre'], item['cantidad'], item['precio_unitario'], item['subtotal']))
        
        conn.commit()
        conn.close()
        
        ticket = self.generar_texto_ticket(venta_id, tipo_servicio, delivery, total_final, metodo_pago)
        
        self.venta_actual = []
        self.total_venta = 0.0
        return True, ticket

    def generar_texto_ticket(self, id_venta, tipo, delivery, total, metodo):
        lines = []
        lines.append("="*40)
        lines.append("        TICKET DE VENTA")
        lines.append("="*40)
        lines.append(f"ID Venta: {id_venta}")
        lines.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append(f"Servicio: {tipo}")
        lines.append(f"Pago: {metodo}")
        lines.append("-" * 40)
        for item in self.venta_actual:
            lines.append(f"{item['cantidad']}x {item['nombre']}")
            lines.append(f"   ${item['subtotal']:.2f}")
        lines.append("-" * 40)
        lines.append(f"Subtotal: ${self.total_venta:.2f}")
        if delivery > 0:
            lines.append(f"Delivery: ${delivery:.2f}")
        lines.append(f"TOTAL:    ${total:.2f}")
        lines.append("="*40)
        lines.append("    ¡Gracias por su compra!")
        lines.append("="*40)
        lines.append("\n\n\n") 
        return "\n".join(lines)
    
    def crear_backup(self):
        if not os.path.exists(self.db_path): return False, "No existe DB"
        backup_dir = "backups"
        if not os.path.exists(backup_dir): os.makedirs(backup_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")
        shutil.copy2(self.db_path, backup_file)
        return True, backup_file

    def obtener_reporte_caja(self, fecha_str=None):
        conn = self.obtener_conexion()
        cursor = conn.cursor()
        
        filtro_sql = ""
        params = ()
        titulo = ""

        if fecha_str:
            try:
                fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")
                fecha_sql = fecha_obj.strftime("%Y-%m-%d")
                filtro_sql = "WHERE date(fecha_venta) = date(?)"
                params = (fecha_sql,)
                titulo = f"Reporte del día: {fecha_str}"
            except ValueError:
                conn.close()
                return False, "Formato de fecha inválido (use DD/MM/YYYY)"
        else:
            if not self.periodo_activo:
                conn.close()
                return False, "No hay periodo activo. Ingrese una fecha específica."
            filtro_sql = "WHERE periodo_id = ?"
            params = (self.periodo_activo,)
            titulo = f"Reporte del Periodo Activo (ID: {self.periodo_activo})"

        # 1. Totales por Método de Pago
        cursor.execute(f"""
            SELECT metodo_pago, COUNT(*), SUM(total) 
            FROM ventas 
            {filtro_sql} 
            GROUP BY metodo_pago
        """, params)
        pagos = cursor.fetchall()

        # 2. Desglose Delivery vs Productos
        cursor.execute(f"SELECT SUM(delivery) FROM ventas {filtro_sql}", params)
        total_delivery = cursor.fetchone()[0] or 0.0
        
        cursor.execute(f"SELECT SUM(total) FROM ventas {filtro_sql}", params)
        total_global = cursor.fetchone()[0] or 0.0
        
        total_productos = total_global - total_delivery

        # 3. Lista Detallada
        cursor.execute(f"""
            SELECT id, strftime('%H:%M', fecha_venta), tipo_servicio, metodo_pago, delivery, total 
            FROM ventas 
            {filtro_sql}
            ORDER BY fecha_venta DESC
        """, params)
        lista_ventas = cursor.fetchall()

        conn.close()

        datos = {
            "titulo": titulo,
            "pagos": pagos,
            "finanzas": {
                "delivery": total_delivery,
                "productos": total_productos,
                "global": total_global
            },
            "lista": lista_ventas
        }
        return True, datos

# =============================================================================
# FRONTEND (GUI - PyQt6) - TEMA OSCURO
# =============================================================================

class LoginDialog(QDialog):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.setWindowTitle("Tecno Slaves - Login Seguro")
        self.setFixedSize(400, 250)
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: #ffffff; }
            QLabel { color: #ffffff; font-size: 14px; }
            QLineEdit { 
                background-color: #353535; 
                color: white; 
                padding: 5px; 
                border: 1px solid #555; 
                border-radius: 5px;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        
        layout = QVBoxLayout()
        
        lbl_title = QLabel("SISTEMA DE VENTAS")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #f1c40f;") 
        layout.addWidget(lbl_title)

        self.lbl_info = QLabel("Ingrese su contraseña de descifrado:")
        layout.addWidget(self.lbl_info)
        
        self.txt_pass = QLineEdit()
        self.txt_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.txt_pass)
        
        self.first_time = not self.backend.existe_clave()
        self.txt_confirm = QLineEdit()
        self.txt_confirm.setPlaceholderText("Confirme contraseña")
        self.txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        if self.first_time:
            self.lbl_info.setText("CONFIGURACIÓN INICIAL\nCree una contraseña segura (mín 8 car):")
            layout.addWidget(self.txt_confirm)
            
        btn_login = QPushButton("INGRESAR")
        btn_login.clicked.connect(self.procesar_login)
        layout.addWidget(btn_login)
        
        self.setLayout(layout)

    def procesar_login(self):
        pwd = self.txt_pass.text()
        if self.first_time:
            conf = self.txt_confirm.text()
            if len(pwd) < 8:
                QMessageBox.warning(self, "Error", "Mínimo 8 caracteres.")
                return
            if pwd != conf:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden.")
                return
            self.backend.crear_clave(pwd)
            self.accept()
        else:
            if self.backend.verificar_clave(pwd):
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Contraseña incorrecta.")
                self.txt_pass.clear()

# --- CLASE DIÁLOGO DE COBRO (OPCIÓN B) ---
class DialogoCobro(QDialog):
    """
    Diálogo separado para procesar el pago. 
    Esta es la solución 'Opción B' que arregla el problema del campo de delivery.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesar Pago")
        self.setFixedSize(400, 350)
        
        # Estilos oscuros específicos
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { font-size: 14px; font-weight: bold; color: white; }
            QComboBox, QLineEdit, QDoubleSpinBox { 
                background-color: #353535; 
                color: white; 
                border: 1px solid #555; 
                padding: 5px; 
                border-radius: 4px;
                font-size: 14px;
            }
            /* Visualmente deshabilitado */
            QDoubleSpinBox:disabled, QLineEdit:disabled {
                background-color: #252525;
                color: #555;
                border: 1px solid #333;
            }
            QPushButton { 
                background-color: #27ae60; 
                color: white; 
                padding: 10px; 
                border-radius: 4px; 
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)

        layout = QVBoxLayout(self)

        # 1. Tipo de Servicio
        layout.addWidget(QLabel("Tipo de Servicio:"))
        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["En el local", "Para llevar"])
        layout.addWidget(self.cb_tipo)

        # 2. Método de Pago
        layout.addWidget(QLabel("Método de Pago:"))
        self.cb_pago = QComboBox()
        self.cb_pago.addItems(["Efectivo", "Transferencia"])
        layout.addWidget(self.cb_pago)

        # 3. Teléfono
        layout.addWidget(QLabel("Teléfono Cliente:"))
        self.txt_tel = QLineEdit()
        self.txt_tel.setPlaceholderText("Opcional")
        layout.addWidget(self.txt_tel)

        # 4. Costo Delivery (SpinBox)
        layout.addWidget(QLabel("Costo Delivery ($):"))
        self.spin_delivery = QDoubleSpinBox()
        self.spin_delivery.setRange(0, 999999)
        self.spin_delivery.setPrefix("$ ")
        self.spin_delivery.setDecimals(2)
        self.spin_delivery.setSingleStep(50)
        self.spin_delivery.setValue(0.00)
        self.spin_delivery.setEnabled(False) # Inicia bloqueado
        layout.addWidget(self.spin_delivery)

        # Botón Confirmar
        self.btn_confirmar = QPushButton("CONFIRMAR VENTA")
        self.btn_confirmar.clicked.connect(self.accept)
        layout.addWidget(self.btn_confirmar)

        # Lógica de activación
        self.cb_tipo.currentIndexChanged.connect(self.actualizar_estado_delivery)

    def actualizar_estado_delivery(self, index):
        # Indice 1 es "Para llevar"
        if index == 1:
            self.spin_delivery.setEnabled(True)
            self.spin_delivery.setFocus()
            self.spin_delivery.selectAll()
        else:
            self.spin_delivery.setEnabled(False)
            self.spin_delivery.setValue(0.00)

    def obtener_datos(self):
        return {
            "tipo": self.cb_tipo.currentText(),
            "pago": self.cb_pago.currentText(),
            "telefono": self.txt_tel.text(),
            "delivery": self.spin_delivery.value()
        }

class PanelVentas(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        layout = QHBoxLayout()
        
        # --- IZQUIERDA: MENÚ ---
        left_panel = QGroupBox("Menú")
        left_layout = QVBoxLayout()
        
        self.cb_categorias = QComboBox()
        self.cb_categorias.addItems([k.capitalize() for k in self.backend.menu.keys()])
        self.cb_categorias.currentIndexChanged.connect(self.cargar_productos)
        left_layout.addWidget(QLabel("Categoría:"))
        left_layout.addWidget(self.cb_categorias)
        
        self.tabla_productos = QTableWidget()
        self.tabla_productos.setColumnCount(3)
        self.tabla_productos.setHorizontalHeaderLabels(["Nombre", "Precio", "Acción"])
        self.tabla_productos.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_productos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        left_layout.addWidget(self.tabla_productos)
        
        btn_mitades = QPushButton("🍕 Pizza Mitades")
        btn_mitades.setStyleSheet("background-color: #e67e22; color: white;")
        btn_mitades.clicked.connect(self.dialogo_mitades)
        left_layout.addWidget(btn_mitades)

        left_panel.setLayout(left_layout)
        
        # --- DERECHA: TICKET ACTUAL ---
        right_panel = QGroupBox("Ticket Actual")
        right_layout = QVBoxLayout()
        
        self.tabla_ticket = QTableWidget()
        self.tabla_ticket.setColumnCount(4)
        self.tabla_ticket.setHorizontalHeaderLabels(["Cant", "Producto", "Subtotal", "X"])
        self.tabla_ticket.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.tabla_ticket)
        
        self.lbl_total = QLabel("Total: $0.00")
        self.lbl_total.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_total.setStyleSheet("color: #2ecc71; font-weight: bold;") 
        right_layout.addWidget(self.lbl_total)
        
        btn_checkout = QPushButton("COBRAR / FINALIZAR")
        btn_checkout.setMinimumHeight(50)
        btn_checkout.setStyleSheet("background-color: #27ae60; color: white; font-size: 16px; font-weight: bold;")
        btn_checkout.clicked.connect(self.procesar_cobro)
        right_layout.addWidget(btn_checkout)
        
        btn_limpiar = QPushButton("Cancelar Pedido")
        btn_limpiar.setStyleSheet("background-color: #c0392b; color: white;")
        btn_limpiar.clicked.connect(self.limpiar_pedido)
        right_layout.addWidget(btn_limpiar)
        
        right_panel.setLayout(right_layout)
        
        layout.addWidget(left_panel, 60)
        layout.addWidget(right_panel, 40)
        self.setLayout(layout)
        
        self.cargar_productos()

    def cargar_productos(self):
        cat = self.cb_categorias.currentText().lower()
        productos = self.backend.menu.get(cat, {})
        self.tabla_productos.setRowCount(0)
        
        row = 0
        for id_prod, data in productos.items():
            self.tabla_productos.insertRow(row)
            self.tabla_productos.setItem(row, 0, QTableWidgetItem(data['nombre']))
            self.tabla_productos.setItem(row, 1, QTableWidgetItem(f"${data['precio']}"))
            
            btn_add = QPushButton("+")
            btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_add.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
            btn_add.clicked.connect(lambda checked, p=data: self.agregar_producto(p))
            self.tabla_productos.setCellWidget(row, 2, btn_add)
            row += 1

    def agregar_producto(self, producto):
        d = QDialog(self)
        d.setWindowTitle("Cantidad")
        d.setStyleSheet("background-color: #2b2b2b; color: white;")
        l = QVBoxLayout(d)
        l.addWidget(QLabel(f"Cantidad de {producto['nombre']}:"))
        spin = QLineEdit("1")
        spin.setStyleSheet("background-color: #353535; color: white; padding: 5px;")
        l.addWidget(spin)
        btn = QPushButton("Aceptar")
        btn.setStyleSheet("background-color: #27ae60; padding: 5px;")
        btn.clicked.connect(d.accept)
        l.addWidget(btn)
        
        if d.exec() == QDialog.DialogCode.Accepted:
            try:
                cant = int(spin.text())
                if cant < 1: cant = 1
            except:
                cant = 1
                
            item = {
                "categoria": self.cb_categorias.currentText(),
                "nombre": producto["nombre"],
                "cantidad": cant,
                "precio_unitario": producto["precio"],
                "subtotal": producto["precio"] * cant
            }
            self.backend.venta_actual.append(item)
            self.backend.total_venta += item["subtotal"]
            self.actualizar_ticket()

    def dialogo_mitades(self):
        d = QDialog(self)
        d.setWindowTitle("Pizza Mitades")
        d.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QComboBox { background-color: #353535; color: white; padding: 5px; }
            QLabel { color: white; }
            QPushButton { background-color: #e67e22; color: white; padding: 5px; }
        """)
        l = QVBoxLayout(d)
        
        c1 = QComboBox()
        c2 = QComboBox()
        pizzas = self.backend.menu["pizzas"]
        for k, v in pizzas.items():
            c1.addItem(v["nombre"], v["precio"])
            c2.addItem(v["nombre"], v["precio"])
            
        l.addWidget(QLabel("Mitad 1:"))
        l.addWidget(c1)
        l.addWidget(QLabel("Mitad 2:"))
        l.addWidget(c2)
        
        btn = QPushButton("Agregar")
        l.addWidget(btn)
        
        def confirmar():
            p1_precio = c1.currentData()
            p2_precio = c2.currentData()
            precio_total = (p1_precio/2 + 5) + (p2_precio/2 + 5)
            nombre = f"{c1.currentText()} / {c2.currentText()} (Mitades)"
            
            item = {
                "categoria": "mitades",
                "nombre": nombre,
                "cantidad": 1,
                "precio_unitario": precio_total,
                "subtotal": precio_total
            }
            self.backend.venta_actual.append(item)
            self.backend.total_venta += item["subtotal"]
            self.actualizar_ticket()
            d.accept()
            
        btn.clicked.connect(confirmar)
        d.exec()

    def actualizar_ticket(self):
        self.tabla_ticket.setRowCount(0)
        for i, item in enumerate(self.backend.venta_actual):
            self.tabla_ticket.insertRow(i)
            self.tabla_ticket.setItem(i, 0, QTableWidgetItem(str(item['cantidad'])))
            self.tabla_ticket.setItem(i, 1, QTableWidgetItem(item['nombre']))
            self.tabla_ticket.setItem(i, 2, QTableWidgetItem(f"${item['subtotal']:.2f}"))
            
            btn_del = QPushButton("X")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet("background-color: transparent; color: #e74c3c; font-weight: bold; font-size: 14px; border: none;")
            btn_del.clicked.connect(lambda checked, idx=i: self.eliminar_item(idx))
            self.tabla_ticket.setCellWidget(i, 3, btn_del)
            
        self.lbl_total.setText(f"Total: ${self.backend.total_venta:.2f}")

    def eliminar_item(self, index):
        item = self.backend.venta_actual.pop(index)
        self.backend.total_venta -= item['subtotal']
        self.actualizar_ticket()

    def limpiar_pedido(self):
        self.backend.venta_actual = []
        self.backend.total_venta = 0.0
        self.actualizar_ticket()

    # --- MÉTODO CORREGIDO QUE USA LA CLASE EXTERNA ---
    def procesar_cobro(self):
        if not self.backend.venta_actual:
            QMessageBox.warning(self, "Vacío", "No hay productos.")
            return
        
        if not self.backend.periodo_activo:
            QMessageBox.warning(self, "Error", "NO HAY UN PERIODO DE CAJA ABIERTO.\nVaya a la pestaña 'Caja' y abra turno.")
            return

        # Instanciamos la clase DialogoCobro (Opción B)
        dialogo = DialogoCobro(self)
        
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            
            ok, ticket_text = self.backend.registrar_venta(
                datos["tipo"], 
                datos["delivery"], 
                datos["telefono"],
                datos["pago"]
            )

            if ok:
                self.limpiar_pedido()
                
                reply = QMessageBox.question(self, "Imprimir", "Venta registrada exitosamente.\n¿Desea imprimir el ticket?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.imprimir_ticket_fisico(ticket_text)
            else:
                QMessageBox.critical(self, "Error", ticket_text)

    def imprimir_ticket_fisico(self, contenido):
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(contenido)
                temp_filename = temp_file.name

            sistema_operativo = platform.system()
            if sistema_operativo == "Windows":
                subprocess.run(['notepad', '/p', temp_filename], check=True)
            else:
                subprocess.run(['lp', temp_filename], check=True)
        except Exception as e:
            QMessageBox.warning(self, "Error de Impresión", f"No se pudo imprimir automáticamente.\n{str(e)}")


class PanelCaja(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        
        main_layout = QVBoxLayout()
        
        # === SECCIÓN 1: CONTROL DE CAJA ===
        gb_control = QGroupBox("Control de Turno")
        control_layout = QHBoxLayout()
        
        self.lbl_estado = QLabel("Estado: DESCONOCIDO")
        self.lbl_estado.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        control_layout.addWidget(self.lbl_estado)
        
        btn_abrir = QPushButton("Abrir Turno")
        btn_abrir.setStyleSheet("background-color: #2980b9; color: white;")
        btn_abrir.clicked.connect(self.abrir_periodo)
        control_layout.addWidget(btn_abrir)
        
        btn_cerrar = QPushButton("Cerrar Turno")
        btn_cerrar.setStyleSheet("background-color: #c0392b; color: white;")
        btn_cerrar.clicked.connect(self.cerrar_periodo)
        control_layout.addWidget(btn_cerrar)
        
        btn_backup = QPushButton("Backup DB")
        btn_backup.setStyleSheet("background-color: #8e44ad; color: white;")
        btn_backup.clicked.connect(self.backup)
        control_layout.addWidget(btn_backup)
        
        gb_control.setLayout(control_layout)
        main_layout.addWidget(gb_control)
        
        # === SECCIÓN 2: REPORTES DETALLADOS ===
        gb_reportes = QGroupBox("Reporte de Ventas")
        reportes_layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar fecha (DD/MM/YYYY) o dejar vacío para turno actual:"))
        self.txt_fecha_search = QLineEdit()
        self.txt_fecha_search.setPlaceholderText("Ej: 25/12/2023")
        self.txt_fecha_search.setFixedWidth(150)
        search_layout.addWidget(self.txt_fecha_search)
        
        btn_buscar = QPushButton("🔍 Ver Reporte")
        btn_buscar.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        btn_buscar.clicked.connect(self.cargar_reporte)
        search_layout.addWidget(btn_buscar)
        search_layout.addStretch()
        reportes_layout.addLayout(search_layout)
        
        # Resumen Global
        summary_layout = QHBoxLayout()
        self.lbl_resumen_global = QLabel("Total Global: $0.00")
        self.lbl_resumen_global.setStyleSheet("border: 1px solid #555; padding: 10px; font-size: 14px; color: #2ecc71; font-weight: bold;")
        
        self.lbl_resumen_medios = QLabel("Efectivo: $0.00 | Transferencia: $0.00")
        self.lbl_resumen_medios.setStyleSheet("border: 1px solid #555; padding: 10px; font-size: 12px;")
        
        self.lbl_resumen_delivery = QLabel("Productos: $0.00 | Delivery: $0.00")
        self.lbl_resumen_delivery.setStyleSheet("border: 1px solid #555; padding: 10px; font-size: 12px;")
        
        summary_layout.addWidget(self.lbl_resumen_global)
        summary_layout.addWidget(self.lbl_resumen_medios)
        summary_layout.addWidget(self.lbl_resumen_delivery)
        reportes_layout.addLayout(summary_layout)
        
        # Tabla Detalle
        self.tabla_detalle = QTableWidget()
        self.tabla_detalle.setColumnCount(5)
        self.tabla_detalle.setHorizontalHeaderLabels(["Hora", "Tipo", "Pago", "Delivery", "Total"])
        self.tabla_detalle.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        reportes_layout.addWidget(self.tabla_detalle)
        
        gb_reportes.setLayout(reportes_layout)
        main_layout.addWidget(gb_reportes)
        
        self.setLayout(main_layout)
        self.actualizar_estado()

    def actualizar_estado(self):
        self.backend.verificar_periodo_activo()
        if self.backend.periodo_activo:
            self.lbl_estado.setText(f"Estado: CAJA ABIERTA")
            self.lbl_estado.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px;")
        else:
            self.lbl_estado.setText("Estado: CAJA CERRADA")
            self.lbl_estado.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")

    def abrir_periodo(self):
        ok, msg = self.backend.crear_periodo()
        if ok:
            QMessageBox.information(self, "Éxito", "Periodo abierto.")
        else:
            QMessageBox.warning(self, "Aviso", msg)
        self.actualizar_estado()

    def cerrar_periodo(self):
        reply = QMessageBox.question(self, "Confirmar", "¿Cerrar caja actual?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            ok, total = self.backend.finalizar_periodo()
            if ok:
                QMessageBox.information(self, "Cierre", f"Caja cerrada.\nTotal Ventas: ${total:.2f}")
            else:
                QMessageBox.warning(self, "Error", str(total))
            self.actualizar_estado()
            
    def backup(self):
        ok, path = self.backend.crear_backup()
        if ok:
            QMessageBox.information(self, "Backup", f"Backup creado en:\n{path}")
        else:
            QMessageBox.critical(self, "Error", path)
            
    def cargar_reporte(self):
        fecha = self.txt_fecha_search.text().strip()
        ok, data = self.backend.obtener_reporte_caja(fecha if fecha else None)
        
        if not ok:
            QMessageBox.warning(self, "Aviso", data)
            return
            
        f = data["finanzas"]
        self.lbl_resumen_global.setText(f"Total Global: ${f['global']:.2f}")
        self.lbl_resumen_delivery.setText(f"Productos: ${f['productos']:.2f} | Delivery: ${f['delivery']:.2f}")
        
        txt_medios = []
        for metodo, cant, total in data["pagos"]:
            txt_medios.append(f"{metodo}: ${total:.2f}")
        self.lbl_resumen_medios.setText(" | ".join(txt_medios) if txt_medios else "Sin ventas")
        
        self.tabla_detalle.setRowCount(0)
        for row_data in data["lista"]:
            row_idx = self.tabla_detalle.rowCount()
            self.tabla_detalle.insertRow(row_idx)
            self.tabla_detalle.setItem(row_idx, 0, QTableWidgetItem(str(row_data[1])))
            self.tabla_detalle.setItem(row_idx, 1, QTableWidgetItem(row_data[2]))
            self.tabla_detalle.setItem(row_idx, 2, QTableWidgetItem(row_data[3]))
            self.tabla_detalle.setItem(row_idx, 3, QTableWidgetItem(f"${row_data[4]:.2f}"))
            self.tabla_detalle.setItem(row_idx, 4, QTableWidgetItem(f"${row_data[5]:.2f}"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.aplicar_tema_oscuro()
        self.backend = SistemaVentasBackend()
        
        login = LoginDialog(self.backend)
        if login.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)
            
        self.setWindowTitle("TECNO SLAVES - Sistema de Ventas (Secure)")
        self.setGeometry(100, 100, 1024, 768)
        
        tabs = QTabWidget()
        self.panel_ventas = PanelVentas(self.backend)
        self.panel_caja = PanelCaja(self.backend)
        
        tabs.addTab(self.panel_ventas, "🛒 Punto de Venta")
        tabs.addTab(self.panel_caja, "💼 Administración / Caja")
        
        tabs.currentChanged.connect(lambda: self.panel_caja.actualizar_estado())
        self.setCentralWidget(tabs)

    def aplicar_tema_oscuro(self):
        estilos = """
            QMainWindow, QWidget { 
                background-color: #2b2b2b; 
                color: #ecf0f1; 
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            QTableWidget {
                background-color: #353535;
                color: #ffffff;
                gridline-color: #555555;
                border: 1px solid #444;
            }
            QTableWidget::item { padding: 5px; }
            QTableWidget::item:selected { background-color: #3498db; color: white; }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 5px;
                border: 1px solid #444;
                font-weight: bold;
            }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { 
                background: #34495e; 
                color: #bdc3c7; 
                padding: 10px 20px; 
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #e67e22; 
                color: white; 
                font-weight: bold; 
            }
            QGroupBox { 
                border: 1px solid #555; 
                margin-top: 20px; 
                border-radius: 5px;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; 
                subcontrol-position: top center; 
                padding: 0 5px;
                color: #f39c12;
                font-weight: bold;
            }
            QComboBox, QLineEdit {
                background-color: #404040;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
            }
            QComboBox::drop-down { border: 0px; }
            QMessageBox { background-color: #2b2b2b; color: white; }
            QMessageBox QLabel { color: white; }
        """
        self.setStyleSheet(estilos)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())