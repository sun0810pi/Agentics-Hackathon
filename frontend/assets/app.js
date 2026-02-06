// ============================================
// AUDIT CORE V4 PRO - JAVASCRIPT
// ============================================

const API_BASE = 'http://localhost:8000/api/v1';

// Global state
let allTransactions = [];
let dashboardStats = {};
let agentStats = {};

// Charts
let statusChart, riskChart, timelineChart, supplierChart;

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initFileUpload();
    loadDashboard();
    
    // Auto refresh every 30s
    setInterval(() => {
        if (document.querySelector('#page-dashboard').classList.contains('active')) {
            loadDashboard();
        }
    }, 30000);
});

// ============================================
// NAVIGATION
// ============================================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active nav
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            
            // Show corresponding page
            const page = item.dataset.page;
            showPage(page);
        });
    });
}

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
    
    // Show selected page
    const targetPage = document.getElementById(`page-${pageName}`);
    if (targetPage) {
        targetPage.classList.add('active');
        
        // Update title
        const titles = {
            'dashboard': 'Dashboard Overview',
            'upload': 'Upload Invoice Data',
            'transactions': 'All Transactions',
            'agents': 'Agent Status Monitor',
            'analytics': 'Advanced Analytics'
        };
        document.getElementById('page-title').textContent = titles[pageName] || pageName;
        
        // Load data for specific pages
        if (pageName === 'transactions') {
            loadAllTransactions();
        } else if (pageName === 'agents') {
            loadAgentStats();
        } else if (pageName === 'analytics') {
            loadAnalytics();
        }
    }
}

// ============================================
// DASHBOARD
// ============================================
async function loadDashboard() {
    try {
        // Load stats
        const statsRes = await fetch(`${API_BASE}/dashboard`);
        dashboardStats = await statsRes.json();
        
        // Update stat cards
        document.getElementById('stat-total').textContent = dashboardStats.total_transactions;
        document.getElementById('stat-pending').textContent = dashboardStats.pending_review;
        document.getElementById('stat-approved').textContent = dashboardStats.approved;
        document.getElementById('stat-highrisk').textContent = dashboardStats.high_risk_count;
        
        // Load transactions for charts
        const txRes = await fetch(`${API_BASE}/transactions`);
        allTransactions = await txRes.json();
        
        // Update charts
        updateStatusChart();
        updateRiskChart();
        updateRecentTransactionsTable();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateStatusChart() {
    const canvas = document.getElementById('statusChart');
    const ctx = canvas.getContext('2d');
    
    // Calculate status counts
    const statusCounts = {
        'pending': 0,
        'approved': 0,
        'rejected': 0,
        'manual_review': 0
    };
    
    allTransactions.forEach(tx => {
        statusCounts[tx.status] = (statusCounts[tx.status] || 0) + 1;
    });
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Pending', 'Approved', 'Rejected', 'Manual Review'],
            datasets: [{
                data: [
                    statusCounts.pending,
                    statusCounts.approved,
                    statusCounts.rejected,
                    statusCounts.manual_review
                ],
                backgroundColor: [
                    '#f59e0b',
                    '#10b981',
                    '#ef4444',
                    '#3b82f6'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#00FFC2' }
                }
            }
        }
    });
}

function updateRiskChart() {
    const canvas = document.getElementById('riskChart');
    const ctx = canvas.getContext('2d');
    
    const riskCounts = { 'LOW': 0, 'MEDIUM': 0, 'HIGH': 0 };
    allTransactions.forEach(tx => {
        riskCounts[tx.risk_level] = (riskCounts[tx.risk_level] || 0) + 1;
    });
    
    if (riskChart) {
        riskChart.destroy();
    }
    
    riskChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                label: 'Transactions',
                data: [riskCounts.LOW, riskCounts.MEDIUM, riskCounts.HIGH],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#00FFC2' }
                },
                x: {
                    ticks: { color: '#00FFC2' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function updateRecentTransactionsTable() {
    const tbody = document.getElementById('recent-tx-body');
    
    if (allTransactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No transactions yet</td></tr>';
        return;
    }
    
    // Show last 10
    const recent = allTransactions.slice(-10).reverse();
    
    tbody.innerHTML = recent.map(tx => `
        <tr>
            <td><strong>${tx.transaction_id}</strong></td>
            <td>${tx.supplier}</td>
            <td>${formatCurrency(tx.invoice_amount)}</td>
            <td>${formatCurrency(tx.po_amount)}</td>
            <td>${tx.diff_percentage.toFixed(2)}%</td>
            <td><span class="risk-badge risk-${tx.risk_level.toLowerCase()}">${tx.risk_level}</span></td>
            <td><span class="status-badge-table status-${tx.status}">${tx.status.replace('_', ' ').toUpperCase()}</span></td>
        </tr>
    `).join('');
}

// ============================================
// FILE UPLOAD
// ============================================
function initFileUpload() {
    const fileInput = document.getElementById('file-input');
    const uploadZone = document.getElementById('upload-zone');
    
    // Click to upload
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selected
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag & drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#10b981';
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.style.borderColor = '#00FFC2';
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = '#00FFC2';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    });
}

