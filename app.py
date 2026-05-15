from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.data_loader import load_formula_catalog, load_materials, paper_options
from core.exporter import make_quote_dataframe
from core.formulas import calculate_edge_protector, calculate_tube
from core.models import EdgeProtectorInput, TubeInput


st.set_page_config(
    page_title="IP Poland Pricing Engine",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 20%, rgba(0,229,255,.18), transparent 28%),
                radial-gradient(circle at 90% 15%, rgba(168,85,247,.20), transparent 28%),
                radial-gradient(circle at 50% 90%, rgba(34,197,94,.12), transparent 30%),
                linear-gradient(135deg, #050816 0%, #0B1020 45%, #111827 100%);
        }

        .hero {
            padding: 34px;
            border: 1px solid rgba(148,163,184,.22);
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(15,23,42,.94), rgba(30,41,59,.66));
            box-shadow: 0 24px 80px rgba(0,0,0,.38);
            margin-bottom: 24px;
        }

        .hero h1 {
            font-size: 46px;
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: -1.4px;
            margin: 0;
            background: linear-gradient(90deg, #FFFFFF, #67E8F9, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            color: #CBD5E1;
            font-size: 17px;
            max-width: 1050px;
        }

        .badge {
            display: inline-block;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(0,229,255,.12);
            color: #67E8F9;
            border: 1px solid rgba(103,232,249,.25);
            font-weight: 700;
            margin-right: 8px;
            margin-bottom: 12px;
        }

        .glass-card {
            padding: 20px;
            border-radius: 22px;
            background: rgba(15,23,42,.74);
            border: 1px solid rgba(148,163,184,.18);
            box-shadow: 0 14px 50px rgba(0,0,0,.25);
        }

        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, rgba(15,23,42,.88), rgba(30,41,59,.62));
            border: 1px solid rgba(148,163,184,.18);
            padding: 18px;
            border-radius: 20px;
            box-shadow: 0 14px 40px rgba(0,0,0,.25);
        }

        div[data-testid="metric-container"] label {
            color: #94A3B8 !important;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #F8FAFC;
            font-weight: 900;
        }

        .warning-box {
            padding: 16px 18px;
            border-radius: 18px;
            background: rgba(251,191,36,.10);
            border: 1px solid rgba(251,191,36,.32);
            color: #FDE68A;
        }

        .footer {
            color: #94A3B8;
            font-size: 13px;
            padding-top: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <span class="badge">STREAMLIT PRICING ENGINE</span>
            <span class="badge">IP POLAND 2025</span>
            <h1>Industrial Packaging Calculator</h1>
            <p>
                Professional pricing cockpit for Edge Protectors, Tubes/Cores,
                palletization, strength estimation, margin simulation, material data,
                and Excel-to-Python formula migration.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def money(value: float) -> str:
    return f"{value:,.4f} PLN"


def number(value: float, digits: int = 3) -> str:
    return f"{value:,.{digits}f}"


def download_quote(product: str, inputs: dict, result: dict) -> None:
    quote_df = make_quote_dataframe(
        product=product,
        inputs=inputs,
        result=result,
    )

    csv = quote_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download quote CSV",
        data=csv,
        file_name=f"{product.lower().replace(' ', '_')}_quote.csv",
        mime="text/csv",
        use_container_width=True,
    )


def result_chart(result: dict, product: str) -> None:
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=["Price / r.m.", "Price / piece", "Price / kg"],
            y=[
                result.get("price_per_rm_pln", 0),
                result.get("price_per_piece_pln", 0),
                result.get("price_per_kg_pln", 0),
            ],
            marker=dict(
                color=[
                    "#00E5FF",
                    "#A78BFA",
                    "#22C55E",
                ]
            ),
            text=[
                f"{result.get('price_per_rm_pln', 0):.4f}",
                f"{result.get('price_per_piece_pln', 0):.4f}",
                f"{result.get('price_per_kg_pln', 0):.4f}",
            ],
            textposition="outside",
        )
    )

    fig.update_layout(
        title=f"{product} price composition",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E5E7EB"),
        height=360,
        margin=dict(l=20, r=20, t=60, b=30),
    )

    st.plotly_chart(fig, use_container_width=True)


