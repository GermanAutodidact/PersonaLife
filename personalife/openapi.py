"""OpenAPI 3.1.0 specification generator for ChatGPT Custom Actions and external connectors."""

def get_openapi_spec(base_url="http://127.0.0.1:8787", language="de"):
    is_de = language == "de"
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "PersonaLife API" if not is_de else "PersonaLife KI-Charakter Lebenssimulation API",
            "version": "1.2.0",
            "description": (
                "Verbindet ChatGPT und Chat-Apps in Echtzeit mit der PersonaLife Lebenssimulation. "
                "Ermöglicht lebendige Charaktere mit autonomem Tagesablauf, Stimmungen, Verpflichtungen und persistentem Gedächtnis."
                if is_de else
                "Connects ChatGPT and chat apps in real-time to the PersonaLife life simulation engine. "
                "Enables living AI characters with autonomous daily routines, emotions, duties, and persistent memory."
            )
        },
        "servers": [
            {"url": base_url.rstrip("/")}
        ],
        "paths": {
            "/v1/personas/{persona_id}/prompt": {
                "get": {
                    "operationId": "getRoleplayPrompt",
                    "summary": "Liefert den aktuellen Rollenspiel-System-Prompt" if is_de else "Get current roleplay system prompt",
                    "description": (
                        "Rufe dies VOR jedem Gespräch auf, um zu wissen, wo sich die Persona gerade befindet, was sie tut und wie es ihr geht."
                        if is_de else
                        "Call this BEFORE responding to know the persona's current location, activity, and emotional state."
                    ),
                    "parameters": [
                        {
                            "name": "persona_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                            "description": "ID der Persona (z.B. 'jenna')" if is_de else "Persona ID (e.g. 'jenna')"
                        },
                        {
                            "name": "auto_advance",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "true"},
                            "description": "Spult die Simulation automatisch auf die aktuelle Echtzeit vor ('true')" if is_de else "Fast-forward simulation to current real-time ('true')"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Erfolgreich" if is_de else "Successful",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "prompt": {"type": "string", "description": "Fertige System-Instruktion für das LLM"},
                                            "persona_id": {"type": "string"},
                                            "location": {"type": "string"},
                                            "activity": {"type": "string"},
                                            "now": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/v1/personas/{persona_id}/state": {
                "get": {
                    "operationId": "getPersonaState",
                    "summary": "Ruft den genauen numerischen und physischen Zustand ab" if is_de else "Get exact state and location",
                    "parameters": [
                        {
                            "name": "persona_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "auto_advance",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "true"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Zustandsobjekt",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/v1/personas/{persona_id}/quick-chat": {
                "post": {
                    "operationId": "recordChatInteraction",
                    "summary": "Speichert die Zusammenfassung eines Gesprächs im Gedächtnis" if is_de else "Record chat summary into memory",
                    "description": (
                        "Rufe dies nach einem Gespräch auf, um besprochene Inhalte im Gedächtnis und Lebensprotokoll der Persona zu verewigen."
                        if is_de else
                        "Call this after a chat to record what was discussed into the persona's life ledger and memory."
                    ),
                    "parameters": [
                        {
                            "name": "persona_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["summary"],
                                    "properties": {
                                        "summary": {"type": "string", "description": "Kurze prägnante Zusammenfassung des Chats"},
                                        "duration_minutes": {"type": "number", "default": 10, "description": "Ungefähre Dauer in Minuten"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Gespräch erfolgreich verbucht",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/v1/personas/{persona_id}/memories": {
                "get": {
                    "operationId": "searchMemories",
                    "summary": "Durchsucht das episodische und Langzeitgedächtnis" if is_de else "Search episodic and long-term memory",
                    "parameters": [
                        {
                            "name": "persona_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "q",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Suchbegriff"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Liste von Erinnerungen",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer"
                }
            }
        },
        "security": [
            {"BearerAuth": []}
        ]
    }
