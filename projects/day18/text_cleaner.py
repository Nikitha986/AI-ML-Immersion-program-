import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
# 1. Setup
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
def clean_bio(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize (Split into words)

    None
    tokens = word_tokenize(text)
    # Remove Stopwords
    stop_words = set(stopwords.words('english'))
    filtered_text = [w for w in tokens if not w in stop_words]
    return " ".join(filtered_text)
sample_bio = "I love Hiking in the mountains and Coding late at night!"
print(f"Cleaned Bio: {clean_bio(sample_bio)}")