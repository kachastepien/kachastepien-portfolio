"""Builds one page per project at work/<slug>/index.html.

The pages share assets/site.css with the home page. Diagrams that already live on the
home page (the visit loop, the ERP flow, the streaming pipeline) are copied from
index.html so there is one source for each. Run from the repo root:

    python3 scripts/build_projects.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://kachastepien.com"
INDEX = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()


def snippet(pattern):
    m = re.search(pattern, INDEX, re.S)
    assert m, pattern
    return m.group(0)


LOOP_SVG = snippet(r'<svg viewBox="0 0 760 170".*?</svg>')
FLOW_SVG = snippet(r'<svg viewBox="0 0 700 250".*?</svg>')
PIPE_SVG = snippet(r'<svg viewBox="0 0 900 170".*?</svg>')

A = "../../assets/"


# ---------- building blocks ----------
def phones(items):
    figs = "".join(
        f'<figure class="phone reveal"><div class="device"><img decoding="async" src="{A}{src.replace('.jpg', '.webp')}" alt="{html.escape(alt)}" loading="lazy" width="393" height="851"></div>'
        f"<figcaption><b>{t}</b>{c}</figcaption></figure>"
        for src, alt, t, c in items
    )
    return f'<div class="phones">{figs}</div>'


def shots(items):
    figs = "".join(
        f'<figure class="shot reveal"><div class="browser"><img decoding="async" src="{A}{src.replace('.jpg', '.webp')}" alt="{html.escape(alt)}" loading="lazy"></div>'
        f"<figcaption><b>{t}</b>{c}</figcaption></figure>"
        for src, alt, t, c in items
    )
    return f'<div class="shots">{figs}</div>'


def decisions(items):
    lis = "".join(f"<li><details open><summary>{t}</summary><p>{p}</p></details></li>" for t, p in items)
    return f'<ol class="decisions reveal">{lis}</ol>'


def tldr(items):
    cells = "".join(f'<div><p class="label">{k}</p><p>{v}</p></div>' for k, v in items)
    return f'<div class="tldr reveal d1">{cells}</div>'


def chips(items, on=0):
    return '<div class="chips reveal">' + "".join(
        f'<span class="chip{" on" if i < on else ""}">{c}</span>' for i, c in enumerate(items)
    ) + "</div>"


def bullets(items):
    return '<ul class="feat reveal">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def cards(items):
    return '<div class="cards">' + "".join(
        f'<div class="card reveal"><p class="label">{k}</p>{"".join(f"<p>{p}</p>" for p in ps)}</div>' for k, ps in items
    ) + "</div>"


def table(head, rows):
    th = "".join(f"<th>{h}</th>" for h in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tbl reveal"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def facts(items):
    return '<div class="facts reveal">' + "".join(
        f'<div class="fact"><b>{n}</b><span>{t} <small>{s}</small></span></div>' for n, t, s in items
    ) + "</div>"


def metrics(items):
    return '<div class="metrics reveal">' + "".join(
        f'<div class="metric"><span>{k}</span><span class="bar"><i style="--v:{float(v) * 100:.1f}%"></i></span><b>{v}</b></div>' for k, v in items
    ) + "</div>"


# ---------- UX method blocks ----------
def process(steps):
    """Design-thinking stepper: (stage, what happened)."""
    lis = "".join(f'<li><span class="pr-n">{i+1:02d}</span><b>{t}</b><p>{d}</p></li>' for i, (t, d) in enumerate(steps))
    return f'<ol class="process reveal">{lis}</ol>'


def personas(items, note):
    """Proto-persona cards: (initials, colour, name, line, quote, goals, pains)."""
    out = []
    for ini, col, name, line, quote, goals, pains in items:
        g = "".join(f"<li>{x}</li>" for x in goals)
        pn = "".join(f"<li>{x}</li>" for x in pains)
        out.append(f'<article class="persona reveal"><header><span class="pa" style="--c:{col}">{ini}</span><div><b>{name}</b><span>{line}</span></div></header>'
                   f'<p class="pq">“{quote}”</p><div class="pgp"><div><p class="label">Goals</p><ul>{g}</ul></div><div><p class="label">Frustrations</p><ul>{pn}</ul></div></div></article>')
    return f'<div class="personas">{"".join(out)}</div><p class="note reveal">{note}</p>'


def vpc(who, jobs, pains, gains, products, relievers, creators):
    """Value Proposition Canvas: value map (square) on the left, customer profile (circle) on the right."""
    ul = lambda xs: "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    return (f'<div class="vpc reveal"><div class="vpc-map"><p class="vpc-h">Value map</p>'
            f'<div class="vq vq-p"><p class="label">Products &amp; services</p>{ul(products)}</div>'
            f'<div class="vq vq-r"><p class="label">Pain relievers</p>{ul(relievers)}</div>'
            f'<div class="vq vq-c"><p class="label">Gain creators</p>{ul(creators)}</div></div>'
            f'<span class="vpc-fit" aria-hidden="true">fit</span>'
            f'<div class="vpc-prof"><p class="vpc-h">Customer profile · {who}</p>'
            f'<div class="vq vq-j"><p class="label">Jobs to be done</p>{ul(jobs)}</div>'
            f'<div class="vq vq-pa"><p class="label">Pains</p>{ul(pains)}</div>'
            f'<div class="vq vq-g"><p class="label">Gains</p>{ul(gains)}</div></div></div>')


def journey(who, stages):
    """Journey map: (stage, doing, feeling 1-5, thought, opportunity) with an emotion curve."""
    n = len(stages); w = 1000; h = 120
    xs = [w * (i + .5) / n for i in range(n)]
    ys = [h - 14 - (f - 1) / 4 * (h - 28) for _, _, f, _, _ in stages]
    d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in zip(xs, ys))
    dots = "".join(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="7" class="{"lo" if f <= 2 else "hi" if f >= 4 else "mid"}"/>' for x, y, (_, _, f, _, _) in zip(xs, ys, stages))
    cols = "".join(f'<div class="jc"><p class="js">{st}</p><p class="jd">{do}</p><p class="jt">“{th}”</p><p class="jo"><span>Opportunity</span>{op}</p></div>' for st, do, f, th, op in stages)
    return (f'<div class="journey reveal" style="--n:{n}"><p class="label">Journey · {who}</p>'
            f'<svg class="jcurve" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true"><line x1="0" x2="{w}" y1="{h/2}" y2="{h/2}" class="mid-l"/><path d="{d}"/>{dots}</svg>'
            f'<div class="jcols">{cols}</div></div>')


def hmw(items):
    return '<ul class="hmw reveal">' + "".join(f"<li><span>How might we</span> {x}</li>" for x in items) + "</ul>"


def pov(text):
    return f'<blockquote class="pov reveal"><span class="label">Point of view</span>{text}</blockquote>'


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", html.unescape(re.sub(r"<[^>]+>", "", t)).lower()).strip("-")


def section(title, *body, lead=None):
    lead_html = f'<p class="cp-lead reveal">{lead}</p>' if lead else ""
    return (f'<section class="cp-sec" id="{slugify(title)}" data-rail="{html.escape(html.unescape(re.sub(r"<[^>]+>", "", title)))}">'
            f'<h2 class="reveal">{title}</h2>{lead_html}{"".join(body)}</section>')


def p(*texts):
    return "".join(f'<p class="cp-p reveal">{t}</p>' for t in texts)


def links(items):
    out = []
    for i, (label, href) in enumerate(items):
        cls = "btn solid" if i == 0 else "btn"
        out.append(f'<a class="{cls}" href="{href}">{label}</a>')
    return '<div class="links reveal">' + "".join(out) + "</div>"


# ---------- projects ----------
P = []

P.append(dict(
    slug="sidly-health", view="design", kicker="Case study · SiDLY Healthcare · ongoing",
    title="SiDLY Health: one record, three people",
    desc="How Katarzyna Stępień designed SiDLY Health: mobile and web apps that connect care managers, carers and residents around one visit.",
    lede="SiDLY Health connects the people around a single visit: the care manager who plans it, the carer who makes it and the resident who receives it. I lead its UX/UI across the mobile apps and the web platform.",
    tldr=[("The challenge", "One visit, three people, three apps that have to agree on the same data."),
          ("What I did", "Led UX/UI for the mobile apps and the web platform, prototyped in React/TypeScript."),
          ("Signature move", "Visits start and end with an NFC scan, so hours are settled from real time.")],
    chips=["Lead UX/UI designer", "Web + mobile", "React/TS prototype", "Medical device · MDR Class IIa"],
    hero=phones([("health/carer-home.jpg", "Carer's home screen", "Carer", "Today's visits and hours."),
                 ("health/res-home.jpg", "Resident's home screen", "Resident", "The band, visits and readings."),
                 ("health/mgr-carers.jpg", "Care manager's carers list", "Care manager", "The team at a glance."),
                 ("health/res-rate.jpg", "Rating a visit", "After the visit", "Rated by the resident.")]),
    body=[
        section("How I worked", process([
            ("Empathise", "50+ interviews and usability tests across the value chain: municipalities, foreign partners, care managers, carers and seniors, plus weekly meetings with stakeholders."),
            ("Define", "One visit seen by three people who never sit together. The same data has to mean the same thing to all of them."),
            ("Ideate", "Flows mapped per role around a single shared object, the visit, and its care card."),
            ("Prototype", "A clickable React/TypeScript prototype with realistic test data, so people test whole visits, not single screens."),
            ("Test &amp; iterate", "Sessions with managers, carers and residents on the prototype; decisions below came out of those rounds.")]),
            lead="A classic design-thinking loop, run continuously next to development rather than once."),
        section("Who it is for", personas([
            ("AN", "#c9a47e", "Anna, care manager", "Runs a team of carers for a municipality", "I need to know who is where, and react before a family calls me.",
             ["See today's visits and gaps at a glance", "Settle carers' hours without chasing paper", "Handle alarms fast"],
             ["Hours reconstructed after the fact", "Problems surface only when someone complains", "The same data kept in several places"]),
            ("IA", "#a6a8ff", "Igor, carer", "Visits several residents a day on foot and by car", "Tell me where to go and what to do, then let me get on with it.",
             ["A clear plan for the day", "Tick off tasks on the spot", "Get paid for the time actually worked"],
             ["Paperwork after a long day", "Access details scattered across calls and notes", "Disputes about when a visit really happened"]),
            ("KW", "#9bd3c0", "Krystyna, resident, 84", "Lives alone, wears a SiDLY band", "I want to know who is coming and that someone will answer if I press the button.",
             ["Know when the next visit is", "Feel safe at home", "Have a say in how care goes"],
             ["Small text and crowded screens", "Not knowing who will come", "Feeling care happens to her, not with her"])],
            "Proto-personas: built from interviews and stakeholder sessions, using the names from the test data. They describe patterns, not real people."),
            lead="Three roles around one visit. Each persona maps to one of the apps."),
        section("Value proposition", vpc("care manager",
            ["Plan and staff every visit", "Prove care was delivered", "Settle hours and billing", "React to alarms"],
            ["Hours rebuilt from memory", "No live view of the field", "Late, second-hand feedback from residents"],
            ["Fewer phone calls", "Trustworthy records for the municipality", "A calm, predictable day"],
            ["Manager app and web dashboard", "Carer Planner with NFC check-in", "Resident app with ratings"],
            ["Visits start and end with a scan, so time is recorded as it happens", "Urgent-first dashboard", "One care card from plan to record"],
            ["Residents rate visits directly", "Weekly schedule with gaps flagged", "Recurring visits that stay editable one by one"]),
            lead="Value Proposition Canvas for the care manager, the role that buys and runs the system day to day."),
        section("A visit, end to end", journey("carer and resident", [
            ("Plan", "Manager assigns the visit; the carer sees it in the Planner", 3, "Where am I going today?", "Today view with hours and residents"),
            ("Arrive", "Carer finds the flat and gets in", 2, "Which intercom, who has the key?", "Access notes on the care card"),
            ("Check in", "Scans the resident's NFC tag", 4, "Done, the clock is running.", "Scan as the only way in"),
            ("Care", "Does the tasks and writes a note", 3, "Did I forget anything?", "Tasks from the care card, ticked on the spot"),
            ("Check out", "Scans again to end the visit", 4, "My hours are right.", "Locked record of the visit"),
            ("Rate", "Resident rates tasks and the visit", 5, "They listen to me.", "Simple star rating in large type")]),
            lead="The emotional low points of the old process became the places the design focuses on."),
        section("Design questions", hmw([
            "make the time a carer actually worked the record, instead of what was planned?",
            "show a manager what needs attention before anyone has to call?",
            "give an 84-year-old resident a voice in her own care, on a phone, without help?"])),
        section("Three accounts on the same data",
                cards([("Care manager", ["Residents, carers, the visit schedule, alarms, devices and reports."]),
                       ("Carer", ["The Planner: today's visits, tasks and the care card for each resident."]),
                       ("Resident", ["Health readings, medication, upcoming visits, visit ratings and SOS."])]),
                p("A visit belongs to all three. When the carer finishes it, it appears in the resident's history, ready to be rated, and in the manager's record of work. An alarm handled by the manager disappears from every view."),
                f'<div class="loop reveal">{LOOP_SVG}</div>'),
        section("The care manager's mobile app", phones([
            ("health/mgr-carers.jpg", "Carers screen", "Carers", "Who is on the team, who is active and when each person works today."),
            ("health/mgr-profile.jpg", "Carer profile", "Carer profile", "Residents, today's hours, today's visits and access, on one screen."),
            ("health/mgr-hours.jpg", "Working hours", "Working hours", "Set per weekday, with several ranges a day for split shifts."),
            ("health/mgr-visits.jpg", "Today's visits", "Today's visits", "Each visit with its care hours, editable from the list.")]),
            lead="Care managers run their team from the phone as much as from the desk. This flow covers the carers: who they look after, when they work and what they can access."),
        section("The carer's Planner", phones([
            ("health/carer-home.jpg", "Planner home", "Today", "Time worked so far, filled-in care cards and today's visits."),
            ("health/carer-start.jpg", "Start a visit", "Start a visit", "Scan the resident's QR code or NFC tag. There is no other way in."),
            ("health/carer-nfc.jpg", "NFC scan", "NFC scan", "Hold the phone to the resident's band or Planner device."),
            ("health/carer-visit.jpg", "Visit in progress", "Visit in progress", "Tasks from the care card, ticked off on the spot, with a note for the office.")]),
            lead="Carers use the Planner on their phone during the visit. The flow is built around the scan: a visit starts when the phone touches the resident's tag and ends the same way."),
        section("The resident's app", phones([
            ("health/res-home.jpg", "Resident home", "Home", "The band, recent visits and today's readings on one screen."),
            ("health/res-history.jpg", "Visit history", "Visit history", "Every visit with its carer, tasks done and rating."),
            ("health/res-rate.jpg", "Rate a visit", "Rate a visit", "Stars for each task and for the visit, plus the carer's note."),
            ("health/res-health.jpg", "Health readings", "Health readings", "Pulse, saturation and steps from the band, in large type.")]),
            lead="The resident sees the same visits from the other side: who came, what was done, and a place to say how it went."),
        section("The web platform", shots([
            ("health/web-dashboard.jpg", "Manager's dashboard", "Manager's dashboard", "What needs a reaction comes first, then the carers in the field today and the week's visits."),
            ("health/web-schedule.jpg", "Weekly schedule", "Schedule", "A week per carer, with the residents who have no visit this week listed underneath."),
            ("health/web-visit.jpg", "Visit in progress", "Visit in progress", "The care card mid-visit. Tasks and notes save as they go; the visit ends in the mobile app."),
            ("health/web-res-home.jpg", "Resident's home", "Resident's home", "The next visit, a prompt to rate the last one, and who to call.")]),
            '<p class="note">Screens shown in English for this page; the product ships in Polish. All names and data are test data.</p>',
            lead="At the desk the same data gets more room. The manager plans and settles the team's work, carers follow their visits from a laptop, and residents see their own record."),
        section("Key design decisions", decisions([
            ("A visit starts with a scan", "The carer starts and ends each visit by scanning the resident's NFC tag with their phone. Work time is recorded as it happened, not as it was planned, and carers' hours are settled from it."),
            ("The care card has a lifetime", "Before a visit the care card is the plan. During the visit the carer fills it in. After the visit it becomes the record that the resident and the office read, so it is locked as it was when the visit ended."),
            ("The resident's home screen answers three questions", "Am I all right, what do I need to do today, and when is someone coming? Large text, large touch targets, few words, and SOS always on top."),
            ("Urgent first, then the day", "The manager's dashboard opens with what needs a reaction, then today's visits in the field, the week ahead and equipment. Each block leads to the screen where that issue gets solved."),
            ("Recurring visits stay ordinary visits", "A series is a set of normal visits that share a tag, so any single one can be moved or cancelled without breaking the rest."),
            ("Prototype in code, not in frames", "The flows are built as a clickable React/TypeScript prototype with realistic test data, so managers and carers test whole visits instead of single screens.")])),
        section("How success is measured", table(["Goal", "Signal the design is built to move"], [
            ("Hours are settled from real time", "Share of visits started and ended with a scan"),
            ("Managers react before families call", "Time from an alarm or missed visit to a reaction"),
            ("Residents have a voice", "Share of visits rated by residents"),
            ("Less admin for carers", "Notes and tasks completed during the visit, not after")]),
            '<p class="note">Product metrics defined with the team; the product is live and in active development.</p>'),
    ],
))

P.append(dict(
    slug="sidly-erp", view="design", kicker="Case study · SiDLY Healthcare · in progress",
    title="Redesigning the ERP that runs public telecare",
    desc="How Katarzyna Stępień is redesigning the SiDLY ERP used by 1,000+ municipalities and care providers: the problem, the process and six design decisions.",
    lede="Municipalities, public institutions and care providers use the SiDLY ERP to order telecare bands, assign them to residents, keep consent documents in order and renew contracts. I am leading its redesign.",
    tldr=[("The challenge", "Routine tasks where mistakes are easy to make and hard to notice, for very different clients."),
          ("What I did", "Research with municipal and foreign clients, then a clickable React/TypeScript prototype."),
          ("Signature move", "An undo instead of a confirm for anything reversible.")],
    chips=["Lead designer", "1,000+ client organisations", "React/TS prototype", "In progress"],
    hero='<div class="lock reveal"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="1.5"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2"/></svg><p>The interface is unreleased and confidential, so this case study describes the process and decisions without screens. I am happy to walk through the prototype in an interview.</p></div>',
    body=[
        section("The problem", p(
            "Most of the work in the ERP is routine: activating a batch of bands, swapping a broken one, attaching a signed consent form. Mistakes in these tasks are easy to make and hard to notice. A band can be activated for the wrong client, or keep sending data under a person who no longer wears it.",
            "The system also serves two very different clients. A Polish municipality works in złoty, uploads documents from its social-welfare office and tracks coverage of its residents aged 60+. An export client sells across borders, invoices in euro and needs dialling codes per country.")),
        section("How I worked", p(
            "Weekly project meetings with stakeholders, plus research with municipal and foreign clients about how they order, assign and renew devices.",
            "I built the redesign as a clickable prototype in React and TypeScript with realistic test data, so whole flows can be tested instead of static mockups.")),
        section("Where the decisions sit", f'<div class="flow reveal">{FLOW_SVG}</div>',
                '<p class="note">The life of an order and its bands, simplified. Numbers match the decisions below.</p>'),
        section("Key design decisions", decisions([
            ("Confirm only what is expensive", "Asking twice for everything trains people to click through. A confirmation now appears only for a new paid year or a change to many devices at once. A single suspend or resume is reversible, so it gets an undo instead."),
            ("Read the file back before acting on it", "Bulk activation comes in as a spreadsheet, with columns in a different order every time. Rows are matched on the device number, and nothing runs until each line has been shown back with what it will do. The template you download is the file you can upload."),
            ("Keep a rule where it matters", "Health data needs signed consent, but the clerk entering a resident rarely has the scan at hand. Blocking the form only taught people to upload placeholder files. Now the resident can be saved, is flagged \"no consent\" everywhere, and cannot receive a band until the scan arrives."),
            ("Every number opens its list", "Each count on the dashboard opens exactly the devices it counts, and each bar in the renewals chart renews what it shows. Nothing on the dashboard sends you hunting elsewhere."),
            ("Show what an action will touch", "With a mixed selection, each action states how many of the selected devices it would change and switches off at zero. The selection bar used to be the one dark element on the screen, which made ticking three rows feel like a warning. It is now calm, with one obvious next step."),
            ("Never rely on colour alone", "Every status carries an icon and a label as well as a colour, because green and amber are hard to tell apart for colour-blind users.")])),
    ],
))

P.append(dict(
    slug="lemi", view="design", kicker="HackYeah 2026 · Sport &amp; Healthcare challenge",
    title="Lemi: health care without the stress",
    desc="Lemi, Katarzyna Stępień's HackYeah 2026 project: a health guide that helps before, during and after a doctor's visit, built on the Claude API and ElevenLabs.",
    lede="Lemi is a health guide with a friendly lemur. It helps every day and at every doctor's visit: it joins mood, movement, medication, measurements and test results, and turns them into one small step for today.",
    tldr=[("The problem", "People put off the doctor because of the phone call, the ten minutes and the advice they forget."),
          ("What I built", "A web app and a Flutter app on the Claude API and ElevenLabs, designed and coded at the hackathon."),
          ("Signature move", "One recorded visit becomes three summaries: for you, for family, for the doctor.")],
    chips=["Claude API", "ElevenLabs Scribe", "React + TypeScript PWA", "Flutter (iOS, Android)", "WCAG 2.2 AA"],
    hero=phones([("lemi/welcome.jpg", "Lemi welcome screen", "Start", "Pick a demo account by age, or start your own."),
                 ("lemi/today.jpg", "Lemi Today screen", "Today", "Mood, the next visit, and a grandmother whose pulse has been higher for days."),
                 ("lemi/visits.jpg", "Lemi visit preparation", "Visits", "Before, during, after: questions and a folder for the doctor."),
                 ("lemi/health.jpg", "Lemi health screen", "Health", "Sleep, resting pulse, HRV, steps and mood over time.")])
         + '<p class="note">Shown in English for this page; the demo runs in Polish.</p>',
    body=[
        section("How I worked", process([
            ("Empathise", "Started from my own habit of putting off the doctor, then talked to people at the hackathon and checked the research below."),
            ("Define", "The hard part is not knowing what is wrong. It is the phone call, the ten minutes and the advice you forget."),
            ("Ideate", "One idea held the rest together: split the visit into before, during and after, and give each moment one job."),
            ("Prototype", "A working web app and a Flutter app on the Claude API and ElevenLabs, with demo accounts for each persona."),
            ("Test", "Walkthroughs with the demo accounts and an automated accessibility check (axe-core) on 14 screens, with no errors.")]),
            lead="Design thinking, compressed into a hackathon."),
        section("Where it started", p(
            "It started with me. I'm a student and I put off calling the doctor, not because I don't know what is wrong, but because I have to call, explain myself, remember everything in ten minutes and then keep track of the advice.",
            "At the hackathon I asked other people whether they felt the same. It was far more common than I thought, and each conversation added a group the app could help: people for whom Polish is not a first language, people with disabilities, neurodivergent people, seniors and their families, and people with health anxiety."),
            facts([("47.6%", "of Europeans have trouble understanding health information", "HLS-EU survey, 2015"),
                   ("40–80%", "of medical advice is forgotten right after the visit", "Kessels, 2003"),
                   ("81%", "of young adults feel stressed before a phone call", "BankMyCell, 1,200+ people")])),
        section("Who it is for", personas([
            ("OL", "#a6a8ff", "Ola, 20", "Student, avoids phone calls", "I know something is off, I just can't make myself call.",
             ["Book a visit without a phone call", "Remember what the doctor said", "Feel in control, not judged"],
             ["Phone anxiety", "Forgetting questions in the room", "Medical words she can't follow"]),
            ("MA", "#c9a47e", "Marek, 42", "Busy parent, higher blood pressure", "I measure it when I remember. I never know if it matters.",
             ["Track pressure without effort", "Know when a result is worth a visit", "Spend less time on admin"],
             ["Numbers without meaning", "No time to prepare for visits", "Paper results he can't find"]),
            ("HA", "#9bd3c0", "Halina, 68", "Retired, shares her pulse with her daughter", "I want to manage on my own, but my daughter worries.",
             ["Large, simple screens", "Clear next steps after a visit", "Let family see what matters"],
             ["Small text and crowded apps", "Leaflets and advice she forgets", "Feeling like a burden"])],
            "Proto-personas behind the demo accounts (18–30, 30–50, 50+). Built from my own experience, conversations at the hackathon and the research above."),
            lead="Three people, one shared fear: the visit itself."),
        section("Point of view", pov("A young adult who keeps putting off the doctor needs a way to prepare, follow and remember a visit without a phone call, because the stress of the call, not the illness, is what stops her."),
            hmw(["make the first contact with a doctor feel as easy as sending a message?",
                 "turn ten rushed minutes in the room into something you can read again later?",
                 "let family help without taking over?"])),
        section("Value proposition", vpc("Ola",
            ["Get an appointment", "Explain symptoms clearly", "Remember and follow the advice"],
            ["Stress before the call", "Forgotten questions", "Jargon in results and summaries"],
            ["Feeling prepared", "Advice she can reread", "Someone close kept in the loop"],
            ["Lemi app (web + Flutter)", "AI assistant on the Claude API", "Live transcription with ElevenLabs"],
            ["Questions drafted from her own data", "An AI voice agent that can call for her (beta)", "Plain-language summaries"],
            ["Three summaries: for her, family and the doctor", "Advice turned into tasks and reminders", "Calm mode for health anxiety"]),
            lead="Value Proposition Canvas for the main persona."),
        section("A doctor's visit, mapped", journey("Ola", [
            ("Notice", "Feels unwell for a few days", 3, "It'll probably pass.", "Gentle nudge from her own data"),
            ("Book", "Has to call the clinic", 1, "I'll do it tomorrow.", "AI call agent, or a folder sent ahead"),
            ("Prepare", "Tries to remember what to say", 2, "What if I forget something?", "Questions drafted for her"),
            ("Visit", "Ten minutes with the doctor", 2, "Too fast, too many words.", "Live transcript and word explanations"),
            ("After", "Has to follow the advice", 3, "What did she say about the dose?", "Three summaries and reminders"),
            ("Follow up", "Feels better, keeps tracking", 5, "I've got this.", "Tasks, reminders and progress")]),
            lead="The lowest points of the journey are exactly where Lemi steps in."),
        section("A doctor's visit in three steps", cards([
            ("Before", ["Questions for the doctor are drafted from your own data, and a folder reaches the doctor before the visit. In beta, an AI voice agent can call the reception for you and introduces itself as AI."]),
            ("During", ["With the doctor's consent, live transcription turns the conversation into text, ticks off your questions and explains difficult words. \"Show instead of tell\" screens help at the reception desk."]),
            ("After", ["A summary in three versions: for you, for someone close to you and for the doctor. Advice turns into tasks and reminders, including e-prescriptions that are about to expire."])])),
        section("Every day", bullets([
            "Mood in one tap, with Lemi the lemur reacting across the app.",
            "Medication with reminders, and movement that starts from what is realistic, with WHO's 150 minutes a week as the goal.",
            "Measurements from a photo: blood pressure monitor, glucometer, scale or thermometer. AI reads the display and you confirm the value.",
            "Health over time: sleep, heart rate, heart-rate variability, steps, mood and measurements by day, week, month or year.",
            "Connections between data, for example worse sleep, lower mood and a test result worth raising with a doctor.",
            "Test results from a PDF or a photo, with every parameter explained in plain language."])),
        section("Mental health, carefully", bullets([
            "Short mood and anxiety check-ins (PHQ-9 and GAD-7) when a doctor recommends them, every two weeks, with a chart to show a doctor or psychologist.",
            "A calm mode for health anxiety: no percentages and no red labels.",
            "When someone circles the same symptoms, Lemi stops adding AI answers and suggests a question for the doctor and a talk with someone close.",
            "A crisis path, with 112 and a helpline always at hand."])),
        section("Accessibility and AI that behaves", cards([
            ("Accessibility", ["Built to WCAG 2.2 level AA; an automated axe-core check on 14 screens found no errors.", "\"My needs\" adapts the app for ADHD, autism, dyslexia, colour blindness, low vision and hearing, limited mobility and eating disorders, for example by hiding weight."]),
            ("AI rules (AI Act, GDPR)", ["You always know when AI is at work. AI does not diagnose or give doses, and every entry, visit and email waits for your approval.", "Sudden symptoms are caught before the model and lead straight to 112. Without API keys the app runs in a rule-based demo mode."])])),
        section("How it is built", table(["Part", "What it uses"], [
            ("Assistant, PDF results, visit summary", "Claude Sonnet (Anthropic)"),
            ("Reading a measurement from a photo, live mode, tip of the day", "Claude Haiku (Anthropic)"),
            ("Speech to text", "ElevenLabs Scribe, with the Web Speech API as a fallback"),
            ("Front-end", "React, TypeScript and Vite, installable as a PWA; a native Flutter app shares the same API"),
            ("Back-end", "Serverless functions on Vercel"),
            ("Privacy", "Health data stays on the phone; sharing, the QR code and the doctor's folder are encrypted with AES-GCM; export for doctors in HL7 FHIR")])),
        section("Try it", p("Open the demo and pick <b>Young adults 18–30</b> (Ola, 20). Other accounts: <b>30–50</b> (Marek, higher blood pressure), <b>50+</b> (Halina, simple mode with large text) and a <b>doctor's view</b>. All characters and data in the demo are fictional."),
                links([("Open the demo", "https://pekao.vercel.app")])),
    ],
))

P.append(dict(
    slug="govbot", view="design", kicker="1st place · AI Place Challenge 2025 · Team lead &amp; AI lead",
    title="GovBot: an AI chatbot for mObywatel",
    desc="GovBot, the AI chatbot for mObywatel that won 1st place in the AI Place Challenge set by the Polish Ministry of Digital Affairs. Katarzyna Stępień was team lead.",
    lede="GovBot lives inside mObywatel, the Polish government app, and answers questions about official matters for your own municipality: what to prepare, where to go and when the office is open. Our team won 1st place in the AI Place Challenge, set by the Ministry of Digital Affairs.",
    tldr=[("The challenge", "Official procedures are spread across portals, and every municipality works a little differently."),
          ("What we built", "An AI assistant inside mObywatel that combines national rules with the user's own office, built in n8n."),
          ("Signature move", "Every answer ends where you live: the right office, address, room and opening hours.")],
    chips=["Team lead", "AI lead", "1st place", "n8n", "LLM", "Figma prototype"],
    hero='<div class="gb-hero"><figure class="phone vid reveal"><div class="device"><video src="' + A + 'govbot/govbot-prototype.mp4" poster="' + A + 'govbot/govbot-poster.webp" autoplay muted loop playsinline preload="metadata" aria-label="Screen recording of the GovBot prototype: from the mObywatel home screen to an answer about a child\'s ID card and the local office"></video></div>'
         '<figcaption><b>The prototype</b>From mObywatel to an answer about a child\'s ID card, and then the local office.</figcaption></figure>'
         '<div class="gb-photo reveal"><img decoding="async" loading="lazy" src="' + A + 'govbot/stage.webp" width="1600" height="1067" alt="The team presenting GovBot on the AI Place stage at Econverse Fuse 2025"><p>On stage at Econverse Fuse 2025, Warsaw</p></div></div>'
         + '<p class="note">Concept prototype for the AI Place Challenge, not an official mObywatel feature. Screens are in Polish, as in the app.</p>',
    body=[
        section("How we worked", process([
            ("Empathise", "Started from the brief set by the Ministry of Digital Affairs and the questions residents actually bring to a municipal office: removing a tree, an ID card for a child, the waste schedule, rules for old boilers."),
            ("Define", "People don't lack information. They lack the right piece of it, for their own office, at the moment they need it."),
            ("Ideate", "Put the assistant where people already are, inside mObywatel's Support and contact, and make it local by default."),
            ("Prototype", "A clickable Figma prototype in mObywatel's visual language, with the assistant's logic built as n8n workflows on an LLM."),
            ("Test", "Walked the jury through real questions on stage at Econverse Fuse 2025. The jury gave it 1st place.")]),
            lead="A hackathon-sized design-thinking loop, from the brief to a working demo."),
        section("Who it is for", personas([
            ("EW", "#c9a47e", "Ewa, 36", "Parent, needs an ID card for her child", "I just want to know what to bring, so I go to the office once.",
             ["Know the steps before leaving home", "Find the right office and hours", "Do it online if she can"],
             ["Contradicting answers online", "Phone lines that are always busy", "A wasted trip for a missing document"]),
            ("ST", "#a6a8ff", "Stanisław, 71", "Retired, prefers talking to typing", "I'd rather ask someone than click through forms.",
             ["Ask in his own words", "Hear the answer, not read it", "Reach a real official when needed"],
             ["Small text and long pages", "Official jargon", "Not knowing which office handles what"]),
            ("TO", "#9bd3c0", "Tomek, 28", "Just moved to a new municipality", "Where do I even register, and when is the bin collected?",
             ["Sort out registration fast", "Learn local rules once", "Keep it on the phone"],
             ["Every municipality has its own rules", "Information scattered across sites", "Office hours that don't fit work"])],
            "Proto-personas built for the challenge from typical questions residents bring to a municipal office. They describe patterns, not real people."),
            lead="Three residents, one shared problem: the answer exists, but not for their own office."),
        section("Point of view", pov("A resident dealing with an official matter needs one clear answer for their own municipality, because general information sends them to the wrong office or back home for a missing document."),
            hmw(["give people an answer for their own office, not for Poland in general?",
                 "make official answers as easy to scan as a checklist?",
                 "help people who would rather speak than type?"])),
        section("Value proposition", vpc("resident",
            ["Find out what a procedure needs", "Get to the right office", "Get it done in one visit"],
            ["Searching several sites", "Busy phone lines", "Missing a document and coming back"],
            ["Feeling prepared", "Less time off work", "Confidence the answer is current"],
            ["GovBot inside mObywatel", "Topic shortcuts and chat history", "Voice messages"],
            ["Answers tied to the user's own municipality", "Office, room, phone and hours in the answer", "Structured answers: who, where, what to bring, fees"],
            ["Date of the last data update on screen", "A route to the office on the map", "Hand-off to an official or a booked visit"]),
            lead="Value Proposition Canvas for the resident."),
        section("An official matter, mapped", journey("Ewa", [
            ("Notice", "Her child needs an ID card", 3, "How does this work for kids?", "Ask in mObywatel, where her documents already are"),
            ("Search", "Looks through several websites", 2, "Every site says something else.", "One answer from official sources"),
            ("Call", "Tries the office phone line", 1, "Nobody picks up.", "Chat that answers at any hour"),
            ("Prepare", "Collects the documents", 3, "Do I have everything?", "A checklist: what to bring, does the child come"),
            ("Go", "Finds the right office", 2, "Which building, which room?", "Address, room and hours of her own office"),
            ("Done", "Submits the application", 5, "One visit, done.", "Route on the map and a booked visit")]),
            lead="The lowest points of the journey are where GovBot answers."),
        section("The flow, in the app", phones([
            ("govbot/home.jpg", "mObywatel home screen with the GovBot entry", "Entry", "GovBot starts from the home screen of mObywatel."),
            ("govbot/support.jpg", "Support and contact screen for the municipal office", "Support &amp; contact", "Chats sit next to contacting an official, booking a visit and FAQ, for the chosen office."),
            ("govbot/chats.jpg", "Chats screen with suggestions and history", "Chats", "Suggested topics and earlier conversations grouped by day."),
            ("govbot/hello.jpg", "GovBot greeting with topic shortcuts", "Start", "Topic shortcuts and the date of the last data update.")]),
            phones([
            ("govbot/answer.jpg", "Structured answer about a child's ID card", "A structured answer", "Who can apply, where, what to bring, does the child come, how long, how much."),
            ("govbot/local.jpg", "Answer with the local office details", "Your own office", "The same question, answered for the user's municipality: office, room, phone, hours."),
            ("govbot/voice.jpg", "Conversation with voice messages", "Voice", "Ask and listen with voice messages, for people who don't want to type."),
            ("govbot/map.jpg", "Map with the route to the municipal office", "The way there", "A route to the office, so the answer ends at the door.")]),
            lead="From the mObywatel home screen to the door of the right office."),
        section("Key design decisions", decisions([
            ("Live where people already are", "GovBot sits in mObywatel's Support and contact, next to contacting an official and booking a visit, instead of being one more app to install."),
            ("Local by default", "The chosen municipality sits at the top of Support and contact, and answers use its own office, room, phone and opening hours."),
            ("Answers shaped like a checklist", "Official answers follow the same headings every time: who can apply, where, what to bring, waiting time and fees, so they can be scanned in seconds."),
            ("Show how fresh the data is", "The greeting shows when the data was last updated, because an outdated official answer is worse than none."),
            ("Voice in and out", "Voice messages let people ask and listen instead of typing and reading."),
            ("Always a way to a person", "Contacting an official or booking a visit stays one tap away from the chat.")])),
        section("How it is built", table(["Part", "What it uses"], [
            ("Assistant logic", "n8n workflows on an LLM"),
            ("Knowledge", "National procedures plus the chosen municipality's own data"),
            ("Prototype", "Figma, clickable, in mObywatel's visual language"),
            ("My role", "Team lead and AI lead")]),
            links([("Open the clickable prototype", "https://www.figma.com/proto/EOTTWQdoZ3btnTGtyjaXaP?node-id=0-1&t=qHPOiibk2nObztgy-6")])),
    ],
))

P.append(dict(
    slug="unmasked", view="data", kicker="NLP · B.A. thesis · SWPS University · 2026",
    title="Unmasked: catching manipulative UX copy with NLP",
    desc="Unmasked, Katarzyna Stępień's NLP project: a classifier for dark patterns in e-commerce copy (F1 0.936) shipped as an offline Chrome extension.",
    lede="Dark patterns live in the words: \"Only 2 left!\", \"43 people are viewing this\". I trained a classifier to spot them and shipped it as a Chrome extension that warns you before you buy.",
    tldr=[("The problem", "Manipulative copy is everywhere in e-commerce, and people rarely notice it."),
          ("What I did", "Trained and compared five classifiers on 2,356 labelled texts, then shipped the best as a Chrome extension."),
          ("Result", "F1 0.936 and ROC AUC 0.976, running fully offline in the browser.")],
    chips=["Python", "scikit-learn", "TF-IDF", "JavaScript", "Chrome extension"],
    hero=metrics([("Binary F1", "0.936"), ("Binary ROC AUC", "0.976"), ("By category, macro F1", "0.891")]),
    body=[
        section("Why it matters", p("Dark patterns undermine user autonomy and informed consent. The project supports ethical UX design by making deceptive copy visible at the moment it works on you."),
                table(["Category", "Example"], [("Scarcity", "\"Only 2 left in stock!\""), ("Urgency", "\"Offer ends in 10:00 minutes\""), ("Social proof", "\"43 people are viewing this\""), ("Misdirection", "Confusing opt-out wording"), ("Obstruction, sneaking, forced action", "Patterns that block, hide or push")])),
        section("Data", p("2,356 short UX texts from e-commerce sites: the Dark Patterns dataset (Mathur et al., 2019) plus neutral interface texts, balanced 50/50 between dark and non-dark. Each sample has a page id, the text, a label and a pattern category.")),
        section("Method", cards([
            ("Preprocessing", ["Lowercasing, whitespace trimming and stop-word removal, then TF-IDF with 1–2-grams and up to 5,000 features."]),
            ("Models compared", ["Logistic Regression, a linear Support Vector Machine, Random Forest, Naive Bayes and Gradient Boosting, on a binary task (dark or not) and a multiclass task (which pattern)."])])),
        section("Results", bullets(["Logistic Regression was the best model on the binary task.",
                         "Dark patterns have their own vocabulary: urgency (\"hurry\", \"limited\"), scarcity (\"only\", \"left\", \"stock\") and social proof (\"people\", \"purchased\").",
                         "Classical models on TF-IDF did surprisingly well; the rare categories suffered from too little data."])),
        section("From model to extension", p(
            "The top lexical features of the trained model, such as <i>left</i>, <i>limited</i>, <i>hurry</i>, <i>people</i> and <i>bought</i>, became explicit rules in a JavaScript classifier. The extension scans the text of any page, highlights flagged copy in place with a severity of critical, warning or info, and a popup explains the psychological mechanism behind each one.",
            "Classification runs fully offline, with no API calls. AI-written explanations are optional, with your own OpenAI key."),
            links([("Try the live demo", "../../?view=data#unmasked"), ("Extension on GitHub", "https://github.com/kachastepien/unmasked"), ("Model notebooks", "https://github.com/kachastepien/automated-dark-pattern-detection")])),
        section("What could come next", bullets(["Transformer models such as BERT or RoBERTa.", "Multimodal analysis of text together with the interface visuals.", "Data augmentation for the under-represented categories."])),
        '<p class="note">Stępień, K. (2026). <i>NLP-Based Detection of Manipulative UX Patterns in Web Interfaces</i>. SWPS University, Warsaw.</p>',
    ],
))

P.append(dict(
    slug="healthplatform", view="data", kicker="Applied AI · B.Eng. thesis · 2024/25",
    title="HealthPlatform: a health summary from a medical wearable",
    desc="HealthPlatform, Katarzyna Stępień's engineering thesis: biometric data from a medical wristband and medical documents turned into health summaries with RAG and voice.",
    lede="An intelligent system that supports health monitoring: it joins biometric data from a medical IoT wristband with the user's own medical documents, and uses AI to generate personal health recommendations.",
    tldr=[("Goal", "Turn data from a medical wristband into readable, personal health insights."),
          ("What I built", "A React/TypeScript platform with a RAG assistant over the user's own medical documents."),
          ("Highlight", "Voice in and out: speech recognition for symptoms, spoken answers back.")],
    chips=["React 18", "TypeScript", "Supabase", "Langflow", "AstraDB", "OpenAI", "Groq", "ElevenLabs"],
    hero=snippet(r'<div class="arch reveal".*?</div>\s*</div>').replace('class="arch reveal"', 'class="arch reveal"'),
    body=[
        section("Objectives", bullets([
            "<b>IoT device integration:</b> connecting the SiDLY medical wristband.",
            "<b>AI assistant with RAG:</b> a chatbot that draws on the user's medical documents.",
            "<b>Recommendation system:</b> machine-learning algorithms that generate personal health advice.",
            "<b>Voice analysis:</b> speech recognition and symptom analysis from audio recordings.",
            "<b>Medical documentation:</b> storing and analysing the user's medical documents."])),
        section("Stack", table(["Layer", "Tools"], [
            ("Front-end", "React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui"),
            ("Back-end and services", "Supabase (database, auth, storage), Langflow for AI workflows, OpenAI API (GPT-4, Whisper), Groq API, ElevenLabs API"),
            ("Data", "AstraDB vector database, PostgreSQL via Supabase, Supabase Storage for documents")])),
        '<p class="note">Engineering thesis in Computer Science, Warsaw School of Computer Science, supervised by Andrzej Ptasznik, M.Sc.Eng. The code is private; happy to show it in an interview.</p>',
    ],
))

P.append(dict(
    slug="ux-friction", view="data", kicker="Data engineering · streaming · CDC",
    title="UX friction detection, in real time",
    desc="A real-time data platform by Katarzyna Stępień that detects rage clicks, abandonment and long screen times with Debezium, Kafka, Spark and Delta Lake.",
    lede="A data platform that watches how people use an app and flags friction as it happens: rage clicks, abandoned sessions, screens people get stuck on. Every interaction is captured from the database with change data capture and processed as a stream.",
    tldr=[("Goal", "Detect UX friction signals while sessions are happening."),
          ("What I built", "A Docker stack: PostgreSQL with Debezium CDC, Kafka, Spark Structured Streaming, Delta Lake on MinIO."),
          ("Output", "Friction events scored per interaction and per session, stored with ACID guarantees.")],
    chips=["Python", "PostgreSQL", "Debezium", "Kafka", "Spark", "Delta Lake", "MinIO", "Docker"],
    hero=f'<div class="pipe reveal">{PIPE_SVG}</div>',
    body=[
        section("Friction rules", table(["Signal", "Rule", "Severity"], [
            ("Rage click", "<code>event_type = 'rage_click'</code> or more than 5 clicks", "High"),
            ("Session abandonment", "<code>event_type = 'session_abandon'</code>", "High"),
            ("Long screen time", "more than 120 s on a screen", "Medium"),
            ("Form error", "<code>event_type = 'form_error'</code>", "Medium"),
            ("Excessive scrolling", "<code>event_type = 'rapid_scroll'</code>", "Low")])),
        section("Data model", table(["Table", "What it holds"], [
            ("users", "Profiles: device, OS, browser, country"),
            ("screens", "Each screen's category, UX goal, expected time and whether it sits on the critical path"),
            ("sessions", "Start and end, device, converted, abandoned, number of events, total friction score"),
            ("ux_interactions", "Each event: screen, type, time on screen, clicks, scroll depth, friction flag and score")])),
        section("How it runs", cards([
            ("Capture", ["A Python simulator writes realistic sessions to PostgreSQL. Debezium reads the logical replication log and publishes every insert and update to Kafka as JSON."]),
            ("Process and store", ["Spark Structured Streaming reads from Kafka, applies the rules and aggregates per session in time windows. Results land in Delta Lake on MinIO, S3-compatible storage with ACID transactions."]),
            ("Operate", ["One <code>docker-compose up -d</code> starts everything, with health checks, automatic connector registration and named volumes. Kafka UI and Spark UI make it observable."]),
            ("A reusable template", ["The same pattern as a mini data platform: CSV-driven activity, Kafka in KRaft mode without Zookeeper, and bronze, silver and gold layers on MinIO, started with one script."])])),
        links([("Friction platform on GitHub", "https://github.com/kachastepien/ux-friction-detection-platform"), ("Mini data platform", "https://github.com/kachastepien/mini-data-platform")]),
    ],
))

P.append(dict(
    slug="funnel-elt", view="data", kicker="Analytics engineering · SQL · DuckDB",
    title="Where do users drop off?",
    desc="A reproducible SQL ELT by Katarzyna Stępień for product funnel analytics on DuckDB, with a bronze, silver and gold model and six data-quality checks.",
    lede="A reproducible SQL ELT for product conversion-funnel analytics, built on a bronze, silver and gold model and running on DuckDB.",
    tldr=[("The questions", "Which funnel step loses the most people, which device converts best, how much traffic is bots."),
          ("What I built", "One idempotent SQL pipeline: raw tracker JSON in, cleaned tables, then dashboard-ready metrics."),
          ("Quality", "Six explicit data-quality rules, each run as a live check.")],
    chips=["SQL", "DuckDB", "Medallion architecture", "Data quality"],
    hero='<div class="medallion reveal" aria-hidden="true"><span class="b">bronze · raw JSON</span><span class="s">silver · cleaned</span><span class="g">gold · metrics</span></div>',
    body=[
        section("The layers", cards([
            ("Bronze", ["<code>raw_sessions</code> and <code>raw_pages</code>: the tracker JSON loaded as it arrived."]),
            ("Silver", ["<code>clean_sessions</code> and <code>clean_pages</code>: device names normalised, impossible durations nulled, timestamps parsed, missing countries set to UNKNOWN, sessions under 5 seconds flagged as suspicious, and a load timestamp for audit."]),
            ("Gold", ["<code>gold_funnel_metrics</code>: sessions, average duration, CTA clicks, conversions and conversion rate per funnel step, from Awareness to Decision.", "<code>gold_device_metrics</code>: click-through and conversion rate per device."])])),
        section("Data-quality rules", table(["ID", "Risk", "Mitigation"], [
            ("DQ-1", "Null primary keys", "Drop rows with a null session or user id"),
            ("DQ-2", "Inconsistent device casing", "<code>lower(trim(device))</code> in Silver"),
            ("DQ-3", "Unrealistic durations", "Null out values below 0 or above 7,200 s"),
            ("DQ-4", "Unparseable timestamps", "<code>try_cast</code> to NULL instead of failing"),
            ("DQ-5", "Sessions with no matching page", "LEFT JOIN and monitor the unmatched rate"),
            ("DQ-6", "Duplicates on re-runs", "Idempotent rebuild and a load-time audit column")]),
            '<p class="note">The pipeline is idempotent: every section starts with <code>DROP ... IF EXISTS</code>, so it can run any number of times with the same result.</p>'),
        links([("Code on GitHub", "https://github.com/kachastepien/ELT-processes")]),
    ],
))


# ---------- page template ----------
import time
import hashlib
# the stylesheet URL carries a hash of its content, so a changed file always gets a new URL
VER = hashlib.sha1(open(os.path.join(ROOT, "assets", "site.css"), "rb").read()).hexdigest()[:10]


SHORT = {"sidly-health": "SiDLY Health", "sidly-erp": "SiDLY ERP", "lemi": "Lemi", "govbot": "GovBot", "unmasked": "Unmasked",
         "healthplatform": "HealthPlatform", "ux-friction": "UX friction detection", "funnel-elt": "Funnel ELT"}
CHEV = '<svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M3 4.5 6 7.5l3-3"/></svg>'
LEFT = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M13 8H3M7.5 3.5 3 8l4.5 4.5"/></svg>'


def project_menu(cur):
    out = []
    for view, label in (("design", "Product design"), ("data", "Data science")):
        out.append(f'<p class="label">{label}</p>')
        for q in P:
            if q["view"] != view:
                continue
            here = ' aria-current="page"' if q is cur else ""
            out.append(f'<a href="../{q["slug"]}/"{here}><span class="dot {view}"></span>{SHORT[q["slug"]]}</a>')
    out.append(f'<a class="pm-all" href="../../?view={cur["view"]}#work">{LEFT}All work</a>')
    return "".join(out)


def section_menu(body):
    secs = re.findall(r'<section class="cp-sec" id="([^"]+)" data-rail="([^"]+)">', body)
    items = [("overview", "Overview")] + secs
    return "".join(f'<a href="#{i}" data-id="{i}">{t}</a>' for i, t in items)


def page(pr, prv, nxt):
    url = f"{SITE}/work/{pr['slug']}/"
    ld = {
        "@context": "https://schema.org", "@type": "CreativeWork", "name": html.unescape(pr["title"]),
        "description": pr["desc"], "url": url, "inLanguage": "en",
        "author": {"@type": "Person", "@id": SITE + "/#person", "name": "Katarzyna Stępień", "alternateName": "Kacha", "url": SITE + "/"},
        "image": SITE + "/assets/og-portrait.png",
    }
    ld = [ld, {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Katarzyna Stępień", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Work", "item": SITE + "/#work"},
        {"@type": "ListItem", "position": 3, "name": SHORT[pr["slug"]], "item": url}]}]
    body = "\n".join(pr["body"])
    return f"""<!doctype html>
