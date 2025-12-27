import { useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function Home() {
  const [selfieA, setSelfieA] = useState(null);
  const [selfieB, setSelfieB] = useState(null);
  const [envPrompt, setEnvPrompt] = useState("create a selfie of the image shared in music cafe");
  const [status, setStatus] = useState(null);
  const [resultUrl, setResultUrl] = useState("");
  const [jobId, setJobId] = useState("");

  async function submit() {
    setResultUrl("");
    setStatus(null);

    const form = new FormData();
    form.append("env_prompt", envPrompt);
    form.append("selfie_a", selfieA);
    form.append("selfie_b", selfieB);

    const res = await fetch(`${API_BASE}/generate`, {
      method: "POST",
      body: form,
    });

    const data = await res.json();
    setJobId(data.job_id);
    poll(data.job_id);
  }

  function poll(id) {
    const interval = setInterval(async () => {
      const res = await fetch(`${API_BASE}/status/${id}`);
      const s = await res.json();
      setStatus(s);

      if (s.status === "done") {
        clearInterval(interval);
        setResultUrl(`${API_BASE}${s.result_url}`);
      }
      if (s.status === "failed") {
        clearInterval(interval);
      }
    }, 1500);
  }

  return (
    <main style={{ maxWidth: 760, margin: "40px auto", fontFamily: "system-ui" }}>
      <h1>Group Selfie App (MVP)</h1>
      <p>Upload 2 selfies + environment prompt → get output (mock for now)</p>

      <div style={{ marginTop: 16 }}>
        <label><b>Selfie A</b></label><br />
        <input type="file" accept="image/*" onChange={(e) => setSelfieA(e.target.files[0])} />
      </div>

      <div style={{ marginTop: 16 }}>
        <label><b>Selfie B</b></label><br />
        <input type="file" accept="image/*" onChange={(e) => setSelfieB(e.target.files[0])} />
      </div>

      <div style={{ marginTop: 16 }}>
        <label><b>Environment prompt</b></label><br />
        <input
          style={{ width: "100%", padding: 10 }}
          value={envPrompt}
          onChange={(e) => setEnvPrompt(e.target.value)}
        />
      </div>

      <button
        style={{ marginTop: 16, padding: "10px 16px", cursor: "pointer" }}
        onClick={submit}
        disabled={!selfieA || !selfieB || !envPrompt}
      >
        Generate
      </button>

      {jobId && (
        <div style={{ marginTop: 16 }}>
          <b>Job ID:</b> {jobId}
        </div>
      )}

      {status && (
        <div style={{ marginTop: 16 }}>
          <b>Status:</b> {status.status}<br />
          <b>Message:</b> {status.message}<br />
          <b>Progress:</b> {Math.round((status.progress || 0) * 100)}%
        </div>
      )}

      {resultUrl && (
        <div style={{ marginTop: 24 }}>
          <h3>Output</h3>
          <img src={resultUrl} alt="final" style={{ width: "100%", borderRadius: 12 }} />
        </div>
      )}
    </main>
  );
}