def dashboard_page() -> None:
    st.subheader("🚀 Command Center")

    catalog = load_formula_catalog()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Formula cells loaded", f"{catalog.get('total_formulas', 0):,}")
    c2.metric("Product modules", "4+")
    c3.metric("Current MVP", "Edge + Tubes")
    c4.metric("Currency", "PLN")

    st.markdown("### Migration status")

    status = pd.DataFrame(
        [
            {
                "Module": "Edge Protectors",
                "Status": "MVP formula engine ready",
                "Priority": "High",
            },
            {
                "Module": "Tubes / Cores",
                "Status": "MVP formula engine ready",
                "Priority": "High",
            },
            {
                "Module": "Paper database",
                "Status": "JSON database ready",
                "Priority": "High",
            },
            {
                "Module": "Cardboard Pallets",
                "Status": "Next implementation",
                "Priority": "Medium",
            },
            {
                "Module": "HoneyComb",
                "Status": "Formula audit ready; full engine pending",
                "Priority": "Medium",
            },
        ]
    )

    st.dataframe(status, use_container_width=True, hide_index=True)


def edge_page() -> None:
    st.subheader("🧱 Edge Protector Calculator")

    left, right = st.columns([0.38, 0.62], gap="large")

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Product inputs")

        papers = paper_options()

        product_type = st.selectbox(
            "Type",
            papers,
            index=papers.index("IPP-30") if "IPP-30" in papers else 0,
        )

        outer_cover = st.selectbox(
            "Outer cover",
            papers,
            index=papers.index("Testliner Grey") if "Testliner Grey" in papers else 0,
        )

        c1, c2 = st.columns(2)

        side_1 = c1.number_input(
            "Side 1 / x1, mm",
            min_value=1.0,
            value=25.0,
            step=1.0,
        )

        side_2 = c2.number_input(
            "Side 2 / x2, mm",
            min_value=1.0,
            value=150.0,
            step=1.0,
        )

        c3, c4 = st.columns(2)

        thickness = c3.number_input(
            "Wall thickness, mm",
            min_value=0.1,
            value=1.8,
            step=0.1,
        )

        length = c4.number_input(
            "Length, mm",
            min_value=1.0,
            value=500.0,
            step=10.0,
        )

        c5, c6 = st.columns(2)

        qty = c5.number_input(
            "Quantity, pcs",
            min_value=1,
            value=33000,
            step=100,
        )

        qty_per_pallet = c6.number_input(
            "Qty per pallet",
            min_value=1,
            value=1000,
            step=10,
        )

        st.markdown("#### Commercial")

        c7, c8 = st.columns(2)

        transport = c7.number_input(
            "Transport, PLN",
            min_value=0.0,
            value=0.0,
            step=50.0,
        )

        margin = c8.number_input(
            "Margin, %",
            min_value=-100.0,
            value=0.0,
            step=1.0,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    inp = EdgeProtectorInput(
        side_1_mm=side_1,
        side_2_mm=side_2,
        thickness_mm=thickness,
        length_mm=length,
        product_type=product_type,
        outer_cover=outer_cover,
        quantity_pcs=int(qty),
        quantity_per_pallet=int(qty_per_pallet),
        transport_cost_pln=transport,
        margin_percent=margin,
    )

    result = calculate_edge_protector(inp)
    result_dict = result.to_dict()

    with right:
        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Price / r.m.", money(result.price_per_rm_pln))
        m2.metric("Price / piece", money(result.price_per_piece_pln))
        m3.metric("Weight kg/r.m.", number(result.weight_kg_per_rm, 6))
        m4.metric("Bending force", f"{result.three_point_bending_n:,.1f} N")

        result_chart(result_dict, "Edge Protector")

        a, b = st.columns(2)

        with a:
            st.markdown("#### Logistics")

            logistics = pd.DataFrame(
                [
                    {"Metric": "Total running meters", "Value": result.total_running_m},
                    {"Metric": "Net weight kg", "Value": result.net_weight_kg},
                    {"Metric": "Pallets", "Value": result.pallets},
                    {"Metric": "Pallet weight kg", "Value": result.pallet_weight_kg},
                ]
            )

            st.dataframe(logistics, use_container_width=True, hide_index=True)

        with b:
            st.markdown("#### Production order")

            st.json(
                {
                    "product": "Kątownik / Edge Protector",
                    "dimensions": f"{side_1} x {side_2} x {thickness} / {length} mm",
                    "type": product_type,
                    "outer_cover": outer_cover,
                    "quantity_pcs": int(qty),
                }
            )

        download_quote(
            product="Edge Protector",
            inputs=asdict(inp),
            result=result_dict,
        )


def tube_page() -> None:
    st.subheader("🌀 Tubes / Cores Calculator")

    left, right = st.columns([0.38, 0.62], gap="large")

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("#### Product inputs")

        papers = paper_options()

        product_type = st.selectbox(
            "Type",
            papers,
            index=papers.index("IPP-30") if "IPP-30" in papers else 0,
            key="tube_type",
        )

        inner_cover = st.selectbox(
            "Inner cover",
            ["nie"] + papers,
            index=0,
        )

        outer_cover = st.selectbox(
            "Outer cover",
            papers,
            index=papers.index("Testliner Grey") if "Testliner Grey" in papers else 0,
            key="tube_outer",
        )

        c1, c2 = st.columns(2)

        diameter = c1.number_input(
            "Diameter, mm",
            min_value=1.0,
            value=76.8,
            step=0.1,
        )

        thickness = c2.number_input(
            "Wall thickness, mm",
            min_value=0.1,
            value=5.8,
            step=0.1,
            key="tube_thickness",
        )

        c3, c4 = st.columns(2)

        length = c3.number_input(
            "Length, mm",
            min_value=1.0,
            value=525.0,
            step=5.0,
            key="tube_length",
        )

        qty_per_pallet = c4.number_input(
            "Qty per pallet",
            min_value=1,
            value=37,
            step=1,
            key="tube_qty_per_pallet",
        )

        c5, c6 = st.columns(2)

        qty = c5.number_input(
            "Quantity, pcs",
            min_value=1,
            value=27324,
            step=100,
            key="tube_qty",
        )

        transport = c6.number_input(
            "Transport, PLN",
            min_value=0.0,
            value=0.0,
            step=50.0,
            key="tube_transport",
        )

        margin = st.number_input(
            "Margin, %",
            min_value=-100.0,
            value=0.0,
            step=1.0,
            key="tube_margin",
        )

        st.markdown("</div>", unsafe_allow_html=True)

    inp = TubeInput(
        diameter_mm=diameter,
        thickness_mm=thickness,
        length_mm=length,
        product_type=product_type,
        inner_cover=inner_cover,
        outer_cover=outer_cover,
        quantity_pcs=int(qty),
        quantity_per_pallet=int(qty_per_pallet),
        transport_cost_pln=transport,
        margin_percent=margin,
    )

    result = calculate_tube(inp)
    result_dict = result.to_dict()

    with right:
        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Price / r.m.", money(result.price_per_rm_pln))
        m2.metric("Price / piece", money(result.price_per_piece_pln))
        m3.metric("Weight kg/r.m.", number(result.weight_kg_per_rm, 6))
        m4.metric("Flat crush", f"{result.flat_crush_n_per_0_1m:,.1f} N")

        result_chart(result_dict, "Tube / Core")

        st.markdown("#### Calculation summary")

        st.dataframe(
            pd.DataFrame(result_dict.items(), columns=["Metric", "Value"]),
            use_container_width=True,
            hide_index=True,
        )

        download_quote(
            product="Tube Core",
            inputs=asdict(inp),
            result=result_dict,
        )


def materials_page() -> None:
    st.subheader("📦 Materials & Calibration Database")

    data = load_materials()

    st.markdown(
        """
        <div class='warning-box'>
            This MVP stores material data in <b>data/materials.json</b>.
            Edit it in GitHub or add an admin save function later.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Paper parameters")

    material_df = (
        pd.DataFrame(data["paper_types"])
        .T
        .reset_index()
        .rename(columns={"index": "material"})
    )

    st.dataframe(material_df, use_container_width=True, hide_index=True)

    st.markdown("### FX rates")
    st.json(data["fx_rates"])

    st.markdown("### Calibration constants")
    st.json(data["calibration"])


def formula_audit_page() -> None:
    st.subheader("🧬 Excel Formula Audit")

    catalog = load_formula_catalog()

    total_formulas = catalog.get("total_formulas", 0)
    sheet_stats = catalog.get("sheet_stats", [])
    formulas = catalog.get("formulas", [])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Extracted formula cells", f"{total_formulas:,}")
    c2.metric("Workbook sheets", f"{len(sheet_stats):,}")
    c3.metric(
        "Migrated MVP modules",
        "2",
        help="Edge Protectors and Tubes / Cores are currently included in the MVP engine."
    )
    c4.metric(
        "Pending modules",
        "4+",
        help="HoneyComb, Cardboard Pallets, Technology sheets, and full formula validation."
    )

    st.markdown("### Workbook formula distribution")

    if not sheet_stats:
        st.info(
            "No formula catalog found yet. "
            "Create data/formula_catalog.json to display workbook formula statistics."
        )
        return

    stats_df = pd.DataFrame(sheet_stats)

    expected_columns = ["sheet", "formulas", "rows", "cols", "status"]

    for col in expected_columns:
        if col not in stats_df.columns:
            stats_df[col] = ""

    st.dataframe(
        stats_df[expected_columns],
        use_container_width=True,
        hide_index=True,
    )

    chart_df = stats_df.copy()
    chart_df["formulas"] = pd.to_numeric(chart_df["formulas"], errors="coerce").fillna(0)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=chart_df["sheet"],
            y=chart_df["formulas"],
            marker=dict(color="#00E5FF"),
            text=chart_df["formulas"],
            textposition="outside",
        )
    )

    fig.update_layout(
        title="Formula count by workbook sheet",
        xaxis_title="Sheet",
        yaxis_title="Formula cells",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E5E7EB"),
        height=430,
        margin=dict(l=20, r=20, t=60, b=120),
        xaxis_tickangle=-35,
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Migration interpretation")

    st.markdown(
        """
        <div class='warning-box'>
            The formula catalog is used as the Excel-to-Python migration map.
            It should not be pasted directly into the app logic. Instead, formulas
            are migrated module by module into clean Python functions inside
            <b>core/formulas.py</b>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Migration priority")

    priority_df = pd.DataFrame(
        [
            {
                "Priority": 1,
                "Module": "Edge Protectors",
                "Reason": "Already included in MVP. Needs validation against Excel.",
                "Next Action": "Add benchmark tests."
            },
            {
                "Priority": 2,
                "Module": "Tubes / Cores",
                "Reason": "Already included in MVP. Needs validation against Excel.",
                "Next Action": "Add benchmark tests."
            },
            {
                "Priority": 3,
                "Module": "Paper Database",
                "Reason": "Material parameters are required by all calculators.",
                "Next Action": "Add admin editing and price fields."
            },
            {
                "Priority": 4,
                "Module": "Cardboard Pallets",
                "Reason": "Medium formula complexity and useful business module.",
                "Next Action": "Create pallet calculator page."
            },
            {
                "Priority": 5,
                "Module": "HoneyComb",
                "Reason": "Highest formula complexity.",
                "Next Action": "Migrate after simpler modules are validated."
            },
        ]
    )

    st.dataframe(
        priority_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Formula search")

    if formulas:
        sheet_names = [item.get("sheet", "") for item in sheet_stats]

        selected_sheet = st.selectbox(
            "Filter by sheet",
            ["All"] + sheet_names,
        )

        filtered_formulas = formulas

        if selected_sheet != "All":
            filtered_formulas = [
                f for f in filtered_formulas
                if f.get("sheet") == selected_sheet
            ]

        query = st.text_input("Search formula text or cell reference")

        if query:
            q = query.lower()
            filtered_formulas = [
                f for f in filtered_formulas
                if q in str(f.get("formula", "")).lower()
                or q in str(f.get("cell", "")).lower()
            ]

        st.dataframe(
            pd.DataFrame(filtered_formulas[:1000]),
            use_container_width=True,
            hide_index=True,
        )

        st.caption("Showing first 1000 filtered formulas for performance.")
    else:
        st.info(
            "Lightweight formula catalog is loaded. "
            "Full individual formula search will become available after uploading "
            "the full extracted formula catalog."
        )
    inject_css()
    hero()

    with st.sidebar:
        st.title("Pricing Engine")

        page = st.radio(
            "Navigation",
            [
                "Dashboard",
                "Edge Protector",
                "Tubes / Cores",
                "Materials",
                "Formula Audit",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        st.caption("Built for GitHub + Streamlit deployment")
        st.caption("Version: 0.1.0 MVP")

    if page == "Dashboard":
        dashboard_page()
    elif page == "Edge Protector":
        edge_page()
    elif page == "Tubes / Cores":
        tube_page()
    elif page == "Materials":
        materials_page()
    elif page == "Formula Audit":
        formula_audit_page()

    st.markdown(
        """
        <div class='footer'>
            © IP Poland Pricing Engine · Excel-to-Python migration scaffold ·
            Validate all pricing before commercial use.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
