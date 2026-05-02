import altair as alt
import pandas as pd
import streamlit as st

from data_source import load_sales_data


st.set_page_config(
    page_title="DataMovil - KPIs de Clientes",
    page_icon="DM",
    layout="wide",
)


BRAND_BLUE = "#155EEF"
BRAND_GREEN = "#0E9F6E"
BRAND_AMBER = "#D97706"
BRAND_RED = "#DC2626"
INK = "#111827"
MUTED = "#6B7280"
PANEL = "#FFFFFF"
LINE = "#E5E7EB"
DEMO_REFERENCE_DATE = pd.Timestamp("2026-05-02")


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_number(value: float) -> str:
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def get_target_total(data: pd.DataFrame) -> float:
    if data.empty:
        return 0

    target_rows = data.drop_duplicates(["vendedor", "cliente", "mes"])
    return target_rows["objetivo_venta"].sum()


def calculate_kpis(data: pd.DataFrame) -> dict:
    if data.empty:
        return {
            "total_sales": 0,
            "target_percentage": 0,
            "target_gap": 0,
            "total_units": 0,
            "average_ticket": 0,
            "order_count": 0,
        }

    total_sales = data["venta_total"].sum()
    total_units = int(data["unidades"].sum())
    sales_target = get_target_total(data)
    order_count = data["pedido_id"].nunique()
    average_ticket = total_sales / order_count if order_count else 0
    target_percentage = (total_sales / sales_target) * 100 if sales_target else 0

    return {
        "total_sales": total_sales,
        "target_percentage": target_percentage,
        "target_gap": total_sales - sales_target,
        "total_units": total_units,
        "average_ticket": average_ticket,
        "order_count": order_count,
    }


def build_client_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(
            columns=[
                "cliente",
                "venta_total",
                "objetivo_venta",
                "cumplimiento",
                "unidades",
                "pedidos",
                "ticket_promedio",
            ]
        )

    sales = (
        data.groupby("cliente", as_index=False)
        .agg(
            vendedor=("vendedor", lambda values: ", ".join(sorted(values.unique()))),
            venta_total=("venta_total", "sum"),
            unidades=("unidades", "sum"),
            pedidos=("pedido_id", "nunique"),
        )
        .sort_values("venta_total", ascending=False)
    )
    targets = (
        data.drop_duplicates(["cliente", "mes"])
        .groupby("cliente", as_index=False)
        .agg(objetivo_venta=("objetivo_venta", "sum"))
    )
    summary = sales.merge(targets, on="cliente", how="left")
    summary["cumplimiento"] = (
        summary["venta_total"] / summary["objetivo_venta"].replace({0: pd.NA}) * 100
    ).fillna(0)
    summary["ticket_promedio"] = summary["venta_total"] / summary["pedidos"]
    summary["estado"] = summary["cumplimiento"].apply(
        lambda value: "Sobre objetivo" if value >= 100 else "Por debajo"
    )
    return summary


