import os
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

ALLOWED_ORIGIN = os.environ.get("CORS_ALLOWED_ORIGIN", "*")

GAME_HTML = """
<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8" />
  <title>Bombadan Kurtul</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: radial-gradient(circle at top, #1f2937, #020617);
      color: #f9fafb;
    }

    .container {
      text-align: center;
      padding: 2rem 3rem;
      border-radius: 1.5rem;
      background: rgba(15, 23, 42, 0.9);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
      max-width: 520px;
      width: 100%;
    }

    h1 {
      font-size: 2rem;
      margin-bottom: 0.75rem;
    }

    .status {
      min-height: 1.8rem;
      margin-bottom: 1rem;
      font-weight: 650;
      font-size: 1.05rem;
    }

    .status.success {
      color: #22c55e;
    }

    .status.error {
      color: #f97316;
    }

    .buttons-wrapper {
      display: flex;
      justify-content: center;
      gap: 1.5rem;
      margin: 0.5rem 0 1rem 0;
    }

    .circle-btn {
      width: 180px;
      height: 180px;
      border-radius: 999px;
      border: none;
      cursor: pointer;
      font-size: 3rem;  /* şekiller büyük gözüksün */
      font-weight: 600;
      background: #0f172a;
      color: #e5e7eb;
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
      transition:
        transform 0.15s ease,
        box-shadow 0.15s ease,
        background 0.15s ease,
        opacity 0.15s ease;
    }

    .circle-btn:hover {
      transform: translateY(-4px);
      box-shadow: 0 14px 24px rgba(0, 0, 0, 0.6);
    }

    .circle-btn:active {
      transform: translateY(0);
      box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }

    .circle-btn.correct {
      background: #16a34a;
    }

    .circle-btn.wrong {
      background: #b91c1c;
    }

    .reset-info {
      font-size: 0.85rem;
      opacity: 0.75;
      margin-bottom: 0.5rem;
      margin-top: 0.5rem;
    }

    .scoreboard {
      font-size: 0.9rem;
      margin-top: 0.25rem;
      padding-top: 0.5rem;
      border-top: 1px solid rgba(148, 163, 184, 0.3);
      opacity: 0.9;
    }

    .scoreboard span {
      display: inline-block;
      margin: 0 0.35rem;
    }

    .score-label {
      opacity: 0.8;
    }

    .score-value {
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Bombadan Kurtul</h1>

    <!-- Mesaj artık butonların ÜSTÜNDE -->
    <div id="status" class="status"></div>

    <div class="buttons-wrapper">
      <!-- Kare, Yuvarlak, Üçgen artık şekil olarak -->
      <button class="circle-btn" data-index="0" aria-label="Kare">&#9632;</button>
      <button class="circle-btn" data-index="1" aria-label="Yuvarlak">&#9679;</button>
      <button class="circle-btn" data-index="2" aria-label="Üçgen">&#9650;</button>
    </div>

    <div class="reset-info">
      Her seçimden sonra oyun otomatik olarak yeniden karışır 🔄
    </div>

    <div id="scoreboard" class="scoreboard">
      <span class="score-label">Toplam Deneme:</span>
      <span id="score-attempts" class="score-value">0</span> |
      <span class="score-label">Kurtulduğun Seçimler:</span>
      <span id="score-correct" class="score-value">0</span> |
      <span class="score-label">Başarı Oranı:</span>
      <span id="score-rate" class="score-value">0%</span>
    </div>
  </div>

  <script>
    const buttons = document.querySelectorAll(".circle-btn");
    const statusEl = document.getElementById("status");

    const attemptsEl = document.getElementById("score-attempts");
    const correctEl = document.getElementById("score-correct");
    const rateEl = document.getElementById("score-rate");

    let bombIndex = null;      // Bomba olan buton
    let attempts = 0;
    let correctCount = 0;      // Kurtulduğun seçimler

    function updateScoreboard() {
      attemptsEl.textContent = attempts;
      correctEl.textContent = correctCount;
      const rate = attempts === 0 ? 0 : Math.round((correctCount / attempts) * 100);
      rateEl.textContent = rate + "%";
    }

    function randomizeBomb() {
      bombIndex = Math.floor(Math.random() * 3);

      buttons.forEach((btn) => {
        btn.classList.remove("correct", "wrong");
        btn.disabled = false;
        btn.style.opacity = "1";
      });

      statusEl.textContent = "";
      statusEl.className = "status";
    }

    function handleClick(event) {
      const clickedBtn = event.currentTarget;
      const clickedIndex = Number(clickedBtn.dataset.index);

      attempts += 1;

      buttons.forEach((btn) => {
        btn.disabled = true;
        btn.style.opacity = "0.75";
      });

      if (clickedIndex === bombIndex) {
        // BOMBA: kaybettin
        clickedBtn.classList.add("wrong");
        statusEl.textContent = "BOMBA 💣 | Tekrar dene!";
        statusEl.classList.add("error");
      } else {
        // Kurtuldun: başarılı seçim
        correctCount += 1;
        clickedBtn.classList.add("correct");
        statusEl.textContent = "KURTULDUN 🎉 | İyi seçim!";
        statusEl.classList.add("success");
      }

      updateScoreboard();

      setTimeout(() => {
        randomizeBomb();
      }, 700);
    }

    buttons.forEach((btn) => {
      btn.addEventListener("click", handleClick);
    });

    updateScoreboard();
    randomizeBomb();
  </script>
</body>
</html>
"""

# --- CORS MIDDLEWARE ---
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

# --- API ENDPOINTLERİ ---

@app.route("/api")
def api():
    return jsonify(status="Hello")


@app.route("/api/saglik")
def saglik():
    return jsonify(status="OK")


@app.route("/api/health", methods=["GET", "OPTIONS"])
def health():
    # Preflight isteği (OPTIONS) için boş 204 dön
    if request.method == "OPTIONS":
        return ("", 204)
    return jsonify(status="ok")


@app.route("/alperen/a")
def alperen():
    return jsonify(status="success")


@app.route("/alperen/b")
def alperen2():
    return jsonify(status="b")


@app.route("/yusuf/y")
def yusuf():
    return jsonify(status="full")


@app.route("/yusuf/f")
def yusuf2():
    return jsonify(status="f")


@app.route("/api/games", methods=["GET", "OPTIONS"])
def game():
    # Preflight isteği (OPTIONS)
    if request.method == "OPTIONS":
        return ("", 204)

    # HTML dönen endpoint (oyun sayfası)
    resp = make_response(GAME_HTML)
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
