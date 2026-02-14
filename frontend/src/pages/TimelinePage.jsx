import React, { useState } from "react";
import {
  Globe,
  TvMinimalPlay,
  FileText,
  X,
  Trash2,
  ExternalLink,
} from "lucide-react";
import "../styles/timeline.css";

const mockData = {
  "2026-02": {
    "02 February 2026": [
      {
        id: 1,
        title: "Introduction to Compiler Design",
        type: "webpage",
        time: "08:45 AM",
        url: "https://example.com/compiler-intro",
        content_summary:
          "Overview of compiler phases including lexical analysis, parsing, semantic analysis, optimization, and code generation.",
      },
      {
        id: 2,
        title: "Lexical Analysis Explained",
        type: "youtube",
        time: "03:20 PM",
        url: "https://youtube.com/lexical-analysis",
        content_summary:
          "Video explanation of tokenization, regular expressions, and how lexical analyzers work in modern compilers.",
      },
    ],

    "05 February 2026": [
      {
        id: 3,
        title: "Understanding Transformers Architecture",
        type: "webpage",
        time: "09:12 AM",
        url: "https://example.com/transformers",
        content_summary:
          "Detailed explanation of the transformer model architecture including self-attention, multi-head attention, and positional encoding.",
      },
      {
        id: 4,
        title: "Attention Is All You Need",
        type: "youtube",
        time: "04:30 PM",
        url: "https://youtube.com/attention-paper",
        content_summary:
          "Walkthrough of the original transformer research paper and why it revolutionized NLP.",
      },
    ],

    "08 February 2026": [
      {
        id: 5,
        title: "NLP Research Paper - BERT Overview",
        type: "pdf",
        time: "11:00 AM",
        url: "https://example.com/bert-paper.pdf",
        content_summary:
          "Research paper explaining Bidirectional Encoder Representations from Transformers and pre-training strategies.",
      },
    ],

    "10 February 2026": [
      {
        id: 6,
        title: "Graph Algorithms - Dijkstra’s Algorithm",
        type: "webpage",
        time: "10:15 AM",
        url: "https://example.com/dijkstra",
        content_summary:
          "Step-by-step breakdown of Dijkstra’s shortest path algorithm with time complexity analysis.",
      },
      {
        id: 7,
        title: "Minimum Spanning Tree Visualized",
        type: "youtube",
        time: "06:10 PM",
        url: "https://youtube.com/mst-visual",
        content_summary:
          "Visual explanation of Prim’s and Kruskal’s algorithms with animated examples.",
      },
      {
        id: 8,
        title: "Operating Systems - Process Scheduling",
        type: "webpage",
        time: "09:00 AM",
        url: "https://example.com/os-scheduling",
        content_summary:
          "Explains CPU scheduling algorithms including FCFS, SJF, Round Robin, and priority scheduling.",
      },
    ],

    "14 February 2026": [
      {
        id: 9,
        title: "Deadlock and Resource Allocation",
        type: "pdf",
        time: "02:45 PM",
        url: "https://example.com/deadlock.pdf",
        content_summary:
          "Comprehensive notes on deadlock conditions, prevention strategies, and Banker's Algorithm.",
      },
    ],
  },
};

export default function TimelinePage() {
  const [selectedEntry, setSelectedEntry] = useState(null);
  const monthData = mockData["2026-02"];

  const getIcon = (type) => {
    switch (type) {
      case "webpage":
        return <Globe size={18} />;
      case "youtube":
        return <TvMinimalPlay size={18} />;
      case "pdf":
        return <FileText size={18} />;
      default:
        return null;
    }
  };

  return (
    <div className="timeline-container">
      <div className="timeline-line"></div>

      {Object.entries(monthData).map(([date, entries], index) => {
        const isLeft = index % 2 === 0;

        return (
          <div
            key={date}
            className={`timeline-item ${isLeft ? "left" : "right"}`}
          >
            <div className="timeline-date"><span>{date}</span></div>

            <div className="timeline-card">
              {entries.map((entry) => (
                <div
                  key={entry.id}
                  className="timeline-entry"
                  onClick={() => setSelectedEntry(entry)}
                >
                  <div className="entry-icon">{getIcon(entry.type)}</div>
                  <div className="timeline-entry-content">
                    <div className="entry-title">{entry.title}</div>
                    <div className="entry-time">{entry.time}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="timeline-dot"></div>
          </div>
        );
      })}

      <div className={`detail-panel ${selectedEntry ? "open" : ""}`}>
        {selectedEntry && (
          <>
            <X
              className="close-icon"
              size={20}
              onClick={() => setSelectedEntry(null)}
            />

            <div className="detail-title-row">
              <div className="detail-icon">{getIcon(selectedEntry.type)}</div>
              <h3 className="detail-title">{selectedEntry.title}</h3>
            </div>

            <div className="detail-date">
              {selectedEntry.date} • {selectedEntry.time}
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

            <div className="detail-summary">
              {selectedEntry.content_summary}
            </div>

            <button className="delete-btn">
              <Trash2 size={16} />
              Delete Entry
            </button>
          </>
        )}
      </div>
    </div>
  );
}
