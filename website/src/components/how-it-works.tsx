import { Card, CardContent } from "@/components/ui/card";
import { MessageSquare, Brain, CheckCircle } from "lucide-react";

const steps = [
  {
    number: "01",
    icon: MessageSquare,
    title: "Ask",
    description:
      "Send a property name, location, or question to the TrueValue.ae Telegram bot. Natural language — no forms or logins.",
    example: '"Analyze Marina Gate Tower 2 for investment"',
  },
  {
    number: "02",
    icon: Brain,
    title: "AI Analyzes",
    description:
      "Our AI engine runs 12 specialized tools: price comparison, chiller costs, supply pipeline, building quality, rental yield, and more.",
    example: "Cross-references live data from DLD, Bayut, Property Finder",
  },
  {
    number: "03",
    icon: CheckCircle,
    title: "Get Your Verdict",
    description:
      "Receive a scored A-F verdict with detailed breakdown, risk flags, and a clear buy/hold/avoid recommendation — all in under 60 seconds.",
    example: "Grade: B+ | Estimated Fair Value: AED 1.85M",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            How It <span className="text-primary">Works</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            From question to verdict in three simple steps.
          </p>
        </div>

        <div className="mt-14 grid gap-8 md:grid-cols-3">
          {steps.map((step, i) => (
            <Card
              key={step.number}
              className="relative border-border/50 bg-card/50"
            >
              <CardContent className="p-6">
                {/* Step number */}
                <span className="text-5xl font-bold text-primary/15">
                  {step.number}
                </span>

                <div className="mt-2 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                    <step.icon className="h-5 w-5 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold">{step.title}</h3>
                </div>

                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
                  {step.description}
                </p>

                {/* Example message */}
                <div className="mt-4 rounded-md border border-border/50 bg-background/50 px-3 py-2">
                  <p className="text-xs italic text-muted-foreground">
                    {step.example}
                  </p>
                </div>
              </CardContent>

              {/* Connector arrow (hidden on last and mobile) */}
              {i < steps.length - 1 && (
                <div className="absolute -right-4 top-1/2 z-10 hidden -translate-y-1/2 text-primary/30 md:block">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
