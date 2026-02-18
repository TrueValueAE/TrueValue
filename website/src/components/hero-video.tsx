"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { VolumeX, Play, Pause } from "lucide-react";

/* 10 scenes — ~3.5s each ≈ 35s total loop */
const SCENE_DURATIONS = [3500, 3500, 3500, 3500, 3500, 3500, 3500, 3500, 3500, 3000];
const SCENE_COUNT = SCENE_DURATIONS.length;
const TOTAL_DURATION = SCENE_DURATIONS.reduce((a, b) => a + b, 0);
const FADE_DURATION = 500;

const SCENE_LABELS = [
  "The Problem",
  "Live Property Search",
  "4-Pillar Investment Score",
  "Chiller Trap Detection",
  "DLD Price Validation",
  "Building Intelligence",
  "Compare Properties",
  "Mortgage & Financial Tools",
  "PDF Reports & Portfolio",
  "Try It Free",
];

const bg = "bg-gradient-to-br from-[hsl(222,47%,7%)] to-[hsl(222,47%,11%)]";
const panel = "rounded-lg border border-border/30 bg-[hsl(217,33%,10%)]";

export function HeroVideo() {
  const [currentScene, setCurrentScene] = useState(0);
  const [fade, setFade] = useState<"in" | "out">("in");
  const [isPaused, setIsPaused] = useState(false);
  const [showControls, setShowControls] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isVisible, setIsVisible] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const progressRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const sceneStartRef = useRef(Date.now());

  const goToScene = useCallback((i: number) => {
    setFade("out");
    setTimeout(() => {
      setCurrentScene(i);
      setFade("in");
      sceneStartRef.current = Date.now();
    }, 300);
  }, []);

  const advanceScene = useCallback(() => {
    setFade("out");
    setTimeout(() => {
      setCurrentScene((prev) => (prev + 1) % SCENE_COUNT);
      setFade("in");
      sceneStartRef.current = Date.now();
    }, FADE_DURATION);
  }, []);

  useEffect(() => {
    if (isPaused || !isVisible) return;
    timerRef.current = setTimeout(advanceScene, SCENE_DURATIONS[currentScene]);
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [currentScene, isPaused, isVisible, advanceScene]);

  useEffect(() => {
    if (isPaused || !isVisible) return;
    sceneStartRef.current = Date.now();
    progressRef.current = setInterval(() => {
      const elapsed = Date.now() - sceneStartRef.current;
      const prior = SCENE_DURATIONS.slice(0, currentScene).reduce((a, b) => a + b, 0);
      setProgress(((prior + elapsed) / TOTAL_DURATION) * 100);
    }, 50);
    return () => { if (progressRef.current) clearInterval(progressRef.current); };
  }, [currentScene, isPaused, isVisible]);

  useEffect(() => {
    if (!containerRef.current) return;
    const obs = new IntersectionObserver(([e]) => setIsVisible(e.isIntersecting), { threshold: 0.3 });
    obs.observe(containerRef.current);
    return () => obs.disconnect();
  }, []);

  const scenes = [
    <ScenePain key={0} />,
    <SceneSearch key={1} />,
    <SceneInvestmentScore key={2} />,
    <SceneChiller key={3} />,
    <SceneDLD key={4} />,
    <SceneBuilding key={5} />,
    <SceneCompare key={6} />,
    <SceneMortgage key={7} />,
    <ScenePDFPortfolio key={8} />,
    <SceneCTA key={9} />,
  ];

  return (
    <section className="py-12 sm:py-20">
      <div className="mx-auto max-w-4xl px-4 sm:px-6">
        {/* Scene label */}
        <div className="mb-3 flex items-center justify-between">
          <span className="text-xs font-medium text-muted-foreground">
            {SCENE_LABELS[currentScene]}
          </span>
          <span className="text-xs tabular-nums text-muted-foreground">
            {currentScene + 1}/{SCENE_COUNT}
          </span>
        </div>

        <div
          ref={containerRef}
          className="group relative overflow-hidden rounded-xl border border-border/50 bg-card/80 shadow-2xl shadow-primary/5"
          onMouseEnter={() => setShowControls(true)}
          onMouseLeave={() => setShowControls(false)}
        >
          {/* 16:9 */}
          <div className="relative w-full" style={{ paddingBottom: "56.25%" }}>
            <div className="absolute inset-0">
              <div
                className="h-full w-full transition-opacity"
                style={{ opacity: fade === "in" ? 1 : 0, transitionDuration: `${FADE_DURATION}ms` }}
              >
                {scenes[currentScene]}
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-muted/30">
            <div className="h-full bg-primary transition-all duration-100" style={{ width: `${progress}%` }} />
          </div>

          {/* Scene dots */}
          <div className="absolute bottom-3 left-1/2 flex -translate-x-1/2 gap-1">
            {SCENE_DURATIONS.map((_, i) => (
              <button
                key={i}
                onClick={() => goToScene(i)}
                className={`h-1.5 rounded-full transition-all ${
                  i === currentScene ? "w-5 bg-primary" : "w-1.5 bg-foreground/25 hover:bg-foreground/50"
                }`}
              />
            ))}
          </div>

          {/* Play/Pause overlay */}
          <div
            className={`absolute inset-0 flex items-center justify-center transition-opacity duration-300 ${
              showControls ? "opacity-100" : "opacity-0"
            }`}
          >
            <button
              onClick={() => setIsPaused(!isPaused)}
              className="rounded-full bg-background/60 p-3 backdrop-blur-sm transition-transform hover:scale-110"
            >
              {isPaused ? <Play className="h-8 w-8 text-foreground" /> : <Pause className="h-8 w-8 text-foreground" />}
            </button>
          </div>

          {/* Mute */}
          <button
            onClick={() => {}}
            className="absolute right-3 top-3 rounded-full bg-background/60 p-2 backdrop-blur-sm hover:bg-background/80"
          >
            <VolumeX className="h-4 w-4 text-foreground" />
          </button>
        </div>
      </div>
    </section>
  );
}

