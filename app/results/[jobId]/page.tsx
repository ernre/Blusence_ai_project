export default function ResultPage({ params }: Readonly<{ params: { jobId: string } }>) {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold tracking-normal">Result {params.jobId}</h1>
      <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
        Result polling arrives in F3.
      </div>
    </section>
  );
}
