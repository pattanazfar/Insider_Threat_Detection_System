import { useParams, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../utils/api";
import AdminAvatar from "../components/AdminAvatar";
import RiskDistribution from "../components/RiskDistribution";

export default function EmployeeDetails() {
  const { employee: employeeId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const goToDashboard = () => navigate("/dashboard", {
    state: { employees, blockedList },
  });

  const cachedEmployees = location.state?.employees;
  const cachedBlockedList = location.state?.blockedList;
  const [employee, setEmployee] = useState(null);
  const [employees, setEmployees] = useState(cachedEmployees || []);
  const [loading, setLoading] = useState(!cachedEmployees);
  const [loadError, setLoadError] = useState("");
  const [blockedList, setBlockedList] = useState([]); // ✅ NEW
  const [darkMode, setDarkMode] = useState(() => {
  return localStorage.getItem("theme") === "light" ? false : true;
});

  // ✅ MODAL STATE
  const [showModal, setShowModal] = useState(false);
  const [note, setNote] = useState("");



  useEffect(() => {
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);



useEffect(() => {
  let mounted = true;

  const load = async () => {
    if (cachedEmployees?.length) {
      const priority = { HIGH: 3, MEDIUM: 2, LOW: 1 };
      const selected = cachedEmployees
        .filter((record) => record.employee === employeeId)
        .reduce((best, record) => {
          if (!best || priority[record.risk_level] > priority[best.risk_level]) return record;
          return best;
        }, null);

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
      const [res1, res2] = await Promise.all([
        api.get("/api/anomalies"),
        api.get("/api/blocked"),
      ]);

      if (mounted) {
        setEmployees(res1.data);

        // 🔥 SELECT BEST EMPLOYEE HERE
        const priority = { HIGH: 3, MEDIUM: 2, LOW: 1 };

        const employeeRecords = res1.data.filter(
          (u) => u.employee === employeeId
        );

        let selected = employeeRecords[0];

        employeeRecords.forEach((u) => {
          if (priority[u.risk_level] > priority[selected.risk_level]) {
            selected = u;
          }
        });

        setEmployee(selected);
        setBlockedList(res2.data);
      }
    } catch (e) {
      console.log(e);
      if (mounted) setLoadError("Unable to load employee details. Please try again.");
    } finally {
      if (mounted) setLoading(false);
    }
  };

  load();

  return () => {
    mounted = false;
  };
}, [employeeId, cachedEmployees, cachedBlockedList]);

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
        <p className="mt-4 text-sm text-slate-300">Loading employee details…</p>
      </div>
    );
  }

  if (loadError || !employee) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white">
        <p className="text-lg">{loadError || "Employee details are unavailable."}</p>
        <button onClick={goToDashboard} className="mt-4 rounded bg-blue-600 px-4 py-2">Back to dashboard</button>
      </div>
    );
  }

  // ✅ CHECK IF BLOCKED
  const isBlocked = blockedList.some(
    (b) => b.employee === employee.employee
  );

  // 📊 GLOBAL STATS
  const priority = {
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
};

const map = new Map();

employees.forEach((u) => {
  if (!map.has(u.employee)) {
    map.set(u.employee, u);
  } else {
    const existing = map.get(u.employee);

    if (priority[u.risk_level] > priority[existing.risk_level]) {
      map.set(u.employee, u);
    }
  }
});

const uniqueEmployees = Array.from(map.values());

  const total = uniqueEmployees.length;
  const high = uniqueEmployees.filter((u) => u.risk_level === "HIGH").length;
  const medium = uniqueEmployees.filter((u) => u.risk_level === "MEDIUM").length;
  const low = uniqueEmployees.filter((u) => u.risk_level === "LOW").length;

  const chartData = [
    { name: "LOW", value: low, color: "#22c55e" },
    { name: "MEDIUM", value: medium, color: "#facc15" },
    { name: "HIGH", value: high, color: "#ef4444" },
  ];

