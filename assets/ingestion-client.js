/* Beluga passenger-side published-context hook (does not replace composer routing). */
(() => {
  "use strict";
  const airportCode = value => /^[A-Za-z]{3}$/.test(String(value || "")) ? String(value).toUpperCase() : null;
  let current = null;
  let lastProfile = null;
  const findAirport = () => airportCode(
    document.querySelector("[data-current-airport]")?.getAttribute("data-current-airport") ||
    document.querySelector("[data-airport-code]")?.getAttribute("data-airport-code") ||
    document.body?.dataset?.airport ||
    window.BELUGA_AIRPORT ||
    "IAD"
  );
  const headerElement = () => document.querySelector(
    "[data-beluga-airport-header], #airportHeroImage, #airportHeaderImage, img[data-airport-header]"
  );
  async function getProfile(airport) {
    const code = airportCode(airport);
    if (!code) throw new Error("Invalid airport code");
    const response = await fetch("/api/ingestion/airport/" + code, {cache:"no-store"});
    if (!response.ok) return null;
    return response.json();
  }
  async function retrieve(question, airport = current) {
    const code = airportCode(airport);
    if (!code || !question) return {airport:code, evidence:[], mode:"unavailable"};
    const response = await fetch("/api/ingestion/retrieve", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({airport:code, question:String(question).slice(0,3000)})
    });
    if (!response.ok) throw new Error("Airport retrieval unavailable");
    return response.json();
  }
  function updateHeader(profile) {
    if (!profile?.header_image_url) return;
    const node = headerElement();
    if (!node) return;
    if (node.tagName === "IMG") {
      if (node.getAttribute("src") !== profile.header_image_url) node.setAttribute("src", profile.header_image_url);
      node.alt = profile.airport_name ? profile.airport_name + " airport" : "Airport";
    } else {
      node.style.backgroundImage = 'url("' + profile.header_image_url.replace(/["\\]/g, "") + '")';
    }
  }
  async function setAirport(code) {
    code = airportCode(code);
    if (!code) return null;
    current = code;
    const requested = code;
    const profile = await getProfile(code).catch(() => null);
    if (current !== requested) return null;
    lastProfile = profile;
    updateHeader(profile);
    document.dispatchEvent(new CustomEvent("beluga:ingestion:updated", {
      detail: {airport:requested, profile, available:!!profile}
    }));
    return profile;
  }
  window.BelugaIngestion = Object.freeze({
    setAirport, getProfile, retrieve,
    get currentAirport() { return current; },
    get profile() { return lastProfile; }
  });
  document.addEventListener("beluga:airport-changed", event => {
    setAirport(event.detail?.airport || event.detail?.code);
  });
  // Reapplies a published header if the home screen re-renders.
  const observer = new MutationObserver(() => updateHeader(lastProfile));
  const start = () => {
    observer.observe(document.body, {childList:true, subtree:true});
    setAirport(findAirport());
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once:true});
  else start();
})();
