console.log("script.js loaded ✅");

let GLOBAL_POSTS = [];

/* ======================================================
   LOAD POSTS (SINGLE + MIX_ALL HANDLING)
====================================================== */
async function loadPosts() {
  const sub = document.getElementById("subreddit").value;
  const target = document.getElementById("posts");
  target.innerHTML = "Loading…";

  try {
    let r;

    // ✅ If user selects MIX_ALL → fetch mixed feed automatically
    if (sub === "MIX_ALL") {
      r = await fetch(`/api/mixed-default`);
    } 
    else {
      r = await fetch(`/api/posts/${encodeURIComponent(sub)}`);
    }

    const posts = await r.json();
    GLOBAL_POSTS = posts;

    target.innerHTML = posts
      .map(
        (p, i) => `
        <div class="card">
          <strong>${p.subreddit || sub}</strong>
          <h3>${p.title}</h3>
          <p>${(p.text || "").slice(0, 300)}...</p>
          <button onclick="analyze(${i})">Analyze</button>
        </div>`
      )
      .join("");

  } catch (err) {
    console.error(err);
    target.innerHTML = "Failed to load posts.";
  }
}

/* ======================================================
   ANALYZE A POST
====================================================== */
async function analyze(index) {
  const post = GLOBAL_POSTS[index];
  const resEl = document.getElementById("results");
  const docEl = document.getElementById("doctors");

  resEl.textContent = "Analyzing...";
  docEl.innerHTML = "";

  try {
    // --- Send post to backend ---
    const r = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: `${post.title} ${post.text}` }),
    });

    const data = await r.json();

    // --- Display analysis ---
    resEl.textContent =
      `Factual: ${data.is_factual}\n` +
      `Prediction: ${data.prediction.label}\n` +
      `Confidence: ${data.prediction.confidence}\n` +
      `Sentiment: ${JSON.stringify(data.sentiment)}`;

    // If factual → skip doctor lookup
    let disorder = data.is_factual ? "" : data.prediction.label;

    const dr = await fetch(
      `/api/doctors?label=${encodeURIComponent(disorder)}&city=Delhi`
    );
    const doctors = await dr.json();

    docEl.innerHTML = doctors.length
      ? doctors
          .map(
            (d) => `
        <div class="card">
          <strong>${d.name}</strong><br>
          Specialty: ${d.specialty}<br>
          Address: ${d.address}<br>
          Phone: ${d.phone}<br>
        </div>`
          )
          .join("")
      : "No doctors found.";

  } catch (err) {
    console.error(err);
    resEl.textContent = "Analysis failed.";
  }
}

/* ======================================================
   EVENT LISTENERS
====================================================== */
document.getElementById("load").addEventListener("click", loadPosts);
