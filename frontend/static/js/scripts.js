// Função para salvar a chave da API
async function enviarApiKey() {
  const apiKeyInput = document.querySelector("#apiKeyInput");
  const apiKey = apiKeyInput ? apiKeyInput.value.trim() : "";

  if (!apiKey) {
    document.querySelector("#resultado").innerHTML = "⚠️ Informe uma chave de API.";
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
      document.querySelector("#resultado").innerHTML = `❌ Erro ao salvar a chave da API: ${data.error}`;
    }
  } catch (error) {
    document.querySelector("#resultado").innerHTML = "❌ Erro na requisição ao salvar a chave da API.";
    console.error("Erro ao enviar a chave:", error);
  }
}

// Função para enviar a verificação ADB
async function enviarCheckAdb() {
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
      const mensagens = resultados.map(item => {
        console.log('items:', item)
        return `<div><strong>${item.category.toUpperCase()}</strong> - ${item.message}</div>`;
      }).join("");
      document.querySelector("#resultado").innerHTML = mensagens || "✅ Dispositivo encontrado!";
    } else {
      document.querySelector("#resultado").innerHTML = `❌ Erro: ${data.error}`;
    }
  } catch (error) {
    document.querySelector("#resultado").innerHTML = "❌ Erro na requisição.";
    console.error("Erro ao chamar /check-adb:", error);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("btnEnviarApiKey").addEventListener("click", enviarApiKey);
  document.getElementById("btnVerificarAdb").addEventListener("click", enviarCheckAdb);
});
