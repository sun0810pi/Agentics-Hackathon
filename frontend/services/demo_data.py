import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
import streamlit as st
from config import config
from utils.constants import *


# ── Fallback agent catalog (used when config.AGENTS not defined) ──────────
_AGENTS_FALLBACK = {
    0:  {'name': 'InvoiceValidator',      'tier': 'Core Detection',   'description': 'Validates invoice structure'},
    1:  {'name': 'VendorVerifier',        'tier': 'Core Detection',   'description': 'Verifies vendor legitimacy'},
    2:  {'name': 'DuplicateDetector',     'tier': 'Core Detection',   'description': 'Detects duplicate invoices'},
    3:  {'name': 'AmountAnalyzer',        'tier': 'Core Detection',   'description': 'Analyzes amount anomalies'},
    4:  {'name': 'PatternMatcher',        'tier': 'Core Detection',   'description': 'Matches fraud patterns'},
    5:  {'name': 'TimingAnalyzer',        'tier': 'Core Detection',   'description': 'Analyzes submission timing'},
    6:  {'name': 'GeoLocationChecker',   'tier': 'Core Detection',   'description': 'Checks geographic data'},
    7:  {'name': 'ComplianceChecker',    'tier': 'Core Detection',   'description': 'Ensures regulatory compliance'},
    8:  {'name': 'MLRiskScorer',          'tier': 'ML Intelligence',  'description': 'ML-based risk scoring'},
    9:  {'name': 'AnomalyDetector',       'tier': 'ML Intelligence',  'description': 'Detects statistical anomalies'},
    10: {'name': 'BehaviorAnalyzer',      'tier': 'ML Intelligence',  'description': 'Analyzes behavioral patterns'},
    11: {'name': 'MerchantProfiler',      'tier': 'Merchant Success', 'description': 'Profiles merchant behavior'},
    12: {'name': 'TransactionAnalyzer',   'tier': 'Merchant Success', 'description': 'Analyzes transaction history'},
    13: {'name': 'RiskAggregator',        'tier': 'Merchant Success', 'description': 'Aggregates risk signals'},
    14: {'name': 'ThreatIntelligence',    'tier': 'Security',         'description': 'Threat intelligence lookup'},
    15: {'name': 'IdentityVerifier',      'tier': 'Security',         'description': 'Identity verification'},
    16: {'name': 'FraudNetworkMapper',    'tier': 'Security',         'description': 'Maps fraud networks'},
}

def _get_agents():
    try:
        from config import config
        return config.AGENTS
    except AttributeError:
        return _AGENTS_FALLBACK


