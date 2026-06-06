import { HistoryGallery } from "@/components/history-gallery";

export default function HistoryPage() {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold tracking-normal">History</h1>
      <HistoryGallery />
    </section>
  );
}
