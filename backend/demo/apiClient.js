import { GraphQLClient } from "https://esm.sh/graphql-request@7";
import { GRAPHQL_URL } from "./config.js";
import { clearToken, getToken } from "./storage.js";

function createClient() {
  const token = getToken();

  return new GraphQLClient(GRAPHQL_URL, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
}

function normalizeGraphQLError(error) {
  const messages =
    error?.response?.errors?.map((item) => item.message) ??
    [error?.message ?? "Unknown error"];

  const text = messages.join(" | ");
  const lower = text.toLowerCase();

  if (lower.includes("unauthorized") || lower.includes("auth")) {
    return { kind: "unauthorized", message: text };
  }

  if (lower.includes("forbidden") || lower.includes("permission")) {
    return { kind: "forbidden", message: text };
  }

  return { kind: "unknown", message: text };
}

export async function gqlRequest(query, variables = {}) {
  try {
    const client = createClient();
    return await client.request(query, variables);
  } catch (error) {
    const normalized = normalizeGraphQLError(error);

    if (normalized.kind === "unauthorized") {
      clearToken();
      throw new Error("Sesion expirada o token invalido. Haz login nuevamente.");
    }

    if (normalized.kind === "forbidden") {
      throw new Error("No tienes permisos para esta operacion (RBAC).");
    }

    throw new Error(normalized.message);
  }
}

