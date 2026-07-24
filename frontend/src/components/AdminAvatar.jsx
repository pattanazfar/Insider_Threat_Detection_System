export default function AdminAvatar({ large = false }) {
  return (
    <div
      role="img"
      aria-label="Application administrator"
      className={`flex shrink-0 items-center justify-center rounded-full border font-bold text-white shadow-lg ${
        large
          ? "mx-auto mb-4 h-20 w-20 border-4 border-blue-500 bg-gradient-to-br from-blue-600 to-indigo-800 text-xl"
          : "h-10 w-10 border-white/20 bg-gradient-to-br from-blue-600 to-indigo-800 text-sm"
      }`}
    >
      AD
    </div>
  );
}
