---
name: saas-ui-redesign
description: Redesigns the UI of an existing Vue 3 app into a modern SaaS-style interface with a vertical left sidebar instead of a top nav bar, design tokens, consistent spacing and a mobile drawer, without changing behaviour. Use when asked to redesign or modernize a Vue app, give it a SaaS or dashboard look, make it look professional, clean up inconsistent styling, or move a top nav to a sidebar. Do not use for non-Vue apps, new apps built from scratch, a tweak to one component, backend work, or feature changes.
---

# SaaS UI Redesign for Vue 3

Restyle an existing Vue 3 app around a left sidebar shell and a token-based design system. The work is presentation only: when you finish, the app does exactly what it did before and looks better doing it.

## Ground rules

- **Presentation only.** Preserve routes, data fetching, stores, business logic, emitted events, i18n keys and URLs. If a fix needs a behaviour change, list it in your final report instead of making it.
- **No new dependencies** unless the user asks. A sidebar, a drawer and tokens need only Vue, Vue Router and CSS.
- **The project's rules win over this skill.** Read `CLAUDE.md`, `README` and any contributing or design docs first. A banned emoji list, a set palette, a font or a required subagent overrides the defaults below. Token values here are defaults for projects with no rules of their own.
- **Use what the project already has.** If it uses a component library (Vuetify, PrimeVue, Quasar) use that library's layout and theme system rather than building a parallel one. In Nuxt the shell lives in `layouts/`.
- **Stay in scope.** No dark mode, collapsible icon rail, command palette or page redesign unless asked.
- **Work in small steps,** in the order below, and keep the app building after each one. Check `git status` first so you do not overwrite someone else's uncommitted work.

## 1. Audit before changing anything

Read, do not assume. Record the results, because the shell work depends on them.

- **Before screenshots:** capture every route at desktop and phone width now. You cannot get these back later.
- **App shell:** the component mounted by the entry file, usually `App.vue`, and any layout components.
- **Router:** every route, including nested, parameterized, redirect, not-found and guarded routes.
- **Nav items:** where they live, how the active state is computed, any `v-if` or permission conditions, and how labels are produced.
- **Global styles:** where they live, and any existing tokens. Count hardcoded colours and magic numbers.
- **i18n:** how many locales exist, how to add a key to all of them, and which labels are already hardcoded.
- **Everything in the top bar:** brand, search, profile, language, notifications, global filters. Each one needs a new home (section 3).
- **Top-bar assumptions.** Search styles and scripts for:
  - `position: sticky` and `position: fixed`, and `top:` offsets equal to the old header height
  - `100vh` and `calc(100vh - ...)`
  - `z-index` values, dropdowns and `<Teleport>` targets
  - `@media` breakpoints, `max-width` wrappers, and `innerWidth` or `getBoundingClientRect` used to size charts
  - `scrollBehavior` in the router and any scroll listeners
- **Tests:** end-to-end tests or scripts that select on classes you are about to rename, such as `.top-nav`. Keep `data-testid` attributes.

## 2. Design tokens

Define tokens as CSS custom properties on `:root`, in the place the project already keeps global styles. Name them by role, not value.

| Group | Default scale |
|---|---|
| Spacing | `--space-1` to `--space-8`: 4, 8, 12, 16, 20, 24, 32, 48px |
| Type size | `--text-xs` to `--text-2xl`: 12, 14, 16, 18, 24, 30px |
| Weight | `--weight-normal`, `--weight-medium`, `--weight-semibold`: 400, 500, 600 |
| Radius | `--radius-sm`, `--radius-md`, `--radius-lg`: 6, 8, 12px |
| Shadow | `--shadow-sm`, `--shadow-md`, `--shadow-lg`: soft and low-contrast |
| Colour | `--color-bg`, `--color-surface`, `--color-border`, `--color-text`, `--color-text-muted`, `--color-primary`, plus success, warning, danger and info, each with a foreground and a tinted background |
| Layout | `--sidebar-width: 240px`, `--topbar-height: 56px`, `--content-max-width` |
| Layer | `--z-sticky`, `--z-sidebar`, `--z-dropdown`, `--z-drawer`, `--z-modal` |

**Migrate, do not add alongside.** Replace hardcoded values with tokens as you touch each file, and snap near-duplicates to the scale (15px and 17px padding both become `--space-4`). Take colour values from the palette the project already uses; do not invent a new brand. If tokens already exist, extend them. A second token system is worse than none.

Move every `z-index` onto the layer tokens. Scattered values are the usual cause of a dropdown rendering behind the sidebar.

