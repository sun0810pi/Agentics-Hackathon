"""app.py — AgentFlow Finance Guard — Single Page Application"""
import sys
import logging
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Page config (MUST be first) ──────────────────────────
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={"About": f"{config.APP_NAME} v{config.APP_VERSION}"},
)

# ─── Session defaults ──────────────────────────────────────
_DEFAULTS = {
    "logged_in": False, "user_email": "", "user_name": "",
    "user_role": "viewer", "access_token": "", "id_token": "",
    "refresh_token": "", "theme": "dark", "language": "EN",
    "page": "Overview", "show_logout_confirm": False,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── Theme ─────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def _get_css(theme):
    from themes.dark import DARK_THEME
    from themes.light import LIGHT_THEME
    return DARK_THEME if theme == "dark" else LIGHT_THEME

st.markdown(_get_css(st.session_state.theme), unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────
PAGES = [
    ("Overview",      "📊", ["admin","analyst","viewer"]),
    ("Upload",        "📄", ["admin","analyst"]),
    ("Fraud",         "🚨", ["admin","analyst"]),
    ("ML_Insights",   "🧠", ["admin","analyst"]),
    ("Security",      "🛡️",  ["admin"]),
    ("Observability", "📈", ["admin","analyst"]),
    ("Merchant",      "💼", ["admin","analyst","viewer"]),
    ("Integrations",  "🔗", ["admin"]),
    ("Settings",      "⚙️",  ["admin","analyst","viewer"]),
]

def render_sidebar():
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:0.75rem 0 1rem;">'
            '<div style="font-size:2.5rem;">🛡️</div>'
            '<div style="font-size:1.3rem;font-weight:900;color:#4A9EFF;">AgentFlow</div>'
            '<div style="opacity:0.6;font-size:0.8rem;">Finance Guard</div>'
            '</div>',
            unsafe_allow_html=True
        )
        st.divider()

        # User info
        name  = st.session_state.user_name or "User"
        role  = (st.session_state.user_role or "viewer").title()
        email = st.session_state.user_email or ""
        rc    = {"Admin":"#4A9EFF","Analyst":"#00d68f","Viewer":"#ffab00"}.get(role,"#718096")
        st.markdown(
            f'<div style="padding:0.6rem;background:rgba(74,158,255,0.1);border-radius:8px;'
            f'border:1px solid rgba(74,158,255,0.2);margin-bottom:0.75rem;">'
            f'<b>{name}</b><br/>'
            f'<span style="font-size:0.72rem;color:{rc};font-weight:700;">{role}</span><br/>'
            f'<span style="font-size:0.68rem;opacity:0.55;">{email}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Navigation
        st.markdown("**📋 Navigation**")
        user_role_key = (st.session_state.user_role or "viewer").lower()
        for page_key, icon, roles in PAGES:
            if user_role_key not in roles:
                continue
            label = page_key.replace("_", " ")
            is_cur = st.session_state.page == page_key
            if st.button(
                f"{icon} {label}",
                key=f"nav_{page_key}",
                use_container_width=True,
                type="primary" if is_cur else "secondary",
            ):
                st.session_state.page = page_key
                st.rerun()

        st.divider()

        # Theme
        st.markdown("**🎨 Theme**")
        c1, c2 = st.columns(2)
        cur = st.session_state.theme
        with c1:
            if st.button("☀️ Light", use_container_width=True,
                         type="primary" if cur=="light" else "secondary", key="th_light"):
                st.session_state.theme = "light"
                st.rerun()
        with c2:
            if st.button("🌙 Dark", use_container_width=True,
                         type="primary" if cur=="dark" else "secondary", key="th_dark"):
                st.session_state.theme = "dark"
                st.rerun()

        st.divider()

        # Logout
        if not st.session_state.show_logout_confirm:
            if st.button("🚪 Logout", use_container_width=True, type="secondary", key="sb_logout"):
                st.session_state.show_logout_confirm = True
                st.rerun()
        else:
            st.warning("⚠️ Logout?")
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ Yes", use_container_width=True, type="primary", key="sb_yes"):
                    for k in ["logged_in","user_email","user_name","user_role","access_token"]:
                        st.session_state[k] = False if k == "logged_in" else ""
                    st.session_state.page = "Overview"
                    st.session_state.show_logout_confirm = False
                    st.rerun()
            with cb:
                if st.button("❌ No", use_container_width=True, key="sb_no"):
                    st.session_state.show_logout_confirm = False
                    st.rerun()

        st.markdown(
            f'<div style="text-align:center;opacity:0.35;font-size:0.68rem;padding-top:0.5rem;">'
            f'AgentFlow v{config.APP_VERSION}</div>',
            unsafe_allow_html=True
        )

# ─── Page routing ──────────────────────────────────────────
def show_page(page_key):
    import logging
    logger = logging.getLogger(__name__)


def _page_Overview():
    try:
    # Step 1: theme
    except Exception as e:
        st.error(f"Theme error: {e}")

    # Step 2: login guard

    # Step 3: sidebar
    except Exception as e:
        st.sidebar.error(f"Sidebar: {e}")

    # Step 4: FORCE VISIBLE content - no matter what
    st.title("📊 Dashboard Overview")
    st.success("✅ Page loaded successfully!")
    st.write(f"Logged in as: **{st.session_state.get('user_name', '?')}** ({st.session_state.get('user_role', '?')})")

    # Step 5: load data safely
        from services.data_provider import get_dashboard_metrics, get_data_provider
        provider = get_data_provider()
        if not provider.backend_available:
            st.warning("⚠️ Backend unavailable — showing demo data.")

        metrics = get_dashboard_metrics()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Processed", f"{metrics.get('total_processed', 0):,}")
        col2.metric("Accuracy", f"{metrics.get('accuracy', 0):.1f}%")
        col3.metric("Fraud Prevented", f"${metrics.get('fraud_prevented_usd', 0):,.0f}")
        col4.metric("Avg Latency", f"{metrics.get('avg_latency_ms', 0):.0f}ms")

    except Exception as e:
        import traceback
        st.error(f"Data error: {e}")
        st.code(traceback.format_exc())

    # Step 6: charts
        from components.metrics import metric_card_group
        from components.charts import plot_time_series, plot_risk_distribution
        from services.data_provider import get_data_provider

        provider = get_data_provider()
        time_series = provider.get_time_series(days=30)
        metrics = get_dashboard_metrics()

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📊 Processing Volume (30 Days)")
            if time_series:
                plot_time_series(data=time_series, title="Invoice Processing Trend", height=350)
            else:
                st.info("No time series data")

        with col2:
            st.markdown("### 🎯 Risk Distribution")
            risk_dist = [
                {'risk_level': 'LOW',    'count': metrics.get('total_approved', 0), 'pct': 75},
                {'risk_level': 'MEDIUM', 'count': metrics.get('total_pending', 0),  'pct': 15},
                {'risk_level': 'HIGH',   'count': metrics.get('total_blocked', 0),  'pct': 10},
            ]
            plot_risk_distribution(data=risk_dist, title="Risk Score Distribution", height=350)

    except Exception as e:
        import traceback
        st.error(f"Charts error: {e}")
        st.code(traceback.format_exc())

    # Navigation
    st.divider()
    st.markdown("### ⚡ Quick Actions")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<a href="/Upload" target="_self"><button style="width:100%;padding:0.5rem;background:#4A9EFF;color:white;border:none;border-radius:8px;cursor:pointer;">📄 Upload Invoice</button></a>', unsafe_allow_html=True)
    c2.markdown('<a href="/Fraud" target="_self"><button style="width:100%;padding:0.5rem;background:rgba(255,255,255,0.1);color:inherit;border:1px solid rgba(255,255,255,0.2);border-radius:8px;cursor:pointer;">🚨 Fraud Alerts</button></a>', unsafe_allow_html=True)
    c3.markdown('<a href="/Observability" target="_self"><button style="width:100%;padding:0.5rem;background:rgba(255,255,255,0.1);color:inherit;border:1px solid rgba(255,255,255,0.2);border-radius:8px;cursor:pointer;">📈 Observability</button></a>', unsafe_allow_html=True)
    except Exception as e:
        import traceback
        st.error(f"Error in Overview: {e}")
        st.code(traceback.format_exc())


def _page_Upload():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
    from components.widgets import alert_box, success_box, error_box, warning_box
    from services.data_provider import process_invoice
    from utils.validators import validate_file_upload
    from utils.helpers import sanitize_filename
    import time

    st.markdown('<h1 class="main-header">📄 Upload Invoice</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload and analyze invoices</p>', unsafe_allow_html=True)

    # Upload section
    st.markdown("### 📤 Upload File")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Select invoice (PDF, PNG, JPG)",
            type=['pdf', 'png', 'jpg', 'jpeg']
        )

    with col2:
        mode = st.selectbox(
            "Mode",
            ['full', 'fast', 'demo'],
            format_func=lambda x: {
                'full': '🔍 Full (17 agents)',
                'fast': '⚡ Fast (5 agents)',
                'demo': '🎭 Demo'
            }[x]
        )

        threshold = st.slider("Auto-approve threshold", 0, 100, 30)

    if uploaded_file:
        st.info(f"📋 {uploaded_file.name} ({len(uploaded_file.getvalue())/1024:.1f} KB)")

        # Validate
        is_valid, error_msg = validate_file_upload(
            uploaded_file.name,
            uploaded_file.getvalue(),
            50
        )

        if not is_valid:
            error_box(f"❌ {error_msg}")
        else:
            if st.button("🚀 Process Invoice", type="primary", use_container_width=True):
                with st.status("Processing...", expanded=True) as status:
                    st.write("⬆️ Uploading...")
                    time.sleep(0.5)

                    st.write("🤖 Running analysis...")
                    result = process_invoice(
                        uploaded_file.getvalue(),
                        sanitize_filename(uploaded_file.name),
                        mode,
                        threshold
                    )

                    status.update(label="✅ Complete!", state="complete")

                # Results
                if result.get('success'):
                    decision = result.get('decision')

                    if decision == 'APPROVE':
                        success_box(f"✅ **APPROVED** - Risk: {result.get('risk_score', 0)}")
                    elif decision == 'BLOCK':
                        error_box(f"🚫 **BLOCKED** - Risk: {result.get('risk_score', 0)}")
                    else:
                        warning_box(f"⚠️ **REVIEW** - Risk: {result.get('risk_score', 0)}")

                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Risk Score", f"{result.get('risk_score', 0)}/100")
                    col2.metric("Confidence", f"{result.get('confidence', 0)*100:.1f}%")
                    col3.metric("Duration", f"{result.get('total_duration_ms', 0):.0f}ms")

                    # Details
                    with st.expander("🔍 Details"):
                        st.json(result.get('metadata', {}))
                else:
                    error_box(f"❌ Error: {result.get('error')}")

    else:
        st.info("👆 Upload a file to get started")
    except Exception as e:
        import traceback
        st.error(f"Error in Upload: {e}")
        st.code(traceback.format_exc())


def _page_Fraud():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
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
    except Exception as e:
        import traceback
        st.error(f"Error in Fraud: {e}")
        st.code(traceback.format_exc())


def _page_ML_Insights():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
    from components.widgets import alert_box, stat_card, progress_bar_animated, card_container
    from components.charts import plot_agent_performance
    from components.metrics import kpi_card
    from services.data_provider import get_agent_metrics, get_data_provider
    from utils.helpers import format_percentage
    import logging

    logger = logging.getLogger(__name__)

    # Page header
    st.markdown('<h1 class="main-header">🧠 ML Insights & Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Machine learning model performance and predictions</p>', unsafe_allow_html=True)

    # Check backend
    provider = get_data_provider()
    if not provider.backend_available:
        alert_box("⚠️ Backend unavailable. Showing demo ML insights.", "warning")

    # Load agent metrics
    with st.spinner("Loading ML insights..."):
            agents = get_agent_metrics()
        except Exception as e:
            logger.error(f"Error loading agent metrics: {e}")
            st.error("Failed to load ML insights")
            agents = []

    # Model performance overview
    st.markdown("### 🎯 Model Performance Overview")

    col1, col2, col3, col4 = st.columns(4)

    # Calculate aggregate metrics
    if agents:
        avg_success = sum(a.get('success_rate', 0) for a in agents) / len(agents)
        avg_latency = sum(a.get('avg_latency_ms', 0) for a in agents) / len(agents)
        total_processed = sum(a.get('processed_count', 0) for a in agents)
        healthy_count = sum(1 for a in agents if a.get('status') == 'active')
    else:
        avg_success = 0
        avg_latency = 0
        total_processed = 0
        healthy_count = 0

    with col1:
        kpi_card(
            title="Model Accuracy",
            value=avg_success,
            format_type='percentage',
            delta=2.3,
            target=99.0,
            variant='success'
        )

    with col2:
        kpi_card(
            title="Avg Inference Time",
            value=avg_latency,
            format_type='number',
            delta=-15.2,
            variant='primary'
        )

    with col3:
        kpi_card(
            title="Total Predictions",
            value=total_processed,
            format_type='number',
            delta=8.7,
            variant='primary'
        )

    with col4:
        kpi_card(
            title="Models Online",
            value=healthy_count,
            format_type='number',
            delta=0,
            variant='success'
        )

    st.divider()

    # Agent performance breakdown
    st.markdown("### 🤖 Agent Performance Breakdown")

    if agents:
        # Tier 1 agents
        tier1_agents = [a for a in agents if a.get('id', 0) <= 7]

        if tier1_agents:
            st.markdown("#### Tier 1: Core Detection Agents")
            plot_agent_performance(tier1_agents, "Core Detection Performance", 400)

        st.divider()

        # Tier 2 agents
        tier2_agents = [a for a in agents if 8 <= a.get('id', 0) <= 10]

        if tier2_agents:
            st.markdown("#### Tier 2: ML Intelligence Agents")

            for agent in tier2_agents:
                with card_container(
                    title=f"Agent {agent.get('id')}: {agent.get('name', 'Unknown')}",
                    icon="🧠",
                    variant='primary'
                ):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Success Rate",
                            f"{agent.get('success_rate', 0):.1f}%",
                            f"+{agent.get('success_rate', 0) - 95:.1f}%"
                        )

                    with col2:
                        st.metric(
                            "Avg Latency",
                            f"{agent.get('avg_latency_ms', 0):.0f}ms",
                            f"-{agent.get('avg_latency_ms', 0) * 0.1:.0f}ms"
                        )

                    with col3:
                        st.metric(
                            "Processed",
                            f"{agent.get('processed_count', 0):,}",
                            "+12.5%"
                        )

                    st.markdown("---")

                    st.markdown("**Description**")
                    st.write(agent.get('description', 'No description available'))

                    # Performance bar
                    st.markdown("**Performance Score**")
                    progress_bar_animated(
                        agent.get('success_rate', 0),
                        100,
                        show_percentage=True,
                        color='success'
                    )

    else:
        st.info("No agent metrics available")

    st.divider()

    # Feature importance
    st.markdown("### 📊 Feature Importance")

    with card_container("Top Features for Fraud Detection", "🎯", variant='primary'):
        features = [
            {'name': 'Transaction Amount', 'importance': 95},
            {'name': 'Merchant History', 'importance': 88},
            {'name': 'Time of Day', 'importance': 76},
            {'name': 'Geographic Location', 'importance': 72},
            {'name': 'User Behavior Pattern', 'importance': 68},
            {'name': 'Payment Method', 'importance': 55},
            {'name': 'Device Fingerprint', 'importance': 48},
            {'name': 'IP Address Reputation', 'importance': 42}
        ]

        for feature in features:
            st.markdown(f"**{feature['name']}**")
            progress_bar_animated(
                feature['importance'],
                100,
                show_percentage=True,
                color='primary'
            )

    st.divider()

    # Model statistics
    st.markdown("### 📈 Model Statistics")

    col1, col2 = st.columns(2)

    with col1:
        with card_container("Confusion Matrix", "📊", variant='default'):
            st.markdown("""
            **Last 1000 Predictions:**

            |              | Predicted Fraud | Predicted Legit |
            |--------------|----------------|----------------|
            | **Actual Fraud** | 142 (TP)       | 8 (FN)         |
            | **Actual Legit** | 12 (FP)        | 838 (TN)       |

            - **True Positive Rate:** 94.7%
            - **False Positive Rate:** 1.4%
            - **Precision:** 92.2%
            - **F1 Score:** 93.4%
            """)

    with col2:
        with card_container("Model Versions", "🔄", variant='info'):
            st.markdown("""
            **Current Models:**

            - **OCR Model:** Tesseract 5.3.0
            - **NLP Model:** Claude Sonnet 4
            - **Fraud Detection:** XGBoost v2.0
            - **Anomaly Detection:** Isolation Forest
            - **Risk Scoring:** Custom Ensemble

            **Last Updated:** 2026-02-15
            """)

    st.divider()

    # Training & optimization
    st.markdown("### 🔧 Model Training & Optimization")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Retrain Models", use_container_width=True, type="primary"):
            st.info("Model retraining scheduled. This will take ~30 minutes.")

    with col2:
        if st.button("📊 View Training History", use_container_width=True):
            st.info("Training history viewer coming soon!")

    with col3:
        if st.button("⚙️ Hyperparameter Tuning", use_container_width=True):
            st.info("Hyperparameter optimization interface coming soon!")
    except Exception as e:
        import traceback
        st.error(f"Error in ML_Insights: {e}")
        st.code(traceback.format_exc())


