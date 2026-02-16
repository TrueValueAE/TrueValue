"use client";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqs = [
  {
    question: "How does TrueValue.ae work?",
    answer:
      "TrueValue.ae is a Telegram bot that uses artificial intelligence to analyze Dubai properties. Simply send a property name, building, or zone, and our AI runs 12 specialized analysis tools — including price comparisons, chiller cost estimates, supply pipeline analysis, and risk assessment — to deliver a scored verdict in under 60 seconds.",
  },
  {
    question: "What data sources does TrueValue use?",
    answer:
      "We aggregate data from multiple sources including Dubai Land Department (DLD) transaction records, major property portals (Bayut, Property Finder), district cooling providers, developer announcements, and market research reports. Our AI cross-references these sources for accuracy.",
  },
  {
    question: "Is the free tier really free?",
    answer:
      "Yes. The free tier gives you 3 queries per day with basic property search and zone overviews. No credit card is required — just open the Telegram bot and start asking questions. Upgrade anytime if you need more queries or advanced features.",
  },
  {
    question: "How accurate are the property valuations?",
    answer:
      "Our AI-generated valuations are based on comparable transaction data from DLD and current market listings. While they provide strong directional guidance, they should be used alongside professional valuations for final purchase decisions. We grade confidence levels from A (highest) to F (lowest).",
  },
  {
    question: "Which areas of Dubai do you cover?",
    answer:
      "We currently cover 15+ major zones including Downtown Dubai, Dubai Marina, JBR, Business Bay, JVC, Dubai Hills, Palm Jumeirah, DIFC, Dubai Creek Harbour, Arabian Ranches, MBR City, and more. We're constantly expanding coverage.",
  },
  {
    question: "Can I get a detailed PDF report?",
    answer:
      "PDF due diligence reports are available on the Pro plan (AED 299/mo). These include comprehensive property analysis, comparable sales data, risk assessment, rental yield projections, and investment recommendations — ready to share with partners or advisors.",
  },
  {
    question: "What is chiller cost analysis?",
    answer:
      "Many Dubai buildings use district cooling (chiller) systems where costs can range from AED 15,000 to AED 40,000+ per year. Our chiller analysis identifies whether a property uses district or individual cooling, estimates annual costs, and flags properties with unusually high chiller fees.",
  },
  {
    question: "Is my data secure?",
    answer:
      "We take data security seriously. Conversations are encrypted, we don't store personal financial data, and we never share your queries or analysis results with third parties. Our infrastructure is hosted on enterprise-grade cloud services with full encryption at rest and in transit.",
  },
];

export function FAQ() {
  return (
    <section id="faq" className="py-20 sm:py-28">
      <div className="mx-auto max-w-3xl px-4 sm:px-6">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Frequently Asked <span className="text-primary">Questions</span>
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to know about TrueValue.ae.
          </p>
        </div>

        <Accordion type="single" collapsible className="mt-12">
          {faqs.map((faq, i) => (
            <AccordionItem key={i} value={`item-${i}`}>
              <AccordionTrigger className="text-left text-base">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </section>
  );
}
