import streamlit as st
from utils.helpers import apply_theme
apply_theme()
if not st.session_state.get('logged_in', False):
    st.warning('⚠️ Vui lòng đăng nhập để tiếp tục.')
    st.stop()
from components.sidebar import render_sidebar
render_sidebar()
from components.widgets import (
    alert_box,
    status_badge,
    timeline_item,
    card_container,
    data_table,
    empty_state
)
from components.charts import plot_fraud_by_type
from components.metrics import metric_card_group
from services.data_provider import get_fraud_scenarios, get_data_provider
from utils.helpers import format_currency, time_ago
import logging

logger = logging.getLogger(__name__)

# Page header
st.markdown('<h1 class="main-header">🚨 Fraud Detection Center</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Active fraud scenarios and security alerts</p>', unsafe_allow_html=True)

# Check backend
provider = get_data_provider()
if not provider.backend_available:
    alert_box("⚠️ Backend unavailable. Showing demo fraud scenarios.", "warning")

# Load fraud scenarios
with st.spinner("Loading fraud scenarios..."):
    try:
        scenarios = get_fraud_scenarios()
    except Exception as e:
        logger.error(f"Error loading fraud scenarios: {e}")
        st.error("Failed to load fraud scenarios")
        scenarios = []

if not scenarios:
    empty_state(
        message="No active fraud scenarios detected",
        icon="✅",
        action_text="Refresh",
        action_callback=lambda: st.rerun()
    )
    st.stop()

# Summary metrics
st.markdown("### 📊 Fraud Overview")

total_scenarios = len(scenarios)
critical_count = sum(1 for s in scenarios if s.get('severity') == 'CRITICAL')
high_count = sum(1 for s in scenarios if s.get('severity') == 'HIGH')
total_loss = sum(s.get('potential_loss', 0) for s in scenarios)

metric_card_group([
    {
        'title': 'Total Scenarios',
        'value': total_scenarios,
        'delta': '+3 today'
    },
    {
        'title': 'Critical',
        'value': critical_count,
        'delta': '+1 today'
    },
    {
        'title': 'High Risk',
        'value': high_count,
        'delta': '+2 today'
    },
    {
        'title': 'Potential Loss',
        'value': format_currency(total_loss),
        'delta': '+12.5%'
    }
])

st.divider()

# Fraud by type chart
st.markdown("### 📈 Fraud Detection by Type")
plot_fraud_by_type(scenarios, "Active Fraud Scenarios", 400)

st.divider()

# Active scenarios list
st.markdown("### 🔍 Active Fraud Scenarios")

# Filter options
col1, col2, col3 = st.columns(3)

with col1:
    severity_filter = st.selectbox(
        "Severity",
        options=['All', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        index=0
    )

with col2:
    status_filter = st.selectbox(
        "Status",
        options=['All', 'Active', 'Investigating', 'Resolved'],
        index=0
    )

with col3:
    sort_by = st.selectbox(
        "Sort by",
        options=['Severity', 'Date', 'Amount'],
        index=0
    )

# Apply filters
filtered_scenarios = scenarios

if severity_filter != 'All':
    filtered_scenarios = [s for s in filtered_scenarios if s.get('severity') == severity_filter]

if status_filter != 'All':
    filtered_scenarios = [s for s in filtered_scenarios if s.get('status') == status_filter]

# Sort
if sort_by == 'Severity':
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    filtered_scenarios.sort(key=lambda x: severity_order.get(x.get('severity', 'LOW'), 999))
elif sort_by == 'Date':
    filtered_scenarios.sort(key=lambda x: x.get('detected_at', ''), reverse=True)
elif sort_by == 'Amount':
    filtered_scenarios.sort(key=lambda x: x.get('potential_loss', 0), reverse=True)

# Display scenarios
if not filtered_scenarios:
    st.info("No scenarios match the selected filters")
else:
    for i, scenario in enumerate(filtered_scenarios):
        severity = scenario.get('severity', 'LOW')
        scenario_type = scenario.get('type', 'Unknown')
        status = scenario.get('status', 'Unknown')
        detected_at = scenario.get('detected_at', '')
        affected = scenario.get('affected_invoices', 0)
        potential_loss = scenario.get('potential_loss', 0)
        confidence = scenario.get('confidence', 0.0)
        description = scenario.get('description', 'No description')
        
        # Severity colors
        severity_colors = {
            'CRITICAL': 'danger',
            'HIGH': 'warning',
            'MEDIUM': 'info',
            'LOW': 'info'
        }
        
        severity_color = severity_colors.get(severity, 'info')
        
        with card_container(
            title=f"{scenario_type}",
            icon="🚨" if severity in ['CRITICAL', 'HIGH'] else "⚠️",
            variant=severity_color
        ):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("**Severity**")
                status_badge(severity, severity_color)
            
            with col2:
                st.markdown("**Status**")
                st.write(status)
            
            with col3:
                st.markdown("**Affected Invoices**")
                st.write(f"{affected} invoices")
            
            with col4:
                st.markdown("**Potential Loss**")
                st.write(format_currency(potential_loss))
            
            st.markdown("---")
            
            st.markdown("**Description**")
            st.write(description)
            
            st.markdown(f"**Confidence:** {confidence*100:.1f}% | **Detected:** {time_ago(detected_at)}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔍 Investigate", key=f"investigate_{i}", use_container_width=True):
                    st.info(f"Opening investigation dashboard for {scenario_type}...")
            
            with col2:
                if st.button("✅ Mark Resolved", key=f"resolve_{i}", use_container_width=True):
                    st.success(f"Marked {scenario_type} as resolved")
            
            with col3:
                if st.button("📊 View Details", key=f"details_{i}", use_container_width=True):
                    with st.expander("Scenario Details", expanded=True):
                        st.json({
                            'id': scenario.get('id'),
                            'type': scenario_type,
                            'severity': severity,
                            'status': status,
                            'detected_at': detected_at,
                            'affected_invoices': affected,
                            'potential_loss': potential_loss,
                            'confidence': confidence
                        })

st.divider()

# Investigation tools
st.markdown("### 🔧 Investigation Tools")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 Pattern Analysis", use_container_width=True, type="primary"):
        st.info("Pattern analysis tool coming soon!")

with col2:
    if st.button("📊 Network Graph", use_container_width=True):
        st.info("Network visualization coming soon!")

with col3:
    if st.button("📄 Export Report", use_container_width=True):
        st.info("Export functionality coming soon!")