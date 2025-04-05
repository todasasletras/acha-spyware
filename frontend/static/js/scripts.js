async function enviarCheckAdb() {
  const url = "/check-adb";
  const dados = {
    serial: "auto",
    fast: false,
    verbose: true
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(dados)
    });

    const data = await response.json();

    console.log(data)

    if (data.success) {
      const resultados = data.output || [];
      const mensagens = resultados.map(item => {
        return `<div><strong>${item.status.toUpperCase()}</strong> - ${item.message}</div>`;
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
  document.getElementById("btnVerificarAdb").addEventListener("click", enviarCheckAdb);
});
