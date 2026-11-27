
import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  Activity, ArrowDownRight, ArrowUpRight, ArrowUp,
  Bell, Bot, Boxes, BriefcaseBusiness, ChartNoAxesCombined,
  Check, ChevronDown, CircleHelp, Command, Compass,
  LayoutDashboard, Menu, MessageCircle, Package,
  Search, Send, Settings2, ShoppingBag, Sparkles,
  TrendingUp, Users, WandSparkles, X
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";

const products = [
  { name: "Cotton T-shirt", category: "Everyday essentials", score: 96.89, margin: "55.6%", demand: "High", color: "lime" },
  { name: "Linen shirt", category: "Summer staples", score: 84.36, margin: "53.1%", demand: "High", color: "purple" },
  { name: "Wide-leg trousers", category: "Contemporary", score: 76.59, margin: "51.4%", demand: "High", color: "orange" },
  { name: "Summer dress", category: "Seasonal edit", score: 63.02, margin: "52.4%", demand: "Medium", color: "pink" },
];

function Avatar({ type = "stylist", size = "large", active = false }) {
  return (
    <div className={`avatar avatar-${type} avatar-${size} ${active ? "avatar-active" : ""}`}>
      <div className="avatar-orbit orbit-one" />
      <div className="avatar-orbit orbit-two" />
      <div className="avatar-core">
        <span>{type === "stylist" ? "✦" : "◈"}</span>
      </div>
      <div className="avatar-spark spark-one">✧</div>
      <div className="avatar-spark spark-two">·</div>
    </div>
  );
}

function Sidebar({ workspace, setWorkspace, page, setPage, mobileOpen, setMobileOpen }) {
  return (
    <>
      {mobileOpen && <div className="mobile-scrim" onClick={() => setMobileOpen(false)} />}
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-symbol">S<span>.</span></div>
          <div>
            <div className="brand-name">stockline<span>®</span></div>
            <div className="brand-caption">FASHION INTELLIGENCE</div>
          </div>
          <button className="mobile-close icon-button" onClick={() => setMobileOpen(false)}><X /></button>
        </div>

        <div className="workspace-label">YOUR WORKSPACE</div>
        <button className={`workspace-choice ${workspace === "business" ? "selected" : ""}`}
          onClick={() => { setWorkspace("business"); setPage("overview"); setMobileOpen(false); }}>
          <div className="workspace-icon business-icon"><BriefcaseBusiness size={17} /></div>
          <span>Business studio</span>
          <span className="nav-indicator" />
        </button>
        <button className={`workspace-choice ${workspace === "customer" ? "selected" : ""}`}
          onClick={() => { setWorkspace("customer"); setPage("assistant"); setMobileOpen(false); }}>
          <div className="workspace-icon customer-icon"><ShoppingBag size={17} /></div>
          <span>Customer studio</span>
          <span className="nav-indicator" />
        </button>

        <div className="sidebar-divider" />
        <div className="workspace-label">WORKSPACE MENU</div>

        {workspace === "business" ? (
          <>
            <button className={`nav-link ${page === "overview" ? "active" : ""}`} onClick={() => setPage("overview")}><LayoutDashboard /> Overview</button>
            <button className={`nav-link ${page === "products" ? "active" : ""}`} onClick={() => setPage("products")}><Package /> Product intelligence</button>
            <button className={`nav-link ${page === "inventory" ? "active" : ""}`} onClick={() => setPage("inventory")}><Boxes /> Inventory & demand</button>
            <button className={`nav-link ${page === "assistant" ? "active" : ""}`} onClick={() => setPage("assistant")}><MessageCircle /> Business agent <span className="live-dot" /></button>
          </>
        ) : (
          <>
            <button className={`nav-link ${page === "assistant" ? "active" : ""}`} onClick={() => setPage("assistant")}><Sparkles /> Your stylist</button>
            <button className={`nav-link ${page === "discover" ? "active" : ""}`} onClick={() => setPage("discover")}><Compass /> Discover</button>
            <button className={`nav-link ${page === "products" ? "active" : ""}`} onClick={() => setPage("products")}><ShoppingBag /> Collection</button>
          </>
        )}

        <div className="sidebar-bottom">
          <div className="sidebar-agent">
            <div className="agent-mini"><Activity size={15} /></div>
            <div><strong>Stockline AI</strong><span>Systems operational</span></div>
            <span className="status-pulse" />
          </div>
          <button className="nav-link"><Settings2 /> Settings</button>
          <button className="nav-link"><CircleHelp /> Help centre</button>
          <div className="profile">
            <div className="profile-avatar">E</div>
            <div><strong>Workspace owner</strong><span>Administrator</span></div>
            <ChevronDown size={15} />
          </div>
        </div>
      </aside>
    </>
  );
}

