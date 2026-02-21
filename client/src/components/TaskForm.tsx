import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Loader2 } from "lucide-react";

interface TaskFormProps {
  onSubmit: (goal: string, context?: string, demoMode?: boolean) => void;
  isLoading?: boolean;
}

export function TaskForm({ onSubmit, isLoading = false }: TaskFormProps) {
  const [goal, setGoal] = useState("");
  const [context, setContext] = useState("");
  const [demoMode, setDemoMode] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (goal.trim()) {
      onSubmit(goal, context || undefined, demoMode);
    }
  };

  return (
    <Card className="card-brutalist">
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-white font-black text-xl mb-3 uppercase tracking-wider">
            Task Goal
          </label>
          <Textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Enter your task goal (e.g., 'Register a new account on example.com')"
            className="input-brutalist min-h-24 font-mono"
            disabled={isLoading}
          />
          <p className="text-gray-400 text-sm mt-2 font-mono">
            Describe what you want the agent to do
          </p>
        </div>

        <div className="divider-red" />

        <div>
          <label className="block text-white font-black text-xl mb-3 uppercase tracking-wider">
            Additional Context (Optional)
          </label>
          <Textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Add any additional context or instructions..."
            className="input-brutalist min-h-20 font-mono"
            disabled={isLoading}
          />
        </div>

        <div className="divider-red" />

        <div className="flex items-center gap-4">
          <input
            type="checkbox"
            id="demoMode"
            checked={demoMode}
            onChange={(e) => setDemoMode(e.target.checked)}
            disabled={isLoading}
            className="w-6 h-6 border-2 border-white cursor-pointer"
          />
          <label htmlFor="demoMode" className="text-white font-black uppercase tracking-wider cursor-pointer">
            Demo Mode (Simulate Actions)
          </label>
        </div>

        <div className="divider-red" />

        <Button
          type="submit"
          disabled={!goal.trim() || isLoading}
          className="btn-brutalist-red w-full"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Starting Task...
            </>
          ) : (
            "START TASK"
          )}
        </Button>
      </form>
    </Card>
  );
}
