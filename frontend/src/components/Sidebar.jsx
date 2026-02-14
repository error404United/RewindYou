export default function Sidebar({ selectedMonth, setSelectedMonth }) {
  const months = ["2026-01", "2026-02", "2026-03"];

  return (
    <div style={{ width: "200px", borderRight: "1px solid #ddd", padding: "1rem" }}>
      <h3>Months</h3>
      {months.map((month) => (
        <div
          key={month}
          onClick={() => setSelectedMonth(month)}
          style={{
            padding: "8px",
            cursor: "pointer",
            background: selectedMonth === month ? "#eee" : "transparent"
          }}
        >
          {month}
        </div>
      ))}
    </div>
  );
}