def _page_Security():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
    from components.widgets import (
        alert_box,
        success_box,
        error_box,
        warning_box,
        card_container,
        timeline_item,
        status_badge
    )
    from components.metrics import metric_card_group
    from services.api_client import get_api_client
    from utils.validators import detect_sql_injection, detect_xss, detect_path_traversal
    import logging

    logger = logging.getLogger(__name__)

    # Page header
    st.markdown('<h1 class="main-header">🛡️ Security Center</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Security monitoring and attack simulation</p>', unsafe_allow_html=True)

    # Security overview
    st.markdown("### 📊 Security Overview")

    metric_card_group([
        {'title': 'Attacks Blocked Today', 'value': '247', 'delta': '+12%'},
        {'title': 'SQL Injection Attempts', 'value': '89', 'delta': '+5%'},
        {'title': 'XSS Attempts', 'value': '134', 'delta': '+8%'},
        {'title': 'Path Traversal', 'value': '24', 'delta': '-3%'}
    ])

    st.divider()

    # Recent security events
    st.markdown("### 🚨 Recent Security Events")

    with card_container("Security Timeline", "🕐", variant='danger'):
        events = [
            {
                'title': 'SQL Injection Blocked',
                'description': 'Malicious query detected in search field',
                'timestamp': '2 minutes ago',
                'severity': 'HIGH'
            },
            {
                'title': 'XSS Attempt Blocked',
                'description': 'Script tag detected in user input',
                'timestamp': '15 minutes ago',
                'severity': 'HIGH'
            },
            {
                'title': 'Path Traversal Blocked',
                'description': '../../../etc/passwd in file upload',
                'timestamp': '1 hour ago',
                'severity': 'CRITICAL'
            },
            {
                'title': 'Brute Force Detected',
                'description': '50 failed login attempts from 192.168.1.100',
                'timestamp': '3 hours ago',
                'severity': 'HIGH'
            }
        ]

        for event in events:
            timeline_item(
                title=event['title'],
                description=event['description'],
                timestamp=event['timestamp'],
                status='error' if event['severity'] in ['CRITICAL', 'HIGH'] else 'warning'
            )

    st.divider()

    # Attack simulation demo
    st.markdown("### 🎭 Attack Simulation Demo")

    alert_box(
        "⚠️ **Educational Purpose Only** - This demo shows how our security layer blocks common attacks. "
        "All simulated attacks are safely contained and logged.",
        "warning"
    )

    tab1, tab2, tab3 = st.tabs(["SQL Injection", "XSS", "Path Traversal"])

    with tab1:
        st.markdown("#### 🗃️ SQL Injection Demo")

        st.markdown("""
        SQL Injection attacks attempt to manipulate database queries through user input.
        Try entering malicious SQL in the field below to see how our system blocks it.
        """)

        sql_input = st.text_area(
            "Enter SQL payload to test:",
            value="' OR '1'='1",
            help="Try: ' OR '1'='1, admin'--, 1'; DROP TABLE users--"
        )

        if st.button("🧪 Test SQL Injection", key="test_sql"):
            is_attack, patterns = detect_sql_injection(sql_input)

            if is_attack:
                error_box(f"🚫 **SQL INJECTION DETECTED!** Patterns found: {', '.join(patterns)}")
                st.code(f"Blocked payload: {sql_input}", language="sql")

                # Log to backend
                    client = get_api_client()
                    result = client.test_attack('sql_injection', sql_input)
                    if result.get('success'):
                        success_box("✅ Attack logged and blocked by backend")
                except:
                    pass
            else:
                success_box("✅ Input is safe - no SQL injection detected")

    with tab2:
        st.markdown("#### 💉 XSS (Cross-Site Scripting) Demo")

        st.markdown("""
        XSS attacks inject malicious scripts into web pages.
        Try entering JavaScript code to see how our sanitization works.
        """)

        xss_input = st.text_area(
            "Enter XSS payload to test:",
            value="<script>alert('XSS')</script>",
            help="Try: <script>alert('XSS')</script>, <img src=x onerror=alert(1)>"
        )

        if st.button("🧪 Test XSS", key="test_xss"):
            is_attack, patterns = detect_xss(xss_input)

            if is_attack:
                error_box(f"🚫 **XSS DETECTED!** Patterns found: {', '.join(patterns)}")
                st.code(f"Blocked payload: {xss_input}", language="html")

                # Show sanitized version
                from utils.validators import sanitize_string
                sanitized = sanitize_string(xss_input)
                st.markdown("**Sanitized output:**")
                st.code(sanitized, language="html")
            else:
                success_box("✅ Input is safe - no XSS detected")

    with tab3:
        st.markdown("#### 📁 Path Traversal Demo")

        st.markdown("""
        Path Traversal attacks try to access files outside allowed directories.
        Try entering a malicious path to see how it's blocked.
        """)

        path_input = st.text_input(
            "Enter file path to test:",
            value="../../../etc/passwd",
            help="Try: ../../../etc/passwd, ..\\windows\\system32"
        )

        if st.button("🧪 Test Path Traversal", key="test_path"):
            is_attack, patterns = detect_path_traversal(path_input)

            if is_attack:
                error_box(f"🚫 **PATH TRAVERSAL DETECTED!** Patterns found: {', '.join(patterns)}")
                st.code(f"Blocked path: {path_input}")
            else:
                success_box("✅ Path is safe - no traversal detected")

    st.divider()

    # Security best practices
    st.markdown("### 📚 Security Best Practices")

    with st.expander("🔒 Input Validation", expanded=False):
        st.markdown("""
        **Our Approach:**
        - ✅ Whitelist validation (allow known good)
        - ✅ Server-side validation (never trust client)
        - ✅ Parameterized queries (SQL injection prevention)
        - ✅ Content Security Policy headers
        - ✅ HTML entity encoding (XSS prevention)
        """)

    with st.expander("🛡️ Authentication & Authorization", expanded=False):
        st.markdown("""
        **Security Measures:**
        - ✅ AWS Cognito for authentication
        - ✅ JWT tokens with short expiry
        - ✅ Role-based access control (RBAC)
        - ✅ MFA support
        - ✅ Session management
        """)

    with st.expander("🔐 Data Protection", expanded=False):
        st.markdown("""
        **Encryption:**
        - ✅ TLS 1.3 for data in transit
        - ✅ AES-256 for data at rest
        - ✅ AWS KMS for key management
        - ✅ PII detection and masking
        - ✅ Secure file storage
        """)

    with st.expander("📊 Monitoring & Logging", expanded=False):
        st.markdown("""
        **Observability:**
        - ✅ Real-time attack detection
        - ✅ Comprehensive audit logs
        - ✅ CloudWatch integration
        - ✅ X-Ray distributed tracing
        - ✅ Automated alerting
        """)
    except Exception as e:
        import traceback
        st.error(f"Error in Security: {e}")
        st.code(traceback.format_exc())


