# Vue + Nuxt Full-Stack Memory Card Prompt Library

**208 cards across 20 sections.**

## Shared style prompt (use once as the reusable prefix)

```text
Create a single educational memory-card infographic for a technical learner studying Vue.js and Nuxt. Use a consistent, polished technical-learning visual system across the entire collection: clean editorial infographic, light warm-neutral background, restrained deep navy + Vue green accents + one muted secondary accent, precise thin-line diagrams, simple geometric shapes, crisp typography, clear hierarchy, generous whitespace, aligned grids, and restrained use of icons. Portrait 4:5 composition suitable for saving as a standalone study card. Put the exact card title prominently at the top. Make the central concept visually obvious before adding details. Prefer one diagram or comparison with arrows and short labels over decorative illustrations. Use correct Vue/Nuxt terminology and readable English; keep on-image copy concise, normally 3–5 labels and no more than about 35 words outside the title. Use at most one tiny code example, no longer than 4 lines, only when it genuinely clarifies the concept. Highlight one practical takeaway in a small footer. Use accurate relationships, not merely decorative icons. Keep each card self-contained and understandable without the neighboring cards. Do not cram multiple unrelated concepts onto one card; do not invent APIs or code; do not use fake UI screenshots, dense paragraphs, tiny text, watermarks, logos that imitate official branding, or extra headings not requested. If a detail cannot be rendered legibly, simplify the diagram rather than adding more text. Follow the exact title and the content instructions that follow.
```

## How to use

For each image, combine the shared style prompt with exactly one card prompt. Keep each card independent; do not combine multiple cards into one image.

```python
from vue_nuxt_memory_prompts import build_prompts
prompts = build_prompts()  # style + card-specific prompt for each image
```

To inspect only a topic, use `build_prompts(sections="Vue reactivity")`. Available section names are printed by running the module.

## 001. Vue and Nuxt: The Learning Map
**Section:** Learning path

Card title: Vue and Nuxt: The Learning Map. Visual instructions: Create a roadmap with five connected stages from left to right: web foundations → Vue reactivity and components → Nuxt routing and rendering → server/data/security → production architecture. Under each stage, show only two representative topics. End with a small “build projects at every stage” marker. Make progression clear without implying that learning is strictly linear. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 002. Vue vs. Nuxt: What Each Layer Does
**Section:** Learning path

Card title: Vue vs. Nuxt: What Each Layer Does. Visual instructions: Show Vue as the UI/reactivity engine in the center and Nuxt as the full-stack framework around it. Connect Vue to templates, components, and reactive state; connect Nuxt to file-based routing, SSR, data fetching, server endpoints, and deployment. Make the relationship “Nuxt uses Vue” unmistakable. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 003. A Web App From Browser to Database
**Section:** Learning path

Card title: A Web App From Browser to Database. Visual instructions: Draw a simple request path: browser UI → Nuxt page/component → server API endpoint → service/business logic → database → response → UI update. Label which steps run in the browser and which run on the server. Use a single read request, not a complex distributed architecture. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 004. Single-File Component Anatomy
**Section:** Learning path

Card title: Single-File Component Anatomy. Visual instructions: Show one `.vue` file divided into `<script setup>`, `<template>`, and `<style>`. Explain each block with one short label: logic/state, rendered structure, presentation. Add a tiny component name at the top and arrows showing that the template consumes values from the script. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 005. The Development Feedback Loop
**Section:** Learning path

Card title: The Development Feedback Loop. Visual instructions: Illustrate edit code → Vite dev server transforms module → browser updates through HMR → developer checks output. Add a separate small production path: build → optimized assets/server output. Distinguish fast development feedback from production build behavior. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 006. Declarative UI vs. Manual DOM Updates
**Section:** Learning path

Card title: Declarative UI vs. Manual DOM Updates. Visual instructions: Compare two mini-panels. Left: imperative code manually changes a DOM text node after a button click. Right: a reactive `count` changes and the Vue template reflects the state. The takeaway should be “describe the UI from state; let Vue update the DOM.” Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 007. Client, Server, and Shared Code
**Section:** Learning path

Card title: Client, Server, and Shared Code. Visual instructions: Show three zones: browser/client code, server-only code, and shared code. Place DOM APIs and click handlers in client; secrets/database access in server; pure types/validation helpers in shared only when environment-safe. Use arrows to show that server-only code must not leak into the client bundle. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 008. The Request Lifecycle in Nuxt
**Section:** Learning path

Card title: The Request Lifecycle in Nuxt. Visual instructions: Show browser navigation entering a Nuxt app, route resolution, optional server data loading, HTML rendering, response delivery, hydration, and interactive client updates. Mark server-side and browser-side phases distinctly and keep it to one successful page request. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 009. HTML DOM: The Browser Tree
**Section:** Web foundations

Card title: HTML DOM: The Browser Tree. Visual instructions: Draw a small DOM tree with `document` at the root, then `html`, `body`, and a `button`. Label parent, child, and sibling. Show Vue rendering ultimately becomes DOM nodes, while Vue developers normally express structure in templates instead of manually constructing the tree. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 010. JavaScript Modules: import and export
**Section:** Web foundations

Card title: JavaScript Modules: import and export. Visual instructions: Show a helper module exporting `formatPrice` and a page importing it. Label export as “publish a value” and import as “reuse a value.” Include a tiny arrow from module A to module B and distinguish named exports from a default export with short examples. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 011. Promises and async/await
**Section:** Web foundations

Card title: Promises and async/await. Visual instructions: Show a request moving through pending → fulfilled or rejected. Under it, show `await fetchData()` inside `try/catch`. Explain that `await` pauses the async function, not the entire JavaScript runtime, and display success and error branches. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 012. The JavaScript Event Loop
**Section:** Web foundations

Card title: The JavaScript Event Loop. Visual instructions: Draw the call stack, task queue, microtask queue, and event loop as a simple flow. Use a short example ordering synchronous log → promise callback → timer callback. Keep the ordering correct: synchronous code first, promise microtasks before timer tasks in the common example. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 013. HTTP Request and Response
**Section:** Web foundations

Card title: HTTP Request and Response. Visual instructions: Show a browser sending method + URL + headers + optional body to an API. Show a response returning status code + headers + JSON body. Use `GET /api/projects` as the example and distinguish the HTTP envelope from the application data inside JSON. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 014. HTTP Methods and Intent
**Section:** Web foundations

Card title: HTTP Methods and Intent. Visual instructions: Make a compact comparison table/diagram for GET, POST, PUT, PATCH, and DELETE. Give one plain-language intent and one endpoint example for each. Highlight that GET should not mutate server state and that PUT generally replaces while PATCH partially updates. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 015. JSON Is Data, Not a Type System
**Section:** Web foundations

Card title: JSON Is Data, Not a Type System. Visual instructions: Show a JSON object flowing between frontend and backend, then a validation gate that checks required fields and types. Contrast “valid JSON syntax” with “valid application payload.” Include an example where a missing `email` property fails schema validation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 016. TypeScript: Static Checks vs. Runtime Validation
**Section:** Web foundations

Card title: TypeScript: Static Checks vs. Runtime Validation. Visual instructions: Show TypeScript checking source code at build time, while a runtime schema validates unknown data arriving from a network. Draw separate “compile-time” and “runtime” gates. Make clear that TypeScript types alone do not validate incoming JSON at runtime. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 017. Template Interpolation
**Section:** Vue templates

Card title: Template Interpolation. Visual instructions: Show a reactive `message` value flowing into `{{ message }}` and becoming visible text in the rendered page. Include one short binding example and label interpolation as text output, not raw HTML. Keep logic in the script and display in the template. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 018. Directive Syntax: v- Prefix
**Section:** Vue templates

Card title: Directive Syntax: v- Prefix. Visual instructions: Place `v-if`, `v-for`, `v-bind`, `v-on`, and `v-model` around a central template fragment. Give each directive one job label: condition, list, bind, event, form sync. Avoid listing every Vue directive; focus on the core mental model. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 019. v-if vs. v-show
**Section:** Vue templates

Card title: v-if vs. v-show. Visual instructions: Use a side-by-side comparison: `v-if` adds/removes an element from the DOM, while `v-show` keeps the element and toggles CSS display. Add a simple DOM sketch for each and a rule of thumb: infrequent toggles vs. frequent visibility toggles. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 020. v-for and Stable Keys
**Section:** Vue templates

Card title: v-for and Stable Keys. Visual instructions: Show a list of three project rows keyed by stable IDs. Contrast a stable `project.id` key with an array index key, then show how identity helps Vue reuse the correct DOM/component state when items reorder. Avoid portraying keys as a speed-only feature. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 021. Event Handling with v-on / @
**Section:** Vue templates

