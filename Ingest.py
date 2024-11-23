import pandas as pd
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

# Path to the CSV file
BOOKS_DATA_PATH = r"\replace\with\your\system\path\books_data.csv"

# Load the data from the CSV file
def load_books_data(file_path):
    """Load books data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

# Preprocess the data for embedding
def preprocess_books_data(df):
    """Combine relevant columns into a single text for embedding."""
    # Ensure columns are present
    required_columns = ["Title", "Author", "Description", "ratingsCount"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Combine title, author, description, and ratings into one text block
    df["content"] = (
        df["Title"] + " by " + df["Author"] + "\n" +
        "Description: " + df["Description"] + "\n" +
        "Ratings Count: " + df["ratingsCount"].astype(str)
    )
    # Fill NaN values with empty strings
    df["content"] = df["content"].fillna("")
    return df["content"].tolist()

def main():
    # Load the books data
    df = load_books_data(BOOKS_DATA_PATH)
    if df is None:
        print("Failed to load books data.")
        return

    # Preprocess the data
    book_texts = preprocess_books_data(df)

    # Split texts into manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=200)
    texts = text_splitter.split_texts(book_texts)

    # Loading Hugging Face embeddings
    embeddings = HuggingFaceEmbeddings(model_name="nomic-ai/nomic-embed-text-v1")

    # Creating FAISS vector store
    faiss_db = FAISS.from_texts(texts, embeddings)

    # Save the FAISS vector store locally
    faiss_db.save_local("books_vector_db")
    print("Vector database for books created and saved successfully!")

if __name__ == "__main__":
    main()
