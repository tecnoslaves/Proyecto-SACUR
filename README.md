# 🛒 Proyecto-SACUR: Sistema de Control de Ventas

> Un sistema de registro de ventas diarias desarrollado en Python, diseñado para pequeños comercios o puntos de venta. Permite registrar ventas, gestionar cierres de caja, generar tickets, consultar historial de ventas por fecha y generación de copias de seguridad de la base de datos.

## Vista Previa de la Interfaz

### Punto de Venta Integrado

![Login](/img/login.png)

![Panel de Ventas](/img/confirmacion_venta.png)

### Control de Caja y Seguridad
![Panel de Caja](/img/reporte_ventas_2E.png)

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
