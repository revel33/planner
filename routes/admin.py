from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy import inspect
from sqlmodel import Session, select
from database.connection import database_file, engine_url, get_session
from models.events import Event
from models.participants import Participant
from models.users import User

admin_router = APIRouter(tags=["Admin"])

TABLES = {"user": User, "event": Event, "participant": Participant}

ADMIN_HTML = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Админ-панель — состояние таблиц БД</title>
<style>
  :root { --ink:#1c2430; --mut:#66788c; --line:#d8e0ea; --bg:#f4f7fb; --card:#fff;
          --acc:#2563eb; --ok:#0f9d58; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.5 "Segoe UI", system-ui, Arial, sans-serif;
         background:var(--bg); color:var(--ink); }
  header { background:#12233c; color:#fff; padding:14px 22px;
           display:flex; align-items:center; gap:14px; flex-wrap:wrap; }
  header h1 { font-size:18px; margin:0; font-weight:600; }
  header .sub { color:#9fb3cc; font-size:13px; }
  main { padding:20px 22px; max-width:1150px; margin:0 auto; }
  .cards { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:16px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:10px;
          padding:10px 16px; min-width:140px; }
  .card .k { color:var(--mut); font-size:12px; text-transform:uppercase;
             letter-spacing:.04em; }
  .card .v { font-size:16px; font-weight:600; word-break:break-all; }
  .card .v.mono { font-family:Consolas, monospace; font-size:13px; font-weight:400; }
  .bar { display:flex; align-items:center; gap:12px; margin:0 0 12px; flex-wrap:wrap; }
  button { background:var(--acc); color:#fff; border:0; border-radius:8px;
           padding:8px 16px; font-size:14px; cursor:pointer; }
  button:hover { filter:brightness(1.1); }
  label.auto { display:flex; align-items:center; gap:6px; color:var(--mut);
               font-size:14px; user-select:none; }
  .status { color:var(--mut); font-size:13px; margin-left:auto; }
  .status.ok { color:var(--ok); }
  .tabs { display:flex; gap:8px; margin:0 0 12px; flex-wrap:wrap; }
  .tab { background:#e6edf7; color:#33465c; border:1px solid var(--line);
         border-radius:999px; padding:6px 16px; font-size:14px; cursor:pointer; }
  .tab .n { background:#fff; border-radius:999px; padding:0 8px; margin-left:6px;
            font-weight:700; color:var(--acc); }
  .tab.active { background:var(--acc); color:#fff; border-color:var(--acc); }
  .tab.active .n { background:rgba(255,255,255,.2); color:#fff; }
  table { width:100%; border-collapse:collapse; background:var(--card);
          border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  th, td { padding:9px 12px; text-align:left; border-bottom:1px solid var(--line);
           vertical-align:top; font-size:14px; }
  th { background:#eef3fa; color:#33465c; font-weight:600; white-space:nowrap; }
  tr:last-child td { border-bottom:0; }
  td.pk { font-family:Consolas, monospace; color:var(--acc); font-weight:600; }
  td.fk { font-family:Consolas, monospace; color:#7c3aed; }
  td.tags code { background:#eef3fa; border-radius:4px; padding:1px 6px;
                 font-size:12px; margin-right:4px; white-space:nowrap; }
  td.desc { color:var(--mut); max-width:320px; }
  .empty { padding:26px; text-align:center; color:var(--mut); background:var(--card);
           border:1px dashed var(--line); border-radius:10px; }
  .schema { color:var(--mut); font-size:13px; margin-top:14px; }
  .schema code { font-family:Consolas, monospace; background:#eef3fa;
                 border-radius:4px; padding:1px 6px; }
</style>
</head>
<body>
<header>
  <h1>Админ-панель Planner API</h1>
</header>
<main>
  <div class="cards">
    <div class="card"><div class="k">Файл БД</div><div class="v mono" id="dbfile">—</div></div>
    <div class="card"><div class="k">Таблиц</div><div class="v" id="tnum">—</div></div>
    <div class="card"><div class="k">Всего записей</div><div class="v" id="total">—</div></div>
    <div class="card"><div class="k">Обновлено</div><div class="v mono" id="stamp">—</div></div>
  </div>

  <div class="bar">
    <button id="refresh" type="button">&#8635; Обновить</button>
    <label class="auto"><input type="checkbox" id="auto" checked> автообновление (5 c)</label>
    <span class="status" id="status"></span>
  </div>

  <div class="tabs" id="tabs"></div>
  <div id="grid"></div>
  <div class="schema" id="schema"></div>
</main>

<script>
const $ = (id) => document.getElementById(id);
let timer = null, DATA = null, CURRENT = null;
const FK = { owner_id:1, user_id:1, event_id:1 };

function esc(s){ return String(s ?? "").replace(/[&<>"]/g,
  c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }

function renderTabs(){
  $("tabs").innerHTML = DATA.tables.map(t =>
    `<button class="tab ${t.name===CURRENT?'active':''}" data-t="${t.name}">` +
    `${t.name}<span class="n">${t.count}</span></button>`).join("");
  document.querySelectorAll(".tab").forEach(b =>
    b.addEventListener("click", () => { CURRENT = b.dataset.t; renderTabs(); renderGrid(); }));
}

function cellHtml(col, v){
  if (col === "tags" && Array.isArray(v))
    return "<td class='tags'>" + v.map(t => "<code>" + esc(t) + "</code>").join("") + "</td>";
  if (col === "id") return "<td class='pk'>" + esc(v) + "</td>";
  if (FK[col]) return "<td class='fk'>" + esc(v) + "</td>";
  if (col === "description") return "<td class='desc'>" + esc(v) + "</td>";
  return "<td>" + esc(v) + "</td>";
}

function renderGrid(){
  const t = DATA.tables.find(x => x.name === CURRENT) || DATA.tables[0];
  CURRENT = t.name;
  const cols = t.columns.map(c => c.name);
  if (!t.rows.length) {
    $("grid").innerHTML = `<div class="empty">Таблица <b>${esc(t.name)}</b> пуста — записей пока нет.</div>`;
  } else {
    let html = "<table><thead><tr>" + cols.map(c => "<th>" + esc(c) + "</th>").join("") +
               "</tr></thead><tbody>";
    for (const row of t.rows)
      html += "<tr>" + cols.map(c => cellHtml(c, row[c])).join("") + "</tr>";
    $("grid").innerHTML = html + "</tbody></table>";
  }
  $("schema").innerHTML = "Схема <b>" + esc(t.name) + "</b>: " +
    t.columns.map(c => "<code>" + esc(c.name) + " " + esc(c.type) + "</code>").join(" ");
}

async function load(){
  const st = $("status");
  st.className = "status"; st.textContent = "загрузка…";
  try {
    const r = await fetch("/admin/data", {cache:"no-store"});
    if (!r.ok) throw new Error("HTTP " + r.status);
    DATA = await r.json();
    $("dbfile").textContent = DATA.db_file;
    $("tnum").textContent = DATA.tables.length;
    $("total").textContent = DATA.tables.reduce((s,t)=>s+t.count,0);
    $("stamp").textContent = DATA.server_time;
    if (!CURRENT || !DATA.tables.some(t=>t.name===CURRENT)) CURRENT = DATA.tables[0].name;
    renderTabs(); renderGrid();
    st.className = "status ok"; st.textContent = "данные прочитаны из БД ✓";
  } catch (e) {
    st.className = "status"; st.textContent = "ошибка: " + e.message;
  }
}

function setAuto(on){ if (timer){clearInterval(timer); timer=null;} if (on) timer=setInterval(load,5000); }
$("refresh").addEventListener("click", load);
$("auto").addEventListener("change", e => setAuto(e.target.checked));
setAuto(true); load();
</script>
</body>
</html>
"""

@admin_router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def admin_page() -> str:
    return ADMIN_HTML

@admin_router.get("/data")
async def admin_data(session: Session = Depends(get_session)) -> dict:
    inspector = inspect(engine_url)
    tables = []
    for name, model in TABLES.items():
        columns = [
            {"name": c["name"], "type": str(c["type"])}
            for c in inspector.get_columns(name)
        ]
        rows = session.exec(select(model)).all()  # type: ignore[arg-type]
        tables.append(
            {
                "name": name,
                "columns": columns,
                "count": len(rows),
                "rows": [r.model_dump() for r in rows],
            }
        )
    return {
        "db_file": database_file,
        "server_time": datetime.now(timezone.utc).astimezone().strftime("%H:%M:%S"),
        "tables": tables,
    }