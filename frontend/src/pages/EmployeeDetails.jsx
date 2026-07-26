import { useEffect, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import AdminAvatar from "../components/AdminAvatar";
import RiskDistribution from "../components/RiskDistribution";
import api from "../utils/api";

const RISK_PRIORITY = {
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
};

export default function EmployeeDetails() {
  const { employee: employeeId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const cachedEmployees = location.state?.employees;
  const cachedBlockedList = location.state?.blockedList;

  const [employee, setEmployee] = useState(null);
  const [employees, setEmployees] = useState(cachedEmployees || []);
  const [blockedList, setBlockedList] = useState(cachedBlockedList || []);
  const [loading, setLoading] = useState(!cachedEmployees);
  const [loadError, setLoadError] = useState("");
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("theme") !== "light");
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [note, setNote] = useState("");
  const [isSubmittingAction, setIsSubmittingAction] = useState(false);
  const [feedback, setFeedback] = useState({
    open: false,
    tone: "success",
    title: "",
    message: "",
  });

  const goToDashboard = () =>
    navigate("/dashboard", {
      state: { employees, blockedList },
    });

  useEffect(() => {
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      if (cachedEmployees?.length) {
        const selected = pickBestEmployeeRecord(cachedEmployees, employeeId);

        if (mounted) {
          setEmployees(cachedEmployees);
          setBlockedList(cachedBlockedList || []);
          setEmployee(selected);
          setLoading(false);
        }
        return;
      }

      try {
        setLoading(true);
        setLoadError("");

        const [anomalyResponse, blockedResponse] = await Promise.all([
          api.get("/api/anomalies"),
          api.get("/api/blocked"),
        ]);

        if (!mounted) {
          return;
        }

        setEmployees(anomalyResponse.data);
        setBlockedList(blockedResponse.data);
        setEmployee(pickBestEmployeeRecord(anomalyResponse.data, employeeId));
      } catch (error) {
        console.log(error);
        if (mounted) {
          setLoadError("Unable to load employee details. Please try again.");
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    load();

    return () => {
      mounted = false;
    };
  }, [employeeId, cachedEmployees, cachedBlockedList]);

  const openFeedback = (tone, title, message) => {
    setFeedback({
      open: true,
      tone,
      title,
      message,
    });
  };

  const closeFeedback = () => {
    setFeedback((current) => ({ ...current, open: false }));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
        <p className="mt-4 text-sm text-slate-300">Loading employee details...</p>
      </div>
    );
  }

  if (loadError || !employee) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white">
        <p className="text-lg">{loadError || "Employee details are unavailable."}</p>
        <button onClick={goToDashboard} className="mt-4 rounded bg-blue-600 px-4 py-2">
          Back to dashboard
        </button>
      </div>
    );
  }

  const isBlocked = blockedList.some((item) => item.employee === employee.employee);
  const uniqueEmployees = getUniqueEmployees(employees);
  const total = uniqueEmployees.length;
  const high = uniqueEmployees.filter((item) => item.risk_level === "HIGH").length;
  const medium = uniqueEmployees.filter((item) => item.risk_level === "MEDIUM").length;
  const low = uniqueEmployees.filter((item) => item.risk_level === "LOW").length;

  const chartData = [
    { name: "LOW", value: low, color: "#22c55e" },
    { name: "MEDIUM", value: medium, color: "#facc15" },
    { name: "HIGH", value: high, color: "#ef4444" },
  ];

  const handleBlockToggle = async () => {
    try {
      setIsSubmittingAction(true);

      if (isBlocked) {
        await api.delete(`/api/unblock/${employee.employee}`);
      } else {
        await api.post("/api/block", { employee: employee.employee });
      }

      const blockedResponse = await api.get("/api/blocked");
      setBlockedList(blockedResponse.data);

      openFeedback(
        "success",
        isBlocked ? "Employee unblocked" : "Employee blocked",
        isBlocked
          ? `${employee.employee} is active again and removed from the blocked list.`
          : `${employee.employee} has been blocked successfully.`
      );
    } catch (error) {
      openFeedback(
        "error",
        isBlocked ? "Could not unblock employee" : "Could not block employee",
        error.response?.data?.detail || "Please try again in a moment."
      );
    } finally {
      setIsSubmittingAction(false);
    }
  };

  const handleAssignToAnalyst = async () => {
    try {
      setIsSubmittingAction(true);

      const response = await api.post("/api/assign", {
        employee: employee.employee,
        note,
      });

      setShowAssignModal(false);
      setNote("");
      openFeedback(
        "success",
        "Assignment sent",
        response.data.message || `The analyst has been notified about ${employee.employee}.`
      );
    } catch (error) {
      openFeedback(
        "error",
        "Assignment failed",
        error.response?.data?.detail || "Email could not be sent. Check the backend logs."
      );
    } finally {
      setIsSubmittingAction(false);
    }
  };

  return (
    <div
      className={`flex min-h-[100dvh] flex-col xl:h-screen xl:overflow-hidden ${
        darkMode
          ? "bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white"
          : "bg-gray-100 text-gray-800"
      }`}
    >
      <div
        className={`flex flex-col items-stretch justify-between gap-3 border-b px-4 py-3 sm:flex-row sm:items-center sm:px-6 sm:py-4 ${
          darkMode
            ? "border-white/10 bg-gradient-to-r from-[#0f172a] to-[#1e293b]"
            : "bg-white shadow"
        }`}
      >
        <div className="flex min-w-0 items-center gap-3 sm:gap-4">
          <img src="/logo.jpg" width="32" height="32" alt="" className="h-8 w-8 shrink-0" />
          <h1 className="text-sm font-semibold leading-tight sm:text-lg">
            Insider Threat Detection System - Employee Details
          </h1>
        </div>

        <div className="flex w-full shrink-0 items-center justify-end gap-2 sm:w-auto sm:gap-4">
          <div className="hidden sm:block">
            <AdminAvatar />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col xl:min-h-0 xl:flex-row">
        <div
          className={`order-last sticky bottom-0 z-30 flex w-full shrink-0 flex-row items-center justify-between border-t px-3 py-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] backdrop-blur-xl xl:order-none xl:h-auto xl:w-20 xl:flex-col xl:border-t-0 xl:px-0 xl:py-6 ${
            darkMode
              ? "border-white/10 bg-[#020617]/95"
              : "border-gray-200 bg-white/95 shadow-lg"
          }`}
        >
          <div className="flex flex-row items-center gap-2 xl:flex-col xl:gap-6">
            <SidebarIcon
              src="/home.svg"
              label="Dashboard"
              active={location.pathname === "/dashboard"}
              onClick={goToDashboard}
              darkMode={darkMode}
            />

            <SidebarIcon
              src="/blocked.svg"
              label="Blocked employees"
              onClick={() =>
                navigate("/BlockedEmployees", {
                  state: { blockedList },
                })
              }
              darkMode={darkMode}
            />

            <SidebarIcon
              src="/moon.svg"
              label={darkMode ? "Use light theme" : "Use dark theme"}
              onClick={() => setDarkMode(!darkMode)}
              darkMode={darkMode}
            />
          </div>

          <SidebarIcon
            src="/logout.svg"
            label="Log out"
            onClick={() => {
              sessionStorage.removeItem("token");
              sessionStorage.removeItem("visibleEmployeeCount");
              navigate("/");
            }}
            danger
            darkMode={darkMode}
          />
        </div>

        <main className="flex min-w-0 flex-1 flex-col p-4 pb-24 sm:p-6 sm:pb-28 xl:min-h-0 xl:overflow-y-auto xl:pb-6">
          <div className="mb-4 grid grid-cols-2 gap-3 sm:mb-6 sm:gap-4 xl:grid-cols-4">
            <Card title="Total Employees" value={total} darkMode={darkMode} />
            <Card title="High Risk Employees" value={high} darkMode={darkMode} />
            <Card title="Medium Risk Employees" value={medium} darkMode={darkMode} />
            <Card title="Low Risk Employees" value={low} darkMode={darkMode} highlight />
          </div>

          <div className="grid flex-1 grid-cols-1 gap-4 xl:grid-cols-3 xl:gap-6">
            <div
              className={`min-w-0 rounded-xl p-4 sm:p-6 xl:col-span-2 ${
                darkMode ? "bg-[#1c2333]" : "border border-gray-200 bg-white shadow"
              }`}
            >
              <div className="flex flex-col gap-6 md:flex-row">
                <div
                  className={`w-full shrink-0 rounded-xl p-4 text-center md:w-64 ${
                    darkMode ? "bg-[#111827]" : "border bg-gray-50"
                  }`}
                >
                  <EmployeeAvatar employeeId={employee.employee} />

                  <h2>{employee.employee}</h2>

                  <p className="mt-2">
                    Risk Score:
                    <span className="ml-2 font-bold text-red-500">
                      {Math.abs(Math.round(employee.risk_score || 0))}
                    </span>
                  </p>

                  <div className="mt-2 rounded-full bg-green-500 px-3 py-1 text-white">
                    {employee.risk_level}
                  </div>
                </div>

                <div className="min-w-0 flex-1">
                  <h2 className="mb-4">Critical Indicators</h2>

                  <div className="mb-6 space-y-3">
                    {getIndicators(employee).map((text) => (
                      <Indicator
                        key={text}
                        darkMode={darkMode}
                        text={text}
                        riskLevel={employee.risk_level}
                      />
                    ))}
                  </div>

                  <h2>Actions</h2>

                  <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:gap-4">
                    <button
                      onClick={handleBlockToggle}
                      disabled={isSubmittingAction}
                      className={`rounded px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-60 ${
                        isBlocked ? "bg-green-600" : "bg-red-600"
                      }`}
                    >
                      {isSubmittingAction
                        ? "Processing..."
                        : isBlocked
                        ? "Unblock Employee"
                        : "Block Employee"}
                    </button>

                    <button
                      onClick={() => setShowAssignModal(true)}
                      disabled={isSubmittingAction}
                      className="rounded bg-blue-600 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      Assign to Analyst
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div
              className={`rounded-xl p-4 ${
                darkMode ? "bg-[#1c2333]" : "border border-gray-200 bg-white shadow"
              }`}
            >
              <h2 className="mb-4">Risk Distribution</h2>

              <div className="h-72 sm:h-96">
                <RiskDistribution data={chartData} darkMode={darkMode} />
              </div>
            </div>
          </div>
        </main>
      </div>

      {showAssignModal && (
        <AssignAnalystModal
          darkMode={darkMode}
          employeeId={employee.employee}
          note={note}
          setNote={setNote}
          submitting={isSubmittingAction}
          onCancel={() => {
            if (!isSubmittingAction) {
              setShowAssignModal(false);
            }
          }}
          onSubmit={handleAssignToAnalyst}
        />
      )}

      {feedback.open && (
        <FeedbackModal
          darkMode={darkMode}
          tone={feedback.tone}
          title={feedback.title}
          message={feedback.message}
          onClose={closeFeedback}
        />
      )}
    </div>
  );
}