Card title: Event Handling with v-on / @. Visual instructions: Show a button click traveling to `@click="increment"`, then a handler updating reactive state, then the displayed count changing. Label event binding, handler, state mutation, DOM update. Add a tiny event modifier example only if space remains. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 022. Attribute Binding with v-bind / :
**Section:** Vue templates

Card title: Attribute Binding with v-bind / :. Visual instructions: Show reactive values bound to `:disabled`, `:href`, and `:class`. Draw arrows from script state to DOM attributes. Make the distinction clear: interpolation renders text, while `v-bind` supplies an attribute or component prop value. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 023. v-model: Form State Synchronization
**Section:** Vue templates

Card title: v-model: Form State Synchronization. Visual instructions: Show an input and a `name` ref connected in both directions: typing updates state, and state updates the input value. Add a separate small note that `v-model` behavior depends on the element or component. Keep the flow bidirectional. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 024. Class and Style Bindings
**Section:** Vue templates

Card title: Class and Style Bindings. Visual instructions: Show a button whose class changes when `isActive` is true and whose style uses a reactive color. Use a simple state → binding → visual result diagram. Include one object-style class binding and avoid turning the card into a CSS tutorial. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 025. Template Refs
**Section:** Vue templates

Card title: Template Refs. Visual instructions: Show a template element referenced by `ref="searchInput"`, then an `onMounted` step focusing that input. Label the ref as a handle to a rendered DOM element or child component. Make clear the element is unavailable before it has been mounted. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 026. Conditional Rendering with Empty, Loading, and Error States
**Section:** Vue templates

Card title: Conditional Rendering with Empty, Loading, and Error States. Visual instructions: Show one content region with three mutually exclusive states: loading spinner, error message, and successful data. Add the corresponding condition flow. Emphasize explicit UI states instead of leaving a blank screen during asynchronous work. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 027. Rendering Lists: Empty State and Keys
**Section:** Vue templates

Card title: Rendering Lists: Empty State and Keys. Visual instructions: Show a list rendering `items` with a stable key, plus a deliberate empty-state panel when the array has no entries. Connect data availability to either list or empty view. Teach that an empty list is a normal state, not necessarily an error. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 028. The Reactivity Mental Model
**Section:** Vue reactivity

Card title: The Reactivity Mental Model. Visual instructions: Draw reactive state read by a render/computed function, tracked as a dependency, then triggered when state changes. The output is scheduled for an update. Keep this as the core chain: read → track → mutate → trigger → update. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 029. ref(): Reactive Values
**Section:** Vue reactivity

Card title: ref(): Reactive Values. Visual instructions: Show `const count = ref(0)` as a wrapper with `.value`, plus a template where `count` is auto-unwrapped. Explain that JavaScript code generally uses `count.value` while templates can use `count`. Do not imply `ref` is limited to primitive values. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 030. reactive(): Reactive Objects
**Section:** Vue reactivity

Card title: reactive(): Reactive Objects. Visual instructions: Show a plain object passed through `reactive()` and represented as a proxy. Property reads are tracked and writes can trigger updates. Add a nested property example. Note visually that the reactive proxy is not strictly identical to the original raw object. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 031. ref vs. reactive
**Section:** Vue reactivity

Card title: ref vs. reactive. Visual instructions: Compare the two APIs in parallel. `ref` wraps any kind of value and uses `.value` in script; `reactive` proxies an object and exposes properties directly. Add a small practical rule: use `ref` as the default unless an object-shaped proxy is specifically useful. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 032. computed(): Derived State
**Section:** Vue reactivity

Card title: computed(): Derived State. Visual instructions: Show source values `price` and `quantity` flowing into `computed(() => price * quantity)`, producing `total`. Include a dependency arrow and label computed as cached derived state that recalculates when tracked dependencies change. Do not show side effects inside the getter. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 033. watch(): Respond to a Specific Source
**Section:** Vue reactivity

Card title: watch(): Respond to a Specific Source. Visual instructions: Show a `searchQuery` ref changing, a watcher reacting, and an asynchronous search request starting. Label source, callback, side effect. Emphasize that `watch` is for effects such as requests or synchronization, not ordinary derived values. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 034. watchEffect(): Auto-Tracked Dependencies
**Section:** Vue reactivity

Card title: watchEffect(): Auto-Tracked Dependencies. Visual instructions: Show a reactive value read inside `watchEffect`, with an automatically collected dependency arrow. When that value changes, the effect runs again. Compare it briefly to explicit-source `watch`, which makes the dependency source deliberate. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 035. Why Destructuring reactive() Can Lose Reactivity
**Section:** Vue reactivity

Card title: Why Destructuring reactive() Can Lose Reactivity. Visual instructions: Show `const state = reactive({ count: 0 })`, then destructuring `const { count } = state` into a disconnected plain local binding. In a second path show `toRef(state, "count")` preserving the reactive connection. Label the pitfall and fix. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 036. toRef and toRefs
**Section:** Vue reactivity

Card title: toRef and toRefs. Visual instructions: Draw a reactive object with `name` and `count`, then create refs that remain connected to the original properties. Show changing either the ref or the object updates the same underlying state. Clarify that this is useful when destructuring without severing reactivity. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 037. Deep vs. Shallow Reactivity
**Section:** Vue reactivity

Card title: Deep vs. Shallow Reactivity. Visual instructions: Show a nested object tree under `ref()` with deeply reactive nested values, versus `shallowRef()` where only replacement of `.value` is tracked automatically. Mention large immutable structures or externally managed state as a possible shallow-ref use case. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 038. nextTick(): Wait for the DOM Flush
**Section:** Vue reactivity

Card title: nextTick(): Wait for the DOM Flush. Visual instructions: Show state mutation at time T, Vue queues/batches a DOM update, then `await nextTick()` resumes after the DOM has been updated. Include a small before/after DOM label. Do not portray `nextTick` as waiting for arbitrary network requests. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 039. Batching and Update Scheduling
**Section:** Vue reactivity

Card title: Batching and Update Scheduling. Visual instructions: Show three synchronous state mutations coalescing into one scheduled render/update. Label “many writes” → “queued update” → “one render pass.” Explain that DOM updates are buffered rather than applied synchronously on every individual mutation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 040. Common Reactivity Pitfalls
**Section:** Vue reactivity

Card title: Common Reactivity Pitfalls. Visual instructions: Use three small warning/fix pairs: destructuring reactive properties, mutating the raw object instead of its proxy, and expecting DOM changes synchronously. Pair them with `toRef/toRefs`, use the proxy, and `nextTick` respectively. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 041. Component Boundaries and Single Responsibility
**Section:** Components

Card title: Component Boundaries and Single Responsibility. Visual instructions: Show a page decomposed into Header, SearchBar, ProjectList, and ProjectCard components. Draw clear parent-child nesting and assign one responsibility to each. Emphasize that components should expose intentional interfaces instead of sharing arbitrary internal implementation details. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 042. Props: Parent to Child Data
**Section:** Components

Card title: Props: Parent to Child Data. Visual instructions: Show a parent owning `project` data and passing it through a prop into `ProjectCard`. The child displays the project title but does not mutate the prop. Use a one-way arrow and label props as inputs. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 043. Emits: Child to Parent Events
**Section:** Components

Card title: Emits: Child to Parent Events. Visual instructions: Show a child button emitting `select` with a project ID and the parent listening with `@select`. Draw the event upward from child to parent. Distinguish the event notification from the actual parent-owned state update. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 044. Props and Emits: The Component Contract
**Section:** Components

Card title: Props and Emits: The Component Contract. Visual instructions: Show a component API card with two sides: props are incoming inputs; emits are outgoing events. Use `ProjectCard` as the example. Treat the component as a contract and keep internal local state separate from the public interface. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 045. Component v-model
**Section:** Components

Card title: Component v-model. Visual instructions: Show a parent value connected to a child component through `modelValue` and `update:modelValue` (or the corresponding `defineModel` abstraction). Draw a two-way synchronization loop and note that component `v-model` is a prop-plus-event contract, not magical shared memory. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 046. Slots: Parent-Supplied Content
**Section:** Components

Card title: Slots: Parent-Supplied Content. Visual instructions: Show a reusable `BaseCard` shell with a slot opening that receives content written by the parent. Label shell ownership vs. inserted content. Demonstrate why slots allow a reusable wrapper to support different child layouts without hardcoding every variant. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 047. Named and Scoped Slots
**Section:** Components

Card title: Named and Scoped Slots. Visual instructions: Show a component with `header`, default, and `footer` named slot regions. Add a scoped slot that passes a `project` value outward for the parent to render. Distinguish named placement from scoped data exposure, and keep labels concise. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 048. Fallthrough Attributes and $attrs
**Section:** Components

