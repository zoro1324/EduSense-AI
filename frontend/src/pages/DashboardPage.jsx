import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { api } from '../lib/api';

export const DashboardPage = () => {
  const [students, setStudents] = useState([]);
  const [attendanceToday, setAttendanceToday] = useState([]);
  const [engagementToday, setEngagementToday] = useState([]);
  const [safetyAlerts, setSafetyAlerts] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [studentsData, attendanceData, engagementData, safetyData] = await Promise.all([
          api.get('/students/'),
          api.get('/attendance/today/'),
          api.get('/engagement/today/'),
          api.get('/safety/alerts/'),
        ]);
        setStudents(Array.isArray(studentsData) ? studentsData : []);
        setAttendanceToday(Array.isArray(attendanceData) ? attendanceData : []);
        setEngagementToday(Array.isArray(engagementData) ? engagementData : []);
        setSafetyAlerts(Array.isArray(safetyData) ? safetyData : []);
      } catch (error) {
        setStudents([]);
        setAttendanceToday([]);
        setEngagementToday([]);
        setSafetyAlerts([]);
      }
    };
    load();
  }, []);

  const latestAttendanceByStudent = useMemo(() => {
    const latestByStudent = new Map();

    attendanceToday.forEach((record) => {
      const studentId = record.student;
      if (!studentId) {
        return;
      }

      const existing = latestByStudent.get(studentId);
      if (!existing) {
        latestByStudent.set(studentId, record);
        return;
      }

      const recordPeriod = Number(record.period || 0);
      const existingPeriod = Number(existing.period || 0);
      const recordMarkedAt = record.marked_at ? new Date(record.marked_at).getTime() : 0;
      const existingMarkedAt = existing.marked_at ? new Date(existing.marked_at).getTime() : 0;

      if (recordPeriod > existingPeriod || (recordPeriod === existingPeriod && recordMarkedAt > existingMarkedAt)) {
        latestByStudent.set(studentId, record);
      }
    });

    return Array.from(latestByStudent.values());
  }, [attendanceToday]);

  const presentToday = latestAttendanceByStudent.filter((x) => x.status === 'present').length;
  const absentToday = latestAttendanceByStudent.filter((x) => x.status === 'absent' || x.status === 'late').length;
  const unresolved = safetyAlerts.filter((a) => a.status === 'unresolved');

  const periodEngagementToday = useMemo(() => {
    const periodMap = new Map();
    engagementToday.forEach((row) => {
      const key = `Period ${row.period}`;
      if (!periodMap.has(key)) {
        periodMap.set(key, []);
      }
      periodMap.get(key).push(Number(row.engagement_percent || 0));
    });
    return Array.from(periodMap.entries()).map(([period, values]) => ({
      period,
      today: Math.round(values.reduce((a, b) => a + b, 0) / values.length),
    }));
  }, [engagementToday]);

  const engagementAvg = periodEngagementToday.length
    ? Math.round(periodEngagementToday.reduce((acc, x) => acc + x.today, 0) / periodEngagementToday.length)
    : 0;

  const lowAttendance = [];

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Dashboard" subtitle="AI insights for attendance, engagement and safety." />

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <Card><CardBody><p className="text-muted text-sm">Total Present Today</p><h3 className="text-3xl font-semibold mt-2">{presentToday}</h3><p className="text-xs text-muted">out of {students.length} students</p></CardBody></Card>
          <Card><CardBody><p className="text-muted text-sm">Overall Engagement %</p><h3 className="text-3xl font-semibold mt-2">{engagementAvg}% ↗</h3><p className="text-xs text-muted">trend +4% vs yesterday</p></CardBody></Card>
          <Card><CardBody><p className="text-muted text-sm">Active Safety Alerts</p><h3 className="text-3xl font-semibold mt-2">{unresolved.length}</h3>{unresolved.length > 0 ? <Badge tone="danger">Attention Needed</Badge> : <Badge tone="success">All Clear</Badge>}</CardBody></Card>
          <Card><CardBody><p className="text-muted text-sm">Total Registered Students</p><h3 className="text-3xl font-semibold mt-2">{students.length}</h3><p className="text-xs text-muted">Classes 10A / 11A / 12A</p></CardBody></Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <Card>
            <CardHeader title="Period-wise Engagement Today" />
            <CardBody>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={periodEngagementToday}>
                  <XAxis dataKey="period" stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} stroke="#94a3b8" />
                  <Tooltip />
                  <Line type="monotone" dataKey="today" stroke="#6366f1" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Present vs Absent Today" />
            <CardBody>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={[{ name: 'Present', value: presentToday }, { name: 'Absent', value: absentToday }]} dataKey="value" innerRadius={75} outerRadius={105}>
                    <Cell fill="#22c55e" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <Card>
            <CardHeader title="Recent Safety Alerts" />
            <CardBody className="space-y-3">
              {safetyAlerts.slice(0, 4).map((a) => (
                <div key={a.id} className="p-3 rounded-lg border border-border bg-slate-900 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${a.threat_level === 'high' ? 'bg-red-500' : a.threat_level === 'medium' ? 'bg-yellow-500' : 'bg-green-500'}`} />
                    <div>
                      <p className="text-sm">{new Date(a.timestamp).toLocaleTimeString()} · {a.location}</p>
                      <p className="text-xs text-muted">{a.threat_level}</p>
                    </div>
                  </div>
                  <Button variant="outline">View</Button>
                </div>
              ))}
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Students Below 75% Attendance" right={<a className="text-xs text-indigo-300">View All</a>} />
            <CardBody className="space-y-3">
              {lowAttendance.length === 0 ? <div className="text-sm text-muted">Use attendance summary endpoint data to monitor chronic absences.</div> : null}
              {lowAttendance.map((s) => (
                <div key={s.student_id} className="p-3 rounded-lg border border-border bg-slate-900 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center">{s.name.split(' ').map((x) => x[0]).join('').slice(0, 2)}</div>
                    <p className="text-sm">{s.name}</p>
                  </div>
                  <Badge tone="danger">Below Threshold</Badge>
                </div>
              ))}
            </CardBody>
          </Card>
        </div>

        <Card>
          <CardHeader title="Camera Status & Quick Actions" />
          <CardBody className="space-y-4">
            <div className="grid md:grid-cols-2 gap-3">
              <div className="p-3 border border-border rounded-lg bg-slate-900 flex justify-between"><p>ESP32 CAM</p><Badge tone="success">● Online</Badge></div>
              <div className="p-3 border border-border rounded-lg bg-slate-900 flex justify-between"><p>Classroom CAM</p><Badge tone="danger">● Offline</Badge></div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button>Start Attendance</Button>
              <Button variant="danger">View Alerts</Button>
              <Button variant="success">Add Student</Button>
            </div>
          </CardBody>
        </Card>
      </PageContainer>
    </AppShell>
  );
};
