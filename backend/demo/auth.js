import { gqlRequest } from "./apiClient.js";
import { clearToken, saveToken } from "./storage.js";

const LOGIN_MUTATION = `
  mutation Login($email: String!, $password: String!) {
    login(login: { email: $email, password: $password }) {
      email
      token
    }
  }
`;

export async function login(email, password) {
  const data = await gqlRequest(LOGIN_MUTATION, { email, password });
  saveToken(data.login.token);
  return data.login;
}

export function logout() {
  clearToken();
}

