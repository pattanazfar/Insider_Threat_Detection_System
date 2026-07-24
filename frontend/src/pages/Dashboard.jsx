import { useNavigate, useLocation } from "react-router-dom"; 
import { useEffect, useRef, useState } from "react";
import api from "../utils/api";
import AdminAvatar from "../components/AdminAvatar";
import RiskDistribution from "../components/RiskDistribution";

export default function Dashboard() {
  const navigate = useNavigate();
  const location = useLocation();

  const cachedEmployees = location.state?.employees;
  const cachedBlockedList = location.state?.blockedList;
  const [employees, setEmployees] = useState(cachedEmployees || []);
  const [loading, setLoading] = useState(!cachedEmployees);
  const [loadError, setLoadError] = useState("");
  const [blockedList, setBlockedList] = useState([]); // ✅ NEW
  const [visibleEmployeeCount, setVisibleEmployeeCount] = useState(() => {
    const savedCount = Number.parseInt(
      sessionStorage.getItem("visibleEmployeeCount") || "20",
      10
    );
    return Number.isNaN(savedCount) ? 20 : Math.max(savedCount, 20);
  });
  const activityListRef = useRef(null);
  const previousVisibleCountRef = useRef(visibleEmployeeCount);
  const activityListMountedRef = useRef(false);
  const shouldFollowNewEmployeesRef = useRef(true);
  const [search, setSearch] = useState("");
  const [darkMode, setDarkMode] = useState(() => {
  return localStorage.getItem("theme") === "light" ? false : true;
});
  useEffect(() => {
    sessionStorage.setItem(
      "visibleEmployeeCount",
      String(visibleEmployeeCount)
    );
  }, [visibleEmployeeCount]);

  useEffect(() => {
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

useEffect(() => {
  let mounted = true;

  const load = async () => {
    if (cachedEmployees?.length) {
      if (mounted) {
        setEmployees(cachedEmployees);
        setBlockedList(cachedBlockedList || []);
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
        setBlockedList(res2.data);
      }
    } catch (e) {
      console.log(e);
      if (mounted) setLoadError("Unable to load dashboard data. Please refresh the page.");
    } finally {
      if (mounted) setLoading(false);
    }
  };

  load();

  return () => {
    mounted = false;
  };
}, [cachedEmployees, cachedBlockedList]);

  // ✅ Merge anomaly + blocked employees
const priority = {
  HIGH: 3,
  MEDIUM: 2,
  LOW: 1,
};

const allEmployeesMap = new Map();

employees.forEach((u) => {
  if (!allEmployeesMap.has(u.employee)) {
    allEmployeesMap.set(u.employee, u);
  } else {
    const existing = allEmployeesMap.get(u.employee);

    // 🔥 Keep highest risk record
    if (priority[u.risk_level] > priority[existing.risk_level]) {
      allEmployeesMap.set(u.employee, u);
    }
  }
});
// Add blocked employees (if not already present)
blockedList.forEach((b) => {
  if (!allEmployeesMap.has(b.employee)) {
    allEmployeesMap.set(b.employee, {
      employee: b.employee,
      risk_level: "LOW",
      anomaly_score: 0,
    });
  }
});

const uniqueEmployees = Array.from(allEmployeesMap.values()).sort((a, b) =>
  a.employee.localeCompare(b.employee)
);

  const filteredEmployees = uniqueEmployees.filter((u) =>
    u.employee.toLowerCase().includes(search.toLowerCase())
  );

useEffect(() => {
  if (search) return;

  const interval = setInterval(() => {
    setVisibleEmployeeCount((previousCount) =>
      Math.min(previousCount + 1, uniqueEmployees.length)
    );
  }, 2000);

  return () => clearInterval(interval);
}, [search, uniqueEmployees.length]);

  const liveEmployees = search
    ? filteredEmployees
    : filteredEmployees.slice(0, visibleEmployeeCount);

  useEffect(() => {
    const activityList = activityListRef.current;
    if (!activityList || search) {
      previousVisibleCountRef.current = visibleEmployeeCount;
      return;
    }

    if (!activityListMountedRef.current) {
      activityListMountedRef.current = true;
      if (visibleEmployeeCount > 20) {
        activityList.scrollTop = activityList.scrollHeight;
      }
    } else if (
      visibleEmployeeCount > previousVisibleCountRef.current &&
      shouldFollowNewEmployeesRef.current
    ) {
      activityList.scrollTo({
        top: activityList.scrollHeight,
        behavior: "smooth",
      });
    }

    previousVisibleCountRef.current = visibleEmployeeCount;
  }, [search, visibleEmployeeCount]);

  const high = uniqueEmployees.filter((u) => u.risk_level === "HIGH").length;
  const medium = uniqueEmployees.filter((u) => u.risk_level === "MEDIUM").length;
  const low = uniqueEmployees.filter((u) => u.risk_level === "LOW").length;

  const chartData = [
    { name: "LOW", value: low, color: "#22c55e" },
    { name: "MEDIUM", value: medium, color: "#facc15" },
    { name: "HIGH", value: high, color: "#ef4444" },
  ];

  // 🔥 ADD HERE
const getIndicator = (u) => {
  const level = u.risk_level?.trim().toUpperCase();

  if (level === "HIGH") return "High-Risk Behavior";
  if (level === "MEDIUM") return "Suspicious Activity";
  return "Normal Activity";
};
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
        <p className="mt-4 text-sm text-slate-300">Loading dashboard…</p>
      </div>
    );
  }

  if (loadError || !uniqueEmployees.length) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white">
        <p className="text-lg">{loadError || "No employee records are available."}</p>
      </div>
    );
  }

  return (
    <div
      className={`flex min-h-[100dvh] flex-col xl:h-screen xl:overflow-hidden ${
        darkMode
          ? "bg-gradient-to-br from-[#020617] via-[#0b1220] to-[#020617] text-white"
          : "bg-gray-100 text-black"
      }`}
    >
      {/* HEADER */}
      <div
        className={`flex flex-col gap-3 border-b px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:px-6 sm:py-4
      backdrop-blur-xl ${
        darkMode
          ? "bg-gradient-to-r from-[#0f172a]/80 via-[#1e293b]/70 to-[#0f172a]/80 border-white/10 shadow-lg"
          : "bg-white shadow"
      }`}
      >
        <div className="flex min-w-0 items-center gap-3 sm:gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-500/20">
            <img src="/logo.jpg" width="32" height="32" alt="" className="h-8 w-8" />
          </div>

          <h1 className="text-base font-semibold leading-tight tracking-wide sm:text-lg">
            Insider Threat Detection System - Admin Dashboard
          </h1>
        </div>

        <div className="flex w-full items-center gap-3 sm:w-auto sm:gap-4">
          <div
            className={`flex min-w-0 flex-1 items-center gap-2 rounded-full border px-4 py-2 sm:w-64 ${
              darkMode
                ? "bg-[#0f172a]/60 border-white/10 focus-within:border-blue-400"
                : "bg-gray-100"
            }`}
          >
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search Employee"
              className="w-full min-w-0 bg-transparent text-sm outline-none"
            />
          </div>

          <div className="hidden sm:block">
            <AdminAvatar />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col xl:min-h-0 xl:flex-row xl:overflow-hidden">
        {/* SIDEBAR */}
        <div
          className={`flex h-16 w-full shrink-0 flex-row items-center justify-between border-b px-3 py-2 xl:h-auto xl:w-20 xl:flex-col xl:border-b-0 xl:border-r xl:px-0 xl:py-6
        ${darkMode ? "bg-[#020617] border-white/10" : "bg-white shadow-lg"}`}
        >
          <div className="flex flex-row items-center gap-2 xl:flex-col xl:gap-6">
            <SidebarIcon
              src="/home.svg"
              label="Dashboard"
              active={location.pathname === "/dashboard"}
              onClick={() => navigate("/dashboard")}
              darkMode={darkMode}
            />

            <SidebarIcon
              src="/blocked.svg"
              label="Blocked employees"
              active={location.pathname === "/BlockedEmployees"} // ✅ FIX
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
        <main className="flex min-w-0 flex-1 flex-col p-4 sm:p-6 xl:h-full xl:min-h-0 xl:overflow-hidden">
          {/* CARDS */}
          <div className="mb-4 grid grid-cols-2 gap-3 sm:mb-6 sm:gap-4 xl:grid-cols-4">
            <Card title="Total Employees" value={uniqueEmployees.length} darkMode={darkMode} />
            <Card title="High Risk Employees" value={high} darkMode={darkMode} />
            <Card title="Medium Risk Employees" value={medium} darkMode={darkMode} />
            <Card title="Low Risk Employees" value={low} darkMode={darkMode} highlight />
          </div>

          {/* CONTENT */}
          <div className="grid min-h-0 flex-1 grid-cols-1 gap-4 xl:grid-cols-3 xl:gap-6 xl:overflow-hidden">
            <div
              className={`min-w-0 overflow-x-auto rounded-xl p-4 xl:col-span-2 ${
                darkMode ? "bg-[#1c2333]/70" : "bg-white shadow"
              }`}
            >
              <h2 className="mb-4 font-semibold">Live Threat Activity</h2>

              <div className="grid min-w-[680px] grid-cols-4 gap-3 text-sm text-gray-400 mb-2">
                <span>Employee</span>
                <span>Risk Score</span>
                <span>Indicator</span>
                <span>Status</span>
              </div>

              <div
                ref={activityListRef}
                onScroll={(event) => {
                  const list = event.currentTarget;
                  const distanceFromBottom =
                    list.scrollHeight - list.scrollTop - list.clientHeight;
                  shouldFollowNewEmployeesRef.current =
                    distanceFromBottom <= 24;
                }}
                className="h-[420px] min-w-[680px] overflow-y-auto pr-2 sm:h-[500px]"
              >
               {liveEmployees.map((u, i) => {
  const riskScore = Math.abs(Math.round(u.risk_score || 0));

  const level = u.risk_level?.trim().toUpperCase();

  const color =
    level === "HIGH"
      ? "bg-red-500"
      : level === "MEDIUM"
      ? "bg-yellow-400"
      : "bg-green-500";

  const isBlocked = blockedList.some(
    (b) => b.employee === u.employee
  );

                  return (
                    <div
                      key={i}
                      onClick={() => navigate(`/employee/${u.employee}`, {
                        state: { employees, blockedList },
                      })}
                      className={`grid grid-cols-4 gap-3 py-3 border-b cursor-pointer
                        ${
                          darkMode
                            ? "border-gray-600 hover:bg-[#2a344a]"
                            : "border-gray-200 hover:bg-gray-100"
                        }`}
                    >
                      <span className="flex gap-2 items-center">
                       

<span className={`w-3 h-3 rounded-full ${color}`} />
                        {u.employee}
                      </span>

                <div className="flex items-center gap-3">
  {/* SCORE */}
  <span className="w-10 text-sm">{riskScore}</span>

  {/* BAR (LIMITED WIDTH) */}
  <div className="w-40 bg-gray-600 h-2 rounded">
    <div
      className={`h-2 rounded ${color}`}
      style={{ width: `${riskScore}%` }}
    />
  </div>
</div>

                      <span>{getIndicator(u)}</span>

                      {/* ✅ STATUS FIX */}
                      {isBlocked ? (
                        <span className="text-red-500 font-semibold">
                          BLOCKED
                        </span>
                      ) : (
                        <span className="text-green-400">ACTIVE</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <div
              className={`min-w-0 rounded-xl p-4 ${
                darkMode ? "bg-[#1c2333]/70" : "bg-white shadow"
              }`}
            >
              <h2 className="mb-4 font-semibold">Risk Distribution</h2>

              <div className="h-72 sm:h-96 xl:h-[550px]">
                <RiskDistribution data={chartData} darkMode={darkMode} />
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

/* SIDEBAR ICON */
function SidebarIcon({ src, label, active, onClick, darkMode, danger }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`flex h-11 w-11 items-center justify-center rounded-xl cursor-pointer transition-all duration-300 xl:h-14 xl:w-14
      ${
        active
          ? darkMode
            ? "bg-blue-500 shadow-lg shadow-blue-500/30 scale-110 "
            : "bg-gray-200 shadow-md scale-110"
          : darkMode
          ? "hover:bg-white/10"
          : "hover:bg-gray-200"
      }
      ${danger ? "hover:bg-red-500/20" : ""}
      `}
    >
      <img
        src={src}
        alt=""
        width="24"
        height="24"
        className={`w-6 h-6 ${
          darkMode ? "invert opacity-80 hover:opacity-100" : ""
        }`}
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
          ? "bg-green-700/30"
          : darkMode
          ? "bg-[#1c2333]/70"
          : "bg-white shadow"
      }`}
    >
      <p className="text-sm leading-tight text-gray-400 sm:text-base">{title}</p>
      <h2 className="mt-1 text-2xl font-bold sm:text-4xl">{value}</h2>
    </div>
  );
}
