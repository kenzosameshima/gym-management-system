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
import { formatDateTime, formatFinancialStatus, getErrorMessage, STATUS_OPTIONS } from "./pageUtils";

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
        user?.role === "ADMIN" ? getUsers({ limit: 100, role: "INSTRUCTOR" }) : Promise.resolve(null)
      ]);
      setStudents(studentPage.items);
      setInstructors(instructorPage?.items ?? (user?.role === "INSTRUCTOR" ? [user] : []));
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
    return students.find((student) => student.id === studentId)?.name ?? "Aluno não encontrado";
  }

  function instructorLabel(instructorId: number): string {
    return instructors.find((instructor) => instructor.id === instructorId)?.full_name ?? "Instrutor não encontrado";
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
      toast.success(editingPlanId === null ? "Ficha de treino criada." : "Ficha de treino atualizada.");
      await loadPlans();
    } catch (submitError) {
      toast.error("Nao foi possivel salvar a ficha.");
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
      toast.success(editingExerciseId === null ? "Exercicio adicionado." : "Exercicio atualizado.");
      setExercises(await getExercises(selectedPlan.id));
    } catch (submitError) {
      toast.error("Nao foi possivel salvar o exercicio.");
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
      toast.success("Evolucao registrada.");
      event.currentTarget.reset();
    } catch (submitError) {
      toast.error("Nao foi possivel registrar a evolucao.");
      setError(getErrorMessage(submitError));
    } finally {
      setIsSaving(false);
    }
  }

  const planColumns: Column<WorkoutPlan>[] = [
    { key: "student", header: "Aluno", render: (plan) => studentLabel(plan.student_id) },
    { key: "instructor", header: "Instrutor", render: (plan) => instructorLabel(plan.instructor_id) },
    { key: "goal", header: "Objetivo", render: (plan) => plan.goal, sortValue: (plan) => plan.goal },
    { key: "status", header: "Status", render: (plan) => formatFinancialStatus(plan.status), sortValue: (plan) => plan.status },
    {
      key: "actions",
      header: "Acoes",
      render: (plan) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => void selectPlan(plan)}>Abrir ficha</button>
          {canWrite && <button type="button" className="secondary" onClick={() => { setEditingPlanId(plan.id); setPlanForm({ student_id: plan.student_id, instructor_id: plan.instructor_id, goal: plan.goal, notes: plan.notes ?? "", status: plan.status }); }}>Editar</button>}
          {canWrite && <button type="button" className="danger" onClick={() => { if (confirm("Desativar esta ficha?")) void deleteWorkoutPlan(plan.id).then(() => { toast.success("Ficha desativada."); return loadPlans(); }); }}>Desativar</button>}
        </div>
      )
    }
  ];

  const exerciseColumns: Column<Exercise>[] = [
    { key: "muscles", header: "Músculos", render: (exercise) => exercise.muscle_group },
    { key: "name", header: "Exercício", render: (exercise) => exercise.name },
    { key: "sets", header: "Séries", render: (exercise) => exercise.sets },
    { key: "reps", header: "Repetições", render: (exercise) => exercise.repetitions },
    { key: "load", header: "Carga (kg)", render: (exercise) => exercise.load ?? "-" },
    { key: "notes", header: "Observações", render: (exercise) => exercise.notes ?? "-" },
    {
      key: "actions",
      header: "Acoes",
      render: (exercise) => (
        <div className="row-actions">
          <button type="button" className="secondary" onClick={() => { setSelectedExerciseId(exercise.id); if (selectedPlan !== null) void getExerciseProgressByStudentAndExercise(selectedPlan.student_id, exercise.id).then(setProgress); }}>Evolucao</button>
          {canWrite && <button type="button" className="secondary" onClick={() => { setEditingExerciseId(exercise.id); setExerciseForm({ name: exercise.name, muscle_group: exercise.muscle_group, sets: exercise.sets, repetitions: exercise.repetitions, load: exercise.load ?? "", notes: exercise.notes ?? "", status: exercise.status }); }}>Editar</button>}
          {canWrite && <button type="button" className="danger" onClick={() => { if (confirm("Desativar este exercicio?") && selectedPlan !== null) void deleteExercise(exercise.id).then(() => { toast.success("Exercicio desativado."); return getExercises(selectedPlan.id); }).then(setExercises); }}>Desativar</button>}
        </div>
      )
    }
  ];
  const sortedPlans = useSortableRows(page?.items ?? [], planColumns);

  return (
    <section className="page-stack">
      <header className="page-header"><h1>Fichas de treino</h1></header>
      {error !== null && <ErrorState message={error} />}
      <form className="toolbar" onSubmit={(event) => { event.preventDefault(); void loadPlans(0); }}>
        <label>Aluno<input placeholder="Nome, CPF ou e-mail" value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} /></label>
        <label>Instrutor<input placeholder="Nome do instrutor" value={instructorSearch} onChange={(event) => setInstructorSearch(event.target.value)} /></label>
        <label>Status<select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value as "" | WorkoutPlanPayload["status"])}>
          <option value="">Todos</option>
          {STATUS_OPTIONS.map((status) => <option key={status} value={status}>{formatFinancialStatus(status)}</option>)}
        </select></label>
        <button type="submit">Filtrar</button>
      </form>
      {canWrite && (
        <form className="panel form-grid" onSubmit={handlePlanSubmit}>
          <label>Aluno
            <select value={planForm.student_id || ""} onChange={(event) => setPlanForm({ ...planForm, student_id: Number(event.target.value) })} required disabled={isLoadingOptions || students.length === 0}>
              <option value="">{isLoadingOptions ? "Carregando alunos..." : "Selecionar aluno"}</option>
              {students.map((student) => <option key={student.id} value={student.id}>{student.name}</option>)}
            </select>
          </label>
          <label>Instrutor
            <select value={user?.role === "INSTRUCTOR" ? user.id : planForm.instructor_id || ""} onChange={(event) => setPlanForm({ ...planForm, instructor_id: Number(event.target.value) })} required disabled={user?.role === "INSTRUCTOR" || isLoadingOptions || instructors.length === 0}>
              <option value="">{isLoadingOptions ? "Carregando instrutores..." : "Selecionar instrutor"}</option>
              {(user?.role === "INSTRUCTOR" && !instructors.some((instructor) => instructor.id === user.id) ? [user, ...instructors] : instructors).map((instructor) => (
                <option key={instructor.id} value={instructor.id}>{instructor.full_name}</option>
              ))}
            </select>
          </label>
          <label>Objetivo<input placeholder="Objetivo" value={planForm.goal} onChange={(event) => setPlanForm({ ...planForm, goal: event.target.value })} required /></label>
          <label>Observacoes<input placeholder="Observacoes" value={planForm.notes ?? ""} onChange={(event) => setPlanForm({ ...planForm, notes: event.target.value })} /></label>
          <label>Status<select value={planForm.status} onChange={(event) => setPlanForm({ ...planForm, status: event.target.value as WorkoutPlanPayload["status"] })}>{STATUS_OPTIONS.map((status) => <option key={status} value={status}>{formatFinancialStatus(status)}</option>)}</select></label>
          <button type="submit" disabled={isSaving}>{isSaving ? "Salvando..." : editingPlanId === null ? "Criar ficha" : "Atualizar ficha"}</button>
        </form>
      )}
      {page === null ? <LoadingState /> : <DataTable columns={planColumns} rows={sortedPlans.rows} getRowKey={(plan) => plan.id} emptyMessage="Nenhuma ficha encontrada." isLoading={isLoading} total={page.total} limit={page.limit} offset={page.offset} onPageChange={(nextOffset) => void loadPlans(nextOffset)} sortKey={sortedPlans.sortKey} sortDirection={sortedPlans.sortDirection} onSortChange={sortedPlans.setSortKey} />}
      {selectedPlan !== null && (
        <section className="page-stack">
          <header className="workout-sheet-header">
            <div>
              <p className="eyebrow">Ficha de treino</p>
              <h2>{studentLabel(selectedPlan.student_id)}</h2>
            </div>
            <div className="workout-sheet-meta">
              <span>{selectedPlan.goal}</span>
              <span>{instructorLabel(selectedPlan.instructor_id)}</span>
            </div>
          </header>
          {canWrite && (
            <form className="panel form-grid" onSubmit={handleExerciseSubmit}>
              <label>Músculos<input placeholder="Ex.: Peitoral, tríceps" value={exerciseForm.muscle_group} onChange={(event) => setExerciseForm({ ...exerciseForm, muscle_group: event.target.value })} required /></label>
              <label>Exercício<input placeholder="Nome do exercício" value={exerciseForm.name} onChange={(event) => setExerciseForm({ ...exerciseForm, name: event.target.value })} required /></label>
              <label>Séries<input type="number" min="1" value={exerciseForm.sets} onChange={(event) => setExerciseForm({ ...exerciseForm, sets: Number(event.target.value) })} required /></label>
              <label>Repetições<input type="number" min="1" value={exerciseForm.repetitions} onChange={(event) => setExerciseForm({ ...exerciseForm, repetitions: Number(event.target.value) })} required /></label>
              <label>Carga (kg)<input placeholder="Carga em kg" value={exerciseForm.load ?? ""} onChange={(event) => setExerciseForm({ ...exerciseForm, load: event.target.value })} /></label>
              <label>Observacoes<input placeholder="Observacoes" value={exerciseForm.notes ?? ""} onChange={(event) => setExerciseForm({ ...exerciseForm, notes: event.target.value })} /></label>
              <label>Status<select value={exerciseForm.status} onChange={(event) => setExerciseForm({ ...exerciseForm, status: event.target.value as ExercisePayload["status"] })}>{STATUS_OPTIONS.map((status) => <option key={status} value={status}>{formatFinancialStatus(status)}</option>)}</select></label>
              <button type="submit" disabled={isSaving}>{editingExerciseId === null ? "Adicionar exercicio" : "Atualizar exercicio"}</button>
            </form>
          )}
          <div className="workout-sheet-table">
            <DataTable columns={exerciseColumns} rows={exercises} getRowKey={(exercise) => exercise.id} emptyMessage="Nenhum exercício cadastrado nesta ficha." />
          </div>
          {canWrite && selectedExerciseId !== null && (
            <form className="panel form-grid" onSubmit={handleProgressSubmit}>
              <label>Carga (kg)<input name="load" placeholder="Carga em kg" /></label>
              <label>Repetições<input name="repetitions" type="number" min="1" placeholder="Repetições" required /></label>
              <label>Observacoes<input name="notes" placeholder="Observacoes" /></label>
              <button type="submit" disabled={isSaving}>Registrar evolucao</button>
            </form>
          )}
          <DataTable
            columns={[
              { key: "date", header: "Registrado em", render: (item) => formatDateTime(item.recorded_at) },
              { key: "load", header: "Carga (kg)", render: (item) => item.load ?? "-" },
              { key: "reps", header: "Repetições", render: (item) => item.repetitions },
              { key: "notes", header: "Observacoes", render: (item) => item.notes ?? "-" }
            ]}
            rows={progress}
            getRowKey={(item) => item.id}
            emptyMessage="Selecione um exercicio para ver a evolucao."
          />
        </section>
      )}
    </section>
  );
}