def build_seller_summary(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(
            columns=[
                "vendedor",
                "venta_total",
                "objetivo_venta",
                "cumplimiento",
                "unidades",
                "clientes",
                "pedidos",
                "ticket_promedio",
                "estado",
            ]
        )

    sales = (
        data.groupby("vendedor", as_index=False)
        .agg(
            venta_total=("venta_total", "sum"),
            unidades=("unidades", "sum"),
            clientes=("cliente", "nunique"),
            pedidos=("pedido_id", "nunique"),
        )
        .sort_values("venta_total", ascending=False)
    )
    targets = (
        data.drop_duplicates(["vendedor", "cliente", "mes"])
        .groupby("vendedor", as_index=False)
        .agg(objetivo_venta=("objetivo_venta", "sum"))
    )
    summary = sales.merge(targets, on="vendedor", how="left")
    summary["cumplimiento"] = (
        summary["venta_total"] / summary["objetivo_venta"].replace({0: pd.NA}) * 100
    ).fillna(0)
    summary["ticket_promedio"] = summary["venta_total"] / summary["pedidos"]
    summary["estado"] = summary["cumplimiento"].apply(
        lambda value: "Sobre objetivo" if value >= 100 else "Por debajo"
    )
    return summary


def build_seller_client_opportunities(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(
            columns=[
                "cliente",
                "ultima_compra",
                "dias_sin_compra",
                "venta_total",
                "objetivo_venta",
                "cumplimiento",
                "brecha",
                "unidades",
                "pedidos",
                "accion_sugerida",
            ]
        )

    sales = (
        data.groupby("cliente", as_index=False)
        .agg(
            ultima_compra=("fecha", "max"),
            venta_total=("venta_total", "sum"),
            unidades=("unidades", "sum"),
            pedidos=("pedido_id", "nunique"),
        )
        .sort_values("venta_total", ascending=False)
    )
    targets = (
        data.drop_duplicates(["cliente", "mes"])
        .groupby("cliente", as_index=False)
        .agg(objetivo_venta=("objetivo_venta", "sum"))
    )
    summary = sales.merge(targets, on="cliente", how="left")
    summary["ultima_compra"] = pd.to_datetime(summary["ultima_compra"])
    summary["dias_sin_compra"] = (
        DEMO_REFERENCE_DATE - summary["ultima_compra"]
    ).dt.days.clip(lower=0)
    summary["cumplimiento"] = (
        summary["venta_total"] / summary["objetivo_venta"].replace({0: pd.NA}) * 100
    ).fillna(0)
    summary["brecha"] = summary["venta_total"] - summary["objetivo_venta"]

    def suggest_action(row):
        if row["cumplimiento"] < 70:
            return "Priorizar visita comercial"
        if row["dias_sin_compra"] >= 25:
            return "Reactivar recompra"
        if row["brecha"] < 0:
            return "Impulsar objetivo pendiente"
        return "Mantener seguimiento"

    summary["accion_sugerida"] = summary.apply(suggest_action, axis=1)
    return summary.sort_values(["cumplimiento", "dias_sin_compra"], ascending=[True, False])


st.markdown(
    f"""
    <style>
    .stApp {{
        background: #F8FAFC;
        color: {INK};
    }}
    [data-testid="stMetric"] {{
        background: {PANEL};
        border: 1px solid {LINE};
        border-radius: 8px;
        padding: 18px 18px 14px;
        box-shadow: 0 8px 22px rgba(17, 24, 39, 0.05);
    }}
    [data-testid="stMetricLabel"] p {{
        color: {MUTED};
        font-size: 0.9rem;
    }}
    [data-testid="stMetricValue"] {{
        color: {INK};
        font-weight: 750;
    }}
    .hero {{
        background: linear-gradient(135deg, #0F172A 0%, #164E63 52%, #047857 100%);
        color: white;
        border-radius: 8px;
        padding: 26px 30px;
        margin-bottom: 22px;
        border: 1px solid rgba(255,255,255,0.16);
    }}
    .hero h1 {{
        margin: 0 0 8px 0;
        font-size: 2.15rem;
        letter-spacing: 0;
    }}
    .hero p {{
        margin: 0;
        max-width: 920px;
        color: rgba(255,255,255,0.86);
        font-size: 1.02rem;
    }}
.section-title {{
        font-size: 1.08rem;
        font-weight: 750;
        margin: 10px 0 8px;
    }}
    .seller-note {{
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 8px;
        color: #064E3B;
        padding: 14px 16px;
        margin: 12px 0 18px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


sales_data = load_sales_data()

with st.sidebar:
    st.header("Panel de control")
    selected_module = st.radio(
        "Modulo",
        ["Directivos / Gerentes", "Vendedores"],
    )
    selected_seller = "Todos los vendedores"
    if selected_module == "Vendedores":
        selected_seller = st.selectbox(
            "Vendedor",
            sorted(sales_data["vendedor"].unique().tolist()),
        )
    else:
        selected_seller = st.selectbox(
            "Equipo comercial",
            ["Todos los vendedores"] + sorted(sales_data["vendedor"].unique().tolist()),
        )
    selected_client = st.selectbox(
        "Cliente analizado",
        ["Todos los clientes"] + sorted(sales_data["cliente"].unique().tolist()),
    )
    selected_months = st.multiselect(
        "Periodo",
        sorted(sales_data["mes"].unique().tolist()),
        default=sorted(sales_data["mes"].unique().tolist()),
    )
    selected_products = st.multiselect(
        "Linea de producto",
        sorted(sales_data["producto"].unique().tolist()),
        default=sorted(sales_data["producto"].unique().tolist()),
    )

filtered_data = sales_data.copy()

if selected_seller != "Todos los vendedores":
    filtered_data = filtered_data[filtered_data["vendedor"] == selected_seller]

if selected_client != "Todos los clientes":
    filtered_data = filtered_data[filtered_data["cliente"] == selected_client]

if selected_months:
    filtered_data = filtered_data[filtered_data["mes"].isin(selected_months)]

if selected_products:
    filtered_data = filtered_data[filtered_data["producto"].isin(selected_products)]

kpis = calculate_kpis(filtered_data)
client_summary = build_client_summary(filtered_data)
seller_summary = build_seller_summary(filtered_data)
seller_opportunities = build_seller_client_opportunities(filtered_data)
gap_label = "sobre objetivo" if kpis["target_gap"] >= 0 else "por debajo del objetivo"

hero_copy = (
    "Vista gerencial para monitorear ventas, vendedores, clientes, cumplimiento de objetivo y oportunidades comerciales."
    if selected_module == "Directivos / Gerentes"
    else f"Vista del vendedor {selected_seller} para seguir su desempeno, clientes atendidos y avance contra objetivo."
)

st.markdown(
    f"""
    <div class="hero">
        <h1>DataMovil</h1>
        <p>{hero_copy}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Ventas facturadas",
    format_currency(kpis["total_sales"]),
    f"{format_currency(abs(kpis['target_gap']))} {gap_label}",
)
col2.metric(
    "Cumplimiento de objetivo",
    format_percent(kpis["target_percentage"]),
    "Meta comercial filtrada",
)
col3.metric(
    "Unidades despachadas",
    format_number(kpis["total_units"]),
    f"{kpis['order_count']} pedidos",
)
col4.metric(
    "Ticket promedio por pedido",
    format_currency(kpis["average_ticket"]),
    "Ventas / pedidos",
)

st.markdown('<div class="section-title">Lectura comercial</div>', unsafe_allow_html=True)
insight_left, insight_right = st.columns([1.15, 1])

with insight_left:
    target_color = BRAND_GREEN if kpis["target_percentage"] >= 100 else BRAND_AMBER
    progress_data = pd.DataFrame(
        {
            "KPI": ["Cumplimiento"],
            "Porcentaje": [min(kpis["target_percentage"], 130)],
            "Meta": [100],
        }
    )
    progress_chart = (
        alt.Chart(progress_data)
        .mark_bar(cornerRadius=5, height=34, color=target_color)
        .encode(
            x=alt.X(
                "Porcentaje:Q",
                scale=alt.Scale(domain=[0, 130]),
                axis=alt.Axis(title=None, format=".0f", labelExpr="datum.value + '%'"),
            ),
            y=alt.Y("KPI:N", axis=None),
            tooltip=[
                alt.Tooltip("Porcentaje:Q", title="Cumplimiento", format=".1f"),
            ],
        )
        .properties(height=80)
    )
    rule = (
        alt.Chart(progress_data)
        .mark_rule(color=BRAND_RED, strokeDash=[6, 4], size=2)
        .encode(x="Meta:Q")
    )
    st.altair_chart(progress_chart + rule, width="stretch")

with insight_right:
    if client_summary.empty:
        st.info("No hay datos para los filtros seleccionados.")
    elif selected_module == "Directivos / Gerentes" and not seller_summary.empty:
        top_seller = seller_summary.iloc[0]
        st.write(
            f"El vendedor con mayor venta es **{top_seller['vendedor']}**, con "
            f"**{format_currency(top_seller['venta_total'])}** facturados, "
            f"**{format_percent(top_seller['cumplimiento'])}** de cumplimiento "
            f"y **{int(top_seller['clientes'])}** clientes atendidos."
        )
    else:
        top_client = client_summary.iloc[0]
        st.write(
            f"El cliente con mayor venta es **{top_client['cliente']}**, con "
            f"**{format_currency(top_client['venta_total'])}** facturados y "
            f"**{format_percent(top_client['cumplimiento'])}** de cumplimiento."
        )

if selected_module == "Directivos / Gerentes":
    st.markdown(
        '<div class="section-title">Ranking de vendedores</div>',
        unsafe_allow_html=True,
    )
    seller_chart = (
        alt.Chart(seller_summary)
        .mark_bar(cornerRadiusEnd=5)
        .encode(
            x=alt.X("venta_total:Q", title="Ventas facturadas"),
            y=alt.Y("vendedor:N", sort="-x", title=None),
            color=alt.Color(
                "estado:N",
                scale=alt.Scale(
                    domain=["Sobre objetivo", "Por debajo"],
                    range=[BRAND_GREEN, BRAND_AMBER],
                ),
                legend=alt.Legend(title="Estado"),
            ),
            tooltip=[
                alt.Tooltip("vendedor:N", title="Vendedor"),
                alt.Tooltip("venta_total:Q", title="Ventas", format="$,.2f"),
                alt.Tooltip("objetivo_venta:Q", title="Objetivo", format="$,.2f"),
                alt.Tooltip("cumplimiento:Q", title="Cumplimiento", format=".1f"),
                alt.Tooltip("clientes:Q", title="Clientes", format=","),
                alt.Tooltip("pedidos:Q", title="Pedidos", format=","),
            ],
        )
        .properties(height=230)
    )
    st.altair_chart(seller_chart, width="stretch")

if selected_module == "Vendedores":
    st.markdown(
        '<div class="section-title">Mi cartera comercial</div>',
        unsafe_allow_html=True,
    )
    if seller_opportunities.empty:
        st.info("No hay clientes para los filtros seleccionados.")
    else:
        urgent_clients = seller_opportunities[
            seller_opportunities["accion_sugerida"].isin(
                ["Priorizar visita comercial", "Reactivar recompra"]
            )
        ]
        urgent_count = len(urgent_clients)
        best_client = seller_opportunities.sort_values(
            "venta_total", ascending=False
        ).iloc[0]
        st.markdown(
            f"""
            <div class="seller-note">
                <strong>{selected_seller}</strong>: tienes <strong>{len(seller_opportunities)}</strong> clientes en cartera.
                El cliente con mayor venta es <strong>{best_client['cliente']}</strong>.
                Hay <strong>{urgent_count}</strong> clientes que requieren atencion prioritaria.
            </div>
            """,
            unsafe_allow_html=True,
        )

        opportunity_chart = (
            alt.Chart(seller_opportunities)
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                x=alt.X("brecha:Q", title="Brecha vs objetivo"),
                y=alt.Y("cliente:N", sort="x", title=None),
                color=alt.condition(
                    alt.datum.brecha >= 0,
                    alt.value(BRAND_GREEN),
                    alt.value(BRAND_RED),
                ),
                tooltip=[
                    alt.Tooltip("cliente:N", title="Cliente"),
                    alt.Tooltip("venta_total:Q", title="Ventas", format="$,.2f"),
                    alt.Tooltip("objetivo_venta:Q", title="Objetivo", format="$,.2f"),
                    alt.Tooltip("brecha:Q", title="Brecha", format="$,.2f"),
                    alt.Tooltip("cumplimiento:Q", title="Cumplimiento", format=".1f"),
                    alt.Tooltip("accion_sugerida:N", title="Accion"),
                ],
            )
            .properties(height=260)
        )
        st.altair_chart(opportunity_chart, width="stretch")

        seller_display = seller_opportunities.copy()
        seller_display["Ultima compra"] = seller_display["ultima_compra"].dt.strftime(
            "%Y-%m-%d"
        )
        seller_display["Ventas"] = seller_display["venta_total"].map(format_currency)
        seller_display["Objetivo"] = seller_display["objetivo_venta"].map(
            format_currency
        )
        seller_display["Brecha"] = seller_display["brecha"].map(format_currency)
        seller_display["Cumplimiento"] = seller_display["cumplimiento"].map(
            format_percent
        )
        seller_display = seller_display[
            [
                "cliente",
                "Ventas",
                "Objetivo",
                "Brecha",
                "Cumplimiento",
                "dias_sin_compra",
                "Ultima compra",
                "accion_sugerida",
            ]
        ].rename(
            columns={
                "cliente": "Cliente",
                "dias_sin_compra": "Dias sin compra",
                "accion_sugerida": "Accion sugerida",
            }
        )
        st.dataframe(seller_display, width="stretch", hide_index=True)

chart_left, chart_right = st.columns([1.35, 1])

with chart_left:
    st.markdown(
        '<div class="section-title">Ranking de ventas por cliente</div>',
        unsafe_allow_html=True,
    )
    client_chart = (
        alt.Chart(client_summary)
        .mark_bar(cornerRadiusEnd=5)
        .encode(
            x=alt.X("venta_total:Q", title="Ventas facturadas"),
            y=alt.Y("cliente:N", sort="-x", title=None),
            color=alt.Color(
                "estado:N",
                scale=alt.Scale(
                    domain=["Sobre objetivo", "Por debajo"],
                    range=[BRAND_GREEN, BRAND_AMBER],
                ),
                legend=alt.Legend(title="Estado"),
            ),
            tooltip=[
                alt.Tooltip("cliente:N", title="Cliente"),
                alt.Tooltip("venta_total:Q", title="Ventas", format="$,.2f"),
                alt.Tooltip("objetivo_venta:Q", title="Objetivo", format="$,.2f"),
                alt.Tooltip("cumplimiento:Q", title="Cumplimiento", format=".1f"),
                alt.Tooltip("unidades:Q", title="Unidades", format=","),
            ],
        )
        .properties(height=330)
    )
    st.altair_chart(client_chart, width="stretch")

with chart_right:
    st.markdown(
        '<div class="section-title">Composicion por linea</div>',
        unsafe_allow_html=True,
    )
    product_summary = (
        filtered_data.groupby("producto", as_index=False)["venta_total"]
        .sum()
        .sort_values("venta_total", ascending=False)
    )
    product_chart = (
        alt.Chart(product_summary)
        .mark_arc(innerRadius=62, outerRadius=122)
        .encode(
            theta=alt.Theta("venta_total:Q"),
            color=alt.Color(
                "producto:N",
                scale=alt.Scale(
                    range=[BRAND_BLUE, BRAND_GREEN, BRAND_AMBER, "#7C3AED", "#0891B2"]
                ),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("producto:N", title="Linea"),
                alt.Tooltip("venta_total:Q", title="Ventas", format="$,.2f"),
            ],
        )
        .properties(height=330)
    )
    st.altair_chart(product_chart, width="stretch")

trend_summary = (
    filtered_data.groupby("mes", as_index=False)
    .agg(venta_total=("venta_total", "sum"), unidades=("unidades", "sum"))
    .sort_values("mes")
)

st.markdown(
    '<div class="section-title">Evolucion mensual de ventas</div>',
    unsafe_allow_html=True,
)
trend_chart = (
    alt.Chart(trend_summary)
    .mark_line(point=alt.OverlayMarkDef(size=80), color=BRAND_BLUE, strokeWidth=3)
    .encode(
        x=alt.X("mes:N", title="Mes"),
        y=alt.Y("venta_total:Q", title="Ventas facturadas"),
        tooltip=[
            alt.Tooltip("mes:N", title="Mes"),
            alt.Tooltip("venta_total:Q", title="Ventas", format="$,.2f"),
            alt.Tooltip("unidades:Q", title="Unidades", format=","),
        ],
    )
    .properties(height=260)
)
st.altair_chart(trend_chart, width="stretch")

st.markdown(
    '<div class="section-title">Clientes priorizados</div>',
    unsafe_allow_html=True,
)
display_summary = client_summary.copy()
display_summary["Ventas"] = display_summary["venta_total"].map(format_currency)
display_summary["Objetivo"] = display_summary["objetivo_venta"].map(format_currency)
display_summary["Cumplimiento"] = display_summary["cumplimiento"].map(format_percent)
display_summary["Ticket promedio"] = display_summary["ticket_promedio"].map(
    format_currency
)
display_summary = display_summary[
    [
        "cliente",
        "vendedor",
        "Ventas",
        "Objetivo",
        "Cumplimiento",
        "unidades",
        "pedidos",
        "Ticket promedio",
        "estado",
    ]
].rename(
    columns={
        "cliente": "Cliente",
        "vendedor": "Vendedor",
        "unidades": "Unidades",
        "pedidos": "Pedidos",
        "estado": "Estado",
    }
)
st.dataframe(display_summary, width="stretch", hide_index=True)

with st.expander("Ver pedidos simulados"):
    detail = filtered_data.rename(
        columns={
            "pedido_id": "Pedido",
            "fecha": "Fecha",
            "mes": "Mes",
            "cliente": "Cliente",
            "vendedor": "Vendedor",
            "producto": "Linea",
            "unidades": "Unidades",
            "precio_unitario": "Precio unitario",
            "objetivo_venta": "Objetivo",
            "venta_total": "Venta total",
        }
    )
    st.dataframe(detail, width="stretch", hide_index=True)
