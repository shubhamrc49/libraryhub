"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { booksApi, reviewsApi, borrowsApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import { Star, BookOpen, Download, MessageSquare } from "lucide-react";

interface Book {
  id: number; title: string; author: string; genre?: string; year?: number;
  description?: string; ai_summary?: string; review_consensus?: string;
  avg_rating?: number; available_copies: number; total_copies: number;
  file_path?: string;
}
interface Review {
  id: number; rating: number; text?: string; username?: string;
  sentiment?: string; created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function BookDetailPage() {
  const { id } = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [newReview, setNewReview] = useState({ rating: 5, text: "" });
  const { user } = useAuthStore();

  useEffect(() => {
    booksApi.get(Number(id)).then((r) => setBook(r.data));
    reviewsApi.forBook(Number(id)).then((r) => setReviews(r.data));
  }, [id]);

  const handleBorrow = async () => {
    if (!user) { window.location.href = "/auth/login"; return; }
    try {
      await borrowsApi.borrow(Number(id));
      const r = await booksApi.get(Number(id));
      setBook(r.data);
      alert("Borrowed successfully!");
    } catch (e: any) { alert(e.response?.data?.detail || "Error"); }
  };

  const handleReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) { window.location.href = "/auth/login"; return; }
    try {
      const r = await reviewsApi.create(Number(id), newReview);
      setReviews([r.data, ...reviews]);
      setNewReview({ rating: 5, text: "" });
    } catch (e: any) { alert(e.response?.data?.detail || "Error"); }
  };

  if (!book) return <div className="flex justify-center py-20"><div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" /></div>;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="bg-gradient-to-r from-primary-900 to-accent-600 p-8 text-white">
          <div className="flex items-start gap-6">
            <div className="bg-white/20 rounded-xl p-4">
              <BookOpen className="w-16 h-16" />
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold">{book.title}</h1>
              <p className="text-primary-100 text-lg mt-1">by {book.author}</p>
              <div className="flex gap-3 mt-3 flex-wrap">
                {book.genre && <span className="bg-white/20 px-3 py-1 rounded-full text-sm">{book.genre}</span>}
                {book.year && <span className="bg-white/20 px-3 py-1 rounded-full text-sm">{book.year}</span>}
                {book.avg_rating && (
                  <span className="bg-yellow-400/20 px-3 py-1 rounded-full text-sm flex items-center gap-1">
                    <Star className="w-3 h-3 fill-current" /> {book.avg_rating.toFixed(1)}
                  </span>
                )}
              </div>
            </div>
            <div className="text-right">
              <p className="text-primary-100 text-sm">{book.available_copies}/{book.total_copies} available</p>
              <button
                onClick={handleBorrow}
                disabled={book.available_copies === 0}
                className="mt-2 bg-white text-primary-900 font-semibold px-6 py-2 rounded-lg hover:bg-primary-50 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                Borrow
              </button>
              {book.file_path && (
                <a
                  href={`${API_URL}/books/${book.id}/download`}
                  className="mt-2 flex items-center gap-1 text-sm text-primary-100 hover:text-white"
                >
                  <Download className="w-4 h-4" /> Download
                </a>
              )}
            </div>
          </div>
        </div>

        <div className="p-8 grid md:grid-cols-2 gap-6">
          {book.description && (
            <div>
              <h3 className="font-semibold text-gray-700 mb-2">Description</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{book.description}</p>
            </div>
          )}
          {book.ai_summary && (
            <div className="bg-primary-50 rounded-xl p-4">
              <h3 className="font-semibold text-primary-700 mb-2 flex items-center gap-1">
                ✨ AI Summary
              </h3>
              <p className="text-primary-800 text-sm leading-relaxed">{book.ai_summary}</p>
            </div>
          )}
          {book.review_consensus && (
            <div className="bg-purple-50 rounded-xl p-4 md:col-span-2">
              <h3 className="font-semibold text-purple-700 mb-2">Reader Consensus</h3>
              <p className="text-purple-800 text-sm leading-relaxed">{book.review_consensus}</p>
            </div>
          )}
        </div>

        {/* Reviews */}
        <div className="px-8 pb-8">
          <h3 className="font-bold text-gray-900 text-xl mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5" /> Reviews ({reviews.length})
          </h3>

          {/* Add review */}
          {user && (
            <form onSubmit={handleReview} className="bg-gray-50 rounded-xl p-4 mb-6">
              <h4 className="font-medium text-gray-700 mb-3">Write a Review</h4>
              <div className="flex gap-2 mb-3">
                {[1,2,3,4,5].map((n) => (
                  <button key={n} type="button" onClick={() => setNewReview(r => ({...r, rating: n}))}
                    className={`w-8 h-8 rounded-full text-sm font-medium transition ${n <= newReview.rating ? "bg-yellow-400 text-yellow-900" : "bg-gray-200 text-gray-500"}`}>
                    {n}
                  </button>
                ))}
              </div>
              <textarea
                placeholder="Share your thoughts... (optional)"
                value={newReview.text}
                onChange={(e) => setNewReview(r => ({...r, text: e.target.value}))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={3}
              />
              <button type="submit" className="mt-2 bg-primary-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-primary-700 transition">
                Submit Review
              </button>
            </form>
          )}

          {/* Review list */}
          <div className="space-y-3">
            {reviews.map((r) => (
              <div key={r.id} className="bg-white border border-gray-100 rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                      {r.username?.[0]?.toUpperCase()}
                    </div>
                    <span className="font-medium text-sm">{r.username}</span>
                    {r.sentiment && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        r.sentiment === "positive" ? "bg-green-100 text-green-700" :
                        r.sentiment === "negative" ? "bg-red-100 text-red-700" :
                        "bg-gray-100 text-gray-600"
                      }`}>{r.sentiment}</span>
                    )}
                  </div>
                  <div className="flex">
                    {Array.from({length: 5}).map((_, i) => (
                      <Star key={i} className={`w-3 h-3 ${i < r.rating ? "fill-yellow-400 text-yellow-400" : "text-gray-200"}`} />
                    ))}
                  </div>
                </div>
                {r.text && <p className="text-sm text-gray-600 mt-2">{r.text}</p>}
                <p className="text-xs text-gray-400 mt-1">{new Date(r.created_at).toLocaleDateString()}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
