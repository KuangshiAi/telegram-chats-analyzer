from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import nltk

nltk.download("vader_lexicon")

# Initialize Sentiment Analyzer
sentiment_analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment_and_generate_tsne(text_data, output_path="static/sentiment_tsne.png"):
    """
    Perform sentiment analysis and generate a t-SNE scatterplot based on emotional tone.

    Parameters:
        text_data (list of str): List of chat messages to analyze.
        output_path (str): Path to save the generated t-SNE scatterplot.

    Returns:
        str: Path to the saved scatterplot image.
    """
    if not text_data:
        raise ValueError("No text data provided for sentiment analysis.")

    # Perform sentiment analysis
    sentiment_scores = []
    for text in text_data:
        scores = sentiment_analyzer.polarity_scores(text)
        sentiment_scores.append([scores["pos"], scores["neu"], scores["neg"]])

    # Normalize sentiment scores
    sentiment_scores_scaled = StandardScaler().fit_transform(sentiment_scores)

    # Determine appropriate perplexity
    n_samples = len(sentiment_scores_scaled)
    perplexity = min(30, max(2, n_samples // 3))  # Set perplexity based on n_samples

    # Apply t-SNE
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    tsne_results = tsne.fit_transform(sentiment_scores_scaled)

    # Generate scatterplot
    plt.figure(figsize=(8, 6))
    plt.scatter(
        tsne_results[:, 0], 
        tsne_results[:, 1], 
        alpha=0.6, 
        c=sentiment_scores_scaled[:, 0], 
        cmap="viridis"
    )
    plt.colorbar(label="Positive Sentiment")
    plt.title("t-SNE Clustering of Sentiments")
    plt.xlabel("t-SNE Dimension 1")
    plt.ylabel("t-SNE Dimension 2")
    plt.savefig(output_path, dpi=1000)
    plt.close()

    return output_path
