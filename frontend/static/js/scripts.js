document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("btnVerificarAdb").addEventListener("click", enviarCheckAdb);
});

async function enviarCheckAdb() {
  const url = "/check-adb";
  const dados = {
      serial: "auto",
      fast: false,
      verbose: true
  };

  try {
    const response = await fetch("/check-adb", { method: "POST" });
    const data = await response.json();

    if (data.success) {
        document.querySelector("#resultado").innerHTML = "✅ Dispositivo encontrado!";
    } else {
        document.querySelector("#resultado").innerHTML = `Erro: ${data.error}`;
    }
  } catch (error) {
      document.querySelector("#resultado").innerHTML = "Erro na requisição.";
      console.error("Erro ao chamar /check-adb:", error);
  }
}
