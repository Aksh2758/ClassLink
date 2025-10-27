
import React from "react";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, allowedRoles = [] }) {
  const token = localStorage.getItem("token");
  const userJson = localStorage.getItem("user");
  if (!token || !userJson) return <Navigate to="/" replace />;

  let user;
  try {
    user = JSON.parse(userJson);
  } catch (e) {
    return <Navigate to="/" replace />;
  }

  // allowedRoles example: ["faculty"]
  if (allowedRoles.length && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />; // not allowed
  }

  return children;
}
