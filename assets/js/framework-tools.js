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
      copySummary: "کپی خلاصه",
      riceTitle: "ماشین‌حساب RICE",
      riceLead: "چند آیتم بک‌لاگ را با پوشش، تأثیر، اطمینان و تلاش بسنجید. امتیاز پایین یعنی اولویت پایین‌تر یا اطمینان ضعیف.",
      riceName: "آیتم بک‌لاگ",
      riceNamePh: "مثلاً دعوت مهمان به فضای کاری",
      riceReach: "پوشش (کاربر در دوره)",
      riceImpact: "تأثیر",
      riceConfidence: "اطمینان (٪)",
      riceEffort: "تلاش (نفر-ماه)",
      riceAdd: "آیتم بعدی",
      riceRemove: "حذف",
      riceEmpty: "حداقل یک آیتم را با چهار عدد پر کنید.",
      riceRank: "رتبه‌بندی",
      impactMassive: "۳ — خیلی زیاد",
      impactHigh: "۲ — زیاد",
      impactMedium: "۱ — متوسط",
      impactLow: "۰٫۵ — کم",
      impactMinimal: "۰٫۲۵ — خیلی کم",
      aarrrTitle: "تشخیص نشتی قیف AARRR",
      aarrrLead: "تعداد کاربر هر مرحله را در یک دوره وارد کنید. ابزار ضعیف‌ترین حلقهٔ متوالی را نشان می‌دهد.",
      aarrrAcq: "جذب",
      aarrrAct: "فعال‌سازی",
      aarrrRet: "نگهداشت",
      aarrrRev: "درآمد",
      aarrrRef: "معرفی",
      aarrrNeed: "حداقل جذب و فعال‌سازی را عدد بدهید.",
      aarrrBottleneck: "ضعیف‌ترین حلقه:",
      aarrrOk: "تبدیل‌ها نزدیک‌اند؛ یک حلقه را هدف بگیرید نه همه را.",
      heartTitle: "کاربرگ HEART + GSM",
      heartLead: "دو یا سه بُعد را انتخاب کنید و برای هرکدام هدف، سیگنال و سنجه بنویسید. لازم نیست هر پنج تا را پر کنید.",
      heartGoal: "هدف",
      heartSignal: "سیگنال",
      heartMetric: "سنجه",
      heartNeed: "حداقل یک بُعد را کامل کنید.",
      heartOk: "برای بُعدهای انتخاب‌شده هدف، سیگنال و سنجه دارید.",
      heartPartial: "بُعدهایی که تیک خورده‌اند هنوز ناقص‌اند.",
      hHappiness: "Happiness — رضایت",
      hEngagement: "Engagement — درگیری",
      hAdoption: "Adoption — پذیرش",
      hRetention: "Retention — نگهداشت",
      hTask: "Task success — موفقیت کار",
      nsTitle: "سازندهٔ North Star",
      nsLead: "نام سنجه را بنویسید، چهار شرط کیفیت را چک کنید و ورودی‌ها را بگذارید.",
      nsName: "نام سنجه",
      nsNamePh: "مثلاً شب رزروشده در ماه",
      nsValue: "ارزش مشتری را می‌سنجد، نه فعالیت داخلی",
      nsLeading: "پیش‌نگر رشد پایدار است",
      nsActionable: "تیم محصول می‌تواند روی آن اثر بگذارد",
      nsHasInputs: "ورودی‌های روشن دارد",
      nsInput: "سنجهٔ ورودی",
      nsNeed: "نام سنجه و دست‌کم دو ورودی لازم است.",
      nsVanity: "این نام شبیه سنجهٔ vanity است. ارزش مشتری را بنویسید، نه فعالیت تیم.",
      nsGaps: "این شرط‌ها هنوز تیک نخورده:",
      nsOk: "سنجه قابل دفاع است. اگر بالا رفت و مشتری بدتر شد، عوضش کنید.",
      gapValue: "ارزش مشتری",
      gapLeading: "پیش‌نگر بودن",
      gapActionable: "قابل اقدام",
      gapInputs: "ورودی‌ها",
      plgTitle: "آمادگی Product-Led Growth",
      plgLead: "چهار ستون را از ۱ تا ۵ امتیاز بدهید. ابزار می‌گوید محصول‌محور، ترکیبی، یا فروش‌محور.",
      plgTtv: "زمان رسیدن به ارزش کوتاه است",
      plgSelf: "خرید و ارتقا self-serve است",
      plgLoop: "حلقه رشد داخل محصول کار می‌کند",
      plgData: "تصمیم از دادهٔ رفتار می‌آید نه فقط پایپ‌لاین",
      plgNeed: "هر چهار ستون را امتیاز بدهید.",
      plgSales: "فعلاً فروش‌محور",
      plgHybrid: "مدل ترکیبی",
      plgReady: "آمادگی PLG",
      dtTitle: "تختهٔ هفتگی Dual-Track",
      dtLead: "کشف این هفته را کنار تحویل بگذارید. اگر یکی خالی باشد، مسیر تکی شده‌اید.",
      dtDiscovery: "Discovery این هفته",
      dtDiscoveryPh: "فرضیه‌ها، مصاحبه، آزمایش ارزان",
      dtDelivery: "Delivery این هفته",
      dtDeliveryPh: "چیزی که کشف تأیید کرده و در حال ساخت است",
      dtOneTeam: "یک تیم هر دو مسیر را مالک است",
      dtDecisions: "خروجی کشف تصمیم است، نه فقط استوری",
      dtFed: "ورودی تحویل از کشف می‌آید نه از ایمیل ذینفع",
      dtEmpty: "هر دو مسیر را با کار همین هفته پر کنید.",
      dtDeliveryOnly: "فقط Delivery دارید؛ یادگیری بعد از انتشار می‌آید.",
      dtDiscoveryOnly: "فقط Discovery دارید؛ محصول جلو نمی‌رود.",
      dtCaution: "دو مسیر هست، ولی سلامت تیم کامل نیست.",
      dtOk: "دو مسیر موازی و سالم به‌نظر می‌رسد.",
      ostTitle: "سازندهٔ درخت فرصت–راه‌حل",
      ostLead: "یک outcome، بعد فرصت مشتری، چند راه‌حل و یک آزمایش ارزان.",
      ostOutcome: "Outcome قابل اندازه‌گیری",
      ostOutcomePh: "مثلاً فعال‌سازی هفتهٔ اول به ۴۰٪ برسد",
      ostOpp: "فرصت مشتری",
      ostOppPh: "درد یا کار ناتمام، نه فیچر",
      ostSol: "راه‌حل",
      ostExp: "کوچک‌ترین آزمایش",
      ostAddOpp: "فرصت بعدی",
      ostNeed: "Outcome و دست‌کم یک فرصت با دو راه‌حل بنویسید.",
      ostSolutionish: "بعضی فرصت‌ها شبیه راه‌حل‌اند. درد مشتری را بنویسید، نه فیچر.",
      ostOk: "درخت برای جلسه قابل استفاده است. هفتهٔ بعد شاخه‌ها را هرس کنید.",
      cdTitle: "ردیاب عادت Continuous Discovery",
      cdLead: "چهار عادت هفته را ببندید. هدف کامل بودن هفته است، نه پروژهٔ فصلی.",
      cdWeek: "شروع هفته",
      cdInterview: "حداقل یک مصاحبهٔ ساخت‌یافته انجام شد",
      cdNotes: "یادداشت مصاحبه",
      cdTrio: "محصول، دیزاین و مهندسی با هم شنیدند",
      cdHyp: "فرضیهٔ این هفته",
      cdHypPh: "اگر X را عوض کنیم، Y در رفتار مشتری دیده می‌شود",
      cdExp: "آزمایش ارزان",
      cdExpPh: "پروتوتایپ، فیک در، یا آزمون پیام",
      cdNeed: "عادت‌ها را یکی‌یکی ببندید.",
      cdPartial: "هفته ناقص است. عادت خالی را اول پر کنید.",
      cdOk: "عادت هفته کامل است."
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
      copySummary: "Copy summary",
      riceTitle: "RICE calculator",
      riceLead: "Score backlog items with reach, impact, confidence, and effort. A low score means lower priority — or weak evidence.",
      riceName: "Backlog item",
      riceNamePh: "e.g. guest invite to the workspace",
      riceReach: "Reach (users in the period)",
      riceImpact: "Impact",
      riceConfidence: "Confidence (%)",
      riceEffort: "Effort (person-months)",
      riceAdd: "Add item",
      riceRemove: "Remove",
      riceEmpty: "Fill at least one item with all four numbers.",
      riceRank: "Ranking",
      impactMassive: "3 — massive",
      impactHigh: "2 — high",
      impactMedium: "1 — medium",
      impactLow: "0.5 — low",
      impactMinimal: "0.25 — minimal",
      aarrrTitle: "AARRR leak finder",
      aarrrLead: "Enter user counts for one period. The tool flags the weakest sequential step.",
      aarrrAcq: "Acquisition",
      aarrrAct: "Activation",
      aarrrRet: "Retention",
      aarrrRev: "Revenue",
      aarrrRef: "Referral",
      aarrrNeed: "Enter at least acquisition and activation.",
      aarrrBottleneck: "Weakest link:",
      aarrrOk: "Conversion rates are close. Attack one stage, not all of them.",
      heartTitle: "HEART + GSM worksheet",
      heartLead: "Pick two or three dimensions and write a goal, signal, and metric for each. You do not need all five.",
      heartGoal: "Goal",
      heartSignal: "Signal",
      heartMetric: "Metric",
      heartNeed: "Complete at least one dimension.",
      heartOk: "Every selected dimension has a goal, signal, and metric.",
      heartPartial: "Selected dimensions are still incomplete.",
      hHappiness: "Happiness",
      hEngagement: "Engagement",
      hAdoption: "Adoption",
      hRetention: "Retention",
      hTask: "Task success",
      nsTitle: "North Star builder",
      nsLead: "Name the metric, tick the quality tests, and add input metrics.",
      nsName: "Metric name",
      nsNamePh: "e.g. nights booked per month",
      nsValue: "It measures customer value, not internal activity",
      nsLeading: "It leads sustainable growth",
      nsActionable: "The product team can move it",
      nsHasInputs: "It has clear input metrics",
      nsInput: "Input metric",
      nsNeed: "A name and at least two inputs are required.",
      nsVanity: "That name looks like a vanity metric. Write customer value, not team activity.",
      nsGaps: "Still unchecked:",
      nsOk: "Defensible metric. If it rises while customers get worse off, change it.",
      gapValue: "customer value",
      gapLeading: "leading indicator",
      gapActionable: "actionable",
      gapInputs: "inputs",
      plgTitle: "Product-Led Growth readiness",
      plgLead: "Score the four pillars from 1 to 5. The tool says product-led, hybrid, or sales-led.",
      plgTtv: "Time-to-value is short",
      plgSelf: "Buy and upgrade are self-serve",
      plgLoop: "A growth loop runs inside the product",
      plgData: "Decisions come from behavior data, not only the pipeline",
      plgNeed: "Score all four pillars.",
      plgSales: "Sales-led for now",
      plgHybrid: "Hybrid model",
      plgReady: "PLG-ready",
      dtTitle: "Dual-Track weekly board",
      dtLead: "Put this week’s discovery next to delivery. If one side is empty, you are on a single track.",
      dtDiscovery: "Discovery this week",
      dtDiscoveryPh: "Hypotheses, interviews, cheap tests",
      dtDelivery: "Delivery this week",
      dtDeliveryPh: "What discovery already confirmed and you are building",
      dtOneTeam: "One team owns both tracks",
      dtDecisions: "Discovery output is a decision, not just a story",
      dtFed: "Delivery input comes from discovery, not a stakeholder email",
      dtEmpty: "Fill both tracks with this week’s work.",
      dtDeliveryOnly: "You only have Delivery; learning will arrive after release.",
      dtDiscoveryOnly: "You only have Discovery; the product is not moving.",
      dtCaution: "Both tracks exist, but team health is incomplete.",
      dtOk: "Two healthy parallel tracks.",
      ostTitle: "Opportunity Solution Tree builder",
      ostLead: "One outcome, then customer opportunities, several solutions, and a cheap experiment.",
      ostOutcome: "Measurable outcome",
      ostOutcomePh: "e.g. first-week activation reaches 40%",
      ostOpp: "Customer opportunity",
      ostOppPh: "Unmet job or pain, not a feature",
      ostSol: "Solution",
      ostExp: "Smallest experiment",
      ostAddOpp: "Add opportunity",
      ostNeed: "Write an outcome and at least one opportunity with two solutions.",
      ostSolutionish: "Some opportunities read like solutions. Write the customer pain, not the feature.",
      ostOk: "Usable tree for the next meeting. Prune it again next week.",
      cdTitle: "Continuous Discovery habit tracker",
      cdLead: "Close the four weekly habits. The goal is a complete week, not a quarterly research project.",
      cdWeek: "Week starting",
      cdInterview: "At least one structured interview happened",
      cdNotes: "Interview notes",
      cdTrio: "Product, design, and engineering heard it together",
      cdHyp: "Hypothesis this week",
      cdHypPh: "If we change X, we will see Y in customer behavior",
      cdExp: "Cheap experiment",
      cdExpPh: "Prototype, fake door, or message test",
      cdNeed: "Close the habits one by one.",
      cdPartial: "The week is incomplete. Fill the empty habit first.",
      cdOk: "This week’s habits are complete."
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

  var SOLUTIONISH = /فیچر|دکمه|بسازیم|\bfeature\b|\bbutton\b|\bbuild a\b|\bapp\b/i;
  var VANITY_METRIC = /بازدید|دانلود|استوری بست|page ?views?|downloads?|story points?|registered users|ثبت.?نام خام|تعداد کاربر ثبت/i;

  function riceScore(reach, impact, confidence, effort) {
    var r = Number(reach);
    var i = Number(impact);
    var c = Number(confidence);
    var e = Number(effort);
    if (!(r > 0) || !(i > 0) || !(c > 0) || !(e > 0)) return null;
    var conf = c > 1 ? c / 100 : c;
    return Math.round((r * i * conf / e) * 10) / 10;
  }

  function riceRank(items) {
    return (items || [])
      .map(function (item) {
        return {
          name: trim(item && item.name),
          score: riceScore(item && item.reach, item && item.impact, item && item.confidence, item && item.effort)
        };
      })
      .filter(function (item) { return item.score !== null; })
      .sort(function (a, b) { return b.score - a.score; });
  }

  function aarrrRates(counts) {
    var list = counts || [];
    var steps = [];
    var i;
    for (i = 1; i < 4; i += 1) {
      var prev = Number(list[i - 1]);
      var curr = Number(list[i]);
      steps.push({
        from: i - 1,
        to: i,
        rate: prev > 0 && curr >= 0 ? Math.round((curr / prev) * 1000) / 10 : null
      });
    }
    var acq = Number(list[0]);
    var ref = Number(list[4]);
    return {
      steps: steps,
      referralShare: acq > 0 && ref >= 0 ? Math.round((ref / acq) * 1000) / 10 : null
    };
  }

  function aarrrBottleneck(counts) {
    var rates = aarrrRates(counts).steps.filter(function (step) { return step.rate !== null; });
    if (rates.length < 1) return { index: -1, rate: null };
    var weakest = rates[0];
    rates.forEach(function (step) {
      if (step.rate < weakest.rate) weakest = step;
    });
    return { index: weakest.from, rate: weakest.rate };
  }

  function heartCompleteness(rows) {
    var active = (rows || []).filter(function (row) { return row && row.on; });
    var complete = active.filter(function (row) {
      return trim(row.goal).length >= 8 && trim(row.signal).length >= 8 && trim(row.metric).length >= 4;
    });
    return {
      selected: active.length,
      complete: complete.length,
      ready: active.length > 0 && complete.length === active.length
    };
  }

  function northStarAssess(input) {
    var name = trim(input && input.name);
    var checks = (input && input.checks) || {};
    var inputs = ((input && input.inputs) || []).map(trim).filter(Boolean);
    var missing = ["value", "leading", "actionable", "inputs"].filter(function (key) { return !checks[key]; });
    var warnings = [];
    if (!name) warnings.push("empty");
    if (name && VANITY_METRIC.test(name)) warnings.push("vanity");
    if (inputs.length < 2) warnings.push("few-inputs");
    return {
      ready: Boolean(name) && missing.length === 0 && inputs.length >= 2 && warnings.indexOf("vanity") === -1,
      missing: missing,
      warnings: warnings,
      inputs: inputs
    };
  }

  function plgRecommendation(scores) {
    var list = scores || [];
    var answered = list.filter(function (n) { return typeof n === "number" && n > 0; });
    if (answered.length < 4) {
      return { verdict: "incomplete", average: average(list) };
    }
    var avg = average(list);
    var ttv = list[0] || 0;
    var selfServe = list[1] || 0;
    var verdict = "plg";
    if (ttv < 2 || avg < 2.5) verdict = "sales";
    else if (avg < 3.5 || ttv < 3 || selfServe < 3) verdict = "hybrid";
    return { verdict: verdict, average: avg };
  }

  function dualTrackBalance(state) {
    var discovery = trim(state && state.discovery).length;
    var delivery = trim(state && state.delivery).length;
    var health = [state && state.oneTeam, state && state.decisions, state && state.fedByDiscovery].filter(Boolean).length;
    var verdict = "ok";
    if (delivery >= 12 && discovery < 12) verdict = "delivery-only";
    else if (discovery >= 12 && delivery < 12) verdict = "discovery-only";
    else if (discovery < 12 && delivery < 12) verdict = "empty";
    else if (health < 3) verdict = "caution";
    return { verdict: verdict, health: health };
  }

  function ostAssess(tree) {
    var outcome = trim(tree && tree.outcome);
    var opps = ((tree && tree.opportunities) || []).filter(function (row) { return trim(row && row.name); });
    var flagged = opps.filter(function (row) { return SOLUTIONISH.test(row.name); });
    var withTwoSolutions = opps.filter(function (row) {
      return ((row.solutions || []).map(trim).filter(Boolean).length >= 2);
    });
    return {
      complete: outcome.length >= 8 && withTwoSolutions.length >= 1,
      opportunityCount: opps.length,
      flaggedSolutionish: flagged.length
    };
  }

  function discoveryHabitScore(state) {
    var points = 0;
    if (state && state.interview) points += 1;
    if (state && state.trio) points += 1;
    if (trim(state && state.hypothesis).length >= 12) points += 1;
    if (trim(state && state.experiment).length >= 12) points += 1;
    return { points: points, total: 4, percent: Math.round((points / 4) * 100) };
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

  function escapeHtml(value) {
    return String(value || "").replace(/[&<>"']/g, function (ch) {
      return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" })[ch];
    });
  }

  function bindCopyReset(root, c, getText, onReset) {
    root.querySelector("[data-action=\"copy\"]").addEventListener("click", function (event) {
      var text = getText();
      if (!text) return;
      copyText(text).then(function () { flashCopied(event.currentTarget, c); });
    });
    root.querySelector("[data-action=\"reset\"]").addEventListener("click", onReset);
  }

  function headHtml(c, title, lead) {
    return (
      "<div class=\"fw-tool-head\">" +
        "<span class=\"fw-tool-badge\">" + c.toolBadge + "</span>" +
        "<h3>" + title + "</h3>" +
        "<p>" + lead + "</p>" +
      "</div>"
    );
  }

  function emptyRiceItem() {
    return { name: "", reach: "", impact: "1", confidence: "80", effort: "" };
  }

  function emptyOstOpp() {
    return { name: "", solutions: ["", ""], experiment: "" };
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

  function mountRice(root, lang) {
    var c = copyFor(lang);
    var saved = loadState("rice", lang);
    var items = saved && saved.items && saved.items.length ? saved.items : [emptyRiceItem(), emptyRiceItem()];

    function impactSelect(index, value) {
      var opts = [["3", c.impactMassive], ["2", c.impactHigh], ["1", c.impactMedium], ["0.5", c.impactLow], ["0.25", c.impactMinimal]];
      return "<select data-k=\"impact\" data-i=\"" + index + "\">" + opts.map(function (opt) {
        return "<option value=\"" + opt[0] + "\"" + (String(value) === opt[0] ? " selected" : "") + ">" + opt[1] + "</option>";
      }).join("") + "</select>";
    }

    function rebuild() {
      root.querySelector("#fw-rice-list").innerHTML = items.map(function (item, index) {
        return (
          "<section class=\"fw-item\">" +
            "<div class=\"fw-item-head\"><strong>" + (index + 1) + "</strong>" +
              (items.length > 1 ? "<button type=\"button\" class=\"fw-tool-btn fw-tool-btn-ghost\" data-remove=\"" + index + "\">" + c.riceRemove + "</button>" : "") +
            "</div>" +
            "<label class=\"fw-tool-field\"><span>" + c.riceName + "</span><input type=\"text\" data-k=\"name\" data-i=\"" + index + "\" placeholder=\"" + escapeHtml(c.riceNamePh) + "\"></label>" +
            "<div class=\"fw-tool-grid fw-tool-grid-4\">" +
              "<label class=\"fw-tool-field\"><span>" + c.riceReach + "</span><input type=\"number\" min=\"0\" data-k=\"reach\" data-i=\"" + index + "\"></label>" +
              "<label class=\"fw-tool-field\"><span>" + c.riceImpact + "</span>" + impactSelect(index, item.impact) + "</label>" +
              "<label class=\"fw-tool-field\"><span>" + c.riceConfidence + "</span><input type=\"number\" min=\"1\" max=\"100\" data-k=\"confidence\" data-i=\"" + index + "\"></label>" +
              "<label class=\"fw-tool-field\"><span>" + c.riceEffort + "</span><input type=\"number\" min=\"0.1\" step=\"0.1\" data-k=\"effort\" data-i=\"" + index + "\"></label>" +
            "</div>" +
            "<p class=\"fw-item-score\" data-score=\"" + index + "\"></p>" +
          "</section>"
        );
      }).join("");
      items.forEach(function (item, index) {
        ["name", "reach", "confidence", "effort"].forEach(function (key) {
          var node = root.querySelector("[data-k=\"" + key + "\"][data-i=\"" + index + "\"]");
          if (node) node.value = item[key] || "";
        });
      });
      update();
    }

    function update() {
      items.forEach(function (item, index) {
        var score = riceScore(item.reach, item.impact, item.confidence, item.effort);
        var node = root.querySelector("[data-score=\"" + index + "\"]");
        if (node) node.textContent = score === null ? "" : ("RICE " + score);
      });
      var ranked = riceRank(items);
      var box = root.querySelector("#fw-rice-preview");
      if (!ranked.length) {
        box.className = "fw-tool-preview";
        box.textContent = c.riceEmpty;
      } else {
        box.className = "fw-tool-preview is-go";
        box.textContent = c.riceRank + "\n" + ranked.map(function (row, i) {
          return (i + 1) + ". " + (row.name || "—") + " — " + row.score;
        }).join("\n");
      }
      saveState("rice", lang, { items: items });
    }

    root.innerHTML =
      headHtml(c, c.riceTitle, c.riceLead) +
      "<div id=\"fw-rice-list\"></div>" +
      "<div class=\"fw-tool-actions\"><button type=\"button\" class=\"fw-tool-btn fw-tool-btn-secondary\" data-action=\"add-item\">" + c.riceAdd + "</button></div>" +
      "<div class=\"fw-tool-preview\" id=\"fw-rice-preview\"></div>" +
      actionBar(c);

    root.addEventListener("input", function (event) {
      var i = event.target.getAttribute("data-i");
      var k = event.target.getAttribute("data-k");
      if (i == null || !k) return;
      items[Number(i)][k] = event.target.value;
      update();
    });
    root.addEventListener("change", function (event) {
      var i = event.target.getAttribute("data-i");
      var k = event.target.getAttribute("data-k");
      if (i == null || !k) return;
      items[Number(i)][k] = event.target.value;
      update();
    });
    root.addEventListener("click", function (event) {
      var action = event.target.getAttribute("data-action");
      var remove = event.target.getAttribute("data-remove");
      if (action === "add-item") {
        items.push(emptyRiceItem());
        rebuild();
      }
      if (remove != null && items.length > 1) {
        items.splice(Number(remove), 1);
        rebuild();
      }
    });
    bindCopyReset(root, c, function () {
      return riceRank(items).map(function (row, i) {
        return (i + 1) + ". " + (row.name || "—") + " — " + row.score;
      }).join("\n");
    }, function () {
      items = [emptyRiceItem(), emptyRiceItem()];
      saveState("rice", lang, {});
      rebuild();
    });
    rebuild();
  }

  function mountAarrr(root, lang) {
    var c = copyFor(lang);
    var keys = ["acq", "act", "ret", "rev", "ref"];
    var labels = [c.aarrrAcq, c.aarrrAct, c.aarrrRet, c.aarrrRev, c.aarrrRef];
    var saved = loadState("aarrr", lang) || {};
    root.innerHTML =
      headHtml(c, c.aarrrTitle, c.aarrrLead) +
      "<div class=\"fw-tool-grid\">" + keys.map(function (key, index) {
        return "<label class=\"fw-tool-field\"><span>" + labels[index] + "</span><input id=\"fw-aarrr-" + key + "\" type=\"number\" min=\"0\"></label>";
      }).join("") + "</div>" +
      "<div id=\"fw-aarrr-bars\"></div>" +
      "<div class=\"fw-tool-preview\" id=\"fw-aarrr-preview\"></div>" +
      actionBar(c);

    keys.forEach(function (key) {
      if (saved[key] != null) root.querySelector("#fw-aarrr-" + key).value = saved[key];
    });

    function read() {
      return keys.map(function (key) { return Number(root.querySelector("#fw-aarrr-" + key).value || 0); });
    }

    function render() {
      var counts = read();
      var rates = aarrrRates(counts);
      var bottle = aarrrBottleneck(counts);
      var barRoot = root.querySelector("#fw-aarrr-bars");
      barRoot.innerHTML = rates.steps.map(function (step) {
        if (step.rate === null) return "";
        var width = Math.max(4, Math.min(100, step.rate));
        var weak = bottle.index === step.from ? " is-weak" : "";
        return "<div class=\"fw-funnel\"><span>" + labels[step.from] + " → " + labels[step.to] + "</span><div class=\"fw-funnel-track\"><i class=\"" + weak + "\" style=\"width:" + width + "%\"></i></div><strong>" + step.rate + "%</strong></div>";
      }).join("");
      var box = root.querySelector("#fw-aarrr-preview");
      if (bottle.index < 0) {
        box.className = "fw-tool-preview";
        box.textContent = c.aarrrNeed;
      } else {
        box.className = "fw-tool-preview is-caution";
        var extra = rates.referralShare !== null ? " · " + c.aarrrRef + " " + rates.referralShare + "%" : "";
        box.textContent = c.aarrrBottleneck + " " + labels[bottle.index] + " → " + labels[bottle.index + 1] + " (" + bottle.rate + "%)" + extra;
      }
      var data = {};
      keys.forEach(function (key, index) { data[key] = counts[index]; });
      saveState("aarrr", lang, data);
    }

    root.querySelectorAll("input").forEach(function (node) { node.addEventListener("input", render); });
    bindCopyReset(root, c, function () { return root.querySelector("#fw-aarrr-preview").textContent; }, function () {
      root.querySelectorAll("input").forEach(function (node) { node.value = ""; });
      saveState("aarrr", lang, {});
      render();
    });
    render();
  }

  function mountHeart(root, lang) {
    var c = copyFor(lang);
    var dims = [
      ["happiness", c.hHappiness],
      ["engagement", c.hEngagement],
      ["adoption", c.hAdoption],
      ["retention", c.hRetention],
      ["task", c.hTask]
    ];
    var saved = loadState("heart", lang) || {};
    root.innerHTML =
      headHtml(c, c.heartTitle, c.heartLead) +
      dims.map(function (dim, index) {
        return (
          "<section class=\"fw-opp-q\" data-heart=\"" + index + "\">" +
            "<label class=\"fw-check\"><input type=\"checkbox\" data-k=\"on\" data-i=\"" + index + "\"> <span>" + dim[1] + "</span></label>" +
            "<label class=\"fw-tool-field\"><span>" + c.heartGoal + "</span><textarea data-k=\"goal\" data-i=\"" + index + "\" rows=\"2\"></textarea></label>" +
            "<label class=\"fw-tool-field\"><span>" + c.heartSignal + "</span><input type=\"text\" data-k=\"signal\" data-i=\"" + index + "\"></label>" +
            "<label class=\"fw-tool-field\"><span>" + c.heartMetric + "</span><input type=\"text\" data-k=\"metric\" data-i=\"" + index + "\"></label>" +
          "</section>"
        );
      }).join("") +
      "<div class=\"fw-tool-preview\" id=\"fw-heart-preview\"></div>" +
      actionBar(c);

    function read() {
      return dims.map(function (dim, index) {
        return {
          id: dim[0],
          title: dim[1],
          on: !!root.querySelector("[data-k=\"on\"][data-i=\"" + index + "\"]").checked,
          goal: root.querySelector("[data-k=\"goal\"][data-i=\"" + index + "\"]").value,
          signal: root.querySelector("[data-k=\"signal\"][data-i=\"" + index + "\"]").value,
          metric: root.querySelector("[data-k=\"metric\"][data-i=\"" + index + "\"]").value
        };
      });
    }

    function render() {
      var rows = read();
      var rec = heartCompleteness(rows);
      var box = root.querySelector("#fw-heart-preview");
      box.className = "fw-tool-preview";
      if (!rec.selected) {
        box.textContent = c.heartNeed;
      } else if (!rec.ready) {
        box.classList.add("is-caution");
        box.textContent = c.heartPartial + " (" + rec.complete + "/" + rec.selected + ")";
      } else {
        box.classList.add("is-go");
        box.textContent = c.heartOk;
      }
      saveState("heart", lang, rows);
    }

    dims.forEach(function (_, index) {
      var row = saved[index] || {};
      var on = root.querySelector("[data-k=\"on\"][data-i=\"" + index + "\"]");
      var goal = root.querySelector("[data-k=\"goal\"][data-i=\"" + index + "\"]");
      var signal = root.querySelector("[data-k=\"signal\"][data-i=\"" + index + "\"]");
      var metric = root.querySelector("[data-k=\"metric\"][data-i=\"" + index + "\"]");
      if (row.on) on.checked = true;
      if (row.goal) goal.value = row.goal;
      if (row.signal) signal.value = row.signal;
      if (row.metric) metric.value = row.metric;
      [on, goal, signal, metric].forEach(function (node) {
        node.addEventListener("input", render);
        node.addEventListener("change", render);
      });
    });
    bindCopyReset(root, c, function () {
      return read().filter(function (row) { return row.on; }).map(function (row) {
        return row.title + "\n" + c.heartGoal + ": " + trim(row.goal) + "\n" + c.heartSignal + ": " + trim(row.signal) + "\n" + c.heartMetric + ": " + trim(row.metric);
      }).join("\n\n");
    }, function () {
      root.querySelectorAll("textarea, input[type=\"text\"]").forEach(function (node) { node.value = ""; });
      root.querySelectorAll("input[type=\"checkbox\"]").forEach(function (node) { node.checked = false; });
      saveState("heart", lang, []);
      render();
    });
    render();
  }

  function mountNorthStar(root, lang) {
    var c = copyFor(lang);
    var checkKeys = ["value", "leading", "actionable", "inputs"];
    var checkLabels = [c.nsValue, c.nsLeading, c.nsActionable, c.nsHasInputs];
    var gapLabels = { value: c.gapValue, leading: c.gapLeading, actionable: c.gapActionable, inputs: c.gapInputs };
    var saved = loadState("northstar", lang) || {};
    root.innerHTML =
      headHtml(c, c.nsTitle, c.nsLead) +
      field("fw-ns-name", c.nsName, c.nsNamePh, false) +
      checkKeys.map(function (key, index) {
        return "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-ns-" + key + "\"> <span>" + checkLabels[index] + "</span></label>";
      }).join("") +
      "<div class=\"fw-tool-grid\">" + [0, 1, 2].map(function (index) {
        return "<label class=\"fw-tool-field\"><span>" + c.nsInput + " " + (index + 1) + "</span><input type=\"text\" id=\"fw-ns-in-" + index + "\"></label>";
      }).join("") + "</div>" +
      "<div class=\"fw-tool-preview\" id=\"fw-ns-preview\"></div>" +
      "<p class=\"fw-tool-note\" id=\"fw-ns-note\"></p>" +
      actionBar(c);

    if (saved.name) root.querySelector("#fw-ns-name").value = saved.name;
    checkKeys.forEach(function (key) {
      if (saved.checks && saved.checks[key]) root.querySelector("#fw-ns-" + key).checked = true;
    });
    (saved.inputs || []).forEach(function (value, index) {
      var node = root.querySelector("#fw-ns-in-" + index);
      if (node) node.value = value;
    });

    function read() {
      return {
        name: root.querySelector("#fw-ns-name").value,
        checks: {
          value: root.querySelector("#fw-ns-value").checked,
          leading: root.querySelector("#fw-ns-leading").checked,
          actionable: root.querySelector("#fw-ns-actionable").checked,
          inputs: root.querySelector("#fw-ns-inputs").checked
        },
        inputs: [0, 1, 2].map(function (index) { return root.querySelector("#fw-ns-in-" + index).value; })
      };
    }

    function render() {
      var data = read();
      var rec = northStarAssess(data);
      var box = root.querySelector("#fw-ns-preview");
      var note = root.querySelector("#fw-ns-note");
      note.className = "fw-tool-note";
      box.className = "fw-tool-preview";
      if (!trim(data.name) || rec.warnings.indexOf("few-inputs") !== -1) {
        box.textContent = c.nsNeed;
      } else {
        box.textContent = trim(data.name) + (rec.inputs.length ? "\n" + rec.inputs.join(" · ") : "");
      }
      if (rec.warnings.indexOf("vanity") !== -1) {
        note.textContent = c.nsVanity;
        note.classList.add("is-warn");
        box.classList.add("is-nogo");
      } else if (rec.ready) {
        note.textContent = c.nsOk;
        note.classList.add("is-ok");
        box.classList.add("is-go");
      } else if (rec.missing.length) {
        note.textContent = c.nsGaps + " " + rec.missing.map(function (key) { return gapLabels[key]; }).join(lang === "en" ? ", " : "، ");
        note.classList.add("is-warn");
        box.classList.add("is-caution");
      } else {
        note.textContent = "";
      }
      saveState("northstar", lang, data);
    }

    root.querySelectorAll("input").forEach(function (node) {
      node.addEventListener("input", render);
      node.addEventListener("change", render);
    });
    bindCopyReset(root, c, function () {
      var data = read();
      return [trim(data.name)].concat(northStarAssess(data).inputs).filter(Boolean).join("\n");
    }, function () {
      root.querySelectorAll("input[type=\"text\"]").forEach(function (node) { node.value = ""; });
      root.querySelectorAll("input[type=\"checkbox\"]").forEach(function (node) { node.checked = false; });
      saveState("northstar", lang, {});
      render();
    });
    render();
  }

  function mountPlg(root, lang) {
    var c = copyFor(lang);
    var pillars = [c.plgTtv, c.plgSelf, c.plgLoop, c.plgData];
    var saved = loadState("plg", lang) || [];
    root.innerHTML =
      headHtml(c, c.plgTitle, c.plgLead) +
      pillars.map(function (label, index) {
        return (
          "<section class=\"fw-opp-q\">" +
            "<h4>" + (index + 1) + ". " + label + "</h4>" +
            "<label class=\"fw-tool-field fw-score\"><span>" + c.score + "</span>" +
              "<input id=\"fw-plg-" + index + "\" type=\"range\" min=\"0\" max=\"5\" step=\"1\" value=\"0\">" +
              "<em id=\"fw-plg-label-" + index + "\">" + c.unanswered + "</em></label>" +
          "</section>"
        );
      }).join("") +
      "<div class=\"fw-tool-preview\" id=\"fw-plg-preview\"></div>" +
      actionBar(c);

    pillars.forEach(function (_, index) {
      if (saved[index]) root.querySelector("#fw-plg-" + index).value = saved[index];
      root.querySelector("#fw-plg-" + index).addEventListener("input", render);
    });

    function read() {
      return pillars.map(function (_, index) { return Number(root.querySelector("#fw-plg-" + index).value || 0); });
    }

    function render() {
      var scores = read();
      scores.forEach(function (score, index) {
        root.querySelector("#fw-plg-label-" + index).textContent = score ? String(score) : c.unanswered;
      });
      var rec = plgRecommendation(scores);
      var box = root.querySelector("#fw-plg-preview");
      box.className = "fw-tool-preview";
      if (rec.verdict === "incomplete") {
        box.textContent = c.plgNeed;
      } else {
        var label = rec.verdict === "plg" ? c.plgReady : rec.verdict === "sales" ? c.plgSales : c.plgHybrid;
        box.classList.add(rec.verdict === "plg" ? "is-go" : rec.verdict === "sales" ? "is-nogo" : "is-caution");
        box.textContent = label + " · " + rec.average + "/5";
      }
      saveState("plg", lang, scores);
    }

    bindCopyReset(root, c, function () { return root.querySelector("#fw-plg-preview").textContent; }, function () {
      root.querySelectorAll("input[type=\"range\"]").forEach(function (node) { node.value = "0"; });
      saveState("plg", lang, []);
      render();
    });
    render();
  }

  function mountDualTrack(root, lang) {
    var c = copyFor(lang);
    var saved = loadState("dualtrack", lang) || {};
    root.innerHTML =
      headHtml(c, c.dtTitle, c.dtLead) +
      "<div class=\"fw-tool-grid fw-tool-grid-2\">" +
        field("fw-dt-discovery", c.dtDiscovery, c.dtDiscoveryPh, true) +
        field("fw-dt-delivery", c.dtDelivery, c.dtDeliveryPh, true) +
      "</div>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-dt-team\"> <span>" + c.dtOneTeam + "</span></label>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-dt-decisions\"> <span>" + c.dtDecisions + "</span></label>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-dt-fed\"> <span>" + c.dtFed + "</span></label>" +
      "<div class=\"fw-tool-preview\" id=\"fw-dt-preview\"></div>" +
      actionBar(c);

    if (saved.discovery) root.querySelector("#fw-dt-discovery").value = saved.discovery;
    if (saved.delivery) root.querySelector("#fw-dt-delivery").value = saved.delivery;
    if (saved.oneTeam) root.querySelector("#fw-dt-team").checked = true;
    if (saved.decisions) root.querySelector("#fw-dt-decisions").checked = true;
    if (saved.fedByDiscovery) root.querySelector("#fw-dt-fed").checked = true;

    function read() {
      return {
        discovery: root.querySelector("#fw-dt-discovery").value,
        delivery: root.querySelector("#fw-dt-delivery").value,
        oneTeam: root.querySelector("#fw-dt-team").checked,
        decisions: root.querySelector("#fw-dt-decisions").checked,
        fedByDiscovery: root.querySelector("#fw-dt-fed").checked
      };
    }

    function render() {
      var data = read();
      var rec = dualTrackBalance(data);
      var box = root.querySelector("#fw-dt-preview");
      var map = {
        empty: [c.dtEmpty, ""],
        "delivery-only": [c.dtDeliveryOnly, "is-nogo"],
        "discovery-only": [c.dtDiscoveryOnly, "is-caution"],
        caution: [c.dtCaution, "is-caution"],
        ok: [c.dtOk, "is-go"]
      };
      var view = map[rec.verdict] || map.empty;
      box.className = "fw-tool-preview " + view[1];
      box.textContent = view[0];
      saveState("dualtrack", lang, data);
    }

    root.querySelectorAll("input, textarea").forEach(function (node) {
      node.addEventListener("input", render);
      node.addEventListener("change", render);
    });
    bindCopyReset(root, c, function () {
      var data = read();
      return [root.querySelector("#fw-dt-preview").textContent, c.dtDiscovery + ":\n" + trim(data.discovery), c.dtDelivery + ":\n" + trim(data.delivery)].join("\n\n");
    }, function () {
      root.querySelectorAll("textarea").forEach(function (node) { node.value = ""; });
      root.querySelectorAll("input[type=\"checkbox\"]").forEach(function (node) { node.checked = false; });
      saveState("dualtrack", lang, {});
      render();
    });
    render();
  }

  function mountOst(root, lang) {
    var c = copyFor(lang);
    var saved = loadState("ost", lang);
    var state = {
      outcome: saved && saved.outcome || "",
      opportunities: saved && saved.opportunities && saved.opportunities.length ? saved.opportunities : [emptyOstOpp()]
    };

    function rebuild() {
      root.querySelector("#fw-ost-list").innerHTML = state.opportunities.map(function (row, index) {
        return (
          "<section class=\"fw-item\">" +
            "<div class=\"fw-item-head\"><strong>" + (index + 1) + "</strong>" +
              (state.opportunities.length > 1 ? "<button type=\"button\" class=\"fw-tool-btn fw-tool-btn-ghost\" data-remove=\"" + index + "\">" + c.riceRemove + "</button>" : "") +
            "</div>" +
            "<label class=\"fw-tool-field\"><span>" + c.ostOpp + "</span><input type=\"text\" data-k=\"name\" data-i=\"" + index + "\" placeholder=\"" + escapeHtml(c.ostOppPh) + "\"></label>" +
            "<div class=\"fw-tool-grid fw-tool-grid-2\">" +
              "<label class=\"fw-tool-field\"><span>" + c.ostSol + " 1</span><input type=\"text\" data-k=\"s0\" data-i=\"" + index + "\"></label>" +
              "<label class=\"fw-tool-field\"><span>" + c.ostSol + " 2</span><input type=\"text\" data-k=\"s1\" data-i=\"" + index + "\"></label>" +
            "</div>" +
            "<label class=\"fw-tool-field\"><span>" + c.ostExp + "</span><input type=\"text\" data-k=\"experiment\" data-i=\"" + index + "\"></label>" +
          "</section>"
        );
      }).join("");
      state.opportunities.forEach(function (row, index) {
        var name = root.querySelector("[data-k=\"name\"][data-i=\"" + index + "\"]");
        var s0 = root.querySelector("[data-k=\"s0\"][data-i=\"" + index + "\"]");
        var s1 = root.querySelector("[data-k=\"s1\"][data-i=\"" + index + "\"]");
        var exp = root.querySelector("[data-k=\"experiment\"][data-i=\"" + index + "\"]");
        if (name) name.value = row.name || "";
        if (s0) s0.value = (row.solutions || [])[0] || "";
        if (s1) s1.value = (row.solutions || [])[1] || "";
        if (exp) exp.value = row.experiment || "";
      });
      update();
    }

    function update() {
      var rec = ostAssess(state);
      var box = root.querySelector("#fw-ost-preview");
      var note = root.querySelector("#fw-ost-note");
      box.className = "fw-tool-preview";
      note.className = "fw-tool-note";
      if (!rec.complete) {
        box.textContent = c.ostNeed;
      } else {
        box.classList.add("is-go");
        box.textContent = trim(state.outcome) + " · " + rec.opportunityCount;
      }
      if (rec.flaggedSolutionish) {
        note.textContent = c.ostSolutionish;
        note.classList.add("is-warn");
        box.classList.remove("is-go");
        box.classList.add("is-caution");
      } else if (rec.complete) {
        note.textContent = c.ostOk;
        note.classList.add("is-ok");
      } else {
        note.textContent = "";
      }
      saveState("ost", lang, state);
    }

    root.innerHTML =
      headHtml(c, c.ostTitle, c.ostLead) +
      field("fw-ost-outcome", c.ostOutcome, c.ostOutcomePh, true) +
      "<div id=\"fw-ost-list\"></div>" +
      "<div class=\"fw-tool-actions\"><button type=\"button\" class=\"fw-tool-btn fw-tool-btn-secondary\" data-action=\"add-item\">" + c.ostAddOpp + "</button></div>" +
      "<div class=\"fw-tool-preview\" id=\"fw-ost-preview\"></div>" +
      "<p class=\"fw-tool-note\" id=\"fw-ost-note\"></p>" +
      actionBar(c);

    root.querySelector("#fw-ost-outcome").value = state.outcome;
    root.querySelector("#fw-ost-outcome").addEventListener("input", function (event) {
      state.outcome = event.target.value;
      update();
    });
    root.addEventListener("input", function (event) {
      var i = event.target.getAttribute("data-i");
      var k = event.target.getAttribute("data-k");
      if (i == null || !k) return;
      var row = state.opportunities[Number(i)];
      if (k === "s0" || k === "s1") {
        row.solutions = row.solutions || ["", ""];
        row.solutions[k === "s0" ? 0 : 1] = event.target.value;
      } else {
        row[k] = event.target.value;
      }
      update();
    });
    root.addEventListener("click", function (event) {
      var action = event.target.getAttribute("data-action");
      var remove = event.target.getAttribute("data-remove");
      if (action === "add-item") {
        state.opportunities.push(emptyOstOpp());
        rebuild();
      }
      if (remove != null && state.opportunities.length > 1) {
        state.opportunities.splice(Number(remove), 1);
        rebuild();
      }
    });
    bindCopyReset(root, c, function () {
      var lines = [trim(state.outcome)].concat(state.opportunities.filter(function (row) { return trim(row.name); }).map(function (row, index) {
        return (index + 1) + ". " + trim(row.name) + " → " + (row.solutions || []).map(trim).filter(Boolean).join(" / ") + (trim(row.experiment) ? " [" + trim(row.experiment) + "]" : "");
      }));
      return lines.join("\n");
    }, function () {
      state = { outcome: "", opportunities: [emptyOstOpp()] };
      root.querySelector("#fw-ost-outcome").value = "";
      saveState("ost", lang, {});
      rebuild();
    });
    rebuild();
  }

  function mountDiscovery(root, lang) {
    var c = copyFor(lang);
    var saved = loadState("discovery", lang) || {};
    root.innerHTML =
      headHtml(c, c.cdTitle, c.cdLead) +
      "<label class=\"fw-tool-field\"><span>" + c.cdWeek + "</span><input id=\"fw-cd-week\" type=\"date\"></label>" +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-cd-interview\"> <span>" + c.cdInterview + "</span></label>" +
      field("fw-cd-notes", c.cdNotes, "", true) +
      "<label class=\"fw-check\"><input type=\"checkbox\" id=\"fw-cd-trio\"> <span>" + c.cdTrio + "</span></label>" +
      field("fw-cd-hyp", c.cdHyp, c.cdHypPh, true) +
      field("fw-cd-exp", c.cdExp, c.cdExpPh, true) +
      "<div class=\"fw-tool-progress\"><span>" + c.progress + "</span><strong id=\"fw-cd-progress\">0%</strong></div>" +
      "<div class=\"fw-tool-preview\" id=\"fw-cd-preview\"></div>" +
      actionBar(c);

    if (saved.week) root.querySelector("#fw-cd-week").value = saved.week;
    if (saved.interview) root.querySelector("#fw-cd-interview").checked = true;
    if (saved.notes) root.querySelector("#fw-cd-notes").value = saved.notes;
    if (saved.trio) root.querySelector("#fw-cd-trio").checked = true;
    if (saved.hypothesis) root.querySelector("#fw-cd-hyp").value = saved.hypothesis;
    if (saved.experiment) root.querySelector("#fw-cd-exp").value = saved.experiment;

    function read() {
      return {
        week: root.querySelector("#fw-cd-week").value,
        interview: root.querySelector("#fw-cd-interview").checked,
        notes: root.querySelector("#fw-cd-notes").value,
        trio: root.querySelector("#fw-cd-trio").checked,
        hypothesis: root.querySelector("#fw-cd-hyp").value,
        experiment: root.querySelector("#fw-cd-exp").value
      };
    }

    function render() {
      var data = read();
      var rec = discoveryHabitScore(data);
      root.querySelector("#fw-cd-progress").textContent = rec.percent + "%";
      var box = root.querySelector("#fw-cd-preview");
      box.className = "fw-tool-preview";
      if (rec.percent === 0) {
        box.textContent = c.cdNeed;
      } else if (rec.percent < 100) {
        box.classList.add("is-caution");
        box.textContent = c.cdPartial + " (" + rec.points + "/" + rec.total + ")";
      } else {
        box.classList.add("is-go");
        box.textContent = c.cdOk;
      }
      saveState("discovery", lang, data);
    }

    root.querySelectorAll("input, textarea").forEach(function (node) {
      node.addEventListener("input", render);
      node.addEventListener("change", render);
    });
    bindCopyReset(root, c, function () {
      var data = read();
      return [data.week, root.querySelector("#fw-cd-preview").textContent, trim(data.notes), trim(data.hypothesis), trim(data.experiment)].filter(Boolean).join("\n");
    }, function () {
      root.querySelectorAll("textarea, input[type=\"text\"], input[type=\"date\"]").forEach(function (node) { node.value = ""; });
      root.querySelectorAll("input[type=\"checkbox\"]").forEach(function (node) { node.checked = false; });
      saveState("discovery", lang, {});
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
      if (name === "rice") mountRice(node, lang);
      if (name === "aarrr") mountAarrr(node, lang);
      if (name === "heart") mountHeart(node, lang);
      if (name === "northstar") mountNorthStar(node, lang);
      if (name === "plg") mountPlg(node, lang);
      if (name === "dualtrack") mountDualTrack(node, lang);
      if (name === "ost") mountOst(node, lang);
      if (name === "discovery") mountDiscovery(node, lang);
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
    riceScore: riceScore,
    riceRank: riceRank,
    aarrrRates: aarrrRates,
    aarrrBottleneck: aarrrBottleneck,
    heartCompleteness: heartCompleteness,
    northStarAssess: northStarAssess,
    plgRecommendation: plgRecommendation,
    dualTrackBalance: dualTrackBalance,
    ostAssess: ostAssess,
    discoveryHabitScore: discoveryHabitScore,
    mountAll: mountAll
  };
});
