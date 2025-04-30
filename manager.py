# Personal Library Manager using Streamlit
# This script allows users to manage their personal book collection

import streamlit as st
import json
import os
from typing import List, Dict, Any

# Constants
BOOKS_FILE = "books_data.json"
GENRES = ["Fiction", "Non-Fiction", "Science", "Technology", "Fantasy", "Romance", "History", "Other"]

# Function to load books from JSON file
def load_books() -> List[Dict[str, Any]]:
    """Load books from JSON file or return empty list if file doesn't exist."""
    if os.path.exists(BOOKS_FILE):
        try:
            with open(BOOKS_FILE, "r") as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

# Function to save books to JSON file
def save_books(books: List[Dict[str, Any]]) -> None:
    """Save books to JSON file."""
    with open(BOOKS_FILE, "w") as file:
        json.dump(books, file, indent=4)

# Function to add a new book
def add_book(books: List[Dict[str, Any]]) -> None:
    """UI for adding a new book."""
    st.header("➕ Add a New Book")
    
    with st.form("add_book_form"):
        title = st.text_input("Book Title*", help="Required field")
        author = st.text_input("Author*", help="Required field")
        year = st.text_input("Publication Year")
        genre = st.selectbox("Genre", GENRES)
        read_status = st.radio("Reading Status", ["Read", "Unread"])
        
        submitted = st.form_submit_button("Add Book")
        if submitted:
            if not title or not author:
                st.error("Title and Author are required fields!")
            else:
                new_book = {
                    "title": title.strip(),
                    "author": author.strip(),
                    "year": year.strip(),
                    "genre": genre,
                    "read": read_status == "Read"
                }
                books.append(new_book)
                save_books(books)
                st.success(f"✅ Book '{title}' added successfully!")
                st.rerun()

# Function to view all books
def view_books(books: List[Dict[str, Any]]) -> None:
    """UI for viewing all books."""
    st.header("📖 Your Book Collection")
    
    if not books:
        st.warning("No books found. Please add a book.")
        return
    
    # Search and filter options
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search by title or author")
    with col2:
        genre_filter = st.selectbox("Filter by genre", ["All Genres"] + GENRES)
    
    # Filter books
    filtered_books = books
    if search_term:
        search_term = search_term.lower()
        filtered_books = [
            book for book in filtered_books 
            if search_term in book["title"].lower() or search_term in book["author"].lower()
        ]
    if genre_filter != "All Genres":
        filtered_books = [book for book in filtered_books if book["genre"] == genre_filter]
    
    # Display books
    if not filtered_books:
        st.info("No books match your search criteria.")
    else:
        for i, book in enumerate(filtered_books, 1):
            with st.expander(f"{i}. 📚 {book['title']}"):
                st.write(f"**Author:** {book['author']}")
                st.write(f"**Year:** {book['year']}")
                st.write(f"**Genre:** {book['genre']}")
                st.write(f"**Status:** {'✅ Read' if book['read'] else '📖 Unread'}")

# Function to update a book
def update_book(books: List[Dict[str, Any]]) -> None:
    """UI for updating book details."""
    st.header("✏️ Update Book Details")
    
    if not books:
        st.warning("No books available to update.")
        return
    
    book_titles = [book["title"] for book in books]
    selected_title = st.selectbox("Select a book to update", book_titles)
    
    # Find the selected book
    selected_book = next((book for book in books if book["title"] == selected_title), None)
    if not selected_book:
        st.error("Book not found!")
        return
    
    with st.form("update_book_form"):
        new_title = st.text_input("Title*", selected_book["title"], help="Required field")
        new_author = st.text_input("Author*", selected_book["author"], help="Required field")
        new_year = st.text_input("Publication Year", selected_book["year"])
        new_genre = st.selectbox("Genre", GENRES, index=GENRES.index(selected_book["genre"]))
        new_read_status = st.radio("Reading Status", ["Read", "Unread"], 
                                index=0 if selected_book["read"] else 1)
        
        submitted = st.form_submit_button("Update Book")
        if submitted:
            if not new_title or not new_author:
                st.error("Title and Author are required fields!")
            else:
                selected_book["title"] = new_title.strip()
                selected_book["author"] = new_author.strip()
                selected_book["year"] = new_year.strip()
                selected_book["genre"] = new_genre
                selected_book["read"] = new_read_status == "Read"
                save_books(books)
                st.success("✅ Book updated successfully!")
                st.rerun()

# Function to delete a book
def delete_book(books: List[Dict[str, Any]]) -> None:
    """UI for deleting a book."""
    st.header("🗑️ Remove a Book")
    
    if not books:
        st.warning("No books available to delete.")
        return
    
    book_titles = [book["title"] for book in books]
    selected_title = st.selectbox("Select a book to delete", book_titles)
    
    if st.button("Delete Book", key="delete_button"):
        updated_books = [book for book in books if book["title"] != selected_title]
        save_books(updated_books)
        st.success(f"🗑️ Book '{selected_title}' deleted successfully!")
        st.rerun()

# Function to show reading progress
def show_reading_progress(books: List[Dict[str, Any]]) -> None:
    """UI for displaying reading statistics."""
    st.header("📊 Reading Progress")
    
    total_books = len(books)
    read_books = sum(1 for book in books if book["read"])
    unread_books = total_books - read_books
    
    if total_books > 0:
        completion_rate = (read_books / total_books) * 100
        st.metric("Total Books", total_books)
        col1, col2 = st.columns(2)
        col1.metric("Books Read", read_books)
        col2.metric("Books Unread", unread_books)
        
        st.progress(int(completion_rate))
        st.write(f"📊 Completion Rate: **{completion_rate:.2f}%**")
        
        # Genre distribution
        st.subheader("Genre Distribution")
        genre_counts = {}
        for book in books:
            genre = book["genre"]
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        if genre_counts:
            st.bar_chart(genre_counts)
    else:
        st.warning("No books in your library yet. Add some books to track your progress!")

# Main function
def main():
    """Main application function."""
    st.set_page_config(page_title="BookShelf AI", page_icon="📚")
    st.title("📚 BookShelf AI - Personal Library Manager")
    st.sidebar.title("Menu")
    
    # Load books data
    books = load_books()
    
    # Navigation menu
    menu_options = {
        "Add Book": lambda: add_book(books),
        "View Books": lambda: view_books(books),
        "Update Book": lambda: update_book(books),
        "Delete Book": lambda: delete_book(books),
        "Reading Progress": lambda: show_reading_progress(books)
    }
    
    selected_option = st.sidebar.radio("Select an option:", list(menu_options.keys()))
    menu_options[selected_option]()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    **BookShelf AI** helps you manage your personal book collection.
    - Add new books
    - Track reading progress
    - Organize by genres
    """)

if __name__ == "__main__":
    main()