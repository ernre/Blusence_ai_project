import { TryOnStudio } from "@/components/tryon-studio";

export default function StudioPage() {
  return (
    <section className="grid gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-normal">Try-on Studio</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">
          Upload a person photo and garment image, then run a mock or live VPE try-on job.
        </p>
      </div>
      <TryOnStudio />
    </section>
  );
}
