import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, AlertCircle, CheckCircle2, ArrowLeft } from "lucide-react";
import AuthLayout from "../components/AuthLayout";
import { forgotPasswordApi } from "../services/api";

export default function ForgotPassword() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [verified, setVerified] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email.trim()) {
      setError("Please enter your email address.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("Please enter a valid email address.");
      return;
    }

    setSubmitting(true);
    try {
      await forgotPasswordApi(email.trim());
      setSubmitting(false);
      setVerified(true);
    } catch (err: unknown) {
      setSubmitting(false);
      setError(err instanceof Error ? err.message : "Failed to request password reset.");
    }
  };

  if (verified) {
    return (
      <AuthLayout title="Password reset sent">
        <div className="flex flex-col items-center text-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-500/15 text-emerald-400">
            <CheckCircle2 className="h-7 w-7" />
          </div>
          <p className="text-sm text-slate-300">
            We've sent a password reset link to <span className="font-semibold text-white">{email}</span>. Please check your inbox.
          </p>
          <button
            type="button"
            onClick={() => navigate("/login", { state: { justVerified: true } })}
            className="mt-6 w-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-400 py-3 text-sm font-bold uppercase tracking-wide text-white shadow-lg transition-opacity hover:opacity-90"
          >
            Back to Sign In
          </button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Reset your password">
      <p className="mb-5 -mt-2 text-center text-xs text-slate-500">
        Enter your registered email address and we'll send you instructions to reset your password.
      </p>

      <form onSubmit={handleSubmit} noValidate className="space-y-4">
        {error && (
          <div className="flex items-start gap-2 rounded-lg border border-risk-critical/30 bg-risk-critical/10 px-3 py-2.5 text-sm text-red-300">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <label htmlFor="resetEmail" className="mb-1.5 block text-sm font-medium text-slate-300">
            Email
          </label>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              id="resetEmail"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="example@company.com"
              className="w-full rounded-xl border border-white/10 bg-navy-950/60 py-3 pl-11 pr-3 text-sm text-white placeholder:text-slate-500 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-400/20"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="mt-2 w-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-400 py-3 text-sm font-bold uppercase tracking-wide text-white shadow-lg transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Sending..." : "Send Reset Link"}
        </button>
      </form>

      <Link
        to="/login"
        className="mt-6 flex items-center justify-center gap-1.5 text-sm font-medium text-slate-400 hover:text-slate-300"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        Back to Sign In
      </Link>
    </AuthLayout>
  );
}
