// S8: når spørringen fra #spor feiler (serverfeil eller nettfeil), viser
// #fremdrift meldingen fra data-feil-server, og spørringen stopper.
// Teksten kommer fra farequiz/feilmeldinger.py.
(function () {
  function sporringFeilet(hendelse) {
    var kilde = hendelse.detail && hendelse.detail.elt;
    if (!kilde || kilde.id !== "spor") return;
    var fremdrift = document.getElementById("fremdrift");
    if (fremdrift) {
      var melding = document.createElement("p");
      melding.setAttribute("role", "alert");
      melding.className = "mb-2 font-semibold text-error";
      melding.textContent = fremdrift.dataset.feilServer;
      while (fremdrift.firstChild) fremdrift.removeChild(fremdrift.firstChild);
      fremdrift.appendChild(melding);
    }
    // Hjelpeteksten og den låste «Lag quiz» gjelder ikke lenger.
    var handlinger = document.getElementById("handlinger");
    if (handlinger) {
      while (handlinger.firstChild) handlinger.removeChild(handlinger.firstChild);
    }
    // Uten #spor går det ingen ny spørring.
    if (kilde.parentNode) kilde.parentNode.removeChild(kilde);
  }

  document.addEventListener("htmx:responseError", sporringFeilet);
  document.addEventListener("htmx:sendError", sporringFeilet);
})();
