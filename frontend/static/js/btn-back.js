document.addEventListener("DOMContentLoaded", function () {
  const btnVoltar = document.getElementById("btnVoltar");

  if (btnVoltar) {
    btnVoltar.addEventListener("click", () => {
      window.history.back();
    });
  }
});
