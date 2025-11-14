import React, { useState } from "react";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Mail,
  Lock,
  User as UserIcon,
  Brain,
  Zap,
  Star,
  Users,
  TrendingUp,
} from "lucide-react";
import { User as UserType } from "../types";

interface LoginSignupProps {
  onComplete: (user: UserType) => void;
}

const API_BASE: string =
  (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000";

type TokenPair = { access_token: string; refresh_token: string; token_type: "bearer" };

const LoginSignup: React.FC<LoginSignupProps> = ({ onComplete }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleSocialLogin = (provider: "google" | "linkedin") => {
    // Redirect to backend OAuth flow
    window.location.href = `${API_BASE}/oauth/${provider}/start`;
  };

  async function fetchMe(accessToken: string) {
    const meRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (!meRes.ok) {
      const t = await meRes.text();
      throw new Error(t || "Failed to fetch user profile");
    }
    return (await meRes.json()) as UserType;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // basic client validations
    if (!isLogin) {
      if (formData.password !== formData.confirmPassword) {
        setError("Passwords do not match");
        return;
      }
      if (!formData.name.trim()) {
        setError("Please enter your full name");
        return;
      }
    }

    // very light email sanity (server also validates)
    if (!/.+@.+\..+/.test(formData.email)) {
      setError("Please enter a valid email address");
      return;
    }

    const url = isLogin ? `${API_BASE}/auth/login` : `${API_BASE}/auth/register`;
    const payload = isLogin
      ? { email: formData.email.trim(), password: formData.password }
      : {
          email: formData.email.trim(),
          password: formData.password,
          full_name: formData.name.trim(),
        };

    try {
      setSubmitting(true);

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        // pydantic / FastAPI errors often return {detail: "..."} or [{loc, msg, ...}]
        let message = "Something went wrong";
        try {
          const data = await res.json();
          if (typeof data.detail === "string") message = data.detail;
          else if (Array.isArray(data.detail) && data.detail[0]?.msg)
            message = data.detail[0].msg;
        } catch {
          message = `${res.status} ${res.statusText}`;
        }
        throw new Error(message);
      }

      let accessToken = "";
      let refreshToken = "";

      if (isLogin) {
        const data = (await res.json()) as TokenPair;
        accessToken = data.access_token;
        refreshToken = data.refresh_token;
      } else {
        // auto-login after successful registration
        const loginRes = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            email: formData.email.trim(),
            password: formData.password,
          }),
        });
        if (!loginRes.ok) {
          const t = await loginRes.text();
          throw new Error(t || "Auto-login failed after registration");
        }
        const data = (await loginRes.json()) as TokenPair;
        accessToken = data.access_token;
        refreshToken = data.refresh_token;
      }

      // persist tokens (consistent names with the rest of the app)
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);

      // load profile and bubble up
      const user = await fetchMe(accessToken);
      onComplete(user);
    } catch (err: any) {
      setError(err?.message || "Request failed");
    } finally {
      setSubmitting(false);
    }
  };

  const canSubmit = () => {
    if (submitting) return false;
    if (isLogin) return Boolean(formData.email && formData.password);
    return Boolean(
      formData.name && formData.email && formData.password && formData.confirmPassword
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 min-h-screen flex">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12 text-white">
          <div className="mb-8">
            <div className="relative">
              <div className="w-32 h-32 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl transform hover:scale-110 transition-all duration-300">
                <div className="text-6xl">🧠</div>
              </div>
              <div className="absolute -top-2 -right-2 w-8 h-8 bg-green-400 rounded-full flex items-center justify-center animate-pulse">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-blue-400 rounded-full flex items-center justify-center animate-bounce">
                <Star className="w-3 h-3 text-white" />
              </div>
            </div>
          </div>

          <h1 className="text-6xl font-bold mb-4 tracking-tight">
            <span className="bg-gradient-to-r from-yellow-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Abhyas
            </span>
          </h1>
          <p className="text-xl text-gray-200 mb-8 text-center max-w-md">
            AI-Powered Product Manager Interview Coach
          </p>

          <div className="space-y-6 max-w-md">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-lg">AI-Powered Evaluation</h3>
                <p className="text-gray-300 text-sm">Get detailed feedback on every response</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-teal-500 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-lg">Company-Specific Practice</h3>
                <p className="text-gray-300 text-sm">Practice with real interview formats</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-red-500 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-lg">Track Your Progress</h3>
                <p className="text-gray-300 text-sm">See improvement with detailed analytics</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Login/Signup Form */}
        <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
          <div className="w-full max-w-md">
            {/* Mobile Logo */}
            <div className="lg:hidden text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-2xl mx-auto mb-4">
                <div className="text-3xl">🧠</div>
              </div>
              <h1 className="text-3xl font-bold">
                <span className="bg-gradient-to-r from-yellow-400 to-orange-400 bg-clip-text text-transparent">
                  Abhyas
                </span>
              </h1>
            </div>

            <div className="bg-white bg-opacity-10 backdrop-blur-lg rounded-3xl p-8 border border-white border-opacity-20 shadow-2xl">
              {/* Toggle Buttons */}
              <div className="flex bg-white bg-opacity-10 rounded-2xl p-1 mb-8">
                <button
                  onClick={() => setIsLogin(true)}
                  className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                    isLogin ? "bg-white text-gray-900 shadow-lg" : "text-white hover:bg-white hover:bg-opacity-10"
                  }`}
                >
                  Sign In
                </button>
                <button
                  onClick={() => setIsLogin(false)}
                  className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                    !isLogin ? "bg-white text-gray-900 shadow-lg" : "text-white hover:bg-white hover:bg-opacity-10"
                  }`}
                >
                  Sign Up
                </button>
              </div>

              {/* Social Login */}
              <div className="space-y-3 mb-6">
                <button
                  onClick={() => handleSocialLogin("google")}
                  className="w-full flex items-center justify-center space-x-3 px-4 py-3 bg-white rounded-xl hover:bg-gray-50 transition-all shadow-lg"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span className="font-medium text-gray-700">Continue with Google</span>
                </button>

                <button
                  onClick={() => handleSocialLogin("linkedin")}
                  className="w-full flex items-center justify-center space-x-3 px-4 py-3 bg-white rounded-xl hover:bg-gray-50 transition-all shadow-lg"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path
                      fill="#0A66C2"
                      d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
                    />
                  </svg>
                  <span className="font-medium text-gray-700">Continue with LinkedIn</span>
                </button>
              </div>

              {/* Divider */}
              <div className="relative mb-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white border-opacity-30" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-transparent text-white">Or continue with email</span>
                </div>
              </div>

              {error && <p className="text-red-400 text-center mb-4">{error}</p>}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {!isLogin && (
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">Full Name</label>
                    <div className="relative">
                      <UserIcon className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        type="text"
                        value={formData.name}
                        onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
                        className="w-full pl-10 pr-4 py-3 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-xl focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-all text-white placeholder-gray-300"
                        placeholder="Enter your full name"
                        required={!isLogin}
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-white mb-2">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData((p) => ({ ...p, email: e.target.value }))}
                      className="w-full pl-10 pr-4 py-3 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-xl focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-all text-white placeholder-gray-300"
                      placeholder="Enter your email"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                    <input
                      type={showPassword ? "text" : "password"}
                      value={formData.password}
                      onChange={(e) => setFormData((p) => ({ ...p, password: e.target.value }))}
                      className="w-full pl-10 pr-12 py-3 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-xl focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-all text-white placeholder-gray-300"
                      placeholder="Enter your password"
                      required
                      minLength={6}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword((s) => !s)}
                      className="absolute right-3 top-3 text-gray-400 hover:text-gray-300"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                {!isLogin && (
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">Confirm Password</label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                      <input
                        type="password"
                        value={formData.confirmPassword}
                        onChange={(e) =>
                          setFormData((p) => ({ ...p, confirmPassword: e.target.value }))
                        }
                        className="w-full pl-10 pr-4 py-3 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-xl focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-all text-white placeholder-gray-300"
                        placeholder="Confirm your password"
                        required={!isLogin}
                        minLength={6}
                      />
                    </div>
                  </div>
                )}

                {isLogin && (
                  <div className="flex items-center justify-between text-sm">
                    <label className="flex items-center text-white">
                      <input type="checkbox" className="mr-2 rounded" />
                      Remember me
                    </label>
                    <button type="button" className="text-yellow-400 hover:text-yellow-300">
                      Forgot password?
                    </button>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!canSubmit()}
                  className="w-full flex items-center justify-center space-x-2 py-3 bg-gradient-to-r from-yellow-400 to-orange-500 text-gray-900 rounded-xl hover:from-yellow-300 hover:to-orange-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-bold shadow-lg"
                >
                  <span>{submitting ? "Please wait..." : isLogin ? "Sign In" : "Create Account"}</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </form>

              {/* Footer */}
              <div className="mt-6 text-center text-sm text-gray-300">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                  onClick={() => setIsLogin((s) => !s)}
                  className="text-yellow-400 hover:text-yellow-300 font-medium"
                >
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Custom CSS for animations */}
      <style>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
};

export default LoginSignup;
