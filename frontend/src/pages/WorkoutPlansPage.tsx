import { FormEvent, useEffect, useState } from "react";
import toast from "react-hot-toast";
import {
  createExercise,
  createExerciseProgress,
  createWorkoutPlan,
  deleteExercise,
  deleteWorkoutPlan,
  getExerciseProgressByStudentAndExercise,
  getExercises,
  getWorkoutPlans,
  updateExercise,
  updateWorkoutPlan
} from "../api/workoutsApi";
import { getStudents } from "../api/studentsApi";
import { getUsers } from "../api/usersApi";
import { DataTable, type Column } from "../components/DataTable";
import { ErrorState } from "../components/ErrorState";
import { LoadingState } from "../components/LoadingState";
import { useAuth } from "../contexts/AuthContext";
import { useSortableRows } from "../hooks/useSortableRows";
import type { AuthUser } from "../types/auth";
import type { Page } from "../types/common";
import type { Student } from "../types/student";
import type { Exercise, ExercisePayload, ExerciseProgress, WorkoutPlan, WorkoutPlanPayload } from "../types/workout";
import { formatDateTime, getErrorMessage, STATUS_OPTIONS } from "./pageUtils";

const EMPTY_PLAN: WorkoutPlanPayload = { student_id: 0, instructor_id: 0, goal: "", notes: "", status: "ACTIVE" };
const EMPTY_EXERCISE: ExercisePayload = { name: "", muscle_group: "", sets: 3, repetitions: 10, load: "", notes: "", status: "ACTIVE" };

