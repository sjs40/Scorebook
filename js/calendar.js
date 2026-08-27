(function () {
  var MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  var DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  var year = 2026;
  var month = 7;
  var issues = [];
  var issueMap = {};

  var monthEl = document.getElementById("cal-month");
  var gridEl = document.getElementById("cal-grid");
  var prevBtn = document.getElementById("cal-prev");
  var nextBtn = document.getElementById("cal-next");
  var latestEl = document.getElementById("latest-issue");

  function pad(n) {
    return n < 10 ? "0" + n : String(n);
  }

  function dateKey(y, m, d) {
    return y + "-" + pad(m + 1) + "-" + pad(d);
  }

  function renderCalendar() {
    monthEl.textContent = MONTHS[month] + " " + year;
    gridEl.innerHTML = "";

    DOW.forEach(function (label) {
      var h = document.createElement("div");
      h.className = "cal-dow";
      h.textContent = label;
      gridEl.appendChild(h);
    });

    var first = new Date(year, month, 1).getDay();
    var daysInMonth = new Date(year, month + 1, 0).getDate();

    for (var i = 0; i < first; i++) {
      var padCell = document.createElement("div");
      padCell.className = "cal-cell pad";
      gridEl.appendChild(padCell);
    }

    for (var day = 1; day <= daysInMonth; day++) {
      var key = dateKey(year, month, day);
      var cell = document.createElement("div");
      cell.className = "cal-cell";

      if (issueMap[key]) {
        var link = document.createElement("a");
        link.href = "/" + key + "/";
        link.textContent = day;
        link.title = issueMap[key].title;
        cell.appendChild(link);
      } else {
        var span = document.createElement("span");
        span.className = "day-num";
        span.textContent = day;
        cell.appendChild(span);
      }

      gridEl.appendChild(cell);
    }

    var total = first + daysInMonth;
    var trailing = total % 7 === 0 ? 0 : 7 - (total % 7);
    for (var j = 0; j < trailing; j++) {
      var trail = document.createElement("div");
      trail.className = "cal-cell pad";
      gridEl.appendChild(trail);
    }
  }

  function composeDek(issue) {
    var dek = issue.dek || "";
    if (issue.playOfTheNight) {
      var clause = "Play of the night: " + issue.playOfTheNight + ".";
      if (!dek) return clause;
      return clause + " " + dek;
    }
    return dek;
  }

  function renderLatest() {
    if (!latestEl || !issues.length) return;

    var sorted = issues.slice().sort(function (a, b) {
      return b.date.localeCompare(a.date);
    });
    var latest = sorted[0];

    latestEl.innerHTML =
      '<p class="latest-label">Latest issue</p>' +
      '<a href="/' + latest.date + '/">' +
      '<h3>' + latest.title + '</h3>' +
      '<p>' + composeDek(latest) + '</p>' +
      '</a>';
  }

  function loadIssues() {
    fetch("/issues.json")
      .then(function (res) {
        if (!res.ok) throw new Error("issues.json unavailable");
        return res.json();
      })
      .then(function (data) {
        issues = data;
        issueMap = {};
        issues.forEach(function (issue) {
          issueMap[issue.date] = issue;
        });
        renderLatest();
        renderCalendar();
      })
      .catch(function () {
        if (latestEl) {
          latestEl.innerHTML = '<p class="latest-label">Latest issue</p><p>Couldn\u2019t load issues.</p>';
        }
      });
  }

  prevBtn.addEventListener("click", function () {
    month -= 1;
    if (month < 0) {
      month = 11;
      year -= 1;
    }
    renderCalendar();
  });

  nextBtn.addEventListener("click", function () {
    month += 1;
    if (month > 11) {
      month = 0;
      year += 1;
    }
    renderCalendar();
  });

  loadIssues();
})();