<html lang="en" data-view="{pr['view']}" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="build" content="0">
<script>
/* GitHub Pages lets browsers keep the page for 10 minutes; if a newer build is live, reload once to get it. */
(function(){{try{{var b=document.querySelector('meta[name="build"]').content;fetch('/version.txt?'+Date.now(),{{cache:'no-store'}}).then(function(r){{return r.ok?r.text():''}}).then(function(v){{v=(v||'').trim();if(v&&v!==b&&!sessionStorage.getItem('ks-rl-'+v)){{sessionStorage.setItem('ks-rl-'+v,'1');location.reload()}}}}).catch(function(){{}})}}catch(e){{}}}})();
</script>

<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{pr['title']} · Katarzyna Stępień</title>
<meta name="description" content="{html.escape(pr['desc'])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{pr['title']} · Katarzyna Stępień">
<meta property="og:description" content="{html.escape(pr['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/assets/og-portrait.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#fbfbfa">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<link rel="icon" href="../../favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="../../apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="../../assets/site.css?v={VER}">
<script>document.documentElement.classList.add('js')</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<script data-goatcounter="https://kachastepien.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</head>
<body class="cp">
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"></div>
<header class="top">
  <div class="wrap glass">
    <a class="brand" href="../../" aria-label="Katarzyna Stępień, home"><span class="mark" aria-hidden="true"><i></i><i></i></span><span>Katarzyna Stępień</span></a>
    <nav class="crumb" aria-label="Breadcrumb"><a class="crumb-home" href="../../?view={pr['view']}#work">Work</a><span class="sep" aria-hidden="true">/</span>
      <details class="pmenu"><summary aria-label="Switch project"><span class="dot {pr['view']}"></span><span class="pm-cur">{SHORT[pr['slug']]}</span>{CHEV}</summary><div class="pm-list glass">{project_menu(pr)}</div></details>
    </nav>
    <details class="pmenu smenu"><summary aria-label="Jump to a section"><span class="sm-now">Overview</span>{CHEV}</summary><div class="pm-list glass"><p class="label">On this page</p>{section_menu(body)}</div></details>
    <a class="btn-all" href="../../?view={pr['view']}#work">{LEFT}<span>All work</span></a>
  </div>
