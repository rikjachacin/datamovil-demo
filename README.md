# DataMovil

Demo inicial en Streamlit para KPIs comerciales de posibles clientes, pensada
como vitrina de Business Intelligence para ventas.

## KPIs incluidos

- Total ventas
- Porcentaje obtenido vs objetivo
- Unidades vendidas
- Ticket promedio

## Vistas incluidas

- Tarjetas ejecutivas de KPI
- Cumplimiento de objetivo
- Ranking de ventas por cliente
- Composicion de ventas por linea de producto
- Evolucion mensual de ventas
- Tabla de clientes priorizados
- Detalle de pedidos simulados
- Modulo Directivos/Gerentes
- Modulo Vendedores
- Ranking y filtros por vendedor
- Resumen ejecutivo para gerencia
- Cumplimiento por vendedor
- Clientes criticos bajo objetivo
- Cartera comercial por vendedor
- Oportunidades sugeridas por cliente
- Brecha contra objetivo por cliente

## Ejecutar

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Cambiar datos simulados por datos reales

La entrada de datos está centralizada en `data_source.py`, dentro de la función
`load_sales_data()`.

Para conectar datos reales, reemplaza esa función por una lectura desde Excel,
CSV, base de datos, API o ERP, manteniendo estas columnas:

- `pedido_id`
- `fecha`
- `mes`
- `cliente`
- `vendedor`
- `producto`
- `unidades`
- `precio_unitario`
- `objetivo_venta`
- `venta_total`
