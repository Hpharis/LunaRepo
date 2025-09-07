# --- agent_runner.py (path-robust) ---
import os, sys, subprocess, json, time, re, shutil, argparse
from pathlib import Path
import requests

def sh(cmd, cwd=None, env=None, check=True, timeout=None):
    """Run a shell command, stream stdout live, optional timeout."""
    print(f"\n$ {cmd}  (cwd={cwd})")
    # ensure unbuffered python so logs show up immediately
    if cmd.strip().startswith("python "):
        cmd = cmd.replace("python ", "python -u ", 1)
    elif cmd.strip().startswith("python.exe "):
        cmd = cmd.replace("python.exe ", "python.exe -u ", 1)

    p = subprocess.Popen(
        cmd, cwd=cwd, env=env, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1
    )
    try:
        for line in p.stdout:
            print(line, end="")
        rc = p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print("\nERROR: command timed out — killing process.")
        p.kill()
        rc = -1

    if check and rc != 0:
        raise RuntimeError(f"Command failed (rc={rc}): {cmd}")
    return rc

# ---------- arg-driven roots (NO auto-detect) ----------
ap = argparse.ArgumentParser(description="TouringMag agent (path-robust)")
ap.add_argument("--site",   required=True, help="Path to touringmag-site (folder with src/ and public/)")
ap.add_argument("--engine", required=True, help="Path to Goldloop engine (folder with scripts/run_goldloop.py)")
args = ap.parse_args()

SITE     = Path(args.site).resolve()
GOLDLOOP = Path(args.engine).resolve()
ROOT     = SITE.parent

# sanity checks
if not (SITE / "src").exists() or not (SITE / "public").exists():
    raise SystemExit(f"Bad --site: {SITE} (missing src/ or public/)")
if not (GOLDLOOP / "scripts" / "run_goldloop.py").exists():
    raise SystemExit(f"Bad --engine: {GOLDLOOP} (missing scripts/run_goldloop.py)")

print("DEBUG — SITE   =", SITE)
print("DEBUG — ROOT   =", ROOT)
print("DEBUG — ENGINE =", GOLDLOOP)

# common subpaths
CONTENT      = SITE / "src" / "content"
PAGES        = SITE / "src" / "pages"
BASE_LAYOUT  = SITE / "src" / "layouts" / "BaseLayout.astro"
CONTENT_CFG  = SITE / "src" / "content.config.ts"
VERCEL       = shutil.which("vercel") or "npx vercel"

# put near the top of agent_runner.py
def load_env_kv(path: Path) -> dict:
    """Parse a simple .env file (KEY=VALUE, ignore blank lines/#)."""
    kv = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line: 
                continue
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip().strip('"').strip("'")
    return kv


def find_astro_config(site_dir: Path) -> Path:
    for ext in ("mjs", "ts", "cjs"):
        p = site_dir / f"astro.config.{ext}"
        if p.exists(): return p
    raise RuntimeError(f"No astro.config.(mjs|ts|cjs) under {site_dir}")

def patch_astro_config():
    astro_cfg = find_astro_config(SITE)
    print("DEBUG — ASTRO_CONFIG =", astro_cfg)
    txt = astro_cfg.read_text(encoding="utf-8")
    txt = re.sub(r"import\s+vercel\s+from\s+['\"]@astrojs/vercel/serverless['\"]\s*;?\s*\n", "", txt)
    if "from '@astrojs/vercel'" not in txt:
        txt = "import vercel from '@astrojs/vercel';\n" + txt
    if "adapter:" not in txt:
        txt = txt.replace("export default defineConfig({", "export default defineConfig({\n  adapter: vercel(),")
    astro_cfg.write_text(txt, encoding="utf-8")

def ensure_dirs():
    (SITE / "public" / "assets").mkdir(parents=True, exist_ok=True)
    CONTENT.mkdir(parents=True, exist_ok=True)

def ensure_getstaticpaths(section):
    f = PAGES / section / "[slug].astro"
    if not f.exists(): return
    s = f.read_text(encoding="utf-8")
    sig = "export async function getStaticPaths()"
    if sig in s:
        if "export const prerender" not in s:
            s = s.replace(sig, "export const prerender = true;\n\n" + sig)
        f.write_text(s, encoding="utf-8"); return

    block = f"""
export async function getStaticPaths() {{
  const entries = await getCollection("{section}");
  return entries.map((e) => ({{ params: {{ slug: e.slug }} }}));
}}
export const prerender = true;
"""
    if re.search(r"^---\s*$", s, flags=re.M):
        s = re.sub(r"(^---\s*\n)", r"\1" + block + "\n", s, count=1, flags=re.M)
    else:
        s = block + "\n" + s
    f.write_text(s, encoding="utf-8")

