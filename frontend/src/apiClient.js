const API_BASE = (
  import.meta.env.VITE_API_URL || "http://localhost:5000/api"
).replace(/\/$/, "");

function getTokens() {
  try {
    return JSON.parse(localStorage.getItem("tokens")) || {};
  } catch (err) {
    return {};
  }
}

function storeTokens(tokens) {
  localStorage.setItem("tokens", JSON.stringify(tokens));
}

function clearTokens() {
  localStorage.removeItem("tokens");
}

let refreshPromise = null;

async function refreshToken(token) {
  const res = await fetch(`${API_BASE}/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: token }),
  });
  if (!res.ok) return null;
  const body = await res.json();
  const updated = {
    accessToken: body.access_token,
    refreshToken: body.refresh_token,
  };
  storeTokens(updated);
  return updated;
}

export async function apiRequest(path, options = {}, config = {}) {
  const basePath = path.startsWith("/api") ? path.replace("/api", "") : path;
  const url = `${API_BASE}${basePath.startsWith("/") ? "" : "/"}${basePath}`;

  const tokens = getTokens();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  if (!config.skipAuth && tokens.accessToken) {
    headers.Authorization = `Bearer ${tokens.accessToken}`;
  }

  let response = await fetch(url, { ...options, headers });

  if (response.status === 401 && tokens.refreshToken && !config.skipRefresh) {
    if (!refreshPromise) {
      refreshPromise = refreshToken(tokens.refreshToken).finally(() => {
        refreshPromise = null;
      });
    }
    const refreshed = await refreshPromise;
    if (refreshed?.accessToken) {
      headers.Authorization = `Bearer ${refreshed.accessToken}`;
      response = await fetch(url, { ...options, headers });
    } else {
      clearTokens();
    }
  }

  return response;
}

export async function login(email, password) {
  const res = await apiRequest(
    "/login",
    { method: "POST", body: JSON.stringify({ email, password }) },
    { skipAuth: true },
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Login failed");
  }
  const body = await res.json();
  const tokens = {
    accessToken: body.access_token,
    refreshToken: body.refresh_token,
  };
  storeTokens(tokens);
  return { tokens, user: body.user };
}

export async function signup(username, email, password) {
  const res = await apiRequest(
    "/signup",
    { method: "POST", body: JSON.stringify({ username, email, password }) },
    { skipAuth: true },
  );
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Signup failed");
  }
  const body = await res.json();
  const tokens = {
    accessToken: body.access_token,
    refreshToken: body.refresh_token,
  };
  storeTokens(tokens);
  return { tokens, user: body.user };
}

export async function search(query) {
  const res = await apiRequest("/search", {
    method: "POST",
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Search failed");
  }
  return res.json();
}

export async function getTimeline(month) {
  const res = await apiRequest(`/timeline?month=${month}`, {
    method: "GET",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Failed to fetch timeline");
  }

  return res.json();
}

export async function deleteTimelineEntry(id) {
  const res = await apiRequest(`/timeline/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Delete failed");
  }

  return res.json();
}

export async function getCurrentUser() {
  const res = await apiRequest("/me", { method: "GET" });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Failed to fetch user");
  }

  return res.json();
}

export async function logout() {
  const res = await apiRequest("/logout", { method: "POST" });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.message || "Logout failed");
  }

  clearTokens();
}

export function getStoredTokens() {
  return getTokens();
}

export { storeTokens, clearTokens };
