"""
ARGO - Analytics Panel
Complete metrics dashboard for API usage and costs
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

from core.logger import get_logger

logger = get_logger("AnalyticsPanel")


def render_analytics_panel(unified_db, config):
    """
    Render complete analytics panel
    
    Args:
        unified_db: UnifiedDatabase instance
        config: Configuration object
    """
    st.subheader("API Usage & Cost Analytics")
    
    # Budget configuration
    monthly_budget = config.get("budget.monthly_limit_usd", 200.0)
    alert_threshold = config.get("budget.alert_threshold_percent", 80)
    
    # Get monthly summary
    monthly = unified_db.get_monthly_summary()
    
    # Budget alert
    budget_alert = unified_db.check_budget_alert(monthly_budget)
    
    if budget_alert['has_alert']:
        if budget_alert['level'] == 'critical':
            st.error(f"⚠️ {budget_alert['message']}")
        else:
            st.warning(f"⚠️ {budget_alert['message']}")
    else:
        st.success(f"✓ {budget_alert['message']}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_cost = monthly.get('total_cost') or 0.0
        st.metric(
            "Monthly Cost",
            f"${total_cost:.2f}",
            f"of ${monthly_budget:.2f}"
        )

    with col2:
        total_tokens = monthly.get('total_tokens') or 0
        total_requests = monthly.get('total_requests') or 0
        st.metric(
            "Total Tokens",
            f"{total_tokens:,}",
            f"{total_requests} requests"
        )

    with col3:
        daily_avg_cost = monthly.get('daily_avg_cost') or 0.0
        daily_avg_tokens = monthly.get('daily_avg_tokens') or 0
        st.metric(
            "Daily Average",
            f"${daily_avg_cost:.2f}",
            f"{int(daily_avg_tokens):,} tokens"
        )

    with col4:
        percentage_used = budget_alert.get('percentage_used') or 0.0
        remaining = budget_alert.get('remaining', monthly_budget)
        remaining_pct = 100 - percentage_used
        st.metric(
            "Budget Remaining",
            f"{remaining_pct:.1f}%",
            f"${remaining:.2f}"
        )
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Daily Usage",
        "By Project",
        "By Model",
        "By Project Type"
    ])
    
    with tab1:
        render_daily_usage(unified_db)
    
    with tab2:
        render_by_project(unified_db)
    
    with tab3:
        render_by_model(unified_db)
    
    with tab4:
        render_by_project_type(unified_db)


def render_daily_usage(unified_db):
    """Render daily usage chart"""
    st.subheader("Daily Usage Trend")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        days_back = st.selectbox(
            "Time period",
            [7, 14, 30, 60, 90],
            index=2,  # Default 30 days
            format_func=lambda x: f"Last {x} days"
        )
    
    # Get data
    daily_data = unified_db.get_daily_usage(days=days_back)
    
    if not daily_data:
        st.info("No usage data available")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(daily_data)
    df['day'] = pd.to_datetime(df['day'])
    df = df.sort_values('day')
    
    # Create dual-axis chart
    fig = go.Figure()
    
    # Tokens (left axis)
    fig.add_trace(go.Scatter(
        x=df['day'],
        y=df['tokens'],
        name='Tokens',
        mode='lines+markers',
        line=dict(color='#4a90e2', width=2),
        yaxis='y'
    ))
    
    # Cost (right axis)
    fig.add_trace(go.Scatter(
        x=df['day'],
        y=df['cost'],
        name='Cost (USD)',
        mode='lines+markers',
        line=dict(color='#e24a4a', width=2),
        yaxis='y2'
    ))
    
    # Layout
    fig.update_layout(
        title='Daily API Usage',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title='Tokens',
            titlefont=dict(color='#4a90e2'),
            tickfont=dict(color='#4a90e2')
        ),
        yaxis2=dict(
            title='Cost (USD)',
            titlefont=dict(color='#e24a4a'),
            tickfont=dict(color='#e24a4a'),
            overlaying='y',
            side='right'
        ),
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Tokens", f"{df['tokens'].sum():,}")
    
    with col2:
        st.metric("Total Cost", f"${df['cost'].sum():.2f}")
    
    with col3:
        st.metric("Avg Daily Cost", f"${df['cost'].mean():.2f}")


def render_by_project(unified_db):
    """Render usage by project"""
    st.subheader("Usage by Project")
    
    # Date range selector
    col1, col2 = st.columns(2)
    
    with col1:
        days_back = st.selectbox(
            "Period",
            [7, 30, 90],
            index=1,
            key="project_days"
        )
    
    start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
    
    # Get data
    project_data = unified_db.get_usage_by_project(start_date=start_date)
    
    if not project_data:
        st.info("No project usage data available")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(project_data)
    
    # Pie chart for cost distribution
    fig_cost = px.pie(
        df,
        values='cost',
        names='project_name',
        title=f'Cost Distribution (Last {days_back} days)',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig_cost.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig_cost, use_container_width=True)
    
    # Table with details
    st.subheader("Project Details")
    
    display_df = df[[
        'project_name',
        'project_type',
        'tokens',
        'cost',
        'requests'
    ]].copy()
    
    display_df.columns = ['Project', 'Type', 'Tokens', 'Cost (USD)', 'Requests']
    display_df['Tokens'] = display_df['Tokens'].apply(lambda x: f"{x:,}")
    display_df['Cost (USD)'] = display_df['Cost (USD)'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_by_model(unified_db):
    """Render usage by model"""
    st.subheader("Usage by Model & Provider")
    
    # Date range
    col1, col2 = st.columns(2)
    
    with col1:
        days_back = st.selectbox(
            "Period",
            [7, 30, 90],
            index=1,
            key="model_days"
        )
    
    start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
    
    # Get data
    model_data = unified_db.get_usage_by_model(start_date=start_date)
    
    if not model_data:
        st.info("No model usage data available")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(model_data)
    df['model_full'] = df['provider'] + ' / ' + df['model']
    
    # Bar chart for cost by model
    fig = px.bar(
        df,
        x='model_full',
        y='cost',
        title=f'Cost by Model (Last {days_back} days)',
        labels={'model_full': 'Provider / Model', 'cost': 'Cost (USD)'},
        color='provider',
        color_discrete_map={
            'openai': '#00a67e',
            'anthropic': '#d97757'
        }
    )
    
    fig.update_layout(height=400, showlegend=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Details table
    st.subheader("Model Details")
    
    display_df = df[[
        'provider',
        'model',
        'tokens',
        'cost',
        'requests',
        'avg_tokens_per_request'
    ]].copy()
    
    display_df.columns = [
        'Provider',
        'Model',
        'Tokens',
        'Cost (USD)',
        'Requests',
        'Avg Tokens/Request'
    ]
    
    display_df['Tokens'] = display_df['Tokens'].apply(lambda x: f"{x:,}")
    display_df['Cost (USD)'] = display_df['Cost (USD)'].apply(lambda x: f"${x:.2f}")
    display_df['Avg Tokens/Request'] = display_df['Avg Tokens/Request'].apply(lambda x: f"{x:.0f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def render_by_project_type(unified_db):
    """Render usage by project type"""
    st.subheader("Usage by Project Type")
    
    # Date range
    col1, col2 = st.columns(2)
    
    with col1:
        days_back = st.selectbox(
            "Period",
            [7, 30, 90],
            index=1,
            key="type_days"
        )
    
    start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
    
    # Get data
    type_data = unified_db.get_usage_by_project_type(start_date=start_date)
    
    if not type_data:
        st.info("No project type data available")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(type_data)
    
    # Clean up project_type names
    type_names = {
        'standard': 'Standard Projects',
        'ed_sto': 'ED/STO Projects',
        'library': 'Library Access'
    }
    
    df['project_type_display'] = df['project_type'].map(type_names).fillna(df['project_type'])
    
    # Comparison chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Tokens comparison
        fig_tokens = px.bar(
            df,
            x='project_type_display',
            y='tokens',
            title='Tokens by Project Type',
            labels={'project_type_display': 'Project Type', 'tokens': 'Total Tokens'},
            color='project_type_display',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig_tokens.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_tokens, use_container_width=True)
    
    with col2:
        # Cost comparison
        fig_cost = px.bar(
            df,
            x='project_type_display',
            y='cost',
            title='Cost by Project Type',
            labels={'project_type_display': 'Project Type', 'cost': 'Total Cost (USD)'},
            color='project_type_display',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        fig_cost.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_cost, use_container_width=True)
    
    # Summary table
    st.subheader("Summary by Type")
    
    display_df = df[[
        'project_type_display',
        'tokens',
        'cost',
        'requests'
    ]].copy()
    
    display_df.columns = ['Project Type', 'Tokens', 'Cost (USD)', 'Requests']
    display_df['Tokens'] = display_df['Tokens'].apply(lambda x: f"{x:,}")
    display_df['Cost (USD)'] = display_df['Cost (USD)'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
