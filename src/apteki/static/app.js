"use strict";

const $ = (id) => document.getElementById(id);
const PAGE = 20;
const DAYS = ["pn", "wt", "sr", "cz", "pt", "sb", "nh", "nn"];
let dayLabels = {};
let offset = 0;
let controller = null;

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const fmtInt = (n) => new Intl.NumberFormat("pl-PL").format(n);

async function getJSON(url, signal) {
  const r = await fetch(url, { signal });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

function params() {
  const p = new URLSearchParams();
  const q = $("q").value.trim();
  if (q) p.set("q", q);
  if ($("wojewodztwo").value) p.set("wojewodztwo", $("wojewodztwo").value);
  const kiedy = $("kiedy").value;
  if (kiedy) p.set("kiedy", kiedy);
  if (kiedy && kiedy !== "teraz" && $("godzina").value) p.set("godzina", $("godzina").value);
  if ($("calodobowa").checked) p.set("calodobowa", "true");
  if ($("wysylkowa").checked) p.set("wysylkowa", "true");
  return p;
}

function card(a, today, isNowFilter) {
  const hoursToday = a[`h_${today}`];
  const badge = isNowFilter
    ? `<span class="badge open">otwarta teraz</span>`
    : hoursToday
      ? `<span class="badge open">dziś ${esc(hoursToday)}</span>`
      : `<span class="badge closed">dziś zamknięta</span>`;
  const place = `${a.adres}, ${a.kod_pocztowy} ${a.miejscowosc}`;
  const maps = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${a.nazwa}, ${place}`)}`;
  const rows = DAYS.filter((d) => d !== "nh")
    .map((d) => `<tr><td>${esc(dayLabels[d] || d)}</td><td>${esc(a[`h_${d}`] || "brak danych / zamknięte")}</td></tr>`)
    .join("");
  const www = a.www ? `<a href="${esc(a.www.startsWith("http") ? a.www : "https://" + a.www)}" rel="noopener nofollow">strona www</a>` : "";
  return `<li class="card">
    <div class="card-head"><h3>${esc(a.nazwa)}</h3>${badge}</div>
    <p class="addr">${esc(place)} · <span class="capitalize">pow. ${esc(a.powiat)}</span>${a.calodobowa ? " · <b>całodobowa</b>" : ""}</p>
    <div class="actions">
      ${a.telefon ? `<a href="tel:${esc(a.telefon.split(/[;,]/)[0].replace(/[^\d+]/g, ""))}">☎ ${esc(a.telefon)}</a>` : ""}
      <a href="${maps}" rel="noopener">Pokaż na mapie</a>
      ${www}
    </div>
    <details><summary>Godziny otwarcia</summary><table>${rows}</table></details>
  </li>`;
}

async function search(append = false) {
  if (!append) offset = 0;
  if (controller) controller.abort();
  controller = new AbortController();
  const p = params();
  p.set("limit", PAGE);
  p.set("offset", offset);
  const t0 = performance.now();
  try {
    const data = await getJSON(`/api/search?${p}`, controller.signal);
    const ms = Math.round(performance.now() - t0);
    const html = data.items.map((a) => card(a, data.dzisiaj, $("kiedy").value === "teraz")).join("");
    $("results").innerHTML = append ? $("results").innerHTML + html : html;
    offset += data.items.length;
    $("summary").textContent = data.total
      ? `Znaleziono ${fmtInt(data.total)} aptek (pokazano ${fmtInt(offset)}) · ${ms} ms`
      : "Brak aptek spełniających kryteria. Spróbuj wybrać „dowolnie” albo poszerzyć obszar.";
    $("more").hidden = offset >= data.total;
  } catch (e) {
    if (e.name !== "AbortError") $("summary").textContent = "Błąd pobierania danych: " + e.message;
  }
}

let timer;
function debounced() {
  clearTimeout(timer);
  timer = setTimeout(() => search(), 250);
}

async function loadStats() {
  const s = await getJSON("/api/stats");
  const pl = s.polska;
  $("kpi").innerHTML = [
    [pl.apteki, "aktywnych aptek i punktów aptecznych"],
    [pl.calodobowe, "całodobowych (pn–sb)"],
    [pl.po_20, "otwartych w poniedziałek po 20:00"],
    [pl.niedziela, "z podanymi godzinami w niedzielę"],
    [s.powiaty_bez_calodobowej.length, `powiatów (z ${pl.powiaty}) bez apteki całodobowej`],
  ].map(([n, l]) => `<div><b>${fmtInt(n)}</b><span>${l}</span></div>`).join("");
  const head = `<tr><th>%NAME%</th><th class="num">Apteki</th><th class="num">Całodobowe</th><th class="num">Po 20:00</th><th class="num">Niedziela</th></tr>`;
  const row = (name, r) => `<tr><td class="capitalize">${esc(name)}</td><td class="num">${fmtInt(r.apteki)}</td><td class="num">${fmtInt(r.calodobowe)}</td><td class="num">${fmtInt(r.po_20)}</td><td class="num">${fmtInt(r.niedziela)}</td></tr>`;
  $("woj").innerHTML = head.replace("%NAME%", "Województwo") + s.wojewodztwa.map((r) => row(r.wojewodztwo, r)).join("");
  $("plamy").innerHTML = head.replace("%NAME%", "Powiat (województwo)") +
    s.powiaty_bez_calodobowej.slice(0, 50).map((r) => row(`${r.powiat} (${r.wojewodztwo})`, r)).join("");
}

async function init() {
  const meta = await getJSON("/api/meta");
  dayLabels = meta.dni;
  for (const w of meta.wojewodztwa) $("wojewodztwo").add(new Option(w, w));
  for (const d of DAYS.filter((d) => d !== "nh")) $("kiedy").add(new Option(`${dayLabels[d].toLowerCase()} o godzinie…`, d));
  if (meta.zrodlo?.data_date) $("data-date").textContent = `(stan na ${meta.zrodlo.data_date})`;

  $("form").addEventListener("input", (e) => {
    if (e.target.id === "kiedy") $("godzina-wrap").hidden = ["", "teraz"].includes($("kiedy").value);
    debounced();
  });
  $("form").addEventListener("submit", (e) => { e.preventDefault(); search(); });
  $("more").addEventListener("click", () => search(true));

  let statsLoaded = false;
  for (const btn of document.querySelectorAll(".tab")) {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === btn));
      document.querySelectorAll(".panel").forEach((p) => (p.hidden = p.id !== btn.dataset.tab));
      if (btn.dataset.tab === "statystyki" && !statsLoaded) {
        statsLoaded = true;
        loadStats().catch((e) => ($("kpi").textContent = "Błąd: " + e.message));
      }
    });
  }
  search();
}

init().catch((e) => ($("summary").textContent = "Nie udało się załadować aplikacji: " + e.message));
