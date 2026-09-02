function showTreatmentImage(src) {
  document.getElementById("treatmentModalImage").src = src;
}

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("treatmentSearch");
  const clearButton = document.getElementById("clearSearch");

  const rows = document.querySelectorAll(".treatment-data-row");

  const noResult = document.getElementById("noSearchResult");

  const visibleCount = document.getElementById("visibleCount");

  function searchTreatments() {
    const keyword = searchInput.value.toLowerCase().trim();

    let count = 0;

    rows.forEach(function (row) {
      const text = row.innerText.toLowerCase();

      if (text.includes(keyword)) {
        row.style.display = "";

        count++;
      } else {
        row.style.display = "none";
      }
    });

    /* Update counter */

    visibleCount.textContent = count;

    /* Show no result */

    if (count === 0) {
      noResult.style.display = "";
    } else {
      noResult.style.display = "none";
    }
  }

  /* Search while typing */

  searchInput.addEventListener("input", searchTreatments);

  /* Clear search */

  clearButton.addEventListener("click", function () {
    searchInput.value = "";

    searchTreatments();

    searchInput.focus();
  });
});
/**
 * Export All Database Treatment Records to PDF
 */
async function exportTreatmentToPDF() {
  if (!window.jspdf || !window.html2canvas) {
    alert("Required libraries (jsPDF or html2canvas) are missing.");
    return;
  }

  const apiUrl = window.TREATMENT_API_URL || '/admin/treatments/api/treatments/all';
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

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.details || `Server returned status ${response.status}`);
    }

    records = await response.json();
  } catch (err) {
    console.error("Database fetch error:", err);
    alert(`Could not load treatment records: ${err.message}`);
    return;
  }

  if (!records || records.length === 0) {
    alert("No treatment records found in database to export.");
    return;
  }

  const headers = ["ID", "Disease", "Treatment Type", "Method Details", "Priority", "Status"];

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
      <h2 style="color: #0d6efd; font-size: 18px; margin: 0 0 5px 0; font-weight: bold;">
        របាយការណ៍ វិធីសាស្ត្រព្យាបាលជំងឺដំណាំ (Treatment Report)
      </h2>
      <p style="color: #6c757d; font-size: 11px; margin: 0;">
        Generated Date: ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()} | Total Records: ${records.length}
      </p>
    </div>
    <table style="width: 100%; border-collapse: collapse; font-size: 11px; text-align: left;">
      <thead>
        <tr style="background-color: #0d6efd; color: #ffffff;">
          ${headers.map((h, i) => `
            <th style="padding: 8px; border: 1px solid #0d6efd; ${i === 0 || i === 5 ? 'text-align: center;' : ''}">${h}</th>
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

    const pdfWidth = 277; 
    const pageHeight = 190;
    const imgHeight = (canvas.height * pdfWidth) / canvas.width;
    
    let heightLeft = imgHeight;
    let position = 10;

    const imgData = canvas.toDataURL("image/jpeg", 0.98);

    doc.addImage(imgData, "JPEG", 10, position, pdfWidth, imgHeight);
    heightLeft -= pageHeight;

    while (heightLeft > 0) {
      position = heightLeft - imgHeight + 10;
      doc.addPage();
      doc.addImage(imgData, "JPEG", 10, position, pdfWidth, imgHeight);
      heightLeft -= pageHeight;
    }

    doc.save(`Treatments_Report_Full_${new Date().toISOString().slice(0, 10)}.pdf`);
  } catch (err) {
    console.error("PDF Export Canvas Error:", err);
    alert("An error occurred while generating the PDF file.");
  } finally {
    document.body.removeChild(container);
  }
}
