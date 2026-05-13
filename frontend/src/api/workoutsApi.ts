import { httpClient } from "./httpClient";
import type { Page } from "../types/common";
import type {
  Exercise,
  ExercisePayload,
  ExerciseProgress,
  ExerciseProgressPayload,
  WorkoutPlan,
  WorkoutPlanPayload,
  WorkoutPlanQueryParams,
  WorkoutPlanTransferPayload,
  WorkoutPlanTransferResult,
  WorkoutPlanUpdatePayload
} from "../types/workout";

const WORKOUT_ENDPOINTS = {
  plans: "/api/workout-plans",
  transferPlans: "/api/workout-plans/transfer",
  planById: (workoutPlanId: number) => `/api/workout-plans/${workoutPlanId}`,
  exercises: (workoutPlanId: number) => `/api/workout-plans/${workoutPlanId}/exercises`,
  exerciseById: (exerciseId: number) => `/api/exercises/${exerciseId}`,
  progress: "/api/exercise-progress",
  progressByStudent: (studentId: number) => `/api/exercise-progress/student/${studentId}`,
  progressByStudentAndExercise: (studentId: number, exerciseId: number) =>
    `/api/exercise-progress/student/${studentId}/exercise/${exerciseId}`
} as const;

export async function getWorkoutPlans(params: WorkoutPlanQueryParams = {}): Promise<Page<WorkoutPlan>> {
  const response = await httpClient.get<Page<WorkoutPlan>>(WORKOUT_ENDPOINTS.plans, { params });
  return response.data;
}

export async function createWorkoutPlan(payload: WorkoutPlanPayload): Promise<WorkoutPlan> {
  const response = await httpClient.post<WorkoutPlan>(WORKOUT_ENDPOINTS.plans, payload);
  return response.data;
}

export async function updateWorkoutPlan(
  workoutPlanId: number,
  payload: WorkoutPlanUpdatePayload
): Promise<WorkoutPlan> {
  const response = await httpClient.put<WorkoutPlan>(WORKOUT_ENDPOINTS.planById(workoutPlanId), payload);
  return response.data;
}

export async function deleteWorkoutPlan(workoutPlanId: number): Promise<WorkoutPlan> {
  const response = await httpClient.delete<WorkoutPlan>(WORKOUT_ENDPOINTS.planById(workoutPlanId));
  return response.data;
}

export async function transferWorkoutPlans(
  payload: WorkoutPlanTransferPayload
): Promise<WorkoutPlanTransferResult> {
  const response = await httpClient.post<WorkoutPlanTransferResult>(WORKOUT_ENDPOINTS.transferPlans, payload);
  return response.data;
}

export async function getExercises(workoutPlanId: number): Promise<Exercise[]> {
  const response = await httpClient.get<Exercise[]>(WORKOUT_ENDPOINTS.exercises(workoutPlanId));
  return response.data;
}

export async function createExercise(workoutPlanId: number, payload: ExercisePayload): Promise<Exercise> {
  const response = await httpClient.post<Exercise>(WORKOUT_ENDPOINTS.exercises(workoutPlanId), payload);
  return response.data;
}

export async function updateExercise(exerciseId: number, payload: Partial<ExercisePayload>): Promise<Exercise> {
  const response = await httpClient.put<Exercise>(WORKOUT_ENDPOINTS.exerciseById(exerciseId), payload);
  return response.data;
}

export async function deleteExercise(exerciseId: number): Promise<Exercise> {
  const response = await httpClient.delete<Exercise>(WORKOUT_ENDPOINTS.exerciseById(exerciseId));
  return response.data;
}

export async function createExerciseProgress(payload: ExerciseProgressPayload): Promise<ExerciseProgress> {
  const response = await httpClient.post<ExerciseProgress>(WORKOUT_ENDPOINTS.progress, payload);
  return response.data;
}

export async function getExerciseProgressByStudent(studentId: number): Promise<ExerciseProgress[]> {
  const response = await httpClient.get<ExerciseProgress[]>(WORKOUT_ENDPOINTS.progressByStudent(studentId));
  return response.data;
}

export async function getExerciseProgressByStudentAndExercise(
  studentId: number,
  exerciseId: number
): Promise<ExerciseProgress[]> {
  const response = await httpClient.get<ExerciseProgress[]>(
    WORKOUT_ENDPOINTS.progressByStudentAndExercise(studentId, exerciseId)
  );
  return response.data;
}