</header>
<nav class="rail" aria-label="Sections">{section_menu(body).replace('">', '"><i></i><span>').replace('</a>', '</span></a>')}</nav>
<main id="main">
  <article class="wrap cp-wrap">
    <header class="cp-head" id="overview" data-rail="Overview">
      <p class="label reveal">{pr['kicker']}</p>
      <h1 class="case-title reveal">{pr['title']}</h1>
      <p class="lede reveal d1">{pr['lede']}</p>
      {tldr(pr['tldr'])}
      {chips(pr['chips'], on=2)}
    </header>
    <div class="cp-hero">{pr['hero']}</div>
    {body}
    <nav class="pn reveal" aria-label="More projects">
      <a class="next prev" href="../{prv['slug']}/"><span class="label">Previous</span><b>{SHORT[prv['slug']]}</b><span class="arrow" aria-hidden="true">←</span></a>
      <a class="next" href="../{nxt['slug']}/"><span class="label">Next project</span><b>{SHORT[nxt['slug']]}</b><span class="arrow" aria-hidden="true">→</span></a>
    </nav>
    <p class="pn-all reveal"><a class="back" href="../../?view={pr['view']}#work">{LEFT}See all work</a></p>
  </article>
</main>
<footer class="end" id="contact">
  <div class="wrap">
    <h2 class="reveal">Let's build<br>something <em>useful</em>.</h2>
    <p class="lede reveal d1" style="max-width:30rem">Hiring for product design or data science? Tell me about the role.</p>
    <div class="row reveal d1">
      <a class="btn solid" href="../../#contact">Write to me</a>
      <button class="mailchip" type="button" id="copy-email" aria-label="Copy email address hello@kachastepien.com"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m4 7 8 6 8-6"/></svg><span id="email">hello@kachastepien.com</span><span class="mc"><svg class="ic-copy" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2.5"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg><b>Copy</b></span></button>
        <div class="socials"><a class="soc" href="https://www.linkedin.com/in/kachastepien" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M5 3.5a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM3.3 9h3.4v11H3.3zM9 9h3.3v1.5h.1c.5-.9 1.6-1.8 3.3-1.8 3.5 0 4.1 2.3 4.1 5.3V20h-3.4v-5.3c0-1.3 0-2.9-1.8-2.9s-2.1 1.4-2.1 2.8V20H9z"/></svg>LinkedIn</a><a class="soc" href="https://github.com/kachastepien" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 2.9.8.1-.6.4-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.2-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.5.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z"/></svg>GitHub</a><a class="soc" href="{A}katarzyna-stepien-cv.pdf" download="Katarzyna-Stepien-CV.pdf" data-goatcounter-click="cv-download-footer"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M12 4v11M7 10.5 12 15l5-4.5M5 20h14"/></svg>CV</a></div>
    </div>
    <div class="fine"><span>Katarzyna Stępień · Warsaw</span><span>Hand-built. No cookies.</span></div>
  </div>
