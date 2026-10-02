import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const DOC = ["DOCX", "word"], PDF = ["PDF", "pdf"], IMG = ["Image", "img"];

// Endpoint ids match the backend routes in /api/tools/<id>
const TOOLS = [
  { id: "word-to-pdf", group: "Documents", name: "Word to PDF", from: DOC, to: PDF, accept: ".docx", kind: "a .docx file", out: "PDF", blurb: "Turn a Word document into a PDF that looks the same on every device." },
  { id: "pdf-to-word", group: "Documents", name: "PDF to Word", from: PDF, to: DOC, accept: ".pdf", kind: "a .pdf file", out: "Word document", blurb: "Get an editable .docx from a PDF. Scanned PDFs need OCR and won't convert well." },
  { id: "pdf-merge", group: "PDF", name: "Merge PDF", from: PDF, to: PDF, accept: ".pdf", kind: "PDF files", out: "PDF", multiple: true, blurb: "Combine two or more PDFs into a single document." },
  { id: "pdf-split", group: "PDF", name: "Split PDF", from: PDF, to: PDF, accept: ".pdf", kind: "a .pdf file", out: "PDF", note: "Split currently returns the first page only.", blurb: "Separate a PDF into individual pages." },
  { id: "pdf-compress", group: "PDF", name: "Compress PDF", from: PDF, to: PDF, accept: ".pdf", kind: "a .pdf file", out: "PDF", blurb: "Reduce the file size of a PDF so it's easier to send." },
  { id: "pdf-rotate", group: "PDF", name: "Rotate PDF", from: PDF, to: PDF, accept: ".pdf", kind: "a .pdf file", out: "PDF", blurb: "Fix pages that were scanned or saved sideways.",
    opts: [{ key: "degrees", label: "Rotation", type: "select", value: "90", choices: [["90", "90°"], ["180", "180°"], ["270", "270°"]] }] },
  { id: "image-resize", group: "Images", name: "Resize Image", from: IMG, to: IMG, accept: "image/*", kind: "an image", out: "image", blurb: "Set an exact width and height in pixels.",
    opts: [{ key: "width", label: "Width (px)", type: "number", value: 1000 }, { key: "height", label: "Height (px)", type: "number", value: 1000 }] },
  { id: "image-compress", group: "Images", name: "Compress Image", from: IMG, to: IMG, accept: "image/*", kind: "an image", out: "image", blurb: "Shrink an image's file size. Lower quality means a smaller file.",
    opts: [{ key: "quality", label: "Quality", type: "range", value: 75, min: 1, max: 100 }] },
  { id: "image-convert", group: "Images", name: "Convert Image", from: IMG, to: IMG, accept: "image/*", kind: "an image", out: "image", blurb: "Switch an image between PNG, JPG and WebP.",
    opts: [{ key: "format", label: "Convert to", type: "select", value: "png", choices: [["png", "PNG"], ["jpg", "JPG"], ["webp", "WebP"]] }] },
  { id: "image-to-pdf", group: "Images", name: "Image to PDF", from: IMG, to: PDF, accept: "image/*", kind: "an image", out: "PDF", blurb: "Put an image on a PDF page." },
];
const GROUPS = [["Documents", "Convert between Word and PDF."], ["PDF", "Combine, split, shrink and rotate."], ["Images", "Resize, compress and convert."]];
const EXT = { "application/pdf": ".pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx", "image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp" };

const size = n => (n < 1024 ? n + " B" : n < 1048576 ? (n / 1024).toFixed(1) + " KB" : (n / 1048576).toFixed(1) + " MB");
const accepts = (t, f) => (t.accept === "image/*" ? f.type.startsWith("image/") : f.name.toLowerCase().endsWith(t.accept));

