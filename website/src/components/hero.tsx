import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Bot } from "lucide-react";

const TELEGRAM_URL = "https://t.me/TrueValueAE_bot";

export function Hero() {
  return (
    <section className="relative flex min-h-[90vh] items-center justify-center overflow-hidden pt-16">
      {/* Background gradient effects */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute left-1/2 top-0 h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-[300px] w-[400px] rounded-full bg-primary/3 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-4xl px-4 text-center sm:px-6">
        <Badge variant="secondary" className="mb-6 gap-1.5 px-3 py-1.5 text-xs">
          <Bot className="h-3.5 w-3.5" />
          AI-Powered Telegram Bot
        </Badge>

        <h1 className="text-balance text-4xl font-bold leading-tight tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
          Institutional-Grade Property Due Diligence{" "}
          <span className="text-primary">for Dubai</span>
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-balance text-lg text-muted-foreground sm:text-xl">
          Don&apos;t risk AED 100K-500K on hidden costs, overpriced deals, or
          building defects. Get AI-scored verdicts on any Dubai property in under
          60 seconds.
        </p>

        <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button asChild size="lg" className="gap-2 px-8 text-base font-semibold">
            <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer">
              Start Free Analysis
              <ArrowRight className="h-4 w-4" />
            </a>
          </Button>
          <Button asChild variant="outline" size="lg" className="gap-2 px-8 text-base">
            <a href="#how-it-works">See How It Works</a>
          </Button>
        </div>

        <p className="mt-6 text-sm text-muted-foreground">
          Free tier available — no credit card required
        </p>
      </div>
    </section>
  );
}
