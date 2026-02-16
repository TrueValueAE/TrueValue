import { Navbar } from "@/components/navbar";
import { Hero } from "@/components/hero";
import { Problem } from "@/components/problem";
import { Solution } from "@/components/solution";
import { HowItWorks } from "@/components/how-it-works";
import { Pricing } from "@/components/pricing";
import { Stats } from "@/components/stats";
import { FAQ } from "@/components/faq";
import { CTABanner } from "@/components/cta-banner";
import { Footer } from "@/components/footer";
import { HeroVideo } from "@/components/hero-video";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <HeroVideo />
        <Problem />
        <Solution />
        <HowItWorks />
        <Pricing />
        <Stats />
        <FAQ />
        <CTABanner />
      </main>
      <Footer />
    </>
  );
}
