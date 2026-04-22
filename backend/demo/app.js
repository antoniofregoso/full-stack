import { login, logout } from "./auth.js";
import { createCountry, getCountries } from "./coreApi.js";

const logBox = document.getElementById("log");
const loginForm = document.getElementById("login-form");
const countriesBtn = document.getElementById("btn-countries");
const createCountryForm = document.getElementById("create-country-form");
const logoutBtn = document.getElementById("btn-logout");

function log(message, data = null) {
  const now = new Date().toISOString();
  const payload = data ? `\n${JSON.stringify(data, null, 2)}` : "";
  logBox.textContent = `[${now}] ${message}${payload}\n\n${logBox.textContent}`;
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const session = await login(email, password);
    log("Login correcto", { email: session.email });
  } catch (error) {
    log(`Error login: ${error.message}`);
  }
});

countriesBtn.addEventListener("click", async () => {
  try {
    const countries = await getCountries();
    log("getAllCountries OK", countries);
  } catch (error) {
    log(`Error getAllCountries: ${error.message}`);
  }
});

createCountryForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const code = document.getElementById("country-code").value.trim().toUpperCase();
  const name = document.getElementById("country-name").value.trim();
  const phoneCodeRaw = document.getElementById("country-phone").value.trim();
  const currencyIdRaw = document.getElementById("country-currency-id").value.trim();

  const payload = {
    code,
    name,
    phoneCode: phoneCodeRaw || null,
    currencyId: currencyIdRaw ? Number(currencyIdRaw) : null,
  };

  try {
    const country = await createCountry(payload);
    log("createCountry OK", country);
  } catch (error) {
    log(`Error createCountry: ${error.message}`);
  }
});

logoutBtn.addEventListener("click", () => {
  logout();
  log("Sesion cerrada");
});

