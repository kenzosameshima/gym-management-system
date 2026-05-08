import type { PageQueryParams, Status } from "./common";

export interface WorkoutPlan {
  id: number;
  student_id: number;
  instructor_id: number;
  goal: string;
  notes: string | null;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface WorkoutPlanPayload {
  student_id: number;
  instructor_id: number;
  goal: string;
  notes?: string | null;
  status: Status;
}

export interface WorkoutPlanUpdatePayload {
  student_id?: number;
  instructor_id?: number;
  goal?: string;
  notes?: string | null;
  status?: Status;
}

export interface WorkoutPlanQueryParams extends PageQueryParams {
  student_id?: number;
  student_search?: string;
  instructor_search?: string;
  status?: Status;
}

export interface Exercise {
  id: number;
  workout_plan_id: number;
  name: string;
  muscle_group: string;
  sets: number;
  repetitions: number;
  load: string | null;
  notes: string | null;
  status: Status;
  created_at: string;
  updated_at: string;
}

export interface ExercisePayload {
  name: string;
  muscle_group: string;
  sets: number;
  repetitions: number;
  load?: string | null;
  notes?: string | null;
  status: Status;
}

export interface ExerciseProgress {
  id: number;
  student_id: number;
  exercise_id: number;
  load: string | null;
  repetitions: number;
  recorded_at: string;
  notes: string | null;
}

export interface ExerciseProgressPayload {
  student_id: number;
  exercise_id: number;
  load?: string | null;
  repetitions: number;
  notes?: string | null;
}