/* ═══════════════════════════════════════════
   SHARED HELPERS
   ═══════════════════════════════════════════ */

function Overlay({ children, color = "primary" }: { children: React.ReactNode; color?: string }) {
  const colors: Record<string, string> = {
    primary: "bg-primary/20 text-primary",
    red: "bg-red-500/20 text-red-300",
    green: "bg-green-500/20 text-green-300",
    amber: "bg-amber-500/20 text-amber-300",
    blue: "bg-blue-500/20 text-blue-300",
  };
  return (
    <div className="absolute bottom-6 left-0 right-0 text-center sm:bottom-10">
      <span className={`inline-block rounded-full px-4 py-1.5 text-[11px] font-semibold backdrop-blur-sm sm:text-sm ${colors[color]}`}>
        {children}
      </span>
    </div>
  );
}

function TelegramFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="w-full max-w-[200px] sm:max-w-[240px]">
      <div className="rounded-[20px] border-2 border-border/40 bg-[hsl(217,33%,8%)] p-1.5 sm:p-2">
        <div className="mx-auto mb-1.5 h-3 w-16 rounded-full bg-[hsl(217,33%,6%)]" />
        <div className="rounded-[14px] bg-[hsl(217,33%,12%)] p-2.5 sm:p-3">
          {/* Header */}
          <div className="flex items-center gap-2 border-b border-border/20 pb-1.5">
            <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20">
              <span className="text-[8px] font-bold text-primary">TV</span>
            </div>
            <div>
              <div className="text-[10px] font-semibold leading-tight">TrueValue.ae</div>
              <div className="text-[8px] text-green-400">online</div>
            </div>
          </div>
          <div className="mt-2 space-y-1.5">{children}</div>
        </div>
      </div>
    </div>
  );
}

function UserMsg({ text, time }: { text: string; time: string }) {
  return (
    <div className="ml-auto max-w-[88%] rounded-lg rounded-br-sm bg-primary/20 px-2 py-1">
      <p className="text-[9px] text-foreground sm:text-[10px]">{text}</p>
      <span className="block text-right text-[7px] text-muted-foreground">{time}</span>
    </div>
  );
}

function BotMsg({ children, time }: { children: React.ReactNode; time: string }) {
  return (
    <div className="max-w-[92%] rounded-lg rounded-bl-sm bg-muted/30 px-2 py-1">
      {children}
      <span className="block text-[7px] text-muted-foreground">{time}</span>
    </div>
  );
}