function useRoute() {
  const [h, setH] = useState(location.hash);
  useEffect(() => {
    const f = () => setH(location.hash);
    addEventListener("hashchange", f);
    return () => removeEventListener("hashchange", f);
  }, []);
  return h.replace(/^#\/?/, "");
}

function Fmt({ f }) { return <span className={"fmt " + f[1]}>{f[0]}</span>; }
function Flow({ t }) { return <span className="fmts"><Fmt f={t.from} /><span className="arrow" aria-hidden="true">→</span><Fmt f={t.to} /></span>; }

function Header({ route, online }) {
  const cur = k => (route === k ? "page" : undefined);
  return (
    <header className="top">
      <div className="top-in">
        <a className="brand" href="#/"><span className="mark" />DocuLab</a>
        <nav aria-label="Main">
          <a href="#/" aria-current={route === "" || route.startsWith("tool/") ? "page" : undefined}>Home</a>
          <a href="#/tools" aria-current={cur("tools")}>Tools</a>
          <a href="#/about" aria-current={cur("about")}>About</a>
          <span className="status" title={online ? "Backend is running" : "Backend not reachable"}>
            <i className={"dot " + (online === null ? "" : online ? "on" : "off")} />
            <span className="status-t">{online === null ? "Checking" : online ? "Server online" : "Server offline"}</span>
          </span>
        </nav>
      </div>
    </header>
  );
}

function Home() {
  return (
    <>
      <section className="wrap hero">
        <h1>Everything you need for documents</h1>
        <p>Convert • Edit • Compress • Organize • Transform</p>
        <a className="btn" href="#/tools">Select a tool</a>
      </section>
      <section className="wrap" id="tools">
        {GROUPS.map(([g, sub]) => (
          <div className="group" key={g}>
            <h2>{g}</h2>
            <p className="sub">{sub}</p>
            <div className="grid">
              {TOOLS.filter(t => t.group === g).map(t => (
                <a className="tool" key={t.id} href={"#/tool/" + t.id}>
                  <Flow t={t} />
                  <h3>{t.name}</h3>
                  <p>{t.blurb}</p>
                </a>
              ))}
            </div>
          </div>
        ))}
      </section>
      <section className="about" id="about">
        <div className="wrap">
          <h2>About DocuLab</h2>
          <div className="cols">
            <div><h3>Runs on your machine</h3><p>Files go to the DocuLab server on this computer, not to a third-party service.</p></div>
            <div><h3>Ten tools, one place</h3><p>Word, PDF and image tasks share the same simple flow: add a file, process it, download the result.</p></div>
            <div><h3>Know the limits</h3><p>PDF to Word quality depends on the source PDF. Scanned documents need OCR, which isn't built in yet.</p></div>
          </div>
        </div>
      </section>
    </>
  );
}

function ToolPage({ tool }) {
  const [files, setFiles] = useState([]);
  const [opts, setOpts] = useState(() => Object.fromEntries((tool.opts || []).map(o => [o.key, o.value])));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [over, setOver] = useState(false);
  const input = useRef();

  useEffect(() => () => { if (result) URL.revokeObjectURL(result.url); }, [result]);

  function add(list) {
    const picked = [...list];
    const bad = picked.find(f => !accepts(tool, f));
    if (bad) return setError(`${bad.name} isn't supported here. Choose ${tool.kind}.`);
    setError(""); setResult(null);
    setFiles(tool.multiple ? [...files, ...picked] : picked.slice(0, 1));
  }

  async function run() {
    if (files.length < (tool.multiple ? 2 : 1)) return setError(tool.multiple ? "Add at least two PDFs to merge." : "Add a file first.");
    setBusy(true); setError(""); setResult(null);
    const form = new FormData();
    files.forEach(f => form.append(tool.multiple ? "files" : "file", f));
    const qs = new URLSearchParams(opts).toString();
    try {
      const res = await fetch(`${API}/api/tools/${tool.id}${qs ? "?" + qs : ""}`, { method: "POST", body: form });
      if (!res.ok) {
        const b = await res.json().catch(() => ({}));
        throw new Error(typeof b.detail === "string" ? b.detail : "The server couldn't process this file.");
      }
      const blob = await res.blob();
      const cd = res.headers.get("content-disposition") || "";
      const header = (cd.match(/filename\*=utf-8''([^;]+)/i) || [])[1] ? decodeURIComponent(cd.match(/filename\*=utf-8''([^;]+)/i)[1]) : (cd.match(/filename="?([^";]+)"?/i) || [])[1];
      const stem = tool.multiple ? "merged" : files[0].name.replace(/\.[^.]+$/, "");
      setResult({ url: URL.createObjectURL(blob), name: header || stem + (EXT[blob.type] || ""), size: blob.size, type: blob.type });
    } catch (e) {
      setError(e instanceof TypeError ? "Can't reach the DocuLab server. Start the backend and try again." : e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <a className="back" href="#/tools">← All tools</a>
      <Flow t={tool} />
      <h1>{tool.name}</h1>
      <p className="lead">{tool.blurb}</p>

      <div className={"drop" + (over ? " over" : "")}
        onDragOver={e => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={e => { e.preventDefault(); setOver(false); add(e.dataTransfer.files); }}>
        <strong>{tool.multiple ? "Drop your PDFs here" : "Drop your file here"}</strong>
        <span>or</span>
        <button type="button" className="btn ghost" onClick={() => input.current.click()}>{tool.multiple ? "Choose files" : "Choose file"}</button>
        <input ref={input} type="file" hidden multiple={tool.multiple} accept={tool.accept}
          onChange={e => { add(e.target.files); e.target.value = ""; }} />
      </div>

      {files.length > 0 && (
        <ul className="files">
          {files.map((f, i) => (
            <li key={f.name + i}>
              <span className="nm">{f.name}</span><span className="sz">{size(f.size)}</span>
              <button type="button" className="x" aria-label={"Remove " + f.name} onClick={() => { setFiles(files.filter((_, j) => j !== i)); setResult(null); }}>×</button>
            </li>
          ))}
        </ul>
      )}

      {tool.opts && (
        <div className="opts">
          {tool.opts.map(o => (
            <label className="f" key={o.key}>
              {o.label}{o.type === "range" && ` — ${opts[o.key]}`}
              {o.type === "select"
                ? <select value={opts[o.key]} onChange={e => setOpts({ ...opts, [o.key]: e.target.value })}>{o.choices.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select>
                : <input type={o.type} min={o.min ?? 1} max={o.max} value={opts[o.key]} onChange={e => setOpts({ ...opts, [o.key]: e.target.value })} />}
            </label>
          ))}
        </div>
      )}

      {tool.note && <p className="note">{tool.note}</p>}
      <div className="act">
        <button className="btn" disabled={busy || !files.length} onClick={run}>{busy ? "Working…" : tool.multiple ? "Merge" : "Convert"}</button>
        {files.length > 0 && !busy && <button className="btn ghost" onClick={() => { setFiles([]); setResult(null); setError(""); }}>Clear</button>}
      </div>
      {busy && <div className="bar" role="progressbar" aria-label="Processing"><i /></div>}
      {error && <p className="err" role="alert">{error}</p>}

      {result ? (
        <div className="done">
          <div><strong>Your {tool.out} is ready</strong><div className="sz">{result.name} · {size(result.size)}</div></div>
          {result.type.startsWith("image/") && <img src={result.url} alt="Result preview" />}
          <a className="btn" href={result.url} download={result.name}>Download {tool.out}</a>
        </div>
      ) : (
        <div className="slot">Your {tool.out} will appear here</div>
      )}
    </div>
  );
}

function App() {
  const route = useRoute();
  const [online, setOnline] = useState(null);
  useEffect(() => { fetch(API + "/health").then(r => setOnline(r.ok)).catch(() => setOnline(false)); }, []);
  useEffect(() => {
    if (route === "tools" || route === "about") document.getElementById(route)?.scrollIntoView();
    else scrollTo(0, 0);
  }, [route]);
  const tool = route.startsWith("tool/") && TOOLS.find(t => t.id === route.slice(5));
  return (
    <>
      <Header route={route} online={online} />
      <main>{tool ? <ToolPage key={tool.id} tool={tool} /> : <Home />}</main>
      <footer className="wrap">DocuLab 1.0.0 · Local processing workspace · <a href={API + "/docs"} target="_blank" rel="noreferrer">API docs</a></footer>
    </>
  );
}

createRoot(document.getElementById("root")).render(<App />);