def patch_routes_and_schemas():
    if CONTENT_CFG.exists():
        s = CONTENT_CFG.read_text(encoding="utf-8")

        def add_fields(block: str) -> str:
            need_thumb = "thumbnail:" not in block
            need_aff  = "affiliateLink:" not in block
            if need_thumb or need_aff:
                # insert after heroImage line (keeps order) — safe & idempotent
                block = re.sub(
                    r"(heroImage:\s*z\.string\(\)\.optional\(\),)",
                    lambda m: m.group(1)
                    + ("\n    thumbnail: z.string().optional()," if need_thumb else "")
                    + ("\n    affiliateLink: z.string().optional()," if need_aff else ""),
                    block,
                    count=1,
                )
            return block

        s = re.sub(r"(defineCollection\(\{[\s\S]*?\}\)\);)", lambda m: add_fields(m.group(0)), s)
        CONTENT_CFG.write_text(s, encoding="utf-8")

    for sec in ["blog","gear","guides","upgrades"]:
        ensure_getstaticpaths(sec)

def ensure_adsense_in_head():
    if not BASE_LAYOUT.exists(): return
    s = BASE_LAYOUT.read_text(encoding="utf-8")
    if "pagead2.googlesyndication.com" not in s:
        s = s.replace("<head>", "<head>\n  <script async src=\"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXX\" crossorigin=\"anonymous\"></script>")
    if "not affiliated with Harley-Davidson" not in s:
        s = s.replace("</footer>", '<p class="italic mt-2">Independently operated — not affiliated with Harley-Davidson.</p>\n</footer>')
    BASE_LAYOUT.write_text(s, encoding="utf-8")

# replace your run_goldloop() with this:
def run_goldloop():
    env = os.environ.copy()

    # load keys from .env files if present (engine first, then repo root, then site)
    for p in [GOLDLOOP / ".env", ROOT / ".env", SITE / ".env"]:
        env.update(load_env_kv(p))

    if not env.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in process env or .env files.")

    # run unbuffered so you see live logs; 10-minute ceiling to avoid hangs
    cmd = "python -u scripts/run_goldloop.py all"
    sh(cmd, cwd=GOLDLOOP, env=env, check=True, timeout=600)

def find_generated_content_src() -> Path:
    cand = [
        GOLDLOOP / "touringmag-site" / "src" / "content",
        GOLDLOOP / "output" / "content",
        SITE / "src" / "content",
    ]
    for c in cand:
        if c.exists() and any(c.rglob("*.md")): return c
    raise RuntimeError("No generated Markdown found. Tried:\n  " + "\n  ".join(str(p) for p in cand))

