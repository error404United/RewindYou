import DaySection from "./DaySection";

export default function TimelineView({ data, onSelectEntry }) {
  return (
    <div style={{ flex: 1, padding: "1rem", overflowY: "auto" }}>
      {Object.entries(data).map(([date, entries]) => (
        <DaySection
          key={date}
          date={date}
          entries={entries}
          onSelectEntry={onSelectEntry}
        />
      ))}
    </div>
  );
}
