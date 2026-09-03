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

test("riceScore uses percent confidence in the Intercom formula", () => {
  assert.equal(tools.riceScore(1000, 2, 80, 4), 400);
  assert.equal(tools.riceScore(1000, 2, 0.8, 4), 400);
  assert.equal(tools.riceScore(1000, 2, 80, 0), null);
});

test("riceRank sorts scored items descending and drops incomplete rows", () => {
  const ranked = tools.riceRank([
    { name: "Invite", reach: 800, impact: 1, confidence: 80, effort: 2 },
    { name: "Incomplete" },
    { name: "Onboarding", reach: 400, impact: 3, confidence: 50, effort: 1 }
  ]);
  assert.equal(ranked.length, 2);
  assert.equal(ranked[0].name, "Onboarding");
  assert.equal(ranked[0].score, 600);
  assert.equal(ranked[1].score, 320);
});

test("aarrrBottleneck flags the weakest sequential conversion", () => {
  const rates = tools.aarrrRates([1000, 400, 200, 50, 80]);
  assert.equal(rates.steps[0].rate, 40);
  assert.equal(rates.steps[2].rate, 25);
  assert.equal(rates.referralShare, 8);
  const bottle = tools.aarrrBottleneck([1000, 400, 200, 50, 80]);
  assert.equal(bottle.index, 2);
  assert.equal(bottle.rate, 25);
});

test("heartCompleteness requires selected dimensions to be fully written", () => {
  const incomplete = tools.heartCompleteness([
    { on: true, goal: "raise NPS", signal: "survey", metric: "" }
  ]);
  assert.equal(incomplete.ready, false);
  const ready = tools.heartCompleteness([
    { on: false, goal: "", signal: "", metric: "" },
    { on: true, goal: "users finish checkout", signal: "error-free submit", metric: "task success %" }
  ]);
  assert.equal(ready.ready, true);
  assert.equal(ready.selected, 1);
});

test("northStarAssess rejects vanity names and incomplete inputs", () => {
  const vanity = tools.northStarAssess({
    name: "page views",
    checks: { value: true, leading: true, actionable: true, inputs: true },
    inputs: ["sessions", "bounce"]
  });
  assert.equal(vanity.ready, false);
  assert.ok(vanity.warnings.includes("vanity"));
  const ready = tools.northStarAssess({
    name: "nights booked per month",
    checks: { value: true, leading: true, actionable: true, inputs: true },
    inputs: ["search to book", "host reply time"]
  });
  assert.equal(ready.ready, true);
});

test("plgRecommendation maps scores to sales, hybrid, or plg", () => {
  assert.equal(tools.plgRecommendation([5, 5, 4, 4]).verdict, "plg");
  assert.equal(tools.plgRecommendation([1, 3, 3, 3]).verdict, "sales");
  assert.equal(tools.plgRecommendation([3, 2, 4, 4]).verdict, "hybrid");
  assert.equal(tools.plgRecommendation([5, 5]).verdict, "incomplete");
});

test("dualTrackBalance warns when one track is empty", () => {
  assert.equal(
    tools.dualTrackBalance({ discovery: "", delivery: "ship the billing rewrite this sprint" }).verdict,
    "delivery-only"
  );
  assert.equal(
    tools.dualTrackBalance({
      discovery: "interview switchers about activation drop",
      delivery: "build the confirmed empty-state experiment",
      oneTeam: true,
      decisions: true,
      fedByDiscovery: true
    }).verdict,
    "ok"
  );
});

test("ostAssess requires an outcome and two solutions, and flags feature-shaped opportunities", () => {
  const weak = tools.ostAssess({ outcome: "activation", opportunities: [{ name: "add a feature button", solutions: ["a"] }] });
  assert.equal(weak.complete, false);
  assert.equal(weak.flaggedSolutionish, 1);
  const ready = tools.ostAssess({
    outcome: "first-week activation reaches 40%",
    opportunities: [{ name: "cannot tell which subscription is active", solutions: ["timeline", "digest"], experiment: "fake door" }]
  });
  assert.equal(ready.complete, true);
  assert.equal(ready.flaggedSolutionish, 0);
});

test("discoveryHabitScore counts the four weekly habits", () => {
  const empty = tools.discoveryHabitScore({});
  assert.equal(empty.percent, 0);
  const full = tools.discoveryHabitScore({
    interview: true,
    trio: true,
    hypothesis: "if we shorten onboarding, activation rises",
    experiment: "prototype the three-step signup"
  });
  assert.equal(full.points, 4);
  assert.equal(full.percent, 100);
});
