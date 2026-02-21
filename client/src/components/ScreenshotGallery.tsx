import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface Screenshot {
  step: number;
  before: string;
  after: string;
  description: string;
}

interface ScreenshotGalleryProps {
  screenshots: Screenshot[];
  title?: string;
}

export function ScreenshotGallery({
  screenshots,
  title = "Evidence Gallery",
}: ScreenshotGalleryProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (screenshots.length === 0) {
    return (
      <Card className="card-brutalist">
        <p className="text-gray-400 font-mono">No screenshots available yet</p>
      </Card>
    );
  }

  const current = screenshots[currentIndex];

  const goToPrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? screenshots.length - 1 : prev - 1));
  };

  const goToNext = () => {
    setCurrentIndex((prev) => (prev === screenshots.length - 1 ? 0 : prev + 1));
  };

  return (
    <Card className="card-brutalist">
      <h3 className="text-white font-black text-2xl uppercase tracking-wider mb-6">
        {title}
      </h3>

      <div className="space-y-6">
        {/* Main Display */}
        <div className="grid grid-cols-2 gap-4">
          {/* Before */}
          <div>
            <p className="text-white font-black uppercase text-sm mb-2">BEFORE</p>
            <div className="border-2 border-white bg-black aspect-video flex items-center justify-center overflow-hidden">
              <img
                src={current.before}
                alt="Before screenshot"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* After */}
          <div>
            <p className="text-white font-black uppercase text-sm mb-2">AFTER</p>
            <div className="border-2 border-white bg-black aspect-video flex items-center justify-center overflow-hidden">
              <img
                src={current.after}
                alt="After screenshot"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>

        <div className="divider-red" />

        {/* Step Info */}
        <div>
          <p className="text-white font-black uppercase text-sm mb-2">Step {current.step}</p>
          <p className="text-gray-300 font-mono">{current.description}</p>
        </div>

        <div className="divider-red" />

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            onClick={goToPrevious}
            className="btn-brutalist"
            disabled={screenshots.length <= 1}
          >
            <ChevronLeft className="h-5 w-5" />
          </Button>

          <span className="text-white font-black uppercase tracking-wider">
            {currentIndex + 1} / {screenshots.length}
          </span>

          <Button
            onClick={goToNext}
            className="btn-brutalist"
            disabled={screenshots.length <= 1}
          >
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>

        {/* Thumbnails */}
        {screenshots.length > 1 && (
          <>
            <div className="divider-red" />
            <div className="grid grid-cols-6 gap-2">
              {screenshots.map((shot, idx) => (
                <button
                  key={idx}
                  onClick={() => setCurrentIndex(idx)}
                  className={`aspect-square border-2 ${
                    idx === currentIndex ? "border-red-600 bg-red-600" : "border-white"
                  } hover:border-red-600 transition-all`}
                >
                  <span className="text-white font-black text-xs">{shot.step}</span>
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    </Card>
  );
}