Card title: Fallthrough Attributes and $attrs. Visual instructions: Show an attribute such as `aria-label` or `class` passed to a wrapper component and forwarded to its root element. Mark the component boundary and the fallthrough path. Explain that attribute inheritance can need explicit handling when a component has multiple roots. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 049. provide / inject: Deep Dependency Sharing
**Section:** Components

Card title: provide / inject: Deep Dependency Sharing. Visual instructions: Show a top-level form provider exposing a shared form context to nested field components, bypassing repeated prop threading. Label provider, injected dependency, and reactive shared value. Include a small warning that this should be used for intentional subtree dependencies, not every state relationship. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 050. Dynamic Components
**Section:** Components

Card title: Dynamic Components. Visual instructions: Show a single `<component :is="currentView">` position switching among `ListView`, `GridView`, and `MapView`. Explain that a dynamic component chooses which component implementation is rendered. Keep the parent state and alternatives visible. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 051. Async Components and Lazy Loading
**Section:** Components

Card title: Async Components and Lazy Loading. Visual instructions: Show a feature button leading to a component chunk being loaded only when needed, then rendering the component. Distinguish lazy loading from merely hiding an already-loaded component. Use a small bundle diagram showing initial code vs. deferred chunk. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 052. Teleport and Modal Placement
**Section:** Components

Card title: Teleport and Modal Placement. Visual instructions: Show a modal component declared within a page component but its rendered DOM placed under a top-level `body` target. Draw separate component ownership and DOM placement. Explain the value for overlays, stacking contexts, and avoiding clipping. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 053. Lifecycle Hooks
**Section:** Components

Card title: Lifecycle Hooks. Visual instructions: Show the component timeline: setup → mount → update(s) → unmount. Attach `onMounted`, `onUpdated`, and `onUnmounted` to the appropriate phases. Keep the distinction clear between initialization, post-DOM-mount work, update observation, and cleanup. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 054. What Is a Composable?
**Section:** Composables

Card title: What Is a Composable?. Visual instructions: Show a reusable `useSearch()` function used by two unrelated components. It returns reactive query/results plus search behavior. Label it as reusable stateful logic rather than a UI component; both callers keep their own state unless the composable intentionally shares state. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 055. Extracting Logic into a Composable
**Section:** Composables

Card title: Extracting Logic into a Composable. Visual instructions: Show a component before extraction with fetching, loading, error, and cleanup logic crowded together; show the same behavior moved to `useProjects()` while the component focuses on rendering. Make clear that extraction improves reuse and organization, not automatic performance. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 056. Composable State Ownership
**Section:** Composables

Card title: Composable State Ownership. Visual instructions: Compare two instances of `useCounter()` creating isolated refs with a module-level shared ref used by all callers. Label per-call state vs. shared singleton state. Flag that shared module state needs special care in SSR to avoid cross-request user-data leakage. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 057. Lifecycle Cleanup in Composables
**Section:** Composables

Card title: Lifecycle Cleanup in Composables. Visual instructions: Show a composable registering an event listener or timer during setup, then removing it in `onUnmounted`. Use paired add/remove symbols and show the component leaving the page. The takeaway is to prevent stale listeners, timers, and memory leaks. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 058. Reusable Fetch State
**Section:** Composables

Card title: Reusable Fetch State. Visual instructions: Show `useProjects()` returning `data`, `pending`, `error`, and `refresh`. Connect request start, success, failure, and retry. Distinguish data state from view rendering, and note that Nuxt data composables should be used when SSR payload transfer or framework caching semantics matter. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 059. Watching Props Safely
**Section:** Composables

Card title: Watching Props Safely. Visual instructions: Show a prop such as `projectId` changing, a watcher receiving the new ID, and old async work being cancelled or ignored before starting the next request. Include a simple generation/token or cleanup marker to illustrate avoiding stale responses overwriting current data. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 060. Composables and Setup Context
**Section:** Composables

Card title: Composables and Setup Context. Visual instructions: Show `useRoute`, lifecycle hooks, and `provide/inject` being invoked within a valid component/setup context. Contrast with calling a context-dependent composable too late or in an unrelated module. Emphasize calling framework composables where their required context exists. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 061. Composable API Design
**Section:** Composables

Card title: Composable API Design. Visual instructions: Show a composable with a small, stable returned interface: reactive state refs plus named actions. Contrast a clear result object with exposing a large mutable internal object. Emphasize predictable naming, explicit inputs, cleanup, and testability. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 062. Testing a Composable
**Section:** Composables

Card title: Testing a Composable. Visual instructions: Show a composable as a small function under test with controlled inputs and asserted reactive outputs. Split examples into pure reactivity-only composables that can be called directly and lifecycle/injection-dependent composables that need a mounted host component. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 063. Avoid Side Effects in computed()
**Section:** Composables

Card title: Avoid Side Effects in computed(). Visual instructions: Show a computed getter deriving a total on one path and an incorrect computed getter that sends a network request on another. The correct separation uses computed for pure derived values and watch/watchEffect for side effects. Use a clear correct/incorrect comparison. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 064. Typed Props with defineProps
**Section:** TypeScript

Card title: Typed Props with defineProps. Visual instructions: Show a component receiving a typed `project` object and `compact?: boolean`. Connect the prop interface to template usage. Distinguish static type checking from runtime validation, and keep the example simple enough to read in one glance. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 065. Typed Emits with defineEmits
**Section:** TypeScript

Card title: Typed Emits with defineEmits. Visual instructions: Show an event contract `select(id: string)` and a parent handler receiving the same ID type. Label the event name and payload type. The teaching point is that typed emits catch mismatched event names or payloads during development. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 066. Types vs. Interfaces for App Models
**Section:** TypeScript

Card title: Types vs. Interfaces for App Models. Visual instructions: Show a `Project` model reused by a page, a component, and an API client. Include a few fields such as `id`, `name`, and `price`. Focus on one shared contract and avoid a debate about every difference between `type` and `interface`. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 067. Union Types for UI States
**Section:** TypeScript

Card title: Union Types for UI States. Visual instructions: Show `idle | loading | success | error` as four mutually exclusive variants. Each variant has the data it needs; success carries results, error carries a message. Explain that modeling states explicitly prevents contradictory combinations such as `loading=true` and `error` at once. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 068. Discriminated Unions
**Section:** TypeScript

Card title: Discriminated Unions. Visual instructions: Show a union with `kind: "success"` carrying `data` and `kind: "error"` carrying `message`. A branch on `kind` selects the valid fields. Make the relationship between discriminant and safe narrowing visually obvious. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 069. Typing Template Refs
**Section:** TypeScript

Card title: Typing Template Refs. Visual instructions: Show an input template ref typed as `HTMLInputElement | null`, a mount check, and a focus action. Explain that template refs can be absent before mount or after unmount; safe code must account for nullability. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 070. Type Inference vs. Explicit Annotations
**Section:** TypeScript

Card title: Type Inference vs. Explicit Annotations. Visual instructions: Show a value inferred from an initializer and an API payload requiring an explicit model or validation. Label “infer when obvious” and “annotate at boundaries.” Avoid suggesting every variable needs a redundant annotation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 071. Unknown vs. Any at Network Boundaries
**Section:** TypeScript

Card title: Unknown vs. Any at Network Boundaries. Visual instructions: Show untrusted JSON entering as `unknown`, then passing schema validation and becoming a typed model. Contrast `any`, which disables safety checks, with `unknown`, which forces narrowing before use. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 072. What the Vue Router Does
**Section:** Routing

Card title: What the Vue Router Does. Visual instructions: Show the URL `/projects/42` mapped to a route record, then the matching page component displayed in the router view. Label URL, route match, component. Distinguish client-side navigation from a full browser page reload. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 073. Dynamic Route Parameters
**Section:** Routing

Card title: Dynamic Route Parameters. Visual instructions: Show `/projects/:id` matching `/projects/42`, with `id = "42"` passed to the page logic. Highlight that route parameters are often strings and may need validation or conversion before being used as numeric identifiers. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 074. Query Parameters and Filters
**Section:** Routing

Card title: Query Parameters and Filters. Visual instructions: Show `/projects?city=ShahAlam&beds=3` turning into filter state, then into a result list. Distinguish query parameters, used for shareable/searchable view state, from path parameters, commonly used to identify a resource. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 075. Nested Routes and Nested Views
**Section:** Routing

Card title: Nested Routes and Nested Views. Visual instructions: Show a parent `/settings` route with a nested router view that swaps among Profile, Security, and Notifications while keeping the settings shell. Label the parent layout and child route. Make nesting distinct from merely placing components inside a template. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 076. Navigation Guards
**Section:** Routing

