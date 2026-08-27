(function () {
  var root = document.getElementById("potn");
  if (!root) return;

  var issue = root.getAttribute("data-potn-issue");
  if (!issue) return;

  var form = document.getElementById("potn-form");
  var results = document.getElementById("potn-results");
  if (!form || !results) return;

  var storageKey = "scorebook-potn-" + issue;
  var apiBase = root.getAttribute("data-potn-api") || "/api/potn/";

  function labelsFromForm() {
    var map = {};
    var order = [];
    var inputs = form.querySelectorAll('input[type="radio"][name="play"]');
    inputs.forEach(function (input) {
      var value = input.value;
      if (!value) return;
      order.push(value);
      var label = input.closest("label");
      map[value] = label ? label.textContent.trim() : value;
    });
    return { order: order, labels: map };
  }

  function pct(count, total) {
    if (!total) return 0;
    return Math.round((count / total) * 100);
  }

  function paint(counts, mine, meta) {
    var parsed = labelsFromForm();
    var order = parsed.order;
    var labels = parsed.labels;
    var total = 0;

    order.forEach(function (key) {
      total += counts[key] || 0;
    });

    results.hidden = false;
    results.innerHTML = order
      .map(function (key) {
        var count = counts[key] || 0;
        var picked = mine === key;
        var you = picked ? " · your vote" : "";
        var share = pct(count, total);
        return (
          '<div class="bar-row"><div><div>' +
          labels[key] +
          you +
          '</div><div class="bar"><span style="width:' +
          share +
          '%"></span></div></div><div>' +
          count +
          "</div></div>"
        );
      })
      .join("");

    if (meta && meta.voted) {
      results.innerHTML +=
        '<p class="subn" style="margin-top:8px">Thanks for voting.</p>';
    } else if (total > 0) {
      results.innerHTML +=
        '<p class="subn" style="margin-top:8px">' +
        total +
        " vote" +
        (total === 1 ? "" : "s") +
        " so far.</p>";
    }
  }

  function fetchTotals() {
    return fetch(apiBase + encodeURIComponent(issue), {
      method: "GET",
      headers: { Accept: "application/json" },
    }).then(function (res) {
      if (!res.ok) throw new Error("potn_fetch_failed");
      return res.json();
    });
  }

  function submitVote(choice) {
    return fetch(apiBase + encodeURIComponent(issue), {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ choice: choice }),
    }).then(function (res) {
      return res.json().then(function (body) {
        if (!res.ok) {
          var err = new Error(body && body.error ? body.error : "potn_vote_failed");
          err.status = res.status;
          err.body = body;
          throw err;
        }
        return body;
      });
    });
  }

  function showError(message) {
    results.hidden = false;
    results.innerHTML =
      '<p class="subn" style="margin-top:8px;color:#8b2942">' +
      message +
      "</p>";
  }

  function sumCounts(counts) {
    var total = 0;
    var parsed = labelsFromForm();
    parsed.order.forEach(function (key) {
      total += counts[key] || 0;
    });
    return total;
  }

  function refresh(mine, voted) {
    return fetchTotals()
      .then(function (data) {
        var counts = data.counts || {};
        if (!voted && !mine && sumCounts(counts) === 0) {
          results.hidden = true;
          results.innerHTML = "";
          return;
        }
        paint(counts, mine || null, { voted: !!voted });
      })
      .catch(function () {
        showError("Could not load vote totals. Try again in a moment.");
      });
  }

  var prior = localStorage.getItem(storageKey);
  if (prior) {
    form.hidden = true;
    refresh(prior, true);
  } else {
    refresh(null, false);
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    var choice = new FormData(form).get("play");
    var parsed = labelsFromForm();
    if (!choice || !parsed.labels[choice]) return;

    if (localStorage.getItem(storageKey)) {
      form.hidden = true;
      refresh(localStorage.getItem(storageKey), true);
      return;
    }

    var button = form.querySelector('button[type="submit"]');
    if (button) button.disabled = true;

    submitVote(String(choice))
      .then(function (data) {
        localStorage.setItem(storageKey, String(choice));
        form.hidden = true;
        paint(data.counts || {}, String(choice), { voted: true });
      })
      .catch(function (err) {
        if (button) button.disabled = false;
        if (err && err.status === 429) {
          showError("Too many votes from this connection. Try again later.");
          return;
        }
        showError("Vote did not go through. Try again in a moment.");
      });
  });
})();
