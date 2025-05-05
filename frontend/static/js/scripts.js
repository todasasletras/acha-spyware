const DB_NAME = "analysisDB";
const STORE_NAME = "analysisResults";
const DB_VERSION = 1;

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

    request.onsuccess = () => resolve(request.result); // ID do item salvo
    request.onerror = () => reject(request.error);
  });
}

async function getAllAnalyses() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.getAll();

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function getAnalysisById(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.get(id);

    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function deleteAnalysis(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.delete(id);

    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}

async function clearAllAnalyses() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.clear();

    request.onsuccess = () => resolve(true);
    request.onerror = () => reject(request.error);
  });
}


// Função para salvar a chave da API
async function enviarApiKey() {
  const apiKeyInput = document.querySelector("#apiKeyInput");
  const apiKey = apiKeyInput ? apiKeyInput.value.trim() : "";

  if (!apiKey) {
    document.querySelector("#resultadoApiKey").innerHTML = "⚠️ Informe uma chave de API.";
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
    } else {
      document.querySelector("#resultadoApiKey").innerHTML = `❌ Erro ao salvar a chave da API: ${data.error}`;
    }
  } catch (error) {
    document.querySelector("#resultadoApiKey").innerHTML = "❌ Erro na requisição ao salvar a chave da API.";
    console.error("Erro ao enviar a chave:", error);
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
    // virustotal: true  // assume que usará virustotal se já salvou a chave antes
  };

  try {
    const response = await fetch("/api/android/check-adb", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(dados)
    });

    const data = await response.json();
    console.log('data:', data)

    if (data.success) {
      const resultados = data.messages || [];
      console.log('success: ', resultados)
      await saveAnalysis(resultados);
      const mensagens = resultados.map(item => {
        return `<div><strong>${item.category.toUpperCase()}</strong> - ${item.message}</div>`;
      }).join("");
      document.querySelector("#resultado").innerHTML = mensagens || "✅ Dispositivo encontrado!";
    } else {
      document.querySelector("#resultado").innerHTML = `❌ Erro: ${data.error}`;
    }
  } catch (error) {
    document.querySelector("#resultado").innerHTML = "❌ Erro na requisição.";
    console.error("Erro ao chamar /check-adb:", error);
  } finally {
    spinner.classList.add("d-none");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("btnEnviarApiKey").addEventListener("click", enviarApiKey);
  document.getElementById("btnVerificarAdb").addEventListener("click", enviarCheckAdb);
});