</footer>
<script>
(function(){{
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var io='IntersectionObserver' in window?new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target)}}}})}},{{rootMargin:'0px 0px -8% 0px',threshold:.06}}):null;
  document.querySelectorAll('.reveal,.metrics').forEach(function(el){{io?io.observe(el):el.classList.add('in')}});
  var top=document.querySelector('.top'),bar=document.querySelector('.progress');
  function onScroll(){{var h=document.documentElement.scrollHeight-innerHeight;bar.style.transform='scaleX('+(h>0?scrollY/h:0)+')';top.classList.toggle('scrolled',scrollY>8)}}
  addEventListener('scroll',onScroll,{{passive:true}});onScroll();
  var now=document.querySelector('.sm-now'),rail=document.querySelector('.rail'),secs=[].slice.call(document.querySelectorAll('[data-rail]'));
  if('IntersectionObserver' in window){{var spy=new IntersectionObserver(function(es){{es.forEach(function(e){{if(!e.isIntersecting)return;var id=e.target.id;now.textContent=e.target.dataset.rail;
    document.querySelectorAll('[data-id]').forEach(function(a){{a.classList.toggle('on',a.dataset.id===id)}})}})}},{{rootMargin:'-40% 0px -55% 0px'}});secs.forEach(function(x){{spy.observe(x)}})}}
  addEventListener('scroll',function(){{rail.classList.toggle('show',scrollY>innerHeight*.5)}},{{passive:true}});
  var menus=[].slice.call(document.querySelectorAll('details.pmenu'));
  menus.forEach(function(d){{d.addEventListener('toggle',function(){{if(d.open)menus.forEach(function(o){{if(o!==d)o.open=false}})}});d.querySelectorAll('a').forEach(function(a){{a.addEventListener('click',function(){{d.open=false}})}})}});
  document.addEventListener('click',function(e){{menus.forEach(function(d){{if(d.open&&!d.contains(e.target))d.open=false}})}});
  document.addEventListener('keydown',function(e){{if(e.key==='Escape')menus.forEach(function(d){{if(d.open){{d.open=false;d.querySelector('summary').focus()}}}})}});
  document.querySelectorAll('.loop,.flow,.pipe').forEach(function(d){{var h=document.createElement('p');h.className='swipe-hint';h.textContent='Swipe to see the whole flow →';d.parentNode.insertBefore(h,d.nextSibling)}});
  var cb=document.getElementById('copy-email'),em=document.getElementById('email');
  cb.addEventListener('click',function(){{try{{navigator.clipboard.writeText(em.textContent.trim()).then(function(){{cb.classList.add('ok');cb.querySelector('b').textContent='Copied';setTimeout(function(){{cb.classList.remove('ok');cb.querySelector('b').textContent='Copy'}},1800)}})}}catch(e){{}}}});
}})();
</script>
</body>
</html>
"""


def main():
    for i, pr in enumerate(P):
        nxt = P[(i + 1) % len(P)]
        prv = P[i - 1]
        out = os.path.join(ROOT, "work", pr["slug"])
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page(pr, prv, nxt))
        print("built", pr["slug"])


if __name__ == "__main__":
    main()
