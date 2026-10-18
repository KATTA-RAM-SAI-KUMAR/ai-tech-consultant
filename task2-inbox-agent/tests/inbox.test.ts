import { test } from "node:test";
import assert from "node:assert/strict";
import { classifyEmail } from "../src/classifier.js";

test("classifies billing messages", () => {
  assert.equal(classifyEmail("Invoice question", "I was charged twice"), "billing");
});

test("classifies technical support messages", () => {
  assert.equal(classifyEmail("Dashboard error", "The page is not working"), "technical_support");
});

test("classifies cancellation messages", () => {
  assert.equal(classifyEmail("Close account", "Please cancel my account"), "cancellation");
});

test("classifies feature requests", () => {
  assert.equal(classifyEmail("Integration", "Please add a CRM integration"), "feature_request");
});

test("classifies complaints", () => {
  assert.equal(classifyEmail("Urgent complaint", "I need a manager"), "complaint");
});

test("defaults to general", () => {
  assert.equal(classifyEmail("Question", "Where can I update my profile?"), "general");
});
