"use client";
import { useEffect, useState } from "react";
import { booksApi, borrowsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import Link from "next/link";
import { Search, BookOpen, Star, Plus } from "lucide-react";

interface Book {
  id: number;
  title: string;
  author: string;
  genre?: string;
  year?: number;
  available_copies: number;
  total_copies: number;
  avg_rating?: number;
  ai_summary?: string;
  cover_path?: string;
}

export default function HomePage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [loading, setLoading] = useState(true);
  const { user } = useAuthStore();

  const fetchBooks = async () => {
    setLoading(true);
    try {
      const res = await booksApi.list({ search: search || undefined, genre: genre || undefined });
      setBooks(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBooks(); }, [search, genre]);

  const handleBorrow = async (bookId: number) => {
    if (!user) { window.location.href = "/auth/login"; return; }
    try {
      await borrowsApi.borrow(bookId);
      await fetchBooks();
      alert("Book borrowed successfully!");
    } catch (e: any) {
      alert(e.response?.data?.detail || "Failed to borrow");
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Library Catalog</h1>
          <p className="text-gray-500 mt-1">{books.length} books available</p>
        </div>
        {user && (
          <Link
            href="/books/add"
            className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition"
          >
            <Plus className="w-4 h-4" /> Add Book
          </Link>
        )}
      </div>

      {/* Search & Filter */}
      <div className="flex gap-3 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title or author..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <input
          type="text"
          placeholder="Filter by genre..."
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          className="w-48 px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Books Grid */}
      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
        </div>
      ) : books.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p className="text-lg">No books found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {books.map((book) => (
            <div key={book.id} className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition overflow-hidden">
              <div className="bg-gradient-to-br from-primary-100 to-accent-500/20 h-32 flex items-center justify-center">
                <BookOpen className="w-12 h-12 text-primary-600 opacity-60" />
              </div>
              <div className="p-4">
                <Link href={`/books/${book.id}`}>
                  <h3 className="font-semibold text-gray-900 hover:text-primary-600 transition line-clamp-2">{book.title}</h3>
                </Link>
                <p className="text-sm text-gray-500 mt-1">{book.author}</p>
                <div className="flex items-center gap-2 mt-2">
                  {book.genre && (
                    <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">{book.genre}</span>
                  )}
                  {book.avg_rating && (
                    <span className="text-xs flex items-center gap-0.5 text-yellow-600">
                      <Star className="w-3 h-3 fill-current" /> {book.avg_rating.toFixed(1)}
                    </span>
                  )}
                </div>
                {book.ai_summary && (
                  <p className="text-xs text-gray-400 mt-2 line-clamp-2">{book.ai_summary}</p>
                )}
                <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
                  <span className={`text-xs ${book.available_copies > 0 ? "text-green-600" : "text-red-500"}`}>
                    {book.available_copies}/{book.total_copies} available
                  </span>
                  <button
                    onClick={() => handleBorrow(book.id)}
                    disabled={book.available_copies === 0}
                    className="text-xs bg-primary-600 text-white px-3 py-1 rounded-full hover:bg-primary-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
                  >
                    Borrow
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
