"""
Vue + Nuxt memory card prompts (beginner -> expert).

Versions this was written against (Oct 2026):
  Vue 3.5 stable (3.6 + Vapor Mode is a release candidate), Nuxt 4.x, Nitro v2 (Nuxt 5 + Nitro v3 upcoming).

Each prompt describes ONE card with the same fields:
  Title / Meaning / Code (all quoted, so only these get rendered as text) + one simple Visual.
The unquoted "Memory card for <tag>" part is context only.

Use:  from vue_nuxt_prompts import prompts, STYLE
      full_prompt = f"{prompt} {STYLE}"      # or concatenate your own style
"""

# Style goes in ONCE. Concatenate it (or your own) to every prompt.
STYLE = (
    "Style: flat vector educational flashcard, 4:5 portrait, one rounded white card on a soft light-gray "
    "background. Large bold sans-serif title at the top. One short sentence in medium regular font under it. "
    "The code sits in a dark navy (#35495e) rounded box with white monospace text. One single simple flat icon "
    "at the bottom, using Vue green (#42b883) and Nuxt green (#00DC82) as accents. Lots of white space, big "
    "readable text, high contrast, centered layout, thick rounded shapes. The quoted Title, Meaning and Code "
    "are the only text on the card, spelled exactly as written. No extra words, no logos, no watermark."
)


def card(tag, title, meaning, code="", visual=""):
    s = f'Memory card for {tag}. Title: "{title}". Meaning: "{meaning}".'
    if code:
        s += f' Code: "{code}".'
    if visual:
        s += f" Visual: {visual}."
    return s


