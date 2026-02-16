import { Badge } from "@/components/ui/badge";
import {
  Search,
  Calculator,
  FileCheck,
  Globe,
  MapPin,
  Shield,
  TrendingUp,
  Building,
  Layers,
  Zap,
  BarChart,
  Scale,
} from "lucide-react";

const tools = [
  { icon: Search, label: "Property Search" },
  { icon: Calculator, label: "ROI Calculator" },
  { icon: FileCheck, label: "Due Diligence Report" },
  { icon: Globe, label: "Live Web Validation" },
  { icon: MapPin, label: "Zone Analysis" },
  { icon: Shield, label: "Risk Assessment" },
  { icon: TrendingUp, label: "Market Trends" },
  { icon: Building, label: "Building Quality" },
  { icon: Layers, label: "Supply Pipeline" },
  { icon: Zap, label: "Chiller Analysis" },
  { icon: BarChart, label: "Rental Yield" },
  { icon: Scale, label: "Price Comparison" },
];

const highlights = [
  { value: "12", label: "Analysis Tools" },
  { value: "15+", label: "Dubai Zones" },
  { value: "A-F", label: "Scored Verdicts" },
  { value: "Live", label: "Web Validation" },
];

export function Solution() {
  return (
    <section id="solution" className="border-y border-border/40 bg-secondary/30 py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <Badge variant="secondary" className="mb-4">
            The Solution
          </Badge>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            AI That Does the Due Diligence{" "}
            <span className="text-primary">For You</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            TrueValue.ae combines 12 specialized analysis tools with live market
            data to give you institutional-grade insights via a simple Telegram
            chat.
          </p>
        </div>

        {/* Highlight numbers */}
        <div className="mt-14 grid grid-cols-2 gap-6 sm:grid-cols-4">
          {highlights.map((h) => (
            <div key={h.label} className="text-center">
              <div className="text-3xl font-bold text-primary">{h.value}</div>
              <div className="mt-1 text-sm text-muted-foreground">{h.label}</div>
            </div>
          ))}
        </div>

        {/* Tools grid */}
        <div className="mt-14 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {tools.map((tool) => (
            <div
              key={tool.label}
              className="flex flex-col items-center gap-2 rounded-lg border border-border/50 bg-card/60 p-4 text-center transition-colors hover:border-primary/30"
            >
              <tool.icon className="h-5 w-5 text-primary" />
              <span className="text-xs font-medium text-muted-foreground">
                {tool.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
