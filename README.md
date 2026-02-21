# 🛒 Proyecto-SACUR: Sistema de Control de Ventas

> Un sistema de registro de ventas diarias desarrollado en Python, diseñado para pequeños comercios o puntos de venta. Permite registrar ventas, gestionar cierres de caja, generar tickets, consultar historial de ventas por fecha y generación de copias de seguridad de la base de datos.

## Vista Previa de la Interfaz

### Punto de Venta Integrado

![Login](<img width="534" height="581" alt="login" src="https://github.com/user-attachments/assets/495df975-5bc0-4375-a5c1-9c7a320de180" />
)

![Panel de Ventas](<img width="1277" height="643" alt="confirmacion_venta" src="https://github.com/user-attachments/assets/a1175d42-0fd9-41f8-9628-0f32607e5c3d" />
)

### Control de Caja y Seguridad
![Panel de Caja](<img width="1279" height="672" alt="reporte_ventas_2E" src="https://github.com/user-attachments/assets/6ed2f27a-a0fa-4f9d-91d9-2a9bb53302ef" />
)

---

## 📌 Funcionalidades principales

✅ **Registro de ventas diarias**  
   - Captura de productos, precios, cantidades y totales por venta.

✅ **Base de datos local**  
   - Almacena todas las ventas en una base de datos SQLite (Cifrada).

✅ **Cierre de caja**  
   - Muestra el resumen de ventas del día: total de ingresos, cantidad de transacciones, clasificacion efectivo de transferencias, clasificación de articulos vendidos separados de costos del delivery.
   
✅ **Impresión de tickets**  
   - Genera y guarda tickets en formato texto para cada venta confirmada.

✅ **Consulta por periodo**  
   - Permite ver ventas de una fecha específica o rango de fechas.
   - Exporta resumen de ventas anteriores.

✅ **Interfaz interactiva**  
   - Interfaz gráfica completa en modo oscuro.

---
🛠️ Tecnologías utilizadas

* **Lenguaje:** Python 3

* **Base de datos (seguridad avanzada):** SQLite cifrada con SQLCipher y contraseñas protegidas con `pbkdf2_hmac`.

* **Interfaz:** Interactiva 
* **GUI Moderna:** Interfaz gráfica completa en modo oscuro usando PyQt6.

* **Impresión Nativa:** Conexión directa con impresoras en Windows 11.

📄 Licencia

Este proyecto está bajo la licencia MIT.

Consulta el archivo LICENSE para más detalles.

🙌 Autor

@tecnoslaves

Proyecto-SACUR – Control de ventas diarias
