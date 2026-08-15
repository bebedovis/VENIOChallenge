## Grano

Cada fila representa una transacción a nivel:
- Día
- Cliente
- Producto
- Transacción individual (ticket)
- Promoción dentro de la que se vendió ese producto

## Diccionario de datos

| Columna | Descripción |
|---|---|
| `year`| Año calendario de la transacción. |
| `month` | Mes calendario de la transacción. |
| `date` | Fecha calendario de la transacción (grano diario). |
| `warehouse` | Bodega que despachó el pedido. |
| `route`| Ruta que hizo la venta. |
| `product_code` | Identificador numérico del SKU. |
| `product_name` | Descripción comercial del SKU. |
| `client_code` | Identificador del cliente. |
| `client_name` | Nombre del cliente (anonimizado). |
| `category` | Categoría de producto. |
| `subcategory` | Subcategoría de producto. |
| `brand` | Marca del SKU (anonimizada). |
| `basket`| Canasta comercial. |
| `ticket_code` | Identificador de la transacción única. |
| `sell_in_quantity` | Cantidad de unidades vendidas. |
| `sell_in_amount` | Monto neto cobrado por las unidades vendidas (precio efectivo × cantidad). |
| `id_combo` | Identificador del combo/promoción aplicado, vacío si la venta fue orgánica (sin promoción). |
| `combo` | Nombre del combo aplicado, vacío si la venta fue orgánica. |
| `bruto` | Monto que se hubiera cobrado al precio de lista, sin descuento (precio de lista × cantidad). |
| `discount` | Profundidad de descuento aplicada sobre el precio de lista, como fracción (0 si fue venta orgánica). |
| `product_cost` | Costo total de adquisición de las unidades vendidas en la transacción (costo unitario × cantidad). |
| `product_margin` | Margen de ganancia fijo por SKU (markup sobre costo). Constante para cada producto durante todo el periodo. |

## Notas sobre calidad de datos (intencional)

- `discount`, `bruto` y `product_cost` tienen nulos en una fracción de las filas — trátalos como los tratarías en un extracto real.
- Hay transacciones con `sell_in_quantity = 0` (tickets cancelados) y transacciones con `sell_in_amount = 0` pero cantidad positiva (producto de regalo/muestra).
- Una fila tiene metadata de producto incompleta (categoría/subcategoría/marca/basket vacíos).
