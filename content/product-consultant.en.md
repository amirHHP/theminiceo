---
title: "Product Advisory"
date: 2019-02-01
layout: hextra-home
description: "Expert product advisory for startups and businesses — from idea to growth. First 30 minutes free."
---

<style>
/* ───────── Landing Page Styles ───────── */
.lp-hero{background:linear-gradient(135deg,#eef2ff 0%,#e0e7ff 50%,#f0f4ff 100%);padding:4rem 1rem;text-align:center;border-radius:0 0 2rem 2rem}
.dark .lp-hero{background:linear-gradient(135deg,#1e1b4b 0%,#1e3a5f 50%,#0f172a 100%)}
.lp-badge{display:inline-flex;align-items:center;gap:.4rem;background:#dcfce7;color:#166534;padding:.35rem .85rem;border-radius:2rem;font-size:.8rem;font-weight:600;margin-bottom:1.5rem}
.dark .lp-badge{background:#064e3b;color:#86efac}
.lp-title{font-size:2.25rem;font-weight:800;background:linear-gradient(135deg,#1e3a5f,#4f46e5);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.3;margin-bottom:1rem}
.dark .lp-title{background:linear-gradient(135deg,#93c5fd,#a78bfa);-webkit-background-clip:text;background-clip:text}
@media(min-width:768px){.lp-title{font-size:3rem}.lp-hero{padding:5rem 2rem}}
.lp-subtitle{color:#4b5563;font-size:1.1rem;max-width:640px;margin:0 auto 2rem;line-height:1.8}
.dark .lp-subtitle{color:#9ca3af}
.lp-btn{display:inline-flex;align-items:center;gap:.5rem;padding:.875rem 2rem;border-radius:.75rem;font-weight:700;font-size:1.05rem;text-decoration:none;transition:all .2s;cursor:pointer}
.lp-btn-primary{background:#4f46e5;color:#fff;box-shadow:0 4px 14px rgba(79,70,229,.3)}
.lp-btn-primary:hover{background:#4338ca;transform:translateY(-2px);box-shadow:0 6px 20px rgba(79,70,229,.4);color:#fff}
.lp-btn-ghost{color:#4f46e5;border:2px solid #c7d2fe;background:transparent;margin-top:.75rem}
.dark .lp-btn-ghost{color:#a5b4fc;border-color:#4338ca}
.lp-btn-ghost:hover{background:#eef2ff;color:#4f46e5}
.dark .lp-btn-ghost:hover{background:#312e81}
.lp-stats{display:flex;justify-content:center;gap:2.5rem;margin-top:3rem;flex-wrap:wrap}
.lp-stat-num{font-size:2rem;font-weight:800;color:#4f46e5}
.dark .lp-stat-num{color:#a5b4fc}
.lp-stat-lbl{font-size:.85rem;color:#6b7280;margin-top:.15rem}
/* Section */
.lp-section{padding:3.5rem 1rem;max-width:72rem;margin:0 auto}
.lp-sec-title{font-size:1.75rem;font-weight:700;text-align:center;margin-bottom:.5rem;color:#111827}
.dark .lp-sec-title{color:#f3f4f6}
.lp-sec-sub{text-align:center;color:#6b7280;max-width:580px;margin:0 auto 2.5rem;font-size:1rem;line-height:1.7}
/* Challenge cards */
.lp-cards{display:grid;grid-template-columns:1fr;gap:1.25rem}
@media(min-width:768px){.lp-cards{grid-template-columns:repeat(3,1fr)}}
.lp-card{background:#fff;border:1px solid #e5e7eb;border-radius:1rem;padding:2rem 1.5rem;text-align:center;transition:all .25s;text-decoration:none;color:inherit;display:block}
.dark .lp-card{background:#1f2937;border-color:#374151}
.lp-card:hover{box-shadow:0 10px 30px rgba(0,0,0,.08);transform:translateY(-4px);border-color:#4f46e5}
.lp-card-icon{font-size:2.5rem;margin-bottom:.75rem}
.lp-card-title{font-size:1.15rem;font-weight:700;margin-bottom:.5rem;color:#111827}
.dark .lp-card-title{color:#f9fafb}
.lp-card-desc{color:#6b7280;font-size:.92rem;line-height:1.7}
/* Pricing */
.lp-pricing{display:grid;grid-template-columns:1fr;gap:1.5rem;align-items:start}
@media(min-width:768px){.lp-pricing{grid-template-columns:repeat(3,1fr)}}
.lp-price-card{background:#fff;border:2px solid #e5e7eb;border-radius:1.25rem;padding:2rem 1.5rem;position:relative;transition:all .25s}
.dark .lp-price-card{background:#1f2937;border-color:#374151}
.lp-price-card.pop{border-color:#4f46e5;box-shadow:0 8px 30px rgba(79,70,229,.12)}
@media(min-width:768px){.lp-price-card.pop{transform:scale(1.04)}}
.lp-price-badge{position:absolute;top:-.7rem;left:50%;transform:translateX(-50%);background:#4f46e5;color:#fff;padding:.2rem 1rem;border-radius:2rem;font-size:.78rem;font-weight:700;white-space:nowrap}
.lp-price-name{font-size:1.35rem;font-weight:700;text-align:center;margin-bottom:.35rem;color:#111827}
.dark .lp-price-name{color:#f9fafb}
.lp-price-desc{text-align:center;color:#6b7280;font-size:.88rem;margin-bottom:1.25rem}
.lp-price-amount{text-align:center;font-size:1.75rem;font-weight:800;color:#059669;margin-bottom:1.25rem}
.dark .lp-price-amount{color:#34d399}
.lp-price-list{list-style:none;padding:0;margin:0 0 1.25rem}
.lp-price-list li{padding:.45rem 0;border-bottom:1px solid #f3f4f6;color:#374151;font-size:.92rem;display:flex;align-items:flex-start;gap:.5rem}
.dark .lp-price-list li{border-color:#374151;color:#d1d5db}
.lp-price-list li::before{content:"✓";color:#059669;font-weight:700;flex-shrink:0}
.lp-price-fit{background:#f9fafb;border-radius:.75rem;padding:1rem;margin-bottom:1.25rem;font-size:.85rem}
.dark .lp-price-fit{background:#111827}
.lp-price-fit strong{display:block;color:#6b7280;margin-bottom:.35rem;font-size:.8rem}
.lp-price-fit ul{list-style:none;padding:0;margin:0}
.lp-price-fit li{color:#6b7280;padding:.15rem 0;display:flex;align-items:flex-start;gap:.4rem}
.lp-price-fit li::before{content:"–";flex-shrink:0}
.lp-pcta{display:block;text-align:center;padding:.75rem;border-radius:.75rem;font-weight:700;text-decoration:none;transition:all .2s;font-size:.95rem}
.lp-pcta-p{background:#4f46e5;color:#fff}
.lp-pcta-p:hover{background:#4338ca;color:#fff}
.lp-pcta-s{background:#f3f4f6;color:#374151;border:1px solid #e5e7eb}
.dark .lp-pcta-s{background:#374151;color:#e5e7eb;border-color:#4b5563}
.lp-pcta-s:hover{background:#e5e7eb}
/* Process steps */
.lp-steps{display:grid;grid-template-columns:repeat(2,1fr);gap:1.5rem}
@media(min-width:768px){.lp-steps{grid-template-columns:repeat(4,1fr)}}
.lp-step{text-align:center}
.lp-step-n{width:3rem;height:3rem;background:#eef2ff;color:#4f46e5;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.2rem;margin:0 auto .75rem;border:2px solid #c7d2fe}
.dark .lp-step-n{background:#312e81;border-color:#4f46e5;color:#a5b4fc}
.lp-step-t{font-weight:700;font-size:.95rem;margin-bottom:.35rem;color:#111827}
.dark .lp-step-t{color:#f9fafb}
.lp-step-d{font-size:.85rem;color:#6b7280;line-height:1.6}
/* Service details (accordion) */
.lp-acc{margin-bottom:1rem}
.lp-acc summary{display:flex;align-items:center;gap:.75rem;padding:1.1rem 1.25rem;background:#fff;border:1px solid #e5e7eb;border-radius:.85rem;cursor:pointer;font-weight:700;font-size:1.05rem;color:#111827;list-style:none;transition:all .2s}
.dark .lp-acc summary{background:#1f2937;border-color:#374151;color:#f9fafb}
.lp-acc summary:hover{border-color:#4f46e5;background:#fafbff}
.dark .lp-acc summary:hover{background:#253047}
.lp-acc summary::-webkit-details-marker{display:none}
.lp-acc summary::after{content:"▾";margin-left:auto;color:#9ca3af;transition:transform .2s;font-size:.85rem}
.lp-acc[open]>summary::after{transform:rotate(180deg)}
.lp-acc[open]>summary{border-radius:.85rem .85rem 0 0;border-bottom-color:transparent}
.lp-acc-body{padding:1.25rem 1.5rem;border:1px solid #e5e7eb;border-top:none;border-radius:0 0 .85rem .85rem;background:#fafbfc}
.dark .lp-acc-body{background:#111827;border-color:#374151}
.lp-acc-body h4{font-size:1rem;font-weight:700;color:#4338ca;margin:1.1rem 0 .4rem}
.dark .lp-acc-body h4{color:#818cf8}
.lp-acc-body h4:first-child{margin-top:0}
.lp-acc-body ul{list-style:none;padding:0;margin:0}
.lp-acc-body li{padding:.3rem 0;color:#4b5563;font-size:.9rem;display:flex;align-items:flex-start;gap:.4rem}
.dark .lp-acc-body li{color:#d1d5db}
.lp-acc-body li::before{content:"◇";color:#4f46e5;font-size:.6rem;margin-top:.35rem;flex-shrink:0}
/* Trust */
.lp-trust-box{background:linear-gradient(135deg,#eef2ff,#f0fdf4);border-radius:1.25rem;padding:2.5rem 1.5rem;text-align:center;margin-top:1rem}
.dark .lp-trust-box{background:linear-gradient(135deg,#1e1b4b,#064e3b)}
.lp-trust-box p{color:#4b5563;font-size:.95rem;max-width:500px;margin:.75rem auto 0;line-height:1.7}
.dark .lp-trust-box p{color:#9ca3af}
.lp-guarantee{display:inline-flex;align-items:center;gap:.4rem;background:#dcfce7;color:#166534;padding:.4rem 1rem;border-radius:2rem;font-weight:600;font-size:.88rem;margin-top:1.5rem}
.dark .lp-guarantee{background:#064e3b;color:#86efac}
/* Final CTA */
.lp-final{background:linear-gradient(135deg,#312e81 0%,#4f46e5 100%);border-radius:1.25rem;padding:3.5rem 1.5rem;text-align:center;color:#fff;margin-top:1rem}
.lp-final h2{font-size:1.75rem;font-weight:800;margin-bottom:.75rem;color:#fff}
@media(min-width:768px){.lp-final h2{font-size:2.25rem}}
.lp-final p{font-size:1.05rem;opacity:.88;max-width:480px;margin:0 auto 2rem;line-height:1.7}
.lp-btn-w{display:inline-flex;align-items:center;gap:.5rem;padding:.875rem 2rem;background:#fff;color:#312e81;border-radius:.75rem;font-weight:700;font-size:1.05rem;text-decoration:none;transition:all .2s;box-shadow:0 4px 14px rgba(0,0,0,.15)}
.lp-btn-w:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.2);color:#312e81}
.lp-final-email{margin-top:1.5rem;font-size:.9rem;opacity:.7}
.lp-final-email a{color:#c7d2fe;text-decoration:underline}
/* Mid CTA */
.lp-mid-cta{text-align:center;padding:2rem 1rem;background:#fafbff;border-radius:1rem;margin:1rem 0}
.dark .lp-mid-cta{background:#1e1b4b}
.lp-mid-cta p{color:#6b7280;margin-bottom:1rem;font-size:.95rem}
.dark .lp-mid-cta p{color:#9ca3af}
/* Divider */
.lp-divider{border:none;border-top:1px solid #e5e7eb;margin:0}
.dark .lp-divider{border-color:#374151}
</style>

<!-- ═══════════════════ HERO ═══════════════════ -->
<div class="lp-hero">
  <div style="max-width:48rem;margin:0 auto">
    <div class="lp-badge">🎯 First 30 minutes free</div>
    <h1 class="lp-title">Build and grow your product with confidence</h1>
    <p class="lp-subtitle">The TMC Product Advisory team stands by you from idea stage through growth and scaling, with a custom-tailored proposal. Over 7 years of hands-on experience building and growing digital products.</p>
    <div>
      <a href="https://zeeg.me/amirhp/30min" target="_blank" rel="noopener" class="lp-btn lp-btn-primary">Book a free consultation →</a>
    </div>
    <div style="margin-top:.75rem">
      <a href="#pricing" class="lp-btn lp-btn-ghost">View advisory packages ↓</a>
    </div>
    <div class="lp-stats">
      <div><div class="lp-stat-num">50+</div><div class="lp-stat-lbl">Advisory projects</div></div>
      <div><div class="lp-stat-num">7+</div><div class="lp-stat-lbl">Years of experience</div></div>
      <div><div class="lp-stat-num">20+</div><div class="lp-stat-lbl">Industries served</div></div>
    </div>
  </div>
</div>

<!-- ═══════════════════ CHALLENGES ═══════════════════ -->
<div class="lp-section">
  <h2 class="lp-sec-title">Which path is yours?</h2>
  <p class="lp-sec-sub">Every business has unique needs. We provide services tailored to whatever stage you are in.</p>
  <div class="lp-cards">
    <a href="#services-idea" class="lp-card">
      <div class="lp-card-icon">💡</div>
      <div class="lp-card-title">I have an idea — where do I start?</div>
      <div class="lp-card-desc">You have an idea but don't know where to begin? We help you turn it into an actionable, executable plan.</div>
    </a>
    <a href="#services-growth" class="lp-card">
      <div class="lp-card-icon">📈</div>
      <div class="lp-card-title">My product isn't growing</div>
      <div class="lp-card-desc">You've raised capital but growth has stalled? We identify weak points and design a sustainable growth path.</div>
    </a>
    <a href="#services-enterprise" class="lp-card">
      <div class="lp-card-icon">🏢</div>
      <div class="lp-card-title">I need a new enterprise product</div>
      <div class="lp-card-desc">You're a large organization and want to build a new product without the hassle? Our expert team paves the way.</div>
    </a>
  </div>
</div>

<hr class="lp-divider">

<!-- ═══════════════════ PRICING ═══════════════════ -->
<div class="lp-section" id="pricing">
  <h2 class="lp-sec-title">Idea review & advisory packages</h2>
  <p class="lp-sec-sub">Pick one of the packages below for a quick start. After the initial review, a custom proposal will be provided for ongoing collaboration.</p>
  <div class="lp-pricing">

    <!-- Pack 1 -->
    <div class="lp-price-card">
      <div class="lp-price-name">Idea-stage Pack</div>
      <div class="lp-price-desc">Best for an initial look at ideas</div>
      <div class="lp-price-amount">12,000,000 Toman</div>
      <ul class="lp-price-list">
        <li>Pitch deck and review file</li>
        <li>Two-year financial plan</li>
        <li>Product roadmap</li>
      </ul>
      <div class="lp-price-fit">
        <strong>Suitable for ideas that:</strong>
        <ul>
          <li>Are simple with no complex twist</li>
          <li>Have existing domestic examples</li>
          <li>Don't need a technical backlog</li>
        </ul>
      </div>
      <a href="https://zeeg.me/amirhp/30min" target="_blank" rel="noopener" class="lp-pcta lp-pcta-s">Start with a free consultation</a>
    </div>

    <!-- Pack 2 (Popular) -->
    <div class="lp-price-card pop">
      <div class="lp-price-badge">⭐ Most Popular</div>
      <div class="lp-price-name">Professional Pack</div>
      <div class="lp-price-desc">Best for complex products</div>
      <div class="lp-price-amount">18,000,000 Toman</div>
      <ul class="lp-price-list">
        <li>Pitch deck and review file</li>
        <li>Two-year financial plan</li>
        <li>Product roadmap and backlog for technical implementation</li>
      </ul>
      <div class="lp-price-fit">
        <strong>Suitable for ideas that:</strong>
        <ul>
          <li>Have complex flows and revenue models</li>
          <li>Have existing domestic examples</li>
          <li>Need a backlog for implementation</li>
        </ul>
      </div>
      <a href="https://zeeg.me/amirhp/30min" target="_blank" rel="noopener" class="lp-pcta lp-pcta-p">Book a free consultation →</a>
    </div>

    <!-- Pack 3 -->
    <div class="lp-price-card">
      <div class="lp-price-name">Global Special Pack</div>
      <div class="lp-price-desc">Best for international ideas</div>
      <div class="lp-price-amount">27,000,000 Toman</div>
      <ul class="lp-price-list">
        <li>Pitch deck and review file</li>
        <li>Two-year financial plan</li>
        <li>Product roadmap and backlog for technical implementation</li>
      </ul>
      <div class="lp-price-fit">
        <strong>Suitable for ideas that:</strong>
        <ul>
          <li>Need foreign market research</li>
          <li>Have complex flows and revenue models</li>
          <li>May not have domestic examples</li>
          <li>Need a technical backlog</li>
        </ul>
      </div>
      <a href="https://zeeg.me/amirhp/30min" target="_blank" rel="noopener" class="lp-pcta lp-pcta-s">Start with a free consultation</a>
    </div>

  </div>
</div>

<!-- ═══════════════════ MID CTA ═══════════════════ -->
<div class="lp-section" style="padding-top:0">
  <div class="lp-mid-cta">
    <p>Not sure which package is right for you? We'll guide you in a free consultation.</p>
    <a href="https://zeeg.me/amirhp/30min" target="_blank" rel="noopener" class="lp-btn lp-btn-primary">Book a free session →</a>
  </div>
</div>

<hr class="lp-divider">

<!-- ═══════════════════ PROCESS ═══════════════════ -->
<div class="lp-section">
  <h2 class="lp-sec-title">How does it work?</h2>
  <p class="lp-sec-sub">In 4 simple steps, from first contact to execution, we're with you.</p>
  <div class="lp-steps">
    <div class="lp-step">
      <div class="lp-step-n">1</div>
      <div class="lp-step-t">Book free consultation</div>
      <div class="lp-step-d">30-minute online call to learn about your project and needs</div>
    </div>
    <div class="lp-step">
      <div class="lp-step-n">2</div>
      <div class="lp-step-t">Review & analysis</div>
      <div class="lp-step-d">Deep analysis of your idea, market, competitors, and growth opportunities</div>
    </div>
    <div class="lp-step">
      <div class="lp-step-n">3</div>
      <div class="lp-step-t">Custom proposal</div>
      <div class="lp-step-d">A tailored collaboration plan designed for your specific needs</div>
    </div>
    <div class="lp-step">
      <div class="lp-step-n">4</div>
      <div class="lp-step-t">Start collaboration</div>
      <div class="lp-step-d">Execute the plan with ongoing support and regular reporting</div>
    </div>
  </div>
</div>

<hr class="lp-divider">

<!-- ═══════════════════ SERVICES DETAIL ═══════════════════ -->
<div class="lp-section" id="services">
  <h2 class="lp-sec-title">Specialized product advisory services</h2>
  <p class="lp-sec-sub">Our services differ based on the stage your business is in. Click each section for details.</p>

  <!-- 1. Ideas -->
  <details class="lp-acc" id="services-idea">
    <summary>💡 Services for new ideas — from idea to product</summary>
    <div class="lp-acc-body">
      <p style="color:#6b7280;margin-bottom:1rem;font-size:.92rem;line-height:1.7">We help you walk the path of launching a new idea at a <strong>much lower financial and time cost</strong>. Before building a product, you need to be sure the market actually needs it.</p>

      <h4>🔍 Maturing the idea</h4>
      <ul>
        <li>Full idea review (origins, competitive advantages)</li>
        <li>Market space and target audience analysis</li>
        <li>Competitive landscape review</li>
        <li>Revenue model analysis</li>
        <li>Final proposal for the project owner</li>
      </ul>

      <h4>🎨 Product design</h4>
      <ul>
        <li>Complete list of product capabilities</li>
        <li>Feature phasing for market entry</li>
        <li>Sketches, wireframes, and UI design</li>
        <li>MVP planning for real-world testing</li>
        <li>Final proposal with UI/UX and release phasing</li>
      </ul>

      <h4>⚙️ Development collaboration</h4>
      <ul>
        <li>Writing complete user stories</li>
        <li>Setting up task management tools</li>
        <li>Sprint planning</li>
        <li>Attending planning and demo sessions</li>
        <li>Implementing analytics tools</li>
      </ul>

      <h4>🚀 Going to market</h4>
      <ul>
        <li>Marketing planning and cost estimation</li>
        <li>Preparing marketing materials</li>
        <li>Helping launch campaigns</li>
        <li>Reviewing results and suggesting improvements</li>
      </ul>

      <h4>📊 Product growth</h4>
      <ul>
        <li>Analyzing current user behavior</li>
        <li>Reviewing feature adoption</li>
        <li>Finding weak points</li>
        <li>Growth plans (engagement, retention, etc.)</li>
      </ul>
    </div>
  </details>

  <!-- 2. Growth -->
  <details class="lp-acc" id="services-growth">
    <summary>📈 Services for startups in the growth stage</summary>
    <div class="lp-acc-body">
      <p style="color:#6b7280;margin-bottom:1rem;font-size:.92rem;line-height:1.7">If you've been in the market for a while and are struggling with product growth, you first need a professional team to identify weak points and present an improvement plan.</p>

      <h4>🔎 Identifying weak points</h4>
      <ul>
        <li>Initial and complete review of the current product</li>
        <li>Accessing user performance data</li>
        <li>Usability tests with various users</li>
        <li>Direct interviews with current users</li>
      </ul>

      <h4>⚡ Identifying quick wins</h4>
      <ul>
        <li>Closer product review</li>
        <li>A/B testing</li>
        <li>Building MVPs to test improvements</li>
      </ul>

      <h4>📊 Capability performance analysis</h4>
      <ul>
        <li>User experience review</li>
        <li>User drop-off analysis at different steps</li>
        <li>Deciding whether to remove ineffective features</li>
      </ul>

      <h4>👥 User behavior analysis</h4>
      <ul>
        <li>LTV per user</li>
        <li>Signup-to-customer conversion gap</li>
        <li>Churn points</li>
        <li>User usage habits</li>
      </ul>

      <h4>🎯 Increasing engagement, retention & sales</h4>
      <ul>
        <li>Running relevant tests</li>
        <li>Marketing collaboration on communication channels</li>
        <li>Revenue model review and optimization</li>
      </ul>

      <h4>🧭 Product positioning</h4>
      <ul>
        <li>Current position mapping</li>
        <li>Market position landscape</li>
      </ul>

      <h4>👨‍💼 Building the product team</h4>
      <ul>
        <li>Role needs analysis</li>
        <li>Improving processes</li>
        <li>Team structuring</li>
        <li>Hiring support and job descriptions</li>
      </ul>
    </div>
  </details>

  <!-- 3. Enterprise -->
  <details class="lp-acc" id="services-enterprise">
    <summary>🏢 Services for large businesses</summary>
    <div class="lp-acc-body">
      <p style="color:#6b7280;margin-bottom:1rem;font-size:.92rem;line-height:1.7">If you hold a large market share and need team structuring, new market entry, or product improvement, our specialized services are for you.</p>

      <h4>🌍 Discovering new markets</h4>
      <ul>
        <li>Reviewing recurring user patterns</li>
        <li>Analyzing competitor side-business strategies</li>
      </ul>

      <h4>👨‍💼 Improving team structure</h4>
      <ul>
        <li>Reviewing current product team setup</li>
        <li>Finding the right structure</li>
      </ul>

      <h4>📋 Backlog management</h4>
      <ul>
        <li>Prioritization support</li>
        <li>Sound customer feedback collection</li>
        <li>Feature request decision framework</li>
        <li>Backlog management tools</li>
      </ul>

      <h4>🔎 Identifying weak points</h4>
      <ul>
        <li>Complete product review</li>
        <li>Performance data access</li>
        <li>Usability testing</li>
        <li>User interviews</li>
      </ul>

      <h4>🎯 Increasing engagement & sales</h4>
      <ul>
        <li>Relevant testing</li>
        <li>Communication channel optimization</li>
        <li>Revenue model review</li>
      </ul>

      <h4>🎓 Specialist workshops</h4>
      <ul>
        <li>Implementing Scrum in the product team</li>
        <li>Training product manager interns</li>
        <li>Writing user stories</li>
        <li>Requirements prioritization</li>
        <li>Lean product management</li>
        <li>Product capability analysis</li>
      </ul>
    </div>
  </details>
</div>

<!-- ═══════════════════ TRUST ═══════════════════ -->
<div class="lp-section" style="padding-top:0">
  <div class="lp-trust-box">
    <div class="lp-stats" style="margin-top:0">
      <div><div class="lp-stat-num">50+</div><div class="lp-stat-lbl">Successful projects</div></div>
      <div><div class="lp-stat-num">7+</div><div class="lp-stat-lbl">Years of experience</div></div>
      <div><div class="lp-stat-num">20+</div><div class="lp-stat-lbl">Industries served</div></div>
    </div>
    <p>Every collaboration proposal is uniquely designed to match your needs. We guarantee you'll receive tangible, actionable output.</p>
    <div class="lp-guarantee">✅ First 30 minutes absolutely free</div>
  </div>
</div>

<!-- ═══════════════════ FINAL CTA ═══════════════════ -->
<div class="lp-section">
  <div class="lp-final">
    <h2>Ready to change your product's growth trajectory?</h2>
    <p>Book a free 30-minute consultation right now and talk to our team about your product challenges.</p>
    <a href="https://zeeg.me/amirhp/30min" target="_blank" rel="noopener" class="lp-btn-w">Book a free consultation →</a>
    <div class="lp-final-email">Or email us: <a href="mailto:hi@theminiceo.ir">hi@theminiceo.ir</a></div>
  </div>
</div>