export function WorkoutPlansPage(): JSX.Element {
  const { user } = useAuth();
  const canWrite = user?.role === "ADMIN" || user?.role === "INSTRUCTOR";
  const [page, setPage] = useState<Page<WorkoutPlan> | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<WorkoutPlan | null>(null);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [progress, setProgress] = useState<ExerciseProgress[]>([]);
  const [planForm, setPlanForm] = useState<WorkoutPlanPayload>(EMPTY_PLAN);
  const [students, setStudents] = useState<Student[]>([]);
  const [instructors, setInstructors] = useState<AuthUser[]>([]);
  const [studentSearch, setStudentSearch] = useState("");
  const [instructorSearch, setInstructorSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<"" | WorkoutPlanPayload["status"]>("");
  const [exerciseForm, setExerciseForm] = useState<ExercisePayload>(EMPTY_EXERCISE);
  const [editingPlanId, setEditingPlanId] = useState<number | null>(null);
  const [editingExerciseId, setEditingExerciseId] = useState<number | null>(null);
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadPlans(offset = page?.offset ?? 0): Promise<void> {
    setIsLoading(true);
    try {
      setPage(await getWorkoutPlans({
        limit: 20,
        offset,
        student_search: studentSearch || undefined,
        instructor_search: instructorSearch || undefined,
        status: statusFilter || undefined
      }));
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }

  async function loadFormOptions(): Promise<void> {
    setIsLoadingOptions(true);
    try {
      const [studentPage, instructorPage] = await Promise.all([
        getStudents({ limit: 100, status: "ACTIVE" }),
        getUsers({ limit: 100, role: "INSTRUCTOR" })
      ]);
      setStudents(studentPage.items);
      setInstructors(instructorPage.items);
    } catch (loadError) {
      setError(getErrorMessage(loadError));
    } finally {
      setIsLoadingOptions(false);
    }
  }

  useEffect(() => {
    void loadPlans();
    void loadFormOptions();
  }, []);

  function studentLabel(studentId: number): string {
    return students.find((student) => student.id === studentId)?.name ?? `Student #${studentId}`;
  }

  function instructorLabel(instructorId: number): string {
    return instructors.find((instructor) => instructor.id === instructorId)?.full_name ?? `Instructor #${instructorId}`;
  }

  async function selectPlan(plan: WorkoutPlan): Promise<void> {
    setSelectedPlan(plan);
    setSelectedExerciseId(null);
    setProgress([]);
    setExercises(await getExercises(plan.id));
  }

  async function handlePlanSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setIsSaving(true);
    const payload = {
      ...planForm,
      instructor_id: user?.role === "INSTRUCTOR" ? user.id : planForm.instructor_id
    };
    try {
      if (editingPlanId === null) {
        await createWorkoutPlan(payload);
      } else {
        await updateWorkoutPlan(editingPlanId, payload);
      }
      setPlanForm(EMPTY_PLAN);
      setEditingPlanId(null);
      toast.success(editingPlanId === null ? "Workout plan created." : "Workout plan updated.");
      await loadPlans();
    } catch (submitError) {
      toast.error("Workout plan save failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleExerciseSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (selectedPlan === null) {
      return;
    }
    setIsSaving(true);
    try {
      if (editingExerciseId === null) {
        await createExercise(selectedPlan.id, exerciseForm);
      } else {
        await updateExercise(editingExerciseId, exerciseForm);
      }
      setExerciseForm(EMPTY_EXERCISE);
      setEditingExerciseId(null);
      toast.success(editingExerciseId === null ? "Exercise added." : "Exercise updated.");
      setExercises(await getExercises(selectedPlan.id));
    } catch (submitError) {
      toast.error("Exercise save failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  async function handleProgressSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (selectedPlan === null || selectedExerciseId === null) {
      return;
    }
    const formData = new FormData(event.currentTarget);
    setIsSaving(true);
    try {
      await createExerciseProgress({
        student_id: selectedPlan.student_id,
        exercise_id: selectedExerciseId,
        load: String(formData.get("load") ?? "") || null,
        repetitions: Number(formData.get("repetitions")),
        notes: String(formData.get("notes") ?? "") || null
      });
      setProgress(await getExerciseProgressByStudentAndExercise(selectedPlan.student_id, selectedExerciseId));
      toast.success("Progress registered.");
      event.currentTarget.reset();
    } catch (submitError) {
      toast.error("Progress save failed.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const planColumns: Column<WorkoutPlan>[] = [
    { key: "id", header: "ID", render: (plan) => plan.id, sortValue: (plan) => plan.id },
    { key: "student", header: "Student", render: (plan) => studentLabel(plan.student_id) },
    { key: "instructor", header: "Instructor", render: (plan) => instructorLabel(plan.instructor_id) },
    { key: "goal", header: "Goal", render: (plan) => plan.goal, sortValue: (plan) => plan.goal },
    { key: "status", header: "Status", render: (plan) => plan.status, sortValue: (plan) => plan.status },
    {
      key: "actions",
      header: "Actions",
      render: (plan) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => void selectPlan(plan)}>Open</button>
          {canWrite && <button type="button" className="secondary" onClick={() => { setEditingPlanId(plan.id); setPlanForm({ student_id: plan.student_id, instructor_id: plan.instructor_id, goal: plan.goal, notes: plan.notes ?? "", status: plan.status }); }}>Edit</button>}
          {canWrite && <button type="button" className="danger" onClick={() => { if (confirm("Deactivate this workout plan?")) void deleteWorkoutPlan(plan.id).then(() => { toast.success("Workout plan deactivated."); return loadPlans(); }); }}>Delete</button>}
        </div>
      )
    }
  ];

  const exerciseColumns: Column<Exercise>[] = [
    { key: "name", header: "Exercise", render: (exercise) => exercise.name },
    { key: "group", header: "Group", render: (exercise) => exercise.muscle_group },
    { key: "sets", header: "Sets", render: (exercise) => exercise.sets },
    { key: "reps", header: "Reps", render: (exercise) => exercise.repetitions },
    { key: "load", header: "Load", render: (exercise) => exercise.load ?? "-" },
    { key: "status", header: "Status", render: (exercise) => exercise.status },
    {
      key: "actions",
      header: "Actions",
      render: (exercise) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => { setSelectedExerciseId(exercise.id); if (selectedPlan !== null) void getExerciseProgressByStudentAndExercise(selectedPlan.student_id, exercise.id).then(setProgress); }}>Progress</button>
          {canWrite && <button type="button" className="secondary" onClick={() => { setEditingExerciseId(exercise.id); setExerciseForm({ name: exercise.name, muscle_group: exercise.muscle_group, sets: exercise.sets, repetitions: exercise.repetitions, load: exercise.load ?? "", notes: exercise.notes ?? "", status: exercise.status }); }}>Edit</button>}
          {canWrite && <button type="button" className="danger" onClick={() => { if (confirm("Deactivate this exercise?") && selectedPlan !== null) void deleteExercise(exercise.id).then(() => { toast.success("Exercise deactivated."); return getExercises(selectedPlan.id); }).then(setExercises); }}>Delete</button>}
        </div>
      )
    }
  ];
  const sortedPlans = useSortableRows(page?.items ?? [], planColumns);

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Workout Plans</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadPlans(0); }}>
        <label>Student<input placeholder="Name, CPF, or email" value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} /></label>
        <label>Instructor<input placeholder="Name or email" value={instructorSearch} onChange={(event) => setInstructorSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "" | WorkoutPlanPayload["status"])}>
          <option value="">All</option>
          {STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}
        </select></label>
        <button type="submit">Filter</button>
      </form>
      {canWrite && (
        <form className="panel form-grid" onSubmit={handlePlanSubmit}>
          <label>Student
            <select value={planForm.student_id || ""} onChange={(event) => setPlanForm({ ...planForm, student_id: Number(event.target.value) })} required disabled={isLoadingOptions || students.length === 0}>
              <option value="">{isLoadingOptions ? "Loading students..." : "Select student"}</option>
              {students.map((student) => <option key={student.id} value={student.id}>{student.name} - {student.email}</option>)}
            </select>
          </label>
          <label>Instructor
            <select value={user?.role === "INSTRUCTOR" ? user.id : planForm.instructor_id || ""} onChange={(event) => setPlanForm({ ...planForm, instructor_id: Number(event.target.value) })} required disabled={user?.role === "INSTRUCTOR" || isLoadingOptions || instructors.length === 0}>
              <option value="">{isLoadingOptions ? "Loading instructors..." : "Select instructor"}</option>
              {(user?.role === "INSTRUCTOR" && !instructors.some((instructor) => instructor.id === user.id) ? [user, ...instructors] : instructors).map((instructor) => (
                <option key={instructor.id} value={instructor.id}>{instructor.full_name} - {instructor.email}</option>
              ))}
            </select>
          </label>
          <label>Goal<input placeholder="Goal" value={planForm.goal} onChange={(event) => setPlanForm({ ...planForm, goal: event.target.value })} required /></label>
          <label>Notes<input placeholder="Notes" value={planForm.notes ?? ""} onChange={(event) => setPlanForm({ ...planForm, notes: event.target.value })} /></label>
          <label>Status<select value={planForm.status} onChange={(event) => setPlanForm({ ...planForm, status: event.target.value as WorkoutPlanPayload["status"] })}>{STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}</select></label>
          <button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : editingPlanId === null ? "Create plan" : "Update plan"}</button>
        </form>
      )}
      {page === null ? <LoadingState /> : <DataTable columns={planColumns} rows={sortedPlans.rows} getRowKey={(plan) => plan.id} emptyMessage="No workout plans found." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadPlans(nextOffset)} sortKey={sortedPlans.sortKey} sortDirection={sortedPlans.sortDirection} onSortChange={sortedPlans.setSortKey} />}
      {selectedPlan !== null && (
        <section className="page-stack">
          <h2>Workout sheet for {studentLabel(selectedPlan.student_id)}</h2>
          {canWrite && (
            <form className="panel form-grid" onSubmit={handleExerciseSubmit}>
              <label>Exercise name<input placeholder="Exercise name" value={exerciseForm.name} onChange={(event) => setExerciseForm({ ...exerciseForm, name: event.target.value })} required /></label>
              <label>Muscle group<input placeholder="Muscle group" value={exerciseForm.muscle_group} onChange={(event) => setExerciseForm({ ...exerciseForm, muscle_group: event.target.value })} required /></label>
              <label>Sets<input type="number" min="1" value={exerciseForm.sets} onChange={(event) => setExerciseForm({ ...exerciseForm, sets: Number(event.target.value) })} required /></label>
              <label>Repetitions<input type="number" min="1" value={exerciseForm.repetitions} onChange={(event) => setExerciseForm({ ...exerciseForm, repetitions: Number(event.target.value) })} required /></label>
              <label>Load<input placeholder="Load" value={exerciseForm.load ?? ""} onChange={(event) => setExerciseForm({ ...exerciseForm, load: event.target.value })} /></label>
              <label>Notes<input placeholder="Notes" value={exerciseForm.notes ?? ""} onChange={(event) => setExerciseForm({ ...exerciseForm, notes: event.target.value })} /></label>
              <label>Status<select value={exerciseForm.status} onChange={(event) => setExerciseForm({ ...exerciseForm, status: event.target.value as ExercisePayload["status"] })}>{STATUS_OPTIONS.map((status) => <option key={status}>{status}</option>)}</select></label>
              <button type="submit" disabled={isSaving}>{editingExerciseId === null ? "Add exercise" : "Update exercise"}</button>
            </form>
          )}
          <DataTable columns={exerciseColumns} rows={exercises} getRowKey={(exercise) => exercise.id} emptyMessage="No exercises found." />
          <div className="exercise-groups">
            {exercises.map((exercise) => (
              <details key={exercise.id} className="panel" open={exercise.id === selectedExerciseId}>
                <summary>{exercise.name} - {exercise.muscle_group} - {exercise.sets}x{exercise.repetitions}</summary>
                <p>Status: {exercise.status}</p>
                <p>Load: {exercise.load ?? "-"}</p>
                <p>{exercise.notes ?? "No notes."}</p>
              </details>
            ))}
          </div>
          {canWrite && selectedExerciseId !== null && (
            <form className="panel form-grid" onSubmit={handleProgressSubmit}>
              <label>Load<input name="load" placeholder="Load" /></label>
              <label>Repetitions<input name="repetitions" type="number" min="1" placeholder="Repetitions" required /></label>
              <label>Notes<input name="notes" placeholder="Notes" /></label>
              <button type="submit" disabled={isSaving}>Register progress</button>
            </form>
          )}
          <DataTable
            columns={[
              { key: "date", header: "Recorded", render: (item) => formatDateTime(item.recorded_at) },
              { key: "load", header: "Load", render: (item) => item.load ?? "-" },
              { key: "reps", header: "Reps", render: (item) => item.repetitions },
              { key: "notes", header: "Notes", render: (item) => item.notes ?? "-" }
            ]}
            rows={progress}
            getRowKey={(item) => item.id}
            emptyMessage="No progress records selected."
          />
        </section>
      )}
    </section>
  );
}
