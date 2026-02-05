import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import random

# --- 1. TẠO DỮ LIỆU KINH DOANH ---
def generate_sales_data():
    products = ['Credit Card', 'Mortgage Loan', 'Savings Account', 
                'Life Insurance', 'Investment Fund', 'Digital Wallet']
    regions = ['Ha Noi', 'Ho Chi Minh', 'Da Nang', 'Can Tho', 'Hai Phong']
    
    data = []
    for i in range(800):
        product = random.choice(products)
        region = random.choice(regions)
        
        if product == 'Mortgage Loan': base = random.randint(500, 5000)
        elif product == 'Investment Fund': base = random.randint(50, 500)
        else: base = random.randint(5, 100)
        
        revenue = base * 1000000
        profit_margin = random.uniform(0.1, 0.3)
        profit = revenue * profit_margin
        discount = random.randint(0, 15)
            
        data.append({
            "Deal ID": f"DL_{1000+i}",
            "Product": product,
            "Region": region,
            "Revenue": revenue,
            "Profit": profit,
            "Discount %": discount,
            "Date": pd.date_range(start="2026-01-01", periods=800)[i]
        })
    return pd.DataFrame(data)

df = generate_sales_data()

# --- 2. TỪ ĐIỂN NGÔN NGỮ (LANG DICT) ---
LANG = {
    'vi': {
        'title': 'BẢNG ĐIỀU KHIỂN DOANH SỐ',
        'sub': 'Phân tích Doanh thu, Lợi nhuận & Biên độ',
        'kpi_rev': 'TỔNG DOANH THU',
        'kpi_prof': 'LỢI NHUẬN RÒNG',
        'kpi_deals': 'SỐ LƯỢNG DEAL',
        'filter': '📍 CHỌN KHU VỰC:',
        'chart_trend': 'HIỆU SUẤT KINH DOANH',
        'chart_pie': 'TỶ TRỌNG DOANH SỐ',
        'chart_bubble': 'MA TRẬN LỢI NHUẬN (BUBBLE)',
        'chart_box': 'BIÊN ĐỘ GIÁ TRỊ DEAL (BOXPLOT)',
        'btn_lang': '🇻🇳 VN / 🇺🇸 EN',
        'btn_theme': '🌙 / ☀️ Giao diện'
    },
    'en': {
        'title': 'SALES MASTER DASHBOARD',
        'sub': 'Revenue, Profit & Margin Analysis',
        'kpi_rev': 'TOTAL REVENUE',
        'kpi_prof': 'NET PROFIT',
        'kpi_deals': 'TOTAL DEALS',
        'filter': '📍 SELECT REGION:',
        'chart_trend': 'BUSINESS PERFORMANCE',
        'chart_pie': 'SALES SHARE',
        'chart_bubble': 'PROFIT MATRIX (BUBBLE)',
        'chart_box': 'DEAL VALUE RANGE (BOXPLOT)',
        'btn_lang': '🇺🇸 EN / 🇻🇳 VN',
        'btn_theme': '🌙 / ☀️ Theme'
    }
}

THEMES = {
    'dark': {'bg': '#0f172a', 'card': '#1e293b', 'text': '#f8fafc', 'accent': '#38bdf8', 'template': 'plotly_dark'},
    'light': {'bg': '#f8fafc', 'card': '#ffffff', 'text': '#1e293b', 'accent': '#2563eb', 'template': 'plotly_white'}
}

app = dash.Dash(__name__)
app.title = "Flow Fintech Sales Global"

# --- 3. HELPER: KPI CARD ---
def create_kpi_card(title, value, sub_text, color, t):
    return html.Div([
        html.H4(title, style={'fontSize': '11px', 'fontWeight': 'bold', 'color': '#94a3b8', 'marginBottom': '5px'}),
        html.H2(value, style={'fontSize': '28px', 'fontWeight': '800', 'margin': '0', 'color': t['text']}),
        html.Div(sub_text, style={'color': color, 'fontSize': '12px', 'fontWeight': 'bold', 'marginTop': '5px'})
    ], style={'backgroundColor': t['card'], 'padding': '20px', 'borderRadius': '16px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)', 'borderLeft': f'4px solid {color}', 'flex': '1', 'margin': '0 8px'})

