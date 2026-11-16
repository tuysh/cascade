#!/usr/bin/env python3
"""Screenshot harness: Firefox 160 + a userChrome folder under Xvfb, driven by Marionette.

usage: ffshot.py --chrome DIR --steps steps.json [--pref k=v ...] [--size WxH] [--display N]

steps.json is a list of steps:
  {"js": "chrome-context JS, may `return` a value"}
  {"wait": 500}                       milliseconds
  {"shot": "/abs/out.png"}            full X screen (includes popups/menus)
  {"shot": "/abs/out.png", "crop": "WxH+X+Y"}
  {"move": [x, y]}                    synthesize a mouse move in the browser window (hover)
  {"key": "a", "mods": {"accelKey": true}}  synthesize a key in the browser window
"""
import argparse, json, os, shutil, socket, subprocess, sys, tempfile, time

SP = os.environ.get("CASCADE_HARNESS_DIR", "/tmp/cascade-harness")
FF = os.environ.get("FIREFOX_BIN", SP + "/firefox/bin/FirefoxApp/firefox")

BASE_PREFS = {
    "toolkit.legacyUserProfileCustomizations.stylesheets": True,
    "browser.shell.checkDefaultBrowser": False,
    "browser.startup.homepage_override.mstone": "ignore",
    "browser.startup.page": 0,
    "browser.startup.homepage": "about:blank",
    "browser.newtabpage.enabled": False,
    "browser.aboutwelcome.enabled": False,
    "trailhead.firstrun.didSeeAboutWelcome": True,
    "datareporting.policy.dataSubmissionEnabled": False,
    "datareporting.healthreport.uploadEnabled": False,
    "toolkit.telemetry.enabled": False,
    "app.update.disabledForTesting": True,
    "browser.tabs.warnOnClose": False,
    "browser.warnOnQuit": False,
    "browser.sessionstore.resume_from_crash": False,
    "browser.uitour.enabled": False,
    "extensions.autoDisableScopes": 0,
    "browser.translations.automaticallyPopup": False,
    "sidebar.notification.badge.aichat": False,
    "browser.ml.chat.enabled": False,
    # keep the browser off the network entirely
    "network.proxy.type": 1,
    "network.proxy.http": "127.0.0.1",
    "network.proxy.http_port": 9,
    "network.proxy.ssl": "127.0.0.1",
    "network.proxy.ssl_port": 9,
    "network.proxy.allow_hijacking_localhost": False,
    "browser.search.suggest.enabled": False,
    "browser.urlbar.suggest.quicksuggest.sponsored": False,
    "browser.urlbar.suggest.quicksuggest.nonsponsored": False,
    "services.settings.server": "http://127.0.0.1:9/",
    "browser.safebrowsing.malware.enabled": False,
    "browser.safebrowsing.phishing.enabled": False,
    "extensions.update.enabled": False,
    "extensions.getAddons.cache.enabled": False,
    "media.gmp-manager.url": "http://127.0.0.1:9/",
    "browser.region.network.url": "",
    "marionette.port": 0,
}


class Marionette:
    def __init__(self, port):
        for _ in range(200):
            try:
                self.s = socket.create_connection(("127.0.0.1", port), timeout=60)
                break
            except OSError:
                time.sleep(0.1)
        else:
            raise RuntimeError("marionette did not come up")
        self.id = 0
        self._read()

    def _read(self):
        buf = b""
        while b":" not in buf:
            buf += self.s.recv(1)
        n, rest = buf.split(b":", 1)
        n = int(n)
        while len(rest) < n:
            rest += self.s.recv(n - len(rest))
        return json.loads(rest)

    def cmd(self, name, params=None):
        self.id += 1
        data = json.dumps([0, self.id, name, params or {}]).encode()
        self.s.sendall(str(len(data)).encode() + b":" + data)
        while True:
            r = self._read()
            if r[0] == 1 and r[1] == self.id:
                if r[2]:
                    raise RuntimeError(f"{name}: {r[2]}")
                return r[3]


