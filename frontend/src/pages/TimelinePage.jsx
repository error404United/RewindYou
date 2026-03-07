import React, { useState, useEffect } from "react";
import {
  Globe,
  TvMinimalPlay,
  FileText,
  X,
  Trash2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";
import "../styles/timeline.css";
import { getTimeline, deleteTimelineEntry } from "../apiClient";

export default function TimelinePage() {
  const [loading, setLoading] = useState(true);
  const [entries, setEntries] = useState([]);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(() => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    return `${year}-${month}`;
  });

  const parseUTCDate = (timestamp) => {
    if (!timestamp) return null;
    return new Date(timestamp.includes("+") ? timestamp : timestamp + "Z");
  };

  useEffect(() => {
    const fetchTimeline = async () => {
      try {
        setLoading(true);
        const data = await getTimeline(selectedMonth);
        setEntries(data);
      } catch (err) {
        console.error("Failed to fetch timeline:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimeline();
  }, [selectedMonth]);

  const getIcon = (url) => {
    if (!url) return <Globe size={18} />;

    if (url.includes("youtube.com") || url.includes("youtu.be"))
      return <TvMinimalPlay size={18} />;

    if (url.endsWith(".pdf")) return <FileText size={18} />;

    return <Globe size={18} />;
  };

  const formatMonthYear = (monthStr) => {
    const date = new Date(monthStr + "-01");
    return date.toLocaleDateString("en-IN", {
      month: "long",
      year: "numeric",
    });
  };

  const goToPreviousMonth = () => {
    const date = new Date(selectedMonth + "-01");
    date.setMonth(date.getMonth() - 1);

    const newMonth =
      date.getFullYear() + "-" + String(date.getMonth() + 1).padStart(2, "0");

    setSelectedMonth(newMonth);
  };

  const goToNextMonth = () => {
    const date = new Date(selectedMonth + "-01");
    date.setMonth(date.getMonth() + 1);

    const newMonth =
      date.getFullYear() + "-" + String(date.getMonth() + 1).padStart(2, "0");

    setSelectedMonth(newMonth);
  };

  const groupedByDate = entries.reduce((acc, entry) => {
    const dateObj = parseUTCDate(entry.created_at);

    const formattedDate = dateObj.toLocaleDateString("en-IN", {
      timeZone: "Asia/Kolkata",
      day: "2-digit",
      month: "long",
      year: "numeric",
    });

    const formattedTime = dateObj
      .toLocaleTimeString("en-IN", {
        timeZone: "Asia/Kolkata",
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      })
      .toLowerCase();

    if (!acc[formattedDate]) {
      acc[formattedDate] = [];
    }

    acc[formattedDate].push(entry);

    return acc;
  }, {});

  const handleDelete = async () => {
    if (!selectedEntry) return;

    try {
      await deleteTimelineEntry(selectedEntry.id);

      setEntries((prev) =>
        prev.filter((entry) => entry.id !== selectedEntry.id),
      );

      setSelectedEntry(null);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const hasEntries = Object.keys(groupedByDate).length > 0;

  return (
    <div className="timeline-container">
      <div className="timeline-header">
        <button className="month-nav-btn" onClick={goToPreviousMonth}>
          <ChevronLeft size={24} />
        </button>

        <div className="month-title">{formatMonthYear(selectedMonth)}</div>

        <button className="month-nav-btn" onClick={goToNextMonth}>
          <ChevronRight size={24} />
        </button>
      </div>

      {loading ? (
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      ) : hasEntries ? (
        Object.entries(groupedByDate).map(([date, dayEntries], index) => {
          const isLeft = index % 2 === 0;

          return (
            <>
              <div className="timeline-line"></div>
              <div
                key={date}
                className={`timeline-item ${isLeft ? "left" : "right"}`}
              >
                <div className="timeline-date">
                  <span>{date}</span>
                </div>

                <div className="timeline-card">
                  {dayEntries.map((entry) => (
                    <div
                      key={entry.id}
                      className="timeline-entry"
                      onClick={() =>
                        setSelectedEntry({
                          ...entry,
                          date,
                        })
                      }
                    >
                      <div className="entry-icon">{getIcon(entry.url)}</div>

                      <div className="timeline-entry-content">
                        <div className="entry-title">{entry.title}</div>
                        <div className="entry-time">
                          {parseUTCDate(entry.created_at)
                            .toLocaleTimeString("en-IN", {
                              timeZone: "Asia/Kolkata",
                              hour: "2-digit",
                              minute: "2-digit",
                              hour12: true,
                            })
                            .toLowerCase()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="timeline-dot"></div>
              </div>
            </>
          );
        })
      ) : (
        <div className="empty-state">
          <div className="empty-illustration">
            <img src="/emptyIllustration.svg" alt="No timeline entries" />
          </div>

          <h3>No memories in {formatMonthYear(selectedMonth)} yet</h3>

          <p>
            Start browsing and your captured content will appear here{" "}
            <Sparkles size={16} />
          </p>
        </div>
      )}

      <div className={`detail-panel ${selectedEntry ? "open" : ""}`}>
        {selectedEntry && (
          <>
            <X
              className="close-icon"
              size={20}
              onClick={() => setSelectedEntry(null)}
            />

            <div className="detail-title-row">
              <div className="detail-icon">{getIcon(selectedEntry.url)}</div>
              <h3 className="detail-title">{selectedEntry.title}</h3>
            </div>

            <div className="detail-date">
              {selectedEntry.date} •{" "}
              {parseUTCDate(selectedEntry.created_at)
                .toLocaleTimeString("en-IN", {
                  timeZone: "Asia/Kolkata",
                  hour: "2-digit",
                  minute: "2-digit",
                  hour12: true,
                })
                .toLowerCase()}
            </div>

            <a
              href={selectedEntry.url}
              target="_blank"
              rel="noreferrer"
              className="detail-url"
            >
              <ExternalLink size={16} />
              {selectedEntry.url}
            </a>

            <div className="detail-summary">{selectedEntry.summary}</div>

            <button className="delete-btn" onClick={handleDelete}>
              <Trash2 size={16} />
              Delete Entry
            </button>
          </>
        )}
      </div>
    </div>
  );
}