function AssignAnalystModal({
  darkMode,
  employeeId,
  note,
  setNote,
  submitting,
  onCancel,
  onSubmit,
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/55 px-4 py-6 backdrop-blur-sm">
      <div
        className={`w-full max-w-md overflow-hidden rounded-[28px] border shadow-2xl ${
          darkMode ? "border-white/10 bg-[#0f172a] text-white" : "border-slate-200 bg-white"
        }`}
      >
        <div
          className={`border-b px-6 py-5 ${
            darkMode ? "border-white/10 bg-slate-900/80" : "border-slate-200 bg-slate-50"
          }`}
        >
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-blue-400">
            Analyst Workflow
          </p>
          <h2 className="mt-2 text-xl font-semibold">Assign {employeeId}</h2>
          <p className={`mt-2 text-sm ${darkMode ? "text-slate-300" : "text-slate-600"}`}>
            Add a short context note for the analyst before sending the escalation.
          </p>
        </div>

        <div className="px-6 py-5">
          <textarea
            placeholder="Summarize why this employee needs analyst review..."
            value={note}
            onChange={(event) => setNote(event.target.value)}
            rows={5}
            className={`mb-4 w-full rounded-2xl border px-4 py-3 outline-none transition ${
              darkMode
                ? "border-white/10 bg-[#020617] text-white placeholder:text-slate-500 focus:border-blue-400"
                : "border-slate-200 bg-slate-50 text-slate-900 placeholder:text-slate-400 focus:border-blue-500"
            }`}
          />

          <div className="flex justify-end gap-3">
            <button
              type="button"
              onClick={onCancel}
              disabled={submitting}
              className={`rounded-full px-4 py-2 text-sm font-medium ${
                darkMode
                  ? "bg-white/10 text-white disabled:opacity-60"
                  : "bg-slate-100 text-slate-700 disabled:opacity-60"
              }`}
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={onSubmit}
              disabled={submitting}
              className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-600/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Sending..." : "Send to Analyst"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function FeedbackModal({ darkMode, tone, title, message, onClose }) {
  const toneStyles =
    tone === "error"
      ? {
          badge: "bg-red-500/15 text-red-300 ring-red-400/30",
          icon: "!",
        }
      : {
          badge: "bg-emerald-500/15 text-emerald-300 ring-emerald-400/30",
          icon: "OK",
        };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/55 px-4 py-6 backdrop-blur-sm">
      <div
        className={`w-full max-w-sm rounded-[28px] border p-6 shadow-2xl ${
          darkMode ? "border-white/10 bg-[#0b1120] text-white" : "border-slate-200 bg-white text-slate-900"
        }`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-sm font-bold ring-1 ${toneStyles.badge}`}
          >
            {toneStyles.icon}
          </div>
          <div className="min-w-0">
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className={`mt-2 text-sm leading-6 ${darkMode ? "text-slate-300" : "text-slate-600"}`}>
              {message}
            </p>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-blue-600/30"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

function SidebarIcon({ src, label, active, onClick, danger, darkMode }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`flex h-11 w-11 cursor-pointer items-center justify-center rounded-xl md:h-12 md:w-12 xl:h-14 xl:w-14 ${
        active ? "scale-110 bg-blue-500" : darkMode ? "hover:bg-white/10" : "hover:bg-gray-200"
      } ${danger ? "hover:bg-red-500/20" : ""}`}
    >
      <img
        src={src}
        alt=""
        width="24"
        height="24"
        className={`h-6 w-6 ${darkMode ? "invert" : "opacity-70"}`}
      />
    </button>
  );
}

function Card({ title, value, darkMode, highlight }) {
  return (
    <div
      className={`min-w-0 rounded-xl p-3 sm:p-4 ${
        highlight
          ? "border border-green-200 bg-green-100 text-green-800"
          : darkMode
          ? "bg-[#1c2333]"
          : "border border-gray-200 bg-white shadow"
      }`}
    >
      <p className="text-sm leading-tight text-gray-400 sm:text-base">{title}</p>
      <h2 className="text-2xl font-bold sm:text-3xl">{value}</h2>
    </div>
  );
}

function Indicator({ darkMode, text, riskLevel }) {
  const isLow = riskLevel === "LOW";

  return (
    <div
      className={`flex items-center gap-2 rounded p-3 ${
        darkMode ? "bg-[#111827]" : "border border-gray-200 bg-gray-100"
      }`}
    >
      {!isLow && <span>!</span>}
      {isLow && <span className="text-green-400">o</span>}
      <span>{text}</span>
    </div>
  );
}

function EmployeeAvatar({ employeeId }) {
  const palette = ["#2563eb", "#7c3aed", "#db2777", "#0891b2", "#059669", "#d97706"];
  const hash = [...employeeId].reduce((total, char) => total + char.charCodeAt(0), 0);
  const initials = employeeId.slice(0, 2).toUpperCase();

  return (
    <div
      role="img"
      aria-label={`Avatar for employee ${employeeId}`}
      style={{ backgroundColor: palette[hash % palette.length] }}
      className="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-full border-4 border-white/20 shadow-lg"
    >
      <span className="text-2xl font-bold tracking-wide text-white">{initials}</span>
    </div>
  );
}

function pickBestEmployeeRecord(records, employeeId) {
  return records
    .filter((record) => record.employee === employeeId)
    .reduce((best, record) => {
      if (!best) {
        return record;
      }

      return RISK_PRIORITY[record.risk_level] > RISK_PRIORITY[best.risk_level] ? record : best;
    }, null);
}

function getUniqueEmployees(records) {
  const map = new Map();

  records.forEach((record) => {
    const existing = map.get(record.employee);
    if (!existing || RISK_PRIORITY[record.risk_level] > RISK_PRIORITY[existing.risk_level]) {
      map.set(record.employee, record);
    }
  });

  return Array.from(map.values());
}

function getIndicators(employee) {
  const level = employee.risk_level?.trim().toUpperCase();

  if (level === "LOW") {
    return ["Normal Activity Detected"];
  }

  const indicators = [];

  if ((employee.file_count || 0) > 5) {
    indicators.push("Excess File Access Detected");
  }

  if ((employee.http_count || 0) > 50) {
    indicators.push("Unusual Web Activity");
  }

  if ((employee.email_count || 0) > 20) {
    indicators.push("High Email Activity");
  }

  if ((employee.device_count || 0) > 10) {
    indicators.push("Multiple Device Usage");
  }

  if (indicators.length === 0) {
    indicators.push("Moderate Behavior Deviation");
  }

  return indicators;
}
