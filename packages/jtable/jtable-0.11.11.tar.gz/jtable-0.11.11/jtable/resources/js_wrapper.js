// var tables = document.getElementsByTagName('table');
const tables = document.querySelectorAll("table");
const pageTitle = $('title').text();
console.log(pageTitle);
const top_search_box = `
<header>
  <label>${pageTitle}</label>
  <input type="text" id="top-search-container" onkeyup="filterAllTables()" placeholder="Filter on all tables">
</header>
`;

// top_search_box = "<header><label>$('title').text()</label><input type='text' id='top-search-container' onkeyup='filterAllTables()' placeholder='filter on all tables'></header>"

let selectedTable = null; // Variable pour stocker la table sélectionnée
add_toc()
add_div_to_tables()

// Écouteur pour détecter le clic sur une table
tables.forEach(table => {
  table.addEventListener("click", function () {
    selectedTable = table; // Met à jour la table actuellement sélectionnée
  });
});

// Écouteur d'événement pour intercepter Ctrl + A
document.addEventListener("keydown", function (event) {
  if (event.ctrlKey && event.key === "a" && selectedTable) {
    event.preventDefault(); // Empêche la sélection de toute la page

    // Création d'une sélection pour la table sélectionnée en excluant le header
    const selection = window.getSelection();
    selection.removeAllRanges(); // Vidage de la sélection actuelle

    const range = document.createRange();

    // Vérifie s'il y a au moins une ligne dans le tbody
    if (selectedTable.tBodies[0]?.rows.length > 1) {
      // Sélection de toutes les lignes sauf la première
      range.setStartBefore(selectedTable.tHead.rows[1]);
      range.setEndAfter(selectedTable.tBodies[0].rows[selectedTable.tBodies[0].rows.length - 1]);

      selection.addRange(range); // Ajout de la sélection du contenu de la table sélectionnée
    }
  }
});

$(top_search_box).prependTo("body");
// console.log(top_search_box);
let table_id = 0;
for (const table of tables) {
  let prepa_search_boxes = "<tr>\n";
  let column_id = 0;
  table.id = table_id;

  for (const cell of table.tHead.rows.item(0).cells) {
    cell.onclick = (function (table_id, column_id) {
      return function () {
        sortTable(table_id, column_id);
      };
    })(table_id, column_id);
    prepa_search_boxes = prepa_search_boxes + "<th><input type='text' class='search-container' onkeyup='filterTable(" +
      table_id + "," + column_id + ")' placeholder='filter by " + cell.innerText + "'></th>\n";
    column_id++;
  }
  prepa_search_boxes = prepa_search_boxes + "</tr>";
  $(table.tHead).prepend(prepa_search_boxes);
  table_id++;

}


update_row_count = function (table_id = null) {
  console.log("update_row_count called with table_id: " + table_id);
  let totalVisibleRows = 0;
  for (const table of tables) {
    const tbody = table.tBodies[0];
    if (tbody) {
      const visibleRows = Array.from(tbody.rows).filter(row => row.style.display !== "none");
      totalVisibleRows += visibleRows.length;
      // Update the row count div for this table
      const container = table.parentNode;
      if (container && container.classList.contains("table-container")) {
        const rowCountDiv = container.querySelector(".table-row-count");
        if (rowCountDiv) {
          rowCountDiv.textContent = `Row Count: ${visibleRows.length}`;
        }
      }
    }
  }
  // Optionally update a global row count element if it exists
  const rowCountElement = document.getElementById('row-count');
  if (rowCountElement) {
    rowCountElement.textContent = `Rows: ${totalVisibleRows}`;
  }
};

function add_div_to_tables() {
  for (const table of tables) {
    // Create a div to hold the row count
    const rowCountDiv = document.createElement("div");
    rowCountDiv.className = "table-row-count";
    rowCountDiv.textContent = `Rows: ${table.tBodies[0].rows.length}`;
    // // Append the div to the table container
    const tableContainer = document.createElement("div");
    tableContainer.className = "table-container";
    tableContainer.appendChild(rowCountDiv);
    table.parentNode.insertBefore(tableContainer, table);
    tableContainer.appendChild(table);
  }
} 

