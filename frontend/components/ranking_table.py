"""Tabela de ranking por casa."""
from dash import dash_table, html


def build_ranking_table(establishments: list[dict], attribution: list[dict] | None = None) -> html.Div:
    def fmt_brl(v) -> str:
        if v is None:
            return "—"
        return f"R$ {float(v):,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_pct(v) -> str:
        return f"{v:.1f}%" if v is not None else "—"

    def fmt_roas(v) -> str:
        return f"{v:.2f}x" if v is not None else "—"

    # Mapear attribution por establishment_id para lookup rápido
    attr_by_id: dict[int, dict] = {}
    if attribution:
        for a in attribution:
            attr_by_id[a.get("establishment_id")] = a

    rows = []
    for e in sorted(establishments, key=lambda x: x.get("total_spend", 0), reverse=True):
        eid = e.get("establishment_id") or e.get("id")
        attr = attr_by_id.get(eid, {})

        spend = e.get("total_spend") or 0
        total_reservations = attr.get("total_reservations", 0)
        total_sessions = attr.get("total_sessions", 0)
        fat_total = attr.get("fat_total") or e.get("fat_total")

        conv_rate = None
        if total_sessions > 0:
            conv_rate = round(total_reservations / total_sessions * 100, 1)

        cpa = None
        if spend > 0 and total_reservations > 0:
            cpa = round(spend / total_reservations, 2)

        roas = None
        if fat_total and spend > 0:
            roas = round(float(fat_total) / spend, 2)

        rows.append({
            "Casa": f"{e.get('sigla', '')} — {e.get('establishment_name', '')}",
            "Marca": e.get("brand", ""),
            "Invest. Ads": fmt_brl(spend if spend else None),
            "Impressões": f"{e.get('total_impressions', 0):,}".replace(",", "."),
            "Cliques": f"{e.get('total_clicks', 0):,}".replace(",", "."),
            "CTR": fmt_pct(e.get("ctr")),
            "Sessões": f"{total_sessions:,}".replace(",", ".") if total_sessions else "—",
            "Reservas": f"{total_reservations:,}".replace(",", ".") if total_reservations else "—",
            "Conv.%": fmt_pct(conv_rate),
            "CPA": fmt_brl(cpa),
            "Fat. Total": fmt_brl(fat_total),
            "ROAS": fmt_roas(roas),
        })

    if not rows:
        return html.Div("Sem dados", style={"color": "#555", "padding": "20px", "textAlign": "center"})

    return html.Div(
        dash_table.DataTable(
            data=rows,
            columns=[{"name": col, "id": col} for col in rows[0].keys()],
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
                {"if": {"column_id": "ROAS"}, "color": "#FFD54F"},
                {"if": {"column_id": "Reservas"}, "color": "#66BB6A"},
                {"if": {"column_id": "Conv.%"}, "color": "#A5D6A7"},
            ],
            page_size=16,
            sort_action="native",
        ),
        style={"marginTop": "8px"},
    )
