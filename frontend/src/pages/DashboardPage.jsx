import React from 'react';
import { AppShell } from '../components/layout/AppShell';
import { attendanceLast7Days, periodEngagementToday, safetyAlerts, students } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export const DashboardPage = () => {
  const presentToday = attendanceLast7Days[attendanceLast7Days.length - 1].present;
  const absentToday = attendanceLast7Days[attendanceLast7Days.length - 1].absent;
  const lowAttendance = students.filter((s) => s.attendance < 75).slice(0, 5);
  const unresolved = safetyAlerts.filter((a) => a.status === 'Unresolved');
  const engagementAvg = Math.round(periodEngagementToday.reduce((acc, x) => acc + x.today, 0) / periodEngagementToday.length);

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
                    <span className={`w-2 h-2 rounded-full ${a.level === 'Alert' ? 'bg-red-500' : a.level === 'Warning' ? 'bg-yellow-500' : 'bg-green-500'}`} />
                    <div>
                      <p className="text-sm">{a.timestamp} · {a.location}</p>
                      <p className="text-xs text-muted">{a.level}</p>
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
              {lowAttendance.map((s) => (
                <div key={s.id} className="p-3 rounded-lg border border-border bg-slate-900 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center">{s.name.split(' ').map((x) => x[0]).join('').slice(0, 2)}</div>
                    <p className="text-sm">{s.name}</p>
                  </div>
                  <Badge tone="danger">{s.attendance}%</Badge>
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
