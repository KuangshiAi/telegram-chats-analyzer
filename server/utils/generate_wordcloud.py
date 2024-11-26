# utils/wordcloud.py

import matplotlib
matplotlib.use('Agg')
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import os
import re

def generate_wordcloud(text_data, output_name='wordcloud.png'):
    # Combine all text data into one string
    text = ' '.join(text_data)

    # Remove URLs, mentions, and other unwanted patterns
    text = re.sub(r'http\S+', '', text)  # remove URLs
    text = re.sub(r'@\w+', '', text)     # remove mentions
    text = re.sub(r'#\w+', '', text)     # remove hashtags
    text = re.sub(r'\d+', '', text)      # remove numbers

    # Set stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(['rt', 'via', 'amp'])  # add any other unwanted words

    # Generate a word cloud object
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        stopwords=stopwords,
        max_words=200,
        max_font_size=100,
        random_state=42
    ).generate(text)

    # Save the word cloud image
    plt.figure(figsize=(20, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    # Ensure the static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    output_path = os.path.join('static', output_name)
    plt.savefig(output_path, format='png')
    plt.close()
    return output_path