def _page_Observability():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
    from components.widgets import (
        alert_box,
        card_container,
        timeline_item,
        data_table,
        empty_state,
        progress_bar_animated
    )
    from components.metrics import metric_card_group, kpi_card
    from services.data_provider import get_data_provider
    from utils.helpers import format_number
    import logging
    import random

    logger = logging.getLogger(__name__)

    # Page header
    st.markdown('<h1 class="main-header">📈 Observability & Monitoring</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">X-Ray traces and performance monitoring</p>', unsafe_allow_html=True)

    # Check backend
    provider = get_data_provider()
    if not provider.backend_available:
        alert_box("⚠️ Backend unavailable. Showing demo observability data.", "warning")

    # Load traces
    with st.spinner("Loading traces..."):
            traces = provider.get_xray_traces(limit=10)
        except Exception as e:
            logger.error(f"Error loading traces: {e}")
            traces = []

    # System health overview
    st.markdown("### 🏥 System Health")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        kpi_card(
            title="System Uptime",
            value=99.95,
            format_type='percentage',
            delta=0.02,
            target=99.9,
            variant='success'
        )

    with col2:
        kpi_card(
            title="Avg Response Time",
            value=245,
            format_type='number',
            delta=-12.5,
            variant='primary'
        )

    with col3:
        kpi_card(
            title="Error Rate",
            value=0.15,
            format_type='percentage',
            delta=-0.05,
            variant='success'
        )

    with col4:
        kpi_card(
            title="Active Requests",
            value=42,
            format_type='number',
            delta=5,
            variant='primary'
        )

    st.divider()

    # Performance metrics
    st.markdown("### ⚡ Performance Metrics")

    metric_card_group([
        {'title': 'P50 Latency', 'value': '187ms', 'delta': '-8ms'},
        {'title': 'P95 Latency', 'value': '534ms', 'delta': '-15ms'},
        {'title': 'P99 Latency', 'value': '1.2s', 'delta': '-200ms'},
        {'title': 'Throughput', 'value': '450/min', 'delta': '+25/min'}
    ])

    st.divider()

    # X-Ray traces
    st.markdown("### 🔍 Recent X-Ray Traces")

    if not traces:
        empty_state(
            message="No traces available",
            icon="📊",
            action_text="Refresh",
            action_callback=lambda: st.rerun()
        )
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.selectbox(
                "Status",
                options=['All', 'SUCCESS', 'ERROR', 'TIMEOUT'],
                index=0
            )

        with col2:
            min_duration = st.number_input(
                "Min Duration (ms)",
                min_value=0,
                value=0,
                step=100
            )

        with col3:
            max_traces = st.slider(
                "Show traces",
                min_value=5,
                max_value=50,
                value=10
            )

        # Display traces
        for i, trace in enumerate(traces[:max_traces]):
            trace_id = trace.get('id', f'TRACE-{i}')
            timestamp = trace.get('timestamp', '')
            duration = trace.get('duration', 0)
            status = trace.get('status', 'UNKNOWN')
            segments = trace.get('segments', [])

            # Apply filters
            if status_filter != 'All' and status != status_filter:
                continue

            if duration < min_duration:
                continue

            variant = 'success' if status == 'SUCCESS' else 'danger'

            with st.expander(
                f"{'✅' if status == 'SUCCESS' else '❌'} {trace_id} - {duration}ms - {timestamp}",
                expanded=False
            ):
                # Trace summary
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Duration", f"{duration}ms")

                with col2:
                    st.metric("Segments", len(segments))

                with col3:
                    st.metric("Status", status)

                st.markdown("---")

                # Segment breakdown
                st.markdown("**Segment Timeline**")

                if segments:
                    for segment in segments:
                        seg_name = segment.get('name', 'Unknown')
                        seg_duration = segment.get('duration', 0)
                        seg_status = segment.get('status', 'OK')

                        # Calculate percentage of total
                        percentage = (seg_duration / duration * 100) if duration > 0 else 0

                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"**{seg_name}** - {seg_duration}ms")
                            progress_bar_animated(
                                percentage,
                                100,
                                show_percentage=False,
                                color='success' if seg_status == 'OK' else 'danger'
                            )

                        with col2:
                            st.markdown(f"{percentage:.1f}%")

                else:
                    st.info("No segment data available")

                # HTTP details
                http_method = trace.get('http_method', 'POST')
                http_status = trace.get('http_status', 200)
                url = trace.get('url', '/api/analyze')

                st.markdown("---")
                st.markdown("**Request Details**")
                st.code(f"{http_method} {url} - HTTP {http_status}")

    st.divider()

    # CloudWatch integration
    st.markdown("### ☁️ CloudWatch Metrics")

    tab1, tab2, tab3 = st.tabs(["API Gateway", "Lambda", "Database"])

    with tab1:
        with card_container("API Gateway Metrics", "🌐", variant='primary'):
            st.markdown("**Request Metrics (Last 1 Hour)**")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Requests", "4,523", "+12%")

            with col2:
                st.metric("4xx Errors", "23", "-5%")

            with col3:
                st.metric("5xx Errors", "7", "-2")

            st.markdown("---")

            # Mock chart data
            import pandas as pd
            import plotly.graph_objects as go

            times = pd.date_range(end=pd.Timestamp.now(), periods=12, freq='5T')
            requests = [random.randint(350, 450) for _ in range(12)]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=requests,
                mode='lines+markers',
                name='Requests/5min',
                line=dict(color='#4A9EFF', width=3)
            ))

            fig.update_layout(
                title='Request Volume',
                xaxis_title='Time',
                yaxis_title='Requests',
                height=300,
                template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with card_container("Lambda Metrics", "λ", variant='warning'):
            st.markdown("**Function Performance (Last 1 Hour)**")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Invocations", "3,892", "+8%")

            with col2:
                st.metric("Avg Duration", "2.3s", "-200ms")

            with col3:
                st.metric("Errors", "12", "-3")

            st.markdown("---")

            # Mock duration chart
            durations = [random.randint(1800, 2800) for _ in range(12)]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=durations,
                mode='lines+markers',
                name='Duration (ms)',
                line=dict(color='#ffab00', width=3)
            ))

            fig.update_layout(
                title='Function Duration',
                xaxis_title='Time',
                yaxis_title='Duration (ms)',
                height=300,
                template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        with card_container("Database Metrics", "🗄️", variant='success'):
            st.markdown("**RDS Performance (Last 1 Hour)**")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("CPU Usage", "42%", "-8%")

            with col2:
                st.metric("Connections", "28", "+3")

            with col3:
                st.metric("Query Time", "15ms", "-2ms")

            st.markdown("---")

            # Mock connection chart
            connections = [random.randint(20, 35) for _ in range(12)]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times,
                y=connections,
                mode='lines+markers',
                name='Active Connections',
                line=dict(color='#00d68f', width=3)
            ))

            fig.update_layout(
                title='Database Connections',
                xaxis_title='Time',
                yaxis_title='Connections',
                height=300,
                template='plotly_dark' if st.session_state.get('theme') == 'dark' else 'plotly_white'
            )

            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Alerts & anomalies
    st.markdown("### 🚨 Alerts & Anomalies")

    with card_container("Recent Alerts", "⚠️", variant='warning'):
        alerts = [
            {
                'title': 'High Latency Detected',
                'description': 'P99 latency exceeded 2s threshold',
                'timestamp': '5 minutes ago',
                'severity': 'WARNING'
            },
            {
                'title': 'Database Connection Pool Near Limit',
                'description': '45/50 connections in use',
                'timestamp': '15 minutes ago',
                'severity': 'WARNING'
            },
            {
                'title': 'Error Rate Spike',
                'description': '5xx errors increased by 50%',
                'timestamp': '1 hour ago',
                'severity': 'HIGH'
            }
        ]

        for alert in alerts:
            timeline_item(
                title=alert['title'],
                description=alert['description'],
                timestamp=alert['timestamp'],
                status='warning' if alert['severity'] == 'WARNING' else 'error'
            )
    except Exception as e:
        import traceback
        st.error(f"Error in Observability: {e}")
        st.code(traceback.format_exc())


