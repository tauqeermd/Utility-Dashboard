import React, { useEffect, useState } from "react";

function IssueFlag({ issues }) {
  if (!issues.length) return <span style={{ color: "green" }}>✔️</span>;
  return (
    <span style={{ color: "red" }}>
      {issues.map((i) => (
        <span key={i}>{i} </span>
      ))}
    </span>
  );
}

function App() {
  const [machines, setMachines] = useState([]);
  const [osFilter, setOsFilter] = useState("");
  const [issueFilter, setIssueFilter] = useState("");

  useEffect(() => {
    let url = "http://localhost:8000/api/machines";
    const params = [];
    if (osFilter) params.push(`os=${osFilter}`);
    if (issueFilter) params.push(`issue=${issueFilter}`);
    if (params.length) url += "?" + params.join("&");
    fetch(url)
      .then((r) => r.json())
      .then(setMachines);
  }, [osFilter, issueFilter]);

  return (
    <div style={{ padding: 32, fontFamily: "sans-serif" }}>
      <h1>System Health Dashboard</h1>
      <div style={{ marginBottom: 16 }}>
        <label>
          OS Filter:
          <select value={osFilter} onChange={e => setOsFilter(e.target.value)}>
            <option value="">All</option>
            <option value="Windows">Windows</option>
            <option value="Darwin">macOS</option>
            <option value="Linux">Linux</option>
          </select>
        </label>
        <label style={{ marginLeft: 16 }}>
          Issue Filter:
          <select value={issueFilter} onChange={e => setIssueFilter(e.target.value)}>
            <option value="">All</option>
            <option value="disk_encryption">Disk Encryption</option>
            <option value="os_update">OS Update</option>
            <option value="antivirus">Antivirus</option>
            <option value="sleep_setting">Sleep Setting</option>
          </select>
        </label>
      </div>
      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>Machine ID</th>
            <th>OS</th>
            <th>OS Version</th>
            <th>Disk Encryption</th>
            <th>OS Update</th>
            <th>Antivirus</th>
            <th>Sleep Setting</th>
            <th>Last Report</th>
            <th>Issues</th>
          </tr>
        </thead>
        <tbody>
          {machines.map((m) => (
            <tr key={m.machine_id}>
              <td>{m.machine_id}</td>
              <td>{m.os}</td>
              <td>{m.os_version}</td>
              <td>{m.disk_encryption ? "Yes" : "No"}</td>
              <td>{m.os_update ? "Yes" : "No"}</td>
              <td>{m.antivirus ? "Yes" : "No"}</td>
              <td>{m.sleep_setting_ok ? "Yes" : "No"}</td>
              <td>{new Date(m.last_report).toLocaleString()}</td>
              <td><IssueFlag issues={m.issues} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;