Card title: Navigation Guards. Visual instructions: Show a navigation request passing an authentication/authorization guard before reaching a protected route. The guard can allow, redirect, or cancel navigation. Note that client-side guards improve navigation UX but do not replace server-side authorization. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 077. Lazy Route Components
**Section:** Routing

Card title: Lazy Route Components. Visual instructions: Show route navigation loading only the JavaScript chunk for the requested page. Contrast initial bundle with a deferred page chunk. Explain that route-level lazy loading can reduce initial JavaScript, while too many tiny chunks can create network overhead. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 078. Route Metadata
**Section:** Routing

Card title: Route Metadata. Visual instructions: Show a route record annotated with `requiresAuth`, title, and breadcrumb metadata, which is read by navigation logic and layout UI. Label metadata as descriptive route configuration, not a security boundary by itself. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 079. 404 and Navigation Error Handling
**Section:** Routing

Card title: 404 and Navigation Error Handling. Visual instructions: Show an unmatched URL entering a fallback route and a navigation failure being reported. Distinguish “route does not exist” from “request/data loading failed.” Include a clear path back to a valid page. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 080. Local State vs. Shared State
**Section:** State management

Card title: Local State vs. Shared State. Visual instructions: Show a component-local toggle owned by one component and a shared user/session state consumed by multiple pages. Draw local state as a small box and global state as a shared store. Emphasize using the narrowest scope that satisfies the requirement. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 081. Pinia Store Anatomy
**Section:** State management

Card title: Pinia Store Anatomy. Visual instructions: Show a Pinia store divided into state, getters, and actions. Use a `cart` example: items in state, `total` as a getter, and `addItem` as an action. Show two components consuming the same store instance within the app. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 082. storeToRefs()
**Section:** State management

Card title: storeToRefs(). Visual instructions: Show a Pinia store being destructured: actions remain callable methods, while reactive state/getters are extracted with `storeToRefs`. Contrast safe reactive extraction with plain destructuring that can break the store property connection. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 083. Server State vs. Client UI State
**Section:** State management

Card title: Server State vs. Client UI State. Visual instructions: Compare server-owned data such as project records and user profile with client-only UI state such as open tabs and temporary modal visibility. Show a server fetch/cache layer separately from Pinia/local UI state. Avoid putting every response in a global store by default. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 084. Avoid Duplicate Sources of Truth
**Section:** State management

Card title: Avoid Duplicate Sources of Truth. Visual instructions: Show one canonical `selectedProjectId` driving a selected item and detail panel. Contrast it with separate copied values that drift out of sync. The takeaway is to store the minimum canonical state and derive views from it. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 085. Persisting State Safely
**Section:** State management

Card title: Persisting State Safely. Visual instructions: Show a preference such as theme saved to local storage, while session secrets remain in secure cookie/session mechanisms rather than arbitrary browser storage. Mark which values are appropriate for persistence and which should not be stored client-side. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 086. State Isolation Under SSR
**Section:** State management

Card title: State Isolation Under SSR. Visual instructions: Show two simultaneous server requests from User A and User B. Each receives an isolated state container. Cross the wires in the “bad” example where one module-level mutable user store leaks information across requests. Emphasize per-request state isolation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 087. State Machines for Complex UI
**Section:** State management

Card title: State Machines for Complex UI. Visual instructions: Show an upload process as idle → uploading → success or error, with allowed transitions and retry. Explain that explicit states and transitions prevent impossible UI combinations. Keep the example to one finite state machine and four or five states. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 088. Nuxt 4 Directory Map
**Section:** Nuxt foundations

Card title: Nuxt 4 Directory Map. Visual instructions: Draw a simplified project tree with `app/` for Vue application code, `server/` for server handlers/utilities, `shared/` for code intended for both sides, and `nuxt.config.ts` for configuration. Include only representative folders; emphasize that Nuxt conventions generate wiring. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 089. File-Based Routing in Nuxt
**Section:** Nuxt foundations

Card title: File-Based Routing in Nuxt. Visual instructions: Show files under `app/pages/` automatically becoming URLs: `index.vue` → `/`, `about.vue` → `/about`, and `projects/[id].vue` → `/projects/:id`. Keep a small file tree on the left and a route map on the right. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 090. Nuxt Layouts
**Section:** Nuxt foundations

Card title: Nuxt Layouts. Visual instructions: Show `app/layouts/default.vue` as a reusable shell containing header, page slot, and footer. Two different pages fill the same slot. Add a separate named admin layout to show that routes can opt into a different shell. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 091. app.vue and the Root Application
**Section:** Nuxt foundations

Card title: app.vue and the Root Application. Visual instructions: Show `app.vue` wrapping the rendered page/layout and the main Nuxt rendering outlet. Distinguish the root application from route page components and reusable components. Keep it focused on the app composition boundary. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 092. Auto-Imports
**Section:** Nuxt foundations

Card title: Auto-Imports. Visual instructions: Show `ref`, a component, and `useProjects` used without explicit import statements because Nuxt auto-imports eligible Vue APIs and project conventions. Add a small note that auto-importing is framework-managed resolution, not arbitrary global state; generated typings support editor assistance. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 093. Nuxt Plugins
**Section:** Nuxt foundations

Card title: Nuxt Plugins. Visual instructions: Show a plugin initializing a shared app capability, such as an API client, and making it available to components through Nuxt app context. Distinguish plugin initialization from route middleware and server API handlers. Avoid using a plugin for ordinary component-only logic. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 094. nuxt.config.ts
**Section:** Nuxt foundations

Card title: nuxt.config.ts. Visual instructions: Show configuration flowing into modules, runtime behavior, build settings, and route/render rules. Separate build-time/configuration values from runtime secrets. Use three labeled configuration concerns rather than listing every option. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 095. Nuxt Modules
**Section:** Nuxt foundations

Card title: Nuxt Modules. Visual instructions: Show a Nuxt module adding a feature by registering components, hooks, configuration defaults, or server handlers during setup. Distinguish a module as framework-level integration from a runtime plugin and a regular composable. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 096. app/ vs. server/ vs. shared/
**Section:** Nuxt foundations

Card title: app/ vs. server/ vs. shared/. Visual instructions: Create three columns. `app/`: pages, Vue components, client-facing app logic. `server/`: API routes, middleware, server utilities and secrets. `shared/`: carefully chosen cross-environment code such as compatible types and pure helpers. Add a warning not to import server-only dependencies into app code. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 097. Assets vs. Public Files
**Section:** Nuxt foundations

Card title: Assets vs. Public Files. Visual instructions: Show `app/assets/` source files passing through the build pipeline, while `public/` files are served at stable paths without being imported through the asset pipeline. Compare a processed stylesheet/image with a fixed public favicon or robots.txt. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 098. Environment Variables and Runtime Config
**Section:** Nuxt foundations

Card title: Environment Variables and Runtime Config. Visual instructions: Show private server runtime config on the server and explicitly public config exposed to the browser. Place database password in the private zone and public API base URL in public config. Emphasize that a variable is not safe just because it came from an environment file. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 099. Route Middleware vs. Server Middleware
**Section:** Nuxt foundations

Card title: Route Middleware vs. Server Middleware. Visual instructions: Show route middleware running during app navigation to decide where the user should navigate, while server middleware runs on incoming server requests for request-level handling. Distinguish both from authorization checks inside the API handler. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 100. CSR: Client-Side Rendering
**Section:** Rendering and SSR

Card title: CSR: Client-Side Rendering. Visual instructions: Show the server returning a minimal document and JavaScript bundle, then the browser fetching data and creating the UI. Label client render, JavaScript download, and content appearance. Include the main trade-off: app-like interaction, but initial content can depend on client loading. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 101. SSR: Server-Side Rendering
**Section:** Rendering and SSR

Card title: SSR: Server-Side Rendering. Visual instructions: Show a request reaching the server, Vue rendering HTML on the server, and the browser receiving meaningful page markup before client JavaScript hydrates it. Keep server rendering and later client interactivity as two distinct phases. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 102. SSG / Prerendering
**Section:** Rendering and SSR

Card title: SSG / Prerendering. Visual instructions: Show a build-time process generating static HTML files for known routes, then a CDN serving those files directly. Distinguish build-time rendering from request-time SSR. Note that purely static output is most suitable when pages do not require per-request server computation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 103. Hybrid Rendering and Route Rules
**Section:** Rendering and SSR

Card title: Hybrid Rendering and Route Rules. Visual instructions: Show three routes with different policies: a marketing page prerendered, a dashboard rendered dynamically, and a public catalog cached for a short period. Connect each route to its render/cache policy. Teach that one app can use different strategies by route. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 104. Hydration: HTML Becomes Interactive
**Section:** Rendering and SSR

