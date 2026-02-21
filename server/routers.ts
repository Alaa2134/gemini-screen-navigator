import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { z } from "zod";

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  navigator: router({
    startTask: protectedProcedure
      .input(z.object({
        goal: z.string().min(1, "Goal is required"),
        context: z.string().optional(),
        demoMode: z.boolean().optional().default(false),
      }))
      .mutation(async ({ input, ctx }) => {
        const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        return {
          taskId,
          goal: input.goal,
          status: "created",
          message: "Task created. Execution will start shortly."
        };
      }),
    
    getTaskStatus: protectedProcedure
      .input(z.object({
        taskId: z.string(),
      }))
      .query(async ({ input }) => {
        return {
          taskId: input.taskId,
          status: "running",
          progress: 50,
          currentStep: 2,
          totalSteps: 5,
        };
      }),
    
    getTaskReport: protectedProcedure
      .input(z.object({
        taskId: z.string(),
      }))
      .query(async ({ input }) => {
        return {
          taskId: input.taskId,
          success: true,
          duration: 45.5,
          totalSteps: 5,
          successfulSteps: 5,
          reportUrl: `/reports/${input.taskId}.md`,
        };
      }),
    
    approveAction: protectedProcedure
      .input(z.object({
        taskId: z.string(),
        stepId: z.number(),
      }))
      .mutation(async ({ input }) => {
        return {
          success: true,
          message: "Action approved",
        };
      }),
    
    rejectAction: protectedProcedure
      .input(z.object({
        taskId: z.string(),
        stepId: z.number(),
        reason: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        return {
          success: true,
          message: "Action rejected",
        };
      }),
  }),
});

export type AppRouter = typeof appRouter;
