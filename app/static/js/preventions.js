/**
 * Prevention Module Logic & PDF Export
 * Saved as: static/js/prevention.js
 */

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const typeFilter = document.getElementById("typeFilter");
  const statusFilter = document.getElementById("statusFilter");
  const resetButton = document.getElementById("resetFilters");
  const table = document.getElementById("preventionTable") || document.querySelector(".prevention-table");
  const resultCount = document.getElementById("resultCount");
  const showingCount = document.getElementById("showingCount");
  const noSearchResult = document.getElementById("noSearchResult");
  const filterStatus = document.getElementById("filterStatus");

  // Retrieve table data rows (supports data-disease attributes or standard tbody rows)
  const rows = table ? table.querySelectorAll("tbody tr") : [];

  function filterTable() {
    if (!rows.length) return;

    const search = searchInput ? searchInput.value.toLowerCase().trim() : "";
    const type = typeFilter ? typeFilter.value.toLowerCase().trim() : "all";
    const status = statusFilter ? statusFilter.value.toLowerCase().trim() : "all";

    let visible = 0;

    rows.forEach(function (row) {
      // Ignore empty state placeholder rows
      if (row.querySelector(".empty-state") || row.cells.length <= 1) return;

      // Extract datasets or fallback to inner text content
      const disease = (row.dataset.disease || row.querySelector(".disease-name")?.textContent || "").toLowerCase();
      const rowType = (row.dataset.type || row.querySelector(".type-badge")?.textContent || "").toLowerCase();
      const method = (row.dataset.method || row.querySelector(".method-cell")?.textContent || "").toLowerCase();
      const description = (row.dataset.description || row.querySelector(".description-text")?.textContent || "").toLowerCase();
      const rowStatus = (row.dataset.status || row.querySelector(".status-badge")?.textContent || "").toLowerCase();

      const matchesSearch =
        !search ||
        disease.includes(search) ||
        rowType.includes(search) ||
        method.includes(search) ||
        description.includes(search);

      const matchesType = type === "all" || type === "" || rowType.includes(type);
      const matchesStatus = status === "all" || status === "" || rowStatus.includes(status);

      if (matchesSearch && matchesType && matchesStatus) {
        row.style.display = "";
        visible++;
      } else {
        row.style.display = "none";
      }
    });

    // Update dynamic counter elements if present
    if (resultCount) resultCount.textContent = visible;
    if (showingCount) showingCount.textContent = visible;

    // Update empty state messaging
    if (noSearchResult && filterStatus) {
      if (visible === 0) {
        noSearchResult.style.display = "";
        filterStatus.textContent = "No matching records found.";
      } else {
        noSearchResult.style.display = "none";
        filterStatus.textContent = (search || type !== "all" || status !== "all") ? "Filters applied." : "";
      }
    }
  }

  // Attach Event Listeners
  if (searchInput) searchInput.addEventListener("input", filterTable);
  if (typeFilter) typeFilter.addEventListener("change", filterTable);
  if (statusFilter) statusFilter.addEventListener("change", filterTable);

  if (resetButton) {
    resetButton.addEventListener("click", function () {
      if (searchInput) searchInput.value = "";
      if (typeFilter) typeFilter.value = "all";
      if (statusFilter) statusFilter.value = "all";
      filterTable();
    });
  }
});

/* =====================================================
   IMAGE MODAL PREVIEW
====================================================== */
function showPreventionImage(src) {
  const modalImg = document.getElementById("preventionModalImage") || document.getElementById("previewModalImage");
  const modalElement = document.getElementById("preventionImageModal") || document.getElementById("imagePreviewModal");

  if (modalImg && modalElement) {
    modalImg.src = src;
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
  } else if (src) {
    window.open(src, "_blank");
  }
}

