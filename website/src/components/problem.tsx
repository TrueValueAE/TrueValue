import { Card, CardContent } from "@/components/ui/card";
import { Thermometer, TrendingDown, AlertTriangle, BarChart3 } from "lucide-react";

const painPoints = [
  {
    icon: Thermometer,
    title: "Hidden Chiller Costs",
    description:
      "District cooling fees can add AED 15,000-40,000/year to ownership costs — often undisclosed until after purchase.",
  },
  {
    icon: TrendingDown,
    title: "Overpriced Deals",
    description:
      "Without comparable transaction data, buyers routinely overpay 10-20% above fair market value.",
  },
  {
    icon: AlertTriangle,
    title: "Building Defects",
    description:
      "Structural issues, poor maintenance, and service charge disputes cost owners hundreds of thousands in unexpected repairs.",
  },
  {
    icon: BarChart3,
    title: "Market Oversupply",
    description:
      "Certain zones face 30-40% upcoming supply increases that will depress rental yields and resale values.",
  },
];

export function Problem() {
  return (
    <section id="problem" className="py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Dubai Property Investment Is a{" "}
            <span className="text-primary">Minefield</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Most buyers discover these costly problems after signing the contract.
          </p>
        </div>

        <div className="mt-14 grid gap-6 sm:grid-cols-2">
          {painPoints.map((point) => (
            <Card
              key={point.title}
              className="border-border/50 bg-card/50 transition-colors hover:border-primary/30"
            >
              <CardContent className="flex gap-4 p-6">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <point.icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">{point.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                    {point.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
