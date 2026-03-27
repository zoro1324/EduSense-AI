import React, { useEffect, useMemo, useState } from 'react';

import { AppShell } from '../components/layout/AppShell';
import {
  Badge,
  Button,
  Card,
  CardBody,
  CardHeader,
  EmptyState,
  Input,
  PageContainer,
  PageTitle,
  Select,
} from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../lib/api';

const DAY_OPTIONS = [
  { value: '', label: 'All Days' },
  { value: 'monday', label: 'Monday' },
  { value: 'tuesday', label: 'Tuesday' },
  { value: 'wednesday', label: 'Wednesday' },
  { value: 'thursday', label: 'Thursday' },
  { value: 'friday', label: 'Friday' },
  { value: 'saturday', label: 'Saturday' },
];

const DAY_ORDER = {
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6,
};

const roleLabel = (role) => {
  if (!role) return 'Unknown';
  return role.charAt(0).toUpperCase() + role.slice(1);
};

export const AcademicPlannerPage = () => {
  const { isPrincipal, managedClasses } = useAuth();
  const { pushToast } = useToast();

  const [loading, setLoading] = useState(true);
  const [classes, setClasses] = useState([]);
  const [faculties, setFaculties] = useState([]);
  const [users, setUsers] = useState([]);
  const [timetable, setTimetable] = useState([]);

  const [selectedClassFilter, setSelectedClassFilter] = useState('');
  const [selectedDayFilter, setSelectedDayFilter] = useState('');
  const [editingTimetableId, setEditingTimetableId] = useState(null);
  const [editingTimetableForm, setEditingTimetableForm] = useState({
    period: '1',
    faculty: '',
    room_number: '',
    start_time: '',
    end_time: '',
  });
  const [savingTimetableId, setSavingTimetableId] = useState(null);

  const [classForm, setClassForm] = useState({ name: '', section: '', incharge: '' });
  const [facultyForm, setFacultyForm] = useState({ user: '', employee_code: '', department: '', designation: '' });
  const [timetableForm, setTimetableForm] = useState({
    school_class: '',
    day_of_week: 'monday',
    period: '1',
    subject_name: '',
    faculty: '',
    room_number: '',
    start_time: '',
    end_time: '',
  });

  const normalizeTimeValue = (value) => {
    if (!value) return '';
    return String(value).slice(0, 5);
  };

  const loadAcademicData = async () => {
    setLoading(true);
    try {
      if (isPrincipal) {
        const [classRows, facultyRows, timetableRows, userRows] = await Promise.all([
          api.get('/academic/classes/'),
          api.get('/academic/faculties/'),
          api.get('/academic/timetable/'),
          api.get('/users/'),
        ]);
        setClasses(Array.isArray(classRows) ? classRows : []);
        setFaculties(Array.isArray(facultyRows) ? facultyRows : []);
        setTimetable(Array.isArray(timetableRows) ? timetableRows : []);
        setUsers(Array.isArray(userRows) ? userRows : []);
      } else {
        const [classRows, timetableRows] = await Promise.all([
          api.get('/academic/classes/'),
          api.get('/academic/timetable/'),
        ]);
        setClasses(Array.isArray(classRows) ? classRows : []);
        setFaculties([]);
        setUsers([]);
        setTimetable(Array.isArray(timetableRows) ? timetableRows : []);
      }
    } catch (error) {
      setClasses([]);
      setFaculties([]);
      setUsers([]);
      setTimetable([]);
      pushToast(error.message || 'Failed to load academic planner data', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAcademicData();
  }, [isPrincipal]);

  useEffect(() => {
    if (selectedClassFilter) {
      return;
    }

    if (!isPrincipal && managedClasses.length > 0) {
      setSelectedClassFilter(managedClasses[0]);
    }
  }, [classes, isPrincipal, managedClasses, selectedClassFilter]);

  useEffect(() => {
    if (timetableForm.school_class) {
      return;
    }
    if (classes.length > 0) {
      setTimetableForm((prev) => ({ ...prev, school_class: String(classes[0].id) }));
    }
  }, [classes, timetableForm.school_class]);

  const availableFacultyUsers = useMemo(() => {
    const assignedUserIds = new Set(faculties.map((row) => row.user));
    return users.filter((candidate) => !assignedUserIds.has(candidate.id));
  }, [faculties, users]);

  const visibleTimetableRows = useMemo(() => {
    const filtered = timetable.filter((entry) => {
      const classMatch = !selectedClassFilter || entry.class_name === selectedClassFilter;
      const dayMatch = !selectedDayFilter || entry.day_of_week === selectedDayFilter;
      return classMatch && dayMatch;
    });

    return filtered.sort((a, b) => {
      const classCmp = (a.class_name || '').localeCompare(b.class_name || '');
      if (classCmp !== 0) return classCmp;
      const dayCmp = (DAY_ORDER[a.day_of_week] || 99) - (DAY_ORDER[b.day_of_week] || 99);
      if (dayCmp !== 0) return dayCmp;
      return Number(a.period || 0) - Number(b.period || 0);
    });
  }, [selectedClassFilter, selectedDayFilter, timetable]);

  const createClass = async (event) => {
    event.preventDefault();
    try {
      await api.post('/academic/classes/', {
        name: classForm.name.trim(),
        section: classForm.section.trim(),
        incharge: classForm.incharge ? Number(classForm.incharge) : null,
      });
      pushToast('Class created', 'success');
      setClassForm({ name: '', section: '', incharge: '' });
      await loadAcademicData();
    } catch (error) {
      pushToast(error.message || 'Failed to create class', 'error');
    }
  };

  const createFaculty = async (event) => {
    event.preventDefault();
    try {
      await api.post('/academic/faculties/', {
        user: Number(facultyForm.user),
        employee_code: facultyForm.employee_code.trim(),
        department: facultyForm.department.trim(),
        designation: facultyForm.designation.trim(),
      });
      pushToast('Faculty record created', 'success');
      setFacultyForm({ user: '', employee_code: '', department: '', designation: '' });
      await loadAcademicData();
    } catch (error) {
      pushToast(error.message || 'Failed to create faculty', 'error');
    }
  };

  const createTimetableEntry = async (event) => {
    event.preventDefault();
    try {
      await api.post('/academic/timetable/', {
        school_class: Number(timetableForm.school_class),
        day_of_week: timetableForm.day_of_week,
        period: Number(timetableForm.period),
        subject_name: timetableForm.subject_name.trim(),
        faculty: Number(timetableForm.faculty),
        room_number: timetableForm.room_number.trim(),
        start_time: timetableForm.start_time || null,
        end_time: timetableForm.end_time || null,
      });
      pushToast('Timetable entry added', 'success');
      setTimetableForm((prev) => ({
        ...prev,
        period: '1',
        subject_name: '',
        room_number: '',
        start_time: '',
        end_time: '',
      }));
      await loadAcademicData();
    } catch (error) {
      pushToast(error.message || 'Failed to add timetable entry', 'error');
    }
  };

  const deleteTimetableEntry = async (id) => {
    try {
      await api.delete(`/academic/timetable/${id}/`);
      pushToast('Timetable entry removed', 'warning');
      if (editingTimetableId === id) {
        setEditingTimetableId(null);
      }
      await loadAcademicData();
    } catch (error) {
      pushToast(error.message || 'Failed to delete timetable entry', 'error');
    }
  };

  const startInlineEdit = (entry) => {
    if (isPrincipal && faculties.length === 0) {
      pushToast('Please add faculty records before editing timetable entries', 'warning');
      return;
    }

    setEditingTimetableId(entry.id);
    setEditingTimetableForm({
      period: String(entry.period || 1),
      faculty: String(entry.faculty || ''),
      room_number: entry.room_number || '',
      start_time: normalizeTimeValue(entry.start_time),
      end_time: normalizeTimeValue(entry.end_time),
    });
  };

  const cancelInlineEdit = () => {
    setEditingTimetableId(null);
    setEditingTimetableForm({
      period: '1',
      faculty: '',
      room_number: '',
      start_time: '',
      end_time: '',
    });
  };

  const saveInlineEdit = async (entryId) => {
    try {
      const start = editingTimetableForm.start_time || null;
      const end = editingTimetableForm.end_time || null;

      if (start && end && start >= end) {
        pushToast('Start time must be before end time', 'error');
        return;
      }

      setSavingTimetableId(entryId);
      await api.put(`/academic/timetable/${entryId}/`, {
        period: Number(editingTimetableForm.period || 1),
        faculty: Number(editingTimetableForm.faculty),
        room_number: editingTimetableForm.room_number.trim(),
        start_time: start,
        end_time: end,
      });

      pushToast('Timetable entry updated', 'success');
      cancelInlineEdit();
      await loadAcademicData();
    } catch (error) {
      pushToast(error.message || 'Failed to update timetable entry', 'error');
    } finally {
      setSavingTimetableId(null);
    }
  };

  return (
    <AppShell>
      <PageContainer>
        <PageTitle
          title="Academic Planner"
          subtitle={
            isPrincipal
              ? 'Manage classes, faculties, and timetable across the full school.'
              : `Viewing your assigned class scope: ${managedClasses.join(', ') || 'No class assigned'}`
          }
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardBody>
              <p className="text-sm text-muted">Role</p>
              <p className="text-2xl font-semibold mt-1">{isPrincipal ? 'Principal' : 'In-charge'}</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <p className="text-sm text-muted">Classes In Scope</p>
              <p className="text-2xl font-semibold mt-1">{isPrincipal ? classes.length : managedClasses.length}</p>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <p className="text-sm text-muted">Timetable Entries</p>
              <p className="text-2xl font-semibold mt-1">{visibleTimetableRows.length}</p>
            </CardBody>
          </Card>
        </div>

        <Card>
          <CardHeader title="Class Table" right={<Button variant="outline" onClick={loadAcademicData}>Refresh</Button>} />
          <CardBody className="space-y-4">
            {loading ? <div className="text-sm text-muted">Loading classes...</div> : null}
            {!loading && classes.length === 0 ? <EmptyState title="No classes" subtitle="Create a class to begin." /> : null}

            {classes.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-muted">
                    <tr>
                      <th className="py-2">Class</th>
                      <th className="py-2">Section</th>
                      <th className="py-2">In-charge</th>
                      <th className="py-2">Email</th>
                      <th className="py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {classes.map((schoolClass) => (
                      <tr key={schoolClass.id} className="border-t border-border">
                        <td className="py-2 font-medium">{schoolClass.name}</td>
                        <td className="py-2">{schoolClass.section || '-'}</td>
                        <td className="py-2">{schoolClass.incharge_name || '-'}</td>
                        <td className="py-2">{schoolClass.incharge_email || '-'}</td>
                        <td className="py-2">
                          <Badge tone={schoolClass.is_active ? 'success' : 'danger'}>
                            {schoolClass.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}

            {isPrincipal ? (
              <form className="grid md:grid-cols-4 gap-2 border border-border rounded-lg p-3 bg-slate-900" onSubmit={createClass}>
                <Input
                  required
                  placeholder="Class Name"
                  value={classForm.name}
                  onChange={(event) => setClassForm((prev) => ({ ...prev, name: event.target.value }))}
                />
                <Input
                  placeholder="Section"
                  value={classForm.section}
                  onChange={(event) => setClassForm((prev) => ({ ...prev, section: event.target.value }))}
                />
                <Select
                  value={classForm.incharge}
                  onChange={(event) => setClassForm((prev) => ({ ...prev, incharge: event.target.value }))}
                >
                  <option value="">Select In-charge</option>
                  {users.map((candidate) => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.first_name || candidate.last_name
                        ? `${candidate.first_name || ''} ${candidate.last_name || ''}`.trim()
                        : candidate.email}{' '}
                      ({roleLabel(candidate.role)})
                    </option>
                  ))}
                </Select>
                <Button type="submit">Add Class</Button>
              </form>
            ) : null}
          </CardBody>
        </Card>

        {isPrincipal ? (
          <Card>
            <CardHeader title="Faculty Table" />
            <CardBody className="space-y-4">
              {faculties.length === 0 ? <EmptyState title="No faculty records" subtitle="Create faculty entries to map timetable periods." /> : null}

              {faculties.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="text-left text-muted">
                      <tr>
                        <th className="py-2">Employee Code</th>
                        <th className="py-2">Faculty Name</th>
                        <th className="py-2">Email</th>
                        <th className="py-2">Department</th>
                        <th className="py-2">Designation</th>
                        <th className="py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {faculties.map((faculty) => (
                        <tr key={faculty.id} className="border-t border-border">
                          <td className="py-2 font-medium">{faculty.employee_code}</td>
                          <td className="py-2">{faculty.user_name || '-'}</td>
                          <td className="py-2">{faculty.user_email || '-'}</td>
                          <td className="py-2">{faculty.department || '-'}</td>
                          <td className="py-2">{faculty.designation || '-'}</td>
                          <td className="py-2">
                            <Badge tone={faculty.is_active ? 'success' : 'danger'}>{faculty.is_active ? 'Active' : 'Inactive'}</Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : null}

              <form className="grid md:grid-cols-5 gap-2 border border-border rounded-lg p-3 bg-slate-900" onSubmit={createFaculty}>
                <Select
                  required
                  value={facultyForm.user}
                  onChange={(event) => setFacultyForm((prev) => ({ ...prev, user: event.target.value }))}
                >
                  <option value="">Select User</option>
                  {availableFacultyUsers.map((candidate) => (
                    <option key={candidate.id} value={candidate.id}>
                      {candidate.first_name || candidate.last_name
                        ? `${candidate.first_name || ''} ${candidate.last_name || ''}`.trim()
                        : candidate.email}{' '}
                      ({roleLabel(candidate.role)})
                    </option>
                  ))}
                </Select>
                <Input
                  required
                  placeholder="Employee Code"
                  value={facultyForm.employee_code}
                  onChange={(event) => setFacultyForm((prev) => ({ ...prev, employee_code: event.target.value }))}
                />
                <Input
                  placeholder="Department"
                  value={facultyForm.department}
                  onChange={(event) => setFacultyForm((prev) => ({ ...prev, department: event.target.value }))}
                />
                <Input
                  placeholder="Designation"
                  value={facultyForm.designation}
                  onChange={(event) => setFacultyForm((prev) => ({ ...prev, designation: event.target.value }))}
                />
                <Button type="submit">Add Faculty</Button>
              </form>
            </CardBody>
          </Card>
        ) : null}

        <Card>
          <CardHeader title="Timetable" />
          <CardBody className="space-y-4">
            <div className="grid md:grid-cols-3 gap-2">
              <Select value={selectedClassFilter} onChange={(event) => setSelectedClassFilter(event.target.value)}>
                <option value="">All Classes</option>
                {classes.map((schoolClass) => (
                  <option key={schoolClass.id} value={schoolClass.name}>
                    {schoolClass.name}
                  </option>
                ))}
              </Select>
              <Select value={selectedDayFilter} onChange={(event) => setSelectedDayFilter(event.target.value)}>
                {DAY_OPTIONS.map((day) => (
                  <option key={day.value || 'all-days'} value={day.value}>
                    {day.label}
                  </option>
                ))}
              </Select>
              <Button variant="outline" onClick={loadAcademicData}>Reload Timetable</Button>
            </div>

            {visibleTimetableRows.length === 0 ? (
              <EmptyState title="No timetable entries" subtitle="Add period assignments to map class, period, and faculty." />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="text-left text-muted">
                    <tr>
                      <th className="py-2">Class</th>
                      <th className="py-2">Day</th>
                      <th className="py-2">Period</th>
                      <th className="py-2">Subject</th>
                      <th className="py-2">Faculty</th>
                      <th className="py-2">Room</th>
                      <th className="py-2">Time</th>
                      {isPrincipal ? <th className="py-2">Action</th> : null}
                    </tr>
                  </thead>
                  <tbody>
                    {visibleTimetableRows.map((entry) => (
                      <tr key={entry.id} className="border-t border-border">
                        <td className="py-2 font-medium">{entry.class_name}</td>
                        <td className="py-2">{roleLabel(entry.day_of_week)}</td>
                        <td className="py-2">
                          {editingTimetableId === entry.id ? (
                            <Input
                              type="number"
                              min="1"
                              max="10"
                              value={editingTimetableForm.period}
                              onChange={(event) =>
                                setEditingTimetableForm((prev) => ({ ...prev, period: event.target.value }))
                              }
                              className="w-20"
                            />
                          ) : (
                            entry.period
                          )}
                        </td>
                        <td className="py-2">{entry.subject_name}</td>
                        <td className="py-2">
                          {editingTimetableId === entry.id ? (
                            <Select
                              value={editingTimetableForm.faculty}
                              onChange={(event) =>
                                setEditingTimetableForm((prev) => ({ ...prev, faculty: event.target.value }))
                              }
                            >
                              <option value="">Select Faculty</option>
                              {faculties.map((faculty) => (
                                <option key={faculty.id} value={faculty.user}>
                                  {faculty.user_name || faculty.user_email} ({faculty.employee_code})
                                </option>
                              ))}
                            </Select>
                          ) : (
                            entry.faculty_name || entry.faculty_email || '-'
                          )}
                        </td>
                        <td className="py-2">
                          {editingTimetableId === entry.id ? (
                            <Input
                              value={editingTimetableForm.room_number}
                              onChange={(event) =>
                                setEditingTimetableForm((prev) => ({ ...prev, room_number: event.target.value }))
                              }
                              placeholder="Room"
                            />
                          ) : (
                            entry.room_number || '-'
                          )}
                        </td>
                        <td className="py-2">
                          {editingTimetableId === entry.id ? (
                            <div className="flex items-center gap-2">
                              <Input
                                type="time"
                                value={editingTimetableForm.start_time}
                                onChange={(event) =>
                                  setEditingTimetableForm((prev) => ({ ...prev, start_time: event.target.value }))
                                }
                              />
                              <span className="text-muted">to</span>
                              <Input
                                type="time"
                                value={editingTimetableForm.end_time}
                                onChange={(event) =>
                                  setEditingTimetableForm((prev) => ({ ...prev, end_time: event.target.value }))
                                }
                              />
                            </div>
                          ) : (
                            entry.start_time && entry.end_time ? `${entry.start_time} - ${entry.end_time}` : '-'
                          )}
                        </td>
                        {isPrincipal ? (
                          <td className="py-2">
                            <div className="flex items-center gap-2">
                              {editingTimetableId === entry.id ? (
                                <>
                                  <Button
                                    size="sm"
                                    loading={savingTimetableId === entry.id}
                                    onClick={() => saveInlineEdit(entry.id)}
                                  >
                                    Save
                                  </Button>
                                  <Button size="sm" variant="outline" onClick={cancelInlineEdit}>
                                    Cancel
                                  </Button>
                                </>
                              ) : (
                                <>
                                  <Button size="sm" variant="outline" onClick={() => startInlineEdit(entry)}>
                                    Edit
                                  </Button>
                                  <Button variant="danger" size="sm" onClick={() => deleteTimetableEntry(entry.id)}>
                                    Delete
                                  </Button>
                                </>
                              )}
                            </div>
                          </td>
                        ) : null}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {isPrincipal ? (
              <form className="grid md:grid-cols-4 gap-2 border border-border rounded-lg p-3 bg-slate-900" onSubmit={createTimetableEntry}>
                <Select
                  required
                  value={timetableForm.school_class}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, school_class: event.target.value }))}
                >
                  <option value="">Class</option>
                  {classes.map((schoolClass) => (
                    <option key={schoolClass.id} value={schoolClass.id}>
                      {schoolClass.name}
                    </option>
                  ))}
                </Select>
                <Select
                  required
                  value={timetableForm.day_of_week}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, day_of_week: event.target.value }))}
                >
                  {DAY_OPTIONS.filter((day) => day.value).map((day) => (
                    <option key={day.value} value={day.value}>
                      {day.label}
                    </option>
                  ))}
                </Select>
                <Input
                  required
                  type="number"
                  min="1"
                  max="10"
                  placeholder="Period"
                  value={timetableForm.period}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, period: event.target.value }))}
                />
                <Input
                  required
                  placeholder="Subject"
                  value={timetableForm.subject_name}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, subject_name: event.target.value }))}
                />
                <Select
                  required
                  value={timetableForm.faculty}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, faculty: event.target.value }))}
                >
                  <option value="">Faculty</option>
                  {faculties.map((faculty) => (
                    <option key={faculty.id} value={faculty.user}>
                      {faculty.user_name || faculty.user_email} ({faculty.employee_code})
                    </option>
                  ))}
                </Select>
                <Input
                  placeholder="Room"
                  value={timetableForm.room_number}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, room_number: event.target.value }))}
                />
                <Input
                  type="time"
                  value={timetableForm.start_time}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, start_time: event.target.value }))}
                />
                <Input
                  type="time"
                  value={timetableForm.end_time}
                  onChange={(event) => setTimetableForm((prev) => ({ ...prev, end_time: event.target.value }))}
                />
                <Button className="md:col-span-4" type="submit">Add Timetable Entry</Button>
              </form>
            ) : null}
          </CardBody>
        </Card>

        {!isPrincipal && managedClasses.length === 0 ? (
          <Card>
            <CardBody>
              <p className="text-sm text-yellow-300">No class is assigned to this account yet. Ask principal to set you as class in-charge.</p>
            </CardBody>
          </Card>
        ) : null}
      </PageContainer>
    </AppShell>
  );
};