function Header({ workspace, page, setMobileOpen }) {
  const title = page === "assistant"
    ? workspace === "business" ? "Your business partner" : "Your personal stylist"
    : page === "overview" ? "Overview"
    : page === "products" ? workspace === "business" ? "Product intelligence" : "The collection"
    : page === "inventory" ? "Inventory & demand" : "Discover";

  return (
    <header className="topbar">
      <button className="icon-button mobile-menu" onClick={() => setMobileOpen(true)}><Menu /></button>
      <div className="breadcrumb"><span>STOCKLINE</span><span className="crumb-slash">/</span><strong>{title}</strong></div>
      <div className="topbar-actions">
        <div className="system-status"><span className="live-dot" /> ALL SYSTEMS LIVE</div>
        <button className="icon-button"><Search /></button>
        <button className="icon-button notification"><Bell /><i /></button>
        <div className="top-avatar">E</div>
      </div>
    </header>
  );
}

function Metric({ label, value, change, icon: Icon, tone }) {
  return (
    <motion.div className="metric-card" whileHover={{ y: -5, scale: 1.015 }} transition={{ type: "spring", stiffness: 280 }}>
      <div className="metric-top"><span>{label}</span><div className={`metric-icon ${tone}`}><Icon size={18} /></div></div>
      <div className="metric-value">{value}</div>
      <div className="metric-foot"><span className="metric-change"><ArrowUpRight size={14} /> {change}</span><span>SIMULATED DATA</span></div>
    </motion.div>
  );
}

function AgentFeature({ workspace, onChat }) {
  const stylist = workspace === "customer";
  const type = stylist ? "stylist" : "operator";

  return (
    <motion.section className={`agent-feature ${type}-feature`} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <div className="feature-glow" />
      <div className="feature-copy">
        <div className="eyebrow"><span className="live-dot" /> MEET YOUR AI {stylist ? "STYLIST" : "OPERATIONS PARTNER"}</div>
        <h2>{stylist ? <>Your style.<br /><em>Reimagined.</em></> : <>Think bigger.<br /><em>Move smarter.</em></>}</h2>
        <p>{stylist
          ? "A little inspiration, a lot of personality. Meet your personal fashion companion."
          : "Your intelligent retail partner. Turning data, demand and decisions into momentum."}</p>
        <button className="primary-button" onClick={onChat}>
          {stylist ? "Meet your stylist" : "Talk to your operator"} <ArrowUpRight size={17} />
        </button>
      </div>
      <div className="feature-avatar-wrap">
        <div className="avatar-label"><span className="live-dot" /> ONLINE NOW</div>
        <Avatar type={type} active />
        <div className="floating-tag tag-top">{stylist ? "STYLE MODE ✦" : "STRATEGY MODE ◈"}</div>
        <div className="floating-tag tag-bottom">{stylist ? "Your creative companion" : "Your retail intelligence"}</div>
      </div>
      <div className="feature-index">01 / 02</div>
    </motion.section>
  );
}

