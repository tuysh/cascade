#!/usr/bin/env python3
"""Run a set of named scenarios against a chrome/ folder and write screenshots.

usage: scenarios.py --chrome DIR --label NAME [--only a,b,c] [--jobs N]
shots land in harness/shots/NAME/<scenario>.png
"""
import argparse, json, os, subprocess, sys, concurrent.futures as cf

H = os.environ.get("CASCADE_HARNESS_DIR", "/tmp/cascade-harness")
HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = H + "/pages"
os.makedirs(PAGES, exist_ok=True)
TITLES = [
    ("cascade", "Cascade — userChrome", "#f6f6f6"),
    ("notes", "Firefox 160 release notes", "#ffffff"),
    ("hn", "Hacker News", "#f6f6ef"),
    ("rust", "Rust documentation", "#ffffff"),
    ("wiki", "Wikipedia, the free encyclopedia", "#ffffff"),
    ("mail", "Inbox (3) — Mail", "#fafafa"),
    ("music", "Music player", "#101010"),
]
for slug, t, bg in TITLES:
    fg = "#eee" if bg == "#101010" else "#111"
    with open(f"{PAGES}/{slug}.html", "w") as f:
        f.write(f'<!doctype html><meta charset="utf-8"><title>{t}</title><body style="margin:0;background:{bg};color:{fg};font:16px sans-serif;padding:40px"><h1>{t}</h1><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p><p><input placeholder="a text field"> <button>A button</button></p></body>')

PRELUDE = r"""
document.documentElement.removeAttribute('remotecontrol');
const P = %s;
const url = s => 'file://' + P + '/' + s + '.html';
""" % json.dumps(PAGES)

OPEN5 = PRELUDE + r"""
for (const s of ['cascade','notes','hn','rust','wiki']) gBrowser.addTrustedTab(url(s));
gBrowser.removeTab(gBrowser.tabs[0]);
gBrowser.selectedTab = gBrowser.tabs[1];
"""

def steps(js_list, shots):
    out = []
    for item in js_list:
        if isinstance(item, int):
            out.append({"wait": item})
        elif isinstance(item, dict):
            out.append(item)
        else:
            out.append({"js": item})
    return out

SC = {}
def sc(name, prefs=(), size="1400x800", seq=()):
    SC[name] = dict(prefs=list(prefs), size=size, seq=list(seq))

DARK = ["ui.systemUsesDarkTheme=1"]
LIGHT = ["ui.systemUsesDarkTheme=0"]

sc("dark", DARK, seq=[OPEN5, 2500, "SHOT"])
sc("light", LIGHT, seq=[OPEN5, 2500, "SHOT"])
sc("urlbar-open", DARK, seq=[OPEN5, 2500, PRELUDE + "gURLBar.focus(); gURLBar.search('c');", 2000, "SHOT"])
sc("urlbar-open-light", LIGHT, seq=[OPEN5, 2500, PRELUDE + "gURLBar.focus(); gURLBar.search('c');", 2000, "SHOT"])
sc("urlbar-focus", DARK, seq=[OPEN5, 2500, PRELUDE + "gURLBar.focus(); gURLBar.select();", 1200, "SHOT"])
sc("appmenu", DARK, seq=[OPEN5, 2500, PRELUDE + "PanelUI.show();", 1500, "SHOT"])
sc("appmenu-light", LIGHT, seq=[OPEN5, 2500, PRELUDE + "PanelUI.show();", 1500, "SHOT"])
CENTER = "const r = %s.getBoundingClientRect(); return [window.mozInnerScreenX + r.x + r.width/2, window.mozInnerScreenY + r.y + r.height/2];"
sc("tab-context", DARK, seq=[OPEN5, 2500, {"click_js": CENTER % "gBrowser.tabs[2]", "button": 3}, 1500, "SHOT"])
sc("tab-context-light", LIGHT, seq=[OPEN5, 2500, {"click_js": CENTER % "gBrowser.tabs[2]", "button": 3}, 1500, "SHOT"])
sc("hover", DARK, seq=[OPEN5, 2500, {"hover_js": "const r = gBrowser.tabs[3].getBoundingClientRect(); return [window.mozInnerScreenX + r.x + r.width/2, window.mozInnerScreenY + r.y + r.height/2];"}, 800, "SHOT"])
sc("hover-button", DARK, seq=[OPEN5, 2500, {"hover_js": "const r = document.getElementById('reload-button').getBoundingClientRect(); return [window.mozInnerScreenX + r.x + r.width/2, window.mozInnerScreenY + r.y + r.height/2];"}, 800, "SHOT"])
sc("focus-ring", DARK, seq=[OPEN5, 2500, PRELUDE + "Services.focus.setFocus(document.getElementById('reload-button'), Services.focus.FLAG_BYKEY);", 800, "SHOT"])
sc("tab-focus-ring", DARK, seq=[OPEN5, 2500, PRELUDE + "gBrowser.tabContainer.ariaFocusedItem = gBrowser.tabs[3]; Services.focus.setFocus(gBrowser.selectedTab, Services.focus.FLAG_BYKEY);", 800, "SHOT"])
sc("compact", DARK + ["browser.compactmode.show=true", "browser.uidensity=1"], seq=[OPEN5, 2500, "SHOT"])
sc("touch", DARK + ["browser.uidensity=2"], seq=[OPEN5, 2500, "SHOT"])
sc("narrow", DARK, size="950x650", seq=[OPEN5, 2500, "SHOT"])
sc("nova-off", DARK + ["browser.nova.enabled=false"], seq=[OPEN5, 2500, "SHOT"])
sc("nova-off-urlbar", DARK + ["browser.nova.enabled=false"], seq=[OPEN5, 2500, PRELUDE + "gURLBar.focus(); gURLBar.search('c');", 2000, "SHOT"])
sc("vertical", DARK + ["sidebar.revamp=true", "sidebar.verticalTabs=true"], seq=[OPEN5, 3000, "SHOT"])
sc("vertical-light", LIGHT + ["sidebar.revamp=true", "sidebar.verticalTabs=true"], seq=[OPEN5, 3000, "SHOT"])
sc("vertical-collapsed", DARK + ["sidebar.revamp=true", "sidebar.verticalTabs=true", "sidebar.visibility=\"always-show\""], seq=[OPEN5, 3000, PRELUDE + "SidebarController._state.launcherExpanded = false;", 1500, "SHOT"])
sc("groups", DARK, seq=[OPEN5 + "gBrowser.addTrustedTab(url('mail')); gBrowser.addTrustedTab(url('music'));", 2000,
    PRELUDE + "gBrowser.addTabGroup([gBrowser.tabs[2], gBrowser.tabs[3]], {color: 'blue', label: 'Work', insertBefore: gBrowser.tabs[2]}); const g = gBrowser.addTabGroup([gBrowser.tabs[5], gBrowser.tabs[6]], {color: 'orange', label: 'Fun', insertBefore: gBrowser.tabs[5]}); g.collapsed = true; gBrowser.pinTab(gBrowser.tabs[0]);", 2000, "SHOT"])
