import { useState, useEffect } from "react"
import axios from "axios"
import {
  Chart as ChartJS,
  CategoryScale, LinearScale,
  BarElement, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
} from "chart.js"
import { Bar, Line } from "react-chartjs-2"

ChartJS.register(
  CategoryScale, LinearScale,
  BarElement, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
)

const API = "http://127.0.0.1:5000/api"

const TYPE_COLORS = {
  sql_injection:          { bg: "#ef4444", light: "#ef444420", border: "#ef444460", label: "SQL Injection" },
  directory_traversal:    { bg: "#f97316", light: "#f9731620", border: "#f9731660", label: "Dir Traversal" },
  command_injection:      { bg: "#eab308", light: "#eab30820", border: "#eab30860", label: "Cmd Injection" },
  xss:                    { bg: "#a855f7", light: "#a855f720", border: "#a855f760", label: "XSS" },
  HONEYTOKEN_ACCESS:      { bg: "#ec4899", light: "#ec489920", border: "#ec489960", label: "Honeytoken" },
  HONEYPOT_BROWSE:        { bg: "#3b82f6", light: "#3b82f620", border: "#3b82f660", label: "Honeypot Browse" },
  HONEYPOT_FILE_DOWNLOAD: { bg: "#06b6d4", light: "#06b6d420", border: "#06b6d460", label: "File Download" },
}

// Fix: add Z suffix so JS knows timestamp is UTC, then convert to IST
const toIST = (timestamp) => {
  const utcString = timestamp.endsWith("Z") ? timestamp : timestamp + "Z"
  return new Date(utcString).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "Asia/Kolkata",
    hour12: true
  })
}

const getColor = (type) =>
  TYPE_COLORS[type] || { bg: "#64748b", light: "#64748b20", border: "#64748b60", label: type }

function AttackBadge({ type }) {
  const c = getColor(type)
  return (
    <span style={{
      background: c.light,
      color: c.bg,
      border: `1px solid ${c.border}`,
      borderRadius: 6,
      padding: "3px 10px",
      fontSize: 11,
      fontWeight: 700,
      letterSpacing: 0.3,
      whiteSpace: "nowrap",
      fontFamily: "monospace"
    }}>
      {c.label}
    </span>
  )
}

function StatCard({ label, value, color, icon, sub }) {
  return (
    <div style={{
      background: "#111827",
      border: "1px solid #1f2d45",
      borderTop: `3px solid ${color}`,
      borderRadius: 12,
      padding: "20px 24px",
      flex: 1,
      minWidth: 160,
      position: "relative",
      overflow: "hidden"
    }}>
      <div style={{
        position: "absolute", right: 20, top: 20,
        fontSize: 28, opacity: 0.15
      }}>{icon}</div>
      <div style={{
        fontSize: 11, color: "#64748b",
        textTransform: "uppercase", letterSpacing: 1, marginBottom: 8
      }}>
        {label}
      </div>
      <div style={{
        fontSize: 36, fontWeight: 700,
        color, fontFamily: "monospace", lineHeight: 1
      }}>
        {value}
      </div>
      {sub && (
        <div style={{ fontSize: 12, color: "#475569", marginTop: 6 }}>{sub}</div>
      )}
    </div>
  )
}

function LiveDot() {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
      <span style={{
        width: 8, height: 8, borderRadius: "50%",
        background: "#22c55e", display: "inline-block",
        animation: "livepulse 2s infinite"
      }}/>
      <span style={{ color: "#22c55e", fontSize: 12, fontWeight: 600 }}>LIVE</span>
    </span>
  )
}

