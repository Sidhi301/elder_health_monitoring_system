/*
  This file handles login state, token storage, and secure API requests.
  These helper functions are reused by all pages.
*/

const API_BASE_URL = "https://elder-health-monitoring-system-2.onrender.com";


function saveSession(token, user) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
}

function getToken() {
    return localStorage.getItem("token");
}

function getUser() {
    const userText = localStorage.getItem("user");
    if (!userText) {
        return null;
    }
    return JSON.parse(userText);
}

function clearSession() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
}

function logoutUser() {
    clearSession();
    window.location.href = "login.html";
}

function requireLogin() {
    if (!getToken() || !getUser()) {
        window.location.href = "login.html";
        return false;
    }
    return true;
}

function requireRole(allowedRoles) {
    const user = getUser();
    if (!user) {
        window.location.href = "login.html";
        return false;
    }
    if (!allowedRoles.includes(user.role)) {
        window.location.href = "dashboard.html";
        return false;
    }
    return true;
}

function getErrorMessage(data) {
    if (!data) {
        return "Request failed.";
    }

    if (typeof data.detail === "string") {
        return data.detail;
    }

    if (Array.isArray(data.detail) && data.detail.length > 0) {
        const firstError = data.detail[0];
        const fieldPath = Array.isArray(firstError.loc)
            ? firstError.loc.slice(1).join(" -> ")
            : "";

        if (fieldPath && firstError.msg) {
            return `${fieldPath}: ${firstError.msg}`;
        }

        if (firstError.msg) {
            return firstError.msg;
        }
    }

    if (typeof data.message === "string") {
        return data.message;
    }

    return "Request failed.";
}

async function apiRequest(path, method = "GET", body = null) {
    const token = getToken();
    const options = {
        method: method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (token) {
        options.headers.Authorization = `Bearer ${token}`;
    }

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${path}`, options);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(getErrorMessage(data));
    }

    return data;
}
