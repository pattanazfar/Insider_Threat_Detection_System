import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import api from "../utils/api";
import AdminAvatar from "../components/AdminAvatar";

export default function BlockedEmployees() {
  const navigate = useNavigate();
  const location = useLocation();

  const [data, setData] = useState([]);
  const [search, setSearch] = useState("");
const [darkMode, setDarkMode] = useState(() => {
  return localStorage.getItem("theme") === "light" ? false : true;
});

  useEffect(() => {
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  // 📡 Fetch blocked employees
  const fetchData = async () => {
    try {
      const res = await api.get("/api/blocked");
      setData(res.data);
    } catch (err) {
      console.log(err);
    }
  };

useEffect(() => {
  let mounted = true;

  const load = async () => {
    try {
      const res = await api.get("/api/blocked");
      if (mounted) setData(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  load();

  return () => {
    mounted = false;
  };
}, []);

  // 🔓 Unblock
  const handleUnblock = async (employee) => {
    await api.delete(`/api/unblock/${employee}`);
    fetchData();
  };

  const filteredEmployees = data.filter((employee) =>
    String(employee.employee || "")
      .toLowerCase()
      .includes(search.trim().toLowerCase())
  );

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
        className={`sticky top-0 z-40 flex shrink-0 flex-col items-stretch justify-between gap-3 border-b px-4 py-3 backdrop-blur-xl sm:flex-row sm:items-center sm:px-6 sm:py-4 ${
          darkMode
            ? "bg-gradient-to-r from-[#0f172a]/95 to-[#1e293b]/95 border-white/10"
            : "bg-white/95 shadow"
        }`}
      >
        <div className="flex min-w-0 items-center gap-3 sm:gap-4">
          <img src="/logo.jpg" width="32" height="32" alt="" className="h-8 w-8 shrink-0" />
          <h1 className="text-sm font-semibold leading-tight sm:text-lg">
            Insider Threat Detection System - Blocked Employees
          </h1>
        </div>

        <div className="flex w-full items-center gap-3 sm:w-auto sm:gap-4">
          <div
            className={`flex min-w-0 flex-1 items-center rounded-full border px-4 py-2 sm:w-64 ${
              darkMode
                ? "bg-[#0f172a]/60 border-white/10 focus-within:border-blue-400"
                : "bg-gray-100 border-gray-200"
            }`}
          >
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search Blocked Employee"
              aria-label="Search blocked employees"
              className="w-full min-w-0 bg-transparent text-sm outline-none"
            />
          </div>

          <div className="hidden shrink-0 sm:block">
            <AdminAvatar />
          </div>
        </div>
      </div>

      <div className="flex flex-1 flex-col xl:min-h-0 xl:flex-row">
        {/* SIDEBAR */}
        <div
          className={`order-last sticky bottom-0 z-30 flex w-full shrink-0 flex-row items-center justify-between border-t px-3 py-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] backdrop-blur-xl xl:order-none xl:h-auto xl:w-20 xl:flex-col xl:border-t-0 xl:px-0 xl:py-6 ${
            darkMode
              ? "bg-[#020617]/95 border-white/10"
              : "bg-white/95 border-gray-200 shadow-lg"
          }`}
        >
          <div className="flex flex-row items-center gap-2 xl:flex-col xl:gap-6">
            <SidebarIcon
              src="/home.svg"
              label="Dashboard"
              onClick={() => navigate("/dashboard")}
              darkMode={darkMode}
            />

            <SidebarIcon
              src="/blocked.svg"
              label="Blocked employees"
              active={location.pathname === "/BlockedEmployees"}
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

        {/* MAIN CONTENT */}
        <main className="min-w-0 flex-1 overflow-y-auto p-4 pb-24 sm:p-6 sm:pb-28 xl:pb-6">
          <h2 className="mb-4 text-xl font-semibold sm:mb-6">Blocked Employees 🚫</h2>

          {data.length === 0 ? (
            <p className="text-gray-400">No blocked employees</p>
          ) : filteredEmployees.length === 0 ? (
            <p className="text-gray-400">
              No blocked employees match &quot;{search.trim()}&quot;
            </p>
          ) : (
            <div className="grid gap-4">
              {filteredEmployees.map((emp, i) => (
                <div
                  key={emp.employee || i}
                  role="button"
                  tabIndex={0}
                  onClick={() => navigate(`/employee/${emp.employee}`)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      navigate(`/employee/${emp.employee}`);
                    }
                  }}
                  className={`flex cursor-pointer flex-col items-stretch gap-4 rounded-xl p-4 transition-colors sm:flex-row sm:items-center sm:justify-between ${
                    darkMode
                      ? "bg-[#1c2333] hover:bg-[#252e42]"
                      : "bg-white shadow border border-gray-200 hover:bg-gray-50"
                  }`}
                >
                  {/* LEFT */}
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center">
                      🚫
                    </div>

                    <div>
                      <h3 className="font-semibold">{emp.employee}</h3>
                      <p className="text-sm text-gray-400">
                        Blocked Employee
                      </p>
                    </div>
                  </div>

                  {/* RIGHT */}
                  <button
                    onClick={(event) => {
                      event.stopPropagation();
                      handleUnblock(emp.employee);
                    }}
                    className="w-full rounded-lg bg-green-600 px-4 py-2 text-white hover:bg-green-500 sm:w-auto"
                  >
                    Unblock
                  </button>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

/* SIDEBAR ICON */
function SidebarIcon({ src, label, active, onClick, danger, darkMode }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      className={`flex h-11 w-11 items-center justify-center rounded-xl cursor-pointer transition-all md:h-12 md:w-12 xl:h-14 xl:w-14 ${
        active
          ? darkMode
            ? "bg-blue-500 scale-110"
            : "bg-gray-200 shadow-md scale-110"   // ✅ FIX HERE
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
