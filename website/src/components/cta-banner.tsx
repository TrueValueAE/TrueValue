import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const TELEGRAM_URL = "https://t.me/TrueValueAE_bot";

export function CTABanner() {
  return (
    <section className="border-y border-border/40 bg-secondary/30 py-20 sm:py-28">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
          Ready to Make Smarter{" "}
          <span className="text-primary">Property Decisions?</span>
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Join investors who use TrueValue.ae to avoid costly mistakes and find
          the best deals in Dubai real estate.
        </p>
        <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
          <Button asChild size="lg" className="gap-2 px-8 text-base font-semibold">
            <a href={TELEGRAM_URL} target="_blank" rel="noopener noreferrer">
              Start Free on Telegram
              <ArrowRight className="h-4 w-4" />
            </a>
          </Button>
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          3 free queries per day — no sign-up required
        </p>
      </div>
    </section>
  );
}
