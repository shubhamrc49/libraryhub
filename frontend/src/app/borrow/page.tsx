"use client";
import { useEffect, useState } from "react";
import { borrowsApi } from "@/lib/api";
import { BookMarked, CheckCircle, Clock } from "lucide-react";

interface Borrow {
  id: number; book_id: number; book_title?: string;
  borrowed_at: string; returned_at?: string; is_returned: boolean;
}

export default function BorrowPage() {
  const [borrows, setBorrows] = useState<Borrow[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBorrows = async () => {
    try {
      const res = await borrowsApi.mine();
      setBorrows(res.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchBorrows(); }, []);

  const handleReturn = async (borrowId: number) => {
    try {
      await borrowsApi.return(borrowId);
      await fetchBorrows();
    } catch (e: any) { alert(e.response?.data?.detail || "Error returning book"); }
  };

  const active = borrows.filter((b) => !b.is_returned);
  const returned = borrows.filter((b) => b.is_returned);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-primary-100 p-2 rounded-xl">
          <BookMarked className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">My Books</h1>
          <p className="text-gray-500 text-sm">{active.length} currently borrowed</p>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <>
          {active.length > 0 && (
            <div className="mb-8">
              <h2 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-500" /> Currently Borrowed
              </h2>
              <div className="space-y-3">
                {active.map((b) => (
                  <div key={b.id} className="bg-white border border-orange-100 rounded-xl p-4 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{b.book_title || `Book #${b.book_id}`}</p>
                      <p className="text-sm text-gray-500">Borrowed {new Date(b.borrowed_at).toLocaleDateString()}</p>
                    </div>
                    <button
                      onClick={() => handleReturn(b.id)}
                      className="bg-primary-600 text-white px-4 py-1.5 rounded-lg text-sm hover:bg-primary-700 transition"
                    >
                      Return
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {returned.length > 0 && (
            <div>
              <h2 className="font-semibold text-gray-700 mb-3 flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" /> Returned
              </h2>
              <div className="space-y-2">
                {returned.map((b) => (
                  <div key={b.id} className="bg-white border border-gray-100 rounded-xl p-4 flex items-center justify-between opacity-70">
                    <div>
                      <p className="font-medium text-gray-700">{b.book_title || `Book #${b.book_id}`}</p>
                      <p className="text-sm text-gray-400">
                        Borrowed {new Date(b.borrowed_at).toLocaleDateString()} · 
                        Returned {b.returned_at ? new Date(b.returned_at).toLocaleDateString() : "—"}
                      </p>
                    </div>
                    <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">Returned</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {borrows.length === 0 && (
            <div className="text-center py-20 text-gray-400">
              <BookMarked className="w-16 h-16 mx-auto mb-4 opacity-30" />
              <p>No borrow history yet. Browse the catalog to get started!</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
