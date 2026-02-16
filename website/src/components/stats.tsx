import { MapPin, Wrench, Clock, Building2 } from "lucide-react";

const stats = [
  {
    icon: MapPin,
    value: "15+",
    label: "Dubai Zones Covered",
    description: "From Downtown to JVC, Marina to Dubai Hills",
  },
  {
    icon: Wrench,
    value: "12",
    label: "Analysis Tools",
    description: "Comprehensive due diligence toolkit",
  },
  {
    icon: Clock,
    value: "<60s",
    label: "Analysis Time",
    description: "Instant AI-powered verdicts",
  },
  {
    icon: Building2,
    value: "AED 500B+",
    label: "Market Covered",
    description: "Dubai's total real estate market value",
  },
];

export function Stats() {
  return (
    <section className="py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Built for the <span className="text-primary">Dubai Market</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Purpose-built AI trained on Dubai real estate data, regulations, and
            market dynamics.
          </p>
        </div>

        <div className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                <stat.icon className="h-7 w-7 text-primary" />
              </div>
              <div className="mt-4 text-4xl font-bold text-foreground">
                {stat.value}
              </div>
              <div className="mt-1 font-medium">{stat.label}</div>
              <p className="mt-1 text-sm text-muted-foreground">
                {stat.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
