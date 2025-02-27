import streamlit as st
import feedparser
from newspaper import Article
from agno.models.openai import OpenAIChat

# Streamlit UI Setup
st.set_page_config(page_title="AI News Fetcher", page_icon="📰", layout="wide")
st.title("📰 AI-Powered News Fetcher")
st.caption("Get the latest news on any topic, summarized by GPT-4o")

# Sidebar - API Key Input & Configurations
st.sidebar.title("🔧 Configuration")
openai_api_key = st.sidebar.text_input("Enter OpenAI API Key:", type="password")

# Topic Input
topic = st.text_input("Enter a topic to fetch the latest news:")

# Fetch news function
def fetch_news(topic):
    feed_url = f"https://news.google.com/rss/search?q={topic}"
    feed = feedparser.parse(feed_url)
    return feed.entries[:5]  # Fetch top 5 news articles

# Summarize articles using GPT-4o
def summarize_article(url, api_key):
    try:
        article = Article(url)
        article.download()
        article.parse()
        content = article.text[:2000]  # Limit text to 2000 chars
        
        model = OpenAIChat(id="gpt-4o", api_key=api_key)
        summary = model.run(f"Summarize this news article: {content}")
        return summary.content
    except Exception as e:
        return "Error processing article."

# Fetch and Display News
if st.button("Fetch News 📰") and openai_api_key:
    with st.spinner("Fetching latest news..."):
        news_items = fetch_news(topic)
        if news_items:
            for item in news_items:
                st.subheader(item.title)
                st.write(f"📰 [Read Full Article]({item.link})")
                summary = summarize_article(item.link, openai_api_key)
                st.write("✍️ GPT-4o Summary:")
                st.success(summary)
        else:
            st.warning("No news articles found. Try another topic.")
else:
    st.info("Enter an API key and a topic to fetch news.")
