import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the dashboard"""
    
    # Load external CSS if exists
    try:
        with open("sri-lanka-tourism-dashboard.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except:
        pass
    
    # Apply enhanced custom CSS
    st.markdown("""
    <style>
        /* Glass Card Effect */
        .glass-card {
            background: rgba(35, 42, 52, 0.6) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(67, 233, 123, 0.1);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        /* Animated gradient background */
        .main {
            background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
            animation: gradientShift 15s ease infinite;
            background-size: 200% 200%;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Enhanced Header */
        .dashboard-header {
            background: linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.1) 100%);
            border-radius: 20px;
            padding: 32px;
            margin-bottom: 32px;
            border: 1px solid rgba(67, 233, 123, 0.2);
            box-shadow: 0 8px 32px rgba(67, 233, 123, 0.1);
        }
        
        .dashboard-header h1 {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem !important;
            font-weight: 800 !important;
            margin-bottom: 8px;
            text-shadow: none !important;
        }
        
        .dashboard-header .subtitle {
            color: #bfc9d1 !important;
            font-size: 1.2rem;
            font-weight: 400;
        }
        
        /* Enhanced Metrics */
        .stMetric {
            background: linear-gradient(135deg, rgba(35, 42, 52, 0.8) 0%, rgba(35, 42, 52, 0.6) 100%) !important;
            border: 1px solid rgba(67, 233, 123, 0.15) !important;
            transition: all 0.3s ease;
        }
        
        .stMetric:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(67, 233, 123, 0.15);
            border-color: rgba(67, 233, 123, 0.3) !important;
        }
        
        /* Section Headers */
        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 16px 0;
            border-bottom: 2px solid rgba(67, 233, 123, 0.2);
            margin-bottom: 24px;
        }
        
        .section-header h2 {
            margin: 0 !important;
            font-size: 1.8rem !important;
        }
        
        /* Stat Cards */
        .stat-card {
            background: linear-gradient(135deg, rgba(35, 42, 52, 0.9) 0%, rgba(35, 42, 52, 0.7) 100%);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(67, 233, 123, 0.15);
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            border-color: rgba(67, 233, 123, 0.4);
            box-shadow: 0 8px 24px rgba(67, 233, 123, 0.15);
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-card .label {
            color: #bfc9d1;
            font-size: 0.9rem;
            margin-top: 8px;
        }
        
        /* Enhanced Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background: rgba(35, 42, 52, 0.4) !important;
            padding: 8px !important;
            border-radius: 12px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px !important;
            padding: 0 24px !important;
        }
        
        .stTabs [aria-selected="true"] {
            box-shadow: 0 4px 12px rgba(67, 233, 123, 0.2);
        }
        
        /* Info boxes */
        .info-box {
            background: linear-gradient(135deg, rgba(67, 233, 123, 0.1) 0%, rgba(56, 249, 215, 0.05) 100%);
            border-left: 4px solid #43e97b;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
        }
        
        /* Country cards */
        .country-card {
            background: rgba(35, 42, 52, 0.6);
            border: 1px solid rgba(67, 233, 123, 0.1);
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            transition: all 0.3s ease;
        }
        
        .country-card:hover {
            border-color: rgba(67, 233, 123, 0.3);
            transform: translateX(4px);
        }
        
        /* Enhanced dividers */
        .stDivider {
            margin: 32px 0 !important;
            border-top: 1px solid rgba(67, 233, 123, 0.15) !important;
        }
        
        /* Footer */
        .dashboard-footer {
            background: linear-gradient(135deg, rgba(35, 42, 52, 0.8) 0%, rgba(35, 42, 52, 0.6) 100%);
            border-radius: 16px;
            border-top: 2px solid rgba(67, 233, 123, 0.2);
            padding: 24px;
            margin-top: 48px;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

def create_metric_card(label, value, icon="📊", delta=None):
    """Create a custom metric card"""
    delta_html = f"<div style='color: #43e97b; font-size: 0.9rem; margin-top: 4px;'>{delta}</div>" if delta else ""
    return f"""
    <div class="stat-card">
        <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
        <div class="number">{value}</div>
        <div class="label">{label}</div>
        {delta_html}
    </div>
    """