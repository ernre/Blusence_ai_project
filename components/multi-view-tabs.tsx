"use client";

import { BeforeAfterSlider } from "@/components/before-after-slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

type MultiViewTabsProps = {
  sourceImages: string[];
  resultImages: string[];
};

export function MultiViewTabs({ sourceImages, resultImages }: MultiViewTabsProps) {
  const count = Math.max(resultImages.length, 1);
  const fallbackBefore = sourceImages[0] ?? resultImages[0];

  return (
    <Tabs defaultValue="view-0" className="w-full">
      {count > 1 ? (
        <TabsList aria-label="Result views">
          {Array.from({ length: count }).map((_, index) => (
            <TabsTrigger key={index} value={`view-${index}`}>
              View {index + 1}
            </TabsTrigger>
          ))}
        </TabsList>
      ) : null}
      {Array.from({ length: count }).map((_, index) => (
        <TabsContent key={index} value={`view-${index}`}>
          <BeforeAfterSlider
            beforeImage={sourceImages[index] ?? fallbackBefore}
            afterImage={resultImages[index] ?? resultImages[0]}
            label={`view ${index + 1}`}
          />
        </TabsContent>
      ))}
    </Tabs>
  );
}