function Overview({ setPage, workspace }) {
  const isCustomer = workspace === "customer";
  return (
    <motion.div className="page-content" key={workspace + "-overview"} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}>
      <div className="page-heading">
        <div><div className="eyebrow">SATURDAY, NOVEMBER 28 · SUMMER THREADS</div><h1>{isCustomer ? "A world of your style." : "The bigger picture."}</h1><p>{isCustomer ? "Explore a collection made for your everyday." : "Your business, at a glance. Let's make things happen."}</p></div>
        <div className="heading-decoration">✳</div>
      </div>

      <AgentFeature workspace={workspace} onChat={() => setPage("assistant")} />

      {isCustomer ? (
        <section className="section-block">
          <div className="section-heading"><div><div className="eyebrow">CURATED FOR THE SEASON</div><h2>Find your next favourite.</h2></div><button className="text-button" onClick={() => setPage("products")}>Explore collection <ArrowUpRight size={15}/></button></div>
          <div className="customer-collection">
            {["The everyday edit", "Summer essentials", "Easy silhouettes"].map((item, i) => <motion.div className={`collection-tile tile-${i}`} key={item} whileHover={{ y: -6 }}><span>0{i + 1} / EDIT</span><h3>{item}</h3><button onClick={() => setPage("products")}>Explore <ArrowUpRight size={15}/></button></motion.div>)}
          </div>
          <p className="data-note">Illustrative collection based on simulated project data. No live catalogue is connected yet.</p>
        </section>
      ) : (
        <>
          <div className="section-heading metric-heading"><div><div className="eyebrow">YOUR BUSINESS, DECODED</div><h2>Numbers with a purpose.</h2></div><span className="data-pill">DEMO ENVIRONMENT</span></div>
          <div className="metrics-grid">
            <Metric label="Historical units sold" value="2,610" change="Across 5 products" icon={ShoppingBag} tone="lime"/>
            <Metric label="Purchasing budget" value="$250K" change="Illustrative allocation" icon={ChartNoAxesCombined} tone="purple"/>
            <Metric label="Target gross margin" value="50%" change="Business objective" icon={TrendingUp} tone="orange"/>
            <Metric label="Product categories" value="05" change="Currently modelled" icon={Boxes} tone="pink"/>
          </div>
          <section className="section-block">
            <div className="section-heading"><div><div className="eyebrow">PRODUCT INTELLIGENCE</div><h2>What's moving the needle.</h2></div><button className="text-button" onClick={() => setPage("products")}>View all products <ArrowUpRight size={15}/></button></div>
            <div className="product-list">
              {products.slice(0, 3).map((p, i) => <motion.div className="product-row" key={p.name} whileHover={{ x: 5 }}>
                <div className={`product-rank rank-${p.color}`}>0{i + 1}</div>
                <div className="product-details"><strong>{p.name}</strong><span>{p.category}</span></div>
                <div className="product-score"><span>PRODUCT SCORE</span><strong>{p.score.toFixed(1)}</strong></div>
                <div className="product-margin"><span>GROSS MARGIN</span><strong>{p.margin}</strong></div>
                <div className="demand-tag">{p.demand} demand</div>
                <ArrowUpRight className="row-arrow" size={17}/>
              </motion.div>)}
            </div>
          </section>
        </>
      )}
    </motion.div>
  );
}

function ProductPage() {
  return (
    <motion.div className="page-content" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
      <div className="page-heading"><div><div className="eyebrow">THE PRODUCT UNIVERSE</div><h1>Product intelligence.</h1><p>Five products. A clearer picture of opportunity.</p></div><div className="heading-decoration">✳</div></div>
      <div className="metrics-grid">
        <Metric label="Products evaluated" value="05" change="Full scoring coverage" icon={Package} tone="lime"/>
        <Metric label="Top product score" value="96.89" change="Cotton T-shirt" icon={TrendingUp} tone="purple"/>
        <Metric label="Margin objective" value="50%" change="Business target" icon={ChartNoAxesCombined} tone="orange"/>
        <Metric label="Dataset status" value="Demo" change="Simulated data" icon={Activity} tone="pink"/>
      </div>
      <div className="product-list product-list-large">
        {products.map((p, i) => <motion.div className="product-row" key={p.name} whileHover={{ x: 5 }}>
          <div className={`product-rank rank-${p.color}`}>0{i + 1}</div>
          <div className="product-details"><strong>{p.name}</strong><span>{p.category}</span></div>
          <div className="product-score"><span>OVERALL SCORE</span><strong>{p.score.toFixed(2)}</strong></div>
          <div className="product-margin"><span>GROSS MARGIN</span><strong>{p.margin}</strong></div>
          <div className="demand-tag">{p.demand} demand</div>
        </motion.div>)}
      </div>
      <p className="data-note">Scores and margins are drawn from the existing simulated evaluation dataset.</p>
    </motion.div>
  );
}

