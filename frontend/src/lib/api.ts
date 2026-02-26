import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/auth/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// ---- Auth ----
export const authApi = {
  register: (data: { email: string; username: string; password: string }) =>
    api.post("/auth/register", data),
  login: (username: string, password: string) => {
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return api.post("/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },
  me: () => api.get("/auth/me"),
};

// ---- Books ----
export const booksApi = {
  list: (params?: { search?: string; genre?: string; skip?: number; limit?: number }) =>
    api.get("/books", { params }),
  get: (id: number) => api.get(`/books/${id}`),
  create: (formData: FormData) => api.post("/books", formData),
  update: (id: number, data: object) => api.put(`/books/${id}`, data),
  delete: (id: number) => api.delete(`/books/${id}`),
};

// ---- Borrows ----
export const borrowsApi = {
  borrow: (bookId: number) => api.post(`/borrows/${bookId}`),
  return: (borrowId: number) => api.post(`/borrows/${borrowId}/return`),
  mine: () => api.get("/borrows/me"),
};

// ---- Reviews ----
export const reviewsApi = {
  forBook: (bookId: number) => api.get(`/reviews/book/${bookId}`),
  create: (bookId: number, data: { rating: number; text?: string }) =>
    api.post(`/reviews/book/${bookId}`, data),
  delete: (reviewId: number) => api.delete(`/reviews/${reviewId}`),
};

// ---- Recommendations ----
export const recommendationsApi = {
  get: (limit = 10) => api.get("/recommendations", { params: { limit } }),
};

// ---- Preferences ----
export const preferencesApi = {
  get: () => api.get("/preferences"),
  update: (data: { favorite_genres?: string; favorite_authors?: string }) =>
    api.put("/preferences", data),
};
