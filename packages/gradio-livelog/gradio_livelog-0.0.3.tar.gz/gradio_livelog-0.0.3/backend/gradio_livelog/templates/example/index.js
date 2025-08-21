const {
  SvelteComponent: _,
  append_hydration: o,
  attr: d,
  children: h,
  claim_element: g,
  claim_text: y,
  detach: c,
  element: m,
  init: v,
  insert_hydration: b,
  noop: u,
  safe_not_equal: E,
  set_data: q,
  text: w,
  toggle_class: r
} = window.__gradio__svelte__internal;
function S(a) {
  let e, t = f(
    /*value*/
    a[0]
  ) + "", i;
  return {
    c() {
      e = m("pre"), i = w(t), this.h();
    },
    l(l) {
      e = g(l, "PRE", { class: !0 });
      var n = h(e);
      i = y(n, t), n.forEach(c), this.h();
    },
    h() {
      d(e, "class", "svelte-1ioyqn2"), r(
        e,
        "table",
        /*type*/
        a[1] === "table"
      ), r(
        e,
        "gallery",
        /*type*/
        a[1] === "gallery"
      ), r(
        e,
        "selected",
        /*selected*/
        a[2]
      );
    },
    m(l, n) {
      b(l, e, n), o(e, i);
    },
    p(l, [n]) {
      n & /*value*/
      1 && t !== (t = f(
        /*value*/
        l[0]
      ) + "") && q(i, t), n & /*type*/
      2 && r(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), n & /*type*/
      2 && r(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), n & /*selected*/
      4 && r(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: u,
    o: u,
    d(l) {
      l && c(e);
    }
  };
}
function f(a, e = 60) {
  if (!a) return "";
  const t = String(a);
  return t.length <= e ? t : t.slice(0, e) + "...";
}
function p(a, e, t) {
  let { value: i } = e, { type: l } = e, { selected: n = !1 } = e;
  return a.$$set = (s) => {
    "value" in s && t(0, i = s.value), "type" in s && t(1, l = s.type), "selected" in s && t(2, n = s.selected);
  }, [i, l, n];
}
class C extends _ {
  constructor(e) {
    super(), v(this, e, p, S, E, { value: 0, type: 1, selected: 2 });
  }
}
export {
  C as default
};