Card title: Hydration: HTML Becomes Interactive. Visual instructions: Show server-rendered HTML arriving in the browser, client JavaScript loading the matching component tree, and Vue attaching behavior to existing DOM. Highlight event handlers becoming interactive. Distinguish hydration from a completely new client render. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 105. Hydration Mismatch
**Section:** Rendering and SSR

Card title: Hydration Mismatch. Visual instructions: Show server output containing one value and client output containing a different value, producing a mismatch warning. Use time/random/browser-only state as the cause. Show the fix direction: make initial server/client output deterministic, then read browser-only state after mount if appropriate. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 106. Why window Is Undefined During SSR
**Section:** Rendering and SSR

Card title: Why window Is Undefined During SSR. Visual instructions: Show server-side execution with no browser `window` or `document`, versus client-side browser execution where those globals exist. Place DOM-only code inside an appropriate client-only lifecycle or client-only boundary. Do not imply every composable automatically runs only in the browser. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 107. useState() for SSR-Safe Shared State
**Section:** Rendering and SSR

Card title: useState() for SSR-Safe Shared State. Visual instructions: Show one request-scoped Nuxt `useState` key reused by two components during the same app render. Contrast with a module-level mutable singleton shared accidentally across server requests. Mark serialization-safe values and avoid storing secrets in client-hydrated state. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 108. ClientOnly Components
**Section:** Rendering and SSR

Card title: ClientOnly Components. Visual instructions: Show a browser-dependent widget such as a map/chart rendered only on the client, while surrounding page content can still be server rendered. Label the client-only boundary and fallback. Explain that client-only rendering trades initial content/SEO of that widget for compatibility. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 109. SEO Metadata per Page
**Section:** Rendering and SSR

Card title: SEO Metadata per Page. Visual instructions: Show a Nuxt page defining title, description, and canonical-related metadata, then the rendered document head. Distinguish page-specific metadata from a global default. Emphasize meaningful unique content and metadata rather than merely adding tags mechanically. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 110. Caching: HTML, Data, and Browser Assets
**Section:** Rendering and SSR

Card title: Caching: HTML, Data, and Browser Assets. Visual instructions: Draw three separate cache layers: rendered route/HTML, fetched data, and static JS/CSS/image assets. For each, show what is stored and invalidation/expiry as a control. Emphasize that caching policy must respect user-specific data and freshness requirements. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 111. useFetch vs. useAsyncData vs. $fetch
**Section:** Data fetching

Card title: useFetch vs. useAsyncData vs. $fetch. Visual instructions: Create three adjacent lanes: `useFetch` for straightforward URL-based SSR-aware fetching; `useAsyncData` for controlled async logic and keys; `$fetch` for event-driven requests such as form submission. Include the rule not to substitute one blindly for all use cases. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 112. SSR Data Payload Transfer
**Section:** Data fetching

Card title: SSR Data Payload Transfer. Visual instructions: Show Nuxt fetching data on the server, placing serializable results into the rendered payload, and the browser reusing that data during hydration rather than repeating the same request unnecessarily. Mark server fetch, payload transfer, client reuse. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 113. pending, data, error
**Section:** Data fetching

Card title: pending, data, error. Visual instructions: Show an async-data resource as a state box with `pending`, `data`, and `error`, changing from pending to success or failure. Connect each state to a UI: loading, content/empty state, or error/retry. Avoid treating null data as always equivalent to a failure. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 114. Reactive Fetch Inputs
**Section:** Data fetching

Card title: Reactive Fetch Inputs. Visual instructions: Show a route parameter or filter ref feeding a `useFetch` URL/options, then a change causing a new request or reactive refresh. Mark the source dependency and result update. Distinguish deliberate reactive inputs from manual refresh after a user action. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 115. refresh, execute, and clear
**Section:** Data fetching

Card title: refresh, execute, and clear. Visual instructions: Show a loaded async-data result with three controls: refresh revalidates the request, execute triggers an execution depending on options, and clear resets the keyed async data state. Keep semantics high-level and avoid inventing option details not shown in the current API. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 116. Request Deduplication and Async Keys
**Section:** Data fetching

Card title: Request Deduplication and Async Keys. Visual instructions: Show two components requesting the same keyed async resource and a single in-flight request serving both. A different key represents different resource inputs. Explain that keys identify cached/shared async data and must represent meaningful input differences. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 117. Transform and Pick API Data
**Section:** Data fetching

Card title: Transform and Pick API Data. Visual instructions: Show a large server payload passing through a transform/pick stage into a smaller client-facing result. Use a projects array with only `id`, `name`, and `price` retained. Explain reduced payload size and cleaner component data contracts, not security through field omission alone. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 118. Avoiding Waterfall Requests
**Section:** Data fetching

Card title: Avoiding Waterfall Requests. Visual instructions: Compare sequential requests A → B → C with independent requests A and B launched together, followed by a combined render. Show dependency arrows only when B truly requires A. The goal is to reduce unnecessary total latency without parallelizing dependent operations incorrectly. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 119. Pagination and Incremental Loading
**Section:** Data fetching

Card title: Pagination and Incremental Loading. Visual instructions: Show a page fetching rows 1–20 and a Next action fetching 21–40, with page state, total/hasMore, and loading indicator. Distinguish pagination from fetching all rows and filtering in the browser. Include an empty/end-of-list state. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 120. Mutation Then Refresh
**Section:** Data fetching

Card title: Mutation Then Refresh. Visual instructions: Show a user submitting an update via `$fetch`, the server confirming success, then the UI refreshing the relevant query or updating its cache. Add error handling and disable/re-enable the submit control. Make the request lifecycle explicit. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 121. Nitro: Nuxt Server Runtime
**Section:** Nuxt server

Card title: Nitro: Nuxt Server Runtime. Visual instructions: Show Nitro as the server runtime layer receiving HTTP requests and running API handlers, server middleware, and server utilities, then producing a response. Put the database/service code behind the endpoint. Distinguish the runtime from Vue’s browser reactivity engine. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 122. File-Based Server API Routes
**Section:** Nuxt server

Card title: File-Based Server API Routes. Visual instructions: Show files such as `server/api/projects.get.ts` and `server/api/projects.post.ts` mapping to HTTP endpoint behavior under `/api/projects`. Include the handler, request, and response. Explain that naming conventions create routes and methods, while exact route naming follows Nuxt conventions. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 123. Reading Query Parameters
**Section:** Nuxt server

Card title: Reading Query Parameters. Visual instructions: Show `GET /api/projects?city=ShahAlam&page=2` entering a handler, parsing query values, validating types/ranges, then calling the service layer. Emphasize that query parameters begin as untrusted strings and should be normalized before database use. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 124. Reading Route Parameters
**Section:** Nuxt server

Card title: Reading Route Parameters. Visual instructions: Show `/api/projects/42` entering a dynamic server route, extracting the ID, validating it, then calling `getProjectById`. Return a clear not-found response when no record exists. Distinguish route-param parsing from authorization. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 125. Reading and Validating Request Bodies
**Section:** Nuxt server

Card title: Reading and Validating Request Bodies. Visual instructions: Show a POST request JSON body crossing a schema-validation gate before business logic runs. Invalid payloads return a 400/422-style client error; valid payloads proceed. Emphasize server validation even when TypeScript types are present in the frontend. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 126. HTTP Status Codes for APIs
**Section:** Nuxt server

Card title: HTTP Status Codes for APIs. Visual instructions: Show a compact decision map: 200 success, 201 created, 204 no content, 400/422 invalid input, 401 unauthenticated, 403 forbidden, 404 missing, 409 conflict, 500 unexpected server error. Use only short meanings and stress consistent status semantics. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 127. Separate Route Handler, Service, and Repository
**Section:** Nuxt server

Card title: Separate Route Handler, Service, and Repository. Visual instructions: Draw `HTTP handler → service/business rules → repository/database`. Label the handler as protocol/input/output, service as policy/workflow, repository as persistence. Show why this separation makes endpoints easier to test and prevents database logic from spreading into route files. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 128. Server-Only Utilities
**Section:** Nuxt server

Card title: Server-Only Utilities. Visual instructions: Show a database connection and secret-bearing API client located in server utilities, imported by a server API handler, but inaccessible to browser components. Mark the dependency direction and a red boundary around private server dependencies. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 129. Server Middleware
**Section:** Nuxt server

Card title: Server Middleware. Visual instructions: Show every incoming request passing through a lightweight middleware stage for request IDs or logging before reaching a route handler. Distinguish request-wide processing from endpoint-specific validation and business logic. Avoid placing expensive database workflows in global middleware. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 130. Error Handling in API Routes
**Section:** Nuxt server

