export default function RiskDistribution({ data, darkMode }) {
  const maxValue = Math.max(...data.map((item) => item.value), 1);

  return (
    <div
      role="img"
      aria-label={data
        .map((item) => `${item.name}: ${item.value} employees`)
        .join(", ")}
      className="flex h-full items-end justify-around gap-4 px-2 pb-2 pt-8"
    >
      {data.map((item) => {
        const height = item.value
          ? Math.max((item.value / maxValue) * 100, 8)
          : 2;

        return (
          <div
            key={item.name}
            className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-2"
          >
            <span
              className={`text-sm font-semibold ${
                darkMode ? "text-slate-200" : "text-slate-700"
              }`}
            >
              {item.value}
            </span>
            <div className="flex h-full w-full max-w-20 items-end overflow-hidden rounded-t-md bg-slate-500/10">
              <div
                className="w-full rounded-t-md transition-[height] duration-300"
                style={{
                  backgroundColor: item.color,
                  height: `${height}%`,
                }}
              />
            </div>
            <span
              className={`text-xs font-medium sm:text-sm ${
                darkMode ? "text-slate-300" : "text-slate-600"
              }`}
            >
              {item.name}
            </span>
          </div>
        );
      })}
    </div>
  );
}
