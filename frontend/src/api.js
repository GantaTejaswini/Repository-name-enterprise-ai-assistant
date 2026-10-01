import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export async function login(email, password) {
  const response = await api.post("/api/auth/login", {
    email,
    password,
  });

  return response.data;
}

export async function sendChat(question, token, topK = 5) {
  const response = await api.post(
    "/api/chat",
    {
      question,
      top_k: topK,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return response.data;
}

export async function getHealth() {
  const response = await api.get("/health");
  return response.data;
}

export async function getDiagnostics(token) {
  const response = await api.get("/api/diagnostics", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
}

export async function getDocuments(token) {
  const response = await api.get("/api/documents", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return response.data;
}

export async function uploadDocument(file, token) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    "/api/documents/upload",
    formData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return response.data;
}

export async function deleteDocument(documentId, token) {
  const response = await api.delete(
    `/api/documents/${documentId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  return response.data;
}

export default api;