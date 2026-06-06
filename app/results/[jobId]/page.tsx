import { ResultView } from "@/components/result-view";

export default async function ResultPage({
  params,
}: Readonly<{ params: Promise<{ jobId: string }> }>) {
  const { jobId } = await params;

  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold tracking-normal">Result {jobId}</h1>
      <ResultView jobId={jobId} />
    </section>
  );
}