# --- 4. LAYOUT ---
app.layout = html.Div(id='main-layout', style={'transition': '0.5s'}, children=[
    dcc.Store(id='store-theme', data='dark'),
    dcc.Store(id='store-lang', data='vi'), # Mặc định Tiếng Việt

    # Header
    html.Div([
        html.Div([
            html.H1(id='lbl-title', style={'background': 'linear-gradient(to right, #38bdf8, #f472b6)', '-webkit-background-clip': 'text', '-webkit-text-fill-color': 'transparent', 'fontWeight': '900', 'margin': '0'}),
            html.P(id='lbl-sub', style={'margin': '0', 'opacity': '0.7', 'fontSize': '14px'})
        ]),
        html.Div([
            html.Button("VN/EN", id='btn-lang', n_clicks=0, style={'marginRight': '10px', 'padding': '8px 16px', 'borderRadius': '20px', 'border': 'none', 'fontWeight': 'bold', 'cursor': 'pointer'}),
            html.Button("Theme", id='btn-theme', n_clicks=0, style={'padding': '8px 16px', 'borderRadius': '20px', 'border': 'none', 'fontWeight': 'bold', 'cursor': 'pointer', 'background': '#38bdf8', 'color': 'white'})
        ])
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '30px'}),

    # KPI Row
    html.Div(id='kpi-row', style={'display': 'flex', 'marginBottom': '30px'}),

    # Filter
    html.Div([
        html.Label(id='lbl-filter', style={'fontWeight': 'bold', 'fontSize': '12px'}),
        dcc.Dropdown(id='dd-region', options=[{'label': r, 'value': r} for r in df['Region'].unique()], value='Ho Chi Minh', clearable=False, style={'color': '#000'})
    ], style={'width': '30%', 'marginBottom': '20px'}),

    # Hàng 1
    html.Div([
        html.Div([dcc.Graph(id='chart-trend')], style={'width': '65%', 'borderRadius': '16px', 'overflow': 'hidden'}),
        html.Div([dcc.Graph(id='chart-pie')], style={'width': '34%', 'borderRadius': '16px', 'overflow': 'hidden'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),

    # Hàng 2
    html.Div([
        html.Div([dcc.Graph(id='chart-bubble')], style={'width': '49%', 'borderRadius': '16px', 'overflow': 'hidden'}),
        html.Div([dcc.Graph(id='chart-box')], style={'width': '49%', 'borderRadius': '16px', 'overflow': 'hidden'}),
    ], style={'display': 'flex', 'justifyContent': 'space-between'})
])

# --- 5. CALLBACK ---
@app.callback(
    [Output('main-layout', 'style'),
     Output('store-theme', 'data'),
     Output('store-lang', 'data'),
     Output('lbl-title', 'children'),
     Output('lbl-sub', 'children'),
     Output('lbl-filter', 'children'),
     Output('btn-lang', 'children'),
     Output('btn-theme', 'children'),
     Output('kpi-row', 'children'),
     Output('chart-trend', 'figure'),
     Output('chart-pie', 'figure'),
     Output('chart-bubble', 'figure'),
     Output('chart-box', 'figure')],
    [Input('btn-theme', 'n_clicks'),
     Input('btn-lang', 'n_clicks'),
     Input('dd-region', 'value')],
    [State('store-theme', 'data'),
     State('store-lang', 'data')]
)
def update_dashboard(n_theme, n_lang, region, cur_theme, cur_lang):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Xử lý State
    if trigger_id == 'btn-theme': cur_theme = 'light' if cur_theme == 'dark' else 'dark'
    if trigger_id == 'btn-lang': cur_lang = 'en' if cur_lang == 'vi' else 'vi'
    
    t = THEMES[cur_theme]
    l = LANG[cur_lang]

    # Filter Data
    dff = df[df['Region'] == region]

    # KPIs
    total_rev = dff['Revenue'].sum()
    total_prof = dff['Profit'].sum()
    rev_str = f"{total_rev/1e9:.1f}B" if total_rev > 1e9 else f"{total_rev/1e6:.0f}M"
    prof_str = f"{total_prof/1e9:.1f}B" if total_prof > 1e9 else f"{total_prof/1e6:.0f}M"
    
    kpis = [
        create_kpi_card(l['kpi_rev'], rev_str, "▲ Target Met", t['accent'], t),
        create_kpi_card(l['kpi_prof'], prof_str, "Healthy Margin", "#10b981", t),
        create_kpi_card(l['kpi_deals'], str(len(dff)), "Active Deals", "#f59e0b", t)
    ]

    # Charts Config
    layout_cfg = {
        'plot_bgcolor': t['card'], 'paper_bgcolor': t['card'], 
        'font': {'color': t['text'], 'family': 'Segoe UI'},
        'margin': {'t': 40, 'l': 40, 'r': 20, 'b': 40}
    }

    # 1. Trend
    fig_trend = px.area(dff.sort_values('Date'), x='Date', y='Revenue', title=l['chart_trend'], template=t['template'])
    fig_trend.update_traces(line_color=t['accent'], fillcolor=f"rgba{tuple(int(t['accent'][1:][i:i+2], 16) for i in (0, 2, 4)) + (0.2,)}")
    fig_trend.update_layout(**layout_cfg)

    # 2. Pie
    fig_pie = px.pie(dff, values='Revenue', names='Product', hole=0.7, title=l['chart_pie'], template=t['template'])
    fig_pie.update_layout(**layout_cfg)
    fig_pie.update_traces(textposition='inside', textinfo='percent')

    # 3. Bubble
    fig_bubble = px.scatter(dff, x="Revenue", y="Profit", size="Discount %", color="Product",
                            title=l['chart_bubble'], template=t['template'], hover_data=['Deal ID'])
    fig_bubble.update_layout(**layout_cfg)
    fig_bubble.update_traces(marker=dict(line=dict(width=1, color='white'), opacity=0.8))

    # 4. Box
    fig_box = px.box(dff, x="Product", y="Revenue", color="Product", title=l['chart_box'], template=t['template'])
    fig_box.update_layout(**layout_cfg, showlegend=False)

    style = {'backgroundColor': t['bg'], 'color': t['text'], 'padding': '40px', 'minHeight': '100vh', 'fontFamily': 'Segoe UI'}
    return style, cur_theme, cur_lang, l['title'], l['sub'], l['filter'], l['btn_lang'], l['btn_theme'], kpis, fig_trend, fig_pie, fig_bubble, fig_box

if __name__ == '__main__':
    app.run(debug=True, port=8050)