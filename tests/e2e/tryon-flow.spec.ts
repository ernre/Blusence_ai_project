import { expect, test } from "@playwright/test";

const tinyPng = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
  "base64",
);

test("mock try-on happy path", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Person photos").setInputFiles({
    name: "person.png",
    mimeType: "image/png",
    buffer: tinyPng,
  });
  await page.getByRole("button", { name: "Teal jacket" }).click();
  await page.getByRole("button", { name: "Run try-on" }).click();

  await expect(page).toHaveURL(/\/results\/mock_/);
  await expect(page.getByText("Result ready")).toBeVisible({ timeout: 6000 });
  await expect(page.getByRole("link", { name: "Download" })).toBeVisible();
});
