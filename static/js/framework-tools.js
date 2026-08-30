(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }
  if (typeof window !== "undefined") {
    window.FrameworkTools = api;
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", api.mountAll);
    } else {
      api.mountAll();
    }
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  var PRODUCTISH = /فیچر|دکمه|اپلیکیشن|\bapp\b|\bfeature\b|\bbutton\b|\bclick\b|\bui\b/i;

  var COPY = {
    fa: {
      toolBadge: "ابزار تعاملی",
      copy: "کپی",
      copied: "کپی شد",
      reset: "پاک کردن",
      saved: "روی همین مرورگر ذخیره می‌شود",
      jtbdTitle: "سازندهٔ جملهٔ Job",
      jtbdLead: "سه خانه را پر کنید تا جملهٔ استخدام محصول ساخته شود. اگر جمله حول فیچر بچرخد، ابزار هشدار می‌دهد.",
      situation: "وقتی… (موقعیت)",
      situationPh: "مثلاً جمعه شب تنها هستم و حوصلهٔ آشپزی ندارم",
      motivation: "می‌خواهم… (انگیزه)",
      motivationPh: "بدون فکر کردن غذای گرم و سریع داشته باشم",
      outcome: "تا بتوانم… (پیشرفت مورد انتظار)",
      outcomePh: "غروب را استراحت کنم، نه اینکه در آشپزخانه بمانم",
      functional: "بُعد کارکردی (اختیاری)",
      emotional: "بُعد عاطفی (اختیاری)",
      social: "بُعد اجتماعی (اختیاری)",
      jobPreview: "جملهٔ Job",
      emptyJob: "هنوز جمله‌ای ساخته نشده است.",
      warnShort: "جمله هنوز کلی است. موقعیت را مشخص‌تر کنید؛ job در وضعیت رخ می‌دهد، نه در انتزاع.",
      warnProduct: "جمله شبیه توضیح فیچر است. محصول را از جمله بردارید و پیشرفت مشتری را بنویسید.",
      warnOk: "جمله قابل استفاده است. در مصاحبه با همین ساختار جلو بروید و چهار نیروی تعویض را بپرسید.",
      sprintTitle: "برنامه‌ریز دیزاین اسپرینت",
      sprintLead: "آمادگی تیم را بسنجید، روز شروع را بگذارید و چک‌لیست پنج روز را تیک بزنید.",
      startDate: "روز شروع اسپرینت",
      problem: "مسئلهٔ اسپرینت در یک جمله",
      problemPh: "مثلاً نرخ فعال‌سازی بعد از ثبت‌نام زیر ۲۰٪ است",
      decider: "تصمیم‌گیر نهایی در اتاق است",
      facilitator: "تسهیل‌گر مشخص شده است",
      users: "حداقل پنج کاربر برای جمعه هماهنگ شده‌اند",
      readyYes: "اسپرینت آمادهٔ شروع است.",
      readyNo: "قبل از دوشنبه این موارد را ببندید:",
      missDecider: "تصمیم‌گیر",
      missFacilitator: "تسهیل‌گر",
      missUsers: "هماهنگی مصاحبهٔ جمعه",
      missProblem: "یک جملهٔ مسئله",
      dayLabel: "روز",
      progress: "پیشرفت چک‌لیست",
      oppTitle: "کاربرگ ارزیابی فرصت",
      oppLead: "نه سؤال اول را با عدد ۱ تا ۵ و یک یادداشت کوتاه جواب دهید. پیشنهاد نهایی را ابزار می‌سازد.",
      score: "قوت پاسخ (۱ ضعیف — ۵ قوی)",
      unanswered: "هنوز امتیازی داده نشده",
      recGo: "بروید",
      recCaution: "با احتیاط ادامه دهید",
      recNogo: "فعلاً نروید",
      recNeed: "اول نه سؤال را امتیاز بدهید",
      copySummary: "کپی خلاصه"
    },
    en: {
      toolBadge: "Interactive tool",
      copy: "Copy",
      copied: "Copied",
      reset: "Reset",
      saved: "Saved in this browser only",
      jtbdTitle: "Job-statement builder",
      jtbdLead: "Fill the three fields to write the hiring statement. The tool warns you if the sentence is really a feature description.",
      situation: "When… (situation)",
      situationPh: "e.g. it is Friday night, I am alone, and I do not want to cook",
      motivation: "I want to… (motivation)",
      motivationPh: "get a hot meal quickly without thinking",
      outcome: "so I can… (progress)",
      outcomePh: "spend the evening resting, not standing in the kitchen",
      functional: "Functional dimension (optional)",
      emotional: "Emotional dimension (optional)",
      social: "Social dimension (optional)",
      jobPreview: "Job statement",
      emptyJob: "No statement yet.",
      warnShort: "The statement is still generic. Make the situation specific — a job happens in a circumstance, not in the abstract.",
      warnProduct: "This reads like a feature. Remove the product and write the customer’s progress.",
      warnOk: "Usable statement. Take it into interviews and probe the four forces of switching.",
      sprintTitle: "Design Sprint planner",
      sprintLead: "Check team readiness, pick a start date, and tick the five-day checklist.",
      startDate: "Sprint start date",
      problem: "Sprint problem in one sentence",
      problemPh: "e.g. activation after signup is below 20%",
      decider: "The decider will be in the room",
      facilitator: "A facilitator is named",
      users: "At least five users are booked for Friday",
      readyYes: "The sprint is ready to start.",
      readyNo: "Close these before Monday:",
      missDecider: "decider",
      missFacilitator: "facilitator",
      missUsers: "Friday interviews",
      missProblem: "one-sentence problem",
      dayLabel: "Day",
      progress: "Checklist progress",
      oppTitle: "Opportunity assessment worksheet",
      oppLead: "Score the first nine questions from 1 to 5 and add a short note. The tool writes the recommendation.",
      score: "Answer strength (1 weak — 5 strong)",
      unanswered: "Not scored yet",
      recGo: "Go",
      recCaution: "Proceed with caution",
      recNogo: "Do not go yet",
      recNeed: "Score the nine questions first",
      copySummary: "Copy summary"
    }
  };

  var SPRINT_DAYS = {
    fa: [
      { title: "دوشنبه — نقشه و هدف", items: ["هدف بلندمدت و سؤال‌های اسپرینت نوشته شد", "نقشهٔ سفر روی دیوار رفت", "مصاحبه با خبره‌ها انجام شد", "یک هدف اسپرینت انتخاب شد"] },
      { title: "سه‌شنبه — اسکچ", items: ["لایتنینگ دمو از راه‌حل‌های موجود", "یادداشت و Crazy 8s", "اسکچ راه‌حل سه‌پنلی هر نفر"] },
      { title: "چهارشنبه — تصمیم", items: ["هیت‌مپ و رأی بی‌حرف", "سوپروات تصمیم‌گیر", "استوری‌بورد تست روز پنجشنبه"] },
      { title: "پنجشنبه — پروتوتایپ", items: ["نقش‌ها تقسیم شد (میز، بازیگر، وصله‌کار)", "پروتوتایپ واقع‌نما، نه محصول واقعی", "اسکریپت مصاحبهٔ فردا آماده است"] },
      { title: "جمعه — تست", items: ["پنج مصاحبه با کاربر واقعی", "الگوی تکرارشونده روی تخته رفت", "تصمیم بعدی: ادامه، چرخش، یا توقف"] }
    ],
    en: [
      { title: "Monday — map and target", items: ["Long-term goal and sprint questions written", "Journey map is on the wall", "Ask the Experts is done", "One sprint target is chosen"] },
      { title: "Tuesday — sketch", items: ["Lightning demos of existing solutions", "Notes and Crazy 8s", "Each person made a three-panel solution sketch"] },
      { title: "Wednesday — decide", items: ["Heat map and silent vote", "Decider supervote", "Thursday test storyboard"] },
      { title: "Thursday — prototype", items: ["Roles split (maker, actor, stitcher)", "Realistic prototype, not the real product", "Friday interview script is ready"] },
      { title: "Friday — test", items: ["Five interviews with real users", "Recurring patterns are on the board", "Next decision: continue, pivot, or stop"] }
    ]
  };

  var OPP_QUESTIONS = {
    fa: [
      ["value", "دقیقاً چه مشکلی حل می‌شود؟", "ارزش پیشنهادی"],
      ["customer", "این مشکل را برای چه کسانی حل می‌کنیم؟", "مشتری هدف"],
      ["size", "اندازهٔ فرصت چقدر است؟", "اندازه بازار"],
      ["alts", "الان چه جایگزین‌هایی وجود دارد؟", "فضای رقابتی"],
      ["us", "چرا ما برای این فرصت مناسبیم؟", "تمایز"],
      ["now", "چرا الان؟", "زمان بازار"],
      ["gtm", "چطور محصول را به بازار می‌رسانیم؟", "ورود به بازار"],
      ["metrics", "موفقیت را چطور می‌سنجیم و چطور درآمد می‌گیریم؟", "سنجه و درآمد"],
      ["critical", "چه عواملی برای موفقیت حیاتی‌اند؟", "نیازمندی‌های راه‌حل"]
    ],
    en: [
      ["value", "Exactly what problem does this solve?", "Value proposition"],
      ["customer", "Who are we solving it for?", "Target customer"],
      ["size", "How big is the opportunity?", "Market size"],
      ["alts", "What alternatives exist today?", "Competitive landscape"],
      ["us", "Why are we the right team?", "Differentiator"],
      ["now", "Why now?", "Market window"],
      ["gtm", "How will we take it to market?", "Go-to-market"],
      ["metrics", "How will we measure success and make money?", "Metrics / revenue"],
      ["critical", "What factors are critical to success?", "Solution requirements"]
    ]
  };

  function copyFor(lang) {
    return COPY[lang] || COPY.fa;
  }

  function trim(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function buildJobStory(input) {
    var situation = trim(input && input.situation);
    var motivation = trim(input && input.motivation);
    var outcome = trim(input && input.outcome);
    var lang = (input && input.lang) || "fa";
    if (!situation && !motivation && !outcome) return "";
    if (lang === "en") {
      return "When " + (situation || "…") + ", I want to " + (motivation || "…") + ", so I can " + (outcome || "…") + ".";
    }
    return "وقتی " + (situation || "…") + "، می‌خواهم " + (motivation || "…") + "، تا بتوانم " + (outcome || "…") + ".";
  }

  function assessJobStory(input) {
    var situation = trim(input && input.situation);
    var motivation = trim(input && input.motivation);
    var outcome = trim(input && input.outcome);
    var blob = [situation, motivation, outcome].join(" ");
    var warnings = [];
    var complete = situation.length >= 8 && motivation.length >= 8 && outcome.length >= 8;
    if (!complete || situation.length < 12) warnings.push("situation-short");
    if (PRODUCTISH.test(blob)) warnings.push("product-centric");
    if (complete && warnings.length === 0) warnings.push("ok");
    return { complete: complete, warnings: warnings };
  }

  function pad2(value) {
    return value < 10 ? "0" + value : String(value);
  }

  function localISODate(date) {
    return date.getFullYear() + "-" + pad2(date.getMonth() + 1) + "-" + pad2(date.getDate());
  }

  function sprintDayDates(startISO, count) {
    var start = startISO ? new Date(startISO + "T00:00:00") : null;
    if (!start || Number.isNaN(start.getTime())) return [];
    var dates = [];
    var i;
    for (i = 0; i < count; i += 1) {
      var cursor = new Date(start.getTime());
      cursor.setDate(start.getDate() + i);
      dates.push(localISODate(cursor));
    }
    return dates;
  }

  function sprintReadiness(input) {
    var missing = [];
    if (!(input && input.decider)) missing.push("decider");
    if (!(input && input.facilitator)) missing.push("facilitator");
    if (!(input && input.users)) missing.push("users");
    if (trim(input && input.problem).length < 12) missing.push("problem");
    return { ready: missing.length === 0, missing: missing };
  }

  function checklistProgress(checked, total) {
    if (!total) return 0;
    return Math.round((Number(checked) / Number(total)) * 100);
  }

  function average(numbers) {
    var values = (numbers || []).filter(function (n) { return typeof n === "number" && n > 0; });
    if (!values.length) return 0;
    var sum = values.reduce(function (acc, n) { return acc + n; }, 0);
    return Math.round((sum / values.length) * 10) / 10;
  }

  function opportunityRecommendation(scores) {
    var list = scores || [];
    var answered = list.filter(function (n) { return typeof n === "number" && n > 0; });
    if (answered.length < 9) {
      return { verdict: "incomplete", average: average(list), weak: [] };
    }
    var avg = average(list);
    var weak = [];
    list.forEach(function (score, index) {
      if (score <= 2) weak.push(index);
    });
    var criticalWeak = (list[0] || 0) < 3 || (list[1] || 0) < 3;
    var verdict = "caution";
    if (avg >= 4 && !criticalWeak && weak.length === 0) verdict = "go";
    else if (avg < 3 || (list[0] || 0) < 2 || (list[1] || 0) < 2) verdict = "nogo";
    return { verdict: verdict, average: avg, weak: weak };
  }

  function storageKey(name, lang) {
    return "tmc-fw-" + name + "-" + lang;
  }

  function loadState(name, lang) {
    try {
      return JSON.parse(localStorage.getItem(storageKey(name, lang)) || "null");
    } catch (err) {
      return null;
    }
  }

  function saveState(name, lang, value) {
    try {
      localStorage.setItem(storageKey(name, lang), JSON.stringify(value));
    } catch (err) {
      /* ignore quota / private mode */
    }
  }

  function el(html) {
    var wrap = document.createElement("div");
    wrap.innerHTML = html.trim();
    return wrap.firstElementChild;
  }

  function field(id, label, placeholder, multiline) {
    var tag = multiline ? "textarea" : "input";
    var extra = multiline ? " rows=\"2\"" : " type=\"text\"";
    return (
      "<label class=\"fw-tool-field\">" +
        "<span>" + label + "</span>" +
        "<" + tag + " id=\"" + id + "\" placeholder=\"" + placeholder + "\"" + extra + "></" + tag + ">" +
      "</label>"
    );
  }

  function actionBar(c, extraButton) {
    return (
      "<div class=\"fw-tool-actions\">" +
        "<button type=\"button\" class=\"fw-tool-btn\" data-action=\"copy\">" + c.copy + "</button>" +
        (extraButton || "") +
        "<button type=\"button\" class=\"fw-tool-btn fw-tool-btn-ghost\" data-action=\"reset\">" + c.reset + "</button>" +
        "<span class=\"fw-tool-hint\">" + c.saved + "</span>" +
      "</div>"
    );
  }

  function flashCopied(button, c) {
    var original = button.textContent;
    button.textContent = c.copied;
    setTimeout(function () { button.textContent = original; }, 1400);
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return Promise.resolve();
  }

  function mountJtbd(root, lang) {
    var c = copyFor(lang);
    root.innerHTML =
      "<div class=\"fw-tool-head\">" +
        "<span class=\"fw-tool-badge\">" + c.toolBadge + "</span>" +
        "<h3>" + c.jtbdTitle + "</h3>" +
        "<p>" + c.jtbdLead + "</p>" +
      "</div>" +
      field("fw-situation", c.situation, c.situationPh, true) +
      field("fw-motivation", c.motivation, c.motivationPh, true) +
      field("fw-outcome", c.outcome, c.outcomePh, true) +
      "<div class=\"fw-tool-grid\">" +
        field("fw-functional", c.functional, "", false) +
        field("fw-emotional", c.emotional, "", false) +
        field("fw-social", c.social, "", false) +
      "</div>" +
      "<div class=\"fw-tool-preview\" id=\"fw-job-preview\">" + c.emptyJob + "</div>" +
      "<p class=\"fw-tool-note\" id=\"fw-job-note\"></p>" +
      actionBar(c);

    var inputs = ["situation", "motivation", "outcome", "functional", "emotional", "social"];
    var saved = loadState("jtbd", lang) || {};

    function read() {
      var data = {};
      inputs.forEach(function (key) {
        var node = root.querySelector("#fw-" + key);
        data[key] = node ? node.value : "";
      });
      data.lang = lang;
      return data;
    }

    function render() {
      var data = read();
      var story = buildJobStory(data);
      var assess = assessJobStory(data);
      root.querySelector("#fw-job-preview").textContent = story || c.emptyJob;
      var note = root.querySelector("#fw-job-note");
      note.className = "fw-tool-note";
      if (assess.warnings.indexOf("product-centric") !== -1) {
        note.textContent = c.warnProduct;
        note.classList.add("is-warn");
      } else if (assess.warnings.indexOf("situation-short") !== -1 && (data.situation || data.motivation || data.outcome)) {
        note.textContent = c.warnShort;
      } else if (assess.warnings.indexOf("ok") !== -1) {
        note.textContent = c.warnOk;
        note.classList.add("is-ok");
      } else {
        note.textContent = "";
      }
      saveState("jtbd", lang, data);
    }

    inputs.forEach(function (key) {
      var node = root.querySelector("#fw-" + key);
      if (!node) return;
      if (saved[key]) node.value = saved[key];
      node.addEventListener("input", render);
    });

    root.querySelector("[data-action=\"copy\"]").addEventListener("click", function (event) {
      var story = buildJobStory(read());
      if (!story) return;
      copyText(story).then(function () { flashCopied(event.currentTarget, c); });
    });
    root.querySelector("[data-action=\"reset\"]").addEventListener("click", function () {
      inputs.forEach(function (key) {
        var node = root.querySelector("#fw-" + key);
        if (node) node.value = "";
      });
      saveState("jtbd", lang, {});
      render();
    });
    render();
  }

  function mountSprint(root, lang) {
    var c = copyFor(lang);
    var days = SPRINT_DAYS[lang] || SPRINT_DAYS.fa;
    var itemTotal = days.reduce(function (sum, day) { return sum + day.items.length; }, 0);
    var checksHtml = days.map(function (day, dayIndex) {
      var boxes = day.items.map(function (item, itemIndex) {
        var id = "fw-sp-" + dayIndex + "-" + itemIndex;
        return "<label class=\"fw-check\"><input type=\"checkbox\" id=\"" + id + "\"> <span>" + item + "</span></label>";
      }).join("");
      return "<section class=\"fw-sprint-day\"><h4 id=\"fw-day-title-" + dayIndex + "\">" + day.title + "</h4>" + boxes + "</section>";
    }).join("");

    root.innerHTML =
      "<div class=\"fw-tool-head\">" +
        "<span class=\"fw-tool-badge\">" + c.toolBadge + "</span>" +
        "<h3>" + c.sprintTitle + "</h3>" +
        "<p>" + c.sprintLead + "</p>" +
      "</div>" +
      "<div class=\"fw-tool-grid\">" +
        "<label class=\"fw-tool-field\"><span>" + c.startDate + "</span><input id=\"fw-start\" type=\"date\"></label>" +
        field("fw-problem", c.problem, c.problemPh, true) +
      "</div>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-decider\"> <span>" + c.decider + "</span></label>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-facilitator\"> <span>" + c.facilitator + "</span></label>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-users\"> <span>" + c.users + "</span></label>" +
      "<p class=\"fw-tool-note\" id=\"fw-ready\"></p>" +
      "<div class=\"fw-tool-progress\"><span>" + c.progress + "</span><strong id=\"fw-progress\">0%</strong></div>" +
      checksHtml +
      actionBar(c);

    var saved = loadState("sprint", lang) || {};

    function read() {
      var checked = [];
      days.forEach(function (day, dayIndex) {
        day.items.forEach(function (_, itemIndex) {
          var box = root.querySelector("#fw-sp-" + dayIndex + "-" + itemIndex);
          checked.push(!!(box && box.checked));
        });
      });
      return {
        start: (root.querySelector("#fw-start") || {}).value || "",
        problem: (root.querySelector("#fw-problem") || {}).value || "",
        decider: !!(root.querySelector("#fw-decider") || {}).checked,
        facilitator: !!(root.querySelector("#fw-facilitator") || {}).checked,
        users: !!(root.querySelector("#fw-users") || {}).checked,
        checked: checked
      };
    }

    function applyDates(start) {
      var dates = sprintDayDates(start, 5);
      days.forEach(function (day, index) {
        var title = root.querySelector("#fw-day-title-" + index);
        if (!title) return;
        title.textContent = dates[index] ? day.title + " · " + dates[index] : day.title;
      });
    }

    function render() {
      var data = read();
      var readiness = sprintReadiness(data);
      var done = data.checked.filter(Boolean).length;
      var note = root.querySelector("#fw-ready");
      note.className = "fw-tool-note";
      if (readiness.ready) {
        note.textContent = c.readyYes;
        note.classList.add("is-ok");
      } else {
        var labels = { decider: c.missDecider, facilitator: c.missFacilitator, users: c.missUsers, problem: c.missProblem };
        note.textContent = c.readyNo + " " + readiness.missing.map(function (key) { return labels[key]; }).join(lang === "en" ? ", " : "، ");
        note.classList.add("is-warn");
      }
      root.querySelector("#fw-progress").textContent = checklistProgress(done, itemTotal) + "%";
      applyDates(data.start);
      saveState("sprint", lang, data);
    }

    if (saved.start) root.querySelector("#fw-start").value = saved.start;
    if (saved.problem) root.querySelector("#fw-problem").value = saved.problem;
    ["decider", "facilitator", "users"].forEach(function (key) {
      if (saved[key]) root.querySelector("#fw-" + key).checked = true;
    });
    (saved.checked || []).forEach(function (on, index) {
      var box = root.querySelectorAll(".fw-sprint-day input[type=\"checkbox\"]")[index];
      if (box) box.checked = on;
    });

    root.querySelectorAll("input, textarea").forEach(function (node) {
      node.addEventListener("input", render);
      node.addEventListener("change", render);
    });
    root.querySelector("[data-action=\"copy\"]").addEventListener("click", function (event) {
      var data = read();
      var dates = sprintDayDates(data.start, 5);
      var lines = [data.problem].concat(days.map(function (day, i) {
        return (dates[i] || c.dayLabel + " " + (i + 1)) + " — " + day.title;
      }));
      copyText(lines.filter(Boolean).join("\n")).then(function () { flashCopied(event.currentTarget, c); });
    });
    root.querySelector("[data-action=\"reset\"]").addEventListener("click", function () {
      root.querySelectorAll("input, textarea").forEach(function (node) {
        if (node.type === "checkbox") node.checked = false;
        else node.value = "";
      });
      saveState("sprint", lang, {});
      render();
    });
    render();
  }

  function mountOpportunity(root, lang) {
    var c = copyFor(lang);
    var questions = OPP_QUESTIONS[lang] || OPP_QUESTIONS.fa;
    var fields = questions.map(function (q, index) {
      return (
        "<section class=\"fw-opp-q\" data-index=\"" + index + "\">" +
          "<h4>" + (index + 1) + ". " + q[1] + " <small>" + q[2] + "</small></h4>" +
          "<textarea id=\"fw-opp-note-" + index + "\" rows=\"2\"></textarea>" +
          "<label class=\"fw-tool-field fw-score\">" +
            "<span>" + c.score + "</span>" +
            "<input id=\"fw-opp-score-" + index + "\" type=\"range\" min=\"0\" max=\"5\" step=\"1\" value=\"0\">" +
            "<em id=\"fw-opp-score-label-" + index + "\">" + c.unanswered + "</em>" +
          "</label>" +
        "</section>"
      );
    }).join("");

    root.innerHTML =
      "<div class=\"fw-tool-head\">" +
        "<span class=\"fw-tool-badge\">" + c.toolBadge + "</span>" +
        "<h3>" + c.oppTitle + "</h3>" +
        "<p>" + c.oppLead + "</p>" +
      "</div>" +
      fields +
      "<div class=\"fw-tool-preview\" id=\"fw-opp-rec\"></div>" +
      actionBar(c, "<button type=\"button\" class=\"fw-tool-btn fw-tool-btn-secondary\" data-action=\"summary\">" + c.copySummary + "</button>");

    var saved = loadState("opportunity", lang) || {};

    function read() {
      return questions.map(function (q, index) {
        return {
          id: q[0],
          title: q[1],
          tag: q[2],
          note: (root.querySelector("#fw-opp-note-" + index) || {}).value || "",
          score: Number((root.querySelector("#fw-opp-score-" + index) || {}).value || 0)
        };
      });
    }

    function render() {
      var rows = read();
      var rec = opportunityRecommendation(rows.map(function (row) { return row.score; }));
      rows.forEach(function (row, index) {
        var label = root.querySelector("#fw-opp-score-label-" + index);
        if (label) label.textContent = row.score ? String(row.score) : c.unanswered;
      });
      var box = root.querySelector("#fw-opp-rec");
      box.className = "fw-tool-preview";
      if (rec.verdict === "incomplete") {
        box.textContent = c.recNeed;
      } else {
        var label = rec.verdict === "go" ? c.recGo : rec.verdict === "nogo" ? c.recNogo : c.recCaution;
        box.classList.add(rec.verdict === "go" ? "is-go" : rec.verdict === "nogo" ? "is-nogo" : "is-caution");
        var weak = rec.weak.map(function (i) { return questions[i][2]; }).join(" · ");
        box.textContent = label + " · " + rec.average + "/5" + (weak ? " — " + weak : "");
      }
      saveState("opportunity", lang, rows);
    }

    questions.forEach(function (_, index) {
      var row = (saved || [])[index] || {};
      var note = root.querySelector("#fw-opp-note-" + index);
      var score = root.querySelector("#fw-opp-score-" + index);
      if (note && row.note) note.value = row.note;
      if (score && row.score) score.value = row.score;
      if (note) note.addEventListener("input", render);
      if (score) score.addEventListener("input", render);
    });

    function summaryText() {
      var rows = read();
      var rec = opportunityRecommendation(rows.map(function (row) { return row.score; }));
      var header = rec.verdict === "go" ? c.recGo : rec.verdict === "nogo" ? c.recNogo : rec.verdict === "caution" ? c.recCaution : c.recNeed;
      return [header + (rec.average ? " (" + rec.average + "/5)" : "")].concat(rows.map(function (row, i) {
        return (i + 1) + ". " + row.title + " [" + (row.score || "-") + "] " + trim(row.note);
      })).join("\n");
    }

    root.querySelector("[data-action=\"copy\"]").addEventListener("click", function (event) {
      copyText(summaryText()).then(function () { flashCopied(event.currentTarget, c); });
    });
    root.querySelector("[data-action=\"summary\"]").addEventListener("click", function (event) {
      copyText(summaryText()).then(function () { flashCopied(event.currentTarget, c); });
    });
    root.querySelector("[data-action=\"reset\"]").addEventListener("click", function () {
      root.querySelectorAll("textarea").forEach(function (node) { node.value = ""; });
      root.querySelectorAll("input[type=\"range\"]").forEach(function (node) { node.value = "0"; });
      saveState("opportunity", lang, []);
      render();
    });
    render();
  }

  function mountAll() {
    if (typeof document === "undefined") return;
    document.querySelectorAll("[data-fw-tool]").forEach(function (node) {
      if (node.getAttribute("data-fw-mounted")) return;
      node.setAttribute("data-fw-mounted", "true");
      var name = node.getAttribute("data-fw-tool");
      var lang = node.getAttribute("data-lang") || "fa";
      if (name === "jtbd") mountJtbd(node, lang);
      if (name === "sprint") mountSprint(node, lang);
      if (name === "opportunity") mountOpportunity(node, lang);
    });
  }

  return {
    buildJobStory: buildJobStory,
    assessJobStory: assessJobStory,
    sprintDayDates: sprintDayDates,
    sprintReadiness: sprintReadiness,
    checklistProgress: checklistProgress,
    average: average,
    opportunityRecommendation: opportunityRecommendation,
    mountAll: mountAll
  };
});