function filterAllTables() {
  var search_input = $("#top-search-container").val().toUpperCase();
  tableId = 0;
  for (const table of tables) {
    filterTable(tableId);
    tableId++;
  }
}

function filterTable(table_id, column = 0) {
  // filterAllTables()
  var top_search_input = $("#top-search-container").val().toUpperCase();

  var table = document.getElementById(table_id);
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);

  rows.forEach(function (row) {
    var cellText = row.textContent.toUpperCase();
    if (cellText.indexOf(top_search_input) > -1) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });

  let columnId = 0;
  for (const column of table.rows[0].cells) {
    input = column.querySelector("input").value;
    filterColumn(table_id, columnId);
    columnId++;
  }
  update_row_count(table_id);

}


function filterColumn(table_id, column) {
  var table = document.getElementById(table_id);
  // var input = table.rows[0].cells[column].querySelector("input");
  var input = table.rows[0].cells[column].querySelector("input");
  var filterText = input.value.toUpperCase();
  var rows = Array.prototype.slice.call(table.tBodies[0].rows).filter(row => row.style.display !== "none");
  rows.forEach(function (row) {
    var cellText = row.cells[column].textContent.toUpperCase();
    if (cellText.indexOf(filterText) > -1) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}



function sortTable(table_id, column) {
  var table = document.getElementById(table_id);
  var rows = Array.prototype.slice.call(table.tBodies[0].rows);
  var isAscending = table.tHead.rows[0].cells[column].classList.toggle("ascending");
  var multiplier = isAscending ? 1 : -1;
  rows.sort(function (a, b) {
    var aVal = a.cells[column].textContent;
    var bVal = b.cells[column].textContent;
    if (!isNaN(aVal) && !isNaN(bVal)) {
      aVal = Number(aVal);
      bVal = Number(bVal);
      return multiplier * (aVal - bVal);
    } else {
      return multiplier * aVal.localeCompare(bVal);
    }
  });
  table.tBodies[0].innerHTML = "";
  rows.forEach(function (row) {
    table.tBodies[0].appendChild(row);
  });
}

function add_toc() {

  document.addEventListener("DOMContentLoaded", () => {
    const tocContainer = document.getElementById("toc");
    const headers = document.querySelectorAll("h1, h2, h3, h4, h5, h6");

    if (!tocContainer || headers.length === 0) return;

    const tocList = document.createElement("ul");

    headers.forEach(header => {
        const level = parseInt(header.tagName.substring(1), 10); // e.g., 1 for <h1>, 2 for <h2>
        const listItem = document.createElement("li");
        listItem.style.marginLeft = `${(level - 1) * 15}px`; // Indentation based on header level
        
        const anchor = document.createElement("a");
        const headerID = header.id || header.textContent.trim().replace(/\s+/g, "-").toLowerCase();
        header.id = headerID; // Assign an ID if it doesn't exist
        
        anchor.href = `#${headerID}`;
        anchor.textContent = header.textContent;

        listItem.appendChild(anchor);
        tocList.appendChild(listItem);
    });

    tocContainer.appendChild(tocList);
});
}



const button = document.getElementById('scrollTopButton');

// Afficher ou masquer le bouton en fonction du défilement
window.onscroll = function() {
  const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
  const scrollHeight = document.documentElement.scrollHeight;
  const clientHeight = document.documentElement.clientHeight;

  // Vérifie si l'utilisateur est au bas de la page
  if (scrollTop + clientHeight >= scrollHeight - 10) {
    button.style.display = "none";
  } else if (scrollTop > 200) {
    button.style.display = "block";
  } else {
    button.style.display = "none";
  }
};

// Fonction pour revenir en haut de la page
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
}

