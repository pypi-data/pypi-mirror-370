const { setContext: ie, getContext: E } = window.__gradio__svelte__internal, C = "WORKER_PROXY_CONTEXT_KEY";
function k() {
  return E(C);
}
const R = "lite.local";
function O(n) {
  return n.host === window.location.host || n.host === "localhost:7860" || n.host === "127.0.0.1:7860" || // Ref: https://github.com/gradio-app/gradio/blob/v3.32.0/js/app/src/Index.svelte#L194
  n.host === R;
}
function q(n, e) {
  const r = e.toLowerCase();
  for (const [t, o] of Object.entries(n))
    if (t.toLowerCase() === r)
      return o;
}
function L(n) {
  const e = typeof window < "u";
  if (n == null || !e)
    return !1;
  const r = new URL(n, window.location.href);
  return !(!O(r) || r.protocol !== "http:" && r.protocol !== "https:");
}
let u;
async function T(n) {
  const e = typeof window < "u";
  if (n == null || !e || !L(n))
    return n;
  if (u == null)
    try {
      u = k();
    } catch {
      return n;
    }
  if (u == null)
    return n;
  const t = new URL(n, window.location.href).pathname;
  return u.httpRequest({
    method: "GET",
    path: t,
    headers: {},
    query_string: ""
  }).then((o) => {
    if (o.status !== 200)
      throw new Error(`Failed to get file ${t} from the Wasm worker.`);
    const l = new Blob([o.body], {
      type: q(o.headers, "content-type")
    });
    return URL.createObjectURL(l);
  });
}
const {
  SvelteComponent: ae,
  assign: _e,
  check_outros: ce,
  children: ue,
  claim_element: fe,
  compute_rest_props: de,
  create_slot: me,
  detach: he,
  element: ge,
  empty: pe,
  exclude_internal_props: we,
  get_all_dirty_from_scope: be,
  get_slot_changes: ye,
  get_spread_update: ve,
  group_outros: Ee,
  init: Ce,
  insert_hydration: ke,
  listen: Re,
  prevent_default: Oe,
  safe_not_equal: qe,
  set_attributes: Le,
  set_style: Te,
  toggle_class: Ke,
  transition_in: Se,
  transition_out: Ue,
  update_slot_base: Pe
} = window.__gradio__svelte__internal, { createEventDispatcher: We, onMount: $e } = window.__gradio__svelte__internal, {
  SvelteComponent: K,
  assign: d,
  bubble: S,
  claim_element: U,
  compute_rest_props: h,
  detach: P,
  element: W,
  exclude_internal_props: $,
  get_spread_update: I,
  init: X,
  insert_hydration: Y,
  listen: j,
  noop: g,
  safe_not_equal: D,
  set_attributes: p,
  src_url_equal: F,
  toggle_class: w
} = window.__gradio__svelte__internal;
function G(n) {
  let e, r, t, o, l = [
    {
      src: r = /*resolved_src*/
      n[0]
    },
    /*$$restProps*/
    n[1]
  ], s = {};
  for (let i = 0; i < l.length; i += 1)
    s = d(s, l[i]);
  return {
    c() {
      e = W("img"), this.h();
    },
    l(i) {
      e = U(i, "IMG", { src: !0 }), this.h();
    },
    h() {
      p(e, s), w(e, "svelte-kxeri3", !0);
    },
    m(i, c) {
      Y(i, e, c), t || (o = j(
        e,
        "load",
        /*load_handler*/
        n[4]
      ), t = !0);
    },
    p(i, [c]) {
      p(e, s = I(l, [
        c & /*resolved_src*/
        1 && !F(e.src, r = /*resolved_src*/
        i[0]) && { src: r },
        c & /*$$restProps*/
        2 && /*$$restProps*/
        i[1]
      ])), w(e, "svelte-kxeri3", !0);
    },
    i: g,
    o: g,
    d(i) {
      i && P(e), t = !1, o();
    }
  };
}
function H(n, e, r) {
  const t = ["src"];
  let o = h(e, t), { src: l = void 0 } = e, s, i;
  function c(a) {
    S.call(this, n, a);
  }
  return n.$$set = (a) => {
    e = d(d({}, e), $(a)), r(1, o = h(e, t)), "src" in a && r(2, l = a.src);
  }, n.$$.update = () => {
    if (n.$$.dirty & /*src, latest_src*/
    12) {
      r(0, s = l), r(3, i = l);
      const a = l;
      T(a).then((v) => {
        i === a && r(0, s = v);
      });
    }
  }, [s, o, l, i, c];
}
class M extends K {
  constructor(e) {
    super(), X(this, e, H, G, D, { src: 2 });
  }
}
const {
  SvelteComponent: N,
  attr: V,
  check_outros: x,
  children: A,
  claim_component: B,
  claim_element: z,
  create_component: J,
  destroy_component: Q,
  detach: b,
  element: Z,
  group_outros: ee,
  init: te,
  insert_hydration: ne,
  mount_component: oe,
  safe_not_equal: re,
  toggle_class: _,
  transition_in: f,
  transition_out: m
} = window.__gradio__svelte__internal;
function y(n) {
  let e, r;
  return e = new M({
    props: { src: (
      /*value*/
      n[0].url
    ), alt: "" }
  }), {
    c() {
      J(e.$$.fragment);
    },
    l(t) {
      B(e.$$.fragment, t);
    },
    m(t, o) {
      oe(e, t, o), r = !0;
    },
    p(t, o) {
      const l = {};
      o & /*value*/
      1 && (l.src = /*value*/
      t[0].url), e.$set(l);
    },
    i(t) {
      r || (f(e.$$.fragment, t), r = !0);
    },
    o(t) {
      m(e.$$.fragment, t), r = !1;
    },
    d(t) {
      Q(e, t);
    }
  };
}
function le(n) {
  let e, r, t = (
    /*value*/
    n[0] && y(n)
  );
  return {
    c() {
      e = Z("div"), t && t.c(), this.h();
    },
    l(o) {
      e = z(o, "DIV", { class: !0 });
      var l = A(e);
      t && t.l(l), l.forEach(b), this.h();
    },
    h() {
      V(e, "class", "container svelte-1sgcyba"), _(
        e,
        "table",
        /*type*/
        n[1] === "table"
      ), _(
        e,
        "gallery",
        /*type*/
        n[1] === "gallery"
      ), _(
        e,
        "selected",
        /*selected*/
        n[2]
      ), _(
        e,
        "border",
        /*value*/
        n[0]
      );
    },
    m(o, l) {
      ne(o, e, l), t && t.m(e, null), r = !0;
    },
    p(o, [l]) {
      /*value*/
      o[0] ? t ? (t.p(o, l), l & /*value*/
      1 && f(t, 1)) : (t = y(o), t.c(), f(t, 1), t.m(e, null)) : t && (ee(), m(t, 1, 1, () => {
        t = null;
      }), x()), (!r || l & /*type*/
      2) && _(
        e,
        "table",
        /*type*/
        o[1] === "table"
      ), (!r || l & /*type*/
      2) && _(
        e,
        "gallery",
        /*type*/
        o[1] === "gallery"
      ), (!r || l & /*selected*/
      4) && _(
        e,
        "selected",
        /*selected*/
        o[2]
      ), (!r || l & /*value*/
      1) && _(
        e,
        "border",
        /*value*/
        o[0]
      );
    },
    i(o) {
      r || (f(t), r = !0);
    },
    o(o) {
      m(t), r = !1;
    },
    d(o) {
      o && b(e), t && t.d();
    }
  };
}
function se(n, e, r) {
  let { value: t } = e, { type: o } = e, { selected: l = !1 } = e;
  return n.$$set = (s) => {
    "value" in s && r(0, t = s.value), "type" in s && r(1, o = s.type), "selected" in s && r(2, l = s.selected);
  }, [t, o, l];
}
class Ie extends N {
  constructor(e) {
    super(), te(this, e, se, le, re, { value: 0, type: 1, selected: 2 });
  }
}
export {
  Ie as default
};
