import { HealthWidget } from "@/components/health-widget";

export default function HealthPage() {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold tracking-normal">Health</h1>
      <HealthWidget />
    </section>
  );
}
