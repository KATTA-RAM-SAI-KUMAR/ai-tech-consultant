import { classifyEmail } from "./classifier.js";
import { createServer } from "node:http";

const PORT = Number(process.env.PORT ?? 3000);
const KNOWLEDGE_API = process.env.KNOWLEDGE_API ?? "http://127.0.0.1:8000/query";

type Email = {
  id?: string;
  from: string;
  subject: string;
  body: string;
};



async function handleEmail(email: Email) {
  const category = classifyEmail(email.subject, email.body);
  let knowledge: any = null;

  try {
    const response = await fetch(KNOWLEDGE_API, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question: `${email.subject}\n${email.body}` }),
      signal: AbortSignal.timeout(120000)
    });
    if (response.ok) knowledge = await response.json();
  } catch {
    // The draft remains available, but must be reviewed without knowledge results.
  }

  const evidence = knowledge?.status === "answered"
    ? `\n\nRelevant knowledge:\n${knowledge.answer}\n\nSources:\n${(knowledge.sources ?? []).map((s: any) => `${s.title}: ${s.url}`).join("\n")}`
    : "\n\nKnowledge lookup was unavailable or inconclusive. Verify the answer before sending.";

  const draft = `Hello,\n\nThank you for contacting us about "${email.subject}". We understand your concern and will review it carefully. ${category === "technical_support" ? "Please share any error message and the steps that led to the issue if you have not already included them." : "We will check the details and follow up with the appropriate next steps."}${evidence}\n\nBest regards,\nSupport Team`;

  return {
    id: email.id ?? `email-${Date.now()}`,
    category,
    draft,
    sources: knowledge?.sources ?? [],
    status: "pending_human_approval",
    autonomousEligible: false
  };
}

const server = createServer(async (req, res) => {
  res.setHeader("content-type", "application/json; charset=utf-8");

  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200);
    res.end(JSON.stringify({ status: "ok", service: "inbox-agent" }));
    return;
  }

  if (req.method !== "POST" || req.url !== "/process") {
    res.writeHead(404);
    res.end(JSON.stringify({ error: "Use POST /process or GET /health" }));
    return;
  }

  try {
    let raw = "";
    for await (const chunk of req) raw += chunk;
    const email = JSON.parse(raw) as Email;

    if (!email || typeof email.from !== "string" ||
        typeof email.subject !== "string" || typeof email.body !== "string") {
      res.writeHead(400);
      res.end(JSON.stringify({ error: "Expected from, subject, and body strings" }));
      return;
    }

    const result = await handleEmail(email);
    res.writeHead(200);
    res.end(JSON.stringify(result, null, 2));
  } catch {
    res.writeHead(400);
    res.end(JSON.stringify({ error: "Invalid JSON request" }));
  }
});

server.listen(PORT, () => console.log(`Inbox Agent running at http://localhost:${PORT}`));

