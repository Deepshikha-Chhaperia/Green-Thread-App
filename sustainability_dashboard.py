# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3

# Database connection function
def get_db_connection():
    """Create and return a database connection with row factory."""
    try:
        conn = sqlite3.connect('greenthreads.db', detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        print("Database connection successful")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {str(e)}")
        return None

def display_sustainability_dashboard():
    st.title("Sustainability Analytics Dashboard")
    
    # Get data from database
    conn = get_db_connection()
    if not conn:
        st.error("Could not connect to database")
        return
        
    try:
        # Fetch all designs
        query = """
        SELECT 
            strftime('%Y-%m', timestamp) as month,
            AVG(sustainability_score) as avg_score,
            COUNT(*) as design_count,
            materials,
            production_method,
            clothing_type
        FROM designs 
        GROUP BY strftime('%Y-%m', timestamp)
        ORDER BY month DESC
        """
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            st.warning("No data available in the database. Generate some designs first!")
            return
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Average Sustainability Score",
                f"{df['avg_score'].mean():.1f}%",
                delta=f"{df['avg_score'].diff().iloc[-1]:.1f}%" if len(df) > 1 else None
            )
            
        with col2:
            st.metric(
                "Total Designs",
                int(df['design_count'].sum()),
                delta=int(df['design_count'].diff().iloc[-1]) if len(df) > 1 else None
            )
            
        with col3:
            if len(df) > 1:
                monthly_growth = ((df['design_count'].iloc[-1] / df['design_count'].iloc[-2]) - 1) * 100
                st.metric(
                    "Monthly Growth",
                    f"{monthly_growth:.1f}%",
                    delta=f"{monthly_growth:.1f}%"
                )
            else:
                st.metric("Monthly Growth", "N/A")
            
        # Sustainability Score Trend
        st.subheader("Sustainability Score Trend")
        fig_trend = px.line(
            df,
            x='month',
            y='avg_score',
            title='Monthly Average Sustainability Score',
            labels={'month': 'Month', 'avg_score': 'Average Sustainability Score'},
            line_shape='linear'
        )
        fig_trend.update_traces(line_color='#00C49F', line_width=3)
        fig_trend.update_layout(
            plot_bgcolor='white',
            yaxis_gridcolor='lightgray',
            xaxis_gridcolor='lightgray'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Material Usage
            st.subheader("Material Distribution")
            materials_df = pd.DataFrame([
                item.strip() 
                for sublist in df['materials'].str.split(',') 
                for item in sublist
            ]).value_counts().reset_index()
            materials_df.columns = ['Material', 'Count']
            
            fig_materials = px.pie(
                materials_df,
                values='Count',
                names='Material',
                title='Material Usage Distribution',
                hole=0.4,  # Makes it a donut chart
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_materials, use_container_width=True)
        
        with col2:
            # Production Methods
            st.subheader("Production Methods")
            production_df = df['production_method'].value_counts().reset_index()
            production_df.columns = ['Method', 'Count']
            
            fig_production = px.bar(
                production_df,
                x='Method',
                y='Count',
                title='Production Methods Distribution',
                color='Count',
                color_continuous_scale='Viridis'
            )
            fig_production.update_layout(
                plot_bgcolor='white',
                yaxis_gridcolor='lightgray',
                xaxis_gridcolor='lightgray'
            )
            st.plotly_chart(fig_production, use_container_width=True)
        
        # Clothing Types
        st.subheader("Popular Clothing Types")
        clothing_df = df['clothing_type'].value_counts().reset_index()
        clothing_df.columns = ['Type', 'Count']
        
        fig_clothing = px.bar(
            clothing_df,
            x='Type',
            y='Count',
            title='Clothing Types Distribution',
            color='Count',
            color_continuous_scale='Viridis'
        )
        fig_clothing.update_layout(
            plot_bgcolor='white',
            yaxis_gridcolor='lightgray',
            xaxis_gridcolor='lightgray',
            height=500
        )
        st.plotly_chart(fig_clothing, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
    finally:
        conn.close()

# Add some custom styling
st.markdown("""
    <style>
    .stMetric .metric-label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
    }
    
    .stMetric .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #27ae60 !important;
    }
    
    .stMetric .metric-delta {
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    h1 {
        color: #2c3e50 !important;
        font-weight: 700 !important;
        margin-bottom: 2rem !important;
    }
    
    h3 {
        color: #34495e !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
    }
    
    .stPlotlyChart {
        background-color: white !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }
    </style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    display_sustainability_dashboard()