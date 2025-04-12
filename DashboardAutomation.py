import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import numpy as np
import os

# Set page configuration
st.set_page_config(
    page_title="Corporate Dashboard",
    page_icon="📊",
    layout="wide",
)

# Custom CSS for corporate styling
def add_corporate_styling():
    st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .st-bw {
        background-color: ##FAFAFA;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        height: 60px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    h1, h2, h3 {
        color: #1f466e;
    }
    .stAlert {
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

add_corporate_styling()

# Corporate color themes
THEMES = {
    "Corporate Blue": {
        "primary": "#1f77b4",
        "secondary": "#aec7e8",
        "accent": "#2c3e50",
        "background": "#f9f9f9",
        "text": "#2c3e50"
    },
    "Professional Green": {
        "primary": "#2ca02c",
        "secondary": "#98df8a",
        "accent": "#1e3d32",
        "background": "#f9f9f9",
        "text": "#1e3d32"
    },
    "Conservative Gray": {
        "primary": "#7f7f7f",
        "secondary": "#c7c7c7",
        "accent": "#333333",
        "background": "#f9f9f9",
        "text": "#333333"
    },
    "Corporate Teal": {
        "primary": "#17a2b8",
        "secondary": "#a8e1eb",
        "accent": "#0c5460",
        "background": "#f9f9f9",
        "text": "#0c5460"
    },

    "Executive Navy": {
    "primary": "#1a1a40",
    "secondary": "#4c4c7a",
    "accent": "#0d0d26",
    "background": "#f4f6f8",
    "text": "#1a1a40"
    },

    "Modern Amber": {
    "primary": "#ff8c00",
    "secondary": "#ffd699",
    "accent": "#cc7000",
    "background": "#fefefe",
    "text": "#663c00"
    },

    "Elegant Purple": {
    "primary": "#6f42c1",
    "secondary": "#d6b3ff",
    "accent": "#4b2a8a",
    "background": "#f9f9f9",
    "text": "#4b2a8a"
    }


}

# Data detection functions
def detect_column_types(df):
    """Detect the types of columns in the dataframe."""
    column_types = {}
    
    for column in df.columns:
        if pd.api.types.is_numeric_dtype(df[column]):
            if df[column].nunique() < 10 and df[column].nunique() / len(df[column]) < 0.05:
                column_types[column] = "categorical_numeric"
            else:
                column_types[column] = "metric"
        elif pd.api.types.is_datetime64_dtype(df[column]):
            column_types[column] = "datetime"
        else:
            # Check if it's potentially a categorical column
            if df[column].nunique() < 30 or df[column].nunique() / len(df[column]) < 0.1:
                column_types[column] = "categorical"
            else:
                column_types[column] = "text"
    
    return column_types

def suggest_visualizations(df, column_types):
    """Suggest visualizations based on column types."""
    categorical_cols = [col for col, type_ in column_types.items() 
                        if type_ in ["categorical", "categorical_numeric"]]
    metric_cols = [col for col, type_ in column_types.items() if type_ == "metric"]
    datetime_cols = [col for col, type_ in column_types.items() if type_ == "datetime"]
    
    suggestions = {
        "city_transactions_columns": {
            "x_axis": next((col for col in categorical_cols if "city" in col.lower()), 
                          next((col for col in categorical_cols), None)),
            "y_axis": next((col for col in metric_cols if "amount" in col.lower() or "transaction" in col.lower()), 
                         next((col for col in metric_cols), None))
        },
        "account_type_columns": {
            "names": next((col for col in categorical_cols if "account" in col.lower() or "type" in col.lower()),
                        next((col for col in categorical_cols), None)),
            "values": next((col for col in metric_cols if "amount" in col.lower() or "transaction" in col.lower()), 
                         next((col for col in metric_cols), None))
        },
        "bank_transactions_columns": {
            "x_axis": next((col for col in metric_cols if "amount" in col.lower() or "transaction" in col.lower()),
                         next((col for col in metric_cols), None)),
            "y_axis": next((col for col in categorical_cols if "bank" in col.lower()),
                         next((col for col in categorical_cols), None))
        },
        "transaction_type_columns": {
            "x_axis": next((col for col in categorical_cols if "type" in col.lower() or "transaction" in col.lower()),
                          next((col for col in categorical_cols if col != suggestions["account_type_columns"]["names"]), None)),
            "y_axis": next((col for col in metric_cols if "amount" in col.lower() or "count" in col.lower()),
                         next((col for col in metric_cols), None))
        }
    }
    
    return suggestions

# Chart creation functions
def create_city_transactions_chart(df, x_column, y_column, theme_colors):
    """Create a clustered column chart for city-wise transactions."""
    if not x_column or not y_column:
        return None
        
    # Group by city and aggregate
    city_data = df.groupby(x_column)[y_column].sum().reset_index()
    city_data = city_data.sort_values(by=y_column, ascending=False)
    
    fig = px.bar(
        city_data, 
        x=x_column, 
        y=y_column,
        title=f"{x_column} wise {y_column}",
        color_discrete_sequence=[theme_colors["primary"]],
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        plot_bgcolor="white",
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=24, color=theme_colors["text"]),
        margin=dict(t=100, b=50, l=50, r=50),
        hoverlabel=dict(bgcolor=theme_colors["accent"], font_size=14),
    )
    
    return fig

