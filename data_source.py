from datetime import date

import pandas as pd


def load_sales_data() -> pd.DataFrame:
    """Central data entry point.

    Replace this function later with an Excel/CSV/API/ERP connection while
    keeping the same column names used by the Streamlit dashboard.
    """
    rows = [
        ["P-1001", date(2026, 1, 8), "2026-01", "Agropecuaria Los Llanos", "Antibioticos", 22, 24.5, 980],
        ["P-1002", date(2026, 1, 14), "2026-01", "Clinica Animal Norte", "Vitaminas", 34, 12.8, 760],
        ["P-1003", date(2026, 1, 21), "2026-01", "Distribuidora Campo Vivo", "Desparasitantes", 46, 9.9, 690],
        ["P-1004", date(2026, 1, 25), "2026-01", "Veterinaria San Rafael", "Suplementos", 18, 31.0, 720],
        ["P-1005", date(2026, 2, 5), "2026-02", "Agropecuaria Los Llanos", "Vacunas", 28, 18.4, 1040],
        ["P-1006", date(2026, 2, 9), "2026-02", "Clinica Animal Norte", "Desinfectantes", 16, 22.0, 820],
        ["P-1007", date(2026, 2, 13), "2026-02", "Distribuidora Campo Vivo", "Vitaminas", 40, 12.8, 740],
        ["P-1008", date(2026, 2, 18), "2026-02", "Veterinaria San Rafael", "Antibioticos", 24, 24.5, 780],
        ["P-1009", date(2026, 2, 26), "2026-02", "Agroservicios El Rodeo", "Desparasitantes", 55, 9.9, 650],
        ["P-1010", date(2026, 3, 4), "2026-03", "Agropecuaria Los Llanos", "Antibioticos", 32, 24.5, 1080],
        ["P-1011", date(2026, 3, 8), "2026-03", "Clinica Animal Norte", "Vacunas", 30, 18.4, 850],
        ["P-1012", date(2026, 3, 12), "2026-03", "Distribuidora Campo Vivo", "Desinfectantes", 21, 22.0, 790],
        ["P-1013", date(2026, 3, 16), "2026-03", "Veterinaria San Rafael", "Suplementos", 26, 31.0, 820],
        ["P-1014", date(2026, 3, 19), "2026-03", "Agroservicios El Rodeo", "Vitaminas", 48, 12.8, 710],
        ["P-1015", date(2026, 3, 24), "2026-03", "Clinica Animal Norte", "Antibioticos", 19, 24.5, 850],
        ["P-1016", date(2026, 4, 2), "2026-04", "Agropecuaria Los Llanos", "Vacunas", 36, 18.4, 1160],
        ["P-1017", date(2026, 4, 5), "2026-04", "Clinica Animal Norte", "Vitaminas", 38, 12.8, 900],
        ["P-1018", date(2026, 4, 9), "2026-04", "Distribuidora Campo Vivo", "Desparasitantes", 62, 9.9, 840],
        ["P-1019", date(2026, 4, 12), "2026-04", "Veterinaria San Rafael", "Antibioticos", 27, 24.5, 880],
        ["P-1020", date(2026, 4, 15), "2026-04", "Agroservicios El Rodeo", "Desinfectantes", 24, 22.0, 760],
        ["P-1021", date(2026, 4, 18), "2026-04", "Clinica Animal Norte", "Suplementos", 17, 31.0, 900],
        ["P-1022", date(2026, 4, 20), "2026-04", "Distribuidora Campo Vivo", "Vacunas", 31, 18.4, 840],
    ]

    data = pd.DataFrame(
        rows,
        columns=[
            "pedido_id",
            "fecha",
            "mes",
            "cliente",
            "producto",
            "unidades",
            "precio_unitario",
            "objetivo_venta",
        ],
    )
    data["venta_total"] = data["unidades"] * data["precio_unitario"]
    return data
