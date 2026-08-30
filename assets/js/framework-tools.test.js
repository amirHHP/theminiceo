const test = require("node:test");
const assert = require("node:assert/strict");
const tools = require("../../static/js/framework-tools.js");

test("buildJobStory returns empty when all fields are blank", () => {
  assert.equal(tools.buildJobStory({ lang: "fa" }), "");
});

test("buildJobStory builds a Persian job story", () => {
  const story = tools.buildJobStory({
    lang: "fa",
    situation: "جمعه شب تنها هستم",
    motivation: "غذای گرم سریع داشته باشم",
    outcome: "استراحت کنم"
  });
  assert.equal(
    story,
    "وقتی جمعه شب تنها هستم، می‌خواهم غذای گرم سریع داشته باشم، تا بتوانم استراحت کنم."
  );
});

test("buildJobStory builds an English job story", () => {
  const story = tools.buildJobStory({
    lang: "en",
    situation: "it is Friday night",
    motivation: "eat without cooking",
    outcome: "rest"
  });
  assert.equal(story, "When it is Friday night, I want to eat without cooking, so I can rest.");
});

test("assessJobStory flags product-centric wording", () => {
  const result = tools.assessJobStory({
    situation: "I open the app homepage",
    motivation: "click the new feature button",
    outcome: "see the dashboard"
  });
  assert.equal(result.complete, true);
  assert.ok(result.warnings.includes("product-centric"));
});

test("assessJobStory marks a specific non-product statement as ok", () => {
  const result = tools.assessJobStory({
    situation: "Friday night I am tired and the kitchen is a mess",
    motivation: "eat something warm without thinking",
    outcome: "spend the evening resting"
  });
  assert.deepEqual(result.warnings, ["ok"]);
});

test("sprintDayDates returns five consecutive calendar days", () => {
  assert.deepEqual(tools.sprintDayDates("2026-08-31", 5), [
    "2026-08-31",
    "2026-09-01",
    "2026-09-02",
    "2026-09-03",
    "2026-09-04"
  ]);
});

test("sprintDayDates returns empty for an invalid date", () => {
  assert.deepEqual(tools.sprintDayDates("not-a-date", 5), []);
});

test("sprintReadiness lists every missing gate", () => {
  const result = tools.sprintReadiness({ problem: "hi" });
  assert.equal(result.ready, false);
  assert.deepEqual(result.missing, ["decider", "facilitator", "users", "problem"]);
});

test("sprintReadiness passes when the team is prepared", () => {
  const result = tools.sprintReadiness({
    decider: true,
    facilitator: true,
    users: true,
    problem: "Activation after signup is below 20%"
  });
  assert.equal(result.ready, true);
  assert.deepEqual(result.missing, []);
});

test("checklistProgress rounds a partial sprint checklist", () => {
  assert.equal(tools.checklistProgress(9, 17), 53);
  assert.equal(tools.checklistProgress(0, 17), 0);
  assert.equal(tools.checklistProgress(3, 0), 0);
});

test("opportunityRecommendation stays incomplete until nine scores exist", () => {
  const result = tools.opportunityRecommendation([5, 5, 4]);
  assert.equal(result.verdict, "incomplete");
});

test("opportunityRecommendation returns go for a strong complete sheet", () => {
  const result = tools.opportunityRecommendation([5, 4, 4, 4, 4, 4, 4, 4, 4]);
  assert.equal(result.verdict, "go");
  assert.equal(result.average, 4.1);
  assert.deepEqual(result.weak, []);
});

test("opportunityRecommendation returns nogo when the problem is unproven", () => {
  const result = tools.opportunityRecommendation([1, 2, 3, 3, 3, 3, 3, 3, 3]);
  assert.equal(result.verdict, "nogo");
  assert.ok(result.weak.includes(0));
});

test("opportunityRecommendation returns caution for mixed scores", () => {
  const result = tools.opportunityRecommendation([4, 3, 3, 2, 4, 4, 3, 3, 4]);
  assert.equal(result.verdict, "caution");
  assert.deepEqual(result.weak, [3]);
});