def create_account_type_pie_chart(df, name_column, value_column, theme_colors):
    """Create a pie chart for account type wise transactions."""
    if not name_column or not value_column:
        return None
        
    # Group by account type and aggregate
    account_data = df.groupby(name_column)[value_column].sum().reset_index()
    
    fig = px.pie(
        account_data,
        names=name_column,
        values=value_column,
        title=f"{name_column} Distribution",
        color_discrete_sequence=[theme_colors["primary"], theme_colors["secondary"], 
                              theme_colors["accent"], theme_colors["text"]],
        template="plotly_white"
    )
    
    fig.update_layout(
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=24, color=theme_colors["text"]),
        margin=dict(t=100, b=50, l=50, r=50),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    
    return fig

def create_bank_transactions_bar_chart(df, x_column, y_column, theme_colors):
    """Create a clustered bar chart for bank-wise transactions."""
    if not x_column or not y_column:
        return None
        
    # Group by bank name and aggregate
    bank_data = df.groupby(y_column)[x_column].sum().reset_index()
    bank_data = bank_data.sort_values(by=x_column)
    
    fig = px.bar(
        bank_data,
        x=x_column,
        y=y_column,
        orientation='h',
        title=f"{y_column} wise {x_column}",
        color_discrete_sequence=[theme_colors["primary"]],
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        plot_bgcolor="white",
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=24, color=theme_colors["text"]),
        margin=dict(t=100, b=50, l=50, r=50),
        hoverlabel=dict(bgcolor=theme_colors["accent"], font_size=14),
    )
    
    return fig

def create_transaction_types_chart(df, x_column, y_column, theme_colors):
    """Create a clustered column chart for transaction types."""
    if not x_column or not y_column:
        return None
        
    # Group by transaction type and aggregate
    type_data = df.groupby(x_column)[y_column].sum().reset_index()
    type_data = type_data.sort_values(by=y_column, ascending=False)
    
    fig = px.bar(
        type_data,
        x=x_column,
        y=y_column,
        title=f"{x_column} wise {y_column}",
        color_discrete_sequence=[theme_colors["primary"]],
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title=x_column,
        yaxis_title=y_column,
        plot_bgcolor="white",
        font=dict(color=theme_colors["text"]),
        title_font=dict(size=24, color=theme_colors["text"]),
        margin=dict(t=100, b=50, l=50, r=50),
        hoverlabel=dict(bgcolor=theme_colors["accent"], font_size=14),
    )
    
    return fig

