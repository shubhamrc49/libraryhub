"use client";
import { useEffect, useState } from "react";
import { preferencesApi } from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import { User, Settings } from "lucide-react";

export default function ProfilePage() {
  const { user } = useAuthStore();
  const [prefs, setPrefs] = useState({ favorite_genres: "", favorite_authors: "" });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    preferencesApi.get().then((r) => setPrefs(r.data)).catch(() => {});
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    await preferencesApi.update(prefs);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  if (!user) return (
    <div className="text-center py-20 text-gray-400">Please log in to view your profile.</div>
  );

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* User Info */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center text-white text-2xl font-bold">
            {user.username[0].toUpperCase()}
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">{user.username}</h1>
            <p className="text-gray-500">{user.email}</p>
            {user.is_admin && (
              <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full mt-1 inline-block">Admin</span>
            )}
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-2 mb-5">
          <Settings className="w-5 h-5 text-primary-600" />
          <h2 className="font-bold text-gray-900">Reading Preferences</h2>
        </div>
        <p className="text-sm text-gray-500 mb-4">These preferences help improve your book recommendations.</p>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Favorite Genres</label>
            <input
              type="text"
              placeholder="e.g. Fiction, Science, History (comma-separated)"
              value={prefs.favorite_genres}
              onChange={(e) => setPrefs((p) => ({...p, favorite_genres: e.target.value}))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Favorite Authors</label>
            <input
              type="text"
              placeholder="e.g. Isaac Asimov, J.K. Rowling (comma-separated)"
              value={prefs.favorite_authors}
              onChange={(e) => setPrefs((p) => ({...p, favorite_authors: e.target.value}))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            type="submit"
            className={`w-full py-2.5 rounded-lg font-medium transition ${saved ? "bg-green-500 text-white" : "bg-primary-600 text-white hover:bg-primary-700"}`}
          >
            {saved ? "✓ Saved!" : "Save Preferences"}
          </button>
        </form>
      </div>
    </div>
  );
}
