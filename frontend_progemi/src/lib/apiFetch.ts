// src/lib/apiFetch.ts
export async function apiFetch<T>(
  url: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");

  /* -------------------- exécution côté serveur uniquement -------------------- */
  if (typeof window === "undefined") {
    const { cookies } = await import("next/headers");
    const store = cookies();

    // ➜ Récupération des cinq cookies
    const token     = store.get("access_token")?.value;
    const ipClient  = store.get("ip_client")?.value;
    const idHolding = store.get("idholding")?.value;
    const idSociete = store.get("idsociete")?.value;
    const idAgence  = store.get("idagence")?.value;

    // 1. Authorization si présent
    if (token) headers.set("Authorization", `Bearer ${token}`);

    // 2. Header Cookie : concatène tous les couples <clé>=<valeur>
    //    (nécessaire car fetch côté serveur n’envoie rien sinon)
    const cookieHeader = [
      token     ? `access_token=${token}`   : null,
      ipClient  ? `ip_client=${ipClient}`   : null,
      idHolding ? `idholding=${idHolding}`  : null,
      idSociete ? `idsociete=${idSociete}`  : null,
      idAgence  ? `idagence=${idAgence}`    : null,
    ]
      .filter(Boolean)
      .join("; ");

    if (cookieHeader) headers.set("Cookie", cookieHeader);
  }
  /* -------------------------------------------------------------------------- */

  const res = await fetch(url, {
    ...init,
    headers,
    credentials: "include",  // indispensable côté client
  });

  // Redirection client si 401
  if (typeof window !== "undefined" && res.status === 401) {
    window.location.replace("/session-expired");
    throw new Error("Unauthenticated");
  }

  if (!res.ok) throw new Error(await res.text());
  const ct = res.headers.get("content-type") ?? "";
  return ct.includes("application/json") ? res.json() : (res.text() as any);
}
