import { gqlRequest } from "./apiClient.js";

const GET_ALL_COUNTRIES = `
  query {
    getAllCountries {
      id
      code
      name
      phoneCode
      currencyId
    }
  }
`;

const CREATE_COUNTRY = `
  mutation CreateCountry($payload: CountryInput!) {
    createCountry(payload: $payload) {
      id
      code
      name
      phoneCode
      currencyId
    }
  }
`;

export async function getCountries() {
  const data = await gqlRequest(GET_ALL_COUNTRIES);
  return data.getAllCountries;
}

export async function createCountry(payload) {
  const data = await gqlRequest(CREATE_COUNTRY, { payload });
  return data.createCountry;
}

