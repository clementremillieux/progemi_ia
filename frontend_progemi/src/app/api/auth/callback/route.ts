// src/app/api/auth/callback/route.ts

// src/app/api/auth/callback/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const search = req.nextUrl.searchParams;

  const token     = search.get("token");
  const ipClient  = search.get("ip_client");
  const idHolding = search.get("idholding");
  const idSociete = search.get("idsociete");
  const idAgence  = search.get("idagence");

  if (!token || !ipClient || !idHolding || !idSociete || !idAgence) {
    return NextResponse.json({ error: "Missing parameter(s)" }, { status: 400 });
  }

  const res = NextResponse.redirect(new URL("/", req.url));

  // Options communes
  const opts = {
    httpOnly : true,
    secure   : process.env.NODE_ENV === "production",
    sameSite : "lax" as const,
    path     : "/",
    maxAge   : 60 * 60,           // 1 h ; adaptez si besoin
  };

  // ⬇️  Quatre + un cookies
  res.cookies.set("access_token", token,     opts);
  res.cookies.set("ip_client",    ipClient,  opts);
  res.cookies.set("idholding",    idHolding, opts);
  res.cookies.set("idsociete",    idSociete, opts);
  res.cookies.set("idagence",     idAgence,  opts);

  return res;
}

