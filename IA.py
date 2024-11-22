import numpy as np
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

###Function that ensures that the text is cleaned correcly
def limpiezaDatos(text):
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\W', ' ', text)
    text = text.strip().lower()
    return text
###Function to clean and rate the new comment
def clasificarMensajes(message):
    message_features = vectorizer.transform([message]).toarray()
    prediction = text_classifier.predict(message_features) 
    print(prediction)
    return "Bueno" if prediction[0] == 1 else "Malo"

###Checks to se if it can read the document criticasCuradas.csv and if the document have Rating and Review
try:
    comentarios = pd.read_csv("reviews.csv")
except FileNotFoundError:
    raise FileNotFoundError("El archivo no se encuentra.")

if 'Review' not in comentarios.columns or 'Rating' not in comentarios.columns:
    raise ValueError("El documento debe tener Review y Rating")

###Shuffles the comentarios to make the training more effective, cleans the text and converts all the Ratings from 1 to 4 to 0, and all the 10 comentaries to 1
comentarios = comentarios.sample(frac=1, random_state=42).reset_index(drop=True)
comentarios['processed'] = comentarios['Review'].astype(str).apply(limpiezaDatos)
comentarios['Rating'] = comentarios['Rating'].apply(lambda x: 1 if x == 10 else 0 if x < 5 else np.nan)

###Removes rows that are not usefull and converts the ratings to ints
comentarios.dropna(subset=['Rating'], inplace=True)
comentarios['Rating'] = comentarios['Rating'].astype(int)

###create TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, min_df=5, max_df=0.8, ngram_range=(1, 2))
processed_features = vectorizer.fit_transform(comentarios['processed'])

###define x and y
X = processed_features
y = comentarios['Rating']

###Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

###Create and train the model    
text_classifier = RandomForestClassifier(n_estimators=200, random_state=42)
text_classifier.fit(X_train, y_train)

###mAke predictions on the test set
predictions = text_classifier.predict(X_test)

###Print metrics
print("Confusion Matrix:\n", confusion_matrix(y_test, predictions))
print("\nClassification Report:\n", classification_report(y_test, predictions))
print("\nAccuracy Score:", accuracy_score(y_test, predictions))
print("\nEscribe un mensaje escribe salir para terminar")

###Bucle que pide mensaje, los limpia 
while True:
    nuevoMensaje = input("Mensaje: ").strip()
    nuevoMensaje = limpiezaDatos(nuevoMensaje)
    if nuevoMensaje.lower()=="salir":
        break
    result = clasificarMensajes(nuevoMensaje)
    print(f"Tu comentario es: {result}")