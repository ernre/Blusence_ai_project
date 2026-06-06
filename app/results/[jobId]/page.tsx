import { ResultView } from "@/components/result-view";

export default function ResultPage({ params }: Readonly<{ params: { jobId: string } }>) {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold tracking-normal">Result {params.jobId}</h1>
      <ResultView jobId={params.jobId} />
    </section>
  );
}