Card title: Error Handling in API Routes. Visual instructions: Show a handler that maps known domain failures to appropriate HTTP errors and unexpected exceptions to a generic server failure. Separate safe client-facing messages from detailed internal logs. Do not expose stack traces, database errors, or secrets in production responses. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 131. File Upload Flow
**Section:** Nuxt server

Card title: File Upload Flow. Visual instructions: Show browser file selection → multipart upload → size/type validation → temporary storage or object storage → database metadata record → response. Include limits and scanning/verification as gate checks. Distinguish uploaded file bytes from metadata saved in the database. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 132. Server API Is Not a Database Proxy
**Section:** Nuxt server

Card title: Server API Is Not a Database Proxy. Visual instructions: Show a naive endpoint returning a raw database row on one side and a deliberately designed response DTO on the other. Include field selection, authorization, normalization, and safe errors. Teach that an API endpoint should enforce domain policy, not blindly mirror tables. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 133. Input Validation at Every Trust Boundary
**Section:** Data and security

Card title: Input Validation at Every Trust Boundary. Visual instructions: Show three validation gates: browser form validation for UX, server schema validation for correctness, and database constraints for integrity. Place untrusted input entering the server. Emphasize that client validation is bypassable and database constraints protect invariants under concurrent writers. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 134. Authentication vs. Authorization
**Section:** Data and security

Card title: Authentication vs. Authorization. Visual instructions: Show authentication establishing who the user is, followed by authorization deciding whether that user can read/update a specific project. Use user identity + resource ownership/role → allow or deny. Make clear that knowing the user is not sufficient permission to access every resource. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 135. Cookie Session Flow
**Section:** Data and security

Card title: Cookie Session Flow. Visual instructions: Show login establishing a server-side session and sending a cookie with secure attributes; later requests include the cookie and the server validates the session. Mark HttpOnly, Secure, and SameSite as relevant cookie attributes. Do not draw the raw session secret as exposed to JavaScript. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 136. CSRF: Trusting Ambient Cookies
**Section:** Data and security

Card title: CSRF: Trusting Ambient Cookies. Visual instructions: Show a browser automatically attaching an authenticated cookie to a state-changing request, and an attacker-controlled page attempting to trigger it. Add defense labels such as SameSite, CSRF token/origin checks where appropriate. Keep the threat and defense logically accurate. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 137. XSS and Unsafe HTML
**Section:** Data and security

Card title: XSS and Unsafe HTML. Visual instructions: Show untrusted text safely rendered as text, contrasted with dangerous raw HTML insertion via `v-html`. Draw a malicious script-like string being escaped in the safe case and interpreted as markup in the unsafe case. Highlight sanitization and avoiding raw HTML for untrusted content. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 138. SQL Injection
**Section:** Data and security

Card title: SQL Injection. Visual instructions: Show unsafe SQL formed by concatenating user input into a query, contrasted with a parameterized query where SQL structure and values are kept separate. Use a search field as the source. The takeaway is never to interpolate untrusted values directly into SQL text. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 139. CORS Is Not Authorization
**Section:** Data and security

Card title: CORS Is Not Authorization. Visual instructions: Show a browser origin requesting a server API and the server’s CORS response controlling whether browser JavaScript may read the response. Separately show an authorization gate protecting the resource. Clarify that CORS does not stop non-browser clients or replace identity/permission checks. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 140. Secrets and Public Runtime Config
**Section:** Data and security

Card title: Secrets and Public Runtime Config. Visual instructions: Show private DB credentials and server API keys inside server-only runtime config, while only intentionally public configuration reaches client bundles. Mark build output/browser DevTools as places where exposed secrets can be recovered. Emphasize secret minimization and rotation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 141. Authorization at Resource Level
**Section:** Data and security

Card title: Authorization at Resource Level. Visual instructions: Show User A requesting Project A (allowed) and Project B (denied) even though both requests are authenticated. Use an owner/tenant check in the service or query. Emphasize that hiding a UI button is not authorization. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 142. Rate Limiting
**Section:** Data and security

Card title: Rate Limiting. Visual instructions: Show repeated requests from a client hitting a quota bucket, followed by throttling or a 429 response when the limit is exceeded. Label keying strategy, time window, and retry guidance. Explain that rate limiting helps reduce abuse and resource exhaustion but must fit legitimate traffic patterns. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 143. File Upload Security
**Section:** Data and security

Card title: File Upload Security. Visual instructions: Show a file crossing checks for size limit, allowed format, actual content/type validation, filename normalization, storage isolation, and optional malware scanning. Put executable files and path traversal in a blocked zone. Do not trust the filename extension alone. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 144. Database Transactions
**Section:** Data and security

Card title: Database Transactions. Visual instructions: Show a multi-step operation inside `BEGIN → statements → COMMIT`, with a failure path to `ROLLBACK`. Use a transfer or multi-row order update. Emphasize all-or-nothing consistency and that transactions do not automatically solve every race condition. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 145. Indexes and Query Plans
**Section:** Data and security

Card title: Indexes and Query Plans. Visual instructions: Show a table scan examining many rows versus an index lookup narrowing to matching rows, followed by row retrieval. Label read speed vs. write/storage cost. Add `EXPLAIN` as the inspection step; avoid implying every index always improves a query. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 146. Database Migrations
**Section:** Data and security

Card title: Database Migrations. Visual instructions: Show schema versions progressing from migration 001 to 002 to 003, with code release aligned to compatible schema changes. Distinguish a repeatable schema migration from manually editing production tables. Mention backups and staged/expand-contract migrations for risky changes. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 147. A Robust Form State Model
**Section:** UI patterns

Card title: A Robust Form State Model. Visual instructions: Show a form split into values, validation errors, submitting state, server error, and success. Connect submit to validation then request then outcome. Keep field-level errors near inputs and demonstrate that loading/disabled behavior should prevent duplicate submissions. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 148. Client Validation vs. Server Validation
**Section:** UI patterns

Card title: Client Validation vs. Server Validation. Visual instructions: Show immediate client-side feedback for a missing email, then server-side validation for the authoritative payload. A forged request bypasses the client but is rejected by the server. Label UX convenience vs. security/correctness enforcement. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 149. Modal Dialog State and Focus
**Section:** UI patterns

Card title: Modal Dialog State and Focus. Visual instructions: Show closed → open dialog → focus moves inside → Escape/close → focus returns to trigger. Include backdrop, accessible title, and focus containment as behaviors. Distinguish visual display from complete keyboard-accessible dialog behavior. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 150. Accessibility: Semantic HTML
**Section:** UI patterns

Card title: Accessibility: Semantic HTML. Visual instructions: Compare a real `<button>` with a clickable `<div>`. Show keyboard activation, focusability, and role semantics working automatically for the button. The main takeaway is to start with native semantic elements before adding ARIA or custom interaction code. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 151. Keyboard Navigation and Focus Order
**Section:** UI patterns

Card title: Keyboard Navigation and Focus Order. Visual instructions: Show a user tabbing through a logical sequence: link → input → button → dialog controls. Mark visible focus and a skipped decorative item. Emphasize that every interactive control should be reachable and operable by keyboard with a predictable focus order. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 152. ARIA Labels and Live Feedback
**Section:** UI patterns

Card title: ARIA Labels and Live Feedback. Visual instructions: Show an icon-only button with an accessible name, and a form success/error message announced through an appropriate live region. Distinguish visual labels from accessible names and dynamic announcements. Keep ARIA purposeful rather than adding redundant attributes to semantic HTML. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 153. Responsive Layout as Progressive Reflow
**Section:** UI patterns

Card title: Responsive Layout as Progressive Reflow. Visual instructions: Show a card layout changing from one column on a narrow viewport to two/three columns on larger screens. Keep content order stable and controls usable at all widths. Focus on responsive structure, not pixel-perfect screenshot breakpoints. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 154. Loading, Empty, Error, and Success UX
**Section:** UI patterns

Card title: Loading, Empty, Error, and Success UX. Visual instructions: Show a four-state card set for the same data region: skeleton/loading, deliberate empty message, retryable error, and successful content. Connect each state to the same resource. Emphasize that resilient interfaces model all outcomes, not only the happy path. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 155. Optimistic UI Updates
**Section:** UI patterns

Card title: Optimistic UI Updates. Visual instructions: Show an item toggled immediately in the UI while a server request is pending, followed by confirmation or rollback on failure. Label optimistic state, server confirmation, and rollback. Mention that this pattern suits reversible, low-risk operations more than high-impact transactions. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 156. Debounced Search
**Section:** UI patterns

