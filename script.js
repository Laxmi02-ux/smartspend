// script.js
// ----------
// Talks to the Flask backend (app.py) and renders:
//   1. The AI-generated risk summary at the top
//   2. The full transaction ledger, with risky rows marked by a coral
//      accent border and an inline deviation bar showing |z-score|

async function loadSummary() {
  const summaryText = document.getElementById("summary-text");
  const summaryStats = document.getElementById("summary-stats");
  const riskyCount = document.getElementById("risky-count");

  try {
    const res = await fetch("/api/summary");
    const data = await res.json();

    riskyCount.textContent = data.risky_count;
    summaryText.textContent = data.summary;
    summaryStats.textContent =
      `${data.risky_count} / ${data.total_transactions} transactions flagged`;
  } catch (err) {
    summaryText.textContent = "Could not load AI summary. Is the Flask server running?";
    console.error(err);
  }
}

// Builds a small inline bar whose fill length represents |z-score|,
// capped visually at a z-score of 5 so extreme outliers don't overflow.
function buildDeviationCell(zScore, isRisky) {
  const magnitude = Math.min(Math.abs(zScore) / 5, 1) * 100;
  return `
    <div class="z-cell">
      <span>${zScore}</span>
      <div class="z-bar-track">
        <div class="z-bar-fill ${isRisky ? "risky" : ""}" style="width:${magnitude}%"></div>
      </div>
    </div>
  `;
}

async function loadTransactions() {
  const tbody = document.getElementById("transactions-body");
  const rowCount = document.getElementById("row-count");

  try {
    const res = await fetch("/api/transactions");
    const rows = await res.json();

    rowCount.textContent = `${rows.length} entries`;
    tbody.innerHTML = "";

    rows.forEach(row => {
      const tr = document.createElement("tr");
      if (row.is_risky) tr.classList.add("risky");

      tr.innerHTML = `
        <td>${row.date}</td>
        <td>${row.department}</td>
        <td>${row.vendor}</td>
        <td class="num">$${row.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
        <td class="num">${buildDeviationCell(row.z_score, row.is_risky)}</td>
        <td>
          <span class="status-pill ${row.is_risky ? "risky" : "safe"}">
            ${row.is_risky ? "Flagged" : "Normal"}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">Could not load transactions. Is the Flask server running?</td></tr>`;
    console.error(err);
  }
}

// Kick everything off as soon as the page loads
loadSummary();
loadTransactions();