# Rows are (title, meaning, code, visual)
SECTIONS = [
    # ------------------------------------------------------------------ roadmap
    ("Learning path", [
        ("Stage 1: Vue Basics", "Template syntax, ref, computed, props, emits.", "", "first step of a staircase"),
        ("Stage 2: Vue Ecosystem", "Router, Pinia, TypeScript, testing.", "", "second step of a staircase"),
        ("Stage 3: Nuxt Frontend", "Pages, layouts, data fetching, rendering modes.", "", "third step of a staircase"),
        ("Stage 4: Nuxt Fullstack", "Nitro API routes, database, auth, deployment.", "", "fourth step of a staircase"),
        ("Stage 5: Expert", "Performance, modules, layers, internals.", "", "top of a staircase with a flag"),
    ]),

    # ------------------------------------------------------------------ vue beginner
    ("Vue / Beginner", [
        ("Mental model", "UI is a function of state. Change state and Vue updates the DOM.", "state -> template -> DOM", "three boxes connected by arrows"),
        ("Create a project", "Scaffold a Vue app powered by Vite.", "npm create vue@latest", "a folder with a small spark"),
        ("Single-File Component", "One .vue file holds template, script, and style.", "<template> <script setup> <style>", "three stacked colored blocks"),
        ("script setup", "Write Composition API code with less boilerplate.", "<script setup>", "a small toolbox"),
        ("Interpolation", "Show data inside the template.", "{{ message }}", "a speech bubble"),
        ("v-bind", "Bind an attribute to data. Short form is a colon.", ":src='imageUrl'", "a chain link"),
        ("v-on", "Listen to events. Short form is @.", "@click='count++'", "a finger pressing a button"),
        ("v-model", "Two-way binding between an input and data.", "<input v-model='name'>", "two arrows pointing opposite ways"),
        ("v-if", "Render an element only when the condition is true.", "<p v-if='ok'>Hi</p>", "a switch turned on"),
        ("v-else", "The fallback branch after v-if.", "<p v-else>No</p>", "a fork in a road"),
        ("v-show", "Toggle CSS display. The element stays in the DOM.", "<p v-show='ok'>Hi</p>", "an open eye"),
        ("v-for", "Render a list from an array.", "<li v-for='i in items' :key='i.id'>", "a vertical list of three dots"),
        ("key", "A unique key lets Vue track each list item.", ":key='item.id'", "a small key"),
        ("ref()", "Reactive value. Use .value in script.", "const count = ref(0)", "a box containing the number 0"),
        ("reactive()", "Reactive object. No .value needed.", "const s = reactive({ n: 0 })", "a box with curly braces"),
        ("Template unwrap", "Refs unwrap automatically in templates.", "{{ count }}", "an opening box"),
        ("computed()", "Cached value derived from other state.", "const dbl = computed(() => n.value * 2)", "a calculator"),
        ("watch()", "Run a side effect when a source changes.", "watch(n, (v) => console.log(v))", "a magnifying glass"),
        ("Class binding", "Toggle CSS classes with an object.", ":class='{ active: isOn }'", "a paint brush"),
        ("Style binding", "Bind inline styles to data.", ":style='{ color: c }'", "a color palette"),
        ("Props", "Pass data from parent to child.", "const props = defineProps(['title'])", "an arrow pointing down"),
        ("Emits", "Child sends events up to the parent.", "const emit = defineEmits(['save'])", "an arrow pointing up"),
        ("Slots", "Parent passes content into a child.", "<slot />", "a box with an empty slot"),
        ("Use a component", "Import it in script setup, then use it in the template.", "import Card from './Card.vue'", "a puzzle piece"),
        ("onMounted", "Runs after the component is added to the DOM.", "onMounted(() => console.log('ready'))", "a planted flag"),
        ("Lifecycle", "A component is created, mounted, updated, then unmounted.", "onMounted / onUpdated / onUnmounted", "four steps of a staircase"),
        ("Event modifiers", "Shortcuts for common event handling.", "@submit.prevent='save'", "a stop sign"),
        ("Key modifiers", "React to one specific key.", "@keyup.enter='send'", "an Enter key"),
        ("v-model modifiers", "Clean up input values automatically.", "v-model.trim='name'", "scissors"),
        ("v-html", "Renders raw HTML. Never use it with user input.", "<div v-html='html'></div>", "a warning triangle"),
        ("Vue DevTools", "Inspect components, state, and events in the browser.", "Vue DevTools", "a bug and a magnifying glass"),
    ]),

    # ------------------------------------------------------------------ vue intermediate
    ("Vue / Intermediate", [
        ("watchEffect", "Auto-tracks dependencies and runs immediately.", "watchEffect(() => log(n.value))", "a radar"),
        ("Watch options", "Run immediately or watch deeply.", "watch(src, cb, { immediate: true })", "a stopwatch"),
        ("Writable computed", "A computed value with a getter and a setter.", "computed({ get, set })", "a two-way door"),
        ("defineModel", "Easy v-model support for a child component.", "const model = defineModel()", "two linked boxes"),
        ("Named slots", "Several slot areas in one component.", "<template #header>Title</template>", "a page with header and footer"),
        ("Scoped slots", "The child passes data back to slot content.", "<slot :item='item' />", "a box handing out a card"),
        ("Fallthrough attrs", "Attributes that are not props fall onto the root element.", "<MyBtn class='big' />", "an arrow dropping into a box"),
        ("provide / inject", "Share data with deep descendants without props.", "provide('theme', theme)", "a tree with a line to a leaf"),
        ("Composable", "A function that reuses stateful logic.", "export function useCounter() {}", "lego bricks"),
        ("Cleanup", "Remove listeners when the component unmounts.", "onUnmounted(() => off())", "a broom"),
        ("toRefs", "Destructure reactive state without losing reactivity.", "const { n } = toRefs(state)", "a box splitting into small boxes"),
        ("shallowRef", "Only replacing .value is reactive. Good for large data.", "const big = shallowRef(data)", "a single flat layer"),
        ("Template refs", "Get a DOM element or a component instance.", "const el = useTemplateRef('box')", "a crosshair target"),
        ("nextTick", "Wait until the DOM has updated.", "await nextTick()", "an hourglass"),
        ("Teleport", "Render content somewhere else in the DOM.", "<Teleport to='body'>", "a portal"),
        ("Suspense", "Show a fallback while async children load. Still experimental.", "<Suspense> <template #fallback>", "a loading spinner"),
        ("KeepAlive", "Cache component state when switching views.", "<KeepAlive>", "a pause button"),
        ("Transition", "Animate elements entering and leaving.", "<Transition name='fade'>", "a fading square"),
        ("TransitionGroup", "Animate items in a list.", "<TransitionGroup name='list' tag='ul'>", "three sliding bars"),
        ("Dynamic component", "Switch components with :is.", "<component :is='current' />", "a swap arrow"),
        ("Async component", "Lazy load a component when needed.", "defineAsyncComponent(() => import('./A.vue'))", "a cloud with a download arrow"),
        ("Custom directive", "Reuse low-level DOM behavior.", "const vFocus = { mounted: (el) => el.focus() }", "a spotlight"),
        ("Router setup", "Create the router and install it on the app.", "createRouter({ history: createWebHistory(), routes })", "a signpost"),
        ("RouterLink / RouterView", "Link to routes. The view shows the matched page.", "<RouterLink to='/'> <RouterView />", "an arrow pointing to a screen"),
        ("useRoute / useRouter", "Read the current route. Navigate with the router.", "router.push('/about')", "a map pin"),
        ("Dynamic params", "A route segment becomes a param.", "{ path: '/user/:id' }", "a pin with a number"),
        ("Nested routes", "Child routes render inside a parent view.", "{ path: '/a', children: [] }", "nested boxes"),
        ("Navigation guard", "Run logic before navigation happens.", "router.beforeEach((to) => {})", "a security gate"),
        ("Lazy routes", "Split code per route.", "component: () => import('./Home.vue')", "a path splitting in two"),
        ("Pinia store", "Global state using the setup syntax.", "defineStore('cart', () => {})", "a shopping cart"),
        ("Pinia setup store", "ref is state, computed is getter, function is action.", "ref / computed / function", "three small icons in a row"),
        ("storeToRefs", "Destructure store state without losing reactivity.", "const { items } = storeToRefs(store)", "a cart splitting into items"),
        ("Typed props", "Declare props with a TypeScript type.", "defineProps<{ title: string }>()", "a blue square with TS"),
        ("Typed emits", "Type your event payloads.", "defineEmits<{ save: [id: number] }>()", "a blue square with TS"),
        ("Typed ref", "Give a ref an explicit type.", "const n = ref<number>(0)", "a blue square with TS"),
        ("Vitest + Test Utils", "Mount a component and assert its output.", "const w = mount(Comp)", "a green check mark"),
        ("VueUse", "A big collection of ready-made composables.", "const { x, y } = useMouse()", "a toolbox"),
        ("CSS v-bind", "Use component state inside CSS.", "color: v-bind(color)", "a paint drop"),
        ("Scoped styles", "Styles apply to this component only.", "<style scoped>", "a shield"),
        ("Error capture", "Catch errors from descendant components.", "onErrorCaptured((e) => false)", "a net"),
    ]),

    # ------------------------------------------------------------------ vue advanced
    ("Vue / Advanced", [
        ("Proxy reactivity", "Vue wraps objects in a Proxy to track reads and writes.", "new Proxy(target, handler)", "a transparent shell around a box"),
        ("track and trigger", "Reads are tracked. Writes trigger effects.", "read -> track, write -> trigger", "two arrows between two boxes"),
        ("effectScope", "Group effects and stop them together.", "const scope = effectScope()", "a bubble holding small circles"),
        ("customRef", "Build a ref with custom get and set, like a debounce.", "customRef((track, trigger) => ({}))", "a gear"),
        ("readonly", "Block mutation of reactive state.", "const ro = readonly(state)", "a padlock"),
        ("markRaw / toRaw", "Opt out of reactivity for third-party objects.", "const m = markRaw(new Map())", "a box with a crossed-out eye"),
        ("triggerRef", "Force an update for a shallowRef.", "triggerRef(big)", "a lightning bolt"),
        ("Render function", "Create vnodes directly with h().", "h('div', { class: 'a' }, 'Hi')", "a tiny tree of nodes"),
        ("JSX / TSX", "Write Vue components in JSX.", "const A = () => <div>Hi</div>", "angle brackets"),
        ("Functional component", "A plain function that returns vnodes.", "const A = (p) => h('p', p.msg)", "a function arrow"),
        ("Plugin", "Install global features with app.use().", "app.use(myPlugin, options)", "an electric plug"),
        ("app.provide", "App-wide dependency injection.", "app.provide('api', api)", "a funnel"),
        ("Generic components", "Make type-safe reusable components.", "<script setup lang='ts' generic='T'>", "a box labeled T"),
        ("defineExpose", "Choose what a parent can access on a component ref.", "defineExpose({ open })", "a door opening"),
        ("defineSlots", "Type your slots.", "defineSlots<{ default(p: { n: number }): any }>()", "a typed slot box"),
        ("defineOptions", "Set options like inheritAttrs in script setup.", "defineOptions({ inheritAttrs: false })", "a settings slider"),
        ("Props destructure", "Reactive props destructure with defaults (3.5+).", "const { size = 'md' } = defineProps<{ size?: string }>()", "a box unpacking"),
        ("useId", "SSR-safe unique IDs for form fields (3.5+).", "const id = useId()", "a name tag"),
        ("onWatcherCleanup", "Cancel stale work inside a watcher (3.5+).", "onWatcherCleanup(() => ctrl.abort())", "a trash bin"),
        ("Lazy hydration", "Hydrate later: on visible, idle, or interaction (3.5+).", "defineAsyncComponent({ hydrate: hydrateOnVisible() })", "a sleeping moon"),
        ("v-memo", "Skip re-rendering unless dependencies change.", "<div v-memo='[item.id]'>", "a memory chip"),
        ("v-once", "Render once and never update.", "<p v-once>{{ msg }}</p>", "the number 1"),
        ("toValue", "Accept values, refs, or getters in a composable.", "const v = toValue(input)", "three inputs into one funnel"),
        ("Debug reactivity", "Find what triggered a re-render.", "onRenderTriggered((e) => console.log(e))", "a bug"),
        ("Global error handler", "Catch all uncaught app errors.", "app.config.errorHandler = (e) => {}", "a safety net"),
        ("Custom Elements", "Use Vue components as native web components.", "defineCustomElement(Comp)", "a lego block with a globe"),
        ("Vue 3.6 reactivity", "Reactivity is rebuilt on alien-signals. Release candidate.", "vue@3.6 (RC)", "a fast lightning bolt"),
        ("Vapor Mode", "Compile templates to direct DOM code with no virtual DOM. Release candidate.", "<script setup vapor>", "a rising steam cloud"),
    ]),

    # ------------------------------------------------------------------ vue expert
    ("Vue / Expert", [
        ("Compiler pipeline", "A template is parsed, transformed, then code is generated.", "parse -> transform -> generate", "three boxes in a row"),
        ("Patch flags", "The compiler marks dynamic parts so diffing skips static nodes.", "PatchFlags.TEXT", "a flag on a node"),
        ("Block tree", "Only dynamic nodes inside a block are tracked.", "openBlock() / createBlock()", "a tree with highlighted leaves"),
        ("Scheduler", "Updates are batched and flushed asynchronously.", "pre flush -> render -> post flush", "a queue of dots"),
        ("Custom renderer", "Render Vue to non-DOM targets.", "createRenderer(nodeOps)", "a paintbrush on a canvas"),
        ("SSR", "Render to a string on the server, then hydrate on the client.", "renderToString(app)", "a server and a browser"),
        ("Hydration mismatch", "Server HTML and client HTML must match.", "Avoid Date.now() in render", "two mismatched puzzle pieces"),
        ("Component library", "Package components with Vite library mode.", "build: { lib: { entry } }", "a box of lego"),
        ("Type augmentation", "Add types for global properties.", "interface ComponentCustomProperties {}", "a puzzle piece with TS"),
        ("Profiling", "Use the DevTools timeline to find slow components.", "Vue DevTools > Performance", "a speedometer"),
        ("Vapor interop", "Mix Vapor and virtual DOM components with the interop plugin.", "app.use(vaporInteropPlugin)", "two bridges joined"),
    ]),

    # ------------------------------------------------------------------ nuxt beginner
    ("Nuxt / Beginner", [
        ("What is Nuxt", "Full-stack Vue framework with SSR, routing, and a server API.", "npm create nuxt@latest", "a green mountain"),
        ("Dev server", "Start the dev server with hot reload.", "npm run dev", "a play button"),
        ("Project structure", "App code lives in app/. Server code lives in server/.", "app/  server/  public/  shared/", "a folder tree"),
        ("nuxt.config.ts", "The central config file.", "export default defineNuxtConfig({})", "a gear"),
        ("app.vue", "Root of your app. Put NuxtPage inside it.", "<NuxtPage />", "a house"),
        ("File-based routing", "The file name becomes the route.", "app/pages/about.vue -> /about", "a file with an arrow to a URL"),
        ("Index route", "index.vue is the root of a folder.", "app/pages/index.vue -> /", "a home icon"),
        ("Dynamic route", "Square brackets make a param.", "app/pages/users/[id].vue", "a file with brackets"),
        ("Catch-all route", "Match any remaining path.", "app/pages/[...slug].vue", "a net"),
        ("Read route params", "Get the current route and its params.", "const route = useRoute()", "a map pin"),
        ("NuxtLink", "Client-side navigation with smart prefetching.", "<NuxtLink to='/about'>About</NuxtLink>", "a link arrow"),
        ("Auto-import components", "Files in app/components need no import.", "<UserCard />", "a magic wand"),
        ("Auto-import composables", "Exports from app/composables are available everywhere.", "export const useCounter = () => {}", "a magic wand"),
        ("Auto-import Vue APIs", "ref, computed, and watch need no import.", "const n = ref(0)", "a magic wand"),
        ("Layouts", "A layout wraps your pages.", "app/layouts/default.vue", "a page frame"),
        ("Use a layout", "Pick a layout per page.", "definePageMeta({ layout: 'admin' })", "a page with a frame"),
        ("useHead", "Set the page title and head tags.", "useHead({ title: 'Home' })", "a head icon"),
        ("useSeoMeta", "Typed SEO meta tags.", "useSeoMeta({ title: 'Home', description: 'Hi' })", "a search bar"),
        ("public vs assets", "public/ is served as-is. assets/ is processed by the bundler.", "/logo.png vs ~/assets/logo.png", "two folders"),
        ("Modules", "Add features by installing a module.", "modules: ['@nuxt/image']", "a puzzle piece"),
        ("error.vue", "Custom error page for the whole app.", "const error = useError()", "a warning triangle"),
        ("ClientOnly", "Render something only in the browser.", "<ClientOnly><MyMap /></ClientOnly>", "a browser window"),
        ("useState", "SSR-friendly shared state.", "const n = useState('n', () => 0)", "a shared box"),
        ("Nuxt DevTools", "Inspect pages, modules, and payload in the browser.", "Nuxt DevTools", "a magnifier over a mountain"),
        ("SSR basics", "The server renders HTML, then the browser hydrates it.", "server HTML -> hydrate -> interactive", "a server arrow to a browser"),
        ("Build and preview", "Build for production and preview locally.", "npx nuxt build && npx nuxt preview", "a package box"),
    ]),

    # ------------------------------------------------------------------ nuxt intermediate
    ("Nuxt / Intermediate", [
        ("useFetch", "SSR-safe data fetching with caching.", "const { data } = await useFetch('/api/posts')", "a cloud with a down arrow"),
        ("useAsyncData", "Wrap any async function with a unique key.", "useAsyncData('posts', () => $fetch('/api/posts'))", "a cloud with a key"),
        ("$fetch", "Plain fetch helper. Use it for user actions, not page data.", "await $fetch('/api/save', { method: 'POST' })", "a paper plane"),
        ("Fetch result", "You get data, status, error, and refresh.", "const { data, status, error, refresh } = await useFetch(url)", "four small boxes"),
        ("Reactive params", "Params that are refs trigger a refetch.", "useFetch('/api/posts', { query: { page } })", "a refresh arrow"),
        ("Lazy fetch", "Navigate first, load data after.", "useFetch(url, { lazy: true })", "a snail"),
        ("Client-only fetch", "Skip fetching on the server.", "useFetch(url, { server: false })", "a browser window"),
        ("pick / transform", "Shrink or reshape the payload.", "useFetch(url, { pick: ['id', 'title'] })", "a filter funnel"),
        ("Shared keys", "The same key shares one cached ref across components (Nuxt 4).", "useFetch(url, { key: 'posts' })", "two boxes sharing one key"),
        ("Nuxt 4 data defaults", "data and error default to undefined, not null.", "if (data.value === undefined)", "an empty box"),
        ("Shallow data", "Fetched data is a shallowRef by default. Opt in to deep.", "useFetch(url, { deep: true })", "a flat layer and a deep layer"),
        ("Rendering modes", "SSR, SPA, static, or hybrid per route.", "SSR | SPA | SSG | Hybrid", "four small boxes"),
        ("routeRules", "Set rendering and caching per route.", "routeRules: { '/blog/**': { swr: 3600 } }", "a rulebook"),
        ("Prerender", "Build a page to static HTML at build time.", "routeRules: { '/': { prerender: true } }", "a document stamp"),
        ("SPA route", "Turn off SSR for part of the app.", "routeRules: { '/admin/**': { ssr: false } }", "a browser window"),
        ("Static generation", "Generate a fully static site.", "npx nuxt generate", "a stack of pages"),
        ("Route middleware", "Run code before navigating to a route.", "defineNuxtRouteMiddleware((to) => {})", "a security gate"),
        ("navigateTo", "Redirect from a middleware or a component.", "return navigateTo('/login')", "an arrow turning right"),
        ("Named middleware", "Attach a middleware to a page.", "definePageMeta({ middleware: 'auth' })", "a gate on a page"),
        ("Plugins", "Run code when the Nuxt app starts.", "export default defineNuxtPlugin(() => {})", "an electric plug"),
        ("Plugin provide", "Expose a helper to the whole app.", "return { provide: { hello: () => 'hi' } }", "a gift box"),
        ("useNuxtApp", "Access the runtime Nuxt instance.", "const { $hello } = useNuxtApp()", "a mountain with a key"),
        ("useCookie", "SSR-friendly cookies.", "const token = useCookie('token')", "a cookie"),
        ("runtimeConfig", "Private keys on the server. Public keys on the client.", "runtimeConfig: { apiSecret: '', public: {} }", "a lock and an open box"),
        ("Env variables", "Override config with NUXT_ environment variables.", "NUXT_PUBLIC_API_BASE=/api", "a dotenv file"),
        ("useRuntimeConfig", "Read config in components and server routes.", "const config = useRuntimeConfig()", "a gear"),
        ("app.config.ts", "Public settings that can update at runtime.", "export default defineAppConfig({ theme: 'dark' })", "a toggle switch"),
        ("Nuxt Image", "Optimized responsive images.", "<NuxtImg src='/a.jpg' width='300' />", "a picture frame"),
        ("Nuxt UI", "A component library for Nuxt.", "modules: ['@nuxt/ui']", "a button and a card"),
        ("Nuxt Content", "File-based content from Markdown.", "queryCollection('blog').all()", "a Markdown file"),
        ("Pinia in Nuxt", "Install the module, then use stores.", "modules: ['@pinia/nuxt']", "a shopping cart"),
        ("i18n", "Add multi-language support.", "modules: ['@nuxtjs/i18n']", "a globe"),
        ("Page transitions", "Animate between pages.", "app: { pageTransition: { name: 'page' } }", "two sliding pages"),
        ("NuxtErrorBoundary", "Catch errors in part of a page.", "<NuxtErrorBoundary>", "a safety net"),
        ("Route validation", "Reject invalid params with a 404.", "definePageMeta({ validate: (r) => !!r.params.id })", "a check mark"),
        ("Lazy components", "Prefix with Lazy to load on demand.", "<LazyHeavyChart v-if='show' />", "a snail"),
        ("Lazy hydration", "Hydrate a component when it becomes visible.", "<LazyChart hydrate-on-visible />", "a sleeping moon"),
        ("Hydration mismatch", "Server and client HTML differ. Avoid random or time values in render.", "useState('now', () => Date.now())", "two mismatched puzzle pieces"),
    ]),

    # ------------------------------------------------------------------ nuxt fullstack (nitro)
    ("Nuxt / Fullstack (Nitro server)", [
        ("Full-stack flow", "A page calls an API route, which talks to the database.", "Page -> useFetch -> /api -> DB", "four boxes connected by arrows"),
        ("API route", "A file in server/api becomes an endpoint.", "server/api/hello.get.ts -> GET /api/hello", "a server rack"),
        ("defineEventHandler", "Every server handler is an event handler.", "export default defineEventHandler(() => ({ ok: true }))", "a lightning bolt"),
        ("HTTP method suffix", "The file suffix sets the method.", "users.post.ts -> POST /api/users", "a POST envelope"),
        ("Route params", "Read a param on the server.", "getRouterParam(event, 'id')", "a pin"),
        ("Query string", "Read query parameters.", "const q = getQuery(event)", "a question mark"),
        ("Request body", "Read the JSON body.", "const body = await readBody(event)", "an envelope"),
        ("Validated body", "Validate input with a schema such as Zod.", "readValidatedBody(event, schema.parse)", "a shield with a check mark"),
        ("Errors", "Throw an HTTP error.", "throw createError({ statusCode: 404 })", "a red cross"),
        ("Status code", "Set the response status.", "setResponseStatus(event, 201)", "the number 201"),
        ("Server cookies", "Set a secure cookie.", "setCookie(event, 'sid', id, { httpOnly: true })", "a cookie with a lock"),
        ("server/routes", "Routes outside /api.", "server/routes/health.get.ts -> /health", "a heart monitor line"),
        ("server/middleware", "Runs on every request.", "export default defineEventHandler((event) => {})", "a gate"),
        ("server/plugins", "Run code when the server starts.", "export default defineNitroPlugin(() => {})", "an electric plug"),
        ("server/utils", "Auto-imported helpers for server code.", "server/utils/db.ts", "a toolbox"),
        ("Server secrets", "Read private config in a handler.", "useRuntimeConfig(event).apiSecret", "a key"),
        ("Typed $fetch", "Types flow from server handlers to the client.", "const user = await $fetch('/api/user')", "a connecting line with TS"),
        ("Cached handler", "Cache an API response.", "defineCachedEventHandler(fn, { maxAge: 60 })", "a stopwatch"),
        ("useStorage", "Key-value storage in Nitro.", "await useStorage().setItem('k', 'v')", "a drawer"),
        ("Database", "Use SQLite with Drizzle for typed queries.", "db.select().from(users)", "a database cylinder"),
        ("Auth", "Use nuxt-auth-utils for sessions.", "const { loggedIn, user } = useUserSession()", "a person badge"),
        ("Login", "Store the session after login.", "await setUserSession(event, { user })", "a key in a door"),
        ("Protect an API", "Reject requests without a session.", "await requireUserSession(event)", "a locked gate"),
        ("File upload", "Read multipart form data.", "await readMultipartFormData(event)", "a file with an up arrow"),
        ("WebSocket", "Real-time two-way connection.", "export default defineWebSocketHandler({})", "two arrows in a loop"),
        ("Server-Sent Events", "Stream updates from the server.", "createEventStream(event)", "a stream of dots"),
        ("Scheduled tasks", "Run cron jobs in Nitro.", "nitro: { scheduledTasks: { '0 * * * *': ['sync'] } }", "a clock"),
        ("Deployment preset", "Nitro builds for many hosts.", "nitro: { preset: 'vercel' }", "a rocket"),
        ("Build output", "The production server lives in .output.", ".output/server/index.mjs", "a package box"),
        ("Testing", "Test components in a Nuxt environment.", "await mountSuspended(MyComponent)", "a green check mark"),
        ("Mock an endpoint", "Fake an API in tests.", "registerEndpoint('/api/user', () => ({}))", "a mask"),
    ]),

    # ------------------------------------------------------------------ nuxt advanced / expert
    ("Nuxt / Advanced and Expert", [
        ("shared/ directory", "Code shared by both app and server.", "shared/utils/format.ts", "two boxes sharing one block"),
        ("createUseFetch", "Make a custom useFetch with your own defaults (4.4+).", "export const useAPI = createUseFetch({ baseURL: '/api' })", "a custom tool"),
        ("createUseAsyncData", "Make a custom useAsyncData with defaults (4.4+).", "export const useLazyData = createUseAsyncData({ lazy: true })", "a custom tool"),
        ("Runtime hooks", "Hook into the Nuxt app lifecycle.", "nuxtApp.hook('page:finish', () => {})", "a hook"),
        ("Build-time hooks", "Hook into Nuxt during the build.", "nuxt.hook('modules:done', () => {})", "a hook and a hammer"),
        ("defineNuxtModule", "Author your own Nuxt module.", "export default defineNuxtModule({ setup() {} })", "a puzzle piece"),
        ("Layers", "Extend another Nuxt project.", "extends: ['../base-layer']", "stacked layers"),
        ("Server components", "Render a component on the server only.", "Banner.server.vue", "a server block"),
        ("NuxtIsland", "Render a component as an island.", "<NuxtIsland name='Banner' />", "an island"),
        ("Payload", "Data serialized from the server to the client.", "nuxtApp.payload", "a package"),
        ("SWR and ISR", "Serve stale content and refresh in the background.", "routeRules: { '/**': { isr: 600 } }", "a refresh arrow"),
        ("Edge rendering", "Run SSR on edge workers.", "nitro: { preset: 'cloudflare_module' }", "a globe with a bolt"),
        ("Typed pages", "Experimental typed route names and params.", "experimental: { typedPages: true }", "a map with TS"),
        ("Bundle analysis", "See what makes your bundle large.", "npx nuxt analyze", "a pie chart"),
        ("Build profiling", "Get a build performance trace (4.4+).", "npx nuxt build --profile", "a flame graph"),
        ("Typecheck", "Check types across app and server.", "npx nuxt typecheck", "a check mark with TS"),
        ("Fonts and scripts", "Optimize fonts and third-party scripts.", "modules: ['@nuxt/fonts', '@nuxt/scripts']", "a letter A"),
        ("SEO modules", "Sitemap, robots, and schema.org.", "modules: ['@nuxtjs/sitemap']", "a search bar"),
        ("Security module", "Add security headers and rate limiting.", "modules: ['nuxt-security']", "a shield"),
        ("Router v5", "Nuxt 4.4 upgrades to vue-router v5.", "nuxt@4.4+", "a signpost"),
        ("Upgrade Nuxt", "Upgrade and dedupe dependencies.", "npx nuxt upgrade --dedupe", "an upward arrow"),
        ("Nuxt 3 to 4", "Run the official migration codemod.", "npx codemod@latest nuxt/4/migration-recipe", "a bridge"),
        ("Nuxt 5 and Nitro v3", "The next major release upgrades to Nitro v3. Upcoming.", "Nuxt 5 + Nitro v3", "a road ahead"),
    ]),
]

prompts = [card(tag, *row) for tag, rows in SECTIONS for row in rows]

if __name__ == "__main__":
    print(f"{len(prompts)} prompts")
    print(prompts[0])
    print(prompts[-1])
