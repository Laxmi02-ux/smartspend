// =========================================================================
// SmartSpend — Premium Frontend Engine
// Coordinates live transaction fetching and populates the UI with smooth animations
// =========================================================================

/**
 * Connects with the Flask AI Summary endpoint.
 * Animates numerical indicators and handles missing key graceful degradations.
 */
async function loadSummary() {
  const summaryText = document.getElementById("summary-text");
  const summaryStats = document.getElementById("summary-stats");
  const riskyCount = document.getElementById("risky-count");

  try {
    const res = await fetch("/api/summary");
    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
    const data = await res.json();

    // Set textual context
    summaryText.textContent = data.summary;
    summaryStats.innerHTML = `
      <span style="color: var(--accent-risk); font-weight: 600;">${data.risky_count}</span> 
      out of ${data.total_transactions} operational items flagged this audit cycle
    `;
    
    // Smooth counter animation for the main risk metric
    animateCounter(riskyCount, 0, data.risky_count, 1000);

  } catch (err) {
    summaryText.textContent = "Unable to extract real-time pipeline telemetry. Verify that your Flask app server is operational.";
    riskyCount.textContent = "ERR";
    console.error("Summary Pipeline Extraction Exception:", err);
  }
}

/**
 * Builds an explicit, high-end visual micro-visualization cell for outlier tracking.
 * Maps the standard deviation magnitude directly into a clean fluid progress bar.
 */
function buildDeviationCell(zScore, isRisky) {
  // Cap at 4 standard deviations to prevent interface line overflow
  const magnitude = Math.min(Math.abs(zScore) / 4, 1) * 100;
  
  return `
    <div class="z-cell">
      <span style="font-weight: 500;">${zScore.toFixed(2)}</span>
      <div class="z-bar-track">
        <div class="z-bar-fill ${isRisky ? "risky" : ""}" style="width: ${magnitude}%"></div>
      </div>
    </div>
  `;
}

/**
 * Pulls the live relational database rows and dynamically draws the modern ledger table
 */
async function loadTransactions() {
  const tbody = document.getElementById("transactions-body");
  const rowCount = document.getElementById("row-count");

  try {
    const res = await fetch("/api/transactions");
    if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
    const rows = await res.json();

    // Modern counter signature update
    rowCount.textContent = `${rows.length} records active`;
    tbody.innerHTML = "";

    if (rows.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 3rem;">No recent ledger data processed.</td></tr>`;
      return;
    }

    rows.forEach(row => {
      const tr = document.createElement("tr");
      if (row.is_risky) tr.classList.add("risky");

      tr.innerHTML = `
        <td style="color: var(--text-muted); font-size: 0.85rem;">${row.date}</td>
        <td style="font-weight: 500; color: #fff;">${row.department}</td>
        <td>${row.vendor}</td>
        <td class="num" style="font-weight: 600; color: ${row.is_risky ? "var(--accent-risk)" : "var(--text)"}">
          ${row.amount < 0 ? "-" : ""}$${Math.abs(row.amount).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </td>
        <td class="num">${buildDeviationCell(row.z_score, row.is_risky)}</td>
        <td>
          <span class="status-pill ${row.is_risky ? "risky" : "safe"}">
            <span style="display:inline-block; width:6px; height:6px; border-radius:50%; background:currentColor; margin-right:6px;"></span>
            ${row.is_risky ? "Anomaly Flag" : "Verified"}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--accent-risk); padding: 2rem; font-weight: 500;">Failed loading database rows. Check app.py logs.</td></tr>`;
    console.error("Ledger Core Injection Exception:", err);
  }
}

/**
 * Utility: Utility script to animate counters for an enterprise software feel
 */
function animateCounter(obj, start, end, duration) {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    obj.innerHTML = Math.floor(progress * (end - start) + start);
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}
