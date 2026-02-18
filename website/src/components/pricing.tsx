import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check } from "lucide-react";

const TELEGRAM_URL = "https://t.me/TrueValueAE_bot";

const tiers = [
  {
    name: "Free",
    price: "AED 0",
    period: "/mo",
    description: "Try it out — no commitment",
    popular: false,
    features: [
      "3 queries per day",
      "Basic property search",
      "Zone overview",
      "Community support",
    ],
    cta: "Start Free",
  },
  {
    name: "Basic",
    price: "AED 99",
    period: "/mo",
    description: "For active property seekers",
    popular: false,
    features: [
      "20 queries per day",
      "Chiller cost analysis",
      "ROI calculator",
      "Price comparisons",
      "Email support",
    ],
    cta: "Get Basic",
  },
  {
    name: "Pro",
    price: "AED 299",
    period: "/mo",
    description: "For serious investors",
    popular: true,
    features: [
      "100 queries per day",
      "PDF due diligence reports",
      "Portfolio tracking",
      "API access",
      "Supply pipeline data",
      "Priority support",
    ],
    cta: "Get Pro",
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For brokerages & funds",
    popular: false,
    features: [
      "Unlimited queries",
      "White-label solution",
      "SLA guarantee",
      "Dedicated account manager",
      "Custom integrations",
      "Bulk analysis tools",
    ],
    cta: "Contact Us",
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="border-y border-border/40 bg-secondary/30 py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Simple, Transparent <span className="text-primary">Pricing</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Start free. Upgrade when you need more power.
          </p>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {tiers.map((tier) => (
            <Card
              key={tier.name}
              className={`relative flex flex-col border-border/50 bg-card/50 ${
                tier.popular
                  ? "border-primary/50 shadow-lg shadow-primary/5"
                  : ""
              }`}
            >
              {tier.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2">
                  Most Popular
                </Badge>
              )}
              <CardHeader className="pb-4">
                <CardTitle className="text-lg">{tier.name}</CardTitle>
                <div className="mt-2">
                  <span className="text-3xl font-bold">{tier.price}</span>
                  <span className="text-sm text-muted-foreground">
                    {tier.period}
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  {tier.description}
                </p>
              </CardHeader>
              <CardContent className="flex flex-1 flex-col">
                <ul className="flex-1 space-y-2.5">
                  {tier.features.map((feature) => (
                    <li
                      key={feature}
                      className="flex items-start gap-2 text-sm"
                    >
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                      <span className="text-muted-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Button
                  asChild
                  variant={tier.popular ? "default" : "outline"}
                  className="mt-6 w-full"
                >
                  <a
                    href={TELEGRAM_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {tier.cta}
                  </a>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
