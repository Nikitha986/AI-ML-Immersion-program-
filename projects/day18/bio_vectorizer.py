from sklearn.feature_extraction.text import TfidfVectorizer
# Sample Dataset of MeetMux User Bios
bios = [
"Expert in Python and Machine Learning for social good.",
"Professional Chef who loves outdoor Hiking and mountains.",
"Machine Learning enthusiast and mountain hiker."
]
# 1. Initialize TF-IDF
vectorizer = TfidfVectorizer()
# 2. Fit and Transform
tfidf_matrix = vectorizer.fit_transform(bios)

# 3. View Features (Words)
print("Vocabulary:", vectorizer.get_feature_names_out())
print("Vector Shape:", tfidf_matrix.toarray().shape)