export type EmailCategory =
  | "billing"
  | "technical_support"
  | "cancellation"
  | "feature_request"
  | "complaint"
  | "general";

export function classifyEmail(subject: string, body: string): EmailCategory {
  const text = `${subject} ${body}`.toLowerCase();

  if (/refund|billing|invoice|payment|charge/.test(text)) return "billing";
  if (/bug|error|not working|broken|failed/.test(text)) return "technical_support";
  if (/cancel|termination|close account/.test(text)) return "cancellation";
  if (/feature|integration|custom development/.test(text)) return "feature_request";
  if (/urgent|angry|complaint|manager/.test(text)) return "complaint";
  return "general";
}
