import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { api } from '../lib/api';

export const LiveAttendancePage = () => {
  const [students, setStudents] = useState([]);
  const [attendanceToday, setAttendanceToday] = useState([]);
  const [streamOn, setStreamOn] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const load = async () => {
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
      }
    };
    load();
  }, []);

  const statusByStudent = useMemo(() => {
    const map = new Map();
    attendanceToday.forEach((row) => {
      map.set(row.student, row.status);
    });
    return map;
  }, [attendanceToday]);

  const presentCount = attendanceToday.filter((x) => x.status === 'present').length;
  const list = useMemo(
    () =>
      students.filter(
        (s) => s.name.toLowerCase().includes(search.toLowerCase()) || s.roll_number.toLowerCase().includes(search.toLowerCase())
      ),
    [students, search]
  );

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Live Attendance" subtitle="Real-time face recognition attendance from ESP32 CAM." />
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
          <div className="xl:col-span-3 space-y-4">
            <Card>
              <CardBody>
                <div className="aspect-video border border-border rounded-xl bg-slate-700/40 grid place-items-center text-muted">
                  <div className="text-center">
                    <div className="text-5xl">📷</div>
                    <p>ESP32 CAM Feed</p>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="p-3 rounded-lg bg-green-500/15 border border-green-500/40 text-green-200">✅ Naveen Kumar — Marked Present — 9:02 AM</div>
                  <div className="p-3 rounded-lg bg-red-500/15 border border-red-500/40 text-red-200">❌ Unknown Face Detected — Snapshot Saved</div>
                </div>
                <div className="mt-4 flex gap-2 items-center">
                  <Button onClick={() => setStreamOn((v) => !v)}>{streamOn ? 'Stop Stream' : 'Start Stream'}</Button>
                  <Badge tone={streamOn ? 'success' : 'danger'}>{streamOn ? '● Camera Online' : '● Camera Offline'}</Badge>
                </div>
              </CardBody>
            </Card>
          </div>

          <div className="xl:col-span-2">
            <Card className="h-full">
              <CardHeader title="Today's Attendance" right={<Badge tone="primary">{presentCount}/{students.length}</Badge>} />
              <CardBody className="space-y-3">
                <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name or roll" />
                <div className="max-h-[420px] overflow-auto thin-scrollbar space-y-2">
                  {list.map((s) => (
                    <div key={s.id} className="p-3 rounded-lg border border-border bg-slate-900 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center text-xs">{s.name.split(' ').map((x) => x[0]).join('').slice(0, 2)}</div>
                        <div className="min-w-0">
                          <p className="text-sm truncate">{s.name}</p>
                          <p className="text-xs text-muted">{s.roll_number} · Real-time</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge tone={statusByStudent.get(s.student_id) === 'present' ? 'success' : 'danger'}>{statusByStudent.get(s.student_id) === 'present' ? 'Present' : 'Absent'}</Badge>
                        <Button variant="outline" className="px-2 py-1 text-xs">Manual</Button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-xs text-muted border-t border-border pt-2">Present: {presentCount} | Absent: {Math.max(0, students.length - presentCount)} | Unknown: 0</div>
              </CardBody>
            </Card>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
};
