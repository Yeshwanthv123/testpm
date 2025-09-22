import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const OAuthCallback: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const qs = new URLSearchParams(window.location.search);
    // also support hash fragments just in case
    const hash = new URLSearchParams(window.location.hash.replace(/^#/, ""));

    const accessToken =
      qs.get("access_token") || hash.get("access_token") || "";
    const refreshToken =
      qs.get("refresh_token") || hash.get("refresh_token") || "";

    if (accessToken && refreshToken) {
      // IMPORTANT: keep these names consistent across the app
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);

      // clean querystring so tokens aren't visible in the URL bar
      const cleanURL = window.location.pathname;
      window.history.replaceState({}, document.title, cleanURL);

      navigate("/profile", { replace: true });
    } else {
      // no tokens -> send user to normal sign-in
      navigate("/signin", { replace: true });
    }
  }, [navigate]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-lg text-gray-600">Finalizing your login...</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
