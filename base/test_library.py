# test_library.py

import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from library_system import LibrarySystem, Book

class TestLibrarySystem(unittest.TestCase):
    def setUp(self):
        self.library = LibrarySystem()
        # Add some test books
        self.library.add_book("B1", "The Great Gatsby", "F. Scott Fitzgerald")
        self.library.add_book("B2", "1984", "George Orwell")
        self.library.add_book("B3", "Pride and Prejudice", "Jane Austen")

    def test_add_book_success(self):
        """Test adding a new book successfully."""
        result = self.library.add_book("B4", "New Book", "New Author")
        self.assertTrue(result)
        self.assertIn("B4", self.library.books)

    def test_add_book_duplicate(self):
        """Test adding a duplicate book."""
        result = self.library.add_book("B1", "Duplicate", "Author")
        self.assertFalse(result)

    def test_remove_book_success(self):
        """Test removing an existing book."""
        result = self.library.remove_book("B1")
        self.assertTrue(result)
        self.assertNotIn("B1", self.library.books)

    def test_remove_book_nonexistent(self):
        """Test removing a non-existent book."""
        result = self.library.remove_book("XX")
        self.assertFalse(result)

    def test_borrow_book_success(self):
        """Test borrowing an available book."""
        result = self.library.borrow_book("B1", "user1")
        self.assertTrue(result)
        self.assertFalse(self.library.books["B1"].is_available)

    def test_borrow_book_already_borrowed(self):
        """Test borrowing an already borrowed book."""
        self.library.borrow_book("B1", "user1")
        result = self.library.borrow_book("B1", "user2")
        self.assertFalse(result)

    def test_return_book_success(self):
        """Test returning a borrowed book."""
        self.library.borrow_book("B1", "user1")
        result = self.library.return_book("B1")
        self.assertTrue(result)
        self.assertTrue(self.library.books["B1"].is_available)

    def test_return_book_not_borrowed(self):
        """Test returning a book that wasn't borrowed."""
        result = self.library.return_book("B1")
        self.assertFalse(result)

    @patch('library_system.datetime')
    def test_get_overdue_books(self, mock_datetime):
        """Test getting overdue books."""
        # Set current time
        current_time = datetime.now()
        mock_datetime.now.return_value = current_time
        
        # Borrow books
        self.library.borrow_book("B1", "user1")
        self.library.borrow_book("B2", "user2")
        
        # Make B1 overdue
        self.library.books["B1"].due_date = current_time - timedelta(days=1)
        # Make B2 not overdue
        self.library.books["B2"].due_date = current_time + timedelta(days=1)
        
        overdue_books = self.library.get_overdue_books()
        self.assertEqual(len(overdue_books), 1)
        self.assertEqual(overdue_books[0].book_id, "B1")

    def test_search_books_by_title(self):
        """Test searching books by title."""
        results = self.library.search_books("great")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].book_id, "B1")

    def test_search_books_by_author(self):
        """Test searching books by author."""
        results = self.library.search_books("Austen")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].book_id, "B3")

    def test_search_books_no_results(self):
        """Test searching with no matching results."""
        results = self.library.search_books("xyz123")
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()