def _page_Merchant():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
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
    except Exception as e:
        import traceback
        st.error(f"Error in Merchant: {e}")
        st.code(traceback.format_exc())


def _page_Integrations():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
    from components.widgets import (
        alert_box,
        success_box,
        card_container,
        status_badge,
        empty_state
    )
    from components.metrics import metric_card_group
    import logging

    logger = logging.getLogger(__name__)

    # Page header
    st.markdown('<h1 class="main-header">🔗 Integrations</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage external service connections</p>', unsafe_allow_html=True)

    # Integration overview
    st.markdown("### 📊 Integration Status")

    metric_card_group([
        {'title': 'Active Integrations', 'value': '8', 'delta': '+2 this month'},
        {'title': 'API Calls Today', 'value': '12,547', 'delta': '+8.3%'},
        {'title': 'Success Rate', 'value': '99.2%', 'delta': '+0.5%'},
        {'title': 'Avg Response Time', 'value': '245ms', 'delta': '-12ms'}
    ])

    st.divider()

    # Available integrations
    st.markdown("### 🔌 Available Integrations")

    integrations = [
        {
            'name': 'AWS Cognito',
            'description': 'User authentication and authorization',
            'category': 'Authentication',
            'status': 'Connected',
            'icon': '🔐',
            'last_sync': '2 minutes ago'
        },
        {
            'name': 'AWS S3',
            'description': 'File storage and document management',
            'category': 'Storage',
            'status': 'Connected',
            'icon': '📦',
            'last_sync': '5 minutes ago'
        },
        {
            'name': 'AWS RDS PostgreSQL',
            'description': 'Primary database for invoice data',
            'category': 'Database',
            'status': 'Connected',
            'icon': '🗄️',
            'last_sync': '1 minute ago'
        },
        {
            'name': 'AWS X-Ray',
            'description': 'Distributed tracing and monitoring',
            'category': 'Observability',
            'status': 'Connected',
            'icon': '📈',
            'last_sync': '30 seconds ago'
        },
        {
            'name': 'AWS CloudWatch',
            'description': 'Logging and metrics collection',
            'category': 'Observability',
            'status': 'Connected',
            'icon': '☁️',
            'last_sync': '1 minute ago'
        },
        {
            'name': 'Slack',
            'description': 'Team notifications and alerts',
            'category': 'Communication',
            'status': 'Not Connected',
            'icon': '💬',
            'last_sync': 'Never'
        },
        {
            'name': 'PagerDuty',
            'description': 'Incident management and alerting',
            'category': 'Alerting',
            'status': 'Not Connected',
            'icon': '🚨',
            'last_sync': 'Never'
        },
        {
            'name': 'Datadog',
            'description': 'Advanced monitoring and APM',
            'category': 'Observability',
            'status': 'Not Connected',
            'icon': '🐶',
            'last_sync': 'Never'
        },
        {
            'name': 'Stripe',
            'description': 'Payment processing integration',
            'category': 'Payments',
            'status': 'Not Connected',
            'icon': '💳',
            'last_sync': 'Never'
        },
        {
            'name': 'SendGrid',
            'description': 'Email notifications',
            'category': 'Communication',
            'status': 'Not Connected',
            'icon': '📧',
            'last_sync': 'Never'
        }
    ]

    # Category filter
    categories = ['All'] + list(set(i['category'] for i in integrations))
    selected_category = st.selectbox("Filter by category", categories, index=0)

    # Filter integrations
    filtered = integrations if selected_category == 'All' else [
        i for i in integrations if i['category'] == selected_category
    ]

    # Display integrations
    for integration in filtered:
        status = integration['status']
        is_connected = status == 'Connected'
        variant = 'success' if is_connected else 'default'

        with card_container(
            title=f"{integration['icon']} {integration['name']}",
            variant=variant
        ):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{integration['description']}**")
                st.markdown(f"Category: {integration['category']}")
                st.markdown(f"Last sync: {integration['last_sync']}")

            with col2:
                status_badge(
                    status,
                    'success' if is_connected else 'info'
                )

            st.markdown("---")

            col1, col2, col3 = st.columns(3)

            with col1:
                if is_connected:
                    if st.button("⚙️ Configure", key=f"config_{integration['name']}", use_container_width=True):
                        st.info(f"Configuration for {integration['name']}")
                else:
                    if st.button("➕ Connect", key=f"connect_{integration['name']}", use_container_width=True, type="primary"):
                        st.success(f"Connecting to {integration['name']}...")

            with col2:
                if is_connected:
                    if st.button("🔄 Sync Now", key=f"sync_{integration['name']}", use_container_width=True):
                        st.success(f"Syncing {integration['name']}...")
                else:
                    if st.button("📖 Learn More", key=f"learn_{integration['name']}", use_container_width=True):
                        st.info(f"Opening documentation for {integration['name']}...")

            with col3:
                if is_connected:
                    if st.button("🔌 Disconnect", key=f"disconnect_{integration['name']}", use_container_width=True):
                        st.warning(f"Disconnecting from {integration['name']}...")
                else:
                    st.write("")  # Empty space

    st.divider()

    # Webhooks
    st.markdown("### 🪝 Webhooks")

    with card_container("Webhook Configuration", "⚡", variant='primary'):
        st.markdown("""
        Configure webhooks to receive real-time notifications about events.

        **Available Events:**
        - 🔔 Invoice Processed
        - 🚨 Fraud Detected
        - ✅ Invoice Approved
        - 🚫 Invoice Blocked
        - ⚠️ High Risk Detected
        """)

        webhook_url = st.text_input(
            "Webhook URL",
            placeholder="https://your-domain.com/webhook",
            help="POST requests will be sent to this URL"
        )

        events = st.multiselect(
            "Subscribe to events",
            options=[
                'invoice.processed',
                'fraud.detected',
                'invoice.approved',
                'invoice.blocked',
                'risk.high'
            ],
            default=['fraud.detected', 'risk.high']
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Save Webhook", use_container_width=True, type="primary"):
                if webhook_url:
                    success_box("✅ Webhook configured successfully!")
                else:
                    alert_box("⚠️ Please enter a webhook URL", "warning")

        with col2:
            if st.button("🧪 Test Webhook", use_container_width=True):
                if webhook_url:
                    st.info("Sending test payload to webhook...")
                else:
                    alert_box("⚠️ Please enter a webhook URL", "warning")

    st.divider()

    # API keys
    st.markdown("### 🔑 API Keys")

    with card_container("API Key Management", "🔐", variant='warning'):
        st.markdown("""
        Generate API keys for programmatic access to AgentFlow.

        **Permissions:**
        - 📖 Read-only access
        - 📝 Write access
        - 🔧 Admin access
        """)

        if st.button("➕ Generate New API Key", type="primary"):
            import secrets
            api_key = f"agf_{secrets.token_hex(16)}"
            st.code(api_key, language="text")
            st.warning("⚠️ Save this key securely. It won't be shown again.")

        st.markdown("---")

        st.markdown("**Active API Keys:**")

        api_keys = [
            {'name': 'Production Key', 'created': '2026-01-15', 'last_used': '2 hours ago', 'permissions': 'Read/Write'},
            {'name': 'Development Key', 'created': '2026-02-01', 'last_used': '5 minutes ago', 'permissions': 'Read-only'},
        ]

        for key in api_keys:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])

            with col1:
                st.text(key['name'])

            with col2:
                st.text(f"Created: {key['created']}")

            with col3:
                st.text(f"Last used: {key['last_used']}")

            with col4:
                st.text(key['permissions'])

            with col5:
                if st.button("🗑️", key=f"delete_{key['name']}"):
                    st.warning(f"Revoked {key['name']}")
    except Exception as e:
        import traceback
        st.error(f"Error in Integrations: {e}")
        st.code(traceback.format_exc())


