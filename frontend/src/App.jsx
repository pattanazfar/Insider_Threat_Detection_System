import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

const Login = lazy(() => import("./pages/Login"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const EmployeeDetails = lazy(() => import("./pages/EmployeeDetails"));
const BlockedEmployees = lazy(() => import("./pages/BlockedEmployees"));

function PageLoader() {
  return (
    <div className="flex min-h-[100dvh] items-center justify-center bg-slate-950 text-white">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-blue-400 border-t-transparent" />
      <span className="sr-only">Loading page</span>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/employee/:employee" element={<EmployeeDetails />} />
          <Route path="/BlockedEmployees" element={<BlockedEmployees />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;
