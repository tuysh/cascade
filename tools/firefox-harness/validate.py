#!/usr/bin/env python3
"""Ask the real Firefox whether every selector and declaration of the theme is valid.

usage: validate.py [files...]   (default: chrome/includes/*.css integrations/*/*.css)

Firefox does not report parse errors of userChrome.css anywhere, and an invalid
declaration is silently dropped. This extracts every selector and declaration and
checks it with CSS.supports() inside Firefox (see ffshot.py for the setup).
Values that contain var() are only checked when used, so they always pass here.
"""
import glob, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
def strip_comments(s):
    out=[]; i=0
    while i < len(s):
        if s.startswith('/*', i):
            j=s.find('*/', i+2); seg=s[i:j+2]; out.append(re.sub(r'[^\n]', ' ', seg)); i=j+2
        else:
            out.append(s[i]); i+=1
    return ''.join(out)
items=[]
def parse(src, fname):
    s=strip_comments(src)
    stack=[]  # preludes
    buf=''; start=0; i=0; depth=0
    def lineno(pos): return s.count('\n',0,pos)+1
    while i < len(s):
        c=s[i]
        if c=='(':  # skip balanced parens (selectors like :not(...), values like calc(...))
            d=1; j=i+1
            while j<len(s) and d: 
                if s[j]=='(': d+=1
                elif s[j]==')': d-=1
                j+=1
            buf+=s[i:j]; i=j; continue
        if c=='{':
            pre=buf.strip(); stack.append(pre)
            if pre and not pre.startswith('@'):
                items.append({'f':fname,'l':lineno(i),'k':'sel','v':pre})
            buf=''; i+=1; continue
        if c=='}':
            d=buf.strip()
            if d and ':' in d: add_decl(d, fname, lineno(i))
            buf=''; stack.pop() if stack else None; i+=1; continue
        if c==';':
            d=buf.strip()
            if d.startswith('@'): pass
            elif d and ':' in d: add_decl(d, fname, lineno(i))
            buf=''; i+=1; continue
        buf+=c; i+=1
def add_decl(d, fname, ln):
    prop, _, val = d.partition(':')
    prop=prop.strip(); val=val.strip()
    imp = val.endswith('!important')
    if imp: val=val[:-len('!important')].strip()
    items.append({'f':fname,'l':ln,'k':'decl','p':prop,'v':val})


def split_top(s):
    parts, d, cur = [], 0, ""
    for c in s:
        d += c == "("
        d -= c == ")"
        if c == "," and d == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


JS = r"""
const items = %s;
const bad = [];
for (const it of items) {
  if (it.k === 'sel') {
    let sel = it.v;
    if (/^[>+~]/.test(sel)) sel = 'div ' + sel;
    sel = sel.replace(/&/g, 'div');
    let ok = false;
    try { ok = CSS.supports('selector(' + sel + ')'); } catch (e) {}
    if (!ok) bad.push(it.f + ':' + it.l + '  selector  ' + it.v);
  } else if (!it.p.startsWith('--')) {
    let ok = false;
    try { ok = CSS.supports(it.p, it.v); } catch (e) {}
    if (!ok) bad.push(it.f + ':' + it.l + '  ' + it.p + ': ' + it.v);
  }
}
return bad;
"""

if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(f"{REPO}/chrome/includes/*.css") + glob.glob(f"{REPO}/integrations/*/*.css"))
    for f in files:
        parse(open(f).read(), os.path.relpath(f, REPO))
    checks = []
    for it in items:
        if it["k"] == "sel":
            checks += [{**it, "v": p} for p in split_top(it["v"])]
        elif it["p"] not in ("syntax", "inherits", "initial-value"):  # @property descriptors
            checks.append(it)
    steps = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump([{"wait": 1500}, {"js": JS % json.dumps(checks)}], steps)
    steps.close()
    with tempfile.TemporaryDirectory() as empty:
        r = subprocess.run([sys.executable, "-I", f"{HERE}/ffshot.py", "--chrome", empty, "--steps", steps.name],
                           capture_output=True, text=True)
    line = next((l for l in r.stdout.splitlines() if l.startswith("[step 1]")), None)
    if line is None:
        sys.exit(r.stdout + r.stderr)
    bad = json.loads(line[len("[step 1] "):])
    print(f"{len(checks)} selectors and declarations checked, {len(bad)} invalid")
    print("\n".join(bad))
    sys.exit(1 if bad else 0)
