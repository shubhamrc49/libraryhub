"use client";
import { useEffect, useState } from "react";
import { recommendationsApi } from "@/lib/api";
import Link from "next/link";
import { Star, Sparkles, BookOpen } from "lucide-react";

interface Recommendation {
  book: { id: number; title: string; author: string; genre?: string; avg_rating?: number; ai_summary?: string };
  score: number;
  reason: string;
}

export default function RecommendationsPage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    recommendationsApi.get(10)
      .then((r) => setRecs(r.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-accent-500/10 p-2 rounded-xl">
          <Sparkles className="w-6 h-6 text-accent-500" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Recommended For You</h1>
          <p className="text-gray-500 text-sm">Personalized picks based on your reading history & preferences</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-accent-500 border-t-transparent rounded-full" />
        </div>
      ) : recs.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <Sparkles className="w-16 h-16 mx-auto mb-4 opacity-30" />
          <p>Borrow and review some books to get personalized recommendations!</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-5">
          {recs.map((rec, i) => (
            <div key={rec.book.id} className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition overflow-hidden">
              <div className="flex items-start gap-4 p-5">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-accent-500/20 to-primary-500/20 rounded-xl flex items-center justify-center font-bold text-accent-600 text-lg">
                  #{i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <Link href={`/books/${rec.book.id}`}>
                    <h3 className="font-semibold text-gray-900 hover:text-primary-600 transition truncate">{rec.book.title}</h3>
                  </Link>
                  <p className="text-sm text-gray-500">{rec.book.author}</p>
                  <div className="flex gap-2 mt-1.5 flex-wrap">
                    {rec.book.genre && (
                      <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">{rec.book.genre}</span>
                    )}
                    {rec.book.avg_rating && (
                      <span className="text-xs flex items-center gap-0.5 text-yellow-600">
                        <Star className="w-3 h-3 fill-current" /> {rec.book.avg_rating.toFixed(1)}
                      </span>
                    )}
                    <span className="text-xs text-accent-600 font-medium">
                      {Math.round(rec.score * 100)}% match
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mt-2 italic">"{rec.reason}"</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