# Download functions
def get_excel_download_link(df, filename="dashboard_data.xlsx"):
    """Generate a download link for the dataframe as Excel."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_csv("output.csv", index=False, encoding="utf-8")
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel file</a>'

def save_charts_to_html(charts, filename="dashboard_charts.html"):
    """Save all charts to a single HTML file."""
    with open(filename, "w") as f:
        f.write("<html><head><title>Dashboard Charts</title></head><body>")
        for chart_name, chart in charts.items():
            if chart:
                f.write(f"<h2>{chart_name}</h2>")
                f.write(chart.to_html(full_html=False))
        f.write("</body></html>")
    
    with open(filename, "rb") as f:
        html_data = f.read()
    
    b64 = base64.b64encode(html_data).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}">Download Charts as HTML</a>'

# Main application
def main():
    st.title("Corporate Dashboard Creator")
    st.write("Upload your data file to automatically generate professional dashboards")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Dashboard Configuration")
        selected_theme = st.selectbox(
            "Select Theme", 
            list(THEMES.keys()),
            index=0
        )
        theme_colors = THEMES[selected_theme]
        
        st.markdown("---")
        st.subheader("About")
        st.info(
            "This application automatically analyzes your data "
            "and creates professional corporate dashboards. "
            "Upload a CSV or Excel file to get started."
        )
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        try:
            # Load data
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv("data.csv", encoding="utf-8")
            else:
                df = pd.read_excel(uploaded_file)
                
            # Display data overview
            st.subheader("Data Overview")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Rows:** {df.shape[0]}")
                st.write(f"**Columns:** {df.shape[1]}")
            with col2:
                st.write(f"**Data Types:** {', '.join(df.dtypes.astype(str).unique())}")
                st.write(f"**Memory Usage:** {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
            
            # Detect column types
            column_types = detect_column_types(df)
            
            # Show sample data
            with st.expander("Preview Data", expanded=True):
                st.dataframe(df.head(5))
            
            # Show column information
            with st.expander("Column Information"):
                col_info = []
                for col in df.columns:
                    col_info.append({
                        "Column": col,
                        "Type": column_types[col],
                        "Non-Null": df[col].count(),
                        "Unique Values": df[col].nunique(),
                        "Sample Values": ", ".join(str(x) for x in df[col].dropna().unique()[:3])
                    })
                st.table(pd.DataFrame(col_info))
            
            # Suggest visualizations
            vis_suggestions = {}
            try:
                vis_suggestions = suggest_visualizations(df, column_types)
            except Exception as e:
                st.warning(f"Could not automatically suggest visualizations: {e}")
            
            # Create tabs for different dashboards
            tabs = st.tabs([
                "City Transactions", 
                "Account Types", 
                "Bank Transactions", 
                "Transaction Types"
            ])
            
            # Store all charts for download
            all_charts = {}
            
            # Tab 1: City Transactions
            with tabs[0]:
                st.header("City-wise Transactions")
                
                # Column selection
                col1, col2 = st.columns(2)
                with col1:
                    city_column = st.selectbox(
                        "Select City Column",
                        options=[col for col, type_ in column_types.items() 
                               if type_ in ["categorical", "categorical_numeric"]],
                        index=next((i for i, col in enumerate(df.columns) 
                                  if col == vis_suggestions.get("city_transactions_columns", {}).get("x_axis")), 0)
                                  if vis_suggestions.get("city_transactions_columns", {}).get("x_axis") in df.columns else 0
                    )
                
                with col2:
                    transaction_column = st.selectbox(
                        "Select Transaction Value Column",
                        options=[col for col, type_ in column_types.items() if type_ == "metric"],
                        index=next((i for i, col in enumerate([c for c, t in column_types.items() if t == "metric"]) 
                                  if col == vis_suggestions.get("city_transactions_columns", {}).get("y_axis")), 0)
                                  if vis_suggestions.get("city_transactions_columns", {}).get("y_axis") in df.columns else 0
                    )
                
                # Create and display chart
                city_chart = create_city_transactions_chart(df, city_column, transaction_column, theme_colors)
                if city_chart:
                    st.plotly_chart(city_chart, use_container_width=True, key="city_chart")
                    all_charts["City Transactions"] = city_chart
                else:
                    st.warning("Could not create city transactions chart with selected columns.")
            
            # Tab 2: Account Types
            with tabs[1]:
                st.header("Account Type-wise Transactions")
                
                # Column selection
                col1, col2 = st.columns(2)
                with col1:
                    account_column = st.selectbox(
                        "Select Account Type Column",
                        options=[col for col, type_ in column_types.items() 
                               if type_ in ["categorical", "categorical_numeric"]],
                        index=next((i for i, col in enumerate(df.columns) 
                                  if col == vis_suggestions.get("account_type_columns", {}).get("names")), 0)
                                  if vis_suggestions.get("account_type_columns", {}).get("names") in df.columns else 0
                    )
                
                with col2:
                    value_column = st.selectbox(
                        "Select Value Column",
                        options=[col for col, type_ in column_types.items() if type_ == "metric"],
                        index=next((i for i, col in enumerate([c for c, t in column_types.items() if t == "metric"]) 
                                  if col == vis_suggestions.get("account_type_columns", {}).get("values")), 0)
                                  if vis_suggestions.get("account_type_columns", {}).get("values") in df.columns else 0
                    )
                
                # Create and display chart
                account_chart = create_account_type_pie_chart(df, account_column, value_column, theme_colors)
                if account_chart:
                    st.plotly_chart(account_chart, use_container_width=True, key="account_chart")
                    all_charts["Account Types"] = account_chart
                else:
                    st.warning("Could not create account type chart with selected columns.")
            
            # Tab 3: Bank Transactions
            with tabs[2]:
                st.header("Bank-wise Transactions")
                
                # Column selection
                col1, col2 = st.columns(2)
                with col1:
                    transaction_value_column = st.selectbox(
                        "Select Transaction Value Column",
                        options=[col for col, type_ in column_types.items() if type_ == "metric"],
                        index=next((i for i, col in enumerate([c for c, t in column_types.items() if t == "metric"]) 
                                  if col == vis_suggestions.get("bank_transactions_columns", {}).get("x_axis")), 0)
                                  if vis_suggestions.get("bank_transactions_columns", {}).get("x_axis") in df.columns else 0,
                        key="bank_value_column"
                    )
                
                with col2:
                    bank_column = st.selectbox(
                        "Select Bank Column",
                        options=[col for col, type_ in column_types.items() 
                               if type_ in ["categorical", "categorical_numeric"]],
                        index=next((i for i, col in enumerate(df.columns) 
                                  if col == vis_suggestions.get("bank_transactions_columns", {}).get("y_axis")), 0)
                                  if vis_suggestions.get("bank_transactions_columns", {}).get("y_axis") in df.columns else 0
                    )
                
                # Create and display chart
                bank_chart = create_bank_transactions_bar_chart(df, transaction_value_column, bank_column, theme_colors)
                if bank_chart:
                    st.plotly_chart(bank_chart, use_container_width=True, key="transaction_chart")
                    all_charts["Bank Transactions"] = bank_chart
                else:
                    st.warning("Could not create bank transactions chart with selected columns.")
            
            # Tab 4: Transaction Types
            with tabs[3]:
                st.header("Transaction Type Analysis")
                
                # Column selection
                col1, col2 = st.columns(2)
                with col1:
                    type_column = st.selectbox(
                        "Select Transaction Type Column",
                        options=[col for col, type_ in column_types.items() 
                               if type_ in ["categorical", "categorical_numeric"]],
                        index=next((i for i, col in enumerate(df.columns) 
                                  if col == vis_suggestions.get("transaction_type_columns", {}).get("x_axis")), 0)
                                  if vis_suggestions.get("transaction_type_columns", {}).get("x_axis") in df.columns else 0
                    )
                
                with col2:
                    count_column = st.selectbox(
                        "Select Count/Amount Column",
                        options=[col for col, type_ in column_types.items() if type_ == "metric"],
                        index=next((i for i, col in enumerate([c for c, t in column_types.items() if t == "metric"]) 
                                  if col == vis_suggestions.get("transaction_type_columns", {}).get("y_axis")), 0)
                                  if vis_suggestions.get("transaction_type_columns", {}).get("y_axis") in df.columns else 0,
                        key="type_count_column"
                    )
                
                # Create and display chart
                type_chart = create_transaction_types_chart(df, type_column, count_column, theme_colors)
                if type_chart:
                    st.plotly_chart(type_chart, use_container_width=True, key="bank_chart")
                    all_charts["Transaction Types"] = type_chart
                else:
                    st.warning("Could not create transaction types chart with selected columns.")
            
            # Download options
            st.markdown("---")
            st.subheader("Export Options")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(get_excel_download_link(df), unsafe_allow_html=True)
            
            with col2:
                if all_charts:
                    html_file = "dashboard_charts.html"
                    save_charts_to_html(all_charts, html_file)
                    st.markdown(save_charts_to_html(all_charts), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error processing file: {e}")
            st.info("Please make sure your file has the correct format and contains relevant transaction data.")

if __name__ == "__main__":
    main()