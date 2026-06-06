import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { JobProgress } from "@/components/job-progress";

describe("JobProgress", () => {
  it("shows queued state", () => {
    render(<JobProgress status="queued" />);

    expect(screen.getByText("Queued")).toBeInTheDocument();
  });

  it("shows actionable error state", () => {
    render(<JobProgress status="error" error="Bad mask" />);

    expect(screen.getByText("Try-on failed")).toBeInTheDocument();
    expect(screen.getByText("Bad mask")).toBeInTheDocument();
  });
});
