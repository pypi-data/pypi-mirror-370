var Ht = Object.defineProperty;
var He = (r) => {
  throw TypeError(r);
};
var Ut = (r, e, t) => e in r ? Ht(r, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : r[e] = t;
var B = (r, e, t) => Ut(r, typeof e != "symbol" ? e + "" : e, t), Ee = (r, e, t) => e.has(r) || He("Cannot " + t);
var ne = (r, e, t) => (Ee(r, e, "read from private field"), t ? t.call(r) : e.get(r)), Ae = (r, e, t) => e.has(r) ? He("Cannot add the same private member more than once") : e instanceof WeakSet ? e.add(r) : e.set(r, t), Ue = (r, e, t, n) => (Ee(r, e, "write to private field"), n ? n.call(r, t) : e.set(r, t), t), he = (r, e, t) => (Ee(r, e, "access private method"), t);
new Intl.Collator(0, { numeric: 1 }).compare;
async function Gt(r, e) {
  return r.map(
    (t) => new st({
      path: t.name,
      orig_name: t.name,
      blob: t,
      size: t.size,
      mime_type: t.type,
      is_stream: e
    })
  );
}
class st {
  constructor({
    path: e,
    url: t,
    orig_name: n,
    size: i,
    blob: a,
    is_stream: o,
    mime_type: l,
    alt_text: s,
    b64: c
  }) {
    this.meta = { _type: "gradio.FileData" }, this.path = e, this.url = t, this.orig_name = n, this.size = i, this.blob = t ? void 0 : a, this.is_stream = o, this.mime_type = l, this.alt_text = s, this.b64 = c;
  }
}
typeof process < "u" && process.versions && process.versions.node;
var V;
class Ji extends TransformStream {
  /** Constructs a new instance. */
  constructor(t = { allowCR: !1 }) {
    super({
      transform: (n, i) => {
        for (n = ne(this, V) + n; ; ) {
          const a = n.indexOf(`
`), o = t.allowCR ? n.indexOf("\r") : -1;
          if (o !== -1 && o !== n.length - 1 && (a === -1 || a - 1 > o)) {
            i.enqueue(n.slice(0, o)), n = n.slice(o + 1);
            continue;
          }
          if (a === -1)
            break;
          const l = n[a - 1] === "\r" ? a - 1 : a;
          i.enqueue(n.slice(0, l)), n = n.slice(a + 1);
        }
        Ue(this, V, n);
      },
      flush: (n) => {
        if (ne(this, V) === "")
          return;
        const i = t.allowCR && ne(this, V).endsWith("\r") ? ne(this, V).slice(0, -1) : ne(this, V);
        n.enqueue(i);
      }
    });
    Ae(this, V, "");
  }
}
V = new WeakMap();
const { setContext: ea, getContext: Zt } = window.__gradio__svelte__internal, Xt = "WORKER_PROXY_CONTEXT_KEY";
function Wt() {
  return Zt(Xt);
}
const Yt = "lite.local";
function Kt(r) {
  return r.host === window.location.host || r.host === "localhost:7860" || r.host === "127.0.0.1:7860" || // Ref: https://github.com/gradio-app/gradio/blob/v3.32.0/js/app/src/Index.svelte#L194
  r.host === Yt;
}
function Qt(r, e) {
  const t = e.toLowerCase();
  for (const [n, i] of Object.entries(r))
    if (n.toLowerCase() === t)
      return i;
}
function Vt(r) {
  const e = typeof window < "u";
  if (r == null || !e)
    return !1;
  const t = new URL(r, window.location.href);
  return !(!Kt(t) || t.protocol !== "http:" && t.protocol !== "https:");
}
let me;
async function Jt(r) {
  const e = typeof window < "u";
  if (r == null || !e || !Vt(r))
    return r;
  if (me == null)
    try {
      me = Wt();
    } catch {
      return r;
    }
  if (me == null)
    return r;
  const n = new URL(r, window.location.href).pathname;
  return me.httpRequest({
    method: "GET",
    path: n,
    headers: {},
    query_string: ""
  }).then((i) => {
    if (i.status !== 200)
      throw new Error(`Failed to get file ${n} from the Wasm worker.`);
    const a = new Blob([i.body], {
      type: Qt(i.headers, "content-type")
    });
    return URL.createObjectURL(a);
  });
}
const {
  SvelteComponent: ta,
  assign: na,
  check_outros: ia,
  children: aa,
  claim_element: oa,
  compute_rest_props: ra,
  create_slot: la,
  detach: sa,
  element: ua,
  empty: ca,
  exclude_internal_props: _a,
  get_all_dirty_from_scope: da,
  get_slot_changes: pa,
  get_spread_update: ha,
  group_outros: ma,
  init: fa,
  insert_hydration: ga,
  listen: $a,
  prevent_default: Da,
  safe_not_equal: va,
  set_attributes: ya,
  set_style: Fa,
  toggle_class: ba,
  transition_in: wa,
  transition_out: ka,
  update_slot_base: Ca
} = window.__gradio__svelte__internal, { createEventDispatcher: Ea, onMount: Aa } = window.__gradio__svelte__internal, {
  SvelteComponent: en,
  assign: Se,
  bubble: tn,
  claim_element: nn,
  compute_rest_props: Ge,
  detach: an,
  element: on,
  exclude_internal_props: rn,
  get_spread_update: ln,
  init: sn,
  insert_hydration: un,
  listen: cn,
  noop: Ze,
  safe_not_equal: _n,
  set_attributes: Xe,
  src_url_equal: dn,
  toggle_class: We
} = window.__gradio__svelte__internal;
function pn(r) {
  let e, t, n, i, a = [
    {
      src: t = /*resolved_src*/
      r[0]
    },
    /*$$restProps*/
    r[1]
  ], o = {};
  for (let l = 0; l < a.length; l += 1)
    o = Se(o, a[l]);
  return {
    c() {
      e = on("img"), this.h();
    },
    l(l) {
      e = nn(l, "IMG", { src: !0 }), this.h();
    },
    h() {
      Xe(e, o), We(e, "svelte-kxeri3", !0);
    },
    m(l, s) {
      un(l, e, s), n || (i = cn(
        e,
        "load",
        /*load_handler*/
        r[4]
      ), n = !0);
    },
    p(l, [s]) {
      Xe(e, o = ln(a, [
        s & /*resolved_src*/
        1 && !dn(e.src, t = /*resolved_src*/
        l[0]) && { src: t },
        s & /*$$restProps*/
        2 && /*$$restProps*/
        l[1]
      ])), We(e, "svelte-kxeri3", !0);
    },
    i: Ze,
    o: Ze,
    d(l) {
      l && an(e), n = !1, i();
    }
  };
}
function hn(r, e, t) {
  const n = ["src"];
  let i = Ge(e, n), { src: a = void 0 } = e, o, l;
  function s(c) {
    tn.call(this, r, c);
  }
  return r.$$set = (c) => {
    e = Se(Se({}, e), rn(c)), t(1, i = Ge(e, n)), "src" in c && t(2, a = c.src);
  }, r.$$.update = () => {
    if (r.$$.dirty & /*src, latest_src*/
    12) {
      t(0, o = a), t(3, l = a);
      const c = a;
      Jt(c).then((d) => {
        l === c && t(0, o = d);
      });
    }
  }, [o, i, a, l, s];
}
class ut extends en {
  constructor(e) {
    super(), sn(this, e, hn, pn, _n, { src: 2 });
  }
}
const mn = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], Ye = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
mn.reduce(
  (r, { color: e, primary: t, secondary: n }) => ({
    ...r,
    [e]: {
      primary: Ye[e][t],
      secondary: Ye[e][n]
    }
  }),
  {}
);
const {
  SvelteComponent: Sa,
  append_hydration: xa,
  assign: Ba,
  attr: qa,
  binding_callbacks: Ta,
  children: Ra,
  claim_element: za,
  claim_space: Ia,
  claim_svg_element: Oa,
  create_slot: La,
  detach: Pa,
  element: Na,
  empty: Ma,
  get_all_dirty_from_scope: ja,
  get_slot_changes: Ha,
  get_spread_update: Ua,
  init: Ga,
  insert_hydration: Za,
  listen: Xa,
  noop: Wa,
  safe_not_equal: Ya,
  set_dynamic_element_data: Ka,
  set_style: Qa,
  space: Va,
  svg_element: Ja,
  toggle_class: eo,
  transition_in: to,
  transition_out: no,
  update_slot_base: io
} = window.__gradio__svelte__internal;
function qe() {
  return {
    async: !1,
    breaks: !1,
    extensions: null,
    gfm: !0,
    hooks: null,
    pedantic: !1,
    renderer: null,
    silent: !1,
    tokenizer: null,
    walkTokens: null
  };
}
let te = qe();
function ct(r) {
  te = r;
}
const _t = /[&<>"']/, fn = new RegExp(_t.source, "g"), dt = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, gn = new RegExp(dt.source, "g"), $n = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, Ke = (r) => $n[r];
function X(r, e) {
  if (e) {
    if (_t.test(r))
      return r.replace(fn, Ke);
  } else if (dt.test(r))
    return r.replace(gn, Ke);
  return r;
}
const Dn = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function vn(r) {
  return r.replace(Dn, (e, t) => (t = t.toLowerCase(), t === "colon" ? ":" : t.charAt(0) === "#" ? t.charAt(1) === "x" ? String.fromCharCode(parseInt(t.substring(2), 16)) : String.fromCharCode(+t.substring(1)) : ""));
}
const yn = /(^|[^\[])\^/g;
function S(r, e) {
  let t = typeof r == "string" ? r : r.source;
  e = e || "";
  const n = {
    replace: (i, a) => {
      let o = typeof a == "string" ? a : a.source;
      return o = o.replace(yn, "$1"), t = t.replace(i, o), n;
    },
    getRegex: () => new RegExp(t, e)
  };
  return n;
}
function Qe(r) {
  try {
    r = encodeURI(r).replace(/%25/g, "%");
  } catch {
    return null;
  }
  return r;
}
const re = { exec: () => null };
function Ve(r, e) {
  const t = r.replace(/\|/g, (a, o, l) => {
    let s = !1, c = o;
    for (; --c >= 0 && l[c] === "\\"; )
      s = !s;
    return s ? "|" : " |";
  }), n = t.split(/ \|/);
  let i = 0;
  if (n[0].trim() || n.shift(), n.length > 0 && !n[n.length - 1].trim() && n.pop(), e)
    if (n.length > e)
      n.splice(e);
    else
      for (; n.length < e; )
        n.push("");
  for (; i < n.length; i++)
    n[i] = n[i].trim().replace(/\\\|/g, "|");
  return n;
}
function fe(r, e, t) {
  const n = r.length;
  if (n === 0)
    return "";
  let i = 0;
  for (; i < n && r.charAt(n - i - 1) === e; )
    i++;
  return r.slice(0, n - i);
}
function Fn(r, e) {
  if (r.indexOf(e[1]) === -1)
    return -1;
  let t = 0;
  for (let n = 0; n < r.length; n++)
    if (r[n] === "\\")
      n++;
    else if (r[n] === e[0])
      t++;
    else if (r[n] === e[1] && (t--, t < 0))
      return n;
  return -1;
}
function Je(r, e, t, n) {
  const i = e.href, a = e.title ? X(e.title) : null, o = r[1].replace(/\\([\[\]])/g, "$1");
  if (r[0].charAt(0) !== "!") {
    n.state.inLink = !0;
    const l = {
      type: "link",
      raw: t,
      href: i,
      title: a,
      text: o,
      tokens: n.inlineTokens(o)
    };
    return n.state.inLink = !1, l;
  }
  return {
    type: "image",
    raw: t,
    href: i,
    title: a,
    text: X(o)
  };
}
function bn(r, e) {
  const t = r.match(/^(\s+)(?:```)/);
  if (t === null)
    return e;
  const n = t[1];
  return e.split(`
`).map((i) => {
    const a = i.match(/^\s+/);
    if (a === null)
      return i;
    const [o] = a;
    return o.length >= n.length ? i.slice(n.length) : i;
  }).join(`
`);
}
class $e {
  // set by the lexer
  constructor(e) {
    B(this, "options");
    B(this, "rules");
    // set by the lexer
    B(this, "lexer");
    this.options = e || te;
  }
  space(e) {
    const t = this.rules.block.newline.exec(e);
    if (t && t[0].length > 0)
      return {
        type: "space",
        raw: t[0]
      };
  }
  code(e) {
    const t = this.rules.block.code.exec(e);
    if (t) {
      const n = t[0].replace(/^ {1,4}/gm, "");
      return {
        type: "code",
        raw: t[0],
        codeBlockStyle: "indented",
        text: this.options.pedantic ? n : fe(n, `
`)
      };
    }
  }
  fences(e) {
    const t = this.rules.block.fences.exec(e);
    if (t) {
      const n = t[0], i = bn(n, t[3] || "");
      return {
        type: "code",
        raw: n,
        lang: t[2] ? t[2].trim().replace(this.rules.inline.anyPunctuation, "$1") : t[2],
        text: i
      };
    }
  }
  heading(e) {
    const t = this.rules.block.heading.exec(e);
    if (t) {
      let n = t[2].trim();
      if (/#$/.test(n)) {
        const i = fe(n, "#");
        (this.options.pedantic || !i || / $/.test(i)) && (n = i.trim());
      }
      return {
        type: "heading",
        raw: t[0],
        depth: t[1].length,
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  hr(e) {
    const t = this.rules.block.hr.exec(e);
    if (t)
      return {
        type: "hr",
        raw: t[0]
      };
  }
  blockquote(e) {
    const t = this.rules.block.blockquote.exec(e);
    if (t) {
      let n = t[0].replace(/\n {0,3}((?:=+|-+) *)(?=\n|$)/g, `
    $1`);
      n = fe(n.replace(/^ *>[ \t]?/gm, ""), `
`);
      const i = this.lexer.state.top;
      this.lexer.state.top = !0;
      const a = this.lexer.blockTokens(n);
      return this.lexer.state.top = i, {
        type: "blockquote",
        raw: t[0],
        tokens: a,
        text: n
      };
    }
  }
  list(e) {
    let t = this.rules.block.list.exec(e);
    if (t) {
      let n = t[1].trim();
      const i = n.length > 1, a = {
        type: "list",
        raw: "",
        ordered: i,
        start: i ? +n.slice(0, -1) : "",
        loose: !1,
        items: []
      };
      n = i ? `\\d{1,9}\\${n.slice(-1)}` : `\\${n}`, this.options.pedantic && (n = i ? n : "[*+-]");
      const o = new RegExp(`^( {0,3}${n})((?:[	 ][^\\n]*)?(?:\\n|$))`);
      let l = "", s = "", c = !1;
      for (; e; ) {
        let d = !1;
        if (!(t = o.exec(e)) || this.rules.block.hr.test(e))
          break;
        l = t[0], e = e.substring(l.length);
        let p = t[2].split(`
`, 1)[0].replace(/^\t+/, (y) => " ".repeat(3 * y.length)), m = e.split(`
`, 1)[0], b = 0;
        this.options.pedantic ? (b = 2, s = p.trimStart()) : (b = t[2].search(/[^ ]/), b = b > 4 ? 1 : b, s = p.slice(b), b += t[1].length);
        let R = !1;
        if (!p && /^ *$/.test(m) && (l += m + `
`, e = e.substring(m.length + 1), d = !0), !d) {
          const y = new RegExp(`^ {0,${Math.min(3, b - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`), _ = new RegExp(`^ {0,${Math.min(3, b - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`), u = new RegExp(`^ {0,${Math.min(3, b - 1)}}(?:\`\`\`|~~~)`), h = new RegExp(`^ {0,${Math.min(3, b - 1)}}#`);
          for (; e; ) {
            const f = e.split(`
`, 1)[0];
            if (m = f, this.options.pedantic && (m = m.replace(/^ {1,4}(?=( {4})*[^ ])/g, "  ")), u.test(m) || h.test(m) || y.test(m) || _.test(e))
              break;
            if (m.search(/[^ ]/) >= b || !m.trim())
              s += `
` + m.slice(b);
            else {
              if (R || p.search(/[^ ]/) >= 4 || u.test(p) || h.test(p) || _.test(p))
                break;
              s += `
` + m;
            }
            !R && !m.trim() && (R = !0), l += f + `
`, e = e.substring(f.length + 1), p = m.slice(b);
          }
        }
        a.loose || (c ? a.loose = !0 : /\n *\n *$/.test(l) && (c = !0));
        let C = null, w;
        this.options.gfm && (C = /^\[[ xX]\] /.exec(s), C && (w = C[0] !== "[ ] ", s = s.replace(/^\[[ xX]\] +/, ""))), a.items.push({
          type: "list_item",
          raw: l,
          task: !!C,
          checked: w,
          loose: !1,
          text: s,
          tokens: []
        }), a.raw += l;
      }
      a.items[a.items.length - 1].raw = l.trimEnd(), a.items[a.items.length - 1].text = s.trimEnd(), a.raw = a.raw.trimEnd();
      for (let d = 0; d < a.items.length; d++)
        if (this.lexer.state.top = !1, a.items[d].tokens = this.lexer.blockTokens(a.items[d].text, []), !a.loose) {
          const p = a.items[d].tokens.filter((b) => b.type === "space"), m = p.length > 0 && p.some((b) => /\n.*\n/.test(b.raw));
          a.loose = m;
        }
      if (a.loose)
        for (let d = 0; d < a.items.length; d++)
          a.items[d].loose = !0;
      return a;
    }
  }
  html(e) {
    const t = this.rules.block.html.exec(e);
    if (t)
      return {
        type: "html",
        block: !0,
        raw: t[0],
        pre: t[1] === "pre" || t[1] === "script" || t[1] === "style",
        text: t[0]
      };
  }
  def(e) {
    const t = this.rules.block.def.exec(e);
    if (t) {
      const n = t[1].toLowerCase().replace(/\s+/g, " "), i = t[2] ? t[2].replace(/^<(.*)>$/, "$1").replace(this.rules.inline.anyPunctuation, "$1") : "", a = t[3] ? t[3].substring(1, t[3].length - 1).replace(this.rules.inline.anyPunctuation, "$1") : t[3];
      return {
        type: "def",
        tag: n,
        raw: t[0],
        href: i,
        title: a
      };
    }
  }
  table(e) {
    const t = this.rules.block.table.exec(e);
    if (!t || !/[:|]/.test(t[2]))
      return;
    const n = Ve(t[1]), i = t[2].replace(/^\||\| *$/g, "").split("|"), a = t[3] && t[3].trim() ? t[3].replace(/\n[ \t]*$/, "").split(`
`) : [], o = {
      type: "table",
      raw: t[0],
      header: [],
      align: [],
      rows: []
    };
    if (n.length === i.length) {
      for (const l of i)
        /^ *-+: *$/.test(l) ? o.align.push("right") : /^ *:-+: *$/.test(l) ? o.align.push("center") : /^ *:-+ *$/.test(l) ? o.align.push("left") : o.align.push(null);
      for (const l of n)
        o.header.push({
          text: l,
          tokens: this.lexer.inline(l)
        });
      for (const l of a)
        o.rows.push(Ve(l, o.header.length).map((s) => ({
          text: s,
          tokens: this.lexer.inline(s)
        })));
      return o;
    }
  }
  lheading(e) {
    const t = this.rules.block.lheading.exec(e);
    if (t)
      return {
        type: "heading",
        raw: t[0],
        depth: t[2].charAt(0) === "=" ? 1 : 2,
        text: t[1],
        tokens: this.lexer.inline(t[1])
      };
  }
  paragraph(e) {
    const t = this.rules.block.paragraph.exec(e);
    if (t) {
      const n = t[1].charAt(t[1].length - 1) === `
` ? t[1].slice(0, -1) : t[1];
      return {
        type: "paragraph",
        raw: t[0],
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  text(e) {
    const t = this.rules.block.text.exec(e);
    if (t)
      return {
        type: "text",
        raw: t[0],
        text: t[0],
        tokens: this.lexer.inline(t[0])
      };
  }
  escape(e) {
    const t = this.rules.inline.escape.exec(e);
    if (t)
      return {
        type: "escape",
        raw: t[0],
        text: X(t[1])
      };
  }
  tag(e) {
    const t = this.rules.inline.tag.exec(e);
    if (t)
      return !this.lexer.state.inLink && /^<a /i.test(t[0]) ? this.lexer.state.inLink = !0 : this.lexer.state.inLink && /^<\/a>/i.test(t[0]) && (this.lexer.state.inLink = !1), !this.lexer.state.inRawBlock && /^<(pre|code|kbd|script)(\s|>)/i.test(t[0]) ? this.lexer.state.inRawBlock = !0 : this.lexer.state.inRawBlock && /^<\/(pre|code|kbd|script)(\s|>)/i.test(t[0]) && (this.lexer.state.inRawBlock = !1), {
        type: "html",
        raw: t[0],
        inLink: this.lexer.state.inLink,
        inRawBlock: this.lexer.state.inRawBlock,
        block: !1,
        text: t[0]
      };
  }
  link(e) {
    const t = this.rules.inline.link.exec(e);
    if (t) {
      const n = t[2].trim();
      if (!this.options.pedantic && /^</.test(n)) {
        if (!/>$/.test(n))
          return;
        const o = fe(n.slice(0, -1), "\\");
        if ((n.length - o.length) % 2 === 0)
          return;
      } else {
        const o = Fn(t[2], "()");
        if (o > -1) {
          const s = (t[0].indexOf("!") === 0 ? 5 : 4) + t[1].length + o;
          t[2] = t[2].substring(0, o), t[0] = t[0].substring(0, s).trim(), t[3] = "";
        }
      }
      let i = t[2], a = "";
      if (this.options.pedantic) {
        const o = /^([^'"]*[^\s])\s+(['"])(.*)\2/.exec(i);
        o && (i = o[1], a = o[3]);
      } else
        a = t[3] ? t[3].slice(1, -1) : "";
      return i = i.trim(), /^</.test(i) && (this.options.pedantic && !/>$/.test(n) ? i = i.slice(1) : i = i.slice(1, -1)), Je(t, {
        href: i && i.replace(this.rules.inline.anyPunctuation, "$1"),
        title: a && a.replace(this.rules.inline.anyPunctuation, "$1")
      }, t[0], this.lexer);
    }
  }
  reflink(e, t) {
    let n;
    if ((n = this.rules.inline.reflink.exec(e)) || (n = this.rules.inline.nolink.exec(e))) {
      const i = (n[2] || n[1]).replace(/\s+/g, " "), a = t[i.toLowerCase()];
      if (!a) {
        const o = n[0].charAt(0);
        return {
          type: "text",
          raw: o,
          text: o
        };
      }
      return Je(n, a, n[0], this.lexer);
    }
  }
  emStrong(e, t, n = "") {
    let i = this.rules.inline.emStrongLDelim.exec(e);
    if (!i || i[3] && n.match(/[\p{L}\p{N}]/u))
      return;
    if (!(i[1] || i[2] || "") || !n || this.rules.inline.punctuation.exec(n)) {
      const o = [...i[0]].length - 1;
      let l, s, c = o, d = 0;
      const p = i[0][0] === "*" ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
      for (p.lastIndex = 0, t = t.slice(-1 * e.length + o); (i = p.exec(t)) != null; ) {
        if (l = i[1] || i[2] || i[3] || i[4] || i[5] || i[6], !l)
          continue;
        if (s = [...l].length, i[3] || i[4]) {
          c += s;
          continue;
        } else if ((i[5] || i[6]) && o % 3 && !((o + s) % 3)) {
          d += s;
          continue;
        }
        if (c -= s, c > 0)
          continue;
        s = Math.min(s, s + c + d);
        const m = [...i[0]][0].length, b = e.slice(0, o + i.index + m + s);
        if (Math.min(o, s) % 2) {
          const C = b.slice(1, -1);
          return {
            type: "em",
            raw: b,
            text: C,
            tokens: this.lexer.inlineTokens(C)
          };
        }
        const R = b.slice(2, -2);
        return {
          type: "strong",
          raw: b,
          text: R,
          tokens: this.lexer.inlineTokens(R)
        };
      }
    }
  }
  codespan(e) {
    const t = this.rules.inline.code.exec(e);
    if (t) {
      let n = t[2].replace(/\n/g, " ");
      const i = /[^ ]/.test(n), a = /^ /.test(n) && / $/.test(n);
      return i && a && (n = n.substring(1, n.length - 1)), n = X(n, !0), {
        type: "codespan",
        raw: t[0],
        text: n
      };
    }
  }
  br(e) {
    const t = this.rules.inline.br.exec(e);
    if (t)
      return {
        type: "br",
        raw: t[0]
      };
  }
  del(e) {
    const t = this.rules.inline.del.exec(e);
    if (t)
      return {
        type: "del",
        raw: t[0],
        text: t[2],
        tokens: this.lexer.inlineTokens(t[2])
      };
  }
  autolink(e) {
    const t = this.rules.inline.autolink.exec(e);
    if (t) {
      let n, i;
      return t[2] === "@" ? (n = X(t[1]), i = "mailto:" + n) : (n = X(t[1]), i = n), {
        type: "link",
        raw: t[0],
        text: n,
        href: i,
        tokens: [
          {
            type: "text",
            raw: n,
            text: n
          }
        ]
      };
    }
  }
  url(e) {
    var n;
    let t;
    if (t = this.rules.inline.url.exec(e)) {
      let i, a;
      if (t[2] === "@")
        i = X(t[0]), a = "mailto:" + i;
      else {
        let o;
        do
          o = t[0], t[0] = ((n = this.rules.inline._backpedal.exec(t[0])) == null ? void 0 : n[0]) ?? "";
        while (o !== t[0]);
        i = X(t[0]), t[1] === "www." ? a = "http://" + t[0] : a = t[0];
      }
      return {
        type: "link",
        raw: t[0],
        text: i,
        href: a,
        tokens: [
          {
            type: "text",
            raw: i,
            text: i
          }
        ]
      };
    }
  }
  inlineText(e) {
    const t = this.rules.inline.text.exec(e);
    if (t) {
      let n;
      return this.lexer.state.inRawBlock ? n = t[0] : n = X(t[0]), {
        type: "text",
        raw: t[0],
        text: n
      };
    }
  }
}
const wn = /^(?: *(?:\n|$))+/, kn = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/, Cn = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/, ue = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/, En = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/, pt = /(?:[*+-]|\d{1,9}[.)])/, ht = S(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/).replace(/bull/g, pt).replace(/blockCode/g, / {4}/).replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g, / {0,3}>/).replace(/heading/g, / {0,3}#{1,6}/).replace(/html/g, / {0,3}<[^\n>]+>\n/).getRegex(), Te = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/, An = /^[^\n]+/, Re = /(?!\s*\])(?:\\.|[^\[\]\\])+/, Sn = S(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/).replace("label", Re).replace("title", /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(), xn = S(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g, pt).getRegex(), be = "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul", ze = /<!--(?:-?>|[\s\S]*?(?:-->|$))/, Bn = S("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$))", "i").replace("comment", ze).replace("tag", be).replace("attribute", / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(), mt = S(Te).replace("hr", ue).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("|table", "").replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", be).getRegex(), qn = S(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph", mt).getRegex(), Ie = {
  blockquote: qn,
  code: kn,
  def: Sn,
  fences: Cn,
  heading: En,
  hr: ue,
  html: Bn,
  lheading: ht,
  list: xn,
  newline: wn,
  paragraph: mt,
  table: re,
  text: An
}, et = S("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr", ue).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("blockquote", " {0,3}>").replace("code", " {4}[^\\n]").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", be).getRegex(), Tn = {
  ...Ie,
  table: et,
  paragraph: S(Te).replace("hr", ue).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("table", et).replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", be).getRegex()
}, Rn = {
  ...Ie,
  html: S(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment", ze).replace(/tag/g, "(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
  heading: /^(#{1,6})(.*)(?:\n+|$)/,
  fences: re,
  // fences not supported
  lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
  paragraph: S(Te).replace("hr", ue).replace("heading", ` *#{1,6} *[^
]`).replace("lheading", ht).replace("|table", "").replace("blockquote", " {0,3}>").replace("|fences", "").replace("|list", "").replace("|html", "").replace("|tag", "").getRegex()
}, ft = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/, zn = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/, gt = /^( {2,}|\\)\n(?!\s*$)/, In = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/, ce = "\\p{P}\\p{S}", On = S(/^((?![*_])[\spunctuation])/, "u").replace(/punctuation/g, ce).getRegex(), Ln = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g, Pn = S(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, "u").replace(/punct/g, ce).getRegex(), Nn = S("^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)[punct](\\*+)(?=[\\s]|$)|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])|[\\s](\\*+)(?!\\*)(?=[punct])|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])|[^punct\\s](\\*+)(?=[^punct\\s])", "gu").replace(/punct/g, ce).getRegex(), Mn = S("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)[punct](_+)(?=[\\s]|$)|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)|(?!_)[punct\\s](_+)(?=[^punct\\s])|[\\s](_+)(?!_)(?=[punct])|(?!_)[punct](_+)(?!_)(?=[punct])", "gu").replace(/punct/g, ce).getRegex(), jn = S(/\\([punct])/, "gu").replace(/punct/g, ce).getRegex(), Hn = S(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme", /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email", /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(), Un = S(ze).replace("(?:-->|$)", "-->").getRegex(), Gn = S("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment", Un).replace("attribute", /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(), De = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/, Zn = S(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/).replace("label", De).replace("href", /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/).replace("title", /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(), $t = S(/^!?\[(label)\]\[(ref)\]/).replace("label", De).replace("ref", Re).getRegex(), Dt = S(/^!?\[(ref)\](?:\[\])?/).replace("ref", Re).getRegex(), Xn = S("reflink|nolink(?!\\()", "g").replace("reflink", $t).replace("nolink", Dt).getRegex(), Oe = {
  _backpedal: re,
  // only used for GFM url
  anyPunctuation: jn,
  autolink: Hn,
  blockSkip: Ln,
  br: gt,
  code: zn,
  del: re,
  emStrongLDelim: Pn,
  emStrongRDelimAst: Nn,
  emStrongRDelimUnd: Mn,
  escape: ft,
  link: Zn,
  nolink: Dt,
  punctuation: On,
  reflink: $t,
  reflinkSearch: Xn,
  tag: Gn,
  text: In,
  url: re
}, Wn = {
  ...Oe,
  link: S(/^!?\[(label)\]\((.*?)\)/).replace("label", De).getRegex(),
  reflink: S(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label", De).getRegex()
}, xe = {
  ...Oe,
  escape: S(ft).replace("])", "~|])").getRegex(),
  url: S(/^((?:ftp|https?):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/, "i").replace("email", /[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),
  _backpedal: /(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,
  del: /^(~~?)(?=[^\s~])([\s\S]*?[^\s~])\1(?=[^~]|$)/,
  text: /^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|https?:\/\/|ftp:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/
}, Yn = {
  ...xe,
  br: S(gt).replace("{2,}", "*").getRegex(),
  text: S(xe.text).replace("\\b_", "\\b_| {2,}\\n").replace(/\{2,\}/g, "*").getRegex()
}, ge = {
  normal: Ie,
  gfm: Tn,
  pedantic: Rn
}, oe = {
  normal: Oe,
  gfm: xe,
  breaks: Yn,
  pedantic: Wn
};
class Y {
  constructor(e) {
    B(this, "tokens");
    B(this, "options");
    B(this, "state");
    B(this, "tokenizer");
    B(this, "inlineQueue");
    this.tokens = [], this.tokens.links = /* @__PURE__ */ Object.create(null), this.options = e || te, this.options.tokenizer = this.options.tokenizer || new $e(), this.tokenizer = this.options.tokenizer, this.tokenizer.options = this.options, this.tokenizer.lexer = this, this.inlineQueue = [], this.state = {
      inLink: !1,
      inRawBlock: !1,
      top: !0
    };
    const t = {
      block: ge.normal,
      inline: oe.normal
    };
    this.options.pedantic ? (t.block = ge.pedantic, t.inline = oe.pedantic) : this.options.gfm && (t.block = ge.gfm, this.options.breaks ? t.inline = oe.breaks : t.inline = oe.gfm), this.tokenizer.rules = t;
  }
  /**
   * Expose Rules
   */
  static get rules() {
    return {
      block: ge,
      inline: oe
    };
  }
  /**
   * Static Lex Method
   */
  static lex(e, t) {
    return new Y(t).lex(e);
  }
  /**
   * Static Lex Inline Method
   */
  static lexInline(e, t) {
    return new Y(t).inlineTokens(e);
  }
  /**
   * Preprocessing
   */
  lex(e) {
    e = e.replace(/\r\n|\r/g, `
`), this.blockTokens(e, this.tokens);
    for (let t = 0; t < this.inlineQueue.length; t++) {
      const n = this.inlineQueue[t];
      this.inlineTokens(n.src, n.tokens);
    }
    return this.inlineQueue = [], this.tokens;
  }
  blockTokens(e, t = []) {
    this.options.pedantic ? e = e.replace(/\t/g, "    ").replace(/^ +$/gm, "") : e = e.replace(/^( *)(\t+)/gm, (l, s, c) => s + "    ".repeat(c.length));
    let n, i, a, o;
    for (; e; )
      if (!(this.options.extensions && this.options.extensions.block && this.options.extensions.block.some((l) => (n = l.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
        if (n = this.tokenizer.space(e)) {
          e = e.substring(n.raw.length), n.raw.length === 1 && t.length > 0 ? t[t.length - 1].raw += `
` : t.push(n);
          continue;
        }
        if (n = this.tokenizer.code(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && (i.type === "paragraph" || i.type === "text") ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.fences(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.heading(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.hr(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.blockquote(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.list(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.html(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.def(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && (i.type === "paragraph" || i.type === "text") ? (i.raw += `
` + n.raw, i.text += `
` + n.raw, this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : this.tokens.links[n.tag] || (this.tokens.links[n.tag] = {
            href: n.href,
            title: n.title
          });
          continue;
        }
        if (n = this.tokenizer.table(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.lheading(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (a = e, this.options.extensions && this.options.extensions.startBlock) {
          let l = 1 / 0;
          const s = e.slice(1);
          let c;
          this.options.extensions.startBlock.forEach((d) => {
            c = d.call({ lexer: this }, s), typeof c == "number" && c >= 0 && (l = Math.min(l, c));
          }), l < 1 / 0 && l >= 0 && (a = e.substring(0, l + 1));
        }
        if (this.state.top && (n = this.tokenizer.paragraph(a))) {
          i = t[t.length - 1], o && i.type === "paragraph" ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n), o = a.length !== e.length, e = e.substring(n.raw.length);
          continue;
        }
        if (n = this.tokenizer.text(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && i.type === "text" ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n);
          continue;
        }
        if (e) {
          const l = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(l);
            break;
          } else
            throw new Error(l);
        }
      }
    return this.state.top = !0, t;
  }
  inline(e, t = []) {
    return this.inlineQueue.push({ src: e, tokens: t }), t;
  }
  /**
   * Lexing/Compiling
   */
  inlineTokens(e, t = []) {
    let n, i, a, o = e, l, s, c;
    if (this.tokens.links) {
      const d = Object.keys(this.tokens.links);
      if (d.length > 0)
        for (; (l = this.tokenizer.rules.inline.reflinkSearch.exec(o)) != null; )
          d.includes(l[0].slice(l[0].lastIndexOf("[") + 1, -1)) && (o = o.slice(0, l.index) + "[" + "a".repeat(l[0].length - 2) + "]" + o.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex));
    }
    for (; (l = this.tokenizer.rules.inline.blockSkip.exec(o)) != null; )
      o = o.slice(0, l.index) + "[" + "a".repeat(l[0].length - 2) + "]" + o.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
    for (; (l = this.tokenizer.rules.inline.anyPunctuation.exec(o)) != null; )
      o = o.slice(0, l.index) + "++" + o.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
    for (; e; )
      if (s || (c = ""), s = !1, !(this.options.extensions && this.options.extensions.inline && this.options.extensions.inline.some((d) => (n = d.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
        if (n = this.tokenizer.escape(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.tag(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && n.type === "text" && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.link(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.reflink(e, this.tokens.links)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && n.type === "text" && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.emStrong(e, o, c)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.codespan(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.br(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.del(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.autolink(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (!this.state.inLink && (n = this.tokenizer.url(e))) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (a = e, this.options.extensions && this.options.extensions.startInline) {
          let d = 1 / 0;
          const p = e.slice(1);
          let m;
          this.options.extensions.startInline.forEach((b) => {
            m = b.call({ lexer: this }, p), typeof m == "number" && m >= 0 && (d = Math.min(d, m));
          }), d < 1 / 0 && d >= 0 && (a = e.substring(0, d + 1));
        }
        if (n = this.tokenizer.inlineText(a)) {
          e = e.substring(n.raw.length), n.raw.slice(-1) !== "_" && (c = n.raw.slice(-1)), s = !0, i = t[t.length - 1], i && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (e) {
          const d = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(d);
            break;
          } else
            throw new Error(d);
        }
      }
    return t;
  }
}
class ve {
  constructor(e) {
    B(this, "options");
    this.options = e || te;
  }
  code(e, t, n) {
    var a;
    const i = (a = (t || "").match(/^\S*/)) == null ? void 0 : a[0];
    return e = e.replace(/\n$/, "") + `
`, i ? '<pre><code class="language-' + X(i) + '">' + (n ? e : X(e, !0)) + `</code></pre>
` : "<pre><code>" + (n ? e : X(e, !0)) + `</code></pre>
`;
  }
  blockquote(e) {
    return `<blockquote>
${e}</blockquote>
`;
  }
  html(e, t) {
    return e;
  }
  heading(e, t, n) {
    return `<h${t}>${e}</h${t}>
`;
  }
  hr() {
    return `<hr>
`;
  }
  list(e, t, n) {
    const i = t ? "ol" : "ul", a = t && n !== 1 ? ' start="' + n + '"' : "";
    return "<" + i + a + `>
` + e + "</" + i + `>
`;
  }
  listitem(e, t, n) {
    return `<li>${e}</li>
`;
  }
  checkbox(e) {
    return "<input " + (e ? 'checked="" ' : "") + 'disabled="" type="checkbox">';
  }
  paragraph(e) {
    return `<p>${e}</p>
`;
  }
  table(e, t) {
    return t && (t = `<tbody>${t}</tbody>`), `<table>
<thead>
` + e + `</thead>
` + t + `</table>
`;
  }
  tablerow(e) {
    return `<tr>
${e}</tr>
`;
  }
  tablecell(e, t) {
    const n = t.header ? "th" : "td";
    return (t.align ? `<${n} align="${t.align}">` : `<${n}>`) + e + `</${n}>
`;
  }
  /**
   * span level renderer
   */
  strong(e) {
    return `<strong>${e}</strong>`;
  }
  em(e) {
    return `<em>${e}</em>`;
  }
  codespan(e) {
    return `<code>${e}</code>`;
  }
  br() {
    return "<br>";
  }
  del(e) {
    return `<del>${e}</del>`;
  }
  link(e, t, n) {
    const i = Qe(e);
    if (i === null)
      return n;
    e = i;
    let a = '<a href="' + e + '"';
    return t && (a += ' title="' + t + '"'), a += ">" + n + "</a>", a;
  }
  image(e, t, n) {
    const i = Qe(e);
    if (i === null)
      return n;
    e = i;
    let a = `<img src="${e}" alt="${n}"`;
    return t && (a += ` title="${t}"`), a += ">", a;
  }
  text(e) {
    return e;
  }
}
class Le {
  // no need for block level renderers
  strong(e) {
    return e;
  }
  em(e) {
    return e;
  }
  codespan(e) {
    return e;
  }
  del(e) {
    return e;
  }
  html(e) {
    return e;
  }
  text(e) {
    return e;
  }
  link(e, t, n) {
    return "" + n;
  }
  image(e, t, n) {
    return "" + n;
  }
  br() {
    return "";
  }
}
class K {
  constructor(e) {
    B(this, "options");
    B(this, "renderer");
    B(this, "textRenderer");
    this.options = e || te, this.options.renderer = this.options.renderer || new ve(), this.renderer = this.options.renderer, this.renderer.options = this.options, this.textRenderer = new Le();
  }
  /**
   * Static Parse Method
   */
  static parse(e, t) {
    return new K(t).parse(e);
  }
  /**
   * Static Parse Inline Method
   */
  static parseInline(e, t) {
    return new K(t).parseInline(e);
  }
  /**
   * Parse Loop
   */
  parse(e, t = !0) {
    let n = "";
    for (let i = 0; i < e.length; i++) {
      const a = e[i];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[a.type]) {
        const o = a, l = this.options.extensions.renderers[o.type].call({ parser: this }, o);
        if (l !== !1 || !["space", "hr", "heading", "code", "table", "blockquote", "list", "html", "paragraph", "text"].includes(o.type)) {
          n += l || "";
          continue;
        }
      }
      switch (a.type) {
        case "space":
          continue;
        case "hr": {
          n += this.renderer.hr();
          continue;
        }
        case "heading": {
          const o = a;
          n += this.renderer.heading(this.parseInline(o.tokens), o.depth, vn(this.parseInline(o.tokens, this.textRenderer)));
          continue;
        }
        case "code": {
          const o = a;
          n += this.renderer.code(o.text, o.lang, !!o.escaped);
          continue;
        }
        case "table": {
          const o = a;
          let l = "", s = "";
          for (let d = 0; d < o.header.length; d++)
            s += this.renderer.tablecell(this.parseInline(o.header[d].tokens), { header: !0, align: o.align[d] });
          l += this.renderer.tablerow(s);
          let c = "";
          for (let d = 0; d < o.rows.length; d++) {
            const p = o.rows[d];
            s = "";
            for (let m = 0; m < p.length; m++)
              s += this.renderer.tablecell(this.parseInline(p[m].tokens), { header: !1, align: o.align[m] });
            c += this.renderer.tablerow(s);
          }
          n += this.renderer.table(l, c);
          continue;
        }
        case "blockquote": {
          const o = a, l = this.parse(o.tokens);
          n += this.renderer.blockquote(l);
          continue;
        }
        case "list": {
          const o = a, l = o.ordered, s = o.start, c = o.loose;
          let d = "";
          for (let p = 0; p < o.items.length; p++) {
            const m = o.items[p], b = m.checked, R = m.task;
            let C = "";
            if (m.task) {
              const w = this.renderer.checkbox(!!b);
              c ? m.tokens.length > 0 && m.tokens[0].type === "paragraph" ? (m.tokens[0].text = w + " " + m.tokens[0].text, m.tokens[0].tokens && m.tokens[0].tokens.length > 0 && m.tokens[0].tokens[0].type === "text" && (m.tokens[0].tokens[0].text = w + " " + m.tokens[0].tokens[0].text)) : m.tokens.unshift({
                type: "text",
                text: w + " "
              }) : C += w + " ";
            }
            C += this.parse(m.tokens, c), d += this.renderer.listitem(C, R, !!b);
          }
          n += this.renderer.list(d, l, s);
          continue;
        }
        case "html": {
          const o = a;
          n += this.renderer.html(o.text, o.block);
          continue;
        }
        case "paragraph": {
          const o = a;
          n += this.renderer.paragraph(this.parseInline(o.tokens));
          continue;
        }
        case "text": {
          let o = a, l = o.tokens ? this.parseInline(o.tokens) : o.text;
          for (; i + 1 < e.length && e[i + 1].type === "text"; )
            o = e[++i], l += `
` + (o.tokens ? this.parseInline(o.tokens) : o.text);
          n += t ? this.renderer.paragraph(l) : l;
          continue;
        }
        default: {
          const o = 'Token with "' + a.type + '" type was not found.';
          if (this.options.silent)
            return console.error(o), "";
          throw new Error(o);
        }
      }
    }
    return n;
  }
  /**
   * Parse Inline Tokens
   */
  parseInline(e, t) {
    t = t || this.renderer;
    let n = "";
    for (let i = 0; i < e.length; i++) {
      const a = e[i];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[a.type]) {
        const o = this.options.extensions.renderers[a.type].call({ parser: this }, a);
        if (o !== !1 || !["escape", "html", "link", "image", "strong", "em", "codespan", "br", "del", "text"].includes(a.type)) {
          n += o || "";
          continue;
        }
      }
      switch (a.type) {
        case "escape": {
          const o = a;
          n += t.text(o.text);
          break;
        }
        case "html": {
          const o = a;
          n += t.html(o.text);
          break;
        }
        case "link": {
          const o = a;
          n += t.link(o.href, o.title, this.parseInline(o.tokens, t));
          break;
        }
        case "image": {
          const o = a;
          n += t.image(o.href, o.title, o.text);
          break;
        }
        case "strong": {
          const o = a;
          n += t.strong(this.parseInline(o.tokens, t));
          break;
        }
        case "em": {
          const o = a;
          n += t.em(this.parseInline(o.tokens, t));
          break;
        }
        case "codespan": {
          const o = a;
          n += t.codespan(o.text);
          break;
        }
        case "br": {
          n += t.br();
          break;
        }
        case "del": {
          const o = a;
          n += t.del(this.parseInline(o.tokens, t));
          break;
        }
        case "text": {
          const o = a;
          n += t.text(o.text);
          break;
        }
        default: {
          const o = 'Token with "' + a.type + '" type was not found.';
          if (this.options.silent)
            return console.error(o), "";
          throw new Error(o);
        }
      }
    }
    return n;
  }
}
class le {
  constructor(e) {
    B(this, "options");
    this.options = e || te;
  }
  /**
   * Process markdown before marked
   */
  preprocess(e) {
    return e;
  }
  /**
   * Process HTML after marked is finished
   */
  postprocess(e) {
    return e;
  }
  /**
   * Process all tokens before walk tokens
   */
  processAllTokens(e) {
    return e;
  }
}
B(le, "passThroughHooks", /* @__PURE__ */ new Set([
  "preprocess",
  "postprocess",
  "processAllTokens"
]));
var ee, Be, vt;
class Kn {
  constructor(...e) {
    Ae(this, ee);
    B(this, "defaults", qe());
    B(this, "options", this.setOptions);
    B(this, "parse", he(this, ee, Be).call(this, Y.lex, K.parse));
    B(this, "parseInline", he(this, ee, Be).call(this, Y.lexInline, K.parseInline));
    B(this, "Parser", K);
    B(this, "Renderer", ve);
    B(this, "TextRenderer", Le);
    B(this, "Lexer", Y);
    B(this, "Tokenizer", $e);
    B(this, "Hooks", le);
    this.use(...e);
  }
  /**
   * Run callback for every token
   */
  walkTokens(e, t) {
    var i, a;
    let n = [];
    for (const o of e)
      switch (n = n.concat(t.call(this, o)), o.type) {
        case "table": {
          const l = o;
          for (const s of l.header)
            n = n.concat(this.walkTokens(s.tokens, t));
          for (const s of l.rows)
            for (const c of s)
              n = n.concat(this.walkTokens(c.tokens, t));
          break;
        }
        case "list": {
          const l = o;
          n = n.concat(this.walkTokens(l.items, t));
          break;
        }
        default: {
          const l = o;
          (a = (i = this.defaults.extensions) == null ? void 0 : i.childTokens) != null && a[l.type] ? this.defaults.extensions.childTokens[l.type].forEach((s) => {
            const c = l[s].flat(1 / 0);
            n = n.concat(this.walkTokens(c, t));
          }) : l.tokens && (n = n.concat(this.walkTokens(l.tokens, t)));
        }
      }
    return n;
  }
  use(...e) {
    const t = this.defaults.extensions || { renderers: {}, childTokens: {} };
    return e.forEach((n) => {
      const i = { ...n };
      if (i.async = this.defaults.async || i.async || !1, n.extensions && (n.extensions.forEach((a) => {
        if (!a.name)
          throw new Error("extension name required");
        if ("renderer" in a) {
          const o = t.renderers[a.name];
          o ? t.renderers[a.name] = function(...l) {
            let s = a.renderer.apply(this, l);
            return s === !1 && (s = o.apply(this, l)), s;
          } : t.renderers[a.name] = a.renderer;
        }
        if ("tokenizer" in a) {
          if (!a.level || a.level !== "block" && a.level !== "inline")
            throw new Error("extension level must be 'block' or 'inline'");
          const o = t[a.level];
          o ? o.unshift(a.tokenizer) : t[a.level] = [a.tokenizer], a.start && (a.level === "block" ? t.startBlock ? t.startBlock.push(a.start) : t.startBlock = [a.start] : a.level === "inline" && (t.startInline ? t.startInline.push(a.start) : t.startInline = [a.start]));
        }
        "childTokens" in a && a.childTokens && (t.childTokens[a.name] = a.childTokens);
      }), i.extensions = t), n.renderer) {
        const a = this.defaults.renderer || new ve(this.defaults);
        for (const o in n.renderer) {
          if (!(o in a))
            throw new Error(`renderer '${o}' does not exist`);
          if (o === "options")
            continue;
          const l = o, s = n.renderer[l], c = a[l];
          a[l] = (...d) => {
            let p = s.apply(a, d);
            return p === !1 && (p = c.apply(a, d)), p || "";
          };
        }
        i.renderer = a;
      }
      if (n.tokenizer) {
        const a = this.defaults.tokenizer || new $e(this.defaults);
        for (const o in n.tokenizer) {
          if (!(o in a))
            throw new Error(`tokenizer '${o}' does not exist`);
          if (["options", "rules", "lexer"].includes(o))
            continue;
          const l = o, s = n.tokenizer[l], c = a[l];
          a[l] = (...d) => {
            let p = s.apply(a, d);
            return p === !1 && (p = c.apply(a, d)), p;
          };
        }
        i.tokenizer = a;
      }
      if (n.hooks) {
        const a = this.defaults.hooks || new le();
        for (const o in n.hooks) {
          if (!(o in a))
            throw new Error(`hook '${o}' does not exist`);
          if (o === "options")
            continue;
          const l = o, s = n.hooks[l], c = a[l];
          le.passThroughHooks.has(o) ? a[l] = (d) => {
            if (this.defaults.async)
              return Promise.resolve(s.call(a, d)).then((m) => c.call(a, m));
            const p = s.call(a, d);
            return c.call(a, p);
          } : a[l] = (...d) => {
            let p = s.apply(a, d);
            return p === !1 && (p = c.apply(a, d)), p;
          };
        }
        i.hooks = a;
      }
      if (n.walkTokens) {
        const a = this.defaults.walkTokens, o = n.walkTokens;
        i.walkTokens = function(l) {
          let s = [];
          return s.push(o.call(this, l)), a && (s = s.concat(a.call(this, l))), s;
        };
      }
      this.defaults = { ...this.defaults, ...i };
    }), this;
  }
  setOptions(e) {
    return this.defaults = { ...this.defaults, ...e }, this;
  }
  lexer(e, t) {
    return Y.lex(e, t ?? this.defaults);
  }
  parser(e, t) {
    return K.parse(e, t ?? this.defaults);
  }
}
ee = new WeakSet(), Be = function(e, t) {
  return (n, i) => {
    const a = { ...i }, o = { ...this.defaults, ...a };
    this.defaults.async === !0 && a.async === !1 && (o.silent || console.warn("marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored."), o.async = !0);
    const l = he(this, ee, vt).call(this, !!o.silent, !!o.async);
    if (typeof n > "u" || n === null)
      return l(new Error("marked(): input parameter is undefined or null"));
    if (typeof n != "string")
      return l(new Error("marked(): input parameter is of type " + Object.prototype.toString.call(n) + ", string expected"));
    if (o.hooks && (o.hooks.options = o), o.async)
      return Promise.resolve(o.hooks ? o.hooks.preprocess(n) : n).then((s) => e(s, o)).then((s) => o.hooks ? o.hooks.processAllTokens(s) : s).then((s) => o.walkTokens ? Promise.all(this.walkTokens(s, o.walkTokens)).then(() => s) : s).then((s) => t(s, o)).then((s) => o.hooks ? o.hooks.postprocess(s) : s).catch(l);
    try {
      o.hooks && (n = o.hooks.preprocess(n));
      let s = e(n, o);
      o.hooks && (s = o.hooks.processAllTokens(s)), o.walkTokens && this.walkTokens(s, o.walkTokens);
      let c = t(s, o);
      return o.hooks && (c = o.hooks.postprocess(c)), c;
    } catch (s) {
      return l(s);
    }
  };
}, vt = function(e, t) {
  return (n) => {
    if (n.message += `
Please report this to https://github.com/markedjs/marked.`, e) {
      const i = "<p>An error occurred:</p><pre>" + X(n.message + "", !0) + "</pre>";
      return t ? Promise.resolve(i) : i;
    }
    if (t)
      return Promise.reject(n);
    throw n;
  };
};
const J = new Kn();
function A(r, e) {
  return J.parse(r, e);
}
A.options = A.setOptions = function(r) {
  return J.setOptions(r), A.defaults = J.defaults, ct(A.defaults), A;
};
A.getDefaults = qe;
A.defaults = te;
A.use = function(...r) {
  return J.use(...r), A.defaults = J.defaults, ct(A.defaults), A;
};
A.walkTokens = function(r, e) {
  return J.walkTokens(r, e);
};
A.parseInline = J.parseInline;
A.Parser = K;
A.parser = K.parse;
A.Renderer = ve;
A.TextRenderer = Le;
A.Lexer = Y;
A.lexer = Y.lex;
A.Tokenizer = $e;
A.Hooks = le;
A.parse = A;
A.options;
A.setOptions;
A.use;
A.walkTokens;
A.parseInline;
K.parse;
Y.lex;
const Qn = /[\0-\x1F!-,\.\/:-@\[-\^`\{-\xA9\xAB-\xB4\xB6-\xB9\xBB-\xBF\xD7\xF7\u02C2-\u02C5\u02D2-\u02DF\u02E5-\u02EB\u02ED\u02EF-\u02FF\u0375\u0378\u0379\u037E\u0380-\u0385\u0387\u038B\u038D\u03A2\u03F6\u0482\u0530\u0557\u0558\u055A-\u055F\u0589-\u0590\u05BE\u05C0\u05C3\u05C6\u05C8-\u05CF\u05EB-\u05EE\u05F3-\u060F\u061B-\u061F\u066A-\u066D\u06D4\u06DD\u06DE\u06E9\u06FD\u06FE\u0700-\u070F\u074B\u074C\u07B2-\u07BF\u07F6-\u07F9\u07FB\u07FC\u07FE\u07FF\u082E-\u083F\u085C-\u085F\u086B-\u089F\u08B5\u08C8-\u08D2\u08E2\u0964\u0965\u0970\u0984\u098D\u098E\u0991\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA\u09BB\u09C5\u09C6\u09C9\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4\u09E5\u09F2-\u09FB\u09FD\u09FF\u0A00\u0A04\u0A0B-\u0A0E\u0A11\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A\u0A3B\u0A3D\u0A43-\u0A46\u0A49\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA\u0ABB\u0AC6\u0ACA\u0ACE\u0ACF\u0AD1-\u0ADF\u0AE4\u0AE5\u0AF0-\u0AF8\u0B00\u0B04\u0B0D\u0B0E\u0B11\u0B12\u0B29\u0B31\u0B34\u0B3A\u0B3B\u0B45\u0B46\u0B49\u0B4A\u0B4E-\u0B54\u0B58-\u0B5B\u0B5E\u0B64\u0B65\u0B70\u0B72-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BF0-\u0BFF\u0C0D\u0C11\u0C29\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5B-\u0C5F\u0C64\u0C65\u0C70-\u0C7F\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4\u0CE5\u0CF0\u0CF3-\u0CFF\u0D0D\u0D11\u0D45\u0D49\u0D4F-\u0D53\u0D58-\u0D5E\u0D64\u0D65\u0D70-\u0D79\u0D80\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DE5\u0DF0\u0DF1\u0DF4-\u0E00\u0E3B-\u0E3F\u0E4F\u0E5A-\u0E80\u0E83\u0E85\u0E8B\u0EA4\u0EA6\u0EBE\u0EBF\u0EC5\u0EC7\u0ECE\u0ECF\u0EDA\u0EDB\u0EE0-\u0EFF\u0F01-\u0F17\u0F1A-\u0F1F\u0F2A-\u0F34\u0F36\u0F38\u0F3A-\u0F3D\u0F48\u0F6D-\u0F70\u0F85\u0F98\u0FBD-\u0FC5\u0FC7-\u0FFF\u104A-\u104F\u109E\u109F\u10C6\u10C8-\u10CC\u10CE\u10CF\u10FB\u1249\u124E\u124F\u1257\u1259\u125E\u125F\u1289\u128E\u128F\u12B1\u12B6\u12B7\u12BF\u12C1\u12C6\u12C7\u12D7\u1311\u1316\u1317\u135B\u135C\u1360-\u137F\u1390-\u139F\u13F6\u13F7\u13FE-\u1400\u166D\u166E\u1680\u169B-\u169F\u16EB-\u16ED\u16F9-\u16FF\u170D\u1715-\u171F\u1735-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17D4-\u17D6\u17D8-\u17DB\u17DE\u17DF\u17EA-\u180A\u180E\u180F\u181A-\u181F\u1879-\u187F\u18AB-\u18AF\u18F6-\u18FF\u191F\u192C-\u192F\u193C-\u1945\u196E\u196F\u1975-\u197F\u19AC-\u19AF\u19CA-\u19CF\u19DA-\u19FF\u1A1C-\u1A1F\u1A5F\u1A7D\u1A7E\u1A8A-\u1A8F\u1A9A-\u1AA6\u1AA8-\u1AAF\u1AC1-\u1AFF\u1B4C-\u1B4F\u1B5A-\u1B6A\u1B74-\u1B7F\u1BF4-\u1BFF\u1C38-\u1C3F\u1C4A-\u1C4C\u1C7E\u1C7F\u1C89-\u1C8F\u1CBB\u1CBC\u1CC0-\u1CCF\u1CD3\u1CFB-\u1CFF\u1DFA\u1F16\u1F17\u1F1E\u1F1F\u1F46\u1F47\u1F4E\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E\u1F7F\u1FB5\u1FBD\u1FBF-\u1FC1\u1FC5\u1FCD-\u1FCF\u1FD4\u1FD5\u1FDC-\u1FDF\u1FED-\u1FF1\u1FF5\u1FFD-\u203E\u2041-\u2053\u2055-\u2070\u2072-\u207E\u2080-\u208F\u209D-\u20CF\u20F1-\u2101\u2103-\u2106\u2108\u2109\u2114\u2116-\u2118\u211E-\u2123\u2125\u2127\u2129\u212E\u213A\u213B\u2140-\u2144\u214A-\u214D\u214F-\u215F\u2189-\u24B5\u24EA-\u2BFF\u2C2F\u2C5F\u2CE5-\u2CEA\u2CF4-\u2CFF\u2D26\u2D28-\u2D2C\u2D2E\u2D2F\u2D68-\u2D6E\u2D70-\u2D7E\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E00-\u2E2E\u2E30-\u3004\u3008-\u3020\u3030\u3036\u3037\u303D-\u3040\u3097\u3098\u309B\u309C\u30A0\u30FB\u3100-\u3104\u3130\u318F-\u319F\u31C0-\u31EF\u3200-\u33FF\u4DC0-\u4DFF\u9FFD-\u9FFF\uA48D-\uA4CF\uA4FE\uA4FF\uA60D-\uA60F\uA62C-\uA63F\uA673\uA67E\uA6F2-\uA716\uA720\uA721\uA789\uA78A\uA7C0\uA7C1\uA7CB-\uA7F4\uA828-\uA82B\uA82D-\uA83F\uA874-\uA87F\uA8C6-\uA8CF\uA8DA-\uA8DF\uA8F8-\uA8FA\uA8FC\uA92E\uA92F\uA954-\uA95F\uA97D-\uA97F\uA9C1-\uA9CE\uA9DA-\uA9DF\uA9FF\uAA37-\uAA3F\uAA4E\uAA4F\uAA5A-\uAA5F\uAA77-\uAA79\uAAC3-\uAADA\uAADE\uAADF\uAAF0\uAAF1\uAAF7-\uAB00\uAB07\uAB08\uAB0F\uAB10\uAB17-\uAB1F\uAB27\uAB2F\uAB5B\uAB6A-\uAB6F\uABEB\uABEE\uABEF\uABFA-\uABFF\uD7A4-\uD7AF\uD7C7-\uD7CA\uD7FC-\uD7FF\uE000-\uF8FF\uFA6E\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB29\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBB2-\uFBD2\uFD3E-\uFD4F\uFD90\uFD91\uFDC8-\uFDEF\uFDFC-\uFDFF\uFE10-\uFE1F\uFE30-\uFE32\uFE35-\uFE4C\uFE50-\uFE6F\uFE75\uFEFD-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF3E\uFF40\uFF5B-\uFF65\uFFBF-\uFFC1\uFFC8\uFFC9\uFFD0\uFFD1\uFFD8\uFFD9\uFFDD-\uFFFF]|\uD800[\uDC0C\uDC27\uDC3B\uDC3E\uDC4E\uDC4F\uDC5E-\uDC7F\uDCFB-\uDD3F\uDD75-\uDDFC\uDDFE-\uDE7F\uDE9D-\uDE9F\uDED1-\uDEDF\uDEE1-\uDEFF\uDF20-\uDF2C\uDF4B-\uDF4F\uDF7B-\uDF7F\uDF9E\uDF9F\uDFC4-\uDFC7\uDFD0\uDFD6-\uDFFF]|\uD801[\uDC9E\uDC9F\uDCAA-\uDCAF\uDCD4-\uDCD7\uDCFC-\uDCFF\uDD28-\uDD2F\uDD64-\uDDFF\uDF37-\uDF3F\uDF56-\uDF5F\uDF68-\uDFFF]|\uD802[\uDC06\uDC07\uDC09\uDC36\uDC39-\uDC3B\uDC3D\uDC3E\uDC56-\uDC5F\uDC77-\uDC7F\uDC9F-\uDCDF\uDCF3\uDCF6-\uDCFF\uDD16-\uDD1F\uDD3A-\uDD7F\uDDB8-\uDDBD\uDDC0-\uDDFF\uDE04\uDE07-\uDE0B\uDE14\uDE18\uDE36\uDE37\uDE3B-\uDE3E\uDE40-\uDE5F\uDE7D-\uDE7F\uDE9D-\uDEBF\uDEC8\uDEE7-\uDEFF\uDF36-\uDF3F\uDF56-\uDF5F\uDF73-\uDF7F\uDF92-\uDFFF]|\uD803[\uDC49-\uDC7F\uDCB3-\uDCBF\uDCF3-\uDCFF\uDD28-\uDD2F\uDD3A-\uDE7F\uDEAA\uDEAD-\uDEAF\uDEB2-\uDEFF\uDF1D-\uDF26\uDF28-\uDF2F\uDF51-\uDFAF\uDFC5-\uDFDF\uDFF7-\uDFFF]|\uD804[\uDC47-\uDC65\uDC70-\uDC7E\uDCBB-\uDCCF\uDCE9-\uDCEF\uDCFA-\uDCFF\uDD35\uDD40-\uDD43\uDD48-\uDD4F\uDD74\uDD75\uDD77-\uDD7F\uDDC5-\uDDC8\uDDCD\uDDDB\uDDDD-\uDDFF\uDE12\uDE38-\uDE3D\uDE3F-\uDE7F\uDE87\uDE89\uDE8E\uDE9E\uDEA9-\uDEAF\uDEEB-\uDEEF\uDEFA-\uDEFF\uDF04\uDF0D\uDF0E\uDF11\uDF12\uDF29\uDF31\uDF34\uDF3A\uDF45\uDF46\uDF49\uDF4A\uDF4E\uDF4F\uDF51-\uDF56\uDF58-\uDF5C\uDF64\uDF65\uDF6D-\uDF6F\uDF75-\uDFFF]|\uD805[\uDC4B-\uDC4F\uDC5A-\uDC5D\uDC62-\uDC7F\uDCC6\uDCC8-\uDCCF\uDCDA-\uDD7F\uDDB6\uDDB7\uDDC1-\uDDD7\uDDDE-\uDDFF\uDE41-\uDE43\uDE45-\uDE4F\uDE5A-\uDE7F\uDEB9-\uDEBF\uDECA-\uDEFF\uDF1B\uDF1C\uDF2C-\uDF2F\uDF3A-\uDFFF]|\uD806[\uDC3B-\uDC9F\uDCEA-\uDCFE\uDD07\uDD08\uDD0A\uDD0B\uDD14\uDD17\uDD36\uDD39\uDD3A\uDD44-\uDD4F\uDD5A-\uDD9F\uDDA8\uDDA9\uDDD8\uDDD9\uDDE2\uDDE5-\uDDFF\uDE3F-\uDE46\uDE48-\uDE4F\uDE9A-\uDE9C\uDE9E-\uDEBF\uDEF9-\uDFFF]|\uD807[\uDC09\uDC37\uDC41-\uDC4F\uDC5A-\uDC71\uDC90\uDC91\uDCA8\uDCB7-\uDCFF\uDD07\uDD0A\uDD37-\uDD39\uDD3B\uDD3E\uDD48-\uDD4F\uDD5A-\uDD5F\uDD66\uDD69\uDD8F\uDD92\uDD99-\uDD9F\uDDAA-\uDEDF\uDEF7-\uDFAF\uDFB1-\uDFFF]|\uD808[\uDF9A-\uDFFF]|\uD809[\uDC6F-\uDC7F\uDD44-\uDFFF]|[\uD80A\uD80B\uD80E-\uD810\uD812-\uD819\uD824-\uD82B\uD82D\uD82E\uD830-\uD833\uD837\uD839\uD83D\uD83F\uD87B-\uD87D\uD87F\uD885-\uDB3F\uDB41-\uDBFF][\uDC00-\uDFFF]|\uD80D[\uDC2F-\uDFFF]|\uD811[\uDE47-\uDFFF]|\uD81A[\uDE39-\uDE3F\uDE5F\uDE6A-\uDECF\uDEEE\uDEEF\uDEF5-\uDEFF\uDF37-\uDF3F\uDF44-\uDF4F\uDF5A-\uDF62\uDF78-\uDF7C\uDF90-\uDFFF]|\uD81B[\uDC00-\uDE3F\uDE80-\uDEFF\uDF4B-\uDF4E\uDF88-\uDF8E\uDFA0-\uDFDF\uDFE2\uDFE5-\uDFEF\uDFF2-\uDFFF]|\uD821[\uDFF8-\uDFFF]|\uD823[\uDCD6-\uDCFF\uDD09-\uDFFF]|\uD82C[\uDD1F-\uDD4F\uDD53-\uDD63\uDD68-\uDD6F\uDEFC-\uDFFF]|\uD82F[\uDC6B-\uDC6F\uDC7D-\uDC7F\uDC89-\uDC8F\uDC9A-\uDC9C\uDC9F-\uDFFF]|\uD834[\uDC00-\uDD64\uDD6A-\uDD6C\uDD73-\uDD7A\uDD83\uDD84\uDD8C-\uDDA9\uDDAE-\uDE41\uDE45-\uDFFF]|\uD835[\uDC55\uDC9D\uDCA0\uDCA1\uDCA3\uDCA4\uDCA7\uDCA8\uDCAD\uDCBA\uDCBC\uDCC4\uDD06\uDD0B\uDD0C\uDD15\uDD1D\uDD3A\uDD3F\uDD45\uDD47-\uDD49\uDD51\uDEA6\uDEA7\uDEC1\uDEDB\uDEFB\uDF15\uDF35\uDF4F\uDF6F\uDF89\uDFA9\uDFC3\uDFCC\uDFCD]|\uD836[\uDC00-\uDDFF\uDE37-\uDE3A\uDE6D-\uDE74\uDE76-\uDE83\uDE85-\uDE9A\uDEA0\uDEB0-\uDFFF]|\uD838[\uDC07\uDC19\uDC1A\uDC22\uDC25\uDC2B-\uDCFF\uDD2D-\uDD2F\uDD3E\uDD3F\uDD4A-\uDD4D\uDD4F-\uDEBF\uDEFA-\uDFFF]|\uD83A[\uDCC5-\uDCCF\uDCD7-\uDCFF\uDD4C-\uDD4F\uDD5A-\uDFFF]|\uD83B[\uDC00-\uDDFF\uDE04\uDE20\uDE23\uDE25\uDE26\uDE28\uDE33\uDE38\uDE3A\uDE3C-\uDE41\uDE43-\uDE46\uDE48\uDE4A\uDE4C\uDE50\uDE53\uDE55\uDE56\uDE58\uDE5A\uDE5C\uDE5E\uDE60\uDE63\uDE65\uDE66\uDE6B\uDE73\uDE78\uDE7D\uDE7F\uDE8A\uDE9C-\uDEA0\uDEA4\uDEAA\uDEBC-\uDFFF]|\uD83C[\uDC00-\uDD2F\uDD4A-\uDD4F\uDD6A-\uDD6F\uDD8A-\uDFFF]|\uD83E[\uDC00-\uDFEF\uDFFA-\uDFFF]|\uD869[\uDEDE-\uDEFF]|\uD86D[\uDF35-\uDF3F]|\uD86E[\uDC1E\uDC1F]|\uD873[\uDEA2-\uDEAF]|\uD87A[\uDFE1-\uDFFF]|\uD87E[\uDE1E-\uDFFF]|\uD884[\uDF4B-\uDFFF]|\uDB40[\uDC00-\uDCFF\uDDF0-\uDFFF]/g, Vn = Object.hasOwnProperty;
class yt {
  /**
   * Create a new slug class.
   */
  constructor() {
    this.occurrences, this.reset();
  }
  /**
   * Generate a unique slug.
  *
  * Tracks previously generated slugs: repeated calls with the same value
  * will result in different slugs.
  * Use the `slug` function to get same slugs.
   *
   * @param  {string} value
   *   String of text to slugify
   * @param  {boolean} [maintainCase=false]
   *   Keep the current case, otherwise make all lowercase
   * @return {string}
   *   A unique slug string
   */
  slug(e, t) {
    const n = this;
    let i = Jn(e, t === !0);
    const a = i;
    for (; Vn.call(n.occurrences, i); )
      n.occurrences[a]++, i = a + "-" + n.occurrences[a];
    return n.occurrences[i] = 0, i;
  }
  /**
   * Reset - Forget all previous slugs
   *
   * @return void
   */
  reset() {
    this.occurrences = /* @__PURE__ */ Object.create(null);
  }
}
function Jn(r, e) {
  return typeof r != "string" ? "" : (e || (r = r.toLowerCase()), r.replace(Qn, "").replace(/ /g, "-"));
}
new yt();
var tt = typeof globalThis < "u" ? globalThis : typeof window < "u" ? window : typeof global < "u" ? global : typeof self < "u" ? self : {}, ei = { exports: {} };
(function(r) {
  var e = typeof window < "u" ? window : typeof WorkerGlobalScope < "u" && self instanceof WorkerGlobalScope ? self : {};
  /**
   * Prism: Lightweight, robust, elegant syntax highlighting
   *
   * @license MIT <https://opensource.org/licenses/MIT>
   * @author Lea Verou <https://lea.verou.me>
   * @namespace
   * @public
   */
  var t = function(n) {
    var i = /(?:^|\s)lang(?:uage)?-([\w-]+)(?=\s|$)/i, a = 0, o = {}, l = {
      /**
       * By default, Prism will attempt to highlight all code elements (by calling {@link Prism.highlightAll}) on the
       * current page after the page finished loading. This might be a problem if e.g. you wanted to asynchronously load
       * additional languages or plugins yourself.
       *
       * By setting this value to `true`, Prism will not automatically highlight all code elements on the page.
       *
       * You obviously have to change this value before the automatic highlighting started. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.manual = true;
       * // add a new <script> to load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      manual: n.Prism && n.Prism.manual,
      /**
       * By default, if Prism is in a web worker, it assumes that it is in a worker it created itself, so it uses
       * `addEventListener` to communicate with its parent instance. However, if you're using Prism manually in your
       * own worker, you don't want it to do this.
       *
       * By setting this value to `true`, Prism will not add its own listeners to the worker.
       *
       * You obviously have to change this value before Prism executes. To do this, you can add an
       * empty Prism object into the global scope before loading the Prism script like this:
       *
       * ```js
       * window.Prism = window.Prism || {};
       * Prism.disableWorkerMessageHandler = true;
       * // Load Prism's script
       * ```
       *
       * @default false
       * @type {boolean}
       * @memberof Prism
       * @public
       */
      disableWorkerMessageHandler: n.Prism && n.Prism.disableWorkerMessageHandler,
      /**
       * A namespace for utility methods.
       *
       * All function in this namespace that are not explicitly marked as _public_ are for __internal use only__ and may
       * change or disappear at any time.
       *
       * @namespace
       * @memberof Prism
       */
      util: {
        encode: function _(u) {
          return u instanceof s ? new s(u.type, _(u.content), u.alias) : Array.isArray(u) ? u.map(_) : u.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/\u00a0/g, " ");
        },
        /**
         * Returns the name of the type of the given value.
         *
         * @param {any} o
         * @returns {string}
         * @example
         * type(null)      === 'Null'
         * type(undefined) === 'Undefined'
         * type(123)       === 'Number'
         * type('foo')     === 'String'
         * type(true)      === 'Boolean'
         * type([1, 2])    === 'Array'
         * type({})        === 'Object'
         * type(String)    === 'Function'
         * type(/abc+/)    === 'RegExp'
         */
        type: function(_) {
          return Object.prototype.toString.call(_).slice(8, -1);
        },
        /**
         * Returns a unique number for the given object. Later calls will still return the same number.
         *
         * @param {Object} obj
         * @returns {number}
         */
        objId: function(_) {
          return _.__id || Object.defineProperty(_, "__id", { value: ++a }), _.__id;
        },
        /**
         * Creates a deep clone of the given object.
         *
         * The main intended use of this function is to clone language definitions.
         *
         * @param {T} o
         * @param {Record<number, any>} [visited]
         * @returns {T}
         * @template T
         */
        clone: function _(u, h) {
          h = h || {};
          var f, g;
          switch (l.util.type(u)) {
            case "Object":
              if (g = l.util.objId(u), h[g])
                return h[g];
              f = /** @type {Record<string, any>} */
              {}, h[g] = f;
              for (var v in u)
                u.hasOwnProperty(v) && (f[v] = _(u[v], h));
              return (
                /** @type {any} */
                f
              );
            case "Array":
              return g = l.util.objId(u), h[g] ? h[g] : (f = [], h[g] = f, /** @type {Array} */
              /** @type {any} */
              u.forEach(function(E, F) {
                f[F] = _(E, h);
              }), /** @type {any} */
              f);
            default:
              return u;
          }
        },
        /**
         * Returns the Prism language of the given element set by a `language-xxxx` or `lang-xxxx` class.
         *
         * If no language is set for the element or the element is `null` or `undefined`, `none` will be returned.
         *
         * @param {Element} element
         * @returns {string}
         */
        getLanguage: function(_) {
          for (; _; ) {
            var u = i.exec(_.className);
            if (u)
              return u[1].toLowerCase();
            _ = _.parentElement;
          }
          return "none";
        },
        /**
         * Sets the Prism `language-xxxx` class of the given element.
         *
         * @param {Element} element
         * @param {string} language
         * @returns {void}
         */
        setLanguage: function(_, u) {
          _.className = _.className.replace(RegExp(i, "gi"), ""), _.classList.add("language-" + u);
        },
        /**
         * Returns the script element that is currently executing.
         *
         * This does __not__ work for line script element.
         *
         * @returns {HTMLScriptElement | null}
         */
        currentScript: function() {
          if (typeof document > "u")
            return null;
          if ("currentScript" in document)
            return (
              /** @type {any} */
              document.currentScript
            );
          try {
            throw new Error();
          } catch (f) {
            var _ = (/at [^(\r\n]*\((.*):[^:]+:[^:]+\)$/i.exec(f.stack) || [])[1];
            if (_) {
              var u = document.getElementsByTagName("script");
              for (var h in u)
                if (u[h].src == _)
                  return u[h];
            }
            return null;
          }
        },
        /**
         * Returns whether a given class is active for `element`.
         *
         * The class can be activated if `element` or one of its ancestors has the given class and it can be deactivated
         * if `element` or one of its ancestors has the negated version of the given class. The _negated version_ of the
         * given class is just the given class with a `no-` prefix.
         *
         * Whether the class is active is determined by the closest ancestor of `element` (where `element` itself is
         * closest ancestor) that has the given class or the negated version of it. If neither `element` nor any of its
         * ancestors have the given class or the negated version of it, then the default activation will be returned.
         *
         * In the paradoxical situation where the closest ancestor contains __both__ the given class and the negated
         * version of it, the class is considered active.
         *
         * @param {Element} element
         * @param {string} className
         * @param {boolean} [defaultActivation=false]
         * @returns {boolean}
         */
        isActive: function(_, u, h) {
          for (var f = "no-" + u; _; ) {
            var g = _.classList;
            if (g.contains(u))
              return !0;
            if (g.contains(f))
              return !1;
            _ = _.parentElement;
          }
          return !!h;
        }
      },
      /**
       * This namespace contains all currently loaded languages and the some helper functions to create and modify languages.
       *
       * @namespace
       * @memberof Prism
       * @public
       */
      languages: {
        /**
         * The grammar for plain, unformatted text.
         */
        plain: o,
        plaintext: o,
        text: o,
        txt: o,
        /**
         * Creates a deep copy of the language with the given id and appends the given tokens.
         *
         * If a token in `redef` also appears in the copied language, then the existing token in the copied language
         * will be overwritten at its original position.
         *
         * ## Best practices
         *
         * Since the position of overwriting tokens (token in `redef` that overwrite tokens in the copied language)
         * doesn't matter, they can technically be in any order. However, this can be confusing to others that trying to
         * understand the language definition because, normally, the order of tokens matters in Prism grammars.
         *
         * Therefore, it is encouraged to order overwriting tokens according to the positions of the overwritten tokens.
         * Furthermore, all non-overwriting tokens should be placed after the overwriting ones.
         *
         * @param {string} id The id of the language to extend. This has to be a key in `Prism.languages`.
         * @param {Grammar} redef The new tokens to append.
         * @returns {Grammar} The new language created.
         * @public
         * @example
         * Prism.languages['css-with-colors'] = Prism.languages.extend('css', {
         *     // Prism.languages.css already has a 'comment' token, so this token will overwrite CSS' 'comment' token
         *     // at its original position
         *     'comment': { ... },
         *     // CSS doesn't have a 'color' token, so this token will be appended
         *     'color': /\b(?:red|green|blue)\b/
         * });
         */
        extend: function(_, u) {
          var h = l.util.clone(l.languages[_]);
          for (var f in u)
            h[f] = u[f];
          return h;
        },
        /**
         * Inserts tokens _before_ another token in a language definition or any other grammar.
         *
         * ## Usage
         *
         * This helper method makes it easy to modify existing languages. For example, the CSS language definition
         * not only defines CSS highlighting for CSS documents, but also needs to define highlighting for CSS embedded
         * in HTML through `<style>` elements. To do this, it needs to modify `Prism.languages.markup` and add the
         * appropriate tokens. However, `Prism.languages.markup` is a regular JavaScript object literal, so if you do
         * this:
         *
         * ```js
         * Prism.languages.markup.style = {
         *     // token
         * };
         * ```
         *
         * then the `style` token will be added (and processed) at the end. `insertBefore` allows you to insert tokens
         * before existing tokens. For the CSS example above, you would use it like this:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'cdata', {
         *     'style': {
         *         // token
         *     }
         * });
         * ```
         *
         * ## Special cases
         *
         * If the grammars of `inside` and `insert` have tokens with the same name, the tokens in `inside`'s grammar
         * will be ignored.
         *
         * This behavior can be used to insert tokens after `before`:
         *
         * ```js
         * Prism.languages.insertBefore('markup', 'comment', {
         *     'comment': Prism.languages.markup.comment,
         *     // tokens after 'comment'
         * });
         * ```
         *
         * ## Limitations
         *
         * The main problem `insertBefore` has to solve is iteration order. Since ES2015, the iteration order for object
         * properties is guaranteed to be the insertion order (except for integer keys) but some browsers behave
         * differently when keys are deleted and re-inserted. So `insertBefore` can't be implemented by temporarily
         * deleting properties which is necessary to insert at arbitrary positions.
         *
         * To solve this problem, `insertBefore` doesn't actually insert the given tokens into the target object.
         * Instead, it will create a new object and replace all references to the target object with the new one. This
         * can be done without temporarily deleting properties, so the iteration order is well-defined.
         *
         * However, only references that can be reached from `Prism.languages` or `insert` will be replaced. I.e. if
         * you hold the target object in a variable, then the value of the variable will not change.
         *
         * ```js
         * var oldMarkup = Prism.languages.markup;
         * var newMarkup = Prism.languages.insertBefore('markup', 'comment', { ... });
         *
         * assert(oldMarkup !== Prism.languages.markup);
         * assert(newMarkup === Prism.languages.markup);
         * ```
         *
         * @param {string} inside The property of `root` (e.g. a language id in `Prism.languages`) that contains the
         * object to be modified.
         * @param {string} before The key to insert before.
         * @param {Grammar} insert An object containing the key-value pairs to be inserted.
         * @param {Object<string, any>} [root] The object containing `inside`, i.e. the object that contains the
         * object to be modified.
         *
         * Defaults to `Prism.languages`.
         * @returns {Grammar} The new grammar object.
         * @public
         */
        insertBefore: function(_, u, h, f) {
          f = f || /** @type {any} */
          l.languages;
          var g = f[_], v = {};
          for (var E in g)
            if (g.hasOwnProperty(E)) {
              if (E == u)
                for (var F in h)
                  h.hasOwnProperty(F) && (v[F] = h[F]);
              h.hasOwnProperty(E) || (v[E] = g[E]);
            }
          var x = f[_];
          return f[_] = v, l.languages.DFS(l.languages, function(P, D) {
            D === x && P != _ && (this[P] = v);
          }), v;
        },
        // Traverse a language definition with Depth First Search
        DFS: function _(u, h, f, g) {
          g = g || {};
          var v = l.util.objId;
          for (var E in u)
            if (u.hasOwnProperty(E)) {
              h.call(u, E, u[E], f || E);
              var F = u[E], x = l.util.type(F);
              x === "Object" && !g[v(F)] ? (g[v(F)] = !0, _(F, h, null, g)) : x === "Array" && !g[v(F)] && (g[v(F)] = !0, _(F, h, E, g));
            }
        }
      },
      plugins: {},
      /**
       * This is the most high-level function in Prism’s API.
       * It fetches all the elements that have a `.language-xxxx` class and then calls {@link Prism.highlightElement} on
       * each one of them.
       *
       * This is equivalent to `Prism.highlightAllUnder(document, async, callback)`.
       *
       * @param {boolean} [async=false] Same as in {@link Prism.highlightAllUnder}.
       * @param {HighlightCallback} [callback] Same as in {@link Prism.highlightAllUnder}.
       * @memberof Prism
       * @public
       */
      highlightAll: function(_, u) {
        l.highlightAllUnder(document, _, u);
      },
      /**
       * Fetches all the descendants of `container` that have a `.language-xxxx` class and then calls
       * {@link Prism.highlightElement} on each one of them.
       *
       * The following hooks will be run:
       * 1. `before-highlightall`
       * 2. `before-all-elements-highlight`
       * 3. All hooks of {@link Prism.highlightElement} for each element.
       *
       * @param {ParentNode} container The root element, whose descendants that have a `.language-xxxx` class will be highlighted.
       * @param {boolean} [async=false] Whether each element is to be highlighted asynchronously using Web Workers.
       * @param {HighlightCallback} [callback] An optional callback to be invoked on each element after its highlighting is done.
       * @memberof Prism
       * @public
       */
      highlightAllUnder: function(_, u, h) {
        var f = {
          callback: h,
          container: _,
          selector: 'code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code'
        };
        l.hooks.run("before-highlightall", f), f.elements = Array.prototype.slice.apply(f.container.querySelectorAll(f.selector)), l.hooks.run("before-all-elements-highlight", f);
        for (var g = 0, v; v = f.elements[g++]; )
          l.highlightElement(v, u === !0, f.callback);
      },
      /**
       * Highlights the code inside a single element.
       *
       * The following hooks will be run:
       * 1. `before-sanity-check`
       * 2. `before-highlight`
       * 3. All hooks of {@link Prism.highlight}. These hooks will be run by an asynchronous worker if `async` is `true`.
       * 4. `before-insert`
       * 5. `after-highlight`
       * 6. `complete`
       *
       * Some the above hooks will be skipped if the element doesn't contain any text or there is no grammar loaded for
       * the element's language.
       *
       * @param {Element} element The element containing the code.
       * It must have a class of `language-xxxx` to be processed, where `xxxx` is a valid language identifier.
       * @param {boolean} [async=false] Whether the element is to be highlighted asynchronously using Web Workers
       * to improve performance and avoid blocking the UI when highlighting very large chunks of code. This option is
       * [disabled by default](https://prismjs.com/faq.html#why-is-asynchronous-highlighting-disabled-by-default).
       *
       * Note: All language definitions required to highlight the code must be included in the main `prism.js` file for
       * asynchronous highlighting to work. You can build your own bundle on the
       * [Download page](https://prismjs.com/download.html).
       * @param {HighlightCallback} [callback] An optional callback to be invoked after the highlighting is done.
       * Mostly useful when `async` is `true`, since in that case, the highlighting is done asynchronously.
       * @memberof Prism
       * @public
       */
      highlightElement: function(_, u, h) {
        var f = l.util.getLanguage(_), g = l.languages[f];
        l.util.setLanguage(_, f);
        var v = _.parentElement;
        v && v.nodeName.toLowerCase() === "pre" && l.util.setLanguage(v, f);
        var E = _.textContent, F = {
          element: _,
          language: f,
          grammar: g,
          code: E
        };
        function x(D) {
          F.highlightedCode = D, l.hooks.run("before-insert", F), F.element.innerHTML = F.highlightedCode, l.hooks.run("after-highlight", F), l.hooks.run("complete", F), h && h.call(F.element);
        }
        if (l.hooks.run("before-sanity-check", F), v = F.element.parentElement, v && v.nodeName.toLowerCase() === "pre" && !v.hasAttribute("tabindex") && v.setAttribute("tabindex", "0"), !F.code) {
          l.hooks.run("complete", F), h && h.call(F.element);
          return;
        }
        if (l.hooks.run("before-highlight", F), !F.grammar) {
          x(l.util.encode(F.code));
          return;
        }
        if (u && n.Worker) {
          var P = new Worker(l.filename);
          P.onmessage = function(D) {
            x(D.data);
          }, P.postMessage(JSON.stringify({
            language: F.language,
            code: F.code,
            immediateClose: !0
          }));
        } else
          x(l.highlight(F.code, F.grammar, F.language));
      },
      /**
       * Low-level function, only use if you know what you’re doing. It accepts a string of text as input
       * and the language definitions to use, and returns a string with the HTML produced.
       *
       * The following hooks will be run:
       * 1. `before-tokenize`
       * 2. `after-tokenize`
       * 3. `wrap`: On each {@link Token}.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @param {string} language The name of the language definition passed to `grammar`.
       * @returns {string} The highlighted HTML.
       * @memberof Prism
       * @public
       * @example
       * Prism.highlight('var foo = true;', Prism.languages.javascript, 'javascript');
       */
      highlight: function(_, u, h) {
        var f = {
          code: _,
          grammar: u,
          language: h
        };
        if (l.hooks.run("before-tokenize", f), !f.grammar)
          throw new Error('The language "' + f.language + '" has no grammar.');
        return f.tokens = l.tokenize(f.code, f.grammar), l.hooks.run("after-tokenize", f), s.stringify(l.util.encode(f.tokens), f.language);
      },
      /**
       * This is the heart of Prism, and the most low-level function you can use. It accepts a string of text as input
       * and the language definitions to use, and returns an array with the tokenized code.
       *
       * When the language definition includes nested tokens, the function is called recursively on each of these tokens.
       *
       * This method could be useful in other contexts as well, as a very crude parser.
       *
       * @param {string} text A string with the code to be highlighted.
       * @param {Grammar} grammar An object containing the tokens to use.
       *
       * Usually a language definition like `Prism.languages.markup`.
       * @returns {TokenStream} An array of strings and tokens, a token stream.
       * @memberof Prism
       * @public
       * @example
       * let code = `var foo = 0;`;
       * let tokens = Prism.tokenize(code, Prism.languages.javascript);
       * tokens.forEach(token => {
       *     if (token instanceof Prism.Token && token.type === 'number') {
       *         console.log(`Found numeric literal: ${token.content}`);
       *     }
       * });
       */
      tokenize: function(_, u) {
        var h = u.rest;
        if (h) {
          for (var f in h)
            u[f] = h[f];
          delete u.rest;
        }
        var g = new p();
        return m(g, g.head, _), d(_, g, u, g.head, 0), R(g);
      },
      /**
       * @namespace
       * @memberof Prism
       * @public
       */
      hooks: {
        all: {},
        /**
         * Adds the given callback to the list of callbacks for the given hook.
         *
         * The callback will be invoked when the hook it is registered for is run.
         * Hooks are usually directly run by a highlight function but you can also run hooks yourself.
         *
         * One callback function can be registered to multiple hooks and the same hook multiple times.
         *
         * @param {string} name The name of the hook.
         * @param {HookCallback} callback The callback function which is given environment variables.
         * @public
         */
        add: function(_, u) {
          var h = l.hooks.all;
          h[_] = h[_] || [], h[_].push(u);
        },
        /**
         * Runs a hook invoking all registered callbacks with the given environment variables.
         *
         * Callbacks will be invoked synchronously and in the order in which they were registered.
         *
         * @param {string} name The name of the hook.
         * @param {Object<string, any>} env The environment variables of the hook passed to all callbacks registered.
         * @public
         */
        run: function(_, u) {
          var h = l.hooks.all[_];
          if (!(!h || !h.length))
            for (var f = 0, g; g = h[f++]; )
              g(u);
        }
      },
      Token: s
    };
    n.Prism = l;
    function s(_, u, h, f) {
      this.type = _, this.content = u, this.alias = h, this.length = (f || "").length | 0;
    }
    s.stringify = function _(u, h) {
      if (typeof u == "string")
        return u;
      if (Array.isArray(u)) {
        var f = "";
        return u.forEach(function(x) {
          f += _(x, h);
        }), f;
      }
      var g = {
        type: u.type,
        content: _(u.content, h),
        tag: "span",
        classes: ["token", u.type],
        attributes: {},
        language: h
      }, v = u.alias;
      v && (Array.isArray(v) ? Array.prototype.push.apply(g.classes, v) : g.classes.push(v)), l.hooks.run("wrap", g);
      var E = "";
      for (var F in g.attributes)
        E += " " + F + '="' + (g.attributes[F] || "").replace(/"/g, "&quot;") + '"';
      return "<" + g.tag + ' class="' + g.classes.join(" ") + '"' + E + ">" + g.content + "</" + g.tag + ">";
    };
    function c(_, u, h, f) {
      _.lastIndex = u;
      var g = _.exec(h);
      if (g && f && g[1]) {
        var v = g[1].length;
        g.index += v, g[0] = g[0].slice(v);
      }
      return g;
    }
    function d(_, u, h, f, g, v) {
      for (var E in h)
        if (!(!h.hasOwnProperty(E) || !h[E])) {
          var F = h[E];
          F = Array.isArray(F) ? F : [F];
          for (var x = 0; x < F.length; ++x) {
            if (v && v.cause == E + "," + x)
              return;
            var P = F[x], D = P.inside, $ = !!P.lookbehind, I = !!P.greedy, N = P.alias;
            if (I && !P.pattern.global) {
              var O = P.pattern.toString().match(/[imsuy]*$/)[0];
              P.pattern = RegExp(P.pattern.source, O + "g");
            }
            for (var z = P.pattern || P, k = f.next, T = g; k !== u.tail && !(v && T >= v.reach); T += k.value.length, k = k.next) {
              var U = k.value;
              if (u.length > _.length)
                return;
              if (!(U instanceof s)) {
                var j = 1, q;
                if (I) {
                  if (q = c(z, T, _, $), !q || q.index >= _.length)
                    break;
                  var _e = q.index, M = q.index + q[0].length, L = T;
                  for (L += k.value.length; _e >= L; )
                    k = k.next, L += k.value.length;
                  if (L -= k.value.length, T = L, k.value instanceof s)
                    continue;
                  for (var ae = k; ae !== u.tail && (L < M || typeof ae.value == "string"); ae = ae.next)
                    j++, L += ae.value.length;
                  j--, U = _.slice(T, L), q.index -= T;
                } else if (q = c(z, 0, U, $), !q)
                  continue;
                var _e = q.index, de = q[0], we = U.slice(0, _e), je = U.slice(_e + de.length), ke = T + U.length;
                v && ke > v.reach && (v.reach = ke);
                var pe = k.prev;
                we && (pe = m(u, pe, we), T += we.length), b(u, pe, j);
                var jt = new s(E, D ? l.tokenize(de, D) : de, N, de);
                if (k = m(u, pe, jt), je && m(u, k, je), j > 1) {
                  var Ce = {
                    cause: E + "," + x,
                    reach: ke
                  };
                  d(_, u, h, k.prev, T, Ce), v && Ce.reach > v.reach && (v.reach = Ce.reach);
                }
              }
            }
          }
        }
    }
    function p() {
      var _ = { value: null, prev: null, next: null }, u = { value: null, prev: _, next: null };
      _.next = u, this.head = _, this.tail = u, this.length = 0;
    }
    function m(_, u, h) {
      var f = u.next, g = { value: h, prev: u, next: f };
      return u.next = g, f.prev = g, _.length++, g;
    }
    function b(_, u, h) {
      for (var f = u.next, g = 0; g < h && f !== _.tail; g++)
        f = f.next;
      u.next = f, f.prev = u, _.length -= g;
    }
    function R(_) {
      for (var u = [], h = _.head.next; h !== _.tail; )
        u.push(h.value), h = h.next;
      return u;
    }
    if (!n.document)
      return n.addEventListener && (l.disableWorkerMessageHandler || n.addEventListener("message", function(_) {
        var u = JSON.parse(_.data), h = u.language, f = u.code, g = u.immediateClose;
        n.postMessage(l.highlight(f, l.languages[h], h)), g && n.close();
      }, !1)), l;
    var C = l.util.currentScript();
    C && (l.filename = C.src, C.hasAttribute("data-manual") && (l.manual = !0));
    function w() {
      l.manual || l.highlightAll();
    }
    if (!l.manual) {
      var y = document.readyState;
      y === "loading" || y === "interactive" && C && C.defer ? document.addEventListener("DOMContentLoaded", w) : window.requestAnimationFrame ? window.requestAnimationFrame(w) : window.setTimeout(w, 16);
    }
    return l;
  }(e);
  r.exports && (r.exports = t), typeof tt < "u" && (tt.Prism = t), t.languages.markup = {
    comment: {
      pattern: /<!--(?:(?!<!--)[\s\S])*?-->/,
      greedy: !0
    },
    prolog: {
      pattern: /<\?[\s\S]+?\?>/,
      greedy: !0
    },
    doctype: {
      // https://www.w3.org/TR/xml/#NT-doctypedecl
      pattern: /<!DOCTYPE(?:[^>"'[\]]|"[^"]*"|'[^']*')+(?:\[(?:[^<"'\]]|"[^"]*"|'[^']*'|<(?!!--)|<!--(?:[^-]|-(?!->))*-->)*\]\s*)?>/i,
      greedy: !0,
      inside: {
        "internal-subset": {
          pattern: /(^[^\[]*\[)[\s\S]+(?=\]>$)/,
          lookbehind: !0,
          greedy: !0,
          inside: null
          // see below
        },
        string: {
          pattern: /"[^"]*"|'[^']*'/,
          greedy: !0
        },
        punctuation: /^<!|>$|[[\]]/,
        "doctype-tag": /^DOCTYPE/i,
        name: /[^\s<>'"]+/
      }
    },
    cdata: {
      pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
      greedy: !0
    },
    tag: {
      pattern: /<\/?(?!\d)[^\s>\/=$<%]+(?:\s(?:\s*[^\s>\/=]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))|(?=[\s/>])))+)?\s*\/?>/,
      greedy: !0,
      inside: {
        tag: {
          pattern: /^<\/?[^\s>\/]+/,
          inside: {
            punctuation: /^<\/?/,
            namespace: /^[^\s>\/:]+:/
          }
        },
        "special-attr": [],
        "attr-value": {
          pattern: /=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+)/,
          inside: {
            punctuation: [
              {
                pattern: /^=/,
                alias: "attr-equals"
              },
              {
                pattern: /^(\s*)["']|["']$/,
                lookbehind: !0
              }
            ]
          }
        },
        punctuation: /\/?>/,
        "attr-name": {
          pattern: /[^\s>\/]+/,
          inside: {
            namespace: /^[^\s>\/:]+:/
          }
        }
      }
    },
    entity: [
      {
        pattern: /&[\da-z]{1,8};/i,
        alias: "named-entity"
      },
      /&#x?[\da-f]{1,8};/i
    ]
  }, t.languages.markup.tag.inside["attr-value"].inside.entity = t.languages.markup.entity, t.languages.markup.doctype.inside["internal-subset"].inside = t.languages.markup, t.hooks.add("wrap", function(n) {
    n.type === "entity" && (n.attributes.title = n.content.replace(/&amp;/, "&"));
  }), Object.defineProperty(t.languages.markup.tag, "addInlined", {
    /**
     * Adds an inlined language to markup.
     *
     * An example of an inlined language is CSS with `<style>` tags.
     *
     * @param {string} tagName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addInlined('style', 'css');
     */
    value: function(i, a) {
      var o = {};
      o["language-" + a] = {
        pattern: /(^<!\[CDATA\[)[\s\S]+?(?=\]\]>$)/i,
        lookbehind: !0,
        inside: t.languages[a]
      }, o.cdata = /^<!\[CDATA\[|\]\]>$/i;
      var l = {
        "included-cdata": {
          pattern: /<!\[CDATA\[[\s\S]*?\]\]>/i,
          inside: o
        }
      };
      l["language-" + a] = {
        pattern: /[\s\S]+/,
        inside: t.languages[a]
      };
      var s = {};
      s[i] = {
        pattern: RegExp(/(<__[^>]*>)(?:<!\[CDATA\[(?:[^\]]|\](?!\]>))*\]\]>|(?!<!\[CDATA\[)[\s\S])*?(?=<\/__>)/.source.replace(/__/g, function() {
          return i;
        }), "i"),
        lookbehind: !0,
        greedy: !0,
        inside: l
      }, t.languages.insertBefore("markup", "cdata", s);
    }
  }), Object.defineProperty(t.languages.markup.tag, "addAttribute", {
    /**
     * Adds an pattern to highlight languages embedded in HTML attributes.
     *
     * An example of an inlined language is CSS with `style` attributes.
     *
     * @param {string} attrName The name of the tag that contains the inlined language. This name will be treated as
     * case insensitive.
     * @param {string} lang The language key.
     * @example
     * addAttribute('style', 'css');
     */
    value: function(n, i) {
      t.languages.markup.tag.inside["special-attr"].push({
        pattern: RegExp(
          /(^|["'\s])/.source + "(?:" + n + ")" + /\s*=\s*(?:"[^"]*"|'[^']*'|[^\s'">=]+(?=[\s>]))/.source,
          "i"
        ),
        lookbehind: !0,
        inside: {
          "attr-name": /^[^\s=]+/,
          "attr-value": {
            pattern: /=[\s\S]+/,
            inside: {
              value: {
                pattern: /(^=\s*(["']|(?!["'])))\S[\s\S]*(?=\2$)/,
                lookbehind: !0,
                alias: [i, "language-" + i],
                inside: t.languages[i]
              },
              punctuation: [
                {
                  pattern: /^=/,
                  alias: "attr-equals"
                },
                /"|'/
              ]
            }
          }
        }
      });
    }
  }), t.languages.html = t.languages.markup, t.languages.mathml = t.languages.markup, t.languages.svg = t.languages.markup, t.languages.xml = t.languages.extend("markup", {}), t.languages.ssml = t.languages.xml, t.languages.atom = t.languages.xml, t.languages.rss = t.languages.xml, function(n) {
    var i = /(?:"(?:\\(?:\r\n|[\s\S])|[^"\\\r\n])*"|'(?:\\(?:\r\n|[\s\S])|[^'\\\r\n])*')/;
    n.languages.css = {
      comment: /\/\*[\s\S]*?\*\//,
      atrule: {
        pattern: RegExp("@[\\w-](?:" + /[^;{\s"']|\s+(?!\s)/.source + "|" + i.source + ")*?" + /(?:;|(?=\s*\{))/.source),
        inside: {
          rule: /^@[\w-]+/,
          "selector-function-argument": {
            pattern: /(\bselector\s*\(\s*(?![\s)]))(?:[^()\s]|\s+(?![\s)])|\((?:[^()]|\([^()]*\))*\))+(?=\s*\))/,
            lookbehind: !0,
            alias: "selector"
          },
          keyword: {
            pattern: /(^|[^\w-])(?:and|not|only|or)(?![\w-])/,
            lookbehind: !0
          }
          // See rest below
        }
      },
      url: {
        // https://drafts.csswg.org/css-values-3/#urls
        pattern: RegExp("\\burl\\((?:" + i.source + "|" + /(?:[^\\\r\n()"']|\\[\s\S])*/.source + ")\\)", "i"),
        greedy: !0,
        inside: {
          function: /^url/i,
          punctuation: /^\(|\)$/,
          string: {
            pattern: RegExp("^" + i.source + "$"),
            alias: "url"
          }
        }
      },
      selector: {
        pattern: RegExp(`(^|[{}\\s])[^{}\\s](?:[^{};"'\\s]|\\s+(?![\\s{])|` + i.source + ")*(?=\\s*\\{)"),
        lookbehind: !0
      },
      string: {
        pattern: i,
        greedy: !0
      },
      property: {
        pattern: /(^|[^-\w\xA0-\uFFFF])(?!\s)[-_a-z\xA0-\uFFFF](?:(?!\s)[-\w\xA0-\uFFFF])*(?=\s*:)/i,
        lookbehind: !0
      },
      important: /!important\b/i,
      function: {
        pattern: /(^|[^-a-z0-9])[-a-z0-9]+(?=\()/i,
        lookbehind: !0
      },
      punctuation: /[(){};:,]/
    }, n.languages.css.atrule.inside.rest = n.languages.css;
    var a = n.languages.markup;
    a && (a.tag.addInlined("style", "css"), a.tag.addAttribute("style", "css"));
  }(t), t.languages.clike = {
    comment: [
      {
        pattern: /(^|[^\\])\/\*[\s\S]*?(?:\*\/|$)/,
        lookbehind: !0,
        greedy: !0
      },
      {
        pattern: /(^|[^\\:])\/\/.*/,
        lookbehind: !0,
        greedy: !0
      }
    ],
    string: {
      pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
      greedy: !0
    },
    "class-name": {
      pattern: /(\b(?:class|extends|implements|instanceof|interface|new|trait)\s+|\bcatch\s+\()[\w.\\]+/i,
      lookbehind: !0,
      inside: {
        punctuation: /[.\\]/
      }
    },
    keyword: /\b(?:break|catch|continue|do|else|finally|for|function|if|in|instanceof|new|null|return|throw|try|while)\b/,
    boolean: /\b(?:false|true)\b/,
    function: /\b\w+(?=\()/,
    number: /\b0x[\da-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:e[+-]?\d+)?/i,
    operator: /[<>]=?|[!=]=?=?|--?|\+\+?|&&?|\|\|?|[?*/~^%]/,
    punctuation: /[{}[\];(),.:]/
  }, t.languages.javascript = t.languages.extend("clike", {
    "class-name": [
      t.languages.clike["class-name"],
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$A-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\.(?:constructor|prototype))/,
        lookbehind: !0
      }
    ],
    keyword: [
      {
        pattern: /((?:^|\})\s*)catch\b/,
        lookbehind: !0
      },
      {
        pattern: /(^|[^.]|\.\.\.\s*)\b(?:as|assert(?=\s*\{)|async(?=\s*(?:function\b|\(|[$\w\xA0-\uFFFF]|$))|await|break|case|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally(?=\s*(?:\{|$))|for|from(?=\s*(?:['"]|$))|function|(?:get|set)(?=\s*(?:[#\[$\w\xA0-\uFFFF]|$))|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)\b/,
        lookbehind: !0
      }
    ],
    // Allow for all non-ASCII characters (See http://stackoverflow.com/a/2008444)
    function: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*(?:\.\s*(?:apply|bind|call)\s*)?\()/,
    number: {
      pattern: RegExp(
        /(^|[^\w$])/.source + "(?:" + // constant
        (/NaN|Infinity/.source + "|" + // binary integer
        /0[bB][01]+(?:_[01]+)*n?/.source + "|" + // octal integer
        /0[oO][0-7]+(?:_[0-7]+)*n?/.source + "|" + // hexadecimal integer
        /0[xX][\dA-Fa-f]+(?:_[\dA-Fa-f]+)*n?/.source + "|" + // decimal bigint
        /\d+(?:_\d+)*n/.source + "|" + // decimal number (integer or float) but no bigint
        /(?:\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\.\d+(?:_\d+)*)(?:[Ee][+-]?\d+(?:_\d+)*)?/.source) + ")" + /(?![\w$])/.source
      ),
      lookbehind: !0
    },
    operator: /--|\+\+|\*\*=?|=>|&&=?|\|\|=?|[!=]==|<<=?|>>>?=?|[-+*/%&|^!=<>]=?|\.{3}|\?\?=?|\?\.?|[~:]/
  }), t.languages.javascript["class-name"][0].pattern = /(\b(?:class|extends|implements|instanceof|interface|new)\s+)[\w.\\]+/, t.languages.insertBefore("javascript", "keyword", {
    regex: {
      pattern: RegExp(
        // lookbehind
        // eslint-disable-next-line regexp/no-dupe-characters-character-class
        /((?:^|[^$\w\xA0-\uFFFF."'\])\s]|\b(?:return|yield))\s*)/.source + // Regex pattern:
        // There are 2 regex patterns here. The RegExp set notation proposal added support for nested character
        // classes if the `v` flag is present. Unfortunately, nested CCs are both context-free and incompatible
        // with the only syntax, so we have to define 2 different regex patterns.
        /\//.source + "(?:" + /(?:\[(?:[^\]\\\r\n]|\\.)*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}/.source + "|" + // `v` flag syntax. This supports 3 levels of nested character classes.
        /(?:\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.|\[(?:[^[\]\\\r\n]|\\.)*\])*\])*\]|\\.|[^/\\\[\r\n])+\/[dgimyus]{0,7}v[dgimyus]{0,7}/.source + ")" + // lookahead
        /(?=(?:\s|\/\*(?:[^*]|\*(?!\/))*\*\/)*(?:$|[\r\n,.;:})\]]|\/\/))/.source
      ),
      lookbehind: !0,
      greedy: !0,
      inside: {
        "regex-source": {
          pattern: /^(\/)[\s\S]+(?=\/[a-z]*$)/,
          lookbehind: !0,
          alias: "language-regex",
          inside: t.languages.regex
        },
        "regex-delimiter": /^\/|\/$/,
        "regex-flags": /^[a-z]+$/
      }
    },
    // This must be declared before keyword because we use "function" inside the look-forward
    "function-variable": {
      pattern: /#?(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*[=:]\s*(?:async\s*)?(?:\bfunction\b|(?:\((?:[^()]|\([^()]*\))*\)|(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)\s*=>))/,
      alias: "function"
    },
    parameter: [
      {
        pattern: /(function(?:\s+(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*)?\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\))/,
        lookbehind: !0,
        inside: t.languages.javascript
      },
      {
        pattern: /(^|[^$\w\xA0-\uFFFF])(?!\s)[_$a-z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*=>)/i,
        lookbehind: !0,
        inside: t.languages.javascript
      },
      {
        pattern: /(\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*=>)/,
        lookbehind: !0,
        inside: t.languages.javascript
      },
      {
        pattern: /((?:\b|\s|^)(?!(?:as|async|await|break|case|catch|class|const|continue|debugger|default|delete|do|else|enum|export|extends|finally|for|from|function|get|if|implements|import|in|instanceof|interface|let|new|null|of|package|private|protected|public|return|set|static|super|switch|this|throw|try|typeof|undefined|var|void|while|with|yield)(?![$\w\xA0-\uFFFF]))(?:(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*\s*)\(\s*|\]\s*\(\s*)(?!\s)(?:[^()\s]|\s+(?![\s)])|\([^()]*\))+(?=\s*\)\s*\{)/,
        lookbehind: !0,
        inside: t.languages.javascript
      }
    ],
    constant: /\b[A-Z](?:[A-Z_]|\dx?)*\b/
  }), t.languages.insertBefore("javascript", "string", {
    hashbang: {
      pattern: /^#!.*/,
      greedy: !0,
      alias: "comment"
    },
    "template-string": {
      pattern: /`(?:\\[\s\S]|\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}|(?!\$\{)[^\\`])*`/,
      greedy: !0,
      inside: {
        "template-punctuation": {
          pattern: /^`|`$/,
          alias: "string"
        },
        interpolation: {
          pattern: /((?:^|[^\\])(?:\\{2})*)\$\{(?:[^{}]|\{(?:[^{}]|\{[^}]*\})*\})+\}/,
          lookbehind: !0,
          inside: {
            "interpolation-punctuation": {
              pattern: /^\$\{|\}$/,
              alias: "punctuation"
            },
            rest: t.languages.javascript
          }
        },
        string: /[\s\S]+/
      }
    },
    "string-property": {
      pattern: /((?:^|[,{])[ \t]*)(["'])(?:\\(?:\r\n|[\s\S])|(?!\2)[^\\\r\n])*\2(?=\s*:)/m,
      lookbehind: !0,
      greedy: !0,
      alias: "property"
    }
  }), t.languages.insertBefore("javascript", "operator", {
    "literal-property": {
      pattern: /((?:^|[,{])[ \t]*)(?!\s)[_$a-zA-Z\xA0-\uFFFF](?:(?!\s)[$\w\xA0-\uFFFF])*(?=\s*:)/m,
      lookbehind: !0,
      alias: "property"
    }
  }), t.languages.markup && (t.languages.markup.tag.addInlined("script", "javascript"), t.languages.markup.tag.addAttribute(
    /on(?:abort|blur|change|click|composition(?:end|start|update)|dblclick|error|focus(?:in|out)?|key(?:down|up)|load|mouse(?:down|enter|leave|move|out|over|up)|reset|resize|scroll|select|slotchange|submit|unload|wheel)/.source,
    "javascript"
  )), t.languages.js = t.languages.javascript, function() {
    if (typeof t > "u" || typeof document > "u")
      return;
    Element.prototype.matches || (Element.prototype.matches = Element.prototype.msMatchesSelector || Element.prototype.webkitMatchesSelector);
    var n = "Loading…", i = function(C, w) {
      return "✖ Error " + C + " while fetching file: " + w;
    }, a = "✖ Error: File does not exist or is empty", o = {
      js: "javascript",
      py: "python",
      rb: "ruby",
      ps1: "powershell",
      psm1: "powershell",
      sh: "bash",
      bat: "batch",
      h: "c",
      tex: "latex"
    }, l = "data-src-status", s = "loading", c = "loaded", d = "failed", p = "pre[data-src]:not([" + l + '="' + c + '"]):not([' + l + '="' + s + '"])';
    function m(C, w, y) {
      var _ = new XMLHttpRequest();
      _.open("GET", C, !0), _.onreadystatechange = function() {
        _.readyState == 4 && (_.status < 400 && _.responseText ? w(_.responseText) : _.status >= 400 ? y(i(_.status, _.statusText)) : y(a));
      }, _.send(null);
    }
    function b(C) {
      var w = /^\s*(\d+)\s*(?:(,)\s*(?:(\d+)\s*)?)?$/.exec(C || "");
      if (w) {
        var y = Number(w[1]), _ = w[2], u = w[3];
        return _ ? u ? [y, Number(u)] : [y, void 0] : [y, y];
      }
    }
    t.hooks.add("before-highlightall", function(C) {
      C.selector += ", " + p;
    }), t.hooks.add("before-sanity-check", function(C) {
      var w = (
        /** @type {HTMLPreElement} */
        C.element
      );
      if (w.matches(p)) {
        C.code = "", w.setAttribute(l, s);
        var y = w.appendChild(document.createElement("CODE"));
        y.textContent = n;
        var _ = w.getAttribute("data-src"), u = C.language;
        if (u === "none") {
          var h = (/\.(\w+)$/.exec(_) || [, "none"])[1];
          u = o[h] || h;
        }
        t.util.setLanguage(y, u), t.util.setLanguage(w, u);
        var f = t.plugins.autoloader;
        f && f.loadLanguages(u), m(
          _,
          function(g) {
            w.setAttribute(l, c);
            var v = b(w.getAttribute("data-range"));
            if (v) {
              var E = g.split(/\r\n?|\n/g), F = v[0], x = v[1] == null ? E.length : v[1];
              F < 0 && (F += E.length), F = Math.max(0, Math.min(F - 1, E.length)), x < 0 && (x += E.length), x = Math.max(0, Math.min(x, E.length)), g = E.slice(F, x).join(`
`), w.hasAttribute("data-start") || w.setAttribute("data-start", String(F + 1));
            }
            y.textContent = g, t.highlightElement(y);
          },
          function(g) {
            w.setAttribute(l, d), y.textContent = g;
          }
        );
      }
    }), t.plugins.fileHighlight = {
      /**
       * Executes the File Highlight plugin for all matching `pre` elements under the given container.
       *
       * Note: Elements which are already loaded or currently loading will not be touched by this method.
       *
       * @param {ParentNode} [container=document]
       */
      highlight: function(w) {
        for (var y = (w || document).querySelectorAll(p), _ = 0, u; u = y[_++]; )
          t.highlightElement(u);
      }
    };
    var R = !1;
    t.fileHighlight = function() {
      R || (console.warn("Prism.fileHighlight is deprecated. Use `Prism.plugins.fileHighlight.highlight` instead."), R = !0), t.plugins.fileHighlight.highlight.apply(this, arguments);
    };
  }();
})(ei);
Prism.languages.python = {
  comment: {
    pattern: /(^|[^\\])#.*/,
    lookbehind: !0,
    greedy: !0
  },
  "string-interpolation": {
    pattern: /(?:f|fr|rf)(?:("""|''')[\s\S]*?\1|("|')(?:\\.|(?!\2)[^\\\r\n])*\2)/i,
    greedy: !0,
    inside: {
      interpolation: {
        // "{" <expression> <optional "!s", "!r", or "!a"> <optional ":" format specifier> "}"
        pattern: /((?:^|[^{])(?:\{\{)*)\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}]|\{(?!\{)(?:[^{}])+\})+\})+\}/,
        lookbehind: !0,
        inside: {
          "format-spec": {
            pattern: /(:)[^:(){}]+(?=\}$)/,
            lookbehind: !0
          },
          "conversion-option": {
            pattern: /![sra](?=[:}]$)/,
            alias: "punctuation"
          },
          rest: null
        }
      },
      string: /[\s\S]+/
    }
  },
  "triple-quoted-string": {
    pattern: /(?:[rub]|br|rb)?("""|''')[\s\S]*?\1/i,
    greedy: !0,
    alias: "string"
  },
  string: {
    pattern: /(?:[rub]|br|rb)?("|')(?:\\.|(?!\1)[^\\\r\n])*\1/i,
    greedy: !0
  },
  function: {
    pattern: /((?:^|\s)def[ \t]+)[a-zA-Z_]\w*(?=\s*\()/g,
    lookbehind: !0
  },
  "class-name": {
    pattern: /(\bclass\s+)\w+/i,
    lookbehind: !0
  },
  decorator: {
    pattern: /(^[\t ]*)@\w+(?:\.\w+)*/m,
    lookbehind: !0,
    alias: ["annotation", "punctuation"],
    inside: {
      punctuation: /\./
    }
  },
  keyword: /\b(?:_(?=\s*:)|and|as|assert|async|await|break|case|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|match|nonlocal|not|or|pass|print|raise|return|try|while|with|yield)\b/,
  builtin: /\b(?:__import__|abs|all|any|apply|ascii|basestring|bin|bool|buffer|bytearray|bytes|callable|chr|classmethod|cmp|coerce|compile|complex|delattr|dict|dir|divmod|enumerate|eval|execfile|file|filter|float|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|int|intern|isinstance|issubclass|iter|len|list|locals|long|map|max|memoryview|min|next|object|oct|open|ord|pow|property|range|raw_input|reduce|reload|repr|reversed|round|set|setattr|slice|sorted|staticmethod|str|sum|super|tuple|type|unichr|unicode|vars|xrange|zip)\b/,
  boolean: /\b(?:False|None|True)\b/,
  number: /\b0(?:b(?:_?[01])+|o(?:_?[0-7])+|x(?:_?[a-f0-9])+)\b|(?:\b\d+(?:_\d+)*(?:\.(?:\d+(?:_\d+)*)?)?|\B\.\d+(?:_\d+)*)(?:e[+-]?\d+(?:_\d+)*)?j?(?!\w)/i,
  operator: /[-+%=]=?|!=|:=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]/,
  punctuation: /[{}[\];(),.:]/
};
Prism.languages.python["string-interpolation"].inside.interpolation.inside.rest = Prism.languages.python;
Prism.languages.py = Prism.languages.python;
(function(r) {
  var e = /\\(?:[^a-z()[\]]|[a-z*]+)/i, t = {
    "equation-command": {
      pattern: e,
      alias: "regex"
    }
  };
  r.languages.latex = {
    comment: /%.*/,
    // the verbatim environment prints whitespace to the document
    cdata: {
      pattern: /(\\begin\{((?:lstlisting|verbatim)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
      lookbehind: !0
    },
    /*
     * equations can be between $$ $$ or $ $ or \( \) or \[ \]
     * (all are multiline)
     */
    equation: [
      {
        pattern: /\$\$(?:\\[\s\S]|[^\\$])+\$\$|\$(?:\\[\s\S]|[^\\$])+\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]/,
        inside: t,
        alias: "string"
      },
      {
        pattern: /(\\begin\{((?:align|eqnarray|equation|gather|math|multline)\*?)\})[\s\S]*?(?=\\end\{\2\})/,
        lookbehind: !0,
        inside: t,
        alias: "string"
      }
    ],
    /*
     * arguments which are keywords or references are highlighted
     * as keywords
     */
    keyword: {
      pattern: /(\\(?:begin|cite|documentclass|end|label|ref|usepackage)(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    url: {
      pattern: /(\\url\{)[^}]+(?=\})/,
      lookbehind: !0
    },
    /*
     * section or chapter headlines are highlighted as bold so that
     * they stand out more
     */
    headline: {
      pattern: /(\\(?:chapter|frametitle|paragraph|part|section|subparagraph|subsection|subsubparagraph|subsubsection|subsubsubparagraph)\*?(?:\[[^\]]+\])?\{)[^}]+(?=\})/,
      lookbehind: !0,
      alias: "class-name"
    },
    function: {
      pattern: e,
      alias: "selector"
    },
    punctuation: /[[\]{}&]/
  }, r.languages.tex = r.languages.latex, r.languages.context = r.languages.latex;
})(Prism);
(function(r) {
  var e = "\\b(?:BASH|BASHOPTS|BASH_ALIASES|BASH_ARGC|BASH_ARGV|BASH_CMDS|BASH_COMPLETION_COMPAT_DIR|BASH_LINENO|BASH_REMATCH|BASH_SOURCE|BASH_VERSINFO|BASH_VERSION|COLORTERM|COLUMNS|COMP_WORDBREAKS|DBUS_SESSION_BUS_ADDRESS|DEFAULTS_PATH|DESKTOP_SESSION|DIRSTACK|DISPLAY|EUID|GDMSESSION|GDM_LANG|GNOME_KEYRING_CONTROL|GNOME_KEYRING_PID|GPG_AGENT_INFO|GROUPS|HISTCONTROL|HISTFILE|HISTFILESIZE|HISTSIZE|HOME|HOSTNAME|HOSTTYPE|IFS|INSTANCE|JOB|LANG|LANGUAGE|LC_ADDRESS|LC_ALL|LC_IDENTIFICATION|LC_MEASUREMENT|LC_MONETARY|LC_NAME|LC_NUMERIC|LC_PAPER|LC_TELEPHONE|LC_TIME|LESSCLOSE|LESSOPEN|LINES|LOGNAME|LS_COLORS|MACHTYPE|MAILCHECK|MANDATORY_PATH|NO_AT_BRIDGE|OLDPWD|OPTERR|OPTIND|ORBIT_SOCKETDIR|OSTYPE|PAPERSIZE|PATH|PIPESTATUS|PPID|PS1|PS2|PS3|PS4|PWD|RANDOM|REPLY|SECONDS|SELINUX_INIT|SESSION|SESSIONTYPE|SESSION_MANAGER|SHELL|SHELLOPTS|SHLVL|SSH_AUTH_SOCK|TERM|UID|UPSTART_EVENTS|UPSTART_INSTANCE|UPSTART_JOB|UPSTART_SESSION|USER|WINDOWID|XAUTHORITY|XDG_CONFIG_DIRS|XDG_CURRENT_DESKTOP|XDG_DATA_DIRS|XDG_GREETER_DATA_DIR|XDG_MENU_PREFIX|XDG_RUNTIME_DIR|XDG_SEAT|XDG_SEAT_PATH|XDG_SESSION_DESKTOP|XDG_SESSION_ID|XDG_SESSION_PATH|XDG_SESSION_TYPE|XDG_VTNR|XMODIFIERS)\\b", t = {
    pattern: /(^(["']?)\w+\2)[ \t]+\S.*/,
    lookbehind: !0,
    alias: "punctuation",
    // this looks reasonably well in all themes
    inside: null
    // see below
  }, n = {
    bash: t,
    environment: {
      pattern: RegExp("\\$" + e),
      alias: "constant"
    },
    variable: [
      // [0]: Arithmetic Environment
      {
        pattern: /\$?\(\([\s\S]+?\)\)/,
        greedy: !0,
        inside: {
          // If there is a $ sign at the beginning highlight $(( and )) as variable
          variable: [
            {
              pattern: /(^\$\(\([\s\S]+)\)\)/,
              lookbehind: !0
            },
            /^\$\(\(/
          ],
          number: /\b0x[\dA-Fa-f]+\b|(?:\b\d+(?:\.\d*)?|\B\.\d+)(?:[Ee]-?\d+)?/,
          // Operators according to https://www.gnu.org/software/bash/manual/bashref.html#Shell-Arithmetic
          operator: /--|\+\+|\*\*=?|<<=?|>>=?|&&|\|\||[=!+\-*/%<>^&|]=?|[?~:]/,
          // If there is no $ sign at the beginning highlight (( and )) as punctuation
          punctuation: /\(\(?|\)\)?|,|;/
        }
      },
      // [1]: Command Substitution
      {
        pattern: /\$\((?:\([^)]+\)|[^()])+\)|`[^`]+`/,
        greedy: !0,
        inside: {
          variable: /^\$\(|^`|\)$|`$/
        }
      },
      // [2]: Brace expansion
      {
        pattern: /\$\{[^}]+\}/,
        greedy: !0,
        inside: {
          operator: /:[-=?+]?|[!\/]|##?|%%?|\^\^?|,,?/,
          punctuation: /[\[\]]/,
          environment: {
            pattern: RegExp("(\\{)" + e),
            lookbehind: !0,
            alias: "constant"
          }
        }
      },
      /\$(?:\w+|[#?*!@$])/
    ],
    // Escape sequences from echo and printf's manuals, and escaped quotes.
    entity: /\\(?:[abceEfnrtv\\"]|O?[0-7]{1,3}|U[0-9a-fA-F]{8}|u[0-9a-fA-F]{4}|x[0-9a-fA-F]{1,2})/
  };
  r.languages.bash = {
    shebang: {
      pattern: /^#!\s*\/.*/,
      alias: "important"
    },
    comment: {
      pattern: /(^|[^"{\\$])#.*/,
      lookbehind: !0
    },
    "function-name": [
      // a) function foo {
      // b) foo() {
      // c) function foo() {
      // but not “foo {”
      {
        // a) and c)
        pattern: /(\bfunction\s+)[\w-]+(?=(?:\s*\(?:\s*\))?\s*\{)/,
        lookbehind: !0,
        alias: "function"
      },
      {
        // b)
        pattern: /\b[\w-]+(?=\s*\(\s*\)\s*\{)/,
        alias: "function"
      }
    ],
    // Highlight variable names as variables in for and select beginnings.
    "for-or-select": {
      pattern: /(\b(?:for|select)\s+)\w+(?=\s+in\s)/,
      alias: "variable",
      lookbehind: !0
    },
    // Highlight variable names as variables in the left-hand part
    // of assignments (“=” and “+=”).
    "assign-left": {
      pattern: /(^|[\s;|&]|[<>]\()\w+(?:\.\w+)*(?=\+?=)/,
      inside: {
        environment: {
          pattern: RegExp("(^|[\\s;|&]|[<>]\\()" + e),
          lookbehind: !0,
          alias: "constant"
        }
      },
      alias: "variable",
      lookbehind: !0
    },
    // Highlight parameter names as variables
    parameter: {
      pattern: /(^|\s)-{1,2}(?:\w+:[+-]?)?\w+(?:\.\w+)*(?=[=\s]|$)/,
      alias: "variable",
      lookbehind: !0
    },
    string: [
      // Support for Here-documents https://en.wikipedia.org/wiki/Here_document
      {
        pattern: /((?:^|[^<])<<-?\s*)(\w+)\s[\s\S]*?(?:\r?\n|\r)\2/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      // Here-document with quotes around the tag
      // → No expansion (so no “inside”).
      {
        pattern: /((?:^|[^<])<<-?\s*)(["'])(\w+)\2\s[\s\S]*?(?:\r?\n|\r)\3/,
        lookbehind: !0,
        greedy: !0,
        inside: {
          bash: t
        }
      },
      // “Normal” string
      {
        // https://www.gnu.org/software/bash/manual/html_node/Double-Quotes.html
        pattern: /(^|[^\\](?:\\\\)*)"(?:\\[\s\S]|\$\([^)]+\)|\$(?!\()|`[^`]+`|[^"\\`$])*"/,
        lookbehind: !0,
        greedy: !0,
        inside: n
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/Single-Quotes.html
        pattern: /(^|[^$\\])'[^']*'/,
        lookbehind: !0,
        greedy: !0
      },
      {
        // https://www.gnu.org/software/bash/manual/html_node/ANSI_002dC-Quoting.html
        pattern: /\$'(?:[^'\\]|\\[\s\S])*'/,
        greedy: !0,
        inside: {
          entity: n.entity
        }
      }
    ],
    environment: {
      pattern: RegExp("\\$?" + e),
      alias: "constant"
    },
    variable: n.variable,
    function: {
      pattern: /(^|[\s;|&]|[<>]\()(?:add|apropos|apt|apt-cache|apt-get|aptitude|aspell|automysqlbackup|awk|basename|bash|bc|bconsole|bg|bzip2|cal|cargo|cat|cfdisk|chgrp|chkconfig|chmod|chown|chroot|cksum|clear|cmp|column|comm|composer|cp|cron|crontab|csplit|curl|cut|date|dc|dd|ddrescue|debootstrap|df|diff|diff3|dig|dir|dircolors|dirname|dirs|dmesg|docker|docker-compose|du|egrep|eject|env|ethtool|expand|expect|expr|fdformat|fdisk|fg|fgrep|file|find|fmt|fold|format|free|fsck|ftp|fuser|gawk|git|gparted|grep|groupadd|groupdel|groupmod|groups|grub-mkconfig|gzip|halt|head|hg|history|host|hostname|htop|iconv|id|ifconfig|ifdown|ifup|import|install|ip|java|jobs|join|kill|killall|less|link|ln|locate|logname|logrotate|look|lpc|lpr|lprint|lprintd|lprintq|lprm|ls|lsof|lynx|make|man|mc|mdadm|mkconfig|mkdir|mke2fs|mkfifo|mkfs|mkisofs|mknod|mkswap|mmv|more|most|mount|mtools|mtr|mutt|mv|nano|nc|netstat|nice|nl|node|nohup|notify-send|npm|nslookup|op|open|parted|passwd|paste|pathchk|ping|pkill|pnpm|podman|podman-compose|popd|pr|printcap|printenv|ps|pushd|pv|quota|quotacheck|quotactl|ram|rar|rcp|reboot|remsync|rename|renice|rev|rm|rmdir|rpm|rsync|scp|screen|sdiff|sed|sendmail|seq|service|sftp|sh|shellcheck|shuf|shutdown|sleep|slocate|sort|split|ssh|stat|strace|su|sudo|sum|suspend|swapon|sync|sysctl|tac|tail|tar|tee|time|timeout|top|touch|tr|traceroute|tsort|tty|umount|uname|unexpand|uniq|units|unrar|unshar|unzip|update-grub|uptime|useradd|userdel|usermod|users|uudecode|uuencode|v|vcpkg|vdir|vi|vim|virsh|vmstat|wait|watch|wc|wget|whereis|which|who|whoami|write|xargs|xdg-open|yarn|yes|zenity|zip|zsh|zypper)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    keyword: {
      pattern: /(^|[\s;|&]|[<>]\()(?:case|do|done|elif|else|esac|fi|for|function|if|in|select|then|until|while)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    // https://www.gnu.org/software/bash/manual/html_node/Shell-Builtin-Commands.html
    builtin: {
      pattern: /(^|[\s;|&]|[<>]\()(?:\.|:|alias|bind|break|builtin|caller|cd|command|continue|declare|echo|enable|eval|exec|exit|export|getopts|hash|help|let|local|logout|mapfile|printf|pwd|read|readarray|readonly|return|set|shift|shopt|source|test|times|trap|type|typeset|ulimit|umask|unalias|unset)(?=$|[)\s;|&])/,
      lookbehind: !0,
      // Alias added to make those easier to distinguish from strings.
      alias: "class-name"
    },
    boolean: {
      pattern: /(^|[\s;|&]|[<>]\()(?:false|true)(?=$|[)\s;|&])/,
      lookbehind: !0
    },
    "file-descriptor": {
      pattern: /\B&\d\b/,
      alias: "important"
    },
    operator: {
      // Lots of redirections here, but not just that.
      pattern: /\d?<>|>\||\+=|=[=~]?|!=?|<<[<-]?|[&\d]?>>|\d[<>]&?|[<>][&=]?|&[>&]?|\|[&|]?/,
      inside: {
        "file-descriptor": {
          pattern: /^\d/,
          alias: "important"
        }
      }
    },
    punctuation: /\$?\(\(?|\)\)?|\.\.|[{}[\];\\]/,
    number: {
      pattern: /(^|\s)(?:[1-9]\d*|0)(?:[.,]\d+)?\b/,
      lookbehind: !0
    }
  }, t.inside = r.languages.bash;
  for (var i = [
    "comment",
    "function-name",
    "for-or-select",
    "assign-left",
    "parameter",
    "string",
    "environment",
    "function",
    "keyword",
    "builtin",
    "boolean",
    "file-descriptor",
    "operator",
    "punctuation",
    "number"
  ], a = n.variable[1].inside, o = 0; o < i.length; o++)
    a[i[o]] = r.languages.bash[i[o]];
  r.languages.sh = r.languages.bash, r.languages.shell = r.languages.bash;
})(Prism);
new yt();
const ti = (r) => {
  const e = {};
  for (let t = 0, n = r.length; t < n; t++) {
    const i = r[t];
    for (const a in i)
      e[a] ? e[a] = e[a].concat(i[a]) : e[a] = i[a];
  }
  return e;
}, ni = [
  "abbr",
  "accept",
  "accept-charset",
  "accesskey",
  "action",
  "align",
  "alink",
  "allow",
  "allowfullscreen",
  "alt",
  "anchor",
  "archive",
  "as",
  "async",
  "autocapitalize",
  "autocomplete",
  "autocorrect",
  "autofocus",
  "autopictureinpicture",
  "autoplay",
  "axis",
  "background",
  "behavior",
  "bgcolor",
  "border",
  "bordercolor",
  "capture",
  "cellpadding",
  "cellspacing",
  "challenge",
  "char",
  "charoff",
  "charset",
  "checked",
  "cite",
  "class",
  "classid",
  "clear",
  "code",
  "codebase",
  "codetype",
  "color",
  "cols",
  "colspan",
  "compact",
  "content",
  "contenteditable",
  "controls",
  "controlslist",
  "conversiondestination",
  "coords",
  "crossorigin",
  "csp",
  "data",
  "datetime",
  "declare",
  "decoding",
  "default",
  "defer",
  "dir",
  "direction",
  "dirname",
  "disabled",
  "disablepictureinpicture",
  "disableremoteplayback",
  "disallowdocumentaccess",
  "download",
  "draggable",
  "elementtiming",
  "enctype",
  "end",
  "enterkeyhint",
  "event",
  "exportparts",
  "face",
  "for",
  "form",
  "formaction",
  "formenctype",
  "formmethod",
  "formnovalidate",
  "formtarget",
  "frame",
  "frameborder",
  "headers",
  "height",
  "hidden",
  "high",
  "href",
  "hreflang",
  "hreftranslate",
  "hspace",
  "http-equiv",
  "id",
  "imagesizes",
  "imagesrcset",
  "importance",
  "impressiondata",
  "impressionexpiry",
  "incremental",
  "inert",
  "inputmode",
  "integrity",
  "invisible",
  "ismap",
  "keytype",
  "kind",
  "label",
  "lang",
  "language",
  "latencyhint",
  "leftmargin",
  "link",
  "list",
  "loading",
  "longdesc",
  "loop",
  "low",
  "lowsrc",
  "manifest",
  "marginheight",
  "marginwidth",
  "max",
  "maxlength",
  "mayscript",
  "media",
  "method",
  "min",
  "minlength",
  "multiple",
  "muted",
  "name",
  "nohref",
  "nomodule",
  "nonce",
  "noresize",
  "noshade",
  "novalidate",
  "nowrap",
  "object",
  "open",
  "optimum",
  "part",
  "pattern",
  "ping",
  "placeholder",
  "playsinline",
  "policy",
  "poster",
  "preload",
  "pseudo",
  "readonly",
  "referrerpolicy",
  "rel",
  "reportingorigin",
  "required",
  "resources",
  "rev",
  "reversed",
  "role",
  "rows",
  "rowspan",
  "rules",
  "sandbox",
  "scheme",
  "scope",
  "scopes",
  "scrollamount",
  "scrolldelay",
  "scrolling",
  "select",
  "selected",
  "shadowroot",
  "shadowrootdelegatesfocus",
  "shape",
  "size",
  "sizes",
  "slot",
  "span",
  "spellcheck",
  "src",
  "srclang",
  "srcset",
  "standby",
  "start",
  "step",
  "style",
  "summary",
  "tabindex",
  "target",
  "text",
  "title",
  "topmargin",
  "translate",
  "truespeed",
  "trusttoken",
  "type",
  "usemap",
  "valign",
  "value",
  "valuetype",
  "version",
  "virtualkeyboardpolicy",
  "vlink",
  "vspace",
  "webkitdirectory",
  "width",
  "wrap"
], ii = [
  "accent-height",
  "accumulate",
  "additive",
  "alignment-baseline",
  "ascent",
  "attributename",
  "attributetype",
  "azimuth",
  "basefrequency",
  "baseline-shift",
  "begin",
  "bias",
  "by",
  "class",
  "clip",
  "clippathunits",
  "clip-path",
  "clip-rule",
  "color",
  "color-interpolation",
  "color-interpolation-filters",
  "color-profile",
  "color-rendering",
  "cx",
  "cy",
  "d",
  "dx",
  "dy",
  "diffuseconstant",
  "direction",
  "display",
  "divisor",
  "dominant-baseline",
  "dur",
  "edgemode",
  "elevation",
  "end",
  "fill",
  "fill-opacity",
  "fill-rule",
  "filter",
  "filterunits",
  "flood-color",
  "flood-opacity",
  "font-family",
  "font-size",
  "font-size-adjust",
  "font-stretch",
  "font-style",
  "font-variant",
  "font-weight",
  "fx",
  "fy",
  "g1",
  "g2",
  "glyph-name",
  "glyphref",
  "gradientunits",
  "gradienttransform",
  "height",
  "href",
  "id",
  "image-rendering",
  "in",
  "in2",
  "k",
  "k1",
  "k2",
  "k3",
  "k4",
  "kerning",
  "keypoints",
  "keysplines",
  "keytimes",
  "lang",
  "lengthadjust",
  "letter-spacing",
  "kernelmatrix",
  "kernelunitlength",
  "lighting-color",
  "local",
  "marker-end",
  "marker-mid",
  "marker-start",
  "markerheight",
  "markerunits",
  "markerwidth",
  "maskcontentunits",
  "maskunits",
  "max",
  "mask",
  "media",
  "method",
  "mode",
  "min",
  "name",
  "numoctaves",
  "offset",
  "operator",
  "opacity",
  "order",
  "orient",
  "orientation",
  "origin",
  "overflow",
  "paint-order",
  "path",
  "pathlength",
  "patterncontentunits",
  "patterntransform",
  "patternunits",
  "points",
  "preservealpha",
  "preserveaspectratio",
  "primitiveunits",
  "r",
  "rx",
  "ry",
  "radius",
  "refx",
  "refy",
  "repeatcount",
  "repeatdur",
  "restart",
  "result",
  "rotate",
  "scale",
  "seed",
  "shape-rendering",
  "specularconstant",
  "specularexponent",
  "spreadmethod",
  "startoffset",
  "stddeviation",
  "stitchtiles",
  "stop-color",
  "stop-opacity",
  "stroke-dasharray",
  "stroke-dashoffset",
  "stroke-linecap",
  "stroke-linejoin",
  "stroke-miterlimit",
  "stroke-opacity",
  "stroke",
  "stroke-width",
  "style",
  "surfacescale",
  "systemlanguage",
  "tabindex",
  "targetx",
  "targety",
  "transform",
  "transform-origin",
  "text-anchor",
  "text-decoration",
  "text-rendering",
  "textlength",
  "type",
  "u1",
  "u2",
  "unicode",
  "values",
  "viewbox",
  "visibility",
  "version",
  "vert-adv-y",
  "vert-origin-x",
  "vert-origin-y",
  "width",
  "word-spacing",
  "wrap",
  "writing-mode",
  "xchannelselector",
  "ychannelselector",
  "x",
  "x1",
  "x2",
  "xmlns",
  "y",
  "y1",
  "y2",
  "z",
  "zoomandpan"
], ai = [
  "accent",
  "accentunder",
  "align",
  "bevelled",
  "close",
  "columnsalign",
  "columnlines",
  "columnspan",
  "denomalign",
  "depth",
  "dir",
  "display",
  "displaystyle",
  "encoding",
  "fence",
  "frame",
  "height",
  "href",
  "id",
  "largeop",
  "length",
  "linethickness",
  "lspace",
  "lquote",
  "mathbackground",
  "mathcolor",
  "mathsize",
  "mathvariant",
  "maxsize",
  "minsize",
  "movablelimits",
  "notation",
  "numalign",
  "open",
  "rowalign",
  "rowlines",
  "rowspacing",
  "rowspan",
  "rspace",
  "rquote",
  "scriptlevel",
  "scriptminsize",
  "scriptsizemultiplier",
  "selection",
  "separator",
  "separators",
  "stretchy",
  "subscriptshift",
  "supscriptshift",
  "symmetric",
  "voffset",
  "width",
  "xmlns"
];
ti([
  Object.fromEntries(ni.map((r) => [r, ["*"]])),
  Object.fromEntries(ii.map((r) => [r, ["svg:*"]])),
  Object.fromEntries(ai.map((r) => [r, ["math:*"]]))
]);
const {
  HtmlTagHydration: ao,
  SvelteComponent: oo,
  attr: ro,
  binding_callbacks: lo,
  children: so,
  claim_element: uo,
  claim_html_tag: co,
  detach: _o,
  element: po,
  init: ho,
  insert_hydration: mo,
  noop: fo,
  safe_not_equal: go,
  toggle_class: $o
} = window.__gradio__svelte__internal, { afterUpdate: Do, tick: vo, onMount: yo } = window.__gradio__svelte__internal, {
  SvelteComponent: Fo,
  attr: bo,
  children: wo,
  claim_component: ko,
  claim_element: Co,
  create_component: Eo,
  destroy_component: Ao,
  detach: So,
  element: xo,
  init: Bo,
  insert_hydration: qo,
  mount_component: To,
  safe_not_equal: Ro,
  transition_in: zo,
  transition_out: Io
} = window.__gradio__svelte__internal, {
  SvelteComponent: Oo,
  attr: Lo,
  check_outros: Po,
  children: No,
  claim_component: Mo,
  claim_element: jo,
  claim_space: Ho,
  create_component: Uo,
  create_slot: Go,
  destroy_component: Zo,
  detach: Xo,
  element: Wo,
  empty: Yo,
  get_all_dirty_from_scope: Ko,
  get_slot_changes: Qo,
  group_outros: Vo,
  init: Jo,
  insert_hydration: er,
  mount_component: tr,
  safe_not_equal: nr,
  space: ir,
  toggle_class: ar,
  transition_in: or,
  transition_out: rr,
  update_slot_base: lr
} = window.__gradio__svelte__internal, {
  SvelteComponent: sr,
  append_hydration: ur,
  attr: cr,
  children: _r,
  claim_component: dr,
  claim_element: pr,
  claim_space: hr,
  claim_text: mr,
  create_component: fr,
  destroy_component: gr,
  detach: $r,
  element: Dr,
  init: vr,
  insert_hydration: yr,
  mount_component: Fr,
  safe_not_equal: br,
  set_data: wr,
  space: kr,
  text: Cr,
  toggle_class: Er,
  transition_in: Ar,
  transition_out: Sr
} = window.__gradio__svelte__internal, {
  SvelteComponent: xr,
  append_hydration: Br,
  attr: qr,
  bubble: Tr,
  check_outros: Rr,
  children: zr,
  claim_component: Ir,
  claim_element: Or,
  claim_space: Lr,
  claim_text: Pr,
  construct_svelte_component: Nr,
  create_component: Mr,
  create_slot: jr,
  destroy_component: Hr,
  detach: Ur,
  element: Gr,
  get_all_dirty_from_scope: Zr,
  get_slot_changes: Xr,
  group_outros: Wr,
  init: Yr,
  insert_hydration: Kr,
  listen: Qr,
  mount_component: Vr,
  safe_not_equal: Jr,
  set_data: el,
  set_style: tl,
  space: nl,
  text: il,
  toggle_class: al,
  transition_in: ol,
  transition_out: rl,
  update_slot_base: ll
} = window.__gradio__svelte__internal, {
  SvelteComponent: sl,
  append_hydration: ul,
  attr: cl,
  binding_callbacks: _l,
  children: dl,
  claim_element: pl,
  create_slot: hl,
  detach: ml,
  element: fl,
  get_all_dirty_from_scope: gl,
  get_slot_changes: $l,
  init: Dl,
  insert_hydration: vl,
  safe_not_equal: yl,
  toggle_class: Fl,
  transition_in: bl,
  transition_out: wl,
  update_slot_base: kl
} = window.__gradio__svelte__internal, {
  SvelteComponent: Cl,
  append_hydration: El,
  attr: Al,
  children: Sl,
  claim_svg_element: xl,
  detach: Bl,
  init: ql,
  insert_hydration: Tl,
  noop: Rl,
  safe_not_equal: zl,
  svg_element: Il
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ol,
  append_hydration: Ll,
  attr: Pl,
  children: Nl,
  claim_svg_element: Ml,
  detach: jl,
  init: Hl,
  insert_hydration: Ul,
  noop: Gl,
  safe_not_equal: Zl,
  svg_element: Xl
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wl,
  append_hydration: Yl,
  attr: Kl,
  children: Ql,
  claim_svg_element: Vl,
  detach: Jl,
  init: es,
  insert_hydration: ts,
  noop: ns,
  safe_not_equal: is,
  svg_element: as
} = window.__gradio__svelte__internal, {
  SvelteComponent: os,
  append_hydration: rs,
  attr: ls,
  children: ss,
  claim_svg_element: us,
  detach: cs,
  init: _s,
  insert_hydration: ds,
  noop: ps,
  safe_not_equal: hs,
  svg_element: ms
} = window.__gradio__svelte__internal, {
  SvelteComponent: fs,
  append_hydration: gs,
  attr: $s,
  children: Ds,
  claim_svg_element: vs,
  detach: ys,
  init: Fs,
  insert_hydration: bs,
  noop: ws,
  safe_not_equal: ks,
  svg_element: Cs
} = window.__gradio__svelte__internal, {
  SvelteComponent: Es,
  append_hydration: As,
  attr: Ss,
  children: xs,
  claim_svg_element: Bs,
  detach: qs,
  init: Ts,
  insert_hydration: Rs,
  noop: zs,
  safe_not_equal: Is,
  svg_element: Os
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ls,
  append_hydration: Ps,
  attr: Ns,
  children: Ms,
  claim_svg_element: js,
  detach: Hs,
  init: Us,
  insert_hydration: Gs,
  noop: Zs,
  safe_not_equal: Xs,
  svg_element: Ws
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ys,
  append_hydration: Ks,
  attr: Qs,
  children: Vs,
  claim_svg_element: Js,
  detach: eu,
  init: tu,
  insert_hydration: nu,
  noop: iu,
  safe_not_equal: au,
  svg_element: ou
} = window.__gradio__svelte__internal, {
  SvelteComponent: ru,
  append_hydration: lu,
  attr: su,
  children: uu,
  claim_svg_element: cu,
  detach: _u,
  init: du,
  insert_hydration: pu,
  noop: hu,
  safe_not_equal: mu,
  svg_element: fu
} = window.__gradio__svelte__internal, {
  SvelteComponent: gu,
  append_hydration: $u,
  attr: Du,
  children: vu,
  claim_svg_element: yu,
  detach: Fu,
  init: bu,
  insert_hydration: wu,
  noop: ku,
  safe_not_equal: Cu,
  svg_element: Eu
} = window.__gradio__svelte__internal, {
  SvelteComponent: Au,
  append_hydration: Su,
  attr: xu,
  children: Bu,
  claim_svg_element: qu,
  detach: Tu,
  init: Ru,
  insert_hydration: zu,
  noop: Iu,
  safe_not_equal: Ou,
  svg_element: Lu
} = window.__gradio__svelte__internal, {
  SvelteComponent: Pu,
  append_hydration: Nu,
  attr: Mu,
  children: ju,
  claim_svg_element: Hu,
  detach: Uu,
  init: Gu,
  insert_hydration: Zu,
  noop: Xu,
  safe_not_equal: Wu,
  svg_element: Yu
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ku,
  append_hydration: Qu,
  attr: Vu,
  children: Ju,
  claim_svg_element: ec,
  detach: tc,
  init: nc,
  insert_hydration: ic,
  noop: ac,
  safe_not_equal: oc,
  set_style: rc,
  svg_element: lc
} = window.__gradio__svelte__internal, {
  SvelteComponent: sc,
  append_hydration: uc,
  attr: cc,
  children: _c,
  claim_svg_element: dc,
  detach: pc,
  init: hc,
  insert_hydration: mc,
  noop: fc,
  safe_not_equal: gc,
  svg_element: $c
} = window.__gradio__svelte__internal, {
  SvelteComponent: Dc,
  append_hydration: vc,
  attr: yc,
  children: Fc,
  claim_svg_element: bc,
  detach: wc,
  init: kc,
  insert_hydration: Cc,
  noop: Ec,
  safe_not_equal: Ac,
  svg_element: Sc
} = window.__gradio__svelte__internal, {
  SvelteComponent: xc,
  append_hydration: Bc,
  attr: qc,
  children: Tc,
  claim_svg_element: Rc,
  detach: zc,
  init: Ic,
  insert_hydration: Oc,
  noop: Lc,
  safe_not_equal: Pc,
  svg_element: Nc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Mc,
  append_hydration: jc,
  attr: Hc,
  children: Uc,
  claim_svg_element: Gc,
  detach: Zc,
  init: Xc,
  insert_hydration: Wc,
  noop: Yc,
  safe_not_equal: Kc,
  svg_element: Qc
} = window.__gradio__svelte__internal, {
  SvelteComponent: Vc,
  append_hydration: Jc,
  attr: e_,
  children: t_,
  claim_svg_element: n_,
  detach: i_,
  init: a_,
  insert_hydration: o_,
  noop: r_,
  safe_not_equal: l_,
  svg_element: s_
} = window.__gradio__svelte__internal, {
  SvelteComponent: u_,
  append_hydration: c_,
  attr: __,
  children: d_,
  claim_svg_element: p_,
  detach: h_,
  init: m_,
  insert_hydration: f_,
  noop: g_,
  safe_not_equal: $_,
  svg_element: D_
} = window.__gradio__svelte__internal, {
  SvelteComponent: v_,
  append_hydration: y_,
  attr: F_,
  children: b_,
  claim_svg_element: w_,
  detach: k_,
  init: C_,
  insert_hydration: E_,
  noop: A_,
  safe_not_equal: S_,
  svg_element: x_
} = window.__gradio__svelte__internal, {
  SvelteComponent: B_,
  append_hydration: q_,
  attr: T_,
  children: R_,
  claim_svg_element: z_,
  detach: I_,
  init: O_,
  insert_hydration: L_,
  noop: P_,
  safe_not_equal: N_,
  svg_element: M_
} = window.__gradio__svelte__internal, {
  SvelteComponent: j_,
  append_hydration: H_,
  attr: U_,
  children: G_,
  claim_svg_element: Z_,
  detach: X_,
  init: W_,
  insert_hydration: Y_,
  noop: K_,
  safe_not_equal: Q_,
  svg_element: V_
} = window.__gradio__svelte__internal, {
  SvelteComponent: J_,
  append_hydration: ed,
  attr: td,
  children: nd,
  claim_svg_element: id,
  detach: ad,
  init: od,
  insert_hydration: rd,
  noop: ld,
  safe_not_equal: sd,
  svg_element: ud
} = window.__gradio__svelte__internal, {
  SvelteComponent: cd,
  append_hydration: _d,
  attr: dd,
  children: pd,
  claim_svg_element: hd,
  detach: md,
  init: fd,
  insert_hydration: gd,
  noop: $d,
  safe_not_equal: Dd,
  svg_element: vd
} = window.__gradio__svelte__internal, {
  SvelteComponent: yd,
  append_hydration: Fd,
  attr: bd,
  children: wd,
  claim_svg_element: kd,
  detach: Cd,
  init: Ed,
  insert_hydration: Ad,
  noop: Sd,
  safe_not_equal: xd,
  svg_element: Bd
} = window.__gradio__svelte__internal, {
  SvelteComponent: qd,
  append_hydration: Td,
  attr: Rd,
  children: zd,
  claim_svg_element: Id,
  detach: Od,
  init: Ld,
  insert_hydration: Pd,
  noop: Nd,
  safe_not_equal: Md,
  svg_element: jd
} = window.__gradio__svelte__internal, {
  SvelteComponent: Hd,
  append_hydration: Ud,
  attr: Gd,
  children: Zd,
  claim_svg_element: Xd,
  detach: Wd,
  init: Yd,
  insert_hydration: Kd,
  noop: Qd,
  safe_not_equal: Vd,
  svg_element: Jd
} = window.__gradio__svelte__internal, {
  SvelteComponent: ep,
  append_hydration: tp,
  attr: np,
  children: ip,
  claim_svg_element: ap,
  detach: op,
  init: rp,
  insert_hydration: lp,
  noop: sp,
  safe_not_equal: up,
  svg_element: cp
} = window.__gradio__svelte__internal, {
  SvelteComponent: _p,
  append_hydration: dp,
  attr: pp,
  children: hp,
  claim_svg_element: mp,
  detach: fp,
  init: gp,
  insert_hydration: $p,
  noop: Dp,
  safe_not_equal: vp,
  svg_element: yp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Fp,
  append_hydration: bp,
  attr: wp,
  children: kp,
  claim_svg_element: Cp,
  detach: Ep,
  init: Ap,
  insert_hydration: Sp,
  noop: xp,
  safe_not_equal: Bp,
  svg_element: qp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Tp,
  append_hydration: Rp,
  attr: zp,
  children: Ip,
  claim_svg_element: Op,
  detach: Lp,
  init: Pp,
  insert_hydration: Np,
  noop: Mp,
  safe_not_equal: jp,
  svg_element: Hp
} = window.__gradio__svelte__internal, {
  SvelteComponent: Up,
  append_hydration: Gp,
  attr: Zp,
  children: Xp,
  claim_svg_element: Wp,
  detach: Yp,
  init: Kp,
  insert_hydration: Qp,
  noop: Vp,
  safe_not_equal: Jp,
  svg_element: eh
} = window.__gradio__svelte__internal, {
  SvelteComponent: th,
  append_hydration: nh,
  attr: ih,
  children: ah,
  claim_svg_element: oh,
  detach: rh,
  init: lh,
  insert_hydration: sh,
  noop: uh,
  safe_not_equal: ch,
  svg_element: _h
} = window.__gradio__svelte__internal, {
  SvelteComponent: dh,
  append_hydration: ph,
  attr: hh,
  children: mh,
  claim_svg_element: fh,
  detach: gh,
  init: $h,
  insert_hydration: Dh,
  noop: vh,
  safe_not_equal: yh,
  svg_element: Fh
} = window.__gradio__svelte__internal, {
  SvelteComponent: bh,
  append_hydration: wh,
  attr: kh,
  children: Ch,
  claim_svg_element: Eh,
  detach: Ah,
  init: Sh,
  insert_hydration: xh,
  noop: Bh,
  safe_not_equal: qh,
  svg_element: Th
} = window.__gradio__svelte__internal, {
  SvelteComponent: Rh,
  append_hydration: zh,
  attr: Ih,
  children: Oh,
  claim_svg_element: Lh,
  detach: Ph,
  init: Nh,
  insert_hydration: Mh,
  noop: jh,
  safe_not_equal: Hh,
  svg_element: Uh
} = window.__gradio__svelte__internal, {
  SvelteComponent: Gh,
  append_hydration: Zh,
  attr: Xh,
  children: Wh,
  claim_svg_element: Yh,
  detach: Kh,
  init: Qh,
  insert_hydration: Vh,
  noop: Jh,
  safe_not_equal: em,
  svg_element: tm
} = window.__gradio__svelte__internal, {
  SvelteComponent: nm,
  append_hydration: im,
  attr: am,
  children: om,
  claim_svg_element: rm,
  detach: lm,
  init: sm,
  insert_hydration: um,
  noop: cm,
  safe_not_equal: _m,
  svg_element: dm
} = window.__gradio__svelte__internal, {
  SvelteComponent: pm,
  append_hydration: hm,
  attr: mm,
  children: fm,
  claim_svg_element: gm,
  detach: $m,
  init: Dm,
  insert_hydration: vm,
  noop: ym,
  safe_not_equal: Fm,
  svg_element: bm
} = window.__gradio__svelte__internal, {
  SvelteComponent: wm,
  append_hydration: km,
  attr: Cm,
  children: Em,
  claim_svg_element: Am,
  detach: Sm,
  init: xm,
  insert_hydration: Bm,
  noop: qm,
  safe_not_equal: Tm,
  svg_element: Rm
} = window.__gradio__svelte__internal, {
  SvelteComponent: zm,
  append_hydration: Im,
  attr: Om,
  children: Lm,
  claim_svg_element: Pm,
  detach: Nm,
  init: Mm,
  insert_hydration: jm,
  noop: Hm,
  safe_not_equal: Um,
  svg_element: Gm
} = window.__gradio__svelte__internal, {
  SvelteComponent: Zm,
  append_hydration: Xm,
  attr: Wm,
  children: Ym,
  claim_svg_element: Km,
  detach: Qm,
  init: Vm,
  insert_hydration: Jm,
  noop: ef,
  safe_not_equal: tf,
  svg_element: nf
} = window.__gradio__svelte__internal, {
  SvelteComponent: af,
  append_hydration: of,
  attr: rf,
  children: lf,
  claim_svg_element: sf,
  detach: uf,
  init: cf,
  insert_hydration: _f,
  noop: df,
  safe_not_equal: pf,
  svg_element: hf
} = window.__gradio__svelte__internal, {
  SvelteComponent: mf,
  append_hydration: ff,
  attr: gf,
  children: $f,
  claim_svg_element: Df,
  detach: vf,
  init: yf,
  insert_hydration: Ff,
  noop: bf,
  safe_not_equal: wf,
  svg_element: kf
} = window.__gradio__svelte__internal, {
  SvelteComponent: Cf,
  append_hydration: Ef,
  attr: Af,
  children: Sf,
  claim_svg_element: xf,
  detach: Bf,
  init: qf,
  insert_hydration: Tf,
  noop: Rf,
  safe_not_equal: zf,
  svg_element: If
} = window.__gradio__svelte__internal, {
  SvelteComponent: Of,
  append_hydration: Lf,
  attr: Pf,
  children: Nf,
  claim_svg_element: Mf,
  detach: jf,
  init: Hf,
  insert_hydration: Uf,
  noop: Gf,
  safe_not_equal: Zf,
  svg_element: Xf
} = window.__gradio__svelte__internal, {
  SvelteComponent: Wf,
  append_hydration: Yf,
  attr: Kf,
  children: Qf,
  claim_svg_element: Vf,
  detach: Jf,
  init: eg,
  insert_hydration: tg,
  noop: ng,
  safe_not_equal: ig,
  svg_element: ag
} = window.__gradio__svelte__internal, {
  SvelteComponent: og,
  append_hydration: rg,
  attr: lg,
  children: sg,
  claim_svg_element: ug,
  detach: cg,
  init: _g,
  insert_hydration: dg,
  noop: pg,
  safe_not_equal: hg,
  set_style: mg,
  svg_element: fg
} = window.__gradio__svelte__internal, {
  SvelteComponent: gg,
  append_hydration: $g,
  attr: Dg,
  children: vg,
  claim_svg_element: yg,
  detach: Fg,
  init: bg,
  insert_hydration: wg,
  noop: kg,
  safe_not_equal: Cg,
  svg_element: Eg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ag,
  append_hydration: Sg,
  attr: xg,
  children: Bg,
  claim_svg_element: qg,
  detach: Tg,
  init: Rg,
  insert_hydration: zg,
  noop: Ig,
  safe_not_equal: Og,
  svg_element: Lg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Pg,
  append_hydration: Ng,
  attr: Mg,
  children: jg,
  claim_svg_element: Hg,
  detach: Ug,
  init: Gg,
  insert_hydration: Zg,
  noop: Xg,
  safe_not_equal: Wg,
  svg_element: Yg
} = window.__gradio__svelte__internal, {
  SvelteComponent: Kg,
  append_hydration: Qg,
  attr: Vg,
  children: Jg,
  claim_svg_element: e0,
  detach: t0,
  init: n0,
  insert_hydration: i0,
  noop: a0,
  safe_not_equal: o0,
  svg_element: r0
} = window.__gradio__svelte__internal, {
  SvelteComponent: l0,
  append_hydration: s0,
  attr: u0,
  children: c0,
  claim_svg_element: _0,
  detach: d0,
  init: p0,
  insert_hydration: h0,
  noop: m0,
  safe_not_equal: f0,
  svg_element: g0
} = window.__gradio__svelte__internal, {
  SvelteComponent: $0,
  append_hydration: D0,
  attr: v0,
  children: y0,
  claim_svg_element: F0,
  detach: b0,
  init: w0,
  insert_hydration: k0,
  noop: C0,
  safe_not_equal: E0,
  svg_element: A0
} = window.__gradio__svelte__internal, {
  SvelteComponent: S0,
  append_hydration: x0,
  attr: B0,
  children: q0,
  claim_svg_element: T0,
  detach: R0,
  init: z0,
  insert_hydration: I0,
  noop: O0,
  safe_not_equal: L0,
  svg_element: P0
} = window.__gradio__svelte__internal, {
  SvelteComponent: N0,
  append_hydration: M0,
  attr: j0,
  children: H0,
  claim_svg_element: U0,
  detach: G0,
  init: Z0,
  insert_hydration: X0,
  noop: W0,
  safe_not_equal: Y0,
  svg_element: K0
} = window.__gradio__svelte__internal, {
  SvelteComponent: Q0,
  append_hydration: V0,
  attr: J0,
  children: e$,
  claim_svg_element: t$,
  claim_text: n$,
  detach: i$,
  init: a$,
  insert_hydration: o$,
  noop: r$,
  safe_not_equal: l$,
  svg_element: s$,
  text: u$
} = window.__gradio__svelte__internal, {
  SvelteComponent: c$,
  append_hydration: _$,
  attr: d$,
  children: p$,
  claim_svg_element: h$,
  detach: m$,
  init: f$,
  insert_hydration: g$,
  noop: $$,
  safe_not_equal: D$,
  svg_element: v$
} = window.__gradio__svelte__internal, {
  SvelteComponent: y$,
  append_hydration: F$,
  attr: b$,
  children: w$,
  claim_svg_element: k$,
  detach: C$,
  init: E$,
  insert_hydration: A$,
  noop: S$,
  safe_not_equal: x$,
  svg_element: B$
} = window.__gradio__svelte__internal, {
  SvelteComponent: q$,
  append_hydration: T$,
  attr: R$,
  children: z$,
  claim_svg_element: I$,
  detach: O$,
  init: L$,
  insert_hydration: P$,
  noop: N$,
  safe_not_equal: M$,
  svg_element: j$
} = window.__gradio__svelte__internal, {
  SvelteComponent: H$,
  append_hydration: U$,
  attr: G$,
  children: Z$,
  claim_svg_element: X$,
  detach: W$,
  init: Y$,
  insert_hydration: K$,
  noop: Q$,
  safe_not_equal: V$,
  svg_element: J$
} = window.__gradio__svelte__internal, {
  SvelteComponent: e1,
  append_hydration: t1,
  attr: n1,
  children: i1,
  claim_svg_element: a1,
  detach: o1,
  init: r1,
  insert_hydration: l1,
  noop: s1,
  safe_not_equal: u1,
  svg_element: c1
} = window.__gradio__svelte__internal, {
  SvelteComponent: _1,
  append_hydration: d1,
  attr: p1,
  children: h1,
  claim_svg_element: m1,
  detach: f1,
  init: g1,
  insert_hydration: $1,
  noop: D1,
  safe_not_equal: v1,
  svg_element: y1
} = window.__gradio__svelte__internal, {
  SvelteComponent: F1,
  append_hydration: b1,
  attr: w1,
  children: k1,
  claim_svg_element: C1,
  detach: E1,
  init: A1,
  insert_hydration: S1,
  noop: x1,
  safe_not_equal: B1,
  svg_element: q1
} = window.__gradio__svelte__internal, {
  SvelteComponent: T1,
  append_hydration: R1,
  attr: z1,
  children: I1,
  claim_svg_element: O1,
  claim_text: L1,
  detach: P1,
  init: N1,
  insert_hydration: M1,
  noop: j1,
  safe_not_equal: H1,
  svg_element: U1,
  text: G1
} = window.__gradio__svelte__internal, {
  SvelteComponent: Z1,
  append_hydration: X1,
  attr: W1,
  children: Y1,
  claim_svg_element: K1,
  claim_text: Q1,
  detach: V1,
  init: J1,
  insert_hydration: eD,
  noop: tD,
  safe_not_equal: nD,
  svg_element: iD,
  text: aD
} = window.__gradio__svelte__internal, {
  SvelteComponent: oD,
  append_hydration: rD,
  attr: lD,
  children: sD,
  claim_svg_element: uD,
  claim_text: cD,
  detach: _D,
  init: dD,
  insert_hydration: pD,
  noop: hD,
  safe_not_equal: mD,
  svg_element: fD,
  text: gD
} = window.__gradio__svelte__internal, {
  SvelteComponent: $D,
  append_hydration: DD,
  attr: vD,
  children: yD,
  claim_svg_element: FD,
  detach: bD,
  init: wD,
  insert_hydration: kD,
  noop: CD,
  safe_not_equal: ED,
  svg_element: AD
} = window.__gradio__svelte__internal, {
  SvelteComponent: SD,
  append_hydration: xD,
  attr: BD,
  children: qD,
  claim_svg_element: TD,
  detach: RD,
  init: zD,
  insert_hydration: ID,
  noop: OD,
  safe_not_equal: LD,
  svg_element: PD
} = window.__gradio__svelte__internal, {
  SvelteComponent: ND,
  append_hydration: MD,
  attr: jD,
  children: HD,
  claim_svg_element: UD,
  detach: GD,
  init: ZD,
  insert_hydration: XD,
  noop: WD,
  safe_not_equal: YD,
  svg_element: KD
} = window.__gradio__svelte__internal, {
  SvelteComponent: QD,
  append_hydration: VD,
  attr: JD,
  children: ev,
  claim_svg_element: tv,
  detach: nv,
  init: iv,
  insert_hydration: av,
  noop: ov,
  safe_not_equal: rv,
  svg_element: lv
} = window.__gradio__svelte__internal, {
  SvelteComponent: sv,
  append_hydration: uv,
  attr: cv,
  children: _v,
  claim_svg_element: dv,
  detach: pv,
  init: hv,
  insert_hydration: mv,
  noop: fv,
  safe_not_equal: gv,
  svg_element: $v
} = window.__gradio__svelte__internal, {
  SvelteComponent: Dv,
  append_hydration: vv,
  attr: yv,
  children: Fv,
  claim_svg_element: bv,
  detach: wv,
  init: kv,
  insert_hydration: Cv,
  noop: Ev,
  safe_not_equal: Av,
  svg_element: Sv
} = window.__gradio__svelte__internal, {
  SvelteComponent: xv,
  append_hydration: Bv,
  attr: qv,
  children: Tv,
  claim_svg_element: Rv,
  detach: zv,
  init: Iv,
  insert_hydration: Ov,
  noop: Lv,
  safe_not_equal: Pv,
  svg_element: Nv
} = window.__gradio__svelte__internal, {
  SvelteComponent: Mv,
  append_hydration: jv,
  attr: Hv,
  children: Uv,
  claim_svg_element: Gv,
  detach: Zv,
  init: Xv,
  insert_hydration: Wv,
  noop: Yv,
  safe_not_equal: Kv,
  svg_element: Qv
} = window.__gradio__svelte__internal, {
  SvelteComponent: Vv,
  claim_component: Jv,
  create_component: ey,
  destroy_component: ty,
  init: ny,
  mount_component: iy,
  safe_not_equal: ay,
  transition_in: oy,
  transition_out: ry
} = window.__gradio__svelte__internal, { createEventDispatcher: ly } = window.__gradio__svelte__internal, {
  SvelteComponent: sy,
  append_hydration: uy,
  attr: cy,
  check_outros: _y,
  children: dy,
  claim_component: py,
  claim_element: hy,
  claim_space: my,
  claim_text: fy,
  create_component: gy,
  destroy_component: $y,
  detach: Dy,
  element: vy,
  empty: yy,
  group_outros: Fy,
  init: by,
  insert_hydration: wy,
  mount_component: ky,
  safe_not_equal: Cy,
  set_data: Ey,
  space: Ay,
  text: Sy,
  toggle_class: xy,
  transition_in: By,
  transition_out: qy
} = window.__gradio__svelte__internal, {
  SvelteComponent: Ty,
  attr: Ry,
  children: zy,
  claim_element: Iy,
  create_slot: Oy,
  detach: Ly,
  element: Py,
  get_all_dirty_from_scope: Ny,
  get_slot_changes: My,
  init: jy,
  insert_hydration: Hy,
  safe_not_equal: Uy,
  toggle_class: Gy,
  transition_in: Zy,
  transition_out: Xy,
  update_slot_base: Wy
} = window.__gradio__svelte__internal, {
  SvelteComponent: Yy,
  append_hydration: Ky,
  attr: Qy,
  check_outros: Vy,
  children: Jy,
  claim_component: eF,
  claim_element: tF,
  claim_space: nF,
  create_component: iF,
  destroy_component: aF,
  detach: oF,
  element: rF,
  empty: lF,
  group_outros: sF,
  init: uF,
  insert_hydration: cF,
  listen: _F,
  mount_component: dF,
  safe_not_equal: pF,
  space: hF,
  toggle_class: mF,
  transition_in: fF,
  transition_out: gF
} = window.__gradio__svelte__internal, {
  SvelteComponent: $F,
  attr: DF,
  children: vF,
  claim_element: yF,
  create_slot: FF,
  detach: bF,
  element: wF,
  get_all_dirty_from_scope: kF,
  get_slot_changes: CF,
  init: EF,
  insert_hydration: AF,
  null_to_empty: SF,
  safe_not_equal: xF,
  transition_in: BF,
  transition_out: qF,
  update_slot_base: TF
} = window.__gradio__svelte__internal, {
  SvelteComponent: RF,
  check_outros: zF,
  claim_component: IF,
  create_component: OF,
  destroy_component: LF,
  detach: PF,
  empty: NF,
  group_outros: MF,
  init: jF,
  insert_hydration: HF,
  mount_component: UF,
  noop: GF,
  safe_not_equal: ZF,
  transition_in: XF,
  transition_out: WF
} = window.__gradio__svelte__internal, { createEventDispatcher: YF } = window.__gradio__svelte__internal, {
  SvelteComponent: KF,
  append_hydration: QF,
  attr: VF,
  binding_callbacks: JF,
  bubble: eb,
  check_outros: tb,
  children: nb,
  claim_component: ib,
  claim_element: ab,
  claim_space: ob,
  create_component: rb,
  destroy_component: lb,
  detach: sb,
  element: ub,
  empty: cb,
  group_outros: _b,
  init: db,
  insert_hydration: pb,
  listen: hb,
  mount_component: mb,
  safe_not_equal: fb,
  space: gb,
  toggle_class: $b,
  transition_in: Db,
  transition_out: vb
} = window.__gradio__svelte__internal, { createEventDispatcher: yb, onMount: Fb } = window.__gradio__svelte__internal, {
  SvelteComponent: oi,
  append_hydration: Ft,
  attr: Z,
  bubble: ri,
  check_outros: Pe,
  children: bt,
  claim_component: wt,
  claim_element: kt,
  claim_space: Ct,
  create_component: Et,
  create_slot: At,
  destroy_component: St,
  detach: se,
  element: xt,
  empty: nt,
  get_all_dirty_from_scope: Bt,
  get_slot_changes: qt,
  group_outros: Ne,
  init: li,
  insert_hydration: Me,
  listen: si,
  mount_component: Tt,
  safe_not_equal: ui,
  set_style: G,
  space: Rt,
  toggle_class: ie,
  transition_in: W,
  transition_out: Q,
  update_slot_base: zt
} = window.__gradio__svelte__internal;
function ci(r) {
  let e, t, n, i, a, o, l = (
    /*icon*/
    r[7] && it(r)
  );
  const s = (
    /*#slots*/
    r[12].default
  ), c = At(
    s,
    r,
    /*$$scope*/
    r[11],
    null
  );
  return {
    c() {
      e = xt("button"), l && l.c(), t = Rt(), c && c.c(), this.h();
    },
    l(d) {
      e = kt(d, "BUTTON", { class: !0, id: !0 });
      var p = bt(e);
      l && l.l(p), t = Ct(p), c && c.l(p), p.forEach(se), this.h();
    },
    h() {
      Z(e, "class", n = /*size*/
      r[4] + " " + /*variant*/
      r[3] + " " + /*elem_classes*/
      r[1].join(" ") + " svelte-rvoavt"), Z(
        e,
        "id",
        /*elem_id*/
        r[0]
      ), e.disabled = /*disabled*/
      r[8], ie(e, "hidden", !/*visible*/
      r[2]), G(
        e,
        "flex-grow",
        /*scale*/
        r[9]
      ), G(
        e,
        "width",
        /*scale*/
        r[9] === 0 ? "fit-content" : null
      ), G(e, "min-width", typeof /*min_width*/
      r[10] == "number" ? `calc(min(${/*min_width*/
      r[10]}px, 100%))` : null);
    },
    m(d, p) {
      Me(d, e, p), l && l.m(e, null), Ft(e, t), c && c.m(e, null), i = !0, a || (o = si(
        e,
        "click",
        /*click_handler*/
        r[13]
      ), a = !0);
    },
    p(d, p) {
      /*icon*/
      d[7] ? l ? (l.p(d, p), p & /*icon*/
      128 && W(l, 1)) : (l = it(d), l.c(), W(l, 1), l.m(e, t)) : l && (Ne(), Q(l, 1, 1, () => {
        l = null;
      }), Pe()), c && c.p && (!i || p & /*$$scope*/
      2048) && zt(
        c,
        s,
        d,
        /*$$scope*/
        d[11],
        i ? qt(
          s,
          /*$$scope*/
          d[11],
          p,
          null
        ) : Bt(
          /*$$scope*/
          d[11]
        ),
        null
      ), (!i || p & /*size, variant, elem_classes*/
      26 && n !== (n = /*size*/
      d[4] + " " + /*variant*/
      d[3] + " " + /*elem_classes*/
      d[1].join(" ") + " svelte-rvoavt")) && Z(e, "class", n), (!i || p & /*elem_id*/
      1) && Z(
        e,
        "id",
        /*elem_id*/
        d[0]
      ), (!i || p & /*disabled*/
      256) && (e.disabled = /*disabled*/
      d[8]), (!i || p & /*size, variant, elem_classes, visible*/
      30) && ie(e, "hidden", !/*visible*/
      d[2]), p & /*scale*/
      512 && G(
        e,
        "flex-grow",
        /*scale*/
        d[9]
      ), p & /*scale*/
      512 && G(
        e,
        "width",
        /*scale*/
        d[9] === 0 ? "fit-content" : null
      ), p & /*min_width*/
      1024 && G(e, "min-width", typeof /*min_width*/
      d[10] == "number" ? `calc(min(${/*min_width*/
      d[10]}px, 100%))` : null);
    },
    i(d) {
      i || (W(l), W(c, d), i = !0);
    },
    o(d) {
      Q(l), Q(c, d), i = !1;
    },
    d(d) {
      d && se(e), l && l.d(), c && c.d(d), a = !1, o();
    }
  };
}
function _i(r) {
  let e, t, n, i, a = (
    /*icon*/
    r[7] && at(r)
  );
  const o = (
    /*#slots*/
    r[12].default
  ), l = At(
    o,
    r,
    /*$$scope*/
    r[11],
    null
  );
  return {
    c() {
      e = xt("a"), a && a.c(), t = Rt(), l && l.c(), this.h();
    },
    l(s) {
      e = kt(s, "A", {
        href: !0,
        rel: !0,
        "aria-disabled": !0,
        class: !0,
        id: !0
      });
      var c = bt(e);
      a && a.l(c), t = Ct(c), l && l.l(c), c.forEach(se), this.h();
    },
    h() {
      Z(
        e,
        "href",
        /*link*/
        r[6]
      ), Z(e, "rel", "noopener noreferrer"), Z(
        e,
        "aria-disabled",
        /*disabled*/
        r[8]
      ), Z(e, "class", n = /*size*/
      r[4] + " " + /*variant*/
      r[3] + " " + /*elem_classes*/
      r[1].join(" ") + " svelte-rvoavt"), Z(
        e,
        "id",
        /*elem_id*/
        r[0]
      ), ie(e, "hidden", !/*visible*/
      r[2]), ie(
        e,
        "disabled",
        /*disabled*/
        r[8]
      ), G(
        e,
        "flex-grow",
        /*scale*/
        r[9]
      ), G(
        e,
        "pointer-events",
        /*disabled*/
        r[8] ? "none" : null
      ), G(
        e,
        "width",
        /*scale*/
        r[9] === 0 ? "fit-content" : null
      ), G(e, "min-width", typeof /*min_width*/
      r[10] == "number" ? `calc(min(${/*min_width*/
      r[10]}px, 100%))` : null);
    },
    m(s, c) {
      Me(s, e, c), a && a.m(e, null), Ft(e, t), l && l.m(e, null), i = !0;
    },
    p(s, c) {
      /*icon*/
      s[7] ? a ? (a.p(s, c), c & /*icon*/
      128 && W(a, 1)) : (a = at(s), a.c(), W(a, 1), a.m(e, t)) : a && (Ne(), Q(a, 1, 1, () => {
        a = null;
      }), Pe()), l && l.p && (!i || c & /*$$scope*/
      2048) && zt(
        l,
        o,
        s,
        /*$$scope*/
        s[11],
        i ? qt(
          o,
          /*$$scope*/
          s[11],
          c,
          null
        ) : Bt(
          /*$$scope*/
          s[11]
        ),
        null
      ), (!i || c & /*link*/
      64) && Z(
        e,
        "href",
        /*link*/
        s[6]
      ), (!i || c & /*disabled*/
      256) && Z(
        e,
        "aria-disabled",
        /*disabled*/
        s[8]
      ), (!i || c & /*size, variant, elem_classes*/
      26 && n !== (n = /*size*/
      s[4] + " " + /*variant*/
      s[3] + " " + /*elem_classes*/
      s[1].join(" ") + " svelte-rvoavt")) && Z(e, "class", n), (!i || c & /*elem_id*/
      1) && Z(
        e,
        "id",
        /*elem_id*/
        s[0]
      ), (!i || c & /*size, variant, elem_classes, visible*/
      30) && ie(e, "hidden", !/*visible*/
      s[2]), (!i || c & /*size, variant, elem_classes, disabled*/
      282) && ie(
        e,
        "disabled",
        /*disabled*/
        s[8]
      ), c & /*scale*/
      512 && G(
        e,
        "flex-grow",
        /*scale*/
        s[9]
      ), c & /*disabled*/
      256 && G(
        e,
        "pointer-events",
        /*disabled*/
        s[8] ? "none" : null
      ), c & /*scale*/
      512 && G(
        e,
        "width",
        /*scale*/
        s[9] === 0 ? "fit-content" : null
      ), c & /*min_width*/
      1024 && G(e, "min-width", typeof /*min_width*/
      s[10] == "number" ? `calc(min(${/*min_width*/
      s[10]}px, 100%))` : null);
    },
    i(s) {
      i || (W(a), W(l, s), i = !0);
    },
    o(s) {
      Q(a), Q(l, s), i = !1;
    },
    d(s) {
      s && se(e), a && a.d(), l && l.d(s);
    }
  };
}
function it(r) {
  let e, t;
  return e = new ut({
    props: {
      class: `button-icon ${/*value*/
      r[5] ? "right-padded" : ""}`,
      src: (
        /*icon*/
        r[7].url
      ),
      alt: `${/*value*/
      r[5]} icon`
    }
  }), {
    c() {
      Et(e.$$.fragment);
    },
    l(n) {
      wt(e.$$.fragment, n);
    },
    m(n, i) {
      Tt(e, n, i), t = !0;
    },
    p(n, i) {
      const a = {};
      i & /*value*/
      32 && (a.class = `button-icon ${/*value*/
      n[5] ? "right-padded" : ""}`), i & /*icon*/
      128 && (a.src = /*icon*/
      n[7].url), i & /*value*/
      32 && (a.alt = `${/*value*/
      n[5]} icon`), e.$set(a);
    },
    i(n) {
      t || (W(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Q(e.$$.fragment, n), t = !1;
    },
    d(n) {
      St(e, n);
    }
  };
}
function at(r) {
  let e, t;
  return e = new ut({
    props: {
      class: "button-icon",
      src: (
        /*icon*/
        r[7].url
      ),
      alt: `${/*value*/
      r[5]} icon`
    }
  }), {
    c() {
      Et(e.$$.fragment);
    },
    l(n) {
      wt(e.$$.fragment, n);
    },
    m(n, i) {
      Tt(e, n, i), t = !0;
    },
    p(n, i) {
      const a = {};
      i & /*icon*/
      128 && (a.src = /*icon*/
      n[7].url), i & /*value*/
      32 && (a.alt = `${/*value*/
      n[5]} icon`), e.$set(a);
    },
    i(n) {
      t || (W(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Q(e.$$.fragment, n), t = !1;
    },
    d(n) {
      St(e, n);
    }
  };
}
function di(r) {
  let e, t, n, i;
  const a = [_i, ci], o = [];
  function l(s, c) {
    return (
      /*link*/
      s[6] && /*link*/
      s[6].length > 0 ? 0 : 1
    );
  }
  return e = l(r), t = o[e] = a[e](r), {
    c() {
      t.c(), n = nt();
    },
    l(s) {
      t.l(s), n = nt();
    },
    m(s, c) {
      o[e].m(s, c), Me(s, n, c), i = !0;
    },
    p(s, [c]) {
      let d = e;
      e = l(s), e === d ? o[e].p(s, c) : (Ne(), Q(o[d], 1, 1, () => {
        o[d] = null;
      }), Pe(), t = o[e], t ? t.p(s, c) : (t = o[e] = a[e](s), t.c()), W(t, 1), t.m(n.parentNode, n));
    },
    i(s) {
      i || (W(t), i = !0);
    },
    o(s) {
      Q(t), i = !1;
    },
    d(s) {
      s && se(n), o[e].d(s);
    }
  };
}
function pi(r, e, t) {
  let { $$slots: n = {}, $$scope: i } = e, { elem_id: a = "" } = e, { elem_classes: o = [] } = e, { visible: l = !0 } = e, { variant: s = "secondary" } = e, { size: c = "lg" } = e, { value: d = null } = e, { link: p = null } = e, { icon: m = null } = e, { disabled: b = !1 } = e, { scale: R = null } = e, { min_width: C = void 0 } = e;
  function w(y) {
    ri.call(this, r, y);
  }
  return r.$$set = (y) => {
    "elem_id" in y && t(0, a = y.elem_id), "elem_classes" in y && t(1, o = y.elem_classes), "visible" in y && t(2, l = y.visible), "variant" in y && t(3, s = y.variant), "size" in y && t(4, c = y.size), "value" in y && t(5, d = y.value), "link" in y && t(6, p = y.link), "icon" in y && t(7, m = y.icon), "disabled" in y && t(8, b = y.disabled), "scale" in y && t(9, R = y.scale), "min_width" in y && t(10, C = y.min_width), "$$scope" in y && t(11, i = y.$$scope);
  }, [
    a,
    o,
    l,
    s,
    c,
    d,
    p,
    m,
    b,
    R,
    C,
    i,
    n,
    w
  ];
}
class hi extends oi {
  constructor(e) {
    super(), li(this, e, pi, di, ui, {
      elem_id: 0,
      elem_classes: 1,
      visible: 2,
      variant: 3,
      size: 4,
      value: 5,
      link: 6,
      icon: 7,
      disabled: 8,
      scale: 9,
      min_width: 10
    });
  }
}
const {
  SvelteComponent: bb,
  claim_component: wb,
  claim_text: kb,
  create_component: Cb,
  destroy_component: Eb,
  detach: Ab,
  init: Sb,
  insert_hydration: xb,
  mount_component: Bb,
  safe_not_equal: qb,
  set_data: Tb,
  text: Rb,
  transition_in: zb,
  transition_out: Ib
} = window.__gradio__svelte__internal, {
  SvelteComponent: mi,
  attr: H,
  binding_callbacks: fi,
  claim_component: gi,
  claim_element: It,
  claim_space: Ot,
  create_component: $i,
  create_slot: Di,
  destroy_component: vi,
  detach: ye,
  element: Lt,
  get_all_dirty_from_scope: yi,
  get_slot_changes: Fi,
  init: bi,
  insert_hydration: Fe,
  listen: ot,
  mount_component: wi,
  run_all: ki,
  safe_not_equal: Ci,
  space: Pt,
  src_url_equal: rt,
  transition_in: Nt,
  transition_out: Mt,
  update_slot_base: Ei
} = window.__gradio__svelte__internal, { tick: Ai, createEventDispatcher: Si } = window.__gradio__svelte__internal;
function lt(r) {
  let e, t, n;
  return {
    c() {
      e = Lt("img"), this.h();
    },
    l(i) {
      e = It(i, "IMG", { class: !0, src: !0, alt: !0 }), this.h();
    },
    h() {
      H(e, "class", "button-icon svelte-1gxyyj1"), rt(e.src, t = /*icon*/
      r[7].url) || H(e, "src", t), H(e, "alt", n = `${/*value*/
      r[0]} icon`);
    },
    m(i, a) {
      Fe(i, e, a);
    },
    p(i, a) {
      a & /*icon*/
      128 && !rt(e.src, t = /*icon*/
      i[7].url) && H(e, "src", t), a & /*value*/
      1 && n !== (n = `${/*value*/
      i[0]} icon`) && H(e, "alt", n);
    },
    d(i) {
      i && ye(e);
    }
  };
}
function xi(r) {
  let e, t, n = (
    /*icon*/
    r[7] && lt(r)
  );
  const i = (
    /*#slots*/
    r[20].default
  ), a = Di(
    i,
    r,
    /*$$scope*/
    r[22],
    null
  );
  return {
    c() {
      n && n.c(), e = Pt(), a && a.c();
    },
    l(o) {
      n && n.l(o), e = Ot(o), a && a.l(o);
    },
    m(o, l) {
      n && n.m(o, l), Fe(o, e, l), a && a.m(o, l), t = !0;
    },
    p(o, l) {
      /*icon*/
      o[7] ? n ? n.p(o, l) : (n = lt(o), n.c(), n.m(e.parentNode, e)) : n && (n.d(1), n = null), a && a.p && (!t || l & /*$$scope*/
      4194304) && Ei(
        a,
        i,
        o,
        /*$$scope*/
        o[22],
        t ? Fi(
          i,
          /*$$scope*/
          o[22],
          l,
          null
        ) : yi(
          /*$$scope*/
          o[22]
        ),
        null
      );
    },
    i(o) {
      t || (Nt(a, o), t = !0);
    },
    o(o) {
      Mt(a, o), t = !1;
    },
    d(o) {
      o && ye(e), n && n.d(o), a && a.d(o);
    }
  };
}
function Bi(r) {
  let e, t, n, i, a, o, l, s, c, d;
  return l = new hi({
    props: {
      size: (
        /*size*/
        r[6]
      ),
      variant: (
        /*variant*/
        r[10]
      ),
      elem_id: (
        /*elem_id*/
        r[1]
      ),
      elem_classes: (
        /*elem_classes*/
        r[2]
      ),
      visible: (
        /*visible*/
        r[3]
      ),
      scale: (
        /*scale*/
        r[8]
      ),
      min_width: (
        /*min_width*/
        r[9]
      ),
      disabled: (
        /*disabled*/
        r[11]
      ),
      $$slots: { default: [xi] },
      $$scope: { ctx: r }
    }
  }), l.$on(
    "click",
    /*open_file_upload*/
    r[14]
  ), {
    c() {
      e = Lt("input"), o = Pt(), $i(l.$$.fragment), this.h();
    },
    l(p) {
      e = It(p, "INPUT", {
        class: !0,
        accept: !0,
        type: !0,
        webkitdirectory: !0,
        mozdirectory: !0,
        "data-testid": !0
      }), o = Ot(p), gi(l.$$.fragment, p), this.h();
    },
    h() {
      H(e, "class", "hide svelte-1gxyyj1"), H(
        e,
        "accept",
        /*accept_file_types*/
        r[13]
      ), H(e, "type", "file"), e.multiple = t = /*file_count*/
      r[5] === "multiple" || void 0, H(e, "webkitdirectory", n = /*file_count*/
      r[5] === "directory" || void 0), H(e, "mozdirectory", i = /*file_count*/
      r[5] === "directory" || void 0), H(e, "data-testid", a = /*label*/
      r[4] + "-upload-button");
    },
    m(p, m) {
      Fe(p, e, m), r[21](e), Fe(p, o, m), wi(l, p, m), s = !0, c || (d = [
        ot(
          e,
          "change",
          /*load_files_from_upload*/
          r[15]
        ),
        ot(e, "click", qi)
      ], c = !0);
    },
    p(p, [m]) {
      (!s || m & /*accept_file_types*/
      8192) && H(
        e,
        "accept",
        /*accept_file_types*/
        p[13]
      ), (!s || m & /*file_count*/
      32 && t !== (t = /*file_count*/
      p[5] === "multiple" || void 0)) && (e.multiple = t), (!s || m & /*file_count*/
      32 && n !== (n = /*file_count*/
      p[5] === "directory" || void 0)) && H(e, "webkitdirectory", n), (!s || m & /*file_count*/
      32 && i !== (i = /*file_count*/
      p[5] === "directory" || void 0)) && H(e, "mozdirectory", i), (!s || m & /*label*/
      16 && a !== (a = /*label*/
      p[4] + "-upload-button")) && H(e, "data-testid", a);
      const b = {};
      m & /*size*/
      64 && (b.size = /*size*/
      p[6]), m & /*variant*/
      1024 && (b.variant = /*variant*/
      p[10]), m & /*elem_id*/
      2 && (b.elem_id = /*elem_id*/
      p[1]), m & /*elem_classes*/
      4 && (b.elem_classes = /*elem_classes*/
      p[2]), m & /*visible*/
      8 && (b.visible = /*visible*/
      p[3]), m & /*scale*/
      256 && (b.scale = /*scale*/
      p[8]), m & /*min_width*/
      512 && (b.min_width = /*min_width*/
      p[9]), m & /*disabled*/
      2048 && (b.disabled = /*disabled*/
      p[11]), m & /*$$scope, icon, value*/
      4194433 && (b.$$scope = { dirty: m, ctx: p }), l.$set(b);
    },
    i(p) {
      s || (Nt(l.$$.fragment, p), s = !0);
    },
    o(p) {
      Mt(l.$$.fragment, p), s = !1;
    },
    d(p) {
      p && (ye(e), ye(o)), r[21](null), vi(l, p), c = !1, ki(d);
    }
  };
}
function qi(r) {
  const e = r.target;
  e.value && (e.value = "");
}
function Ti(r, e, t) {
  let { $$slots: n = {}, $$scope: i } = e;
  var a = this && this.__awaiter || function($, I, N, O) {
    function z(k) {
      return k instanceof N ? k : new N(function(T) {
        T(k);
      });
    }
    return new (N || (N = Promise))(function(k, T) {
      function U(M) {
        try {
          q(O.next(M));
        } catch (L) {
          T(L);
        }
      }
      function j(M) {
        try {
          q(O.throw(M));
        } catch (L) {
          T(L);
        }
      }
      function q(M) {
        M.done ? k(M.value) : z(M.value).then(U, j);
      }
      q((O = O.apply($, I || [])).next());
    });
  };
  let { elem_id: o = "" } = e, { elem_classes: l = [] } = e, { visible: s = !0 } = e, { label: c } = e, { value: d } = e, { file_count: p } = e, { file_types: m = [] } = e, { root: b } = e, { size: R = "lg" } = e, { icon: C = null } = e, { scale: w = null } = e, { min_width: y = void 0 } = e, { variant: _ = "secondary" } = e, { disabled: u = !1 } = e, { max_file_size: h = null } = e, { upload: f } = e;
  const g = Si();
  let v, E;
  m == null ? E = null : (m = m.map(($) => $.startsWith(".") ? $ : $ + "/*"), E = m.join(", "));
  function F() {
    g("click"), v.click();
  }
  function x($) {
    return a(this, void 0, void 0, function* () {
      var I;
      let N = Array.from($);
      if (!$.length)
        return;
      p === "single" && (N = [$[0]]);
      let O = yield Gt(N);
      yield Ai();
      try {
        O = (I = yield f(O, b, void 0, h ?? 1 / 0)) === null || I === void 0 ? void 0 : I.filter((z) => z !== null);
      } catch (z) {
        g("error", z.message);
        return;
      }
      t(0, d = p === "single" ? O == null ? void 0 : O[0] : O), g("change", d), g("upload", d);
    });
  }
  function P($) {
    return a(this, void 0, void 0, function* () {
      const I = $.target;
      I.files && (yield x(I.files));
    });
  }
  function D($) {
    fi[$ ? "unshift" : "push"](() => {
      v = $, t(12, v);
    });
  }
  return r.$$set = ($) => {
    "elem_id" in $ && t(1, o = $.elem_id), "elem_classes" in $ && t(2, l = $.elem_classes), "visible" in $ && t(3, s = $.visible), "label" in $ && t(4, c = $.label), "value" in $ && t(0, d = $.value), "file_count" in $ && t(5, p = $.file_count), "file_types" in $ && t(16, m = $.file_types), "root" in $ && t(17, b = $.root), "size" in $ && t(6, R = $.size), "icon" in $ && t(7, C = $.icon), "scale" in $ && t(8, w = $.scale), "min_width" in $ && t(9, y = $.min_width), "variant" in $ && t(10, _ = $.variant), "disabled" in $ && t(11, u = $.disabled), "max_file_size" in $ && t(18, h = $.max_file_size), "upload" in $ && t(19, f = $.upload), "$$scope" in $ && t(22, i = $.$$scope);
  }, [
    d,
    o,
    l,
    s,
    c,
    p,
    R,
    C,
    w,
    y,
    _,
    u,
    v,
    E,
    F,
    P,
    m,
    b,
    h,
    f,
    n,
    D,
    i
  ];
}
class Ri extends mi {
  constructor(e) {
    super(), bi(this, e, Ti, Bi, Ci, {
      elem_id: 1,
      elem_classes: 2,
      visible: 3,
      label: 4,
      value: 0,
      file_count: 5,
      file_types: 16,
      root: 17,
      size: 6,
      icon: 7,
      scale: 8,
      min_width: 9,
      variant: 10,
      disabled: 11,
      max_file_size: 18,
      upload: 19
    });
  }
}
const {
  SvelteComponent: zi,
  claim_component: Ii,
  claim_text: Oi,
  create_component: Li,
  destroy_component: Pi,
  detach: Ni,
  init: Mi,
  insert_hydration: ji,
  mount_component: Hi,
  safe_not_equal: Ui,
  set_data: Gi,
  text: Zi,
  transition_in: Xi,
  transition_out: Wi
} = window.__gradio__svelte__internal;
function Yi(r) {
  let e = (
    /*label*/
    (r[4] ?? "") + ""
  ), t;
  return {
    c() {
      t = Zi(e);
    },
    l(n) {
      t = Oi(n, e);
    },
    m(n, i) {
      ji(n, t, i);
    },
    p(n, i) {
      i & /*label*/
      16 && e !== (e = /*label*/
      (n[4] ?? "") + "") && Gi(t, e);
    },
    d(n) {
      n && Ni(t);
    }
  };
}
function Ki(r) {
  let e, t;
  return e = new Ri({
    props: {
      elem_id: (
        /*elem_id*/
        r[1]
      ),
      elem_classes: (
        /*elem_classes*/
        r[2]
      ),
      visible: (
        /*visible*/
        r[3]
      ),
      file_count: (
        /*file_count*/
        r[5]
      ),
      file_types: (
        /*file_types*/
        r[6]
      ),
      size: (
        /*size*/
        r[8]
      ),
      scale: (
        /*scale*/
        r[9]
      ),
      icon: (
        /*icon*/
        r[10]
      ),
      min_width: (
        /*min_width*/
        r[11]
      ),
      root: (
        /*root*/
        r[7]
      ),
      value: (
        /*value*/
        r[0]
      ),
      disabled: (
        /*disabled*/
        r[14]
      ),
      variant: (
        /*variant*/
        r[12]
      ),
      label: (
        /*label*/
        r[4]
      ),
      max_file_size: (
        /*gradio*/
        r[13].max_file_size
      ),
      upload: (
        /*func*/
        r[18]
      ),
      $$slots: { default: [Yi] },
      $$scope: { ctx: r }
    }
  }), e.$on(
    "click",
    /*click_handler*/
    r[19]
  ), e.$on(
    "change",
    /*change_handler*/
    r[20]
  ), e.$on(
    "upload",
    /*upload_handler*/
    r[21]
  ), e.$on(
    "error",
    /*error_handler*/
    r[22]
  ), {
    c() {
      Li(e.$$.fragment);
    },
    l(n) {
      Ii(e.$$.fragment, n);
    },
    m(n, i) {
      Hi(e, n, i), t = !0;
    },
    p(n, [i]) {
      const a = {};
      i & /*elem_id*/
      2 && (a.elem_id = /*elem_id*/
      n[1]), i & /*elem_classes*/
      4 && (a.elem_classes = /*elem_classes*/
      n[2]), i & /*visible*/
      8 && (a.visible = /*visible*/
      n[3]), i & /*file_count*/
      32 && (a.file_count = /*file_count*/
      n[5]), i & /*file_types*/
      64 && (a.file_types = /*file_types*/
      n[6]), i & /*size*/
      256 && (a.size = /*size*/
      n[8]), i & /*scale*/
      512 && (a.scale = /*scale*/
      n[9]), i & /*icon*/
      1024 && (a.icon = /*icon*/
      n[10]), i & /*min_width*/
      2048 && (a.min_width = /*min_width*/
      n[11]), i & /*root*/
      128 && (a.root = /*root*/
      n[7]), i & /*value*/
      1 && (a.value = /*value*/
      n[0]), i & /*disabled*/
      16384 && (a.disabled = /*disabled*/
      n[14]), i & /*variant*/
      4096 && (a.variant = /*variant*/
      n[12]), i & /*label*/
      16 && (a.label = /*label*/
      n[4]), i & /*gradio*/
      8192 && (a.max_file_size = /*gradio*/
      n[13].max_file_size), i & /*$$scope, label*/
      33554448 && (a.$$scope = { dirty: i, ctx: n }), e.$set(a);
    },
    i(n) {
      t || (Xi(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Wi(e.$$.fragment, n), t = !1;
    },
    d(n) {
      Pi(e, n);
    }
  };
}
function Qi(r, e, t) {
  let n;
  var i = this && this.__awaiter || function(D, $, I, N) {
    function O(z) {
      return z instanceof I ? z : new I(function(k) {
        k(z);
      });
    }
    return new (I || (I = Promise))(function(z, k) {
      function T(q) {
        try {
          j(N.next(q));
        } catch (M) {
          k(M);
        }
      }
      function U(q) {
        try {
          j(N.throw(q));
        } catch (M) {
          k(M);
        }
      }
      function j(q) {
        q.done ? z(q.value) : O(q.value).then(T, U);
      }
      j((N = N.apply(D, $ || [])).next());
    });
  };
  let { elem_id: a = "" } = e, { elem_classes: o = [] } = e, { visible: l = !0 } = e, { label: s } = e, { value: c } = e, { file_count: d } = e, { file_types: p = [] } = e, { root: m } = e, { size: b = "lg" } = e, { scale: R = null } = e, { icon: C = null } = e, { min_width: w = void 0 } = e, { variant: y = "secondary" } = e, { gradio: _ } = e, { interactive: u } = e;
  function h(D, $) {
    return i(this, void 0, void 0, function* () {
      var I;
      const O = [];
      for (let z = 0; z < $.length; z += 1e3) {
        const k = $.slice(z, z + 1e3), T = new FormData();
        k.forEach((L) => {
          T.append("files", L);
        });
        const U = `${D}/upload_files`;
        let j;
        try {
          j = yield fetch(U, { method: "POST", body: T });
        } catch (L) {
          throw new Error(`Network error: ${(I = L == null ? void 0 : L.message) !== null && I !== void 0 ? I : L}`);
        }
        if (!j.ok) {
          const L = yield j.text();
          throw new Error(`Upload failed: ${L}`);
        }
        const M = (yield j.json()).files;
        M != null && M.length && O.push(...M);
      }
      return { files: O };
    });
  }
  function f(D, $, I, N) {
    return i(this, void 0, void 0, function* () {
      let O = (Array.isArray(D) ? D : [D]).map((k) => k.blob);
      const z = O.filter((k) => k.size > (N ?? 1 / 0));
      if (z.length)
        throw new Error(`File size exceeds the maximum allowed size of ${N} bytes: ${z.map((k) => k.name).join(", ")}`);
      return yield Promise.all(yield h($, O).then((k) => i(this, void 0, void 0, function* () {
        if (k.error)
          throw new Error(k.error);
        return k.files ? k.files.map((T, U) => new st(Object.assign(Object.assign({}, D[U]), { path: T, url: `${T}` }))) : [];
      })));
    });
  }
  function g(D, $) {
    return i(this, void 0, void 0, function* () {
      t(0, c = D), _.dispatch($);
    });
  }
  const v = (...D) => f(...D), E = () => _.dispatch("click"), F = ({ detail: D }) => g(D, "change"), x = ({ detail: D }) => g(D, "upload"), P = ({ detail: D }) => {
    _.dispatch("error", D);
  };
  return r.$$set = (D) => {
    "elem_id" in D && t(1, a = D.elem_id), "elem_classes" in D && t(2, o = D.elem_classes), "visible" in D && t(3, l = D.visible), "label" in D && t(4, s = D.label), "value" in D && t(0, c = D.value), "file_count" in D && t(5, d = D.file_count), "file_types" in D && t(6, p = D.file_types), "root" in D && t(7, m = D.root), "size" in D && t(8, b = D.size), "scale" in D && t(9, R = D.scale), "icon" in D && t(10, C = D.icon), "min_width" in D && t(11, w = D.min_width), "variant" in D && t(12, y = D.variant), "gradio" in D && t(13, _ = D.gradio), "interactive" in D && t(17, u = D.interactive);
  }, r.$$.update = () => {
    r.$$.dirty & /*interactive*/
    131072 && t(14, n = !u);
  }, [
    c,
    a,
    o,
    l,
    s,
    d,
    p,
    m,
    b,
    R,
    C,
    w,
    y,
    _,
    n,
    f,
    g,
    u,
    v,
    E,
    F,
    x,
    P
  ];
}
class Ob extends zi {
  constructor(e) {
    super(), Mi(this, e, Qi, Ki, Ui, {
      elem_id: 1,
      elem_classes: 2,
      visible: 3,
      label: 4,
      value: 0,
      file_count: 5,
      file_types: 6,
      root: 7,
      size: 8,
      scale: 9,
      icon: 10,
      min_width: 11,
      variant: 12,
      gradio: 13,
      interactive: 17
    });
  }
}
export {
  Ri as BaseUploadButton,
  Ob as default
};