function handleFileSelect() {
    const file = document.getElementById('file-input').files[0];
    if (!file) return;
    
    const preview = document.getElementById('upload-preview');
    const previewContent = document.getElementById('preview-content');
    
    previewContent.innerHTML = `
        <div style="padding: 20px; background: rgba(0,255,194,0.1); border-radius: 12px;">
            <h4>📄 ${file.name}</h4>
            <p>Size: ${(file.size / 1024).toFixed(2)} KB</p>
            <p>Type: ${file.type || 'Unknown'}</p>
        </div>
    `;
    
    preview.style.display = 'block';
}

async function processUploadedFile() {
    const file = document.getElementById('file-input').files[0];
    if (!file) {
        alert('Please select a file first');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const resultsDiv = document.getElementById('upload-results');
    resultsDiv.innerHTML = '<p>⏳ Processing...</p>';
    resultsDiv.style.display = 'block';
    
    try {
        const response = await fetch(`${API_BASE}/upload-excel`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        
        resultsDiv.innerHTML = `
            <div style="padding: 20px; background: rgba(16,185,129,0.2); border-radius: 12px; margin-top: 20px;">
                <h3>✅ Upload Successful!</h3>
                <p>Total Processed: ${result.total_processed}</p>
                <p>Success: ${result.success_count}</p>
                <p>Failed: ${result.failed_count}</p>
                <button class="btn-primary" onclick="showPage('dashboard'); loadDashboard();">
                    View Dashboard
                </button>
            </div>
        `;
        
        // Auto redirect after 2s
        setTimeout(() => {
            showPage('dashboard');
            loadDashboard();
        }, 2000);
        
    } catch (error) {
        resultsDiv.innerHTML = `
            <div style="padding: 20px; background: rgba(239,68,68,0.2); border-radius: 12px; margin-top: 20px;">
                <h3>❌ Upload Failed</h3>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// ============================================
// TRANSACTIONS PAGE
// ============================================
async function loadAllTransactions() {
    try {
        const response = await fetch(`${API_BASE}/transactions`);
        allTransactions = await response.json();
        filterTransactions();
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

function filterTransactions() {
    const statusFilter = document.getElementById('filter-status').value;
    const riskFilter = document.getElementById('filter-risk').value;
    
    let filtered = allTransactions;
    
    if (statusFilter !== 'all') {
        filtered = filtered.filter(tx => tx.status === statusFilter);
    }
    
    if (riskFilter !== 'all') {
        filtered = filtered.filter(tx => tx.risk_level === riskFilter);
    }
    
    renderTransactionsTable(filtered);
}

function renderTransactionsTable(transactions) {
    const tbody = document.getElementById('tx-body');
    
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No transactions match filters</td></tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(tx => `
        <tr>
            <td><strong>${tx.transaction_id}</strong></td>
            <td>${tx.supplier}</td>
            <td>${formatCurrency(tx.invoice_amount)}</td>
            <td>${formatCurrency(tx.po_amount)}</td>
            <td>${tx.diff_percentage.toFixed(2)}%</td>
            <td><span class="risk-badge risk-${tx.risk_level.toLowerCase()}">${tx.risk_level}</span></td>
            <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis;">${tx.ai_verdict || 'N/A'}</td>
            <td><span class="status-badge-table status-${tx.status}">${tx.status.replace('_', ' ').toUpperCase()}</span></td>
            <td>
                ${tx.status === 'manual_review' ? `
                    <button class="btn-success" style="padding: 4px 12px; font-size: 12px;" onclick="approveTransaction('${tx.transaction_id}')">✓</button>
                    <button class="btn-danger" style="padding: 4px 12px; font-size: 12px;" onclick="rejectTransaction('${tx.transaction_id}')">✗</button>
                ` : '-'}
            </td>
        </tr>
    `).join('');
}

async function approveTransaction(txId) {
    try {
        await fetch(`${API_BASE}/transactions/${txId}/approve`, { method: 'POST' });
        alert('Transaction approved!');
        loadAllTransactions();
    } catch (error) {
        alert('Error approving transaction');
    }
}

async function rejectTransaction(txId) {
    const reason = prompt('Rejection reason:');
    if (!reason) return;
    
    try {
        await fetch(`${API_BASE}/transactions/${txId}/reject?reason=${encodeURIComponent(reason)}`, { 
            method: 'POST' 
        });
        alert('Transaction rejected!');
        loadAllTransactions();
    } catch (error) {
        alert('Error rejecting transaction');
    }
}

// ============================================
// AGENTS PAGE
// ============================================
async function loadAgentStats() {
    try {
        const response = await fetch(`${API_BASE}/agents/stats`);
        agentStats = await response.json();
        
        ['agent1', 'agent2', 'agent3'].forEach(agentKey => {
            const stats = agentStats[agentKey];
            
            // Update status
            const statusEl = document.getElementById(`${agentKey}-status`);
            const dot = statusEl.querySelector('.status-dot');
            dot.className = `status-dot ${stats.status}`;
            statusEl.querySelector('span:last-child').textContent = stats.status.toUpperCase();
            
            // Update metrics
            document.getElementById(`${agentKey}-processed`).textContent = stats.processed;
            document.getElementById(`${agentKey}-failed`).textContent = stats.failed;
        });
    } catch (error) {
        console.error('Error loading agent stats:', error);
    }
}

// ============================================
// ANALYTICS PAGE
// ============================================
async function loadAnalytics() {
    try {
        const response = await fetch(`${API_BASE}/transactions`);
        allTransactions = await response.json();
        
        updateTimelineChart();
        updateSupplierChart();
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function updateTimelineChart() {
    const canvas = document.getElementById('timelineChart');
    const ctx = canvas.getContext('2d');
    
    // Group by date
    const dateGroups = {};
    allTransactions.forEach(tx => {
        const date = tx.created_at.split('T')[0];
        dateGroups[date] = (dateGroups[date] || 0) + 1;
    });
    
    const dates = Object.keys(dateGroups).sort();
    const counts = dates.map(d => dateGroups[d]);
    
    if (timelineChart) {
        timelineChart.destroy();
    }
    
    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Transactions per Day',
                data: counts,
                borderColor: '#00FFC2',
                backgroundColor: 'rgba(0, 255, 194, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { 
                    beginAtZero: true,
                    ticks: { color: '#00FFC2' }
                },
                x: {
                    ticks: { color: '#00FFC2' }
                }
            }
        }
    });
}

function updateSupplierChart() {
    const canvas = document.getElementById('supplierChart');
    const ctx = canvas.getContext('2d');
    
    // Group by supplier
    const supplierTotals = {};
    allTransactions.forEach(tx => {
        supplierTotals[tx.supplier] = (supplierTotals[tx.supplier] || 0) + tx.invoice_amount;
    });
    
    // Top 10
    const sorted = Object.entries(supplierTotals)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const suppliers = sorted.map(s => s[0]);
    const amounts = sorted.map(s => s[1]);
    
    if (supplierChart) {
        supplierChart.destroy();
    }
    
    supplierChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: suppliers,
            datasets: [{
                label: 'Total Amount',
                data: amounts,
                backgroundColor: '#3b82f6'
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    ticks: { color: '#00FFC2' }
                },
                y: {
                    ticks: { color: '#00FFC2' }
                }
            }
        }
    });
}

// ============================================
// UTILITIES
// ============================================
function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}

function refreshData() {
    loadDashboard();
    alert('Data refreshed!');
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Recreate charts with new colors
    if (statusChart) updateStatusChart();
    if (riskChart) updateRiskChart();
}