function InlineButtons({ labels }: { labels: string[] }) {
  return (
    <div className="flex flex-wrap gap-0.5">
      {labels.map((l) => (
        <div key={l} className="rounded border border-primary/30 bg-primary/10 px-1.5 py-0.5 text-[7px] font-medium text-primary sm:text-[8px]">
          {l}
        </div>
      ))}
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 1 — THE PROBLEM
   ═══════════════════════════════════════════ */
function ScenePain() {
  return (
    <div className={`relative flex h-full flex-col items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="w-full max-w-lg animate-scene-float">
        {/* Browser chrome */}
        <div className="flex items-center gap-2 rounded-t-lg border border-border/30 bg-[hsl(217,33%,12%)] px-3 py-1.5">
          <div className="flex gap-1">
            <div className="h-2 w-2 rounded-full bg-red-500/70" />
            <div className="h-2 w-2 rounded-full bg-yellow-500/70" />
            <div className="h-2 w-2 rounded-full bg-green-500/70" />
          </div>
          <div className="ml-2 flex gap-0.5">
            {["Bayut", "Property Finder", "DLD", "Excel", "Google"].map((t, i) => (
              <div key={t} className={`rounded-t px-2 py-0.5 text-[8px] font-medium sm:text-[9px] ${i === 0 ? "bg-[hsl(217,33%,17%)] text-foreground" : "text-muted-foreground/50"}`}>{t}</div>
            ))}
          </div>
        </div>
        <div className="rounded-b-lg border border-t-0 border-border/30 bg-[hsl(217,33%,10%)] p-3 sm:p-4">
          <div className="space-y-1.5">
            <div className="h-2.5 w-3/4 animate-pulse rounded bg-muted/30" />
            <div className="h-2.5 w-1/2 animate-pulse rounded bg-muted/20" />
            <div className="mt-2 grid grid-cols-3 gap-1.5">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-10 animate-pulse rounded bg-muted/15" />
              ))}
            </div>
            <div className="h-2.5 w-2/3 animate-pulse rounded bg-muted/20" />
          </div>
        </div>
      </div>
      {/* Clock */}
      <div className="absolute right-4 top-4 sm:right-8 sm:top-6">
        <div className="relative h-9 w-9 rounded-full border-2 border-red-400/60 sm:h-11 sm:w-11">
          <div className="absolute left-1/2 top-1/2 h-2.5 w-0.5 -translate-x-1/2 origin-bottom -rotate-45 bg-red-400/80 sm:h-3.5" />
          <div className="absolute left-1/2 top-1/2 h-2 w-0.5 -translate-x-1/2 origin-bottom rotate-90 bg-red-400/60 sm:h-2.5" />
        </div>
      </div>
      <div className="absolute bottom-14 left-5 text-xl animate-scene-float sm:left-8 sm:text-2xl">😤</div>
      <Overlay color="red">Hours of manual research per property</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 2 — LIVE PROPERTY SEARCH (Bayut API)
   ═══════════════════════════════════════════ */
function SceneSearch() {
  const listings = [
    { title: "Marina Gate T2 — 2BR", price: "AED 2.1M", area: "1,247 sqft", psf: "1,684", beds: "2", img: "🏙️" },
    { title: "Princess Tower — 2BR", price: "AED 1.75M", area: "1,180 sqft", psf: "1,483", beds: "2", img: "🌆" },
    { title: "Damac Heights — 2BR", price: "AED 1.95M", area: "1,310 sqft", psf: "1,489", beds: "2", img: "🏢" },
  ];
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="flex w-full max-w-xl gap-3">
        {/* Phone with search command */}
        <TelegramFrame>
          <UserMsg text="/search Marina 2BR under 2.5M" time="2:10 PM" />
          <BotMsg time="2:10 PM">
            <p className="text-[9px] font-semibold text-primary sm:text-[10px]">🔍 Found 6 properties</p>
            <p className="text-[8px] text-muted-foreground sm:text-[9px]">Dubai Marina · 2BR · Under AED 2.5M</p>
            <p className="mt-0.5 text-[8px] text-muted-foreground sm:text-[9px]">Showing top 3 results...</p>
          </BotMsg>
        </TelegramFrame>

        {/* Results panel */}
        <div className="hidden flex-1 animate-scene-scale sm:block">
          <div className="space-y-1.5">
            {listings.map((l) => (
              <div key={l.title} className={`${panel} flex items-center gap-2 p-2`}>
                <span className="text-lg">{l.img}</span>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[10px] font-semibold">{l.title}</div>
                  <div className="flex gap-2 text-[9px] text-muted-foreground">
                    <span className="font-medium text-primary">{l.price}</span>
                    <span>{l.area}</span>
                    <span>AED {l.psf}/sqft</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-1.5 text-[8px] text-muted-foreground">Live results via Bayut API</div>
        </div>
      </div>
      <Overlay color="primary">Live property search across 15+ zones</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 3 — 4-PILLAR INVESTMENT SCORING
   ═══════════════════════════════════════════ */
function SceneInvestmentScore() {
  const pillars = [
    { name: "Price", pts: "27/30", pct: 90, verdict: "Below avg PSF" },
    { name: "Yield", pts: "20/25", pct: 80, verdict: "6.2% gross" },
    { name: "Liquidity", pts: "16/20", pct: 80, verdict: "High exit ease" },
    { name: "Quality", pts: "11/15", pct: 73, verdict: "Moderate supply" },
    { name: "Chiller", pts: "6/10", pct: 60, verdict: "District cooling" },
  ];
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="w-full max-w-lg animate-scene-scale">
        <div className="grid grid-cols-[1fr_auto] gap-4">
          {/* Score card */}
          <div className={`${panel} p-3 sm:p-4`}>
            <div className="text-[9px] uppercase tracking-wider text-muted-foreground sm:text-[10px]">Investment Score</div>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-3xl font-bold text-green-400 sm:text-4xl">80</span>
              <span className="text-xs text-muted-foreground">/100</span>
            </div>
            <div className="mt-0.5 rounded bg-green-500/20 px-1.5 py-0.5 text-[10px] font-bold text-green-300 w-fit sm:text-xs">
              GOOD BUY ✅
            </div>
            <div className="mt-2 text-[9px] text-muted-foreground sm:text-[10px]">
              Marina Gate Tower 2 · 2BR · AED 2.1M
            </div>
          </div>
          {/* Grade badge */}
          <div className="flex flex-col items-center justify-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-xl border-2 border-green-400/40 bg-green-500/10 sm:h-16 sm:w-16">
              <span className="text-2xl font-bold text-green-400 sm:text-3xl">B+</span>
            </div>
            <span className="mt-1 text-[8px] text-muted-foreground">Grade</span>
          </div>
        </div>
        {/* Pillar breakdown */}
        <div className={`${panel} mt-2 p-3`}>
          <div className="text-[9px] uppercase tracking-wider text-muted-foreground sm:text-[10px]">4-Pillar Breakdown</div>
          <div className="mt-2 space-y-1.5">
            {pillars.map((p) => (
              <div key={p.name} className="flex items-center gap-2">
                <span className="w-12 text-[9px] text-muted-foreground sm:text-[10px]">{p.name}</span>
                <div className="h-1.5 flex-1 rounded-full bg-muted/20">
                  <div className="h-full rounded-full bg-primary/70" style={{ width: `${p.pct}%` }} />
                </div>
                <span className="w-10 text-right text-[9px] font-medium tabular-nums text-foreground sm:text-[10px]">{p.pts}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <Overlay color="green">Institutional-grade 4-pillar scoring (0-100)</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 4 — CHILLER TRAP DETECTION
   ═══════════════════════════════════════════ */
function SceneChiller() {
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="flex w-full max-w-xl gap-3">
        {/* Chiller analysis panel */}
        <div className={`${panel} flex-1 animate-scene-scale p-3 sm:p-4`}>
          <div className="flex items-center gap-2">
            <span className="text-base sm:text-lg">❄️</span>
            <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground sm:text-xs">Chiller Cost Analysis</div>
          </div>
          <div className="mt-2 space-y-1.5 sm:mt-3">
            <div className="flex justify-between text-[9px] sm:text-[10px]">
              <span className="text-muted-foreground">Provider</span>
              <span className="font-medium text-amber-300">Empower (District)</span>
            </div>
            <div className="flex justify-between text-[9px] sm:text-[10px]">
              <span className="text-muted-foreground">Unit Size</span>
              <span>1,247 sqft → 4.36 TR</span>
            </div>
            <div className="flex justify-between text-[9px] sm:text-[10px]">
              <span className="text-muted-foreground">Capacity Charge</span>
              <span className="text-red-300">AED 85/TR/month (fixed!)</span>
            </div>
            <div className="flex justify-between text-[9px] sm:text-[10px]">
              <span className="text-muted-foreground">Variable Usage</span>
              <span>~AED 1,200/month</span>
            </div>
            <div className="mt-1 border-t border-border/20 pt-1.5">
              <div className="flex justify-between text-[10px] font-semibold sm:text-xs">
                <span>Annual Cost</span>
                <span className="rounded bg-red-500/20 px-1.5 py-0.5 text-red-300 ring-1 ring-red-500/30">AED 29,028/yr</span>
              </div>
            </div>
          </div>
          <div className="mt-2 rounded border border-amber-500/30 bg-amber-500/10 p-1.5 sm:mt-3 sm:p-2">
            <p className="text-[9px] font-bold text-amber-300 sm:text-[11px]">⚠️ CHILLER TRAP DETECTED</p>
            <p className="text-[8px] text-amber-300/70 sm:text-[9px]">Fixed capacity charge AED 85/TR/mo adds AED 4,447/yr regardless of usage</p>
          </div>
        </div>

        {/* Impact on yield */}
        <div className="hidden w-36 flex-col gap-2 sm:flex">
          <div className={`${panel} p-2.5 text-center`}>
            <div className="text-[9px] text-muted-foreground">Gross Yield</div>
            <div className="text-lg font-bold text-green-400">6.2%</div>
          </div>
          <div className={`${panel} p-2.5 text-center`}>
            <div className="text-[9px] text-muted-foreground">After Chiller</div>
            <div className="text-lg font-bold text-amber-300">4.8%</div>
          </div>
          <div className={`${panel} p-2.5 text-center`}>
            <div className="text-[9px] text-muted-foreground">Yield Impact</div>
            <div className="text-lg font-bold text-red-400">-1.4%</div>
          </div>
        </div>
      </div>
      <Overlay color="amber">Signature feature: Hidden chiller costs exposed</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 5 — DLD TRANSACTION VALIDATION
   ═══════════════════════════════════════════ */
function SceneDLD() {
  const txns = [
    { date: "Jan 2025", type: "2BR", price: "AED 1.92M", psf: "1,540", resale: true },
    { date: "Dec 2024", type: "2BR", price: "AED 2.05M", psf: "1,642", resale: true },
    { date: "Nov 2024", type: "2BR", price: "AED 1.88M", psf: "1,510", resale: false },
    { date: "Oct 2024", type: "2BR", price: "AED 2.11M", psf: "1,690", resale: true },
    { date: "Sep 2024", type: "1BR", price: "AED 1.35M", psf: "1,580", resale: true },
  ];
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="w-full max-w-lg animate-scene-scale">
        <div className={`${panel} p-3 sm:p-4`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-sm sm:text-base">🏛️</span>
              <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground sm:text-xs">DLD Transaction Data</div>
            </div>
            <div className="rounded bg-green-500/20 px-1.5 py-0.5 text-[8px] font-medium text-green-300 sm:text-[9px]">LIVE DATA</div>
          </div>

          {/* Table */}
          <div className="mt-2 sm:mt-3">
            <div className="grid grid-cols-5 gap-1 border-b border-border/20 pb-1 text-[8px] font-medium text-muted-foreground sm:text-[9px]">
              <span>Date</span><span>Type</span><span>Price</span><span>PSF</span><span>Status</span>
            </div>
            {txns.map((t, i) => (
              <div key={i} className="grid grid-cols-5 gap-1 border-b border-border/10 py-1 text-[8px] sm:text-[9px]">
                <span className="text-muted-foreground">{t.date}</span>
                <span>{t.type}</span>
                <span className="font-medium">{t.price}</span>
                <span className="tabular-nums">{t.psf}</span>
                <span className={t.resale ? "text-blue-300" : "text-green-300"}>{t.resale ? "Resale" : "New"}</span>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="mt-2 grid grid-cols-3 gap-2 sm:mt-3">
            <div className="rounded bg-muted/20 p-1.5 text-center">
              <div className="text-[8px] text-muted-foreground sm:text-[9px]">Avg PSF</div>
              <div className="text-[10px] font-bold text-primary sm:text-xs">AED 1,592</div>
            </div>
            <div className="rounded bg-muted/20 p-1.5 text-center">
              <div className="text-[8px] text-muted-foreground sm:text-[9px]">Median</div>
              <div className="text-[10px] font-bold text-primary sm:text-xs">AED 1.92M</div>
            </div>
            <div className="rounded bg-muted/20 p-1.5 text-center">
              <div className="text-[8px] text-muted-foreground sm:text-[9px]">Trend</div>
              <div className="text-[10px] font-bold text-green-400 sm:text-xs">+4.2%</div>
            </div>
          </div>
        </div>
      </div>
      <Overlay color="blue">Real sold prices from Dubai Land Department</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 6 — BUILDING INTELLIGENCE / SNAGGING
   ═══════════════════════════════════════════ */
function SceneBuilding() {
  const issues = [
    { severity: "HIGH", text: "HVAC noise complaints in upper floors", src: "Reddit" },
    { severity: "MED", text: "Elevator wait times during peak hours", src: "Reddit" },
    { severity: "LOW", text: "Minor paint chipping in corridors", src: "Report" },
  ];
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="flex w-full max-w-xl gap-3">
        {/* Phone with command */}
        <TelegramFrame>
          <UserMsg text="/analyze Cayan Tower" time="3:05 PM" />
          <BotMsg time="3:05 PM">
            <p className="text-[9px] font-semibold text-primary sm:text-[10px]">🏗️ Building Quality Report</p>
            <p className="text-[8px] text-muted-foreground sm:text-[9px]">Risk Signal: MEDIUM 🟡</p>
            <p className="text-[8px] text-muted-foreground sm:text-[9px]">3 issues found via community intel</p>
          </BotMsg>
          <InlineButtons labels={["📊 Full Report", "📈 Compare", "✅ Save"]} />
        </TelegramFrame>

        {/* Issues panel */}
        <div className="hidden flex-1 animate-scene-scale sm:block">
          <div className={`${panel} p-3`}>
            <div className="flex items-center gap-2">
              <span>🔍</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Snagging Intelligence</span>
            </div>
            <div className="mt-2 space-y-1.5">
              {issues.map((issue, i) => (
                <div key={i} className="flex items-start gap-2 rounded bg-muted/10 p-1.5">
                  <span className={`mt-0.5 rounded px-1 py-0.5 text-[7px] font-bold ${
                    issue.severity === "HIGH" ? "bg-red-500/20 text-red-300" :
                    issue.severity === "MED" ? "bg-amber-500/20 text-amber-300" :
                    "bg-green-500/20 text-green-300"
                  }`}>{issue.severity}</span>
                  <div>
                    <p className="text-[9px]">{issue.text}</p>
                    <p className="text-[7px] text-muted-foreground">Source: {issue.src}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-1.5 text-[8px] text-muted-foreground">Sourced from Reddit r/dubai + community reports</div>
        </div>
      </div>
      <Overlay color="amber">Building defect & snagging detection</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 7 — COMPARE PROPERTIES
   ═══════════════════════════════════════════ */
function SceneCompare() {
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="w-full max-w-lg animate-scene-scale">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm sm:text-base">⚖️</span>
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground sm:text-xs">Side-by-Side Comparison</div>
        </div>
        <div className="grid grid-cols-3 gap-1.5 sm:gap-2">
          {/* Header */}
          <div />
          <div className={`${panel} p-2 text-center`}>
            <div className="text-[9px] font-semibold text-primary sm:text-[10px]">Marina Gate</div>
            <div className="text-[8px] text-muted-foreground">AED 2.1M</div>
          </div>
          <div className={`${panel} p-2 text-center`}>
            <div className="text-[9px] font-semibold sm:text-[10px]">Princess Tower</div>
            <div className="text-[8px] text-muted-foreground">AED 1.75M</div>
          </div>

          {/* Rows */}
          {[
            { label: "Score", a: "80 (B+)", b: "72 (B)", aWin: true },
            { label: "Yield", a: "6.2%", b: "6.8%", aWin: false },
            { label: "PSF", a: "1,684", b: "1,483", aWin: false },
            { label: "Chiller", a: "29K/yr", b: "18K/yr", aWin: false },
            { label: "Supply", a: "Moderate", b: "Low", aWin: false },
            { label: "Quality", a: "A-", b: "B", aWin: true },
          ].map((row) => (
            <React.Fragment key={row.label}>
              <div className="flex items-center text-[9px] text-muted-foreground sm:text-[10px]">{row.label}</div>
              <div className={`flex items-center justify-center rounded p-1 text-[9px] font-medium sm:text-[10px] ${row.aWin ? "bg-green-500/10 text-green-300" : "bg-muted/10"}`}>
                {row.a} {row.aWin && "🏆"}
              </div>
              <div className={`flex items-center justify-center rounded p-1 text-[9px] font-medium sm:text-[10px] ${!row.aWin ? "bg-green-500/10 text-green-300" : "bg-muted/10"}`}>
                {row.b} {!row.aWin && "🏆"}
              </div>
            </React.Fragment>
          ))}
        </div>
        <div className={`${panel} mt-2 p-2 text-center`}>
          <span className="text-[9px] font-semibold text-green-300 sm:text-[10px]">🏆 Winner: Marina Gate — Higher score & better quality</span>
        </div>
      </div>
      <Overlay color="green">Compare 2-4 properties with scored verdicts</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 8 — MORTGAGE & FINANCIAL TOOLS
   ═══════════════════════════════════════════ */
function SceneMortgage() {
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="flex w-full max-w-xl gap-3">
        {/* Phone with mortgage command */}
        <TelegramFrame>
          <UserMsg text="Calculate mortgage for AED 2.1M, 20% down, 4.5%" time="4:22 PM" />
          <BotMsg time="4:22 PM">
            <p className="text-[9px] font-semibold text-primary sm:text-[10px]">💰 Mortgage Calculator</p>
            <p className="text-[8px] text-muted-foreground sm:text-[9px]">Down: AED 420K (20%)</p>
            <p className="text-[8px] text-muted-foreground sm:text-[9px]">EMI: AED 8,516/mo</p>
            <p className="text-[8px] text-muted-foreground sm:text-[9px]">Total Interest: AED 897K</p>
          </BotMsg>
          <InlineButtons labels={["💰 ROI Calc", "📈 Trends", "✅ Save"]} />
        </TelegramFrame>

        {/* Finance panel */}
        <div className="hidden flex-1 animate-scene-scale space-y-2 sm:block">
          <div className={`${panel} p-3`}>
            <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Financing Breakdown</div>
            <div className="mt-2 space-y-1">
              {[
                { l: "Property Price", v: "AED 2,100,000" },
                { l: "Down Payment (20%)", v: "AED 420,000" },
                { l: "Loan Amount", v: "AED 1,680,000" },
                { l: "Monthly EMI", v: "AED 8,516" },
                { l: "Total Interest (25yr)", v: "AED 897,480" },
                { l: "Total Cost", v: "AED 2,997,480" },
              ].map((r) => (
                <div key={r.l} className="flex justify-between text-[9px] sm:text-[10px]">
                  <span className="text-muted-foreground">{r.l}</span>
                  <span className="font-medium tabular-nums">{r.v}</span>
                </div>
              ))}
            </div>
          </div>
          <div className={`${panel} p-2.5`}>
            <div className="text-[9px] text-muted-foreground">Cash vs Leveraged Yield</div>
            <div className="mt-1 flex gap-3">
              <div>
                <span className="text-[9px] text-muted-foreground">Cash: </span>
                <span className="text-[10px] font-bold text-primary">6.2%</span>
              </div>
              <div>
                <span className="text-[9px] text-muted-foreground">Leveraged: </span>
                <span className="text-[10px] font-bold text-green-400">11.4%</span>
              </div>
              <span className="text-[9px] font-semibold text-green-300">LEVERAGE ✅</span>
            </div>
          </div>
        </div>
      </div>
      <Overlay color="primary">Mortgage calculator with leveraged yield analysis</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 9 — PDF REPORTS + PORTFOLIO + DIGEST
   ═══════════════════════════════════════════ */
function ScenePDFPortfolio() {
  return (
    <div className={`relative flex h-full items-center justify-center ${bg} p-4 sm:p-6`}>
      <div className="flex w-full max-w-xl gap-3 animate-scene-scale">
        {/* PDF Report mock */}
        <div className={`${panel} flex-1 p-3 sm:p-4`}>
          <div className="flex items-center gap-2">
            <span className="text-sm sm:text-base">📄</span>
            <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground sm:text-xs">PDF Due Diligence Report</div>
          </div>
          <div className="mt-2 rounded border border-border/20 bg-[hsl(217,33%,14%)] p-2 sm:mt-3">
            {/* Mini PDF preview */}
            <div className="flex items-center gap-2 border-b border-border/20 pb-1.5">
              <div className="flex h-5 w-5 items-center justify-center rounded bg-primary/20 text-[7px] font-bold text-primary">TV</div>
              <div className="text-[9px] font-semibold">TrueValue.ae — Investment Report</div>
            </div>
            <div className="mt-1.5 grid grid-cols-2 gap-1.5">
              <div className="rounded bg-muted/10 p-1.5 text-center">
                <div className="text-[7px] text-muted-foreground">Score Gauge</div>
                <div className="text-lg font-bold text-green-400">80</div>
              </div>
              <div className="rounded bg-muted/10 p-1.5 text-center">
                <div className="text-[7px] text-muted-foreground">Pillar Radar</div>
                <div className="text-lg">📊</div>
              </div>
            </div>
            <div className="mt-1.5 space-y-0.5">
              <div className="h-1.5 w-full rounded bg-muted/20" />
              <div className="h-1.5 w-4/5 rounded bg-muted/15" />
              <div className="h-1.5 w-3/4 rounded bg-muted/10" />
            </div>
          </div>
          <div className="mt-1.5 text-[8px] text-muted-foreground">Multi-page A4 with charts · Pro plan</div>
        </div>

        {/* Portfolio + Digest */}
        <div className="hidden w-44 flex-col gap-2 sm:flex">
          {/* Watchlist */}
          <div className={`${panel} p-2.5`}>
            <div className="flex items-center gap-1.5">
              <span className="text-xs">📋</span>
              <span className="text-[9px] font-semibold">Portfolio Watchlist</span>
            </div>
            <div className="mt-1.5 space-y-1">
              {["Marina Gate T2", "Palm Jumeirah 3BR", "JVC Studio"].map((p) => (
                <div key={p} className="flex items-center justify-between rounded bg-muted/10 px-1.5 py-0.5">
                  <span className="text-[8px]">{p}</span>
                  <span className="text-[7px] text-green-300">✓</span>
                </div>
              ))}
            </div>
          </div>
          {/* Market Digest */}
          <div className={`${panel} p-2.5`}>
            <div className="flex items-center gap-1.5">
              <span className="text-xs">📰</span>
              <span className="text-[9px] font-semibold">Market Digest</span>
            </div>
            <div className="mt-1 text-[8px] text-muted-foreground">Daily/weekly updates for your zones</div>
            <div className="mt-1 flex flex-wrap gap-0.5">
              {["Marina", "JVC", "Downtown"].map((z) => (
                <span key={z} className="rounded bg-primary/10 px-1 py-0.5 text-[7px] font-medium text-primary">{z}</span>
              ))}
            </div>
          </div>
          {/* Voice */}
          <div className={`${panel} p-2.5`}>
            <div className="flex items-center gap-1.5">
              <span className="text-xs">🎤</span>
              <span className="text-[9px] font-semibold">Voice Queries</span>
            </div>
            <div className="mt-1 text-[8px] text-muted-foreground">Send voice messages — AI transcribes via Whisper</div>
          </div>
        </div>
      </div>
      <Overlay color="primary">PDF reports, portfolio tracking, voice & market digest</Overlay>
    </div>
  );
}

/* ═══════════════════════════════════════════
   SCENE 10 — CTA
   ═══════════════════════════════════════════ */
function SceneCTA() {
  const features = [
    "12 Analysis Tools", "15+ Zones", "4-Pillar Scoring",
    "Chiller Detection", "DLD Transactions", "Building Intel",
    "Property Compare", "Mortgage Calc", "PDF Reports",
    "Voice Queries", "Market Digest", "Portfolio Tracking",
  ];
  return (
    <div className={`relative flex h-full flex-col items-center justify-center ${bg} p-6`}>
      <div className="animate-scene-scale text-center">
        <div className="flex items-center justify-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/20 sm:h-14 sm:w-14">
            <span className="text-xl font-bold text-primary sm:text-2xl">TV</span>
          </div>
        </div>
        <h3 className="mt-3 text-xl font-bold sm:text-2xl">
          TrueValue<span className="text-primary">.ae</span>
        </h3>
        <p className="mt-1 text-xs text-muted-foreground sm:text-sm">All of this — free on Telegram</p>
      </div>

      {/* Feature cloud */}
      <div className="mt-4 flex max-w-md flex-wrap justify-center gap-1 sm:mt-5 sm:gap-1.5">
        {features.map((f) => (
          <span key={f} className="rounded-full border border-primary/20 bg-primary/5 px-2 py-0.5 text-[8px] font-medium text-primary/80 sm:px-2.5 sm:text-[9px]">
            {f}
          </span>
        ))}
      </div>

      <div className="mt-4 rounded-lg border border-primary/30 bg-primary/10 px-5 py-2.5 text-center animate-scene-float sm:mt-5">
        <div className="text-xs font-semibold text-primary sm:text-sm">Start Free on Telegram</div>
        <div className="mt-0.5 text-[9px] text-muted-foreground sm:text-xs">@TrueValueAE_bot · No sign-up required</div>
      </div>
    </div>
  );
}

/* React import needed for Fragment in SceneCompare */
import React from "react";