def jsval(v):
    return json.dumps(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chrome", required=True)
    ap.add_argument("--steps", required=True)
    ap.add_argument("--pref", action="append", default=[])
    ap.add_argument("--size", default="1400x800")
    ap.add_argument("--display", default="99")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    w, h = map(int, a.size.split("x"))

    os.makedirs(SP, exist_ok=True)
    prof = tempfile.mkdtemp(prefix="ffprof-", dir=SP)
    shutil.copytree(a.chrome, prof + "/chrome")
    prefs = dict(BASE_PREFS)
    for p in a.pref:
        k, v = p.split("=", 1)
        try:
            v = json.loads(v)
        except json.JSONDecodeError:
            pass
        prefs[k] = v
    with open(prof + "/user.js", "w") as f:
        for k, v in prefs.items():
            f.write(f"user_pref({jsval(k)}, {jsval(v)});\n")
    # xulstore: window size
    with open(prof + "/xulstore.json", "w") as f:
        json.dump({"chrome://browser/content/browser.xhtml": {"main-window": {
            "screenX": "0", "screenY": "0", "width": str(w), "height": str(h), "sizemode": "normal"}}}, f)

    disp = ":" + a.display
    xvfb = subprocess.Popen(["Xvfb", disp, "-screen", "0", f"{w}x{h}x24", "-nolisten", "tcp"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    env = dict(os.environ, DISPLAY=disp, MOZ_ENABLE_WAYLAND="0", MOZ_CRASHREPORTER_DISABLE="1",
               HOME=prof, XDG_RUNTIME_DIR=prof, NO_AT_BRIDGE="1", MOZ_REMOTE_ALLOW_SYSTEM_ACCESS="1")
    for k in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy", "ALL_PROXY", "all_proxy"):
        env.pop(k, None)
    log = open(prof + "/firefox.log", "w")
    ff = subprocess.Popen([FF, "--profile", prof, "--no-remote", "--marionette", "--width", str(w), "--height", str(h)],
                          env=env, stdout=log, stderr=subprocess.STDOUT)
    out = {}
    try:
        port = None
        for _ in range(300):
            try:
                with open(prof + "/MarionetteActivePort") as f:
                    port = int(f.read().strip())
                break
            except (OSError, ValueError):
                time.sleep(0.1)
        if not port:
            raise RuntimeError("no MarionetteActivePort")
        m = Marionette(port)
        m.cmd("WebDriver:NewSession", {"capabilities": {}})
        m.cmd("Marionette:SetContext", {"value": "chrome"})
        # make sure the window fills the screen
        m.cmd("WebDriver:ExecuteScript", {"script": f"window.resizeTo({w},{h}); window.moveTo(0,0);", "args": []})
        time.sleep(1.0)
        steps = json.load(open(a.steps))
        for i, s in enumerate(steps):
            if "js" in s:
                r = m.cmd("WebDriver:ExecuteScript", {"script": s["js"], "args": [], "sandbox": None})
                if r and r.get("value") is not None:
                    out[f"step{i}"] = r["value"]
                    print(f"[step {i}]", json.dumps(r["value"])[:4000])
            elif "wait" in s:
                time.sleep(s["wait"] / 1000)
            elif "move" in s:
                x, y = s["move"]
                subprocess.run(["xdotool", "mousemove", str(int(x)), str(int(y))], env=dict(os.environ, DISPLAY=disp))
            elif "click_js" in s:
                r = m.cmd("WebDriver:ExecuteScript", {"script": s["click_js"], "args": []})
                x, y = r["value"]
                subprocess.run(["xdotool", "mousemove", str(int(x)), str(int(y)), "click", str(s.get("button", 1))], env=dict(os.environ, DISPLAY=disp))
            elif "xkey" in s:
                subprocess.run(["xdotool", "key"] + s["xkey"].split(), env=dict(os.environ, DISPLAY=disp))
            elif "hover_js" in s:
                r = m.cmd("WebDriver:ExecuteScript", {"script": s["hover_js"], "args": []})
                x, y = r["value"]
                subprocess.run(["xdotool", "mousemove", str(int(x)), str(int(y))], env=dict(os.environ, DISPLAY=disp))
            elif "key" in s:
                mods = s.get("mods", {})
                m.cmd("WebDriver:ExecuteScript", {"script": f"EventUtils_synth({jsval(s['key'])}, {jsval(mods)});".replace(
                    "EventUtils_synth", "(function(k,m){const e=new KeyboardEvent('keydown',Object.assign({key:k,bubbles:true},m));document.dispatchEvent(e);})"), "args": []})
            elif "shot" in s:
                cmd = ["import", "-display", disp, "-window", "root"]
                if s.get("crop"):
                    cmd += ["-crop", s["crop"]]
                subprocess.run(cmd + [s["shot"]], check=True)
                print("shot", s["shot"])
        try:
            m.cmd("Marionette:Quit", {"flags": ["eForceQuit"]})
        except Exception:
            pass
    finally:
        try:
            ff.wait(timeout=10)
        except subprocess.TimeoutExpired:
            ff.kill()
        xvfb.kill()
        log.close()
        if not a.keep:
            shutil.rmtree(prof, ignore_errors=True)
        else:
            print("profile kept at", prof)


if __name__ == "__main__":
    main()
