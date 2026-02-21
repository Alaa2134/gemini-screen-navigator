import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Pause, Play, X, CheckCircle, AlertCircle } from "lucide-react";

interface ExecutionDashboardProps {
  taskId: string;
  goal: string;
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
}

interface TaskStatus {
  taskId: string;
  status: "running" | "paused" | "completed" | "failed" | "waiting_approval";
  progress: number;
  currentStep: number;
  totalSteps: number;
  logs: string[];
  screenshots: Array<{
    step: number;
    before: string;
    after: string;
  }>;
}

export function ExecutionDashboard({
  taskId,
  goal,
  onPause,
  onResume,
  onCancel,
}: ExecutionDashboardProps) {
  const [status, setStatus] = useState<TaskStatus | null>(null);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    // Simulate polling for task status
    const interval = setInterval(() => {
      // In real implementation, fetch from API
      setStatus({
        taskId,
        status: "running",
        progress: Math.min(100, (status?.progress || 0) + 10),
        currentStep: (status?.currentStep || 0) + 1,
        totalSteps: 5,
        logs: [
          ...(status?.logs || []),
          `[${new Date().toLocaleTimeString()}] Step ${(status?.currentStep || 0) + 1} completed`,
        ],
        screenshots: status?.screenshots || [],
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [taskId, status]);

  if (!status) {
    return (
      <Card className="card-brutalist">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-red-600 mr-3" />
          <span className="text-white font-black text-lg">Loading...</span>
        </div>
      </Card>
    );
  }

  const statusColor = {
    running: "bg-red-600",
    paused: "bg-yellow-600",
    completed: "bg-green-600",
    failed: "bg-red-900",
    waiting_approval: "bg-blue-600",
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="card-brutalist">
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-white font-black text-3xl uppercase tracking-wider">
                Task Execution
              </h2>
              <p className="text-gray-400 font-mono mt-2">{goal}</p>
            </div>
            <Badge className={`${statusColor[status.status]} text-white font-black uppercase`}>
              {status.status}
            </Badge>
          </div>

          <div className="divider-red" />

          {/* Progress */}
          <div>
            <div className="flex justify-between mb-2">
              <span className="text-white font-black uppercase">Progress</span>
              <span className="text-white font-black">
                {status.currentStep} / {status.totalSteps}
              </span>
            </div>
            <Progress value={status.progress} className="h-2 bg-gray-800" />
            <p className="text-gray-400 text-sm mt-2 font-mono">{status.progress}%</p>
          </div>

          <div className="divider-red" />

          {/* Controls */}
          <div className="flex gap-3">
            {status.status === "running" && (
              <Button
                onClick={() => {
                  setIsPaused(true);
                  onPause?.();
                }}
                className="btn-brutalist flex-1"
              >
                <Pause className="mr-2 h-4 w-4" />
                PAUSE
              </Button>
            )}
            {status.status === "paused" && (
              <Button
                onClick={() => {
                  setIsPaused(false);
                  onResume?.();
                }}
                className="btn-brutalist flex-1"
              >
                <Play className="mr-2 h-4 w-4" />
                RESUME
              </Button>
            )}
            <Button
              onClick={onCancel}
              className="btn-brutalist flex-1 border-red-600 text-red-600 hover:bg-red-600 hover:text-white"
            >
              <X className="mr-2 h-4 w-4" />
              CANCEL
            </Button>
          </div>
        </div>
      </Card>

      {/* Logs */}
      <Card className="card-brutalist">
        <h3 className="text-white font-black text-2xl uppercase tracking-wider mb-4">
          Execution Logs
        </h3>
        <div className="bg-black border-2 border-white p-4 max-h-64 overflow-y-auto font-mono text-sm text-green-400">
          {status.logs.length === 0 ? (
            <p className="text-gray-500">No logs yet...</p>
          ) : (
            status.logs.map((log, i) => (
              <div key={i} className="mb-1">
                {log}
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Step Information */}
      <Card className="card-brutalist">
        <h3 className="text-white font-black text-2xl uppercase tracking-wider mb-4">
          Current Step
        </h3>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Loader2 className="h-6 w-6 animate-spin text-red-600" />
            <span className="text-white font-black text-lg">
              Step {status.currentStep} of {status.totalSteps}
            </span>
          </div>
          <p className="text-gray-400 font-mono">
            Executing action and capturing evidence...
          </p>
        </div>
      </Card>
    </div>
  );
}
