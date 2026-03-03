import streamlit as st

def apply_custom_styles():
    """Professional dashboard styles - dark neutral, no white, no glow"""
    
    st.markdown("""
    <style>
        /* App Background */
        .main {
            background: #ECEFF3;
        }

        /* Header */
        .dashboard-header {
            background: #2E3440; /* dark slate */
            border-radius: 14px;
            padding: 30px;
            margin-bottom: 32px;
            border: 1px solid #3B4252;
        }

        .dashboard-header h1 {
            color: #ECEFF4 !important;
            font-size: 2.4rem !important;
            font-weight: 700 !important;
        }

        .dashboard-header .subtitle {
            color: #D8DEE9 !important;
            font-size: 1.05rem;
            font-weight: 400;
        }

        /* Metric Cards */
        .stat-card {
            background: #3B4252; /* dark muted card */
            border-radius: 14px;
            padding: 22px;
            border: 1px solid #4C566A;
            text-align: center;
            transition: all 0.2s ease;
            color: #ECEFF4;
        }

        .stat-card:hover {
            border-color: #5E81AC; /* muted blue accent */
            transform: translateY(-2px);
        }

        .stat-card .number {
            font-size: 1.9rem;
            font-weight: 700;
            color: #ECEFF4;
        }

        .stat-card .label {
            color: #D8DEE9;
            font-size: 0.9rem;
            margin-top: 8px;
        }

        .stat-card .delta {
            font-size: 0.85rem;
            color: #88C0D0;
            margin-top: 6px;
        }

        /* Info Boxes */
        .info-box {
            background: #434C5E;
            border-left: 5px solid #81A1C1;
            border-radius: 14px;
            padding: 20px;
            margin: 20px 0;
            color: #ECEFF4;
        }

        /* Section Headers */
        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 0;
            border-bottom: 1px solid #4C566A;
            margin-bottom: 24px;
        }

        .section-header h2 {
            margin: 0 !important;
            font-size: 1.7rem !important;
            color: #2E3440;
            font-weight: 700;
        }

        /* Country Cards */
        .country-card {
            background: #3B4252;
            border: 1px solid #4C566A;
            border-radius: 12px;
            padding: 16px;
            margin: 10px 0;
            transition: all 0.2s ease;
            color: #ECEFF4;
        }

        .country-card:hover {
            border-color: #81A1C1;
            transform: translateX(3px);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background: #DDE2E8 !important;
            padding: 8px !important;
            border-radius: 14px !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px !important;
            padding: 0 22px !important;
            font-weight: 500;
            color: #2E3440;
        }

        .stTabs [aria-selected="true"] {
            border-bottom: 3px solid #5E81AC;
            color: #2E3440;
        }

        /* Divider */
        .stDivider {
            margin: 32px 0 !important;
            border-top: 1px solid #C0C7D1 !important;
        }

        /* Footer */
        .dashboard-footer {
            background: #2E3440;
            border-radius: 14px;
            border-top: 1px solid #3B4252;
            padding: 26px;
            margin-top: 48px;
            text-align: center;
            color: #D8DEE9;
            font-size: 0.9rem;
        }
    </style>
    """, unsafe_allow_html=True)


def create_metric_card(label, value, icon="📊", delta=None):
    """Custom metric card with professional dark-muted theme"""
    delta_html = f"<div class='delta'>{delta}</div>" if delta else ""
    return f"""
    <div class="stat-card">
        <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
        <div class="number">{value}</div>
        <div class="label">{label}</div>
        {delta_html}
    </div>
    """

def apply_plotly_theme():
    import plotly.io as pio

    pio.templates["professional_dark"] = pio.templates["plotly_white"].update({
        "layout": {
            "paper_bgcolor": "#ECEFF3",
            "plot_bgcolor": "#ECEFF3",
            "font": {
                "color": "#E6E8EB",
                "size": 13
            },
            "title": {
                "font": {"size": 18, "color": "#E6E8EB"}
            },
            "xaxis": {
                "gridcolor": "#C7CED9",
                "zerolinecolor": "#C7CED9"
            },
            "yaxis": {
                "gridcolor": "#C7CED9",
                "zerolinecolor": "#C7CED9"
            }
        }
    })

    pio.templates.default = "professional_dark"

