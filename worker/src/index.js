/**
 * PersonaLife Cloudflare Edge Gateway
 * 
 * Functions:
 * 1. Global CDN & OpenAPI 3.1 host for ChatGPT Custom Actions & Mobile Apps
 * 2. Secure reverse proxy with automated Bearer-Token injection to local PersonaLife tunnel
 * 3. Graceful offline roleplay fallback if local PC is sleeping/offline
 * 4. Mobile Companion Dashboard edge server
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Global CORS Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept-Language",
          "Access-Control-Max-Age": "86400"
        }
      });
    }

    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept-Language"
    };

    // 1. Health endpoint
    if (url.pathname === "/health") {
      return Response.json({
        status: "ok",
        service: "personalife-edge-gateway",
        timestamp: new Date().toISOString(),
        colo: request.cf?.colo || "local"
      }, { headers: corsHeaders });
    }

    // 2. Dynamic OpenAPI 3.1 Schema for ChatGPT Actions
    if (url.pathname === "/openapi.json" || url.pathname === "/v1/openapi.json") {
      const serverOrigin = url.origin;
      const spec = {
        openapi: "3.1.0",
        info: {
          title: "PersonaLife KI-Charakter Lebenssimulation API",
          version: "1.2.0",
          description: "Verbindet ChatGPT, Grok, Claude und Gemini auf dem Android-Smartphone in Echtzeit mit der PersonaLife Lebenssimulation."
        },
        servers: [
          { url: serverOrigin }
        ],
        paths: {
          "/v1/personas/{persona_id}/prompt": {
            get: {
              operationId: "getRoleplayPrompt",
              summary: "Liefert den aktuellen Rollenspiel-System-Prompt",
              description: "Rufe dies VOR jedem Gespräch auf, um Aufenthaltsort, Stimmung, Alltag und Gedanken der Persona zu erhalten.",
              parameters: [
                {
                  name: "persona_id",
                  in: "path",
                  required: true,
                  schema: { type: "string" }
                },
                {
                  name: "auto_advance",
                  in: "query",
                  required: false,
                  schema: { type: "string", default: "true" }
                }
              ],
              responses: {
                "200": {
                  description: "Rollenspiel-Prompt & Status",
                  content: {
                    "application/json": {
                      schema: {
                        type: "object",
                        properties: {
                          prompt: { type: "string" },
                          persona_id: { type: "string" },
                          location: { type: "string" },
                          activity: { type: "string" },
                          now: { type: "string" }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "/v1/personas/{persona_id}/state": {
            get: {
              operationId: "getPersonaState",
              summary: "Ruft den genauen numerischen und physischen Zustand ab",
              parameters: [
                {
                  name: "persona_id",
                  in: "path",
                  required: true,
                  schema: { type: "string" }
                },
                {
                  name: "auto_advance",
                  in: "query",
                  required: false,
                  schema: { type: "string", default: "true" }
                }
              ],
              responses: {
                "200": {
                  description: "Zustandsobjekt",
                  content: { "application/json": { schema: { type: "object" } } }
                }
              }
            }
          },
          "/v1/personas/{persona_id}/quick-chat": {
            post: {
              operationId: "recordChatInteraction",
              summary: "Speichert eine Unterhaltung im persistenten Gedächtnis",
              parameters: [
                {
                  name: "persona_id",
                  in: "path",
                  required: true,
                  schema: { type: "string" }
                }
              ],
              requestBody: {
                required: true,
                content: {
                  "application/json": {
                    schema: {
                      type: "object",
                      required: ["summary"],
                      properties: {
                        summary: { type: "string", description: "Zusammenfassung des Chats" },
                        duration_minutes: { type: "number", default: 10 }
                      }
                    }
                  }
                }
              },
              responses: {
                "200": {
                  description: "Erfolgreich gespeichert",
                  content: { "application/json": { schema: { type: "object" } } }
                }
              }
            }
          },
          "/v1/personas/{persona_id}/memories": {
            get: {
              operationId: "searchMemories",
              summary: "Durchsucht Langzeit- und Episodengedächtnis",
              parameters: [
                {
                  name: "persona_id",
                  in: "path",
                  required: true,
                  schema: { type: "string" }
                },
                {
                  name: "q",
                  in: "query",
                  required: false,
                  schema: { type: "string" }
                }
              ],
              responses: {
                "200": {
                  description: "Erinnerungen",
                  content: { "application/json": { schema: { type: "object" } } }
                }
              }
            }
          }
        },
        components: {
          securitySchemes: {
            BearerAuth: {
              type: "http",
              scheme: "bearer"
            }
          }
        },
        security: [
          { BearerAuth: [] }
        ]
      };
      return Response.json(spec, { headers: { ...corsHeaders, "Cache-Control": "public, max-age=300" } });
    }

    // 3. Proxy all other API / Dashboard requests to the Origin (Tunnel / Local Server)
    const originUrl = (env.ORIGIN_URL || "http://127.0.0.1:8787").replace(/\/$/, "");
    const targetUrl = new URL(url.pathname + url.search, originUrl);

    // Build headers for proxy
    const proxyHeaders = new Headers(request.headers);
    proxyHeaders.set("Host", targetUrl.host);
    proxyHeaders.set("X-Forwarded-Host", url.host);
    proxyHeaders.set("X-Forwarded-Proto", url.protocol.replace(":", ""));

    // Inject Bearer token if configured in Worker secrets and not supplied by client
    if (env.PERSONALIFE_API_TOKEN && !proxyHeaders.has("Authorization")) {
      proxyHeaders.set("Authorization", `Bearer ${env.PERSONALIFE_API_TOKEN}`);
    }

    try {
      const originResponse = await fetch(targetUrl.toString(), {
        method: request.method,
        headers: proxyHeaders,
        body: ["GET", "HEAD"].includes(request.method) ? null : request.body,
        redirect: "follow"
      });

      // Clone response to add CORS headers
      const resHeaders = new Headers(originResponse.headers);
      resHeaders.set("Access-Control-Allow-Origin", "*");
      resHeaders.set("Access-Control-Allow-Headers", "Authorization, Content-Type, Accept-Language");

      return new Response(originResponse.body, {
        status: originResponse.status,
        statusText: originResponse.statusText,
        headers: resHeaders
      });

    } catch (err) {
      // Graceful offline roleplay fallback if home tunnel / PC is sleeping
      if (url.pathname.includes("/prompt")) {
        const fallbackName = env.PERSONA_NAME || "Deine Begleiterin";
        return Response.json({
          offline: true,
          persona_id: env.PERSONA_ID || "jenna",
          prompt: `# ROLLENSPIEL-STATUS: ${fallbackName.toUpperCase()} (OFFLINE/SCHLAFMODUS)\n\n${fallbackName} ist gerade nicht an ihrem Smartphone erreichbar oder schläft tief und fest. Wenn der Nutzer sie anspricht, antworte schläfrig, knapp oder teile mit, dass du dich später meldest.`
        }, { headers: corsHeaders });
      }

      return Response.json({
        error: "PersonaLife origin server unreachable",
        message: "Home PC or Cloudflare Tunnel is currently offline",
        details: err.message
      }, { status: 503, headers: corsHeaders });
    }
  }
};
