// S6b og S6c: sjekk i nettleseren, opplasting med fremdrift og melding om avbrudd.
// Uten dette skriptet sendes skjemaet som vanlig, og serveren sjekker filen (AD-13).
// Serveren sjekker alltid filen på nytt.
(function () {
  if (!window.FormData || !window.DOMParser) return;
  var xhrTest = new XMLHttpRequest();
  if (!("upload" in xhrTest) || !("responseURL" in xhrTest)) return;

  var ENDELSER = [".pdf", ".docx", ".txt"];
  var opptatt = false;

  function hent(id) {
    return document.getElementById(id);
  }

  function filfelt(skjema) {
    return skjema.querySelector('input[type="file"]');
  }

  function fjernFeil(skjema) {
    var felt = filfelt(skjema);
    var feil = hent("feil-fil");
    if (feil) feil.parentNode.removeChild(feil);
    felt.removeAttribute("aria-invalid");
    felt.setAttribute("aria-describedby", "hjelp-fil");
    var avbrutt = hent("opplasting-avbrutt");
    if (avbrutt) {
      avbrutt.hidden = true;
      avbrutt.textContent = "";
    }
  }

  function visFeil(skjema, tekst) {
    var felt = filfelt(skjema);
    var feil = document.createElement("p");
    feil.id = "feil-fil";
    feil.setAttribute("role", "alert");
    feil.setAttribute("tabindex", "-1");
    feil.className = "mt-2 font-semibold text-error";
    feil.textContent = tekst;
    felt.parentNode.insertBefore(feil, felt.nextSibling);
    felt.setAttribute("aria-invalid", "true");
    felt.setAttribute("aria-describedby", "hjelp-fil feil-fil");
    feil.focus();
  }

  function sjekkFil(skjema) {
    var felt = filfelt(skjema);
    var fil = felt.files && felt.files[0];
    if (!fil) return skjema.dataset.feilIngen;
    if (fil.size > Number(skjema.dataset.maks)) return skjema.dataset.feilForStor;
    var navn = fil.name.toLowerCase();
    var punktum = navn.lastIndexOf(".");
    // Som på serveren: et navn som bare er «.txt», har ingen endelse.
    var endelse = punktum > 0 ? navn.slice(punktum) : "";
    if (ENDELSER.indexOf(endelse) < 0) return skjema.dataset.feilFormat;
    if (fil.size === 0) return skjema.dataset.feilTom;
    return null;
  }

  function settFremdrift(skjema, filnavn, prosent) {
    var status = hent("opplasting-status");
    var strek = skjema.querySelector(".reiserute span");
    if (strek) strek.style.width = prosent + "%";
    // Teksten oppdateres i steg på 10 %, så skjermlesere ikke får en melding per prosent.
    var steg = prosent === 100 ? 100 : Math.floor(prosent / 10) * 10;
    if (status && status.getAttribute("data-steg") !== String(steg)) {
      status.setAttribute("data-steg", String(steg));
      status.textContent = filnavn + " · " + steg + " % lastet opp";
    }
  }

  function startOpplasting(skjema, filnavn) {
    opptatt = true;
    hent("opplasting-knapp").setAttribute("aria-disabled", "true");
    hent("opplasting-overskrift").textContent = "Laster opp notat";
    hent("opplasting-fremdrift").hidden = false;
    settFremdrift(skjema, filnavn, 0);
  }

  function stoppOpplasting(skjema) {
    opptatt = false;
    var knapp = hent("opplasting-knapp");
    if (knapp) knapp.removeAttribute("aria-disabled");
    var overskrift = hent("opplasting-overskrift");
    if (overskrift) overskrift.textContent = "Last opp notat";
    var fremdrift = hent("opplasting-fremdrift");
    if (fremdrift) fremdrift.hidden = true;
    var status = hent("opplasting-status");
    if (status) {
      status.textContent = "";
      status.removeAttribute("data-steg");
    }
    var strek = skjema.querySelector(".reiserute span");
    if (strek) strek.style.width = "0";
  }

  function visAvbrutt(skjema) {
    stoppOpplasting(skjema);
    var avbrutt = hent("opplasting-avbrutt");
    avbrutt.textContent = skjema.dataset.feilAvbrutt;
    avbrutt.hidden = false;
    avbrutt.focus();
  }

  // Serveren svarte med en side i stedet for å sende videre, for eksempel skjemaet
  // med en feil. Innholdet byttes ut, og fokus flyttes til feilen.
  function visSvar(skjema, html) {
    var dokument = new DOMParser().parseFromString(html, "text/html");
    var nytt = dokument.getElementById("innhold");
    var gammelt = hent("innhold");
    if (!nytt || !gammelt) return false;
    opptatt = false;
    gammelt.innerHTML = nytt.innerHTML;
    if (dokument.title) document.title = dokument.title;
    var fokus = gammelt.querySelector("[autofocus]") || gammelt.querySelector("h1");
    if (fokus) {
      if (!fokus.hasAttribute("tabindex")) fokus.setAttribute("tabindex", "-1");
      fokus.focus();
    }
    return true;
  }

  document.addEventListener("submit", function (hendelse) {
    var skjema = hendelse.target;
    if (!skjema || skjema.id !== "opplasting") return;
    hendelse.preventDefault();
    if (opptatt) return;

    fjernFeil(skjema);
    var feil = sjekkFil(skjema);
    if (feil) {
      visFeil(skjema, feil);
      return;
    }

    var fil = filfelt(skjema).files[0];
    var data = new FormData(skjema);
    var xhr = new XMLHttpRequest();
    xhr.open("POST", skjema.action);
    xhr.timeout = 300000;
    xhr.upload.addEventListener("progress", function (e) {
      if (e.lengthComputable && e.total > 0) {
        settFremdrift(skjema, fil.name, Math.min(100, Math.round((e.loaded / e.total) * 100)));
      }
    });
    xhr.addEventListener("load", function () {
      var tilbake = new URL(skjema.action, window.location.href).pathname;
      var svarUrl = xhr.responseURL ? new URL(xhr.responseURL) : null;
      // Serveren sendte videre, for eksempel til notatsiden etter vellykket opplasting.
      if (svarUrl && svarUrl.pathname !== tilbake && xhr.status < 400) {
        settFremdrift(skjema, fil.name, 100);
        window.location.assign(xhr.responseURL);
        return;
      }
      // Bare skjemaet med en feil (200) vises. Andre svar regnes som avbrutt.
      if (xhr.status !== 200 || !visSvar(skjema, xhr.responseText)) visAvbrutt(skjema);
    });
    xhr.addEventListener("error", function () { visAvbrutt(skjema); });
    xhr.addEventListener("abort", function () { visAvbrutt(skjema); });
    xhr.addEventListener("timeout", function () { visAvbrutt(skjema); });

    startOpplasting(skjema, fil.name);
    xhr.send(data);
  });
})();