sc("split", DARK, seq=[OPEN5, 2500, PRELUDE + "gBrowser.addTabSplitView([gBrowser.tabs[1], gBrowser.tabs[2]], {insertBefore: gBrowser.tabs[1]}); gBrowser.selectedTab = gBrowser.tabs[1];", 2500, "SHOT"])
sc("containers", DARK + ["privacy.userContext.enabled=true", "privacy.userContext.ui.enabled=true"], seq=[PRELUDE + "for (const [s,id] of [['cascade',1],['notes',2],['hn',3],['rust',4],['wiki',0]]) gBrowser.addTrustedTab(url(s), {userContextId: id}); gBrowser.removeTab(gBrowser.tabs[0]); gBrowser.selectedTab = gBrowser.tabs[1];", 3000, "SHOT"])
sc("bookmarks", DARK + ["browser.toolbars.bookmarks.visibility=\"always\""], seq=[OPEN5, 2500, "SHOT"])
sc("private", DARK + ["browser.privatebrowsing.autostart=true"], seq=[OPEN5, 2500, "SHOT"])
sc("many-tabs", DARK, seq=[PRELUDE + "for (let i = 0; i < 30; i++) gBrowser.addTrustedTab(url(['cascade','notes','hn','rust','wiki'][i%5])); gBrowser.removeTab(gBrowser.tabs[0]); gBrowser.selectedTab = gBrowser.tabs[12];", 3500, "SHOT"])
sc("downloads-panel", DARK, seq=[OPEN5, 2500, PRELUDE + "DownloadsPanel.showPanel();", 1500, "SHOT"])
sc("findbar", DARK, seq=[OPEN5, 2500, PRELUDE + "gLazyFindCommand('onFindCommand');", 1500, "SHOT"])
sc("sidebar-bookmarks", DARK + ["sidebar.revamp=true"], seq=[OPEN5, 2500, PRELUDE + "SidebarController.show('viewBookmarksSidebar');", 2000, "SHOT"])
sc("status", DARK, seq=[OPEN5, 2500, PRELUDE + "XULBrowserWindow.setOverLink('https://example.com/some/long/link/target');", 800, "SHOT"])
sc("customize", DARK, seq=[OPEN5, 2500, PRELUDE + "gCustomizeMode.enter();", 3500, "SHOT"])
sc("menubar", DARK, seq=[OPEN5, 2500, PRELUDE + "setToolbarVisibility(document.getElementById('toolbar-menubar'), true);", 1500, "SHOT"])
sc("notification", DARK, seq=[OPEN5, 2500, PRELUDE + "gNotificationBox.appendNotification('test', {label: 'Firefox is not your default browser', priority: gNotificationBox.PRIORITY_INFO_MEDIUM}, [{label: 'Set as default'}]);", 1500, "SHOT"])
sc("identity-panel", DARK, seq=[OPEN5, 2500, {"click_js": CENTER % "document.getElementById('identity-icon-box')"}, 1500, "SHOT"])
sc("keyboard-nav", DARK, seq=[OPEN5, 2500, PRELUDE + "gURLBar.focus();", 500, {"xkey": "shift+Tab"}, 400, "SHOT"])


def run(chrome, label, name, display):
    s = SC[name]
    outdir = f"{H}/shots/{label}"
    os.makedirs(outdir, exist_ok=True)
    seq = []
    for it in s["seq"]:
        if it == "SHOT":
            seq.append({"shot": f"{outdir}/{name}.png"})
        elif isinstance(it, int):
            seq.append({"wait": it})
        elif isinstance(it, dict):
            seq.append(it)
        else:
            seq.append({"js": it})
    sf = f"{H}/steps-{label}-{name}.json"
    json.dump(seq, open(sf, "w"))
    cmd = [sys.executable, "-I", f"{HERE}/ffshot.py", "--chrome", chrome, "--steps", sf, "--size", s["size"], "--display", str(display)]
    for p in s["prefs"]:
        cmd += ["--pref", p]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    ok = r.returncode == 0
    return name, ok, (r.stdout + r.stderr)[-600:] if not ok else ""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chrome", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    names = [n for n in SC if not a.only or n in a.only.split(",")]
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = [ex.submit(run, a.chrome, a.label, n, 100 + i) for i, n in enumerate(names)]
        for f in cf.as_completed(futs):
            n, ok, err = f.result()
            print(("ok  " if ok else "FAIL") + " " + n + ("\n" + err if err else ""))
