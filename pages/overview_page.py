import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils.data_loader import format_number
from utils.styles import create_metric_card


def render(data):
    """Render the Overview Dashboard"""

    overview = data.get("overview", {})
    filtered_df = data.get("filtered_df", pd.DataFrame())
    year_comparison = data.get("year_comparison", [])
    regional_data = data.get("regional_data", [])

    # =======================
    # PAGE HEADER
    # =======================
    st.markdown(
        """
        <div class="section-header">
            <h2>📊 Dashboard Overview</h2>
            <p>
                High-level insights and arrival trends based on selected filters
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # =======================
    # KPI METRICS
    # =======================
    st.markdown("### 🔢 Key Performance Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            create_metric_card(
                label="Total Arrivals",
                value=format_number(overview.get("total_arrivals", 0)),
                icon="🌍"
            ),
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            create_metric_card(
                label="Average Monthly Arrivals",
                value=format_number(overview.get("avg_monthly_arrivals", 0)),
                icon="📅"
            ),
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            create_metric_card(
                label="Arrivals (Last 6 Months)",
                value=format_number(overview.get("recent_6_months", 0)),
                icon="⏳"
            ),
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =======================
    # TABS
    # =======================
    tab1, tab2, tab3 = st.tabs(
        [
            "📈 Time Series Analysis",
            "🌎 Regional Distribution",
            "📅 Yearly Comparison",
        ]
    )

    # =======================
    # TAB 1: TIME SERIES
    # =======================
    with tab1:
        st.markdown("#### Total Arrivals Over Time")

        if not filtered_df.empty:
            ts_df = (
                filtered_df
                .groupby("date", as_index=False)["arrivals"]
                .sum()
            )

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=ts_df["date"],
                    y=ts_df["arrivals"],
                    mode="lines+markers",
                    name="Total Arrivals",
                    line=dict(width=3),
                    marker=dict(size=7),
                    fill="tozeroy"
                )
            )

            fig.update_layout(
                template="professional_dark",
                height=420,
                xaxis_title="Date",
                yaxis_title="Arrivals",
                hovermode="x unified",
                margin=dict(t=40, b=30, l=30, r=30),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key="overview_time_series"
            )
        else:
            st.info("No data available for the selected filters.")

    # =======================
    # TAB 2: REGIONAL BREAKDOWN
    # =======================
    with tab2:
        st.markdown("#### Arrivals by Region")

        if regional_data:
            region_df = pd.DataFrame(regional_data)

            fig_pie = px.pie(
                region_df,
                names="region",
                values="arrivals",
                hole=0.45,
            )

            fig_pie.update_traces(
                textinfo="percent+label",
                pull=[0.03] * len(region_df)
            )

            fig_pie.update_layout(
                template="professional_dark",
                height=380,
                margin=dict(t=30, b=20, l=20, r=20),
                showlegend=True,
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True,
                key="overview_region_pie"
            )

            with st.expander("📋 View Regional Data Table"):
                st.dataframe(region_df, use_container_width=True)
        else:
            st.warning("Regional data is not available.")

    # =======================
    # TAB 3: YEARLY COMPARISON
    # =======================
    with tab3:
        st.markdown("#### Year-over-Year Comparison")

        if year_comparison:
            yc_df = pd.DataFrame(year_comparison)

            fig_bar = px.bar(
                yc_df,
                x="year",
                y="total_arrivals",
                text_auto=True,
            )

            fig_bar.update_layout(
                template="professional_dark",
                height=380,
                xaxis_title="Year",
                yaxis_title="Total Arrivals",
                margin=dict(t=40, b=30, l=30, r=30),
            )

            st.plotly_chart(
                fig_bar,
                use_container_width=True,
                key="overview_yearly_bar"
            )

            with st.expander("📊 View Yearly Comparison Table"):
                st.dataframe(yc_df, use_container_width=True)
        else:
            st.info("Yearly comparison data is unavailable.")
