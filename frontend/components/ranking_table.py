"""Tabela de ranking por casa."""
from dash import dash_table, html


def build_ranking_table(establishments: list[dict]) -> html.Div:
    def fmt_brl(v) -> str:
        if v is None:
            return "—"
        return f"R$ {float(v):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_pct(v) -> str:
        return f"{v:.1f}%" if v is not None else "—"

    def fmt_roas(v) -> str:
        return f"{v:.2f}x" if v is not None else "—"

    rows = []
    for e in sorted(establishments, key=lambda x: x.get("total_spend", 0), reverse=True):
        roas = None
        if e.get("fat_salao") and e.get("total_spend") and e["total_spend"] > 0:
            roas = round(e["fat_salao"] / e["total_spend"], 2)
        rows.append({
            "Casa": f"{e.get('sigla', '')} — {e.get('establishment_name', '')}",
            "Marca": e.get("brand", ""),
            "Invest. Ads": fmt_brl(e.get("total_spend")),
            "Impressões": f"{e.get('total_impressions', 0):,}".replace(",", "."),
            "Cliques": f"{e.get('total_clicks', 0):,}".replace(",", "."),
            "CTR": fmt_pct(e.get("ctr")),
            "CPC": f"R$ {e['cpc']:.2f}".replace(".", ",") if e.get("cpc") else "—",
            "Reservas 🔒": "—",
            "Fat. Salão": fmt_brl(e.get("fat_salao")),
            "CMV%": fmt_pct(e.get("cmv_pct")),
            "ROAS": fmt_roas(roas),
        })

    return html.Div(
        dash_table.DataTable(
            data=rows,
            columns=[{"name": col, "id": col} for col in (rows[0].keys() if rows else [])],
            style_table={"overflowX": "auto"},
            style_cell={
                "backgroundColor": "#0D0D1A",
                "color": "#DDD",
                "border": "1px solid #1F1F3A",
                "padding": "8px 12px",
                "fontSize": "12px",
                "fontFamily": "Inter, sans-serif",
                "textAlign": "center",
            },
            style_header={
                "backgroundColor": "#1A1A2E",
                "color": "#aaa",
                "fontWeight": "600",
                "border": "1px solid #2A2A4A",
                "textAlign": "center",
                "fontSize": "11px",
                "textTransform": "uppercase",
            },
            style_data_conditional=[
                {"if": {"column_id": "Reservas 🔒"}, "color": "#555", "fontStyle": "italic"},
            ],
            page_size=16,
            sort_action="native",
        ),
        style={"marginTop": "8px"},
    )
