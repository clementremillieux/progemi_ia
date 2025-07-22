// middleware.ts
import { NextRequest, NextResponse } from "next/server";
import * as jose from "jose";

export function middleware(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;
  const isPublic = ["/", "/session-expired", "/api"].some((p) =>
    req.nextUrl.pathname.startsWith(p),
  );

  if (isPublic) return NextResponse.next();
  if (!token) return NextResponse.redirect(new URL("/session-expired", req.url));

  return NextResponse.next();
}

export const config = { matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"] };
