# library_system.py

from typing import Dict, List, Optional
from datetime import datetime, timedelta

class Book:
    def __init__(self, book_id: str, title: str, author: str):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.is_available = True
        self.due_date: Optional[datetime] = None
        self.borrower: Optional[str] = None
    
    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ID: {self.book_id})"

class LibrarySystem:
    def __init__(self):
        self.books: Dict[str, Book] = {}
        self.loan_period = timedelta(days=14)
    
    def add_book(self, book_id: str, title: str, author: str) -> bool:
        """Add a new book to the library."""
        if book_id in self.books:
            return False
        self.books[book_id] = Book(book_id, title, author)
        return True
    
    def remove_book(self, book_id: str) -> bool:
        """Remove a book from the library."""
        if book_id not in self.books:
            return False
        del self.books[book_id]
        return True
    
    def borrow_book(self, book_id: str, user_id: str) -> bool:
        """Borrow a book from the library."""
        if book_id not in self.books:
            return False
        
        book = self.books[book_id]
        if not book.is_available:
            return False
        
        book.is_available = False
        book.borrower = user_id
        book.due_date = datetime.now() + self.loan_period
        return True
    
    def return_book(self, book_id: str) -> bool:
        """Return a book to the library."""
        if book_id not in self.books:
            return False
        
        book = self.books[book_id]
        if book.is_available:
            return False
        
        book.is_available = True
        book.borrower = None
        book.due_date = None
        return True
    
    def get_overdue_books(self) -> List[Book]:
        """Get a list of overdue books."""
        now = datetime.now()
        return [
            book for book in self.books.values()
            if not book.is_available and book.due_date and book.due_date < now
        ]
    
    def search_books(self, query: str) -> List[Book]:
        """Search for books by title or author."""
        query = query.lower()
        return [
            book for book in self.books.values()
            if query in book.title.lower() or query in book.author.lower()
        ]