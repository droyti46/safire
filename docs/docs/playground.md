<script src="https://cdn.jsdelivr.net/pyodide/v0.24.0/full/pyodide.js"></script>
<script>
let pyodideReady = false;
let pyodide;

async function loadPyodideAndPackages() {
    pyodide = await loadPyodide();
    pyodideReady = true;
    console.log("Pyodide ready!");
}

loadPyodideAndPackages();
</script>

<textarea id="prompt" rows="4" cols="50" placeholder="Введите текст"></textarea><br>
<input type="number" id="n" value="1" min="1" style="width:50px;">
<button onclick="runPlayground()">Run</button>
<pre id="output"></pre>

<script>
async function runPlayground() {
    if (!pyodideReady) {
        document.getElementById("output").textContent = "⏳ Pyodide ещё загружается...";
        return;
    }

    const text = document.getElementById("prompt").value;
    const n = parseInt(document.getElementById("n").value) || 1;

    // Определяем функцию в Pyodide
    await pyodide.runPythonAsync(`
import random

def mask_random_words(text, n=1, seed=None):
    words = text.split()
    if not words:
        return text
    if seed is not None:
        random.seed(seed)
    n = min(n, len(words))
    indices = random.sample(range(len(words)), n)
    for idx in indices:
        words[idx] = f"[{words[idx]}]"
    return " ".join(words)
    `);

    // Вызываем Python функцию
    const result = pyodide.runPython(`mask_random_words("${text.replace(/"/g, '\\"')}", ${n})`);
    document.getElementById("output").textContent = result;
}
</script>