async function exportToPDF() {
  if (!window.jspdf || !window.html2canvas) {
    alert("Required libraries (jsPDF or html2canvas) are missing.");
    return;
  }

  const apiUrl = window.PREVENTION_API_URL || '/admin/preventions/api/preventions/all';
  let records = [];

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'same-origin'
    });

    if (!response.ok) throw new Error(`Server returned status ${response.status}`);
    records = await response.json();
  } catch (err) {
    console.error("Database fetch error:", err);
    alert(`Could not load records: ${err.message}`);
    return;
  }

  if (!records || records.length === 0) {
    alert("No records found to export.");
    return;
  }

  const headers = ["ID", "Disease", "Type", "Method Details", "Priority", "Status"];

  // 1. CREATE OFF-SCREEN CONTAINER
  const container = document.createElement("div");
  container.style.position = "absolute";
  container.style.left = "-9999px";
  container.style.top = "-9999px";
  container.style.width = "1050px"; 
  container.style.padding = "20px";
  container.style.backgroundColor = "#ffffff";
  container.style.fontFamily = "'Khmer OS Siemreap', 'Hanuman', 'Battambang', sans-serif";
  container.style.color = "#212529";

  let htmlContent = `
    <div style="margin-bottom: 15px;">
      <h2 style="color: #198754; font-size: 18px; margin: 0 0 5px 0; font-weight: bold;">
        របាយការណ៍ វិធីសាស្ត្របង្ការ ជំងឺដំណាំ (Prevention Report)
      </h2>
      <p style="color: #6c757d; font-size: 11px; margin: 0;">
        Generated Date: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()} | Total Records: ${records.length}
      </p>
    </div>
    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">
      <thead>
        <tr style="background-color: #198754; color: #ffffff;">
          ${headers.map((h, i) => `
            <th style="padding: 8px; border: 1px solid #198754; ${i === 0 || i === 5 ? 'text-align: center;' : ''}">${h}</th>
          `).join("")}
        </tr>
      </thead>
      <tbody>
  `;

  records.forEach((row, index) => {
    let methodDetails = row.method || "";
    if (row.description) {
      methodDetails += `<br><span style="color: #495057; font-size: 10px;">${row.description}</span>`;
    }
    const bgStyle = index % 2 === 0 ? "background-color: #ffffff;" : "background-color: #f8f9fa;";

    htmlContent += `
      <tr style="${bgStyle} border-bottom: 1px solid #dee2e6;">
        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center; width: 6%; font-weight: bold;">${row.id}</td>
        <td style="padding: 8px; border: 1px solid #dee2e6; width: 20%;">${row.disease}</td>
        <td style="padding: 8px; border: 1px solid #dee2e6; width: 14%;">${row.type}</td>
        <td style="padding: 8px; border: 1px solid #dee2e6; width: 42%;">${methodDetails}</td>
        <td style="padding: 8px; border: 1px solid #dee2e6; width: 10%;">${row.priority}</td>
        <td style="padding: 8px; border: 1px solid #dee2e6; text-align: center; width: 8%;">${row.status}</td>
      </tr>
    `;
  });

  htmlContent += `</tbody></table>`;
  container.innerHTML = htmlContent;
  document.body.appendChild(container);

  // 2. MULTI-PAGE CANVAS RENDERING
  try {
    const canvas = await html2canvas(container, {
      scale: 2,
      useCORS: true,
      logging: false
    });

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF("landscape", "mm", "a4");

    const pdfWidth = 277; // A4 width minus margins (297mm - 20mm)
    const pageHeight = 190; // Available A4 height minus margins (210mm - 20mm)
    const imgHeight = (canvas.height * pdfWidth) / canvas.width;
    
    let heightLeft = imgHeight;
    let position = 10;

    const imgData = canvas.toDataURL("image/jpeg", 0.98);

    // Add First Page
    doc.addImage(imgData, "JPEG", 10, position, pdfWidth, imgHeight);
    heightLeft -= pageHeight;

    // Loop through remaining height to create Page 2, Page 3, etc.
    while (heightLeft > 0) {
      position = heightLeft - imgHeight + 10; // Shift vertical position up
      doc.addPage();
      doc.addImage(imgData, "JPEG", 10, position, pdfWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    doc.save(`Preventions_Report_Full_${new Date().toISOString().slice(0, 10)}.pdf`);
  } catch (err) {
    console.error("PDF Export Canvas Error:", err);
    alert("An error occurred while generating the PDF file.");
  } finally {
    document.body.removeChild(container);
  }
}