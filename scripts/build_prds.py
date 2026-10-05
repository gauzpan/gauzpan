#!/usr/bin/env python3
"""Builds one Double Diamond case-study page per project into docs/prds/.

Content is distilled from each project's PRD (kept private under spec/PRDs).
Rules: only facts stated in the PRD, figures as cited there, no personal
names of officials/teammates, and no credentials or demo logins.

Usage:  python3 scripts/build_prds.py
"""
import html
import os
import re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "prds")
SITE = "https://gauzpan.github.io/gauzpan/"


def fmt(s):
    """Escape, then turn **bold** into <b>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s, quote=False))


P = []  # projects, in the same order as the README

# --------------------------------------------------------------------------
P.append(dict(
    slug="rideinsync", name="RideInSync", domain="Mobility", color="--acc",
    tagline="One live map for the whole ride: every rider tracked, every route shared, help one tap away.",
    chips=["Buildathon winner · ReThink System Cohort 8", "PWA + Android", "Voice-first"],
    demo=("http://rideinsync.in", "Live demo"),
    why=[
        "**An unserved safety problem.** When the pack splits at a junction or a rider slips behind, no one knows until someone pulls over.",
        "**A large, growing community.** Group riding has a real coordination and safety gap that today's tools don't touch.",
        "**The tools in use can't see the group.** Riders coordinate over chat threads and each rides with their own turn-by-turn navigation. Neither shows the operational state of the group.",
    ],
    stats_title="The pack in numbers",
    stats=[("5–10", "bikes in a typical pack", "Product brief"),
           ("4", "rider roles, each with a different blind spot", "Product brief"),
           ("0", "taps needed to signal: voice-first", "Product brief"),
           ("1", "shared live map for route, riders and SOS", "Product brief")],
    discover=[
        "Group rides run on **WhatsApp threads** plus each rider's own navigation app.",
        "Neither shows whether the group is whole, who dropped back, or who stopped.",
        "A hazard on the road means **hand signals**; a split at a junction means guessing.",
        "Four roles feel it differently: captain, lead, sweep and regular rider.",
    ],
    problem="Group riders have no shared view of the ride's live state, so splits, stragglers and emergencies go unnoticed until someone stops.",
    insights=[
        ("Four roles, four blind spots", "The captain has no single workspace; the lead can't see who is falling behind; the sweep can't tell who is missing or where they were last seen; a regular rider has no one-action way to signal or call for help."),
        ("Safety has to be hands-free", "A rider who drops back panics, and it is unsafe to touch the phone. That drives voice-first signals, one-tap SOS and minimal touch while riding."),
        ("Speak the pack's language", "Status reads in terms the pack already uses: intact, behind, stopped, stale."),
    ],
    develop_lead="Five jobs that grow out of one shared live state:",
    develop=[
        "**Discover:** find a trip or a group to join",
        "**Organize:** route, roles and stops",
        "**Coordinate:** live position, signals, regroup",
        "**Protect:** consent-based sharing, SOS",
        "**Remember:** a shared record of the trip",
    ],
    develop_note="**Explored for later:** soft pace warnings, emergency-contact notify with location link, proximity SOS, in-ride voice chat, offline mesh fallback, weather and traffic alerts.",
    decision="**The wedge:** ship the whole ride, not a screenshot. Discovery, safety and memory grow from the same shared live state.",
    deliver_lead="The MVP runs a real ride end to end: create, share a code, approve riders, watch the pack move, signal by voice, raise an SOS.",
    deliver=[
        "**Live ops map** with lead, co-lead, sweep and rider pins, live status, and a last-known marker with timestamp",
        "**One-tap SOS** that alerts the group and the lead at once, by tap or voice",
        "**Voice-first signals:** say “sync”, then hazard, regroup or pit stop, with a signal log",
        "**Structured rides:** a route with shared stops, synced live when the lead changes the plan",
        "**Fast join** by code or QR, lead-approved, with capacity per ride",
        "**Judge-ready demo:** a guided tour and a one-tap simulated pack so the map moves without phones",
    ],
    deliver_note="Stack: React + TypeScript PWA, Google Maps, Web Push, Web Speech, Supabase Postgres and realtime. Design: dark-first, a single lime accent, voice-first.",
    validate=[
        "The brief has **no survey or interview data**. The evidence here is observation of how packs coordinate today.",
        "In-ride voice chat is pending a spike on quality and battery at riding speed.",
        "Pace nudges would be tunable per ride, never a forced stop or removal.",
    ],
))

# --------------------------------------------------------------------------
P.append(dict(
    slug="civicrouter", name="CivicRouter", domain="GovTech", color="--teal",
    tagline="Map a citizen's location and issue to the right public officials, then scaffold a well-tagged post they publish themselves.",
    chips=["Hackathon MVP", "Bengaluru + Indore", "RAG + deterministic routing"],
    demo=("https://karma-setu.vercel.app/", "Live demo"),
    why=[
        "**Citizens can't find the right person.** They know the CM or the Mayor, not their ward-level officer. There is no single directory a layperson can read.",
        "**Officials get reputational noise.** Indiscriminate tagging on social media drowns the people who could act.",
        "**The accountability loop breaks at the matching step.** Nothing downstream works if the wrong person is tagged.",
    ],
    stats_title="Evidence from the civic landscape",
    stats=[("129", "official records across 2 cities (61 Bengaluru, 68 Indore)", "PRD data coverage"),
           ("198→~369", "wards in Bengaluru's re-delimitation after BBMP was dissolved", "Sept 2025 restructuring, per PRD"),
           ("85 vs 0", "elected ward corporators: Indore vs Bengaluru", "PRD city comparison"),
           ("13 / 129", "records carry an X handle, by design", "Invented handles are worse than none")],
    discover=[
        "**Surface complaint:** “I posted about the overflowing drain in my gully, tagged the municipal corporation, and nothing happened.”",
        "**Root causes:** an identity gap, a channel mismatch (portals bind officials but feel slow, so people default to X), tagging dilution (stale or wrong-tier handles), and structural churn (BBMP replaced by the Greater Bengaluru Authority and five corporations).",
        "**Existing options fall short:** CPGRAMS and state portals have an incomprehensible department taxonomy; civic-tech orgs are city-specific; crowdsourced directories are stale; department handles are scattered.",
    ],
    problem="Citizens face high friction discovering the right official for a hyperlocal issue, and officials face reputational noise from indiscriminate tagging. The accountability loop breaks at the matching step.",
    insights=[
        ("The right person is usually more local than people assume", "A gully drain tagged at a Union minister gets zero traction. The ward officer is the one who can act."),
        ("Same complaint, different correct answer", "“No water in my tap” routes to BWSSB in Bengaluru but to IMC Water Works in Indore, which has no water parastatal. A hard-coded rule would misroute every Indore water complaint."),
        ("Routing is the product, not the name", "81 of 129 records have no published name, yet a designation, helpline and portal are still actionable. Org charts also churn, so any directory hard-coded to one city is wrong within a year."),
    ],
    develop_lead="Choices that shaped the solution space:",
    develop=[
        "**Job chosen:** discovery plus post-drafting. Accountability tracking (did the official respond?) deferred to v2",
        "**Two entry points:** a deterministic lookup that always works, and a RAG chatbot as the delighter",
        "**Two cities, not one:** one city is a directory; two proves routing generalises. Indore was picked because it is structurally unlike Bengaluru",
        "**Neighbourhood dropdown, not pincode:** pincodes map poorly to ward boundaries",
        "**Out of scope:** accounts, pan-India expansion, crowdsourced updates, full localisation",
    ],
    develop_note="",
    decision="**City-agnostic by design:** the tier model (ward, zone, city, parastatal) is universal; routing rules live in data, so adding a city is a data-only change.",
    deliver_lead="One results page with three actions for the citizen:",
    deliver=[
        "**Amplify:** matched officials' X handles with last-verified date and a confidence badge",
        "**Drafted post:** editable, 280-character counter, opens X with the text pre-filled",
        "**File officially:** the grievance portal link plus the helpline for that city",
        "**Guardrails:** handles come only from retrieved records, city and location are mandatory, cities are never mixed, drafts are always editable",
        "**Trust:** a last-verified date, source and data confidence on every record; a monthly refresh opens a review PR and never pushes to main",
    ],
    deliver_note="Stack: Next.js, LangChain.js, OpenAI embeddings and GPT-4o-mini, JSON data files, X intent URL (no OAuth, no auto-posting). The test that matters: the same “no water” complaint must route differently in each city.",
    validate=[
        "Officials transfer constantly, so staleness is the standing risk: verification dates, confidence badges and a “Report stale” button.",
        "The chatbot is the delighter; the deterministic form is the shippable product.",
        "Government sensitivities: citizen-empowerment framing, an assertive-professional tone, and the citizen posts themselves.",
    ],
))

# --------------------------------------------------------------------------
P.append(dict(
    slug="charaka-ai", name="Charaka AI", domain="Healthtech · Edtech", color="--blue",
    tagline="A mobile-first AI learning coach that teaches physicians, nurses and care coordinators to use generative AI safely inside real clinical workflows.",
    chips=["Mobile-first", "Physician-only MVP slice built", "Live app · local only"],
    demo=None,
    why=[
        "**Adoption has outrun training.** 81% of physicians now use AI professionally (38% in 2023), yet 92% want more training and 27% report none (AMA 2026 survey, as cited in the PRD).",
        "**The stakes are highest in healthcare.** Misusing AI on patient data, or trusting an unverified summary, carries compliance, safety and liability consequences.",
        "**The workforce maths make the case.** WHO projects an 11.1M health-worker shortfall by 2030, so any tool that safely returns minutes to patient care is valuable.",
    ],
    stats_title="Evidence: adoption without competence",
    stats=[("81%", "of physicians use AI professionally, up from 38% in 2023", "AMA 2026, via PRD"),
           ("27%", "report no AI training from any source", "AMA 2026, via PRD"),
           ("65.7%", "prefer hands-on exercises tied to job tasks", "Survey, n=35"),
           ("51%", "cite “too much content, no clear path” as top frustration", "Survey, n=35")],
    discover=[
        "**Competitive scan:** institutional CME (AMA Ed Hub, Harvard, Mayo), CE and LMS platforms, hospital compliance training, cross-industry AI courses and AI point-tools. None combines clinical workflow specificity with hands-on practice.",
        "**Market:** the global CME/CE spend is roughly $9.4–10.5B in 2025, heading to $14.6–18.4B by 2030.",
        "**Primary survey (n=35):** time-poor knowledge workers, only two in medicine. It validates the behaviour pattern; healthcare specifics are triangulated with AMA data.",
    ],
    problem="Healthcare professionals are expected to use AI, but the learning on offer is generic, long-format and doesn't build trust. The gap is structured practice under safety constraints, not awareness or access.",
    insights=[
        ("Using it isn't understanding it", "80% of respondents use generative AI regularly, yet about 40% say they are guessing."),
        ("Not short of content, short of a path", "51% name “too much content, no clear path” as their biggest frustration, more than triple the runner-up (17%)."),
        ("Doing beats watching", "65.7% want hands-on exercises tied to their job; five-minute bite-sized lessons on their own rank near the bottom (17.1%)."),
    ],
    develop_lead="Choices that shaped the solution space:",
    develop=[
        "**Why healthcare:** the pain showed up across every profession surveyed, so it was a choice: the gap is measurable, the stakes highest, the ROI clearest",
        "**Three roles explored:** physician, nurse, care coordinator",
        "**Safety-visible design:** physicians want a feedback channel (88%), privacy assurances (87%), a say in adoption (85%) and EHR integration (84%)",
        "**B2B2C distribution:** 88.6% of respondents self-pay nothing, so institutional sponsorship is the primary revenue assumption",
    ],
    develop_note="",
    decision="**The bet:** structured, safe, role-specific practice closes the gap. More content does not.",
    deliver_lead="A physician-only MVP slice, built and demoable:",
    deliver=[
        "**Five tabs:** Today, Journey, Practice, Resources, Progress",
        "**Six-card lesson player:** objective, concept, good-vs-bad, insight, try-it sandbox, recap",
        "**Practice loop** on a synthetic research paper with LLM output and a deterministic four-dimension rubric: clinical question, evidence framing, verification demand, uncertainty flag",
        "**Safe by construction:** the sandbox is synthetic-only, with no field that can take patient-identifiable data",
        "**Skill ladder:** Learner, Enabled, Proficient, Expert. A 17-tool AI Toolkit is near-done",
    ],
    deliver_note="North star: the share of active users who report applying an AI skill to real work in the last 7 days. Targets to validate: first-session completion at least 70%, 7-day retention at least 40%. Time in app is deliberately not optimised.",
    validate=[
        "The survey is general (n=35, two medical respondents); healthcare precision comes from AMA data.",
        "That practice on synthetic data transfers to real cases is an assumption to test early.",
        "Employers co-funding access is assumed, and content must refresh as fast as the tools change.",
    ],
))

# --------------------------------------------------------------------------
P.append(dict(
    slug="agent-management-portal", name="Agent Management Portal", domain="B2B SaaS · Education", color="--coral",
    tagline="One system of record for onboarding, verifying and governing international education agents, built for small colleges.",
    chips=["Australia", "ESOS Act + National Code", "Live app · local only"],
    demo=None,
    why=[
        "**Compliance is mandatory, the process is manual.** The ESOS Act and National Code already require verified agents, documented decisions, current marketing materials and an audit trail. Institutes meet them through email and spreadsheets.",
        "**A rule change raised the stakes.** Australia's 1 April 2026 ban on onshore transfer commissions put agent compliance in the spotlight, and TEQSA mandates auditable agent processes.",
        "**Existing tools leave gaps.** Point solutions are priced out of reach of tertiary colleges and smaller universities, and are heavy to implement.",
    ],
    stats_title="Evidence: a regulated, underserved segment",
    stats=[("~4,000", "registered training organisations in Australia", "ASQA, via PRD"),
           ("206", "registered higher-education providers at 30 June 2025", "TEQSA, via PRD"),
           ("95%", "of higher-ed providers registered to teach international students", "Australian Government, via PRD"),
           ("200–400", "small colleges with active agents: the first target", "PRD sizing assumption")],
    discover=[
        "**Started broad, with vendor onboarding.** An organisation checks 3–10 systems (five on average) before a decision, and at least half still onboard on email, Excel and ERP.",
        "**Every tool touches a piece, none owns the vendor end to end.** Procurement suites, ERP, contract and risk tools rarely talk to each other.",
        "**Customer discovery:** the same vendor evidence is collected and re-validated again and again, despite digital platforms.",
        "**Primary research:** three interviews with admissions, compliance, marketing and finance staff at small education providers.",
    ],
    problem="Institutes manage international agents across the student system, the PRISMS portal, email and spreadsheets, none of which talk to each other. Staff re-key data by hand and reconcile commissions against spreadsheets, creating regulatory, operational and financial exposure.",
    insights=[
        ("“Most applications start as an email.”", "Admissions has to work out whether everything needed is actually there. Result: incomplete applications and repeated follow-ups."),
        ("“Knowing whether the documents are still valid.”", "Compliance names this as the biggest issue. Document validation and expiry tracking are done by hand."),
        ("“Checking names against another spreadsheet.”", "Finance reconciles commissions by hand when the invoice arrives. Commission integrity means paying agents only for students who genuinely enrolled and cleared the rules."),
    ],
    develop_lead="Three opportunity areas, judged by how contested each already is:",
    develop=[
        "**Core vendor onboarding:** a deep red ocean. Large suites and mid-market tools own it, and switching is hard",
        "**Education institutes managing agents:** a blue ocean. Existing players are partial, costly for small colleges, and heavy to implement",
        "**Restaurants and small suppliers:** a red ocean, cheap and commoditised, with thin willingness to pay",
    ],
    develop_note="",
    decision="**Chosen:** the agent-management segment, competing on compliance enforcement, end-to-end workflow and commission reconciliation.",
    deliver_lead="Two connected sides on the same data, from application to active agent:",
    deliver=[
        "**Agents apply with no login;** the application email becomes the single address for everything after",
        "**Staff queue** with per-document verification, referee notes hidden from the agent, and a mandatory reason on every approval or rejection",
        "**Five-stage tracker** with a 30-day SLA, a compliance checklist and a tracked agreement",
        "**Toolkit gated:** marketing materials can only be sent once the agent is Active",
        "**Audit-ready:** an append-only activity log, a live exportable compliance report and staff two-factor login",
    ],
    deliver_note="Goals: cut onboarding from weeks to days and hold a 90%+ agent compliance score. Metric: the share of agents registered on PRISMS within 30 days of signing.",
    validate=[
        "Only three interviews and limited access to administrators, so pain points aren't yet validated across institution types and geographies.",
        "Assumed: most target colleges have no agent-management system and rely on spreadsheets and email.",
        "The referee non-response timeout is not yet defined.",
    ],
))

# --------------------------------------------------------------------------
P.append(dict(
    slug="lifeloom", name="LifeLoom", domain="Silver economy", color="--acc",
    tagline="Companionship as preventative emotional care: a verified human companion and a voice AI companion, matched to each older adult.",
    chips=["Human + AI companions", "English · Hindi · Kannada"],
    demo=("https://lifeloom-prototype.netlify.app/", "Prototype"),
    why=[
        "**Families are dispersing.** One in five older adults in India lives alone or only with a spouse, while children increasingly live away.",
        "**Loneliness is common and under-served.** 13–15% report frequent loneliness, about 37% among those living alone, often despite adequate physical care.",
        "**It is a health issue, not only a feeling.** Globally, isolation is associated with a 50% higher dementia risk, 32% higher stroke risk and 20% more emergency visits (as cited in the PRD).",
    ],
    stats_title="Evidence: an ageing country, living apart",
    stats=[("140M→230M", "older adults today to 2036, 20% of India by 2050", "Secondary research"),
           ("~37%", "of elders living alone report frequent loneliness", "LASI Wave-1, via PRD"),
           ("7 of 8", "stakeholder groups interviewed raised loneliness as an unmet need", "Primary interviews"),
           ("41%", "of Indian elders own a smartphone", "Secondary research")],
    discover=[
        "**Ecosystem mapped:** about 140M older people; adult children who decide and pay, often from another city; a 4.3M caregiver shortfall with around 40% annual attrition; providers, hospitals, insurers and regulators.",
        "**Market view:** senior living, home healthcare, subscriptions, companionship apps, medicine, emergency and insurance. The market sells services, not outcomes.",
        "**Primary research:** 30–45 minute interviews with older adults, family and formal caregivers, clinicians and providers across eight stakeholder groups.",
        "**Companionship today** is “activity, not attachment”. The category leader GenWise shut down in December 2025 despite claiming 30 lakh users.",
    ],
    problem="Elder care is built for physical and clinical needs. As families spread out, older adults spend long stretches alone, with little companionship or sense of purpose, even when their physical care is adequate.",
    insights=[
        ("The buyer isn't the user", "Adult children decide and pay from elsewhere. They are buying relief from guilt and risk as much as care, so the product must create value for both."),
        ("The unmet need is being known, not being busy", "The personas' frustrations: activities that fill time without meaning, and being surrounded by people yet known by none."),
        ("Trust breaks when quality varies", "Reviews of care services keep flagging reliability, accountability and continuity, which makes verified, trained companions essential."),
    ],
    develop_lead="Five opportunity areas, ranked on evidence strength and market size:",
    develop=[
        "Emotional isolation, loss of purpose and dignity",
        "Trust and verifiability of caregivers",
        "An untrained and unretained caregiving workforce",
        "Fragmented coordination, with the adult child as unpaid integrator",
        "No continuous record of the older adult",
    ],
    develop_note="**Narrowed to two:** isolation versus the workforce shortage. The workforce needs long-term training and regulation, so companionship won.",
    decision="**Companionship over a caregiver marketplace:** a marketplace solves the transaction of finding care, not the experience of ageing. Trade-offs chosen: depth over scale, quality over quantity, trust over speed.",
    deliver_lead="Two kinds of companion, and the elder always chooses:",
    deliver=[
        "**Weaver:** a verified, trained human companion matched on personality, interests and language",
        "**SageAI:** a voice AI that always says it is an AI and nudges the elder toward family and their Weaver",
        "**The elder picks their Weaver.** Nobody is auto-assigned, and the adult child can only shortlist",
        "**Low-tech onboarding:** setup over a phone call, in English, Hindi or Kannada",
        "**Peace of mind without surveillance:** a wellbeing digest with no raw conversations, plus an always-on SOS for defined crisis events",
    ],
    deliver_note="Success is measured by meaningful, recurring relationships and emotional outcomes, not app usage. Sizing basis in the PRD: 600,000 growing to 1.2M paying users.",
    validate=[
        "Will families pay to fix loneliness when it is named as part of care? Willingness to pay and churn need primary validation.",
        "Will an older adult accept company from a paid stranger? It may be easiest right after a hospital stay.",
        "Can enough high-quality companions be recruited, verified and retained across locations and languages?",
    ],
))

# --------------------------------------------------------------------------
P.append(dict(
    slug="tooti-gullak", name="Tooti Gullak", domain="Fintech · Gig economy", color="--teal",
    tagline="A savings bridge for gig workers who earn digitally every day but live payout to payout.",
    chips=["Discovery PRD", "~30 worker interviews", "Prototype"],
    demo=None,
    why=[
        "**A large, growing workforce.** About 12M gig workers today, projected at 23.5M by 2030 and 61.6M by 2047.",
        "**Digital income, but no wealth path.** Payouts are digital and regular, yet the financial products on offer are built for short-term liquidity, not savings.",
        "**The risk lands on households.** The worker's household absorbs every cost shock without ever appearing on the app screen.",
    ],
    stats_title="Evidence: income without a safety net",
    stats=[("~12M→23.5M", "gig workers, FY25 to 2030", "Economic Survey, NITI Aayog"),
           ("~69%", "earn ₹1,500 or less a day", "Secondary research"),
           ("42%", "of surveyed gig workers have accident insurance", "Secondary research"),
           ("80%", "of interviewed workers carry higher-interest debt", "Primary, ~30 interviews")],
    discover=[
        "**Ecosystem mapped** across five tiers: workers, platforms, consumers, merchants and worker households, plus capital providers, intermediaries, regulators and civil society.",
        "**Trends:** gig work is shifting from side income to livelihood; workers multi-app; payouts are digital; EV rentals change daily costs.",
        "**Primary research:** about 30 semi-structured interviews with Tier-1 delivery, home-service and quick-commerce workers aged 18–40.",
        "**Observed:** roughly ₹7,000 a month on fuel, around ₹180 a day for EV rental and charging, and informal borrowing as the first resort in an emergency.",
    ],
    problem="Despite regular, digitised income, gig workers are trapped in short-term survival cycles. There is no accessible financial bridge from daily cash-flow management and debt reliance to long-term resilience.",
    insights=[
        ("Technology is used to lend, not to save", "Fintechs auto-deduct from payouts for loan repayments and EV rental fees, but no app uses the same mechanism to help workers save."),
        ("They tried saving, then it broke", "One interviewee built ₹10,000 on a micro-savings app over a year, then withdrew it all in a debt emergency. Withdrawal charges added to the frustration."),
        ("One job, three enabling jobs", "Permission to save (the money must feel liquid), a reason to save (named goals with visible progress) and less friction (trust and simplicity)."),
    ],
    develop_lead="Three lenses on gig workers led to three opportunity areas:",
    develop=[
        "**Welfare and finance:** scheme awareness, and products for unstable income",
        "**Cross-platform:** wage visibility and credit inclusion",
        "**Infrastructure:** portable credit identity, and workers as trained first responders",
        "**Existing players:** early-wage and credit apps solve debt, not wealth; micro-investing apps put the whole behaviour burden on the worker",
    ],
    develop_note="**Primary persona:** a stabilised full-time worker earning ₹25,000–30,000 a month with a small, consistent surplus. Not the first target: new or low-rated entrants and debt-carrying migrants.",
    decision="**Converged on** a long-term savings bridge, since credit and short-term liquidity are already crowded.",
    deliver_lead="The solution hypothesis from the research synthesis:",
    deliver=[
        "**Automatic by default:** sweep a small portion of every payout aside, with no active decision or discipline",
        "**Reversible:** saved money must feel as liquid and easy to withdraw as cash",
        "**Goal-based:** route savings into a named goal with visible progress",
        "**Small and frequent:** deductions aligned to daily or weekly payouts, not large monthly contributions",
        "**In the worker's language,** starting with one instrument such as an FD or RD",
    ],
    deliver_note="Opportunity sizing basis: about 12M workers, 60% adoption from interviews, and a conservative 10% subscription rate benchmarked on competitors.",
    validate=[
        "Assumed: speed, trust and simplicity drive where workers borrow, more than the interest rate.",
        "Assumed: small, frequent deductions feel more acceptable than large monthly contributions.",
        "Open: actual weekly spend, 3–5 year goals, and what an “ideal” product sounds like in workers' own words.",
    ],
))

# --------------------------------------------------------------------------
CSS = """
:root{--bg:#0D1117;--navy:#0B1220;--card:#111A2C;--line:#1E2A40;--line2:#33415C;--fg:#E8ECF4;--soft:#D3D9E4;--sub:#B4BDCE;--mut:#8C97AD;--acc:#F5A524;--acc2:#FFC861;--teal:#3FB8AF;--blue:#8AB4FF;--coral:#FF8A65;
--head:'Space Grotesk',system-ui,sans-serif;--body:'IBM Plex Sans',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--fg);font:400 15px/1.55 var(--body)}
a{color:var(--acc);text-decoration:none}a:hover{color:var(--acc2);text-decoration:underline}
a:focus-visible{outline:2px solid var(--acc2);outline-offset:3px;border-radius:4px}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px}
.top{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:18px 0;font:400 12.5px var(--mono);color:var(--mut)}
.top a{color:var(--mut)}.top a:hover{color:var(--acc)}
.hero{padding:10px 0 26px}
.kick{font:400 12px var(--mono);color:var(--mut);text-transform:uppercase;letter-spacing:.09em}
h1{margin:6px 0 8px;font:600 clamp(34px,6vw,54px)/1.04 var(--head);letter-spacing:-.025em}
.tag{display:inline-block;font:400 11.5px var(--mono);padding:3px 10px;border-radius:999px;color:var(--navy);background:var(--c);margin-right:8px;vertical-align:middle}
.tagline{margin:10px 0 14px;max-width:68ch;color:var(--sub);font-size:17px}
.chips{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chips span{font:400 12px var(--mono);color:var(--soft);border:1px solid var(--line2);border-radius:6px;padding:3px 9px}
.btn{display:inline-flex;align-items:center;height:34px;padding:0 14px;border-radius:7px;background:var(--acc);color:var(--navy)!important;font:500 12.5px var(--mono);text-transform:uppercase;letter-spacing:.05em}
.btn:hover{background:var(--acc2);text-decoration:none}
.eyebrow{font:400 11px var(--mono);letter-spacing:.09em;text-transform:uppercase;color:var(--mut);margin:0 0 10px}
.grid2{display:grid;grid-template-columns:1.15fr 1fr;gap:16px;margin-bottom:26px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px}
.why ul{margin:0;padding:0;list-style:none;display:grid;gap:12px}
.why li{color:var(--sub);font-size:14.5px;padding-left:16px;position:relative}
.why li::before{content:"";position:absolute;left:0;top:.62em;width:7px;height:7px;border-radius:2px;background:var(--acc)}
b{color:var(--fg);font-weight:600}
.stats{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stat{background:var(--navy);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:flex;flex-direction:column;gap:3px}
.stat .n{font:700 clamp(24px,3.2vw,32px)/1.05 var(--head);color:var(--acc);letter-spacing:-.02em}
.stat .l{font-size:13px;color:var(--soft);line-height:1.35}
.stat .s{font:400 10.5px var(--mono);color:var(--mut);margin-top:auto;padding-top:4px}
.dd{margin:6px 0 14px}.dd svg{width:100%;height:auto;display:block}
.dd text{font-family:var(--head)}
.phases{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;align-items:stretch}
.ph{background:var(--card);border:1px solid var(--line);border-top:3px solid var(--pc);border-radius:12px;padding:18px 18px 20px;display:flex;flex-direction:column;gap:12px}
.ph .no{font:400 11px var(--mono);color:var(--pc);letter-spacing:.08em;text-transform:uppercase}
.ph h2{margin:0;font:600 20px/1.15 var(--head);letter-spacing:-.01em}
.ph .q{margin:-6px 0 0;color:var(--mut);font-size:13px}
.ph ul{margin:0;padding:0;list-style:none;display:grid;gap:9px}
.ph li{font-size:13.5px;color:var(--sub);padding-left:14px;position:relative;line-height:1.5}
.ph li::before{content:"";position:absolute;left:0;top:.6em;width:5px;height:5px;border-radius:50%;background:var(--pc)}
.lead{margin:0;font-size:13.5px;color:var(--soft)}
.problem{background:rgba(63,184,175,.09);border:1px solid rgba(63,184,175,.45);border-radius:10px;padding:12px 14px;font:500 14px/1.45 var(--head);color:var(--fg)}
.problem small{display:block;font:400 10.5px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--teal);margin-bottom:5px}
.ins{display:grid;gap:10px}
.insight{background:var(--navy);border:1px solid var(--line);border-left:3px solid var(--acc);border-radius:8px;padding:10px 12px}
.insight small{display:block;font:400 10px var(--mono);letter-spacing:.09em;color:var(--acc);text-transform:uppercase}
.insight strong{display:block;font:600 14px/1.3 var(--head);margin:2px 0 4px;color:var(--fg)}
.insight p{margin:0;font-size:13px;color:var(--sub);line-height:1.5}
.decision{background:rgba(245,165,36,.09);border:1px solid rgba(245,165,36,.45);border-radius:10px;padding:11px 13px;font-size:13.5px;color:var(--soft);margin-top:auto}
.note{font-size:12.5px;color:var(--mut);margin:0}
.foot{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:26px 0 8px}
.val ul{margin:0;padding:0;list-style:none;display:grid;gap:9px}
.val li{font-size:13.5px;color:var(--sub);padding-left:16px;position:relative}
.val li::before{content:"?";position:absolute;left:0;top:0;font:600 12px var(--mono);color:var(--acc)}
.more{display:flex;flex-wrap:wrap;gap:8px}
.more a{font:400 12.5px var(--mono);border:1px solid var(--line2);border-radius:6px;padding:5px 10px;color:var(--soft)}
.more a:hover{border-color:var(--acc);color:var(--acc);text-decoration:none}
.src{color:var(--mut);font:400 11.5px var(--mono);padding:14px 0 40px}
code{font:400 .88em var(--mono);color:var(--acc)}
@media(max-width:1020px){.phases{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:760px){.wrap{padding:0 16px}.grid2,.foot{grid-template-columns:1fr}.phases{grid-template-columns:1fr}.dd{display:none}.top{flex-direction:column;align-items:flex-start}}
@media print{@page{size:A4 landscape;margin:8mm}body{background:#fff;color:#111;font-size:10px}.top,.more,.dd{display:none}
.card,.ph,.stat,.insight,.problem,.decision{background:#fff!important;border-color:#ccc!important;color:#111}
b,h1,h2,.insight strong,.problem{color:#000}.ph li,.insight p,.why li,.lead,.tagline,.stat .l{color:#333}.phases{grid-template-columns:repeat(4,1fr);gap:8px}.ph,.card{padding:10px}.ph h2{font-size:14px}.ph li,.insight p{font-size:9px}h1{font-size:30px}}
"""


def diamond():
    t, s = "#3FB8AF", "#F5A524"
    return f"""<div class="dd"><svg viewBox="0 0 1000 150" role="img" aria-label="Double Diamond: Discover and Define make up the problem space; Develop and Deliver make up the solution space">
<text x="247" y="14" text-anchor="middle" font-size="11" fill="{t}" letter-spacing="2" style="font-family:var(--mono)">PROBLEM SPACE</text>
<text x="749" y="14" text-anchor="middle" font-size="11" fill="{s}" letter-spacing="2" style="font-family:var(--mono)">SOLUTION SPACE</text>
<polygon points="4,86 247,28 490,86 247,144" fill="{t}" fill-opacity=".10" stroke="{t}" stroke-width="2" stroke-linejoin="round"/>
<polygon points="508,86 751,28 994,86 751,144" fill="{s}" fill-opacity=".10" stroke="{s}" stroke-width="2" stroke-linejoin="round"/>
<line x1="247" y1="28" x2="247" y2="144" stroke="{t}" stroke-opacity=".5" stroke-dasharray="4 5"/>
<line x1="751" y1="28" x2="751" y2="144" stroke="{s}" stroke-opacity=".5" stroke-dasharray="4 5"/>
<path d="M492 86h14m-5-5l5 5-5 5" fill="none" stroke="#8C97AD" stroke-width="1.6"/>
<g fill="#E8ECF4" font-weight="600" font-size="20" text-anchor="middle">
<text x="135" y="84">Discover</text><text x="371" y="84">Define</text><text x="639" y="84">Develop</text><text x="875" y="84">Deliver</text></g>
<g font-size="11" text-anchor="middle" fill="#8C97AD" style="font-family:var(--mono)">
<text x="135" y="104">diverge</text><text x="371" y="104">converge</text><text x="639" y="104">diverge</text><text x="875" y="104">converge</text></g>
</svg></div>"""


def lis(items):
    return "".join(f"<li>{fmt(i)}</li>" for i in items)


def render(p):
    c = f"var({p['color']})"
    stats = "".join(
        f'<div class="stat"><span class="n">{html.escape(n)}</span><span class="l">{fmt(l)}</span><span class="s">{html.escape(s)}</span></div>'
        for n, l, s in p["stats"])
    ins = "".join(
        f'<div class="insight"><small>Insight 0{i}</small><strong>{html.escape(t)}</strong><p>{fmt(d)}</p></div>'
        for i, (t, d) in enumerate(p["insights"], 1))
    btn = f'<a class="btn" href="{p["demo"][0]}">▶ {p["demo"][1]}</a>' if p["demo"] else ""
    chips = "".join(f"<span>{html.escape(x)}</span>" for x in p["chips"])
    more = "".join(f'<a href="{q["slug"]}.html">{html.escape(q["name"])}</a>' for q in P if q["slug"] != p["slug"])
    dnote = f'<p class="note">{fmt(p["develop_note"])}</p>' if p["develop_note"] else ""
    desc = f'{p["name"]}: a product manager\'s one-page case study, from problem space to solution space.'
    teal, saf = "var(--teal)", "var(--acc)"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(p['name'])} · Case study · Gaurav Pandvia</title>
<meta name="description" content="{html.escape(desc)}"><meta name="theme-color" content="#0B1220">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><div class="wrap">
<div class="top"><a href="../index.html#projects">← Back to portfolio</a><span>Case study · a product manager's one-pager · Double Diamond</span></div>

<header class="hero"><div class="kick">AI Build Quests &amp; Prototypes</div>
<h1>{html.escape(p['name'])}</h1>
<div style="margin-bottom:6px"><span class="tag" style="--c:{c}">{html.escape(p['domain'])}</span></div>
<p class="tagline">{fmt(p['tagline'])}</p>
<div class="chips">{btn}{chips}</div></header>

<section class="grid2" aria-label="Why build this and the evidence">
<div class="card why"><p class="eyebrow">Why build a solution for it</p><ul>{lis(p['why'])}</ul></div>
<div class="card"><p class="eyebrow">{html.escape(p['stats_title'])}</p><div class="stats">{stats}</div></div>
</section>

{diamond()}
<section class="phases" aria-label="Double Diamond phases">
<article class="ph" style="--pc:{teal}"><span class="no">01 · Discover · diverge</span><h2>What is going on?</h2><p class="q">Research and observation, kept wide.</p><ul>{lis(p['discover'])}</ul></article>
<article class="ph" style="--pc:{teal}"><span class="no">02 · Define · converge</span><h2>What is the real problem?</h2>
<div class="problem"><small>Problem statement</small>{fmt(p['problem'])}</div><div class="ins">{ins}</div></article>
<article class="ph" style="--pc:{saf}"><span class="no">03 · Develop · diverge</span><h2>What could we build?</h2><p class="lead">{fmt(p['develop_lead'])}</p><ul>{lis(p['develop'])}</ul>{dnote}<div class="decision">{fmt(p['decision'])}</div></article>
<article class="ph" style="--pc:{saf}"><span class="no">04 · Deliver · converge</span><h2>What are we shipping?</h2><p class="lead">{fmt(p['deliver_lead'])}</p><ul>{lis(p['deliver'])}</ul><p class="note">{fmt(p['deliver_note'])}</p></article>
</section>

<section class="foot">
<div class="card val"><p class="eyebrow">Still to validate</p><ul>{lis(p['validate'])}</ul></div>
<div class="card"><p class="eyebrow">More case studies</p><div class="more">{more}</div></div>
</section>
<p class="src">Distilled from the project's PRD. Figures are as cited there, with sources noted on each stat.</p>
</div></body></html>
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    for p in P:
        with open(os.path.join(OUT, p["slug"] + ".html"), "w") as f:
            f.write(render(p))
        print("wrote", p["slug"])


if __name__ == "__main__":
    main()