function ChatPage({ workspace }) {
  const isCustomer = workspace === "customer";
  const type = isCustomer ? "stylist" : "operator";
  const name = isCustomer ? "The Stylist" : "The Operator";
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  async function send(text = input) {
    const value = text.trim();
    if (!value || loading) return;
    setMessages(prev => [...prev, { role: "user", text: value }]);
    setInput("");
    setLoading(true);
    try {
      const response = await fetch(`${API}/api/chat/${workspace}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "stockline_demo_user", message: value, session_id: sessionId })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "The assistant could not respond.");
      setSessionId(data.session_id);
      setMessages(prev => [...prev, { role: "assistant", text: data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", text: `I couldn't connect just now: ${error.message}. Please check that the Stockline backend is running.` }]);
    } finally {
      setLoading(false);
    }
  }

  const suggestions = isCustomer
    ? ["Help me find summer essentials", "I like relaxed, neutral styles", "What would suit everyday wear?"]
    : ["Give me a business overview", "Analyse my product rankings", "Prepare a purchasing recommendation"];

  return (
    <motion.div className="chat-layout" key={workspace} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
      <div className="chat-main">
        <div className="chat-welcome">
          <Avatar type={type} size="medium" active/>
          <div className="eyebrow"><span className="live-dot"/> YOUR AI {isCustomer ? "STYLIST" : "OPERATIONS PARTNER"}</div>
          <h1>{isCustomer ? <>Let's find your<br/><em>kind of style.</em></> : <>Let's make<br/><em>smarter moves.</em></>}</h1>
          <p>{isCustomer ? "Tell me what you're drawn to. We'll find something that feels like you." : "Your business intelligence partner is ready. What should we look at first?"}</p>
        </div>
        <div className="chat-messages">
          {messages.map((m, i) => <motion.div className={`chat-message ${m.role}`} key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            {m.role === "assistant" && <Avatar type={type} size="small"/>}
            <div className="message-bubble">{m.text}</div>
          </motion.div>)}
          {loading && <div className="chat-message assistant"><Avatar type={type} size="small" active/><div className="message-bubble typing"><i/><i/><i/></div></div>}
        </div>
        {messages.length === 0 && <div className="suggestion-list">{suggestions.map(s => <button key={s} onClick={() => send(s)}>{s}<ArrowUpRight size={14}/></button>)}</div>}
        <form className="chat-composer" onSubmit={e => { e.preventDefault(); send(); }}>
          <input value={input} onChange={e => setInput(e.target.value)} placeholder={isCustomer ? "Tell your stylist what you're looking for..." : "Ask Stockline about your business..."} />
          <button type="submit" disabled={!input.trim() || loading}><ArrowUp size={19}/></button>
        </form>
        <div className="chat-disclaimer">STOCKLINE AI · RESPONSES MAY NEED VERIFICATION · DEMO DATA</div>
      </div>
      <aside className="chat-side">
        <div className="chat-side-art"><div className="art-ring"/><Avatar type={type} active/><span className="art-star">✳</span></div>
        <div className="chat-side-copy"><div className="eyebrow">YOUR COMPANION</div><h3>{name}</h3><p>{isCustomer ? "A creative eye for your everyday. Here to make fashion feel more personal." : "A sharp mind for your business. Here to turn information into action."}</p></div>
        <div className="chat-side-status"><span className="live-dot"/> CONNECTED TO STOCKLINE</div>
      </aside>
    </motion.div>
  );
}

function InventoryPage() {
  return (
    <motion.div className="page-content" initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
      <div className="page-heading"><div><div className="eyebrow">OPERATIONS INTELLIGENCE</div><h1>Inventory & demand.</h1><p>A view into simulated stock and replenishment planning.</p></div><div className="heading-decoration">◈</div></div>
      <div className="metrics-grid">
        <Metric label="Forecast horizon" value="30 days" change="Historical baseline" icon={Activity} tone="lime"/>
        <Metric label="Products tracked" value="05" change="Illustrative inventory" icon={Boxes} tone="purple"/>
        <Metric label="Replenishment" value="504" change="Previously calculated units" icon={Package} tone="orange"/>
        <Metric label="Incoming orders" value="170" change="Simulated inbound units" icon={TrendingUp} tone="pink"/>
      </div>
      <div className="inventory-note"><Sparkles/><div><strong>Inventory intelligence is ready to explore.</strong><p>Ask the Business Agent to calculate current replenishment requirements using the inventory and demand tools.</p></div></div>
    </motion.div>
  );
}

function App() {
  const [workspace, setWorkspace] = useState("business");
  const [page, setPage] = useState("overview");
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-shell">
      <div className="ambient ambient-one"/><div className="ambient ambient-two"/>
      <Sidebar {...{workspace, setWorkspace, page, setPage, mobileOpen, setMobileOpen}}/>
      <main className="main-area">
        <Header {...{workspace, page, setMobileOpen}}/>
        <AnimatePresence mode="wait">
          {page === "assistant" ? <ChatPage key={workspace + page} workspace={workspace}/> :
           page === "products" ? <ProductPage key={workspace + page}/> :
           page === "inventory" ? <InventoryPage key={page}/> :
           <Overview key={workspace + page} workspace={workspace} setPage={setPage}/>}
        </AnimatePresence>
        <footer className="app-footer"><span>STOCKLINE® · FASHION INTELLIGENCE</span><span>BUILT TO MOVE DIFFERENTLY <span className="footer-star">✳</span></span></footer>
      </main>
    </div>
  );
}

export default App;
