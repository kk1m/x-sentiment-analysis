"""
View Today's Analysis
Show sentiment analysis results for posts collected today
"""
from backend.src.storage.database import get_session
from backend.src.models.post import Post
from backend.src.models.sentiment_score import SentimentScore
from backend.src.models.bot_signal import BotSignal
from backend.src.models.author import Author
from datetime import datetime
from collections import Counter


def main():
    print("📊 Today's Post Analysis Summary")
    print("=" * 60)
    print("")
    
    session = get_session()
    
    # Get today's posts
    today = datetime.now().date()
    posts_today = session.query(Post).filter(
        Post.collected_at >= datetime.combine(today, datetime.min.time())
    ).all()
    
    if not posts_today:
        print("⚠️  No posts collected today")
        return
    
    print(f"📅 Date: {today.strftime('%Y-%m-%d (%A)')}")
    print(f"📝 Total posts collected: {len(posts_today)}")
    print("")
    
    # Sentiment analysis
    sentiments = []
    scores = []
    analyzed_count = 0
    
    for post in posts_today:
        sentiment = session.query(SentimentScore).filter_by(
            post_id=post.post_id
        ).first()
        
        if sentiment:
            analyzed_count += 1
            sentiments.append(sentiment.classification.value)
            if sentiment.score:
                scores.append(sentiment.score)
    
    print(f"🧠 Posts analyzed: {analyzed_count}/{len(posts_today)}")
    
    if analyzed_count > 0:
        print("")
        print("📈 Sentiment Breakdown:")
        sentiment_counts = Counter(sentiments)
        for sentiment, count in sentiment_counts.most_common():
            percentage = (count / analyzed_count) * 100
            bar = "█" * int(percentage / 5)
            print(f"   {sentiment:12} {count:3} ({percentage:5.1f}%) {bar}")
        
        if scores:
            avg_score = sum(scores) / len(scores)
            print("")
            print(f"📊 Average Fear & Greed Score: {avg_score:.1f}/100")
            if avg_score < 40:
                mood = "😨 Extreme Fear"
            elif avg_score < 45:
                mood = "😰 Fear"
            elif avg_score < 55:
                mood = "😐 Neutral"
            elif avg_score < 60:
                mood = "🙂 Greed"
            else:
                mood = "🤑 Extreme Greed"
            print(f"   Market Mood: {mood}")
    
    # Bot detection
    print("")
    print("🤖 Bot Detection:")
    bot_scores = []
    for post in posts_today:
        bot_signal = session.query(BotSignal).filter_by(
            post_id=post.post_id
        ).first()
        if bot_signal:
            bot_scores.append(bot_signal.score)
    
    if bot_scores:
        avg_bot = sum(bot_scores) / len(bot_scores)
        likely_bots = sum(1 for s in bot_scores if s > 0.7)
        print(f"   Average bot score: {avg_bot:.2f}")
        print(f"   Likely bots (>0.7): {likely_bots}/{len(bot_scores)}")
    else:
        print("   No bot detection data yet")
    
    # Sample posts
    print("")
    print("📝 Sample Posts:")
    print("-" * 60)
    
    sample_posts = posts_today[:5]
    for i, post in enumerate(sample_posts, 1):
        author = session.query(Author).filter_by(user_id=post.author_id).first()
        sentiment = session.query(SentimentScore).filter_by(post_id=post.post_id).first()
        
        print(f"\n{i}. @{author.username if author else 'unknown'}")
        print(f"   {post.text[:100]}{'...' if len(post.text) > 100 else ''}")
        
        if sentiment:
            if sentiment.score:
                score_label = "Fear" if sentiment.score < 40 else "Neutral" if sentiment.score < 60 else "Greed"
                print(f"   Sentiment: {sentiment.score:.0f}/100 ({score_label}) - {sentiment.classification.value}")
            else:
                print(f"   Sentiment: {sentiment.classification.value}")
        else:
            print(f"   Sentiment: Not analyzed yet")
    
    session.close()
    
    print("")
    print("=" * 60)
    print("✅ Analysis complete!")


if __name__ == "__main__":
    main()