def _page_Settings():
    try:
    st.sidebar.error(f"Sidebar error: {_e}")
    from components.widgets import (
        success_box,
        warning_box,
        card_container,
        alert_box
    )
    from auth.login import logout
    import logging

    logger = logging.getLogger(__name__)

    # Page header
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Manage your account and preferences</p>', unsafe_allow_html=True)

    # Settings tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👤 Profile",
        "🎨 Appearance",
        "🔔 Notifications",
        "🔐 Security",
        "🌐 Advanced"
    ])

    with tab1:
        st.markdown("### 👤 Profile Settings")

        with card_container("User Information", "ℹ️", variant='primary'):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "Full Name",
                    value=st.session_state.get('user_name', 'Admin User')
                )

                email = st.text_input(
                    "Email",
                    value=st.session_state.get('user_email', 'admin@agentflow.ai'),
                    disabled=True,
                    help="Email cannot be changed"
                )

            with col2:
                role = st.text_input(
                    "Role",
                    value=(st.session_state.get('user_role') or 'viewer').title(),
                    disabled=True,
                    help="Role is assigned by administrators"
                )

                timezone = st.selectbox(
                    "Timezone",
                    options=['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo'],
                    index=0
                )

            language = st.selectbox(
                "Language",
                options=['English', 'Vietnamese', 'Spanish', 'French'],
                index=0
            )

            if st.button("💾 Save Profile", type="primary"):
                st.session_state.user_name = name
                success_box("✅ Profile updated successfully!")

    with tab2:
        st.markdown("### 🎨 Appearance Settings")

        with card_container("Theme", "🌓", variant='primary'):
            current_theme = st.session_state.get('theme', 'dark')

            theme_option = st.radio(
                "Select Theme",
                options=['dark', 'light'],
                format_func=lambda x: '🌙 Dark Mode' if x == 'dark' else '☀️ Light Mode',
                index=0 if current_theme == 'dark' else 1,
                horizontal=True
            )

            if theme_option != current_theme:
                if st.button("Apply Theme", type="primary"):
                    st.session_state.theme = theme_option
                    success_box(f"✅ Switched to {theme_option} theme!")
                    st.rerun()

        with card_container("Display Options", "👁️", variant='default'):
            compact_mode = st.checkbox("Compact Mode", value=False, help="Reduce spacing for more content")
            show_animations = st.checkbox("Enable Animations", value=True)
            show_tooltips = st.checkbox("Show Tooltips", value=True)

            if st.button("💾 Save Display Settings"):
                success_box("✅ Display settings saved!")

    with tab3:
        st.markdown("### 🔔 Notification Settings")

        with card_container("Email Notifications", "📧", variant='info'):
            st.markdown("**Receive email notifications for:**")

            email_fraud_alerts = st.checkbox("🚨 Fraud Alerts", value=True)
            email_high_risk = st.checkbox("⚠️ High Risk Invoices", value=True)
            email_system_updates = st.checkbox("🔄 System Updates", value=False)
            email_weekly_report = st.checkbox("📊 Weekly Reports", value=True)

            email_frequency = st.selectbox(
                "Email Frequency",
                options=['Immediate', 'Daily Digest', 'Weekly Digest'],
                index=0
            )

        with card_container("In-App Notifications", "🔔", variant='info'):
            st.markdown("**Show in-app notifications for:**")

            app_fraud_detected = st.checkbox("🚨 Fraud Detected", value=True, key="app_fraud")
            app_processing_complete = st.checkbox("✅ Processing Complete", value=True, key="app_complete")
            app_system_alerts = st.checkbox("⚠️ System Alerts", value=True, key="app_alerts")

        if st.button("💾 Save Notification Settings", type="primary"):
            success_box("✅ Notification preferences saved!")

    with tab4:
        st.markdown("### 🔐 Security Settings")

        with card_container("Change Password", "🔑", variant='warning'):
            st.markdown("Update your password to keep your account secure.")

            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")

            if st.button("🔒 Change Password", type="primary"):
                if not current_password or not new_password or not confirm_password:
                    warning_box("⚠️ Please fill in all password fields")
                elif new_password != confirm_password:
                    warning_box("⚠️ New passwords don't match")
                elif len(new_password) < 8:
                    warning_box("⚠️ Password must be at least 8 characters")
                else:
                    success_box("✅ Password changed successfully!")

        with card_container("Two-Factor Authentication", "🔐", variant='success'):
            mfa_enabled = st.session_state.get('mfa_enabled', False)

            st.markdown(f"**Status:** {'✅ Enabled' if mfa_enabled else '❌ Disabled'}")

            if not mfa_enabled:
                st.markdown("""
                Two-factor authentication adds an extra layer of security to your account.
                You'll need your password and a verification code to sign in.
                """)

                if st.button("🔐 Enable 2FA", type="primary"):
                    st.session_state.mfa_enabled = True
                    success_box("✅ 2FA enabled! Scan this QR code with your authenticator app:")
                    st.image("https://via.placeholder.com/200x200?text=QR+Code", width=200)
            else:
                st.markdown("Two-factor authentication is currently enabled for your account.")

                if st.button("🔓 Disable 2FA"):
                    st.session_state.mfa_enabled = False
                    warning_box("⚠️ 2FA has been disabled")

        with card_container("Active Sessions", "📱", variant='default'):
            st.markdown("**Current Sessions:**")

            sessions = [
                {'device': 'Chrome on Windows', 'location': 'Pleiku, VN', 'last_active': 'Now'},
                {'device': 'Safari on iPhone', 'location': 'Pleiku, VN', 'last_active': '2 hours ago'},
            ]

            for i, session in enumerate(sessions):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"""
                    **{session['device']}**  
                    {session['location']} • {session['last_active']}
                    """)

                with col2:
                    if session['last_active'] != 'Now':
                        if st.button("🚫 Revoke", key=f"revoke_{i}"):
                            success_box(f"✅ Session revoked")

    with tab5:
        st.markdown("### 🌐 Advanced Settings")

        with card_container("Developer Options", "🔧", variant='warning'):
            st.markdown("**API Access:**")

            enable_api = st.checkbox("Enable API Access", value=True)

            if enable_api:
                st.code("API Endpoint: https://api.agentflow.ai/v1", language="text")
                st.code(f"API Key: agf_{st.session_state.get('user_email', 'user').split('@')[0]}_***", language="text")

                if st.button("🔄 Regenerate API Key"):
                    success_box("✅ New API key generated!")

        with card_container("Data & Privacy", "🔒", variant='info'):
            st.markdown("**Data Management:**")

            if st.button("📥 Export My Data"):
                st.info("Data export will be emailed to you within 24 hours")

            if st.button("🗑️ Delete My Account", type="secondary"):
                st.error("⚠️ This action cannot be undone!")

                confirm = st.checkbox("I understand that deleting my account is permanent")

                if confirm:
                    if st.button("⚠️ Confirm Deletion"):
                        alert_box("Account deletion requested. You will be logged out.", "error")

        with card_container("System Information", "ℹ️", variant='default'):
            st.markdown(f"""
            **Frontend Version:** {st.session_state.get('app_version', '3.1.0')}  
            **Backend Version:** 3.1.0  
            **Last Updated:** 2026-02-24  
            **Build:** production  
            **Region:** ap-southeast-1
            """)

    st.divider()

    # Danger zone
    st.markdown("### ⚠️ Danger Zone")

    with card_container("Logout & Reset", "🚪", variant='danger'):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                logout()
                st.rerun()

        with col2:
            if st.button("🔄 Reset All Settings", use_container_width=True):
                st.warning("⚠️ All settings will be reset to defaults")
    except Exception as e:
        import traceback
        st.error(f"Error in Settings: {e}")
        st.code(traceback.format_exc())


    routers = {
        "Overview": _page_Overview,
        "Upload": _page_Upload,
        "Fraud": _page_Fraud,
        "ML_Insights": _page_ML_Insights,
        "Security": _page_Security,
        "Observability": _page_Observability,
        "Merchant": _page_Merchant,
        "Integrations": _page_Integrations,
        "Settings": _page_Settings,
    }
    fn = routers.get(page_key, _page_Overview)
    fn()

# ─── Main ──────────────────────────────────────────────────
if not st.session_state.logged_in:
    from auth.login import login_page
    login_page()
else:
    render_sidebar()
    show_page(st.session_state.page)