Card title: Debounced Search. Visual instructions: Show keystrokes arriving rapidly, a debounce timer resetting, and only one request sent after typing pauses. Compare with firing a request for every keypress. Include cancellation or stale-response handling so earlier responses do not overwrite the newest query. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 157. The Testing Pyramid for Vue and Nuxt
**Section:** Testing and debugging

Card title: The Testing Pyramid for Vue and Nuxt. Visual instructions: Show three levels: unit tests for pure logic/composables, component tests for rendered UI and interactions, and E2E tests for real navigation/API workflows. Use a broad unit-test base and fewer full-stack E2E tests, while noting that each level covers different failures. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 158. Unit Test a Pure Function
**Section:** Testing and debugging

Card title: Unit Test a Pure Function. Visual instructions: Show input fixtures entering a deterministic function and expected output checked by assertions. Use a formatter or calculation with no DOM/network. Emphasize fast isolated feedback and test boundaries/edge cases rather than implementation details. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 159. Component Tests: Public Behavior
**Section:** Testing and debugging

Card title: Component Tests: Public Behavior. Visual instructions: Show mounting a Vue component with props, interacting through its visible button/input, and asserting rendered output or emitted events. Avoid peeking at private internal state. The test should resemble how a user observes and uses the component. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 160. Testing Composables with Lifecycle Hooks
**Section:** Testing and debugging

Card title: Testing Composables with Lifecycle Hooks. Visual instructions: Compare directly testing a reactivity-only composable with testing a lifecycle/provide-inject composable through a mounted host component. Show setup, assertions, and unmount cleanup. Make the host component need specific, not automatic for all composables. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 161. Testing a Nuxt Server API
**Section:** Testing and debugging

Card title: Testing a Nuxt Server API. Visual instructions: Show an HTTP request entering a test server handler with valid and invalid payloads, then assert status code and response shape. Include mocked or isolated persistence where appropriate. Focus on API contract and authorization behavior rather than testing private helper implementation only. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 162. End-to-End Test Flow
**Section:** Testing and debugging

Card title: End-to-End Test Flow. Visual instructions: Show Playwright opening the app, logging in with a test account, creating an item, and verifying it appears after navigation/reload. Mark browser, real route, server/API, and database layers. Keep setup deterministic and avoid relying on production data. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 163. Reproducing a Hydration Bug
**Section:** Testing and debugging

Card title: Reproducing a Hydration Bug. Visual instructions: Show a failing page with different server and browser values, then a minimal reproduction capturing the route, expected HTML, actual DOM, and console warning. The goal is to isolate the mismatch before trying random changes. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 164. Debugging the Data Path
**Section:** Testing and debugging

Card title: Debugging the Data Path. Visual instructions: Show a request traced through UI input → composable/data-fetch function → API route → service → SQL query → response → UI state. Place logs/breakpoints at boundaries and attach a request ID. Teach systematic layer-by-layer isolation. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 165. Client Error vs. Server Error
**Section:** Testing and debugging

Card title: Client Error vs. Server Error. Visual instructions: Draw separate client console/network errors and server terminal/log errors connected by one request ID. Show a browser-visible generic message and a detailed server log. Emphasize that a failed UI can originate from serialization, request, runtime, or persistence layers. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 166. Stale Async Response Race
**Section:** Testing and debugging

Card title: Stale Async Response Race. Visual instructions: Show request A for query “vu” taking longer than request B for “vue”; B returns first, then A returns late. Cross out A’s stale result and show cancellation, request ID, or latest-only logic. The displayed results must match the newest input. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 167. Debugging a Missing Auto-Import
**Section:** Testing and debugging

Card title: Debugging a Missing Auto-Import. Visual instructions: Show a symbol used in a `.vue` file, generated Nuxt type/import metadata, and a failed build if the symbol is outside the scanned convention or named incorrectly. Check directory/configuration and generated types before assuming Vue runtime reactivity is broken. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 168. Production Error Observability
**Section:** Testing and debugging

Card title: Production Error Observability. Visual instructions: Show an error moving from user request to structured server log, request ID, metrics/alert, and a sanitized user response. Include severity and enough context for diagnosis without exposing tokens, personal data, or secrets. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 169. Measure Before Optimizing
**Section:** Performance

Card title: Measure Before Optimizing. Visual instructions: Show a performance profile with a measured slow operation highlighted, then a focused fix and a second measurement. Label baseline, bottleneck, change, and verification. Emphasize measuring actual user-facing latency and bundle/runtime costs before choosing an optimization. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 170. Bundle Splitting and Lazy Loading
**Section:** Performance

Card title: Bundle Splitting and Lazy Loading. Visual instructions: Show a small initial JavaScript bundle loading core app code and optional feature bundles fetched on navigation/interaction. Contrast eager import with dynamic/lazy import. Include the trade-off: faster first load versus additional network round trips when deferred code is needed. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 171. Avoid Unnecessary Deep Reactivity
**Section:** Performance

Card title: Avoid Unnecessary Deep Reactivity. Visual instructions: Show a large immutable dataset wrapped deeply on the left and a shallow/non-reactive data strategy on the right when nested mutation is unnecessary. Label tracking overhead vs. update control. Avoid presenting shallow refs as a universal replacement for ordinary refs. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 172. List Rendering and Stable Identity
**Section:** Performance

Card title: List Rendering and Stable Identity. Visual instructions: Show a reordered list retaining component identity through stable keys, compared with index keys causing state to attach to the wrong row. Include an input inside rows to make the bug obvious. Focus on correctness and DOM reuse, not microbenchmark claims. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 173. Virtual Scrolling
**Section:** Performance

Card title: Virtual Scrolling. Visual instructions: Show 10,000 logical rows with only a small visible window mounted in the DOM. A scrollbar represents the full list while a viewport renders visible rows plus a buffer. Explain reduced DOM/layout work for very large lists and the complexity trade-off. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 174. Computed Caching vs. Recomputing
**Section:** Performance

Card title: Computed Caching vs. Recomputing. Visual instructions: Show an expensive derived filter depending on reactive source state. `computed` reuses the cached result until dependencies change, while a repeated method call recalculates when evaluated. Emphasize computed for pure derived state and measure before optimizing small calculations. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 175. Avoid Request Waterfalls
**Section:** Performance

Card title: Avoid Request Waterfalls. Visual instructions: Show two independent API calls executed sequentially vs. concurrently, with elapsed timelines. Place dependent calls in a separate note: parallelize only independent work. Tie the technique to page startup latency and server-side data loading. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 176. Image and Asset Optimization
**Section:** Performance

Card title: Image and Asset Optimization. Visual instructions: Show an oversized source image transformed into appropriately sized, compressed responsive variants, with lazy loading below the fold. Label bytes transferred, dimensions, and loading priority. Keep image optimization separate from JavaScript bundle optimization. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 177. Caching and Invalidation Trade-Offs
**Section:** Performance

Card title: Caching and Invalidation Trade-Offs. Visual instructions: Show a cache hit serving a recent result quickly and an invalidation/update event after data changes. Label TTL, stale data risk, and cache scope. Explain that cache correctness depends on the data’s freshness needs and whether the response is user-specific. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 178. Profile Re-Renders and Watchers
**Section:** Performance

Card title: Profile Re-Renders and Watchers. Visual instructions: Show an interaction triggering a component update and a profiler locating unnecessary work. Trace dependencies and watcher side effects. Avoid claiming Vue requires manual memoization everywhere; optimize the measured expensive path and reduce overly broad dependencies. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 179. Nuxt Build Output and Runtime
**Section:** Deployment and operations

Card title: Nuxt Build Output and Runtime. Visual instructions: Show source modules passing through compile/bundle/build, producing server output plus static assets. At runtime, the hosting platform executes the generated server entry and serves assets. Distinguish development server behavior from production deployment artifacts. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 180. SSR Server vs. Static Hosting
**Section:** Deployment and operations

Card title: SSR Server vs. Static Hosting. Visual instructions: Compare a deployed SSR application needing a compatible server/runtime with a prerendered static site served from object storage/CDN. Show the capabilities and limits of each, including per-request server logic versus static route output. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 181. Environment-Specific Configuration
**Section:** Deployment and operations

Card title: Environment-Specific Configuration. Visual instructions: Show local development, test, staging, and production environments with different URLs/credentials supplied through configuration. Keep secrets out of source control and client output. Emphasize validated configuration at startup and explicit differences between build-time and runtime values. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 182. Dockerized Nuxt App
**Section:** Deployment and operations

Card title: Dockerized Nuxt App. Visual instructions: Show a multi-stage Docker build: dependency install and compile in a build stage, then only required runtime output in a smaller final image. Label dependency/build artifacts, runtime user, exposed port, and environment configuration. Avoid embedding secrets in image layers. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 183. CI/CD Pipeline for Nuxt
**Section:** Deployment and operations

