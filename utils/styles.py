import streamlit as st

def apply_custom_styles():
    """Professional dashboard styles - no white cards, no glowing colors"""
    
    st.markdown("""
    <style>
        /* Dashboard Background */
        .main {
            background: #F4F5F7;
        }

        /* Header */
        .dashboard-header {
            background: #D9E2EC; /* soft muted blue-gray */
            border-radius: 12px;
            padding: 28px;
            margin-bottom: 32px;
            border: 1px solid #BCCCDC;
        }

        .dashboard-header h1 {
            color: #1B3A57;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
        }

        .dashboard-header .subtitle {
            color: #495057 !important;
            font-size: 1.1rem;
            font-weight: 400;
        }

        /* Metric Cards */
        .stat-card {
            background: #E0E4E8; /* muted card color */
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #BCCCDC;
            text-align: center;
            transition: all 0.2s ease;
            color: #1B3A57;
        }

        .stat-card:hover {
            border-color: #3A8D7C; /* subtle accent */
            transform: translateY(-2px);
        }

        .stat-card .number {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1B3A57;
        }

        .stat-card .label {
            color: #495057;
            font-size: 0.9rem;
            margin-top: 8px;
        }

        .stat-card .delta {
            font-size: 0.9rem;
            color: #3A8D7C;
            margin-top: 4px;
        }

        /* Info Boxes */
        .info-box {
            background: #D9E2EC;
            border-left: 4px solid #3A8D7C;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            color: #1B3A57;
        }

        /* Section Headers */
        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 0;
            border-bottom: 2px solid #BCCCDC;
            margin-bottom: 24px;
        }

        .section-header h2 {
            margin: 0 !important;
            font-size: 1.8rem !important;
            color: #1B3A57;
        }

        /* Country Cards */
        .country-card {
            background: #E0E4E8;
            border: 1px solid #BCCCDC;
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            transition: all 0.2s ease;
            color: #1B3A57;
        }

        .country-card:hover {
            border-color: #3A8D7C;
            transform: translateX(2px);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background: #D9E2EC !important;
            padding: 8px !important;
            border-radius: 12px !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px !important;
            padding: 0 24px !important;
        }

        .stTabs [aria-selected="true"] {
            border-bottom: 3px solid #3A8D7C;
        }

        /* Divider */
        .stDivider {
            margin: 32px 0 !important;
            border-top: 1px solid #BCCCDC !important;
        }

        /* Footer */
        .dashboard-footer {
            background: #D9E2EC;
            border-radius: 12px;
            border-top: 1px solid #BCCCDC;
            padding: 24px;
            margin-top: 48px;
            text-align: center;
            color: #495057;
        }
    </style>
    """, unsafe_allow_html=True)


def create_metric_card(label, value, icon="📊", delta=None):
    """Custom metric card with professional muted color theme"""
    delta_html = f"<div class='delta'>{delta}</div>" if delta else ""
    return f"""
    <div class="stat-card">
        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
        <div class="number">{value}</div>
        <div class="label">{label}</div>
        {delta_html}
    </div>
    """
