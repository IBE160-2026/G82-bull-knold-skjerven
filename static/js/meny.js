// Lukker «Meny» med Esc og med klikk utenfor. Uten dette virker menyen fortsatt
// med tastatur og klikk på «Meny», og den åpnes og lukkes av nettleseren.
(function () {
  function lukkAlle(unntatt) {
    document.querySelectorAll("details.meny[open]").forEach(function (meny) {
      if (meny !== unntatt) meny.open = false;
    });
  }
  document.addEventListener("keydown", function (hendelse) {
    if (hendelse.key !== "Escape") return;
    document.querySelectorAll("details.meny[open]").forEach(function (meny) {
      meny.open = false;
      meny.querySelector("summary").focus();
    });
  });
  document.addEventListener("click", function (hendelse) {
    var meny = hendelse.target.closest ? hendelse.target.closest("details.meny") : null;
    lukkAlle(meny);
  });
})();