const getIndicators = (u) => {
  const level = u.risk_level?.trim().toUpperCase();

  if (level === "LOW") {
    return ["Normal Activity Detected"];
  }

  const indicators = [];

  if ((u.file_count || 0) > 5) {
    indicators.push("Excess File Access Detected");
  }

  if ((u.http_count || 0) > 50) {
    indicators.push("Unusual Web Activity");
  }

  if ((u.email_count || 0) > 20) {
    indicators.push("High Email Activity");
  }

  if ((u.device_count || 0) > 10) {
    indicators.push("Multiple Device Usage");
  }

  if (indicators.length === 0) {
    indicators.push("Moderate Behavior Deviation");
  }

  return indicators; // show only 2
};
  return (
    <div
      className={`flex min-h-[100dvh] flex-col xl:h-screen xl:overflow-hidden ${
        darkMode
          ? "bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white"
          : "bg-gray-100 text-gray-800"
      }`}
    >
      {/* HEADER */}
      <div
        className={`flex flex-col items-stretch justify-between gap-3 border-b px-4 py-3 sm:flex-row sm:items-center sm:px-6 sm:py-4 ${
          darkMode
            ? "bg-gradient-to-r from-[#0f172a] to-[#1e293b] border-white/10"
            : "bg-white shadow"
        }`}
      >
        <div className="flex min-w-0 items-center gap-3 sm:gap-4">
          <img src="/logo.jpg" width="32" height="32" alt="" className="h-8 w-8 shrink-0" />
          <h1 className="text-sm font-semibold leading-tight sm:text-lg">
            Insider Threat Detection System - Employee Details
          </h1>
        </div>

        <div className="flex w-full shrink-0 items-center justify-between gap-2 sm:w-auto sm:justify-start sm:gap-4">
          <button
            onClick={goToDashboard}
            className="rounded-lg bg-blue-500 px-3 py-2 text-sm text-white sm:px-4 sm:text-base"
          >
            ← Back
          </button>

          <div className="hidden sm:block">
            <AdminAvatar />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col xl:min-h-0 xl:flex-row">
        {/* SIDEBAR */}
        <div
          className={`flex h-16 w-full shrink-0 flex-row items-center justify-between border-b px-3 py-2 xl:h-auto xl:w-20 xl:flex-col xl:border-b-0 xl:px-0 xl:py-6 ${
            darkMode
              ? "bg-[#020617]"
              : "bg-white border-r border-gray-200"
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
              onClick={() => navigate("/BlockedEmployees")}
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

        {/* MAIN */}
        <main className="flex min-w-0 flex-1 flex-col p-4 sm:p-6 xl:min-h-0 xl:overflow-y-auto">
          {/* CARDS */}
          <div className="mb-4 grid grid-cols-2 gap-3 sm:mb-6 sm:gap-4 xl:grid-cols-4">
            <Card title="Total Employees" value={total} darkMode={darkMode} />
            <Card title="High Risk Employees" value={high} darkMode={darkMode} />
            <Card title="Medium Risk Employees" value={medium} darkMode={darkMode} />
            <Card title="Low Risk Employees" value={low} darkMode={darkMode} highlight />
          </div>

          {/* CONTENT */}
          <div className="grid flex-1 grid-cols-1 gap-4 xl:grid-cols-3 xl:gap-6">
            {/* LEFT */}
            <div
              className={`min-w-0 rounded-xl p-4 sm:p-6 xl:col-span-2 ${
                darkMode
                  ? "bg-[#1c2333]"
                  : "bg-white shadow border border-gray-200"
              }`}
            >
              <div className="flex flex-col gap-6 md:flex-row">
                {/* PROFILE */}
                <div
                  className={`w-full shrink-0 rounded-xl p-4 text-center md:w-64 ${
                    darkMode
                      ? "bg-[#111827]"
                      : "bg-gray-50 border"
                  }`}
                >
                  <EmployeeAvatar employeeId={employee.employee} />

                  <h2>{employee.employee}</h2>

                  <p className="mt-2">
                    Risk Score:
                    <span className="text-red-500 font-bold ml-2">
                      {Math.abs(Math.round(employee.risk_score || 0))}
                    </span>
                  </p>

                  <div className="mt-2 bg-green-500 text-white px-3 py-1 rounded-full">
                    {employee.risk_level}
                  </div>
                </div>

                {/* DETAILS */}
                <div className="min-w-0 flex-1">
                  <h2 className="mb-4">Critical Indicators</h2>

                  <div className="space-y-3 mb-6">
                    {getIndicators(employee).map((text) => (
  <Indicator
  darkMode={darkMode}
  text={text}
  riskLevel={employee.risk_level}
/>
))}
                  </div>

                  <h2>Actions</h2>

                  <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:gap-4">

                    {/* ✅ TOGGLE BUTTON */}
                    {isBlocked ? (
                      <button
                        onClick={async () => {
                          await api.delete(`/api/unblock/${employee.employee}`);

const res = await api.get("/api/blocked");
setBlockedList(res.data);
                          alert("Employee Unblocked ✅");
                        }}
                        className="rounded bg-green-600 px-4 py-2 text-white"
                      >
                        🔓 Unblock Employee
                      </button>
                    ) : (
                      <button
                        onClick={async () => {
                          await api.post("/api/block", {
                            employee: employee.employee,
                          });
                          const res = await api.get("/api/blocked");
setBlockedList(res.data);
                          alert("Employee Blocked 🚫");
                        }}
                        className="rounded bg-red-600 px-4 py-2 text-white"
                      >
                        🔒 Block Employee
                      </button>
                    )}

                    <button
                      onClick={() => setShowModal(true)}
                      className="rounded bg-blue-600 px-4 py-2 text-white"
                    >
                      Assign to Analyst
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* RIGHT */}
            <div
              className={`p-4 rounded-xl ${
                darkMode
                  ? "bg-[#1c2333]"
                  : "bg-white shadow border border-gray-200"
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

      {/* MODAL */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 py-6">
          <div
            className={`w-full max-w-sm rounded-xl p-5 shadow-xl sm:p-6 ${
              darkMode
                ? "bg-[#1e293b] text-white border border-white/10"
                : "bg-white text-black"
            }`}
          >
            <h2 className="mb-3 font-semibold text-lg">
              Assign to Analyst
            </h2>

            <textarea
              placeholder="Enter note..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className={`w-full p-2 rounded mb-4 ${
                darkMode
                  ? "bg-[#0f172a] border border-white/10 text-white"
                  : "bg-gray-100 border"
              }`}
            />

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowModal(false)}
                className="px-3 py-1 rounded bg-gray-400"
              >
                Cancel
              </button>

              <button
                onClick={async () => {
                  try {
                    const response = await api.post("/api/assign", {
                      employee: employee.employee,
                      note,
                    });
                    setShowModal(false);
                    setNote("");
                    alert(response.data.message);
                  } catch (error) {
                    alert(
                      error.response?.data?.detail ||
                        "Email could not be sent. Check the backend logs."
                    );
                  }
                }}
                className="bg-blue-600 text-white px-3 py-1 rounded"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* SIDEBAR */
function SidebarIcon({ src, label, active, onClick, danger, darkMode }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`flex h-11 w-11 items-center justify-center rounded-xl cursor-pointer xl:h-14 xl:w-14 ${
        active
          ? "bg-blue-500 scale-110"
          : darkMode
          ? "hover:bg-white/10"
          : "hover:bg-gray-200"
      } ${danger ? "hover:bg-red-500/20" : ""}`}
    >
      <img
        src={src}
        alt=""
        width="24"
        height="24"
        className={`w-6 h-6 ${darkMode ? "invert" : "opacity-70"}`}
      />
    </button>
  );
}

/* CARD */
function Card({ title, value, darkMode, highlight }) {
  return (
    <div
      className={`min-w-0 rounded-xl p-3 sm:p-4 ${
        highlight
          ? "bg-green-100 text-green-800 border border-green-200"
          : darkMode
          ? "bg-[#1c2333]"
          : "bg-white shadow border border-gray-200"
      }`}
    >
      <p className="text-sm leading-tight text-gray-400 sm:text-base">{title}</p>
      <h2 className="text-2xl font-bold sm:text-3xl">{value}</h2>
    </div>
  );
}

/* INDICATOR */
function Indicator({ darkMode, text, riskLevel }) {
  const isLow = riskLevel === "LOW";

  return (
    <div
      className={`p-3 rounded flex items-center gap-2 ${
        darkMode ? "bg-[#111827]" : "bg-gray-100 border border-gray-200"
      }`}
    >
      {/* ✅ Show icon only if NOT LOW */}
      {!isLow && <span>❗</span>}

      {/* Optional: green dot for LOW */}
      {isLow && <span className="text-green-400">●</span>}

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
      className="w-24 h-24 rounded-full mx-auto mb-4 flex items-center justify-center border-4 border-white/20 shadow-lg"
    >
      <span className="text-2xl font-bold tracking-wide text-white">{initials}</span>
    </div>
  );
}
