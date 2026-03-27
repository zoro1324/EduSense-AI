import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';
import { api } from '../lib/api';

export const LiveAttendancePage = () => {
  const [students, setStudents] = useState([]);
  const [attendanceToday, setAttendanceToday] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState(1);
  const [manualUpdatingByStudent, setManualUpdatingByStudent] = useState({});
  const { pushToast } = useToast();

  const loadLiveAttendanceData = async () => {
    try {
      const [studentsData, attendanceData] = await Promise.all([
        api.get('/students/'),
        api.get('/attendance/today/'),
      ]);
      setStudents(Array.isArray(studentsData) ? studentsData : []);
      setAttendanceToday(Array.isArray(attendanceData) ? attendanceData : []);
    } catch (error) {
      setStudents([]);
      setAttendanceToday([]);
      pushToast(error.message || 'Failed to load live attendance data', 'error');
    }
  };

  useEffect(() => {
    loadLiveAttendanceData();
  }, []);

  const attendanceByStudentAndPeriod = useMemo(() => {
    const recordsByStudentPeriod = new Map();
    attendanceToday.forEach((record) => {
      const studentId = record.student;
      const period = Number(record.period || 0);
      if (!studentId || !period) {
        return;
      }

      const key = `${studentId}-${period}`;
      const existing = recordsByStudentPeriod.get(key);
      if (!existing) {
        recordsByStudentPeriod.set(key, record);
        return;
      }

      const recordMarkedAt = record.marked_at ? new Date(record.marked_at).getTime() : 0;
      const existingMarkedAt = existing.marked_at ? new Date(existing.marked_at).getTime() : 0;

      if (recordMarkedAt > existingMarkedAt) {
        recordsByStudentPeriod.set(key, record);
      }
    });

    return recordsByStudentPeriod;
  }, [attendanceToday]);

  const selectedPeriodRecordsByStudent = useMemo(() => {
    const map = new Map();
    students.forEach((student) => {
      const row = attendanceByStudentAndPeriod.get(`${student.student_id}-${selectedPeriod}`);
      if (row) {
        map.set(student.student_id, row);
      }
    });
    return map;
  }, [students, attendanceByStudentAndPeriod, selectedPeriod]);

  const statusByStudent = useMemo(() => {
    const map = new Map();
    selectedPeriodRecordsByStudent.forEach((record, studentId) => {
      map.set(studentId, record.status);
    });
    return map;
  }, [selectedPeriodRecordsByStudent]);

  const presentCount = useMemo(() => {
    let total = 0;
    statusByStudent.forEach((status) => {
      if (status === 'present') {
        total += 1;
      }
    });
    return total;
  }, [statusByStudent]);

  const absentCount = useMemo(() => {
    let total = 0;
    statusByStudent.forEach((status) => {
      if (status === 'absent' || status === 'late') {
        total += 1;
      }
    });
    return total;
  }, [statusByStudent]);

  const unknownCount = Math.max(0, students.length - (presentCount + absentCount));

  const markAttendanceManual = async (studentId) => {
    const current = selectedPeriodRecordsByStudent.get(studentId);
    const nextStatus = current?.status === 'present' ? 'absent' : 'present';

    setManualUpdatingByStudent((prev) => ({ ...prev, [studentId]: true }));
    try {
      if (current) {
        await api.put(`/attendance/${current.id}/`, {
          status: nextStatus,
          note: 'Manually updated from Live Attendance page',
        });
      } else {
        await api.post('/attendance/mark/', {
          student: studentId,
          status: nextStatus,
          period: selectedPeriod,
          note: `Manually marked from Live Attendance page (Period ${selectedPeriod})`,
        });
      }

      await loadLiveAttendanceData();
      pushToast(
        nextStatus === 'present' ? 'Attendance marked present manually' : 'Attendance marked absent manually',
        'success'
      );
    } catch (error) {
      pushToast(error.message || 'Manual attendance update failed', 'error');
    } finally {
      setManualUpdatingByStudent((prev) => ({ ...prev, [studentId]: false }));
    }
  };

  const list = useMemo(
    () =>
      students.filter(
        (s) =>
          s.name.toLowerCase().includes(search.toLowerCase()) ||
          String(s.roll_number || '').toLowerCase().includes(search.toLowerCase())
      ),
    [students, search]
  );

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Live Attendance" subtitle={`Period-wise attendance with manual override controls (Period ${selectedPeriod}).`} />
        <div className="grid grid-cols-1 gap-4">
          <Card className="h-full">
            <CardHeader title="Today's Attendance" right={<Badge tone="primary">P{selectedPeriod}: {presentCount}/{students.length}</Badge>} />
            <CardBody className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
                <div className="md:col-span-3">
                  <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name or roll" />
                </div>
                <Select value={String(selectedPeriod)} onChange={(e) => setSelectedPeriod(Number(e.target.value))}>
                  <option value="1">Period 1</option>
                  <option value="2">Period 2</option>
                  <option value="3">Period 3</option>
                  <option value="4">Period 4</option>
                  <option value="5">Period 5</option>
                  <option value="6">Period 6</option>
                </Select>
              </div>
              <div className="max-h-[620px] overflow-auto thin-scrollbar space-y-2">
                {list.map((s) => {
                  const status = statusByStudent.get(s.student_id) || 'unknown';
                  const statusTone = status === 'present' ? 'success' : status === 'unknown' ? 'warning' : 'danger';
                  const statusText = status === 'present' ? 'Present' : status === 'unknown' ? 'Unknown' : 'Absent';
                  const actionLabel = status === 'present' ? 'Mark Absent' : 'Mark Present';
                  const isUpdating = !!manualUpdatingByStudent[s.student_id];

                  return (
                    <div key={s.student_id} className="p-3 rounded-lg border border-border bg-slate-900 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center text-xs">{s.name.split(' ').map((x) => x[0]).join('').slice(0, 2)}</div>
                        <div className="min-w-0">
                          <p className="text-sm truncate">{s.name}</p>
                          <p className="text-xs text-muted">{s.roll_number} · Period {selectedPeriod}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge tone={statusTone}>{statusText}</Badge>
                        <Button
                          variant="outline"
                          className="px-2 py-1 text-xs"
                          disabled={isUpdating}
                          onClick={() => markAttendanceManual(s.student_id)}
                        >
                          {isUpdating ? 'Saving...' : actionLabel}
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="text-xs text-muted border-t border-border pt-2">Present: {presentCount} | Absent: {absentCount} | Unknown: {unknownCount}</div>
            </CardBody>
          </Card>
        </div>
      </PageContainer>
    </AppShell>
  );
};