def copy_content():
    src = find_generated_content_src()
    print("DEBUG — GENERATED CONTENT SOURCE =", src)
    for sec in ["blog","gear","guides","upgrades"]:
        (CONTENT / sec).mkdir(parents=True, exist_ok=True)
        s = src / sec
        if not s.exists(): 
            print(f"NOTE: no source {s}")
            continue
        for f in s.rglob("*.md"):
            (CONTENT / sec / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    print("Content sync complete →", CONTENT)

def npm_install_and_build():
    def kill_lockers():
        try:
            subprocess.run('powershell -NoProfile "Get-Process node,esbuild,rollup -ErrorAction SilentlyContinue | Stop-Process -Force"', shell=True)
        except: pass

    def clean_modules():
        # remove attrs and delete node_modules
        subprocess.run(r'powershell -NoProfile "attrib -R /S /D \"{}\\*\" "'.format(SITE), shell=True)
        subprocess.run(f'npx rimraf "{SITE}\\node_modules"', shell=True)

    # first attempt
    rc = sh("npm ci", cwd=SITE, check=False)
    if rc != 0:
        print("npm ci failed — attempting Windows EPERM recovery…")
        kill_lockers(); clean_modules()
        rc = sh("npm ci", cwd=SITE, check=False)
        if rc != 0:
            print("npm ci still failing — falling back to npm install")
            rc = sh("npm install", cwd=SITE, check=True)

    sh("npm run build", cwd=SITE, check=False)
    # auto-fix missing getStaticPaths once, then rebuild
    if "GetStaticPathsRequired" in open((SITE/"dist").with_name("build.log"), "a+", encoding="utf-8", errors="ignore").read():
        print("Detected missing getStaticPaths — patching and rebuilding…")
        patch_routes_and_schemas()
        sh("npm run build", cwd=SITE, check=True)

def static_root():
    a = SITE / ".vercel" / "output" / "static"
    b = SITE / "dist"
    if a.exists(): return a
    if b.exists(): return b
    raise RuntimeError("No static root found (.vercel/output/static or dist)")

def smoke_static(root: Path):
    for sec in ["blog","gear","guides","upgrades"]:
        secdir = root / sec
        if not secdir.exists(): raise RuntimeError(f"Missing section folder: {secdir}")
        slug = next((p for p in secdir.rglob("index.html")), None)
        if not slug: raise RuntimeError(f"No built pages under {secdir}")
        print(f"OK: {slug.relative_to(root)}")

def vercel_prebuilt_deploy():
    env = os.environ.copy()
    # load from .env files (already in your file)
    for p in [SITE / ".env", ROOT / ".env", (ROOT / "goldloop" / ".env")]:
        try: env.update(load_env_kv(p))
        except: pass

    token = env.get("VERCEL_TOKEN") or env.get("VERCEL_API_TOKEN")
    if not token:
        print("WARNING: VERCEL_TOKEN not found — skipping deploy.")
        return False
    env["VERCEL_TOKEN"] = token

    yes = "--yes"

    # ✅ Ensure PRODUCTION settings are pulled (not preview)
    sh(f"{VERCEL} pull {yes} --environment=production", cwd=SITE, env=env, check=True, timeout=180)

    # ✅ Build for PRODUCTION
    sh(f"{VERCEL} build {yes} --prod", cwd=SITE, env=env, check=True, timeout=1800)

    # ✅ Deploy the PRODUCTION prebuild
    try:
        sh(f"{VERCEL} deploy --prebuilt --prod {yes}", cwd=SITE, env=env, check=True, timeout=1800)
        return True
    except RuntimeError as e:
        # Safety net: if a mismatch somehow slips through, rebuild + retry once
        if "prebuilt output found in \".vercel/output\" was built with target environment \"preview\"" in str(e):
            print("Detected preview/prod mismatch — rebuilding for prod and retrying…")
            sh(f"{VERCEL} build {yes} --prod", cwd=SITE, env=env, check=True, timeout=1800)
            sh(f"{VERCEL} deploy --prebuilt --prod {yes}", cwd=SITE, env=env, check=True, timeout=1800)
            return True
        raise

def check_prod():
    base = "https://touringmag.com"
    ok = True
    for path in ["/", "/blog", "/gear"]:
        try:
            r = requests.get(base+path, timeout=15)
            print(path, r.status_code)
            if r.status_code != 200: ok = False
            if path == "/" and "pagead2.googlesyndication.com" not in r.text:
                print("WARN: AdSense loader not found on /"); ok = False
        except Exception as e:
            print("ERR:", e); ok = False
    if not ok: raise RuntimeError("Production checks failed")
    print("Production checks passed")

def main():
    ensure_dirs()
    patch_astro_config()
    patch_routes_and_schemas()
    ensure_adsense_in_head()

    generated = False
    for i in range(6):
        print(f"\n=== AGENT LOOP {i+1} ===")
        try:
            if not generated:
                run_goldloop()
                copy_content()
                generated = True

            npm_install_and_build()
            root = static_root()
            smoke_static(root)
            vercel_prebuilt_deploy()
            check_prod()
            print("All gates passed ✅")
            return
        except Exception as e:
            print("Attempt failed:", e)
            # try to self-repair & retry
            patch_astro_config()
            patch_routes_and_schemas()
            ensure_adsense_in_head()

    raise SystemExit("Loop cap reached without satisfying all gates")


# ---------- entrypoint (must be top-level, not indented) ----------
if __name__ == "__main__":
    print(">>> Agent starting", flush=True)
    try:
        main()
    except Exception as e:
        print("Agent failed:", e, flush=True)
        sys.exit(1)