export default function App() {
  const [stats,      setStats]      = useState(null)
  const [attacks,    setAttacks]    = useState([])
  const [error,      setError]      = useState(null)
  const [lastUpdate, setLastUpdate] = useState(null)

  const fetchData = async () => {
    try {
      const [s, a] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/attacks`)
      ])
      setStats(s.data)
      setAttacks(a.data)
      setLastUpdate(
        new Date().toLocaleTimeString("en-IN", {
          timeZone: "Asia/Kolkata",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: true
        })
      )
      setError(null)
    } catch {
      setError("Cannot reach interceptor — make sure it is running on port 5000")
    }
  }

  useEffect(() => {
    fetchData()
    const t = setInterval(fetchData, 5000)
    return () => clearInterval(t)
  }, [])

  if (error) return (
    <div style={{
      padding: 40, fontFamily: "monospace",
      color: "#ef4444", background: "#0a0e1a", minHeight: "100vh"
    }}>
      <h2>⚠️ Connection Error</h2>
      <p style={{ marginTop: 12, color: "#64748b" }}>{error}</p>
      <button onClick={fetchData} style={{
        marginTop: 20, padding: "10px 24px",
        background: "#3b82f6", border: "none",
        borderRadius: 8, color: "white",
        cursor: "pointer", fontSize: 14
      }}>Retry</button>
    </div>
  )

  if (!stats) return (
    <div style={{
      padding: 40, fontFamily: "monospace",
      color: "#64748b", background: "#0a0e1a",
      minHeight: "100vh", display: "flex",
      alignItems: "center", justifyContent: "center"
    }}>
      <div>
        <div style={{ fontSize: 32, marginBottom: 12 }}>🛡️</div>
        <div>Connecting to honeypot server...</div>
      </div>
    </div>
  )

  // ── Timeline — every attack at its exact IST time ──────────────────────
  const timelineMap = {}
  attacks.slice().reverse().forEach(a => {
    const t = toIST(a.timestamp)
    timelineMap[t] = (timelineMap[t] || 0) + 1
  })
  const timelineLabels = Object.keys(timelineMap)
  const timelineData   = timelineLabels.map(k => timelineMap[k])

  // ── Attack type breakdown ──────────────────────────────────────────────
  const typeLabels      = Object.keys(stats.by_type)
  const typeData        = Object.values(stats.by_type)
  const typeColors      = typeLabels.map(t => getColor(t).bg)
  const typeLightColors = typeLabels.map(t => getColor(t).light)

  // ── Insight calculations ───────────────────────────────────────────────
  const pathMap = {}
  attacks.forEach(a => { pathMap[a.path] = (pathMap[a.path] || 0) + 1 })
  const topPath        = Object.entries(pathMap).sort((a, b) => b[1] - a[1])[0]
  const topAttack      = typeLabels[typeData.indexOf(Math.max(...typeData))]
  const topAttackColor = getColor(topAttack).bg
  const honeytokenHits = attacks.filter(a => a.attack_type === "HONEYTOKEN_ACCESS").length
  const honeypotHits   = attacks.filter(a =>
    a.attack_type === "HONEYPOT_BROWSE" ||
    a.attack_type === "HONEYPOT_FILE_DOWNLOAD"
  ).length

  return (
    <div style={{
      background: "#0a0e1a", minHeight: "100vh",
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      color: "#e2e8f0"
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
        @keyframes livepulse {
          0%   { box-shadow: 0 0 0 0 #22c55e60; }
          70%  { box-shadow: 0 0 0 8px #22c55e00; }
          100% { box-shadow: 0 0 0 0 #22c55e00; }
        }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #111827; }
        ::-webkit-scrollbar-thumb { background: #1f2d45; border-radius: 3px; }
      `}</style>

      {/* ── Header ── */}
      <div style={{
        background: "#111827",
        borderBottom: "1px solid #1f2d45",
        padding: "0 32px",
        height: 60,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        position: "sticky",
        top: 0,
        zIndex: 100
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{
            width: 36, height: 36,
            background: "linear-gradient(135deg, #3b82f6, #06b6d4)",
            borderRadius: 8,
            display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 18
          }}>🛡️</div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 16 }}>Honeypot Control Center</div>
            <div style={{ fontSize: 11, color: "#475569" }}>
              Proactive Cyber Defense — Live Monitoring
            </div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div style={{ fontSize: 12, color: "#475569" }}>
            IST &nbsp;
            <span style={{ color: "#94a3b8", fontFamily: "monospace" }}>
              {lastUpdate}
            </span>
          </div>
          <LiveDot />
        </div>
      </div>

      <div style={{ padding: "28px 32px", maxWidth: 1400, margin: "0 auto" }}>

        {/* ── Stat cards ── */}
        <div style={{ display: "flex", gap: 16, marginBottom: 24, flexWrap: "wrap" }}>
          <StatCard
            label="Total Attacks Detected"
            value={stats.total}
            color="#ef4444"
            icon="⚡"
            sub="Since monitoring began"
          />
          <StatCard
            label="Attack Types Seen"
            value={Object.keys(stats.by_type).length}
            color="#f97316"
            icon="🎯"
            sub="Unique attack vectors"
          />
          <StatCard
            label="Honeytokens Triggered"
            value={honeytokenHits}
            color="#ec4899"
            icon="🪤"
            sub="Insider threat detections"
          />
          <StatCard
            label="Honeypot Interactions"
            value={honeypotHits}
            color="#3b82f6"
            icon="🕵️"
            sub="Attacker trapped and monitored"
          />
        </div>

        {/* ── Threat summary bar ── */}
        <div style={{
          background: "#111827",
          border: "1px solid #1f2d45",
          borderLeft: `4px solid ${topAttackColor}`,
          borderRadius: 10,
          padding: "14px 24px",
          marginBottom: 24,
          display: "flex",
          alignItems: "center",
          gap: 32,
          flexWrap: "wrap"
        }}>
          <div style={{ fontSize: 13 }}>
            <span style={{ color: "#64748b" }}>🔴 Top threat: </span>
            <span style={{ color: topAttackColor, fontWeight: 600 }}>
              {getColor(topAttack).label}
            </span>
            <span style={{ color: "#475569" }}>
              {" "}— {Math.max(...typeData)} occurrences
            </span>
          </div>
          <div style={{ fontSize: 13 }}>
            <span style={{ color: "#64748b" }}>📁 Most targeted: </span>
            <span style={{ color: "#38bdf8", fontFamily: "monospace", fontSize: 12 }}>
              {topPath?.[0]}
            </span>
          </div>
          <div style={{ fontSize: 13 }}>
            <span style={{ color: "#64748b" }}>🌐 Attacker IP: </span>
            <span style={{ color: "#94a3b8", fontFamily: "monospace" }}>
              127.0.0.1
            </span>
            <span style={{ color: "#334155" }}> — localhost (demo environment)</span>
          </div>
          <div style={{ fontSize: 13 }}>
            <span style={{ color: "#64748b" }}>🕐 Timezone: </span>
            <span style={{ color: "#94a3b8" }}>IST (Asia/Kolkata)</span>
          </div>
        </div>

        {/* ── Charts ── */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 20,
          marginBottom: 24
        }}>

          {/* Attack Timeline */}
          <div style={{
            background: "#111827",
            border: "1px solid #1f2d45",
            borderRadius: 12,
            padding: 24
          }}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 600, fontSize: 15 }}>Attack Timeline (IST)</div>
              <div style={{ fontSize: 12, color: "#475569", marginTop: 2 }}>
                Each point = one attack event at that exact IST time
              </div>
            </div>
            <Line
              data={{
                labels: timelineLabels,
                datasets: [{
                  label: "Attacks",
                  data: timelineData,
                  borderColor: "#3b82f6",
                  backgroundColor: "#3b82f615",
                  borderWidth: 2,
                  pointBackgroundColor: "#3b82f6",
                  pointBorderColor: "#fff",
                  pointRadius: 5,
                  pointHoverRadius: 7,
                  fill: true,
                  tension: 0.3
                }]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false },
                  tooltip: {
                    callbacks: {
                      title: (items) => `IST Time: ${items[0].label}`,
                      label: (item)  => `Attacks: ${item.raw}`
                    }
                  }
                },
                scales: {
                  x: {
                    ticks: {
                      color: "#475569",
                      font: { size: 10 },
                      maxRotation: 45
                    },
                    grid: { color: "#1f2d45" }
                  },
                  y: {
                    ticks: {
                      color: "#475569",
                      font: { size: 11 },
                      stepSize: 1
                    },
                    grid: { color: "#1f2d45" },
                    beginAtZero: true
                  }
                }
              }}
            />
          </div>

          {/* Attack Type Breakdown */}
          <div style={{
            background: "#111827",
            border: "1px solid #1f2d45",
            borderRadius: 12,
            padding: 24
          }}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 600, fontSize: 15 }}>Attack Type Breakdown</div>
              <div style={{ fontSize: 12, color: "#475569", marginTop: 2 }}>
                Frequency by attack category — all types shown
              </div>
            </div>
            <Bar
              data={{
                labels: typeLabels.map(t => getColor(t).label),
                datasets: [{
                  label: "Count",
                  data: typeData,
                  backgroundColor: typeLightColors,
                  borderColor: typeColors,
                  borderWidth: 2,
                  borderRadius: 6,
                }]
              }}
              options={{
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                  x: {
                    ticks: { color: "#475569", font: { size: 11 } },
                    grid: { color: "#1f2d45" }
                  },
                  y: {
                    ticks: {
                      color: "#475569",
                      font: { size: 11 },
                      stepSize: 1
                    },
                    grid: { color: "#1f2d45" },
                    beginAtZero: true
                  }
                }
              }}
            />
          </div>
        </div>

        {/* ── Attack type progress cards ── */}
        <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
          {Object.entries(stats.by_type).map(([type, count]) => {
            const c   = getColor(type)
            const pct = Math.round((count / stats.total) * 100)
            return (
              <div key={type} style={{
                background: "#111827",
                border: "1px solid #1f2d45",
                borderRadius: 10,
                padding: "14px 18px",
                flex: 1,
                minWidth: 150
              }}>
                <div style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 10
                }}>
                  <span style={{ fontSize: 12, color: "#64748b" }}>{c.label}</span>
                  <span style={{
                    fontSize: 20, fontWeight: 700,
                    color: c.bg, fontFamily: "monospace"
                  }}>{count}</span>
                </div>
                <div style={{
                  background: "#1f2d45",
                  borderRadius: 4, height: 4, overflow: "hidden"
                }}>
                  <div style={{
                    width: `${pct}%`,
                    height: "100%",
                    background: c.bg,
                    borderRadius: 4,
                    transition: "width 0.6s ease"
                  }}/>
                </div>
                <div style={{ fontSize: 11, color: "#334155", marginTop: 6 }}>
                  {pct}% of all attacks
                </div>
              </div>
            )
          })}
        </div>

        {/* ── Attack log table ── */}
        <div style={{
          background: "#111827",
          border: "1px solid #1f2d45",
          borderRadius: 12,
          overflow: "hidden"
        }}>
          <div style={{
            padding: "18px 24px",
            borderBottom: "1px solid #1f2d45",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15 }}>Attack Log</div>
              <div style={{ fontSize: 12, color: "#475569", marginTop: 2 }}>
                Complete record of all detected threats — times shown in IST
              </div>
            </div>
            <div style={{
              background: "#ef444420",
              border: "1px solid #ef444440",
              color: "#fca5a5",
              fontSize: 12,
              padding: "4px 14px",
              borderRadius: 20,
              fontFamily: "monospace"
            }}>
              {attacks.length} events logged
            </div>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ borderBottom: "1px solid #1f2d45" }}>
                  {["#", "Time (IST)", "IP Address", "Attack Type", "Path Targeted", "User Agent"].map(h => (
                    <th key={h} style={{
                      padding: "12px 20px",
                      textAlign: "left",
                      fontSize: 11,
                      textTransform: "uppercase",
                      letterSpacing: 0.8,
                      color: "#334155",
                      fontWeight: 600,
                      whiteSpace: "nowrap"
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {attacks.length === 0 && (
                  <tr>
                    <td colSpan={6} style={{
                      padding: 40,
                      textAlign: "center",
                      color: "#334155"
                    }}>
                      No attacks logged yet — run a simulation to see data here
                    </td>
                  </tr>
                )}
                {attacks.map((a, i) => (
                  <tr
                    key={i}
                    style={{ borderBottom: "1px solid #1f2d4530", transition: "background 0.15s" }}
                    onMouseEnter={e => e.currentTarget.style.background = "#1e293b40"}
                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                  >
                    <td style={{
                      padding: "12px 20px",
                      color: "#334155",
                      fontFamily: "monospace",
                      fontSize: 11
                    }}>
                      {attacks.length - i}
                    </td>
                    <td style={{
                      padding: "12px 20px",
                      color: "#64748b",
                      fontFamily: "monospace",
                      fontSize: 12,
                      whiteSpace: "nowrap"
                    }}>
                      {toIST(a.timestamp)}
                    </td>
                    <td style={{
                      padding: "12px 20px",
                      fontFamily: "monospace",
                      fontSize: 12,
                      color: "#94a3b8"
                    }}>
                      {a.ip}
                    </td>
                    <td style={{ padding: "12px 20px" }}>
                      <AttackBadge type={a.attack_type} />
                    </td>
                    <td style={{
                      padding: "12px 20px",
                      fontFamily: "monospace",
                      fontSize: 11,
                      color: "#38bdf8"
                    }}>
                      {a.path}
                    </td>
                    <td style={{
                      padding: "12px 20px",
                      color: "#334155",
                      fontSize: 11,
                      maxWidth: 200,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap"
                    }}>
                      {a.user_agent}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* ── Footer ── */}
        <div style={{
          textAlign: "center",
          marginTop: 28,
          fontSize: 12,
          color: "#1f2d45",
          paddingBottom: 20
        }}>
          Proactive Cyber Defense System — Honeypot & Honeytoken Deception Techniques
          &nbsp;|&nbsp; RVU Network Security Project
        </div>

      </div>
    </div>
  )
}
