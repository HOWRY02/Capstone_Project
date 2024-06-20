// Fetch available tables from backend
fetch('/tables')
    .then(response => response.json())
    .then(data => {
        const tableSelect = document.getElementById('table-select');
        data.forEach(table => {
            const option = document.createElement('option');
            option.value = table;
            option.text = table;
            tableSelect.appendChild(option);
        });
    });

// Handle table selection change
document.getElementById('table-select').addEventListener('change', function () {
    const selectedTable = this.value;
    if (selectedTable) {
        fetchTableData(selectedTable);
    } else {
        // Clear table data
        document.getElementById('data-table').getElementsByTagName('tbody')[0].innerHTML = '';
        document.getElementById('data-table').getElementsByTagName('thead')[0].innerHTML = '';
    }
});

// Function to fetch and display table data
function fetchTableData(table, searchTerm = '') {
    let url = `/tables/${table}`;
    if (searchTerm) {
        url += `/search?search_term=${searchTerm}`; // Add search query parameter
    }
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            // Update table headers and rows with retrieved data
            const tableBody = document.getElementById('data-table').getElementsByTagName('tbody')[0];
            tableBody.innerHTML = ''; // Clear existing data

            // Generate table headers dynamically based on data structure
            const tableHeader = document.getElementById('data-table').getElementsByTagName('thead')[0];
            tableHeader.innerHTML = '';

            const headerRow = document.createElement('tr');

            // Use received column names for header with checkbox
            const selectHeaderCell = document.createElement('th');
            selectHeaderCell.innerHTML = '<input type="checkbox" id="select-all">';
            headerRow.appendChild(selectHeaderCell);

            data.column_names.forEach(columnName => {
                const headerCell = document.createElement('th');
                headerCell.textContent = columnName;
                headerRow.appendChild(headerCell);
            });
            tableHeader.appendChild(headerRow);

            // Populate table rows with data and checkboxes
            data.inside_data.forEach(row => {
                const rowElement = document.createElement('tr');
                const checkboxCell = document.createElement('td');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.classList.add('row-checkbox');
                checkboxCell.appendChild(checkbox);
                rowElement.appendChild(checkboxCell);

                Object.values(row).forEach(cellValue => {
                    const cell = document.createElement('td');
                    cell.textContent = cellValue;
                    rowElement.appendChild(cell);
                });
                tableBody.appendChild(rowElement);
            });

            // Track selected rows
            let selectedRows = [];  // Array to store selected row IDs (assuming an 'id' property)

            // Function to handle row checkbox selection
            function handleRowCheckboxChange(event) {
                const rowIndex = event.target.parentElement.parentElement.rowIndex;
                const rowId = 1;
                if (event.target.checked) {
                    selectedRows.push(rowId);
                } else {
                    const index = selectedRows.indexOf(rowId);
                    selectedRows.splice(index, 1);
                }
            }

            // Add event listener to each row checkbox
            const rowCheckboxes = document.querySelectorAll('.row-checkbox');
            rowCheckboxes.forEach(checkbox => checkbox.addEventListener('change', handleRowCheckboxChange));

            // Add event listener to "Select All" checkbox
            const selectAllCheckbox = document.getElementById('select-all');
            selectAllCheckbox.addEventListener('change', function () {
                const rowCheckboxes = document.querySelectorAll('.row-checkbox');
                rowCheckboxes.forEach(checkbox => checkbox.checked = this.checked);
            });

            return { column_names: data.column_names, inside_data: data.inside_data };
        });
}

// Handle search form submission
document.getElementById('search-form').addEventListener('submit', function (event) {
    event.preventDefault();
    const selectedTable = document.getElementById('table-select').value;
    const searchTerm = document.getElementById('search-term').value;
    if (selectedTable) {
        fetchTableData(selectedTable, searchTerm)
    } else {
        alert('Please select a table before searching.');
    }
});

// Handle export data button click
document.getElementById('export-data-btn').addEventListener('click', function () {
    const selectedTable = document.getElementById('table-select').value;

    if (selectedTable) {
        fetchTableData(selectedTable)
            .then(data => {
                // Convert data to CSV format
                const csvContent = data.inside_data.map(row => Object.values(row).join(',')).join('\n');
                const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `exported_${selectedTable}.csv`;
                link.style.display = 'none';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            });
    }
});

// function scanDocument() {
//     fetch('/tables/scan', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         }
//     });
// }

// // Handle export data button click
// document.getElementById('scan-data-btn').addEventListener('click', function () {
//     scanDocument();
// });

// You can add functionalities for "Add Data" and "Scan Data" buttons here

// Example for a basic alert on clicking "Add Data" button
document.getElementById('add-data-btn').addEventListener('click', function () {
    alert('Functionality for adding data is not yet implemented.');
});

// JavaScript to handle button click and navigate to index.html
document.getElementById('homeButton').addEventListener('click', function () {
    window.location.href = '/'; // This navigates to index.html
});


