import random 
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import sqlite3
import os
import warnings
warnings.filterwarnings('ignore')

# Import our modules
try:
    from utils.ai_helper import get_financial_analysis
    from utils.data_handler import (
        init_db, add_expense, get_expenses,
        add_goal, get_goals, update_goal,
        add_saving, get_savings
    )
except ImportError:
    # Create fallback functions
    st.error("Required modules not found. Please check your file structure.")
    def init_db(): pass
    def add_expense(x): return True
    def get_expenses(x=None): return []
    def add_goal(x): return True
    def get_goals(): return []
    def update_goal(x, y): return True
    def add_saving(x): return True
    def get_savings(): return []
    
    def get_financial_analysis(*args, **kwargs):
        return "## 🧠 Smart Analysis\n\nAdd your financial data to get personalized insights and recommendations!"

# Page configuration
st.set_page_config(
    page_title="SmartSpend - Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
def load_css():
    st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1a1d24 !important;
    }
    
    /* Sidebar content */
    .sidebar-content {
        padding: 1rem;
    }
    
    /* Cards */
    .card {
        background-color: #1a1d24;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4cc9f0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Metrics */
    [data-testid="stMetric"] {
        background-color: #1a1d24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #2d3746;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #4cc9f0, #7209b7);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        transition: all 0.3s;
        padding: 0.5rem 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 201, 240, 0.3);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #2d3746;
        color: white;
        border: 1px solid #4cc9f0;
        border-radius: 6px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1d24;
        border-radius: 5px 5px 0 0;
        padding: 0.5rem 1rem;
        border: 1px solid #2d3746;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4cc9f0 !important;
        color: #0e1117 !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #4cc9f0, #7209b7);
    }
    
    /* Custom title */
    .main-title {
        background: linear-gradient(45deg, #4cc9f0, #7209b7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1rem;
        padding: 1rem;
    }
    
    /* Custom subtitle */
    .sub-title {
        color: #4cc9f0;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 4px solid #7209b7;
    }
    
    /* AI Response Box */
    .ai-response {
        background: linear-gradient(135deg, #1a1d24 0%, #2d3746 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #4cc9f0;
        margin: 1rem 0;
        line-height: 1.6;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Insights box */
    .insight-box {
        background: linear-gradient(135deg, #1a1d24 0%, #7209b7 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4cc9f0;
    }
    
    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        background: linear-gradient(45deg, #4cc9f0, #7209b7);
        color: white;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    /* Rupee symbol styling */
    .rupee {
        color: #4cc9f0;
        font-weight: bold;
    }
    
    /* Animation for metrics */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Hover effects */
    .hover-card:hover {
        transform: translateY(-5px);
        transition: transform 0.3s;
        box-shadow: 0 8px 16px rgba(76, 201, 240, 0.2);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #1a1d24, #2d3746);
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0 1rem 0;
        border-left: 4px solid #4cc9f0;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: #1a1d24;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Tooltip styling */
    .stTooltip {
        background-color: #2d3746 !important;
        color: white !important;
        border: 1px solid #4cc9f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize database
init_db()

# Load CSS
load_css()

# Title with gradient
st.markdown('<h1 class="main-title">💰 SmartSpend - Your Personal Expense Tracker</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #888; margin-bottom: 2rem; font-size: 1.1rem;">Track • Analyze • Improve</p>', unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    st.markdown('<div class="section-header">🎯 Navigation</div>', unsafe_allow_html=True)
    
    menu = st.selectbox(
        "Choose Section",
        ["📊 Dashboard", "💸 Add Expense", "🎯 Goals & Savings", "🧠 Smart Analysis", "📈 Insights"]
    )
    
    st.markdown("---")
    
    # Quick Stats in Sidebar
    st.markdown('<div class="section-header">📈 Quick Stats</div>', unsafe_allow_html=True)
    
    # Get current month's data
    current_month = datetime.now().strftime('%Y-%m')
    monthly_expenses = get_expenses(month=current_month)
    monthly_total = sum(exp['amount'] for exp in monthly_expenses) if monthly_expenses else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Monthly Spend", f"₹{monthly_total:,.0f}")
    with col2:
        days_in_month = datetime.now().day
        daily_avg = monthly_total / days_in_month if days_in_month > 0 else 0
        st.metric("Daily Avg", f"₹{daily_avg:,.0f}")
    
    st.markdown("---")
    
    # Quick Insights
    st.markdown('<div class="section-header">💡 Quick Insight</div>', unsafe_allow_html=True)
    
    # Get expense data for insight
    all_expenses = get_expenses()
    if all_expenses:
        expense_summary = {}
        for expense in all_expenses:
            category = expense['category']
            expense_summary[category] = expense_summary.get(category, 0) + expense['amount']
        
        if expense_summary:
            from utils.ai_helper import smart_ai
            insight = smart_ai.get_quick_insight(expense_summary)
            st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)
    else:
        st.info("Add expenses to get insights")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown('<div class="section-header">⚡ Quick Actions</div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("📊 View Charts", use_container_width=True):
        st.session_state.menu = "📈 Insights"
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Dashboard
if menu == "📊 Dashboard":
    col1, col2, col3 = st.columns(3)
    
    # Get all data
    all_expenses = get_expenses()
    all_savings = get_savings()
    goals = get_goals()
    
    # Total Expenses
    with col1:
        total_expenses = sum(exp['amount'] for exp in all_expenses) if all_expenses else 0
        st.metric("Total Expenses", f"₹{total_expenses:,.0f}")
    
    # Total Savings
    with col2:
        total_savings = sum(saving['amount'] for saving in all_savings) if all_savings else 0
        st.metric("Total Savings", f"₹{total_savings:,.0f}")
    
    # Active Goals
    with col3:
        active_goals = len([g for g in goals if g['status'] == 'active']) if goals else 0
        completed_goals = len([g for g in goals if g['status'] == 'achieved']) if goals else 0
        st.metric("Goals", f"{active_goals} Active", f"{completed_goals} Completed")
    
    # Recent Transactions
    st.markdown('<div class="section-header">📝 Recent Transactions</div>', unsafe_allow_html=True)
    
    if all_expenses:
        # Get last 5 expenses
        recent_expenses = all_expenses[:5]
        
        for exp in recent_expenses:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{exp['category']}**")
                if exp['description']:
                    st.caption(exp['description'])
            with col2:
                st.write(f"₹{exp['amount']:,.0f}")
            with col3:
                st.caption(exp['date'])
            st.divider()
    else:
        st.info("No expenses recorded yet. Add your first expense!")
    
    # Monthly Overview
    st.markdown('<div class="section-header">📅 This Month Overview</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category breakdown for current month
        monthly_categories = {}
        for exp in monthly_expenses:
            category = exp['category']
            monthly_categories[category] = monthly_categories.get(category, 0) + exp['amount']
        
        if monthly_categories:
            fig = go.Figure(data=[go.Pie(
                labels=list(monthly_categories.keys()),
                values=list(monthly_categories.values()),
                hole=0.4,
                marker_colors=px.colors.qualitative.Set3
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fafafa',
                height=300,
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#fafafa')
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly trend
        months = []
        amounts = []
        
        # Get last 6 months
        for i in range(5, -1, -1):
            month = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
            monthly_data = get_expenses(month=month)
            total = sum(exp['amount'] for exp in monthly_data)
            months.append(month[-2:])  # Just month number
            amounts.append(total)
        
        if sum(amounts) > 0:
            fig = go.Figure(data=go.Scatter(
                x=months,
                y=amounts,
                mode='lines+markers',
                line=dict(color='#4cc9f0', width=3),
                marker=dict(size=8, color='#7209b7'),
                fill='tozeroy',
                fillcolor='rgba(76, 201, 240, 0.1)'
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fafafa',
                height=300,
                showlegend=False,
                xaxis_title="Month",
                yaxis_title="Amount (₹)"
            )
            st.plotly_chart(fig, use_container_width=True)

# Add Expense
elif menu == "💸 Add Expense":
    st.markdown('<div class="section-header">💸 Add New Expense</div>', unsafe_allow_html=True)
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            amount = st.number_input("Amount (₹)", min_value=1.0, value=500.0, step=100.0)
            category = st.selectbox(
                "Category",
                [
                    "Food & Dining", "Transportation", "Shopping", "Entertainment",
                    "Bills & Utilities", "Healthcare", "Education", "Housing",
                    "Personal Care", "Travel", "Gifts", "Investments", "Other"
                ]
            )
        
        with col2:
            date = st.date_input("Date", datetime.now())
            description = st.text_input("Description", placeholder="What was this expense for?")
        
        # Tags input
        tags = st.multiselect(
            "Tags (optional)",
            ["Essential", "Discretionary", "Work", "Personal", "Recurring", "One-time"],
            help="Categorize your expenses"
        )
        
        submitted = st.form_submit_button("💾 Save Expense", use_container_width=True, type="primary")
        
        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0")
            else:
                expense_data = {
                    "amount": float(amount),
                    "category": category,
                    "date": date.strftime('%Y-%m-%d'),
                    "description": description,
                    "tags": ",".join(tags)
                }
                
                if add_expense(expense_data):
                    st.success("✅ Expense added successfully!")
                    st.balloons()
                    # Auto-refresh after 2 seconds
                    st.markdown('<meta http-equiv="refresh" content="2">', unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to add expense")

# Goals & Savings
elif menu == "🎯 Goals & Savings":
    tab1, tab2 = st.tabs(["🎯 Financial Goals", "💰 Savings"])
    
    with tab1:
        st.markdown('<div class="section-header">🎯 Set Financial Goals</div>', unsafe_allow_html=True)
        
        # Add new goal form
        with st.expander("➕ Add New Goal", expanded=False):
            with st.form("goal_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    goal_name = st.text_input("Goal Name", placeholder="e.g., Vacation, New Device")
                    target_amount = st.number_input("Target Amount (₹)", min_value=100.0, value=50000.0, step=1000.0)
                
                with col2:
                    deadline = st.date_input("Target Date", min_value=datetime.now())
                    priority = st.select_slider(
                        "Priority",
                        options=["Low", "Medium", "High"],
                        value="Medium"
                    )
                
                goal_description = st.text_area("Description", placeholder="Describe your goal...", height=100)
                
                submitted = st.form_submit_button("🎯 Set Goal", use_container_width=True)
                
                if submitted:
                    if not goal_name.strip():
                        st.error("Goal name is required")
                    else:
                        goal_data = {
                            "name": goal_name,
                            "target_amount": float(target_amount),
                            "current_amount": 0.0,
                            "deadline": deadline.strftime('%Y-%m-%d'),
                            "priority": priority,
                            "description": goal_description,
                            "status": "active"
                        }
                        
                        if add_goal(goal_data):
                            st.success("✅ Goal added successfully!")
                            st.rerun()
        
        # Display goals
        st.markdown("### Your Goals")
        goals = get_goals()
        
        if not goals:
            st.info("No goals set yet. Create your first financial goal!")
        else:
            for goal in goals:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        progress = min(100, (goal['current_amount'] / goal['target_amount']) * 100) if goal['target_amount'] > 0 else 0
                        status_color = "#4cc9f0" if goal['status'] == 'active' else "#00cc66"
                        st.markdown(f"**{goal['name']}**")
                        st.caption(f"Target: ₹{goal['target_amount']:,.0f} • Due: {goal['deadline']}")
                        st.progress(progress/100)
                    
                    with col2:
                        st.metric(
                            "Progress",
                            f"₹{goal['current_amount']:,.0f}",
                            f"{progress:.1f}%"
                        )
                    
                    with col3:
                        with st.popover("➕ Add"):
                            add_amount = st.number_input("Amount to add", min_value=100.0, key=f"add_{goal['id']}")
                            if st.button("Add", key=f"confirm_{goal['id']}"):
                                new_amount = goal['current_amount'] + add_amount
                                if update_goal(goal['id'], new_amount):
                                    st.success(f"Added ₹{add_amount:,.0f}!")
                                    st.rerun()
    
    with tab2:
        st.markdown('<div class="section-header">💰 Track Savings</div>', unsafe_allow_html=True)
        
        # Add savings form
        with st.form("savings_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                savings_amount = st.number_input("Savings Amount (₹)", min_value=100.0, value=5000.0, step=500.0)
                savings_date = st.date_input("Savings Date", datetime.now())
            
            with col2:
                savings_source = st.selectbox(
                    "Source",
                    ["Salary", "Bonus", "Investment", "Gift", "Business", "Other"]
                )
                savings_purpose = st.text_input("Purpose", placeholder="e.g., Emergency fund, Vacation")
            
            submitted = st.form_submit_button("💰 Add Savings", use_container_width=True)
            
            if submitted:
                savings_data = {
                    "amount": float(savings_amount),
                    "date": savings_date.strftime('%Y-%m-%d'),
                    "source": savings_source,
                    "purpose": savings_purpose
                }
                
                if add_saving(savings_data):
                    st.success("✅ Savings added successfully!")
                    st.rerun()
        
        # Display savings
        st.markdown("### Savings History")
        savings = get_savings()
        
        if savings:
            df_savings = pd.DataFrame(savings)
            st.dataframe(
                df_savings,
                column_config={
                    "amount": st.column_config.NumberColumn("Amount", format="₹%.0f"),
                    "date": "Date",
                    "source": "Source",
                    "purpose": "Purpose"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Stats
            total_saved = df_savings['amount'].sum()
            avg_saving = df_savings['amount'].mean()
            st.metric("Total Saved", f"₹{total_saved:,.0f}", f"Avg: ₹{avg_saving:,.0f}")
        else:
            st.info("No savings recorded yet. Start building your savings!")

# Smart Analysis
elif menu == "🧠 Smart Analysis":
    st.markdown('<div class="section-header">🧠 Smart Financial Analysis</div>', unsafe_allow_html=True)
    
    # Get financial data
    expenses = get_expenses()
    savings_data = get_savings()
    goals = get_goals()
    
    if not expenses:
        st.warning("Add some expenses first to get personalized analysis!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add First Expense", use_container_width=True):
                st.session_state.menu = "💸 Add Expense"
                st.rerun()
        with col2:
            if st.button("📊 See Example Analysis", use_container_width=True):
                example_analysis = get_financial_analysis(
                    {"Food": 8000, "Transport": 3000, "Shopping": 5000, "Bills": 6000},
                    22000, 50000, [], "Example Analysis"
                )
                st.markdown(f'<div class="ai-response">{example_analysis}</div>', unsafe_allow_html=True)
    else:
        # Prepare data for analysis
        expense_summary = {}
        for expense in expenses:
            category = expense['category']
            expense_summary[category] = expense_summary.get(category, 0) + expense['amount']
        
        total_expenses = sum(expense['amount'] for expense in expenses)
        total_savings = sum(saving['amount'] for saving in savings_data) if savings_data else 0
        
        # Financial snapshot
        st.markdown("### 📊 Your Financial Snapshot")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Expenses", f"₹{total_expenses:,.0f}")
        with col2:
            st.metric("Total Savings", f"₹{total_savings:,.0f}")
        with col3:
            savings_rate = (total_savings / total_expenses * 100) if total_expenses > 0 else 0
            st.metric("Savings Rate", f"{savings_rate:.1f}%")
        
        # Analysis options
        st.markdown("---")
        st.markdown("### 🔍 What would you like to analyze?")
        
        col1, col2 = st.columns(2)
        with col1:
            analysis_type = st.selectbox(
                "Analysis Focus",
                [
                    "Comprehensive Overview",
                    "Spending Patterns",
                    "Savings Strategy",
                    "Goal Achievement",
                    "Budget Optimization",
                    "Financial Health"
                ]
            )
        
        with col2:
            timeframe = st.select_slider(
                "Timeframe",
                options=["This Week", "This Month", "Next 3 Months", "This Year"]
            )
        
        # Additional context
        with st.expander("➕ Add Specific Context (Optional)"):
            user_context = st.text_area(
                "Any specific questions or concerns?",
                placeholder="E.g., 'I want to save more for travel' or 'My food expenses are high'",
                height=100
            )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            analyze_btn = st.button("🚀 Get Smart Analysis", type="primary", use_container_width=True)
        
        with col2:
            quick_btn = st.button("⚡ Quick Insights", use_container_width=True)
        
        with col3:
            if st.button("🔄 Reset", use_container_width=True):
                st.rerun()
        
        # Perform analysis
        if analyze_btn or quick_btn:
            with st.spinner("🧠 Analyzing your finances..."):
                if quick_btn:
                    # Quick analysis
                    from utils.ai_helper import smart_ai
                    analysis = smart_ai.get_quick_insight(expense_summary)
                    st.markdown(f'<div class="ai-response">{analysis}</div>', unsafe_allow_html=True)
                else:
                    # Full analysis
                    analysis = get_financial_analysis(
                        expense_summary, total_expenses, total_savings, goals, analysis_type
                    )
                    
                    # Display analysis
                    st.markdown("---")
                    st.markdown("### 💡 Your Personalized Analysis")
                    st.markdown(f'<div class="ai-response">{analysis}</div>', unsafe_allow_html=True)
                    
                    # Export option
                    st.download_button(
                        label="📥 Download Analysis",
                        data=analysis,
                        file_name=f"financial_analysis_{datetime.now().strftime('%Y%m%d')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
        
        # Quick tips
        st.markdown("---")
        with st.expander("💡 Quick Tips While We Analyze", expanded=False):
            tips = [
                "**Track every expense** for 7 days to identify patterns",
                "**Save before you spend** - transfer savings immediately on payday",
                "**Review subscriptions** monthly and cancel unused ones",
                "**Use the 50/30/20 rule**: 50% needs, 30% wants, 20% savings",
                "**Set specific financial goals** with deadlines",
                "**Automate your savings** to make it effortless",
                "**Invest in learning** - financial education pays the best returns",
                "**Celebrate small wins** to stay motivated"
            ]
            
            for tip in random.sample(tips, 4):
                st.markdown(f"• {tip}")

# Insights
elif menu == "📈 Insights":
    st.markdown('<div class="section-header">📈 Detailed Insights</div>', unsafe_allow_html=True)
    
    # Get all data
    all_expenses = get_expenses()
    
    if not all_expenses:
        st.info("Add expenses to see detailed insights and charts")
    else:
        # Convert to DataFrame
        df = pd.DataFrame(all_expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        # Time period selection
        col1, col2 = st.columns(2)
        with col1:
            period = st.selectbox(
                "Time Period",
                ["Last 7 days", "Last 30 days", "Last 3 months", "Last 6 months", "All time"]
            )
        with col2:
            chart_type = st.selectbox(
                "Chart Type",
                ["Category Breakdown", "Monthly Trend", "Daily Spending", "Category Comparison"]
            )
        
        # Filter data based on period
        now = datetime.now()
        if period == "Last 7 days":
            cutoff = now - timedelta(days=7)
        elif period == "Last 30 days":
            cutoff = now - timedelta(days=30)
        elif period == "Last 3 months":
            cutoff = now - timedelta(days=90)
        elif period == "Last 6 months":
            cutoff = now - timedelta(days=180)
        else:
            cutoff = df['date'].min() if not df.empty else now
        
        df_filtered = df[df['date'] >= cutoff] if not df.empty else df
        
        if not df_filtered.empty:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total = df_filtered['amount'].sum()
                st.metric("Total Spend", f"₹{total:,.0f}")
            
            with col2:
                avg_daily = total / max(len(df_filtered['date'].dt.date.unique()), 1)
                st.metric("Avg Daily", f"₹{avg_daily:,.0f}")
            
            with col3:
                avg_transaction = df_filtered['amount'].mean()
                st.metric("Avg Transaction", f"₹{avg_transaction:,.0f}")
            
            with col4:
                transaction_count = len(df_filtered)
                st.metric("Transactions", transaction_count)
            
            # Charts
            st.markdown("---")
            
            if chart_type == "Category Breakdown":
                category_data = df_filtered.groupby('category')['amount'].sum().reset_index()
                
                fig = px.treemap(
                    category_data,
                    path=['category'],
                    values='amount',
                    title="Expense Distribution by Category",
                    color='amount',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#fafafa',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Top categories table
                st.markdown("### Top Categories")
                top_categories = category_data.nlargest(5, 'amount')
                st.dataframe(
                    top_categories,
                    column_config={
                        "category": "Category",
                        "amount": st.column_config.NumberColumn("Amount", format="₹%.0f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
            
            elif chart_type == "Monthly Trend":
                monthly_trend = df_filtered.groupby(df_filtered['date'].dt.to_period('M'))['amount'].sum().reset_index()
                monthly_trend['date'] = monthly_trend['date'].dt.to_timestamp()
                
                fig = px.bar(
                    monthly_trend,
                    x='date',
                    y='amount',
                    title="Monthly Spending Trend",
                    color='amount',
                    color_continuous_scale='Plasma'
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#fafafa',
                    xaxis_title="Month",
                    yaxis_title="Amount (₹)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Daily Spending":
                daily_trend = df_filtered.groupby(df_filtered['date'].dt.date)['amount'].sum().reset_index()
                
                fig = px.line(
                    daily_trend,
                    x='date',
                    y='amount',
                    title="Daily Spending Trend",
                    markers=True
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#fafafa',
                    xaxis_title="Date",
                    yaxis_title="Amount (₹)",
                    height=400
                )
                fig.update_traces(line_color='#4cc9f0', marker_color='#7209b7')
                st.plotly_chart(fig, use_container_width=True)
            
            # Export options
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Export to CSV", use_container_width=True):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name="expense_data.csv",
                        mime="text/csv"
                    )
            
            with col2:
                if st.button("📊 Generate Report", use_container_width=True):
                    st.info("Report generation coming soon!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem;'>"
    "💰 Smart Expense Tracker • Your financial companion"
    "</div>",
    unsafe_allow_html=True
)

# mobile-friendly features
st.set_page_config(
    page_title="SmartSpend - Your Personal Expense Tracker",
    page_icon="💰",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed",  # Hide sidebar on mobile
)