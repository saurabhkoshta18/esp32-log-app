document.getElementById("logout").addEventListener("click", function () {
    document.cookie = "user=; max-age=0; path=/";
    window.location.href = "/";
});

function refreshLogs() {
    fetch("/refresh")
        .then(response => response.json())
        .then(data => {
            let logTable = document.getElementById("log-table");
            logTable.innerHTML = "";
            data.logs.forEach(log => {
                let row = document.createElement("tr");
                row.innerHTML = `<td>${log.UID}</td><td>${log.Action}</td><td>${log.Date}</td><td>${log.Time}</td>`;
                logTable.appendChild(row);
            });
        });
}

setInterval(refreshLogs, 5000);