class DemoDataGenerator:
    """
    Generates realistic demo data for testing and presentation
    
    All data is randomly generated but follows realistic patterns:
    - Risk scores follow normal distribution
    - Timestamps are realistic
    - Amounts follow business patterns
    - Fraud scenarios are plausible
    """
    
    def __init__(self):
        """Initialize demo data generator"""
        self.companies = [
            "Tech Solutions Inc", "Global Logistics Ltd", "Retail Express",
            "Manufacturing Co", "Healthcare Systems", "Finance Group",
            "Energy Corp", "Telecom Networks", "Media Publishing",
            "Construction Partners", "Food & Beverage Co", "Auto Parts Ltd",
            "Software House", "Consulting Firm", "Real Estate Group"
        ]
        
        self.merchants = [
            "Amazon Web Services", "Microsoft Azure", "Google Cloud",
            "Salesforce", "Adobe Creative Cloud", "Slack",
            "Zoom Video", "Dropbox", "GitHub",
            "Atlassian", "Shopify", "Stripe",
            "HubSpot", "Mailchimp", "Zendesk"
        ]
        
        self.fraud_types = [
            "Duplicate Payment", "Vendor Impersonation", "Invoice Manipulation",
            "Ghost Vendor", "Price Inflation", "Quantity Mismatch",
            "Unauthorized Purchase", "Split Transaction", "Kickback Scheme",
            "Shell Company", "Round Amount Pattern", "Weekend Transaction"
        ]
        
        # Seed for consistent demo data in same session
        if 'demo_seed' not in st.session_state:
            st.session_state.demo_seed = random.randint(1, 1000000)
    
    def _get_random_date(self, days_ago: int = 30) -> datetime:
        """Generate random date within last N days"""
        return datetime.now() - timedelta(
            days=random.randint(0, days_ago),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
    
    def _get_risk_score(self, bias: str = "normal") -> int:
        """
        Generate risk score with different distributions
        
        Args:
            bias: Distribution bias (low, normal, high)
            
        Returns:
            Risk score 0-100
        """
        if bias == "low":
            return random.randint(0, 40)
        elif bias == "high":
            return random.randint(60, 100)
        else:
            # Normal distribution around 30-40
            return int(random.gauss(35, 15))
    
    # =====================================================
    # DASHBOARD METRICS
    # =====================================================
    
    def generate_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Generate dashboard overview metrics
        
        Returns:
            Dict with all dashboard metrics
        """
        total_processed = random.randint(8500, 12000)
        approved = int(total_processed * random.uniform(0.75, 0.85))
        blocked = int(total_processed * random.uniform(0.05, 0.10))
        pending = total_processed - approved - blocked
        
        return {
            'total_processed': total_processed,
            'total_approved': approved,
            'total_blocked': blocked,
            'total_pending': pending,
            'accuracy': round(random.uniform(97.5, 99.8), 1),
            'automation_rate': round(random.uniform(92.0, 98.0), 1),
            'avg_latency_ms': random.randint(150, 350),
            'fraud_prevented_usd': random.randint(2500000, 5000000),
            'uptime_pct': round(random.uniform(99.5, 99.99), 2),
            'agents_active': 17,
            'agents_total': 17,
            'false_positive_rate': round(random.uniform(0.5, 2.0), 2),
            'processing_speed': random.randint(450, 850),  # invoices/hour
            'cost_savings_usd': random.randint(150000, 300000),
            'avg_risk_score': round(random.uniform(25, 35), 1)
        }
    
    # =====================================================
    # INVOICES
    # =====================================================
    
    def generate_invoices(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate list of invoices
        
        Args:
            count: Number of invoices to generate
            
        Returns:
            List of invoice dicts
        """
        invoices = []
        
        for i in range(count):
            # Determine status with realistic distribution
            status_roll = random.random()
            if status_roll < 0.80:
                status = STATUS_APPROVED
                risk_bias = "low"
            elif status_roll < 0.90:
                status = STATUS_PENDING
                risk_bias = "normal"
            else:
                status = STATUS_BLOCKED
                risk_bias = "high"
            
            risk_score = self._get_risk_score(risk_bias)
            
            # Generate amount (follows realistic business patterns)
            amount = self._generate_invoice_amount()
            
            invoice = {
                'id': f"INV-{random.randint(100000, 999999)}",
                'company': random.choice(self.companies),
                'merchant': random.choice(self.merchants),
                'amount': amount,
                'currency': random.choice([CURRENCY_USD, CURRENCY_EUR, CURRENCY_VND]),
                'status': status,
                'risk_score': risk_score,
                'confidence': round(random.uniform(0.85, 0.99), 2),
                'created_at': self._get_random_date(days_ago=60).isoformat(),
                'processed_at': self._get_random_date(days_ago=30).isoformat(),
                'processing_time_ms': random.randint(150, 800),
                'flags': self._generate_risk_flags(risk_score),
                'decision': self._get_decision_from_status(status)
            }
            
            invoices.append(invoice)
        
        # Sort by date (newest first)
        invoices.sort(key=lambda x: x['created_at'], reverse=True)
        
        return invoices
    
    def _generate_invoice_amount(self) -> float:
        """Generate realistic invoice amount"""
        # 70% are small amounts, 20% medium, 10% large
        roll = random.random()
        
        if roll < 0.70:
            # Small: $100 - $5,000
            return round(random.uniform(100, 5000), 2)
        elif roll < 0.90:
            # Medium: $5,000 - $50,000
            return round(random.uniform(5000, 50000), 2)
        else:
            # Large: $50,000 - $500,000
            return round(random.uniform(50000, 500000), 2)
    
    def _generate_risk_flags(self, risk_score: int) -> List[str]:
        """Generate risk flags based on score"""
        flags = []
        
        if risk_score > 70:
            flags.append("High Risk Amount")
            flags.append("Suspicious Pattern")
        elif risk_score > 50:
            flags.append("New Vendor")
            flags.append("Rush Payment Request")
        elif risk_score > 30:
            flags.append("Minor Inconsistency")
        
        # Add random specific flags
        possible_flags = [
            "Duplicate Detection",
            "Weekend Transaction",
            "After Hours",
            "Unusual Amount",
            "Multiple Invoices",
            "Changed Bank Details",
            "Round Amount"
        ]
        
        if random.random() < 0.3:
            flags.append(random.choice(possible_flags))
        
        return flags
    
    def _get_decision_from_status(self, status: str) -> str:
        """Get decision type from status"""
        if status == STATUS_APPROVED:
            return DECISION_APPROVE
        elif status == STATUS_BLOCKED:
            return DECISION_BLOCK
        else:
            return DECISION_REVIEW
    
    # =====================================================
    # FRAUD SCENARIOS
    # =====================================================
    
    def generate_fraud_scenarios(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate active fraud scenarios
        
        Args:
            count: Number of scenarios
            
        Returns:
            List of fraud scenario dicts
        """
        scenarios = []
        
        for i in range(count):
            severity_roll = random.random()
            if severity_roll < 0.3:
                severity = SEVERITY_CRITICAL
            elif severity_roll < 0.6:
                severity = SEVERITY_HIGH
            elif severity_roll < 0.85:
                severity = SEVERITY_MEDIUM
            else:
                severity = SEVERITY_LOW
            
            scenario = {
                'id': f"FRD-{random.randint(1000, 9999)}",
                'type': random.choice(self.fraud_types),
                'severity': severity,
                'status': random.choice(['Active', 'Investigating', 'Resolved']),
                'detected_at': self._get_random_date(days_ago=7).isoformat(),
                'affected_invoices': random.randint(1, 15),
                'potential_loss': random.randint(5000, 500000),
                'confidence': round(random.uniform(0.75, 0.98), 2),
                'description': self._generate_fraud_description()
            }
            
            scenarios.append(scenario)
        
        # Sort by severity and date
        severity_order = {
            SEVERITY_CRITICAL: 0,
            SEVERITY_HIGH: 1,
            SEVERITY_MEDIUM: 2,
            SEVERITY_LOW: 3
        }
        scenarios.sort(key=lambda x: (severity_order[x['severity']], x['detected_at']), reverse=True)
        
        return scenarios
    
    def _generate_fraud_description(self) -> str:
        """Generate fraud description"""
        descriptions = [
            "Multiple invoices from same vendor with sequential numbers detected",
            "Unusual payment pattern identified across multiple accounts",
            "Vendor information mismatch with external database records",
            "Suspicious timing of transactions outside business hours",
            "Amount manipulation detected in invoice line items",
            "Ghost vendor identified through cross-reference analysis",
            "Duplicate invoice submitted with different invoice numbers",
            "Price inflation detected compared to market rates",
            "Shell company identified through network analysis",
            "Round amount pattern suggesting potential fraud"
        ]
        return random.choice(descriptions)
    
    # =====================================================
    # AGENT METRICS
    # =====================================================
    
    def generate_agent_metrics(self) -> List[Dict[str, Any]]:
        """
        Generate performance metrics for all 17 agents
        
        Returns:
            List of agent metric dicts
        """
        agents = []
        
        for agent_id, agent_config in _get_agents().items():
            # Generate realistic metrics
            uptime = round(random.uniform(98.5, 99.99), 2)
            processed = random.randint(5000, 15000)
            
            agent = {
                'id': agent_id,
                'name': agent_config['name'],
                'tier': agent_config['tier'],
                'description': agent_config['description'],
                'status': 'active' if random.random() > 0.05 else 'degraded',
                'uptime': uptime,
                'processed_count': processed,
                'avg_latency_ms': random.randint(50, 500),
                'success_rate': round(random.uniform(96.0, 99.9), 1),
                'errors': random.randint(0, 50),
                'last_run': self._get_random_date(days_ago=1).isoformat()
            }
            
            agents.append(agent)
        
        return agents
    
    # =====================================================
    # TIME SERIES DATA
    # =====================================================
    
    def generate_time_series(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Generate time series data for charts
        
        Args:
            days: Number of days of data
            
        Returns:
            List of time series points
        """
        data = []
        base_processed = 300
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            
            # Add some realistic variation
            daily_processed = base_processed + random.randint(-50, 100)
            approved_rate = random.uniform(0.75, 0.85)
            blocked_rate = random.uniform(0.05, 0.10)
            
            point = {
                'date': date.strftime('%Y-%m-%d'),
                'processed': daily_processed,
                'approved': int(daily_processed * approved_rate),
                'blocked': int(daily_processed * blocked_rate),
                'pending': int(daily_processed * (1 - approved_rate - blocked_rate)),
                'avg_risk_score': round(random.uniform(25, 40), 1),
                'accuracy': round(random.uniform(97, 99.5), 1)
            }
            
            data.append(point)
        
        return data
    
    # =====================================================
    # AUDIT LOGS
    # =====================================================
    
    def generate_audit_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate audit log entries
        
        Args:
            count: Number of logs
            
        Returns:
            List of audit log dicts
        """
        actions = [
            'LOGIN', 'LOGOUT', 'VIEW_INVOICE', 'PROCESS_INVOICE',
            'APPROVE', 'BLOCK', 'REVIEW', 'SETTINGS_CHANGE',
            'DATA_EXPORT', 'USER_CREATE', 'USER_DELETE'
        ]
        
        users = [
            'admin@agentflow.ai',
            'analyst@agentflow.ai',
            'viewer@agentflow.ai',
            'manager@agentflow.ai'
        ]
        
        logs = []
        
        for i in range(count):
            log = {
                'id': f"LOG-{random.randint(100000, 999999)}",
                'timestamp': self._get_random_date(days_ago=7).isoformat(),
                'user': random.choice(users),
                'action': random.choice(actions),
                'resource': f"INV-{random.randint(100000, 999999)}" if random.random() > 0.3 else None,
                'ip_address': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'user_agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                    'Mozilla/5.0 (X11; Linux x86_64)'
                ]),
                'status': random.choice(['SUCCESS', 'SUCCESS', 'SUCCESS', 'FAILED'])
            }
            
            logs.append(log)
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return logs
    
    # =====================================================
    # X-RAY TRACES
    # =====================================================
    
    def generate_xray_traces(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate X-Ray distributed traces
        
        Args:
            count: Number of traces
            
        Returns:
            List of X-Ray trace dicts
        """
        traces = []
        
        for i in range(count):
            total_duration = random.randint(200, 2000)
            
            # Generate segments for each agent
            segments = []
            remaining_time = total_duration
            
            for agent_id in range(8):  # Tier 1 agents (sequential)
                duration = random.randint(20, 200)
                remaining_time -= duration
                
                segments.append({
                    'name': f'Agent {agent_id}',
                    'start_time': 0,  # Simplified
                    'duration': duration,
                    'status': 'OK' if random.random() > 0.05 else 'ERROR'
                })
            
            trace = {
                'id': f"TRACE-{random.randint(1000000, 9999999)}",
                'timestamp': self._get_random_date(days_ago=1).isoformat(),
                'duration': total_duration,
                'status': 'SUCCESS' if random.random() > 0.05 else 'ERROR',
                'segments': segments,
                'http_method': 'POST',
                'http_status': random.choice([200, 200, 200, 500, 429]),
                'url': '/api/analyze'
            }
            
            traces.append(trace)
        
        # Sort by timestamp (newest first)
        traces.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return traces
    
    # =====================================================
    # INVOICE PROCESSING SIMULATION
    # =====================================================
    
    def simulate_invoice_processing(
        self,
        filename: str,
        mode: str = "full"
    ) -> Dict[str, Any]:
        """
        Simulate invoice processing result
        
        Args:
            filename: Invoice filename
            mode: Processing mode (full, fast, demo)
            
        Returns:
            Processing result dict matching backend schema
        """
        # Determine outcome
        risk_roll = random.random()
        
        if risk_roll < 0.75:
            # Approved (75%)
            decision = DECISION_APPROVE
            risk_score = random.randint(0, 40)
        elif risk_roll < 0.90:
            # Review (15%)
            decision = DECISION_REVIEW
            risk_score = random.randint(40, 70)
        else:
            # Blocked (10%)
            decision = DECISION_BLOCK
            risk_score = random.randint(70, 100)
        
        # Generate agent results
        agent_results = []
        total_duration = 0
        
        for agent_id, agent_config in _get_agents().items():
            duration = random.randint(50, 300)
            total_duration += duration
            
            agent_result = {
                'agent_id': agent_id,
                'agent_name': agent_config['name'],
                'status': 'SUCCESS' if random.random() > 0.02 else 'ERROR',
                'duration': duration,
                'result': {
                    'risk_contribution': random.randint(0, 20),
                    'findings': random.randint(0, 3),
                    'confidence': round(random.uniform(0.85, 0.99), 2)
                },
                'timestamp': datetime.now().isoformat()
            }
            
            agent_results.append(agent_result)
        
        # Build complete result
        result = {
            'success': True,
            'invoice_id': f"INV-{random.randint(100000, 999999)}",
            'filename': filename,
            'decision': decision,
            'risk_score': risk_score,
            'confidence': round(random.uniform(0.85, 0.99), 2),
            'agent_results': agent_results,
            'total_duration': total_duration,
            'processed_at': datetime.now().isoformat(),
            'metadata': {
                'mode': mode,
                'extracted_data': {
                    'amount': round(random.uniform(100, 50000), 2),
                    'currency': 'USD',
                    'vendor': random.choice(self.merchants),
                    'invoice_date': self._get_random_date(days_ago=30).strftime('%Y-%m-%d')
                },
                'risk_factors': self._generate_risk_flags(risk_score)
            }
        }
        
        return result


# Singleton instance
@st.cache_resource
def get_demo_data_generator() -> DemoDataGenerator:
    """
    Get cached demo data generator instance
    
    Returns:
        DemoDataGenerator instance
    """
    return DemoDataGenerator()