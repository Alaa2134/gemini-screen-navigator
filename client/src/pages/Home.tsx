import { useState } from "react";
import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { getLoginUrl } from "@/const";
import { TaskForm } from "@/components/TaskForm";
import { ExecutionDashboard } from "@/components/ExecutionDashboard";
import { ScreenshotGallery } from "@/components/ScreenshotGallery";

type Page = "home" | "execution" | "results";

export default function Home() {
  const { user, isAuthenticated, loading } = useAuth();
  const [currentPage, setCurrentPage] = useState<Page>("home");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [taskGoal, setTaskGoal] = useState<string>("");

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-white font-black text-3xl uppercase tracking-wider">
          Loading...
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-8">
        <div className="max-w-2xl text-center space-y-8">
          <h1 className="text-6xl md:text-7xl font-black uppercase tracking-wider">
            Gemini Screen Navigator
          </h1>

          <div className="divider-red" />

          <p className="text-2xl font-black uppercase tracking-wider">
            AI-Powered Desktop Automation
          </p>

          <p className="text-gray-300 font-mono text-lg">
            Automate complex tasks on your desktop using Google Gemini AI.
            Watch the agent perceive, plan, act, and verify in real-time.
          </p>

          <div className="divider-red" />

          <div className="space-y-4">
            <p className="text-gray-400 font-mono">
              Sign in to start automating your tasks
            </p>
            <Button
              onClick={() => (window.location.href = getLoginUrl())}
              className="btn-brutalist-red w-full md:w-auto px-12"
            >
              Sign In
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const handleTaskSubmit = (goal: string, context?: string, demoMode?: boolean) => {
    const newTaskId = `task_${Date.now()}`;
    setTaskId(newTaskId);
    setTaskGoal(goal);
    setCurrentPage("execution");
  };

  return (
    <div className="min-h-screen bg-black text-white">
      <header className="border-b-4 border-white p-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black uppercase tracking-wider">
              Gemini Navigator
            </h1>
            <p className="text-gray-400 font-mono mt-2">
              {user?.name || "User"} • AI Desktop Automation
            </p>
          </div>
          <div className="text-right">
            <p className="text-gray-400 font-mono text-sm">
              {new Date().toLocaleString()}
            </p>
          </div>
        </div>
      </header>

      <div className="h-1 bg-red-600" />

      <main className="max-w-7xl mx-auto p-8">
        {currentPage === "home" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-5xl font-black uppercase tracking-wider mb-4">
                Start New Task
              </h2>
              <p className="text-gray-400 font-mono mb-8">
                Describe what you want the AI agent to do on your desktop
              </p>
            </div>

            <TaskForm onSubmit={handleTaskSubmit} />

            <div className="space-y-4">
              <h3 className="text-3xl font-black uppercase tracking-wider">
                Demo Scenarios
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  {
                    title: "Website Registration",
                    description: "Register a new account on a demo website",
                  },
                  {
                    title: "Bug Finding",
                    description: "Identify UI bugs and generate report",
                  },
                ].map((demo, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      handleTaskSubmit(demo.description, "", true);
                    }}
                    className="card-brutalist hover:bg-red-600 hover:text-black transition-all text-left"
                  >
                    <h4 className="font-black text-xl uppercase tracking-wider mb-2">
                      {demo.title}
                    </h4>
                    <p className="text-gray-300 font-mono">{demo.description}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {currentPage === "execution" && taskId && (
          <ExecutionDashboard
            taskId={taskId}
            goal={taskGoal}
            onCancel={() => setCurrentPage("home")}
          />
        )}

        {currentPage === "results" && (
          <div className="space-y-8">
            <h2 className="text-5xl font-black uppercase tracking-wider">
              Task Complete
            </h2>

            <ScreenshotGallery
              screenshots={[
                {
                  step: 1,
                  before: "https://via.placeholder.com/800x600?text=Before",
                  after: "https://via.placeholder.com/800x600?text=After",
                  description: "Clicked on registration button",
                },
              ]}
            />

            <div className="card-brutalist">
              <h3 className="text-2xl font-black uppercase tracking-wider mb-4">
                Summary
              </h3>
              <div className="space-y-2 font-mono text-gray-300">
                <p>✓ Task completed successfully</p>
                <p>✓ 5 steps executed</p>
                <p>✓ 100% success rate</p>
                <p>✓ Duration: 45 seconds</p>
              </div>
            </div>

            <Button
              onClick={() => setCurrentPage("home")}
              className="btn-brutalist-red w-full"
            >
              Start New Task
            </Button>
          </div>
        )}
      </main>
    </div>
  );
}
