const DB_NAME = "analysisDB";
const STORE_NAME = "analysisResults";
const DB_VERSION = 1;

function showAlert(message, type = "success") {
  const alertContainer = document.getElementById("alertContainer");
  const alert = document.createElement("div");
  alert.className = `alert alert-${type} alert-dismissible fade show shadow`;
  alert.role = "alert";
  alert.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  alertContainer.appendChild(alert);

  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
    bsAlert.close();
  }, 4000);
}

async function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      console.log("Atualizando banco de dados...");
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        console.log("Criando object store...");
        db.createObjectStore(STORE_NAME, { keyPath: "id", autoIncrement: true });
      }
    };

    request.onsuccess = () => {
      console.log("Banco de dados aberto com sucesso!");
      resolve(request.result);
    };

    request.onerror = (event) => {
      console.error('Erro ao abrir o banco de dados:', event.target.error);
      showAlert("❌ Erro ao abrir o banco de dados!", "danger");
      reject(event.target.error);
    };
  });
}

async function saveAnalysis(data) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.add(data);

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => {
      showAlert("❌ Erro ao salvar a análise!", "danger");
      reject(request.error);
    };
  });
}

async function getAllAnalyses() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => {
      showAlert("❌ Erro ao buscar análises!", "danger");
      reject(request.error);
    };
  });
}

async function getAnalysisById(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.get(id);

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => {
      showAlert("❌ Erro ao buscar análise por ID!", "danger");
      reject(request.error);
    };
  });
}

async function deleteAnalysis(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.delete(id);

    request.onsuccess = () => resolve(true);
    request.onerror = () => {
      showAlert("❌ Erro ao excluir análise!", "danger");
      reject(request.error);
    };
  });
}

async function clearAllAnalyses() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.clear();

    request.onsuccess = () => resolve(true);
    request.onerror = () => {
      showAlert("❌ Erro ao limpar todas as análises!", "danger");
      reject(request.error);
    };
  });
}

// Função para salvar a chave da API
async function enviarApiKey() {
  const apiKeyInput = document.querySelector("#apiKeyInput");
  const apiKey = apiKeyInput ? apiKeyInput.value.trim() : "";

  // Resetando estado anterior de erro
  apiKeyInput.classList.remove("is-invalid");

  if (!apiKey) {
    apiKeyInput.classList.add("is-invalid");
    apiKeyInput.focus();
    showAlert("⚠️ Informe uma chave de API.", "warning");
    return;
  }

  try {
    const response = await fetch("/api/config/set-vt-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: apiKey })
    });

    const data = await response.json();

    if (data.success) {
      document.querySelector("#resultadoApiKey").innerHTML = "✅ Chave da API salva com sucesso!";
      showAlert("✅ Chave da API salva com sucesso!", "success");
    } else {
      document.querySelector("#resultadoApiKey").innerHTML = `❌ Erro: ${data.error}`;
      showAlert(`❌ Erro ao salvar a API: ${data.error}`, "danger");
    }
  } catch (error) {
    document.querySelector("#resultadoApiKey").innerHTML = "❌ Erro na requisição.";
    console.error("Erro ao enviar a chave:", error);
    showAlert("❌ Erro na requisição ao salvar a API.", "danger");
  }
}

// Função para enviar a verificação ADB
async function enviarCheckAdb() {
  const spinner = document.querySelector("#btnVerificarAdb .spinner");
  spinner.classList.remove("d-none");
  const dados = {
    serial: null,
    fast: false,
    verbose: true,
  };

  try {
    const response = await fetch("/api/android/check-adb", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados)
    });

    const data = await response.json();

    if (data.success) {
      const resultados = data.messages || [];
      await saveAnalysis(resultados);
      const mensagens = resultados.map(item => {
        return `<div><strong>${item.category.toUpperCase()}</strong> - ${item.message}</div>`;
      }).join("");
      document.querySelector("#resultado").innerHTML = mensagens || "✅ Dispositivo encontrado!";
      showAlert("✅ Dispositivo verificado com sucesso!", "success");
    } else {
      document.querySelector("#resultado").innerHTML = `❌ Erro: ${data.error}`;
      showAlert(`❌ Erro: ${data.error}`, "danger");
    }
  } catch (error) {
    document.querySelector("#resultado").innerHTML = "❌ Erro na requisição.";
    console.error("Erro ao chamar /check-adb:", error);
    showAlert("❌ Erro na requisição ao verificar o dispositivo.", "danger");
  } finally {
    spinner.classList.add("d-none");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("btnEnviarApiKey").addEventListener("click", enviarApiKey);
  document.getElementById("btnVerificarAdb").addEventListener("click", enviarCheckAdb);
});
