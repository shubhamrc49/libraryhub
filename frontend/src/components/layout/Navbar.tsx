"use client";
import Link from "next/link";
import { useAuthStore } from "@/lib/auth";
import { useEffect } from "react";
import { authApi } from "@/lib/api";
import { BookOpen, Home, Star, User, LogOut, BookMarked } from "lucide-react";

export default function Navbar() {
  const { user, token, setAuth, logout, loadFromStorage } = useAuthStore();

  useEffect(() => {
    loadFromStorage();
  }, []);

  useEffect(() => {
    if (token && !user) {
      authApi.me().then((res) => setAuth(res.data, token)).catch(() => logout());
    }
  }, [token]);

  return (
    <nav className="bg-gradient-to-r from-primary-900 to-accent-600 text-white shadow-lg">
      <div className="container mx-auto px-4 max-w-6xl flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <BookOpen className="w-6 h-6" />
          LibraryHub
        </Link>
        <div className="flex items-center gap-4 text-sm">
          <Link href="/" className="flex items-center gap-1 hover:text-primary-100 transition">
            <Home className="w-4 h-4" /> Browse
          </Link>
          {user ? (
            <>
              <Link href="/borrow" className="flex items-center gap-1 hover:text-primary-100 transition">
                <BookMarked className="w-4 h-4" /> My Books
              </Link>
              <Link href="/recommendations" className="flex items-center gap-1 hover:text-primary-100 transition">
                <Star className="w-4 h-4" /> For You
              </Link>
              <Link href="/profile" className="flex items-center gap-1 hover:text-primary-100 transition">
                <User className="w-4 h-4" /> {user.username}
              </Link>
              <button
                onClick={logout}
                className="flex items-center gap-1 hover:text-red-300 transition"
              >
                <LogOut className="w-4 h-4" /> Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/auth/login" className="hover:text-primary-100 transition">Login</Link>
              <Link
                href="/auth/register"
                className="bg-white text-primary-900 px-3 py-1 rounded-full font-medium hover:bg-primary-50 transition"
              >
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
