"""
MSTR Sentiment Analysis Dashboard
Interactive Streamlit dashboard for visualizing sentiment data
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sqlalchemy import func
from backend.src.storage.database import get_session
from backend.src.models.post import Post
from backend.src.models.author import Author
from backend.src.models.engagement import Engagement
from backend.src.models.sentiment_score import SentimentScore
from backend.src.models.bot_signal import BotSignal
from backend.src.models.daily_aggregate import DailyAggregate

# Page config
st.set_page_config(
    page_title="MSTR Sentiment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Professional dark theme
st.markdown("""
<style>
    /* Main container */
    .main {
        background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%);
    }
    
    /* Headers */
    h1 {
        color: #ffffff;
        font-weight: 700;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.8rem !important;
        margin-top: 2rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #2ecc71;
    }
    
    h3 {
        color: #b0b0b0;
        font-weight: 500;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #a0a0a0;
    }
    
    /* Fear & Greed styling */
    .fear-greed-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 1rem 0;
    }
    
    .greed-indicator {
        color: #2ecc71;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(46, 204, 113, 0.5);
    }
    
    .fear-indicator {
        color: #e74c3c;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(231, 76, 60, 0.5);
    }
    
    .neutral-indicator {
        color: #f39c12;
        font-size: 3rem;
        font-weight: 800;
        text-shadow: 0 0 20px rgba(243, 156, 18, 0.5);
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600;
        color: #e0e0e0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: rgba(52, 152, 219, 0.1);
        border-left: 4px solid #3498db;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0f3460 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=10)
def load_data(days=90):
    """Load data from database"""
    session = get_session()
    
    try:
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query posts with all related data
        posts_query = session.query(
            Post,
            Author,
            Engagement,
            SentimentScore,
            BotSignal
        ).join(
            Author, Post.author_id == Author.user_id
        ).outerjoin(
            Engagement, Post.post_id == Engagement.post_id
        ).outerjoin(
            SentimentScore, Post.post_id == SentimentScore.post_id
        ).outerjoin(
            BotSignal, Post.post_id == BotSignal.post_id
        ).filter(
            Post.created_at >= start_date
        ).all()
        
        # Convert to DataFrame
        data = []
        for post, author, engagement, sentiment, bot in posts_query:
            data.append({
                'post_id': post.post_id,
                'text': post.text,
                'created_at': post.created_at,
                'author': author.username,
                'display_name': author.display_name,
                'followers': author.followers_count,
                'verified': author.verified,
                'likes': engagement.like_count if engagement else 0,
                'retweets': engagement.retweet_count if engagement else 0,
                'replies': engagement.reply_count if engagement else 0,
                'sentiment': sentiment.classification.value if sentiment else 'Unknown',
                'confidence': sentiment.confidence if sentiment else 0,
                'bot_score': bot.score if bot else 0
            })
        
        df = pd.DataFrame(data)
        
        # Query daily aggregates
        aggregates = session.query(DailyAggregate).filter(
            DailyAggregate.date >= start_date.date()
        ).all()
        
        agg_data = []
        for agg in aggregates:
            agg_data.append({
                'date': agg.date,
                'topic': agg.topic.value,
                'total_posts': agg.total_posts,
                'bullish_count': agg.bullish_count,
                'bearish_count': agg.bearish_count,
                'neutral_count': agg.neutral_count,
                'weighted_score': agg.weighted_score,
                'dominant_sentiment': agg.dominant_sentiment.value
            })
        
        agg_df = pd.DataFrame(agg_data)
        
        return df, agg_df
        
    finally:
        session.close()


def main():
    # Header with professional styling
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0 1rem 0;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 0;'>📊 MSTR Sentiment Tracker</h1>
        <p style='font-size: 1.3rem; color: #a0a0a0; margin-top: 0.5rem;'>
            Fear & Greed Index for MicroStrategy | Real-time Bot Detection
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Info")
    st.sidebar.caption("Collection: Mon/Wed/Fri/Sun")
    st.sidebar.caption("Posts per collection: 5")
    st.sidebar.caption("Bot threshold: 0.7")
    
    # Load all data (90 days)
    with st.spinner("Loading data..."):
        df, agg_df = load_data(days=90)
    
    if df.empty:
        st.warning("⚠️ No data available. Run `python collect_community_posts.py` to collect data!")
        st.info("💡 **Quick Start:**\n1. `python collect_community_posts.py`\n2. `python analyze_posts.py`\n3. `python run_aggregator.py`")
        return
    
    # Prepare data
    df['date'] = pd.to_datetime(df['created_at']).dt.date
    df['is_bot'] = df['bot_score'] > 0.7
    df['sentiment_numeric'] = df['sentiment'].map({'Bullish': 1, 'Neutral': 0, 'Bearish': -1})
    
    # Get today's data
    today = df['date'].max()
    today_df = df[df['date'] == today]
    
    # =================================================================
    # QUESTION 1: What is the overall sentiment TODAY?
    # =================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🎯 Today's Sentiment")
    
    # Calculate today's sentiment (overall, human, bot)
    # Convert from -1 to +1 scale to 0-100 Fear & Greed scale
    today_overall_raw = today_df['sentiment_numeric'].mean()
    today_human_raw = today_df[today_df['is_bot'] == False]['sentiment_numeric'].mean() if not today_df[today_df['is_bot'] == False].empty else 0
    today_bot_raw = today_df[today_df['is_bot'] == True]['sentiment_numeric'].mean() if not today_df[today_df['is_bot'] == True].empty else 0
    
    # Convert to 0-100 scale (0 = Extreme Fear, 50 = Neutral, 100 = Extreme Greed)
    today_overall = (today_overall_raw + 1) * 50
    today_human = (today_human_raw + 1) * 50
    today_bot = (today_bot_raw + 1) * 50
    
    # View mode selector
    view_mode = st.radio(
        "📊 Analysis View:",
        ["Overall", "Bot Breakdown"],
        horizontal=True,
        key="today_view"
    )
    
    if view_mode == "Overall":
        # Create Fear & Greed gauge (0-100 scale)
        sentiment_label = "EXTREME GREED" if today_overall > 75 else "GREED" if today_overall > 60 else "FEAR" if today_overall < 40 else "EXTREME FEAR" if today_overall < 25 else "NEUTRAL"
        
        # Gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=today_overall,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>Now: {sentiment_label}</b>", 'font': {'size': 28, 'color': '#e0e0e0'}},
            number={'font': {'size': 60, 'color': '#ffffff'}, 'suffix': ''},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': '#e0e0e0'},
                'bar': {'color': '#3498db', 'thickness': 0.3},
                'bgcolor': 'rgba(0, 0, 0, 0.2)',
                'borderwidth': 2,
                'bordercolor': '#ffffff',
                'steps': [
                    {'range': [0, 25], 'color': '#e74c3c'},      # Extreme Fear
                    {'range': [25, 40], 'color': '#e67e22'},     # Fear
                    {'range': [40, 60], 'color': '#f39c12'},     # Neutral
                    {'range': [60, 75], 'color': '#2ecc71'},     # Greed
                    {'range': [75, 100], 'color': '#27ae60'}     # Extreme Greed
                ],
                'threshold': {
                    'line': {'color': '#ffffff', 'width': 4},
                    'thickness': 0.75,
                    'value': today_overall
                }
            }
        ))
        
        fig_gauge.update_layout(
            height=400,
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font={'color': '#e0e0e0', 'family': 'Arial'},
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Date and description
        st.markdown(f"""
        <div style='text-align: center; margin: 1rem 0;'>
            <p style='font-size: 1.1rem; color: #a0a0a0;'>📅 {today} | 📊 Based on {len(today_df)} posts</p>
            <p style='font-size: 0.95rem; color: #808080;'>
                0 = Extreme Fear | 25 = Fear | 50 = Neutral | 75 = Greed | 100 = Extreme Greed
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        bullish_today = (today_df['sentiment'] == 'Bullish').sum()
        bearish_today = (today_df['sentiment'] == 'Bearish').sum()
        neutral_today = (today_df['sentiment'] == 'Neutral').sum()
        
        with col1:
            st.metric("🟢 Bullish Posts", f"{bullish_today}/{len(today_df)}", f"{bullish_today/len(today_df)*100:.0f}%")
        with col2:
            st.metric("🔴 Bearish Posts", f"{bearish_today}/{len(today_df)}", f"{bearish_today/len(today_df)*100:.0f}%")
        with col3:
            st.metric("🟡 Neutral Posts", f"{neutral_today}/{len(today_df)}", f"{neutral_today/len(today_df)*100:.0f}%")
    
    else:  # Bot Breakdown
        # Show human vs bot with visual cards (0-100 scale)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            human_color = "#2ecc71" if today_human > 60 else "#e74c3c" if today_human < 40 else "#f39c12"
            human_label = "GREED" if today_human > 60 else "FEAR" if today_human < 40 else "NEUTRAL"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(46, 204, 113, 0.2) 0%, rgba(46, 204, 113, 0.05) 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; border: 2px solid {human_color};'>
                <p style='color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;'>👤 HUMAN SENTIMENT</p>
                <h2 style='color: {human_color}; font-size: 3rem; margin: 0.5rem 0;'>{today_human:.0f}</h2>
                <p style='color: #e0e0e0; font-size: 1.2rem;'>{human_label}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            bot_color = "#e74c3c" if today_bot > 70 else "#f39c12"
            bot_label = "GREED" if today_bot > 60 else "FEAR" if today_bot < 40 else "NEUTRAL"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(231, 76, 60, 0.2) 0%, rgba(231, 76, 60, 0.05) 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; border: 2px solid {bot_color};'>
                <p style='color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;'>🤖 BOT SENTIMENT</p>
                <h2 style='color: {bot_color}; font-size: 3rem; margin: 0.5rem 0;'>{today_bot:.0f}</h2>
                <p style='color: #e0e0e0; font-size: 1.2rem;'>{bot_label}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            overall_color = "#3498db"
            overall_label = "GREED" if today_overall > 60 else "FEAR" if today_overall < 40 else "NEUTRAL"
            skew_direction = "↑ INFLATED" if today_bot > today_human else "↓ DEFLATED" if today_bot < today_human else "BALANCED"
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(52, 152, 219, 0.2) 0%, rgba(52, 152, 219, 0.05) 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; border: 2px solid {overall_color};'>
                <p style='color: #a0a0a0; font-size: 0.9rem; margin-bottom: 0.5rem;'>📊 OVERALL (SKEWED)</p>
                <h2 style='color: {overall_color}; font-size: 3rem; margin: 0.5rem 0;'>{today_overall:.0f}</h2>
                <p style='color: #e0e0e0; font-size: 1.2rem;'>{skew_direction}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        skew_amount = abs(today_overall - today_human)
        st.warning(f"⚠️ **Bot Impact:** Bots are skewing sentiment by **{skew_amount:.0f} points** {'upward ↑' if today_bot > today_human else 'downward ↓'}. Human sentiment is **{today_human:.0f}** but overall shows **{today_overall:.0f}**.")
    
    st.markdown("---")
    
    # =================================================================
    # QUESTION 2: What has been the sentiment trend?
    # =================================================================
    st.header("📈 Sentiment Trend Over Time")
    
    # View mode selector for trend
    trend_view = st.radio(
        "Trend Analysis View:",
        ["Overall", "Bot Breakdown", "Compare All"],
        horizontal=True,
        key="trend_view"
    )
    
    # Group by date and bot status
    daily_sentiment = df.groupby(['date', 'is_bot'])['sentiment_numeric'].mean().reset_index()
    overall_daily = df.groupby('date')['sentiment_numeric'].mean().reset_index()
    
    # Convert to 0-100 scale for user-friendly display
    daily_sentiment['fear_greed_score'] = (daily_sentiment['sentiment_numeric'] + 1) * 50
    overall_daily['fear_greed_score'] = (overall_daily['sentiment_numeric'] + 1) * 50
    
    human_data = daily_sentiment[daily_sentiment['is_bot'] == False]
    bot_data = daily_sentiment[daily_sentiment['is_bot'] == True]
    
    fig = go.Figure()
    
    # Add traces based on view mode (using 0-100 scale)
    if trend_view == "Overall":
        # Just show overall
        fig.add_trace(go.Scatter(
            x=overall_daily['date'],
            y=overall_daily['fear_greed_score'],
            mode='lines+markers',
            name='Overall Sentiment',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Score: %{y:.0f}<extra></extra>'
        ))
        
    elif trend_view == "Bot Breakdown":
        # Show human and bot separately
        if not human_data.empty:
            fig.add_trace(go.Scatter(
                x=human_data['date'],
                y=human_data['fear_greed_score'],
                mode='lines+markers',
                name='👤 Human Sentiment',
                line=dict(color='#2ecc71', width=2.5),
                marker=dict(size=7),
                hovertemplate='<b>%{x}</b><br>Human: %{y:.0f}<extra></extra>'
            ))
        
        if not bot_data.empty:
            fig.add_trace(go.Scatter(
                x=bot_data['date'],
                y=bot_data['fear_greed_score'],
                mode='lines+markers',
                name='🤖 Bot Sentiment',
                line=dict(color='#e74c3c', width=2.5, dash='dash'),
                marker=dict(size=7),
                hovertemplate='<b>%{x}</b><br>Bot: %{y:.0f}<extra></extra>'
            ))
    
    else:  # Compare All
        # Show all three lines
        if not human_data.empty:
            fig.add_trace(go.Scatter(
                x=human_data['date'],
                y=human_data['fear_greed_score'],
                mode='lines+markers',
                name='👤 Human Sentiment',
                line=dict(color='#2ecc71', width=2),
                marker=dict(size=6),
                hovertemplate='<b>%{x}</b><br>Human: %{y:.0f}<extra></extra>'
            ))
        
        if not bot_data.empty:
            fig.add_trace(go.Scatter(
                x=bot_data['date'],
                y=bot_data['fear_greed_score'],
                mode='lines+markers',
                name='🤖 Bot Sentiment (Skewing)',
                line=dict(color='#e74c3c', width=2, dash='dash'),
                marker=dict(size=6),
                hovertemplate='<b>%{x}</b><br>Bot: %{y:.0f}<extra></extra>'
            ))
        
        fig.add_trace(go.Scatter(
            x=overall_daily['date'],
            y=overall_daily['fear_greed_score'],
            mode='lines+markers',
            name='📊 Overall (Skewed by Bots)',
            line=dict(color='#3498db', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Overall: %{y:.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text="Sentiment Score Over Time",
            font=dict(size=24, color='#e0e0e0', family='Arial Black')
        ),
        xaxis_title="Date",
        yaxis_title="Fear & Greed Index (0 = Extreme Fear, 100 = Extreme Greed)",
        hovermode='x unified',
        yaxis=dict(
            range=[0, 100],
            gridcolor='rgba(255, 255, 255, 0.1)',
            tickvals=[0, 25, 40, 50, 60, 75, 100],
            ticktext=['0<br>Extreme<br>Fear', '25<br>Fear', '40', '50<br>Neutral', '60', '75<br>Greed', '100<br>Extreme<br>Greed']
        ),
        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#e0e0e0')
        ),
        height=550,
        plot_bgcolor='rgba(0, 0, 0, 0.2)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='#e0e0e0')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add insight based on view mode
    if trend_view == "Compare All":
        st.info("💡 **Insight:** Bot posts (red dashed line) consistently push toward extreme greed (100) and inflate the overall index (blue line) above genuine human sentiment (green line). This shows how bot manipulation artificially inflates market sentiment.")
    elif trend_view == "Bot Breakdown":
        st.info("💡 **Insight:** Compare human vs bot sentiment patterns. Bots typically show more extreme scores (closer to 0 or 100) while humans show more moderate, varied sentiment.")
    
    st.markdown("---")
    
    # Top Posts (keep this - useful context)
    st.header("🔥 Top Posts Driving Sentiment")
    
    df['total_engagement'] = df['likes'] + df['retweets'] + df['replies']
    top_posts = df.nlargest(10, 'total_engagement')
    
    for idx, row in top_posts.iterrows():
        bot_badge = "🤖 BOT" if row['bot_score'] > 0.7 else "👤 HUMAN"
        sentiment_emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}.get(row['sentiment'], "⚪")
        
        with st.expander(f"{sentiment_emoji} @{row['author']} | {bot_badge} | ❤️ {row['likes']} 🔁 {row['retweets']}"):
            st.markdown(f"**{row['text']}**")
            st.caption(f"Sentiment: {row['sentiment']} ({row['confidence']:.2f}) | Bot Score: {row['bot_score']:.2f}")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit | Data updates every 60 seconds")


if __name__ == "__main__":
    main()