Card title: CI/CD Pipeline for Nuxt. Visual instructions: Show commit → lint/typecheck → unit/component tests → production build → artifact/image → deployment → smoke test. Use a failing quality gate to block release. Keep credentials in the CI secret store and treat migration/deployment ordering explicitly. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 184. Database Connection Pooling
**Section:** Deployment and operations

Card title: Database Connection Pooling. Visual instructions: Show many incoming HTTP requests sharing a bounded pool of database connections rather than each creating a new connection. Label pool size, waiting queue, timeout, and database capacity. Emphasize that pool limits must match worker/process count and DB limits. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 185. Logging, Metrics, and Tracing
**Section:** Deployment and operations

Card title: Logging, Metrics, and Tracing. Visual instructions: Show one request associated with a request ID across handler, service, and database timing. Separate logs (events/details), metrics (counts/latencies), and traces (cross-layer path). Mark sensitive fields that must be redacted. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 186. Graceful Failure and Timeouts
**Section:** Deployment and operations

Card title: Graceful Failure and Timeouts. Visual instructions: Show a request calling a slow downstream service, hitting a timeout, then returning a controlled error or fallback. Include request deadline and cancellation path. Emphasize that unlimited waits can exhaust connections and worker capacity. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 187. Production Readiness Checklist
**Section:** Deployment and operations

Card title: Production Readiness Checklist. Visual instructions: Show a compact checklist: typecheck/build, tests, auth checks, runtime secrets, database migrations/backups, HTTPS/cookies, logs/alerts, caching rules, and rollback plan. Make it a go/no-go gate, not a generic decorative checklist. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 188. Scaling a Nuxt Application
**Section:** Deployment and operations

Card title: Scaling a Nuxt Application. Visual instructions: Show multiple stateless Nuxt server instances behind a load balancer, shared durable database/cache, and static assets on a CDN. Mark where local in-memory state fails across instances. Keep sticky sessions out of the default assumption; use shared session storage when needed. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 189. Feature-Oriented Project Structure
**Section:** Advanced architecture

Card title: Feature-Oriented Project Structure. Visual instructions: Show modules organized by business capability (`projects/`, `clients/`, `auth/`) each with UI, composable, types, and service boundaries as appropriate. Contrast with a folder structure organized only by file type. Keep framework conventions intact while clarifying ownership. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 190. Dependency Direction and Layering
**Section:** Advanced architecture

Card title: Dependency Direction and Layering. Visual instructions: Draw dependencies flowing from route/controller to application service to domain rules and repository interfaces, with infrastructure implementations at the edge. Show a prohibited reverse import from domain logic into Nuxt UI/runtime-specific code. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 191. Server-Only Imports and Bundle Boundaries
**Section:** Advanced architecture

Card title: Server-Only Imports and Bundle Boundaries. Visual instructions: Show a server handler importing database drivers and private environment variables, while the client page imports only safe types/API helpers. Draw a hard build boundary between server bundle and browser bundle. The takeaway is to keep secrets and Node-only modules out of client dependencies. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 192. API Contracts and DTOs
**Section:** Advanced architecture

Card title: API Contracts and DTOs. Visual instructions: Show database rows transformed into a stable response DTO, then consumed by the frontend. Place validation and schema version/compatibility at the boundary. Explain why leaking database table structure couples the UI to persistence details. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 193. Error Taxonomy Across Layers
**Section:** Advanced architecture

Card title: Error Taxonomy Across Layers. Visual instructions: Show distinct categories: validation error, unauthenticated, forbidden, not found, conflict, dependency failure, and unexpected bug. Map each to an HTTP status, a safe client message, and internal diagnostic detail. Keep known domain errors separate from raw exceptions. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 194. Idempotency for Retried Mutations
**Section:** Advanced architecture

Card title: Idempotency for Retried Mutations. Visual instructions: Show a client retrying a create-payment/order request after a timeout. A stable idempotency key lets the server return the original result rather than performing the operation twice. Mark request key, stored outcome, and duplicate detection. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 195. Concurrency and Lost Updates
**Section:** Advanced architecture

Card title: Concurrency and Lost Updates. Visual instructions: Show two users reading version 5, then both attempting to update it. Without a concurrency check, the later write overwrites the earlier one; with version/ETag/conditional update, the conflict is detected. Distinguish transactions from optimistic concurrency control. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 196. Background Jobs vs. Request Work
**Section:** Advanced architecture

Card title: Background Jobs vs. Request Work. Visual instructions: Show a request validating and enqueuing a long-running task, returning a job ID, and a worker processing it asynchronously. The client polls or receives status updates. Use report generation/email processing as examples; keep the HTTP request short. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 197. Caching Without Cross-User Leakage
**Section:** Advanced architecture

Card title: Caching Without Cross-User Leakage. Visual instructions: Show a shared cache serving public catalog data safely while user-specific account data is keyed or excluded appropriately. Highlight user/tenant identity, authorization, cache key design, and invalidation. Mark a dangerous shared-cache collision between two users in red. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 198. Monolith First, Clear Boundaries
**Section:** Advanced architecture

Card title: Monolith First, Clear Boundaries. Visual instructions: Show one deployable Nuxt application split into clear modules/services, with a database and stable internal interfaces. Contrast it with prematurely splitting each feature into networked microservices. Teach that modularity and deployment distribution are separate choices. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 199. Project 1: Reactive Counter and Settings
**Section:** Projects and practice

Card title: Project 1: Reactive Counter and Settings. Visual instructions: Show a tiny starter app with a reactive counter, computed double, toggle setting, and two components passing props/events. Map each feature to `ref`, `computed`, event handling, props, and emits. Keep the scope deliberately small for a first implementation exercise. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 200. Project 2: Searchable Project Catalog
**Section:** Projects and practice

Card title: Project 2: Searchable Project Catalog. Visual instructions: Show a search/filter UI, query parameters in the URL, results loading state, empty state, and a project detail page. Label the Vue skills: `v-model`, computed filters, `v-for` keys, router params, and async data loading. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 201. Project 3: CRUD Full-Stack App
**Section:** Projects and practice

Card title: Project 3: CRUD Full-Stack App. Visual instructions: Show create/list/detail/update/delete flow through Nuxt page → server API → service → database. Include form validation and status/error states. Emphasize end-to-end data ownership and server-side validation, not just connecting buttons to endpoints. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 202. Project 4: Authentication and Permissions
**Section:** Projects and practice

Card title: Project 4: Authentication and Permissions. Visual instructions: Show login, secure session cookie, protected navigation, API authorization, and resource ownership check. Mark that middleware guides navigation but the API enforces permissions. Use a user accessing only resources they are allowed to manage. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 203. Project 5: File Upload and Processing
**Section:** Projects and practice

Card title: Project 5: File Upload and Processing. Visual instructions: Show upload form, progress state, server validation, private/object storage, metadata persistence, and a processing status. Include size/type limits and a failure/retry branch. Connect the UI lifecycle to secure backend handling. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 204. Project 6: Admin Dashboard
**Section:** Projects and practice

Card title: Project 6: Admin Dashboard. Visual instructions: Show a dashboard with paginated table, filters persisted in the URL, summary metrics, detail drawer/modal, and role-gated actions. Map features to async data, composables, route query, component interfaces, and API authorization. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 205. Project 7: Production-Ready Search
**Section:** Projects and practice

Card title: Project 7: Production-Ready Search. Visual instructions: Show debounced input → validated query → backend search → paginated results, with request cancellation and performance metrics. Add indexing and parameterized SQL on the server side. Distinguish frontend convenience filtering from scalable backend search. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 206. Project 8: Testable Feature Slice
**Section:** Projects and practice

Card title: Project 8: Testable Feature Slice. Visual instructions: Show one feature implemented with a unit test for business logic, component test for interaction, server API integration test, and Playwright E2E flow. Keep all four test levels connected to a single user story. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 207. Project 9: Deploy and Observe
**Section:** Projects and practice

Card title: Project 9: Deploy and Observe. Visual instructions: Show a Nuxt app moving through CI checks, container/build artifact, staging smoke test, production rollout, request metrics, and rollback. Make deployment a repeatable pipeline rather than a manual SSH checklist. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.

## 208. Expert Self-Review: Trace Every Value
**Section:** Projects and practice

Card title: Expert Self-Review: Trace Every Value. Visual instructions: Show a value originating in a form, becoming reactive state, entering a request, being validated and authorized on the server, becoming a database mutation, returning as a DTO, and rendering back to the user. Use it as an end-to-end mental model for debugging and design review. Keep the main diagram limited to this concept, use short exact labels, and include one practical takeaway.
