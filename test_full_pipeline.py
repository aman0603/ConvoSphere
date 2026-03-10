import asyncio
import aiohttp
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

SESSION_DATA = {
    "name": "Yuvraj Rathi",
    "phone": "+917224848813",
    "context": "he is a college student persuing B.Tech from Jaypee Institute of Information Technology, Noida. He is also working in xspecie",
    "goal": "Understand his interests and see if he would be open to a collaborative project or opportunity",
    "owner_id": "sales_agent_001"
}

CONVERSATION = [
    {"sender": "agent",    "text": "Hey Yuvraj! Saw your GitHub — the BCI Gaming project looks really cool. How's it going?",    "channel": "telegram"},
    {"sender": "customer", "text": "Thanks! Yeah it's a fun side project. Still in early stages but the concept is exciting.",     "channel": "telegram"},
    {"sender": "agent",    "text": "For sure! Are you using EEG headsets for the input? And what game engine?",                   "channel": "telegram"},
    {"sender": "customer", "text": "Yeah using an OpenBCI board and building it in Unity. Lots of signal processing involved.",  "channel": "telegram"},
    {"sender": "agent",    "text": "That's impressive for a student project. Is xspecie related to this or a separate thing?",    "channel": "telegram"},
    {"sender": "customer", "text": "Separate — xspecie is more of a FinTech startup I'm working on with some friends.",           "channel": "telegram"},
    {"sender": "agent",    "text": "FinTech + ML is a great combo. Are you building trading tools or more on the analytics side?", "channel": "telegram"},
    {"sender": "customer", "text": "Analytics and algo trading. We're using quantitative models to identify market patterns.",     "channel": "telegram"},
    {"sender": "agent",    "text": "Awesome. Would you be open to a quick call sometime to explore any potential collaboration?",  "channel": "telegram"},
    {"sender": "customer", "text": "Sure, drop me a message on LinkedIn and we can set something up.",                            "channel": "telegram"},
]

def section(title):
    print(f"\n{'='*60}\n  {title}\n{'='*60}")

def step(msg):
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⚡ {msg}")

def ok(msg):   print(f"  ✅ {msg}")
def warn(msg): print(f"  ⚠️  {msg}")
def info(msg): print(f"  ℹ️  {msg}")

async def main():
    section("🚀 FULL PIPELINE TEST — Yuvraj Rathi")

    async with aiohttp.ClientSession() as http:

        # ── 1. Create session ────────────────────────────────────────────────
        step("Creating session via POST /api/sessions ...")
        async with http.post(f"{API_BASE}/api/sessions", json=SESSION_DATA) as resp:
            if resp.status != 201:
                print(f"  ❌ Failed: {resp.status} — {await resp.text()}")
                return
            session = await resp.json()

        session_id = session["session_id"]
        ok(f"Session created: {session_id}")
        info(f"Customer: {session['customer']['name']} | {session['customer']['phone']}")

        # ── 2. Poll OSINT status ─────────────────────────────────────────────
        section("🔍 OSINT ENRICHMENT — polling every 10s (max 4 min)")
        osint_status = "not started"
        for attempt in range(24):
            await asyncio.sleep(10)
            async with http.get(f"{API_BASE}/api/sessions/{session_id}") as resp:
                s = await resp.json()
            osint_status = s.get("osint", {}).get("status", "unknown")
            print(f"  [{(attempt+1)*10:3d}s] OSINT status: {osint_status}")
            if osint_status in ("completed", "failed"):
                break

        if osint_status == "completed":
            ok("OSINT enrichment completed!")
            osint   = s.get("osint", {}).get("data", {})
            final   = osint.get("final_summary", {})
            if final:
                p  = final.get("person_profile", {}).get("basic_info", {})
                si = final.get("sales_intelligence", {})
                print(f"\n  📋 Person Profile:")
                info(f"Name:        {p.get('name','N/A')}")
                info(f"Role:        {p.get('current_role','N/A')}")
                info(f"Company:     {p.get('company','N/A')}")
                info(f"Location:    {p.get('location','N/A')}")
                info(f"Confidence:  {final.get('confidence_score','N/A')}")
                info(f"Verified:    {final.get('verification_status','N/A')}")
                ct = final.get("person_profile",{}).get("contact_info",{})
                info(f"LinkedIn:    {ct.get('linkedin','N/A')}")
                info(f"Twitter:     {ct.get('twitter','N/A')}")
                if si.get("talking_points"):
                    print("\n  🗣️  Talking Points:")
                    for i, pt in enumerate(si["talking_points"][:3], 1):
                        print(f"     {i}. {pt}")
                if si.get("interests"):
                    info(f"Interests: {', '.join(si['interests'][:4])}")
        elif osint_status == "failed":
            warn(f"OSINT failed: {s.get('osint',{}).get('error','unknown')}")
        else:
            warn(f"OSINT still '{osint_status}' after 4 min — proceeding anyway")

        # ── 3. Inject conversation ───────────────────────────────────────────
        section("💬 CONVERSATION — injecting messages (3s apart)")
        for i, msg in enumerate(CONVERSATION, 1):
            async with http.post(f"{API_BASE}/api/sessions/{session_id}/messages", json=msg) as resp:
                status_icon = "✅" if resp.status == 200 else "❌"
                print(f"  [{i:02d}] {status_icon} [{msg['sender'].upper():8s}] {msg['text'][:65]}")
            await asyncio.sleep(3)
        ok(f"All {len(CONVERSATION)} messages injected")

        # ── 4. Wait for Gemini auto-analysis ────────────────────────────────
        section("🤖 GEMINI ANALYSIS — waiting 20s for auto-trigger")
        await asyncio.sleep(20)

        async with http.get(f"{API_BASE}/api/sessions/{session_id}") as resp:
            final_session = await resp.json()

        gemini = final_session.get("gemini", {})
        r = gemini.get("response", {})
        if r:
            ok("Gemini analysis available!")
            a = r.get("analysis", {})
            t = r.get("tracker", {})
            st = r.get("strategy", {})
            ob = r.get("objections", {})
            if a:
                print(f"\n  📊 Analysis:")
                info(f"Stage:     {a.get('current_stage','N/A')}")
                info(f"Mode:      {a.get('client_mode','N/A')}")
                info(f"Critique:  {str(a.get('salesperson_critique','N/A'))[:120]}")
            if t:
                print(f"\n  🎯 BANT Tracker:")
                info(f"Trust:     {t.get('trust_level','N/A')}")
                info(f"Budget:    {t.get('budget_clarity','N/A')}")
                info(f"Pain pts:  {t.get('pain_points_discovered',[])[:2]}")
            if st:
                print(f"\n  💡 Strategy:")
                info(f"Next msg:  {str(st.get('suggested_next_message','N/A'))[:120]}")
                info(f"Hook:      {str(st.get('personal_hook','N/A'))[:100]}")
            if ob:
                print(f"\n  🛡️  Objections:")
                info(f"Predicted: {ob.get('predicted_next','N/A')}")
                info(f"Tactic:    {str(ob.get('preemptive_tactic','N/A'))[:100]}")
        else:
            warn("No Gemini response yet")

        # ── 5. Final summary ────────────────────────────────────────────────
        section("✅ PIPELINE COMPLETE")
        ok(f"Session ID:  {session_id}")
        ok(f"OSINT:       {osint_status}")
        ok(f"Messages:    {len(CONVERSATION)} injected")
        ok(f"Gemini:      {'active' if r else 'pending'}")
        print(f"\n  🌐 View in frontend: http://localhost:5173\n")

if __name__ == "__main__":
    asyncio.run(main())
