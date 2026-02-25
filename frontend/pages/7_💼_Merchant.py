import streamlit as st
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.switch_page("app.py")
from components.sidebar import render_sidebar
render_sidebar()
from components.widgets import (
    alert_box,
    card_container,
    stat_card,
    data_table,
    status_badge
)
from components.metrics import metric_card_group, kpi_card
from services.data_provider import get_data_provider
from utils.helpers import format_currency, format_percentage, format_number
import logging
import random

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">💼 Merchant Insights</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Merchant performance and risk analysis</p>', unsafe_allow_html=True)

# Check backend
provider = get_data_provider()
if not provider.backend_available:
    alert_box("⚠️ Backend unavailable. Showing demo merchant data.", "warning")

# Top merchants overview
st.markdown("### 🏆 Top Merchants")

# Generate mock merchant data
merchants = [
    {'name': 'Amazon Web Services', 'transactions': 1247, 'amount': 487500, 'risk': 12},
    {'name': 'Microsoft Azure', 'transactions': 892, 'amount': 345200, 'risk': 15},
    {'name': 'Google Cloud', 'transactions': 756, 'amount': 289300, 'risk': 18},
    {'name': 'Salesforce', 'transactions': 634, 'amount': 198700, 'risk': 22},
    {'name': 'Adobe Creative Cloud', 'transactions': 523, 'amount': 156800, 'risk': 25},
]

# Summary metrics
total_transactions = sum(m['transactions'] for m in merchants)
total_amount = sum(m['amount'] for m in merchants)
avg_risk = sum(m['risk'] for m in merchants) / len(merchants)

metric_card_group([
    {'title': 'Total Merchants', 'value': '247', 'delta': '+12 this month'},
    {'title': 'Total Transactions', 'value': format_number(total_transactions), 'delta': '+8.3%'},
    {'title': 'Total Volume', 'value': format_currency(total_amount), 'delta': '+12.5%'},
    {'title': 'Avg Risk Score', 'value': f'{avg_risk:.1f}', 'delta': '-2.3'}
])

st.divider()

# Merchant leaderboard
st.markdown("### 📊 Merchant Leaderboard")

col1, col2 = st.columns([3, 1])

with col1:
    sort_by = st.selectbox(
        "Sort by",
        options=['Transaction Volume', 'Dollar Amount', 'Risk Score'],
        index=0
    )

with col2:
    period = st.selectbox(
        "Period",
        options=['Last 7 Days', 'Last 30 Days', 'Last 90 Days'],
        index=1
    )

# Display merchant cards
for i, merchant in enumerate(merchants):
    risk_color = 'success' if merchant['risk'] < 20 else 'warning' if merchant['risk'] < 30 else 'danger'
    
    with card_container(
        title=f"#{i+1} {merchant['name']}",
        icon="🏢",
        variant=risk_color
    ):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**Transactions**")
            st.markdown(f"### {format_number(merchant['transactions'])}")
        
        with col2:
            st.markdown("**Volume**")
            st.markdown(f"### {format_currency(merchant['amount'])}")
        
        with col3:
            st.markdown("**Avg Amount**")
            avg = merchant['amount'] / merchant['transactions'] if merchant['transactions'] > 0 else 0
            st.markdown(f"### {format_currency(avg)}")
        
        with col4:
            st.markdown("**Risk Score**")
            st.markdown(f"### {merchant['risk']}")
            status_badge(
                'Low Risk' if merchant['risk'] < 20 else 'Medium Risk' if merchant['risk'] < 30 else 'High Risk',
                risk_color
            )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 View Details", key=f"details_{i}", use_container_width=True):
                st.info(f"Loading details for {merchant['name']}...")
        
        with col2:
            if st.button("📈 Trends", key=f"trends_{i}", use_container_width=True):
                st.info(f"Loading trends for {merchant['name']}...")
        
        with col3:
            if st.button("🔍 Investigate", key=f"investigate_{i}", use_container_width=True):
                st.info(f"Opening investigation for {merchant['name']}...")

st.divider()

# Merchant categories
st.markdown("### 🏷️ Merchant Categories")

tab1, tab2, tab3 = st.tabs(["By Industry", "By Region", "By Risk"])

with tab1:
    with card_container("Industry Breakdown", "🏭", variant='primary'):
        industries = [
            {'name': 'Cloud Services', 'count': 45, 'amount': 1250000},
            {'name': 'Software/SaaS', 'count': 78, 'amount': 980000},
            {'name': 'Professional Services', 'count': 34, 'amount': 560000},
            {'name': 'Marketing Tools', 'count': 52, 'amount': 420000},
            {'name': 'Other', 'count': 38, 'amount': 340000}
        ]
        
        data_table(
            data=industries,
            columns=['name', 'count', 'amount'],
            max_height=300
        )

with tab2:
    with card_container("Regional Distribution", "🌍", variant='success'):
        regions = [
            {'region': 'North America', 'merchants': 145, 'volume': 2100000},
            {'region': 'Europe', 'merchants': 67, 'volume': 890000},
            {'region': 'Asia Pacific', 'merchants': 28, 'volume': 450000},
            {'region': 'Other', 'merchants': 7, 'volume': 110000}
        ]
        
        data_table(
            data=regions,
            columns=['region', 'merchants', 'volume'],
            max_height=300
        )

with tab3:
    with card_container("Risk Distribution", "⚠️", variant='warning'):
        st.markdown("""
        **Merchant Risk Levels:**
        
        - 🟢 **Low Risk (0-20):** 156 merchants (63%)
        - 🟡 **Medium Risk (21-40):** 67 merchants (27%)
        - 🔴 **High Risk (41-60):** 18 merchants (7%)
        - 🔴 **Critical (61+):** 6 merchants (2%)
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Merchants Under Review", "24", "+3")
        
        with col2:
            st.metric("Blacklisted", "6", "+1")

st.divider()

# Merchant trends
st.markdown("### 📈 Merchant Trends")

import pandas as pd
import plotly.graph_objects as go

# Mock trend data
dates = pd.date_range(end=pd.Timestamp.now(), periods=30, freq='D')
new_merchants = [random.randint(3, 12) for _ in range(30)]
churned_merchants = [random.randint(0, 5) for _ in range(30)]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=dates,
    y=new_merchants,
    mode='lines+markers',
    name='New Merchants',
    line=dict(color='#00d68f', width=3)
))

fig.add_trace(go.Scatter(
    x=dates,
    y=churned_merchants,
    mode='lines+markers',
    name='Churned Merchants',
    line=dict(color='#ff5252', width=3)
))

fig.update_layout(
    title='Merchant Growth (Last 30 Days)',
    xaxis_title='Date',
    yaxis_title='Count',
    height=400,
    template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white',
    hovermode='x unified'
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Merchant actions
st.markdown("### 🔧 Merchant Management")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ Add Merchant", use_container_width=True, type="primary"):
        st.info("Add merchant form coming soon!")

with col2:
    if st.button("📊 Export Report", use_container_width=True):
        st.info("Export functionality coming soon!")

with col3:
    if st.button("⚙️ Manage Categories", use_container_width=True):
        st.info("Category management coming soon!")