## 3. App shell

Replace the top bar with a sidebar and a content column. Extract the sidebar into its own component if the shell would otherwise get crowded.

```css
.app-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100dvh;
}
.app-sidebar {
  position: sticky;
  top: 0;
  height: 100dvh;
  display: flex;
  flex-direction: column;
}
.app-sidebar-nav { flex: 1; min-height: 0; overflow-y: auto; }
```

- **`minmax(0, 1fr)` is required.** With plain `1fr`, a wide table stretches the column and the whole page scrolls sideways instead of the table.
- **Keep document scrolling.** Let the window scroll and keep the sidebar sticky. Making `main` the scroller breaks router `scrollBehavior`, scroll restoration and existing sticky offsets. Do it only if the audit shows the app already depends on it.
- **Sidebar structure,** top to bottom: brand, primary nav (scrolls if long), footer with account controls.
- **Landmarks:** use `<aside>` for the sidebar, `<nav aria-label="...">` around the links and `<main>` for the content. Add a skip link to `main` if the project has none, since keyboard users now tab past every nav item on each page.
- **Active state:** use `<router-link>`, which sets `aria-current="page"` on the exact match by itself. Style `.router-link-active` for sections with child routes so the parent stays highlighted on detail pages. Use `.router-link-exact-active` for `/`, or an item for the root route can light up everywhere. Remove hand-rolled `$route.path ===` class bindings, which also miss child routes.
- **Nav item style:** full-width row, at least 40px tall, with consistent padding. Show the active item through tinted background and text colour, never colour alone at low contrast. Show hover separately from active.
- **Focus:** give every interactive element a visible `:focus-visible` ring from a token. Never leave `outline: none` without a replacement.
- **Icons are optional.** With no icon library, use inline SVG with `aria-hidden="true"` or use text alone. Respect any emoji ban.

### Give every top-bar control a home

Decide each one explicitly and record it in your report.

| Control | Default home |
|---|---|
| Brand or logo | Top of the sidebar. Plain text or a link home, not the page's `h1` |
| Profile, account menu | Sidebar footer |
| Language, theme | Sidebar footer |
| Global search | Top of the sidebar, or a slim sticky bar in the content column |
| Global filters | Sticky bar at the top of the content column, above `<router-view>`. They affect content, and they need more width than a sidebar offers |
| Page-specific actions | The page header |

When you move these:

- **Keep the wiring.** Every prop, listener and event a moved component had must still work. If it moves into a child component, forward the events up.
- **Dropdowns must flip.** A menu in the sidebar footer has to open upward (`bottom: 100%`). Keep the footer outside the `overflow-y: auto` region, or the menu gets clipped. Check that the width still fits inside or overlaps cleanly past the sidebar edge.
- **Fix sticky offsets.** An offset equal to the old header height becomes `top: 0` on desktop and `top: var(--topbar-height)` on mobile. Replace magic numbers with the token.
- **Modals stay put.** Teleported modals remain above everything on `--z-modal`.
- **Content width shrinks.** Charts and grids lose the sidebar's width, while viewport `@media` queries do not notice. Recheck every multi-column layout, and move breakpoints or use container queries where they now break too late.

## 4. Responsive behaviour

Define one breakpoint for the shell, 1024px by default, and use it everywhere. Below it the sidebar becomes a drawer and a slim top bar appears.

- **Top bar:** sticky, `--topbar-height` tall, containing a menu toggle and the brand.
- **Toggle:** a real `<button>` with `aria-expanded`, `aria-controls` and a translated `aria-label`.
- **Drawer:** `position: fixed` on `--z-drawer`, slid in with `transform`, with a backdrop below it.
- **Closed means not focusable.** Add `visibility: hidden` to the closed drawer, delayed until the slide finishes. An element moved off-screen by `transform` alone stays in the tab order.
- **Close it** on Escape, backdrop click, a close button inside the drawer, and every route change (watch `route.fullPath`).
- **Focus:** on open, move focus to the first control in the drawer. Set `inert` on the content and top bar while open, which keeps Tab inside the drawer without a focus-trap library. On close, remove `inert`, wait for `nextTick`, then return focus to the toggle. Focus cannot land on an inert element.
- **Scroll lock:** stop the page behind the open drawer from scrolling, and restore it on close.
- **Resize:** listen with `matchMedia` and clear the open state when the viewport crosses to desktop. Otherwise `inert` can leave the content dead on a wide screen.
- **Motion:** 150 to 200ms on `transform` and `opacity` only, disabled under `prefers-reduced-motion`.
- **Fixed-position children:** an element with `transform` becomes the containing block for `position: fixed` descendants, so a fixed menu inside the drawer lands in the wrong place. Use absolute positioning or a Teleport.

On phones, also: padding drops to `--space-4`, page headers stack, tables scroll inside their container, the page itself never scrolls sideways, touch targets reach 44px, and sticky filter bars stop being sticky if they wrap past two rows.

## 5. Spacing and polish rules

Each rule is checkable. Every spacing, radius, shadow and colour value comes from a token.

**Page layout**
- Content padding is `--space-6` on desktop. Sections are `--space-6` apart. Grid gaps are `--space-4`.
- Each route has exactly one `h1`. The same header pattern appears on every page.

**Page headers**
- Title at `--text-2xl` semibold, optional description at `--text-sm` muted, `--space-1` between them, `--space-6` below.
- Actions sit on the right and wrap below the title on phones.

**Cards**
- Padding `--space-5`, `--radius-lg`, 1px `--color-border`. Use a border or a shadow, not a heavy version of both.
- Card header has title on the left, actions on the right, `--space-4` below it. Do not nest cards.
- Stat cards in one row align their labels, values and heights.

**Tables**
- Wrap each table in an `overflow-x: auto` container so it scrolls alone.
- Header row: `--text-xs`, medium or semibold, muted. Body: `--text-sm`, one row density across the app.
- Numbers are right-aligned with `font-variant-numeric: tabular-nums`. Text is left-aligned.
- Row dividers are 1px `--color-border`; no vertical lines. Hover applies a subtle tint only when rows are clickable, or matches the existing behaviour.

**Forms**
- Label above the field, `--space-1` apart, `--space-4` between fields.
- Input, select and button share one height, 36 to 40px, and one radius.
- Every input has a real `<label>`. Hover, focus, disabled and error states are all styled. Error text sits below the field.

**Buttons**
- Three variants at most: primary, secondary, ghost, plus danger if destructive actions exist.
- No more than one primary per page region. All variants show hover, active, focus, disabled and busy states.

**States**
- Every view that loads data shows loading, empty and error states with one shared look.
- Loading keeps the layout stable, with a reserved area or skeleton instead of a jump. Empty says what is missing and sits centred in its container. Error uses the danger tint and the existing message.
- If a state is missing, add the presentational branch. Add a retry button only if a retry already exists.

**Finish**
- Text contrast is at least 4.5:1. Status is never shown by colour alone.
- Transitions name their properties, 150 to 200ms; avoid `transition: all`.
- Long labels and the longest locale fit the sidebar without breaking it.
- New user-facing strings, including `aria-label`s, go through i18n in every locale. Do not rename existing keys, and do not change existing copy. Report hardcoded labels you find rather than fixing them.

## 6. Verify

Run all of it. Use the project's documented commands and browser tooling, and reuse a dev server that is already running. If you cannot check something, say so in the report rather than implying it passed.

1. **Build:** the production build passes with no new warnings. Run existing tests and lint.
2. **Routes:** every route from the audit renders, including nested and not-found routes, with no new console errors or failed requests.
3. **Screenshots:** capture every route at desktop (1440px wide) and phone (390px wide) and compare each with its before screenshot. Look for lost content, clipped menus and misaligned headers. Also check the shell breakpoint itself, where layouts usually fail.
4. **Behaviour:** filters, language switching, profile menu, modals and any create, edit or delete flow work as before, and data shown matches before. Change a filter on one page and confirm it still applies.
5. **Keyboard:** Tab from the top of the page reaches the skip link, every nav item and the content in order, with a visible focus ring. Enter activates links. Dropdowns close on Escape if they did before.
6. **Drawer on phone width:** opens from the toggle, focus moves in, Tab stays inside, Escape closes and focus returns to the toggle, backdrop closes it, a link navigates and closes it, the closed drawer is not tabbable, and the page does not scroll behind it. Resize to desktop while open and confirm the content still works.
7. **Layout:** confirm `document.documentElement.scrollWidth <= clientWidth` on every route at phone width. Scroll a long page on desktop: the sidebar stays put and sticky bars sit at the right offset.
8. **Token migration:** search for hardcoded hex values and `z-index` numbers again, and compare with the audit count. Anything left should be deliberate.
9. **Accessibility:** a labelled `nav`, one `main`, `aria-current` on the current link, one `h1` per route.

## Final report

State what changed by area, the home chosen for each former top-bar control, the verification results including anything you could not check, and any behaviour issues or hardcoded labels you found and deliberately left alone.
