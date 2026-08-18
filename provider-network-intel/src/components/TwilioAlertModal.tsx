import { useState } from "react";
import { Send, Phone, X, CheckCircle, AlertTriangle } from "lucide-react";

interface TwilioAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultCountyName?: string;
  defaultSpecialty?: string;
  defaultGapLevel?: string;
}

export default function TwilioAlertModal({
  isOpen,
  onClose,
  defaultCountyName = "Longview",
  defaultSpecialty = "Endocrinology",
  defaultGapLevel = "CRITICAL GAP",
}: TwilioAlertModalProps) {
  const [toPhone, setToPhone] = useState("+1");
  const [message, setMessage] = useState(
    `[HEALTHCARE NETWORK ALERT]\nCounty: ${defaultCountyName}\nSpecialty: ${defaultSpecialty}\nShortage Level: ${defaultGapLevel}\nAction Required: Recruit +2 specialists immediately.`
  );
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSendCallAndSMS = async () => {
    if (!toPhone || toPhone.trim().length < 5) {
      setError("Please enter a valid phone number with country code (e.g. +1234567890).");
      return;
    }

    setSending(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/api/v1/twilio/send-call-and-sms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          to_phone: toPhone,
          message: message,
        }),
      });

      const data = await res.json();
      if (data.success || (data.sms?.success && data.call?.success)) {
        setResult(data);
      } else {
        setError(data.message || "Failed to dispatch Twilio SMS and Voice Call.");
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect to Twilio backend endpoint.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600/30 text-brand-400 border border-brand-500/40">
              <Phone className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Twilio Dispatch System</h3>
              <p className="text-xs text-slate-400">Dispatch live Voice & SMS alerts to field team & recruiters</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mt-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Recipient Phone Number</label>
            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2">
              <Phone className="h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={toPhone}
                onChange={(e) => setToPhone(e.target.value)}
                placeholder="+1234567890"
                className="w-full bg-transparent text-sm text-white focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Voice & SMS Text Body</label>
            <textarea
              rows={4}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 p-3 text-xs text-white focus:outline-none focus:border-brand-500"
            />
          </div>

          {result && (
            <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-3.5 text-xs text-emerald-300 flex items-start gap-2.5">
              <CheckCircle className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-emerald-200">{result.message || "Alerts dispatched successfully!"}</p>
                <p className="mt-1 text-[11px] text-emerald-400/80">SMS SID: <code className="font-mono">{result.sms?.sid || "N/A"}</code></p>
                <p className="text-[11px] text-emerald-400/80">Call SID: <code className="font-mono">{result.call?.sid || "N/A"}</code></p>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-3.5 text-xs text-rose-300 flex items-start gap-2.5">
              <AlertTriangle className="h-5 w-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-rose-200">Alert Error</p>
                <p className="mt-0.5 text-rose-300">{error}</p>
              </div>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              onClick={onClose}
              className="rounded-xl px-4 py-2 text-xs font-medium text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              Cancel
            </button>
            <button
              onClick={handleSendCallAndSMS}
              disabled={sending}
              className="flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2 text-xs font-bold text-white shadow-lg hover:bg-brand-500 disabled:opacity-50"
            >
              <Send className="h-3.5 w-3.5" />
              <span>{sending ? "Dispatching..." : "Send Voice & SMS Alert"}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

