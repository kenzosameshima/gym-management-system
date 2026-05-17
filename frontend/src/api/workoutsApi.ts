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

type RawExercise = Partial<Exercise> & {
  exercise?: string;
  exercise_name?: string;
  muscle_groups?: string;
  muscles?: string;
  load_kg?: string | number | null;
  weight?: string | number | null;
  observation?: string | null;
  observations?: string | null;
};

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

function normalizeExercise(rawExercise: RawExercise): Exercise {
  return {
    id: Number(rawExercise.id ?? 0),
    workout_plan_id: Number(rawExercise.workout_plan_id ?? 0),
    name: String(rawExercise.name ?? rawExercise.exercise_name ?? rawExercise.exercise ?? "Exercicio sem nome"),
    muscle_group: String(rawExercise.muscle_group ?? rawExercise.muscle_groups ?? rawExercise.muscles ?? "Nao informado"),
    sets: Number(rawExercise.sets ?? 1),
    repetitions: Number(rawExercise.repetitions ?? 1),
    load: rawExercise.load === undefined || rawExercise.load === null
      ? rawExercise.load_kg === undefined || rawExercise.load_kg === null
        ? rawExercise.weight === undefined || rawExercise.weight === null
          ? null
          : String(rawExercise.weight)
        : String(rawExercise.load_kg)
      : String(rawExercise.load),
    notes: rawExercise.notes ?? rawExercise.observations ?? rawExercise.observation ?? null,
    status: rawExercise.status === "INACTIVE" ? "INACTIVE" : "ACTIVE",
    created_at: rawExercise.created_at ?? "",
    updated_at: rawExercise.updated_at ?? ""
  };
}

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
  const response = await httpClient.get<RawExercise[]>(WORKOUT_ENDPOINTS.exercises(workoutPlanId));
  return response.data.map(normalizeExercise);
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
