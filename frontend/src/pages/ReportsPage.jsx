import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export const ReportsPage = () => {
  const tabs = ['Attendance Report', 'Engagement Report', 'Safety Report', 'Academic Report'];
  const [tab, setTab] = useState(tabs[0]);

  const [attendanceReport, setAttendanceReport] = useState([]);
  const [engagementReport, setEngagementReport] = useState([]);
  const [safetyReport, setSafetyReport] = useState({ by_type: [], by_status: [] });
  const [academicReport, setAcademicReport] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const [attendanceData, engagementData, safetyData, academicData] = await Promise.all([
          api.get('/reports/attendance/'),
          api.get('/reports/engagement/'),
          api.get('/reports/safety/'),
          api.get('/reports/academic/'),
        ]);
        setAttendanceReport(Array.isArray(attendanceData) ? attendanceData : []);
        setEngagementReport(Array.isArray(engagementData) ? engagementData : []);
        setSafetyReport(safetyData || { by_type: [], by_status: [] });
        setAcademicReport(Array.isArray(academicData) ? academicData : []);
      } catch (error) {
        setAttendanceReport([]);
        setEngagementReport([]);
        setSafetyReport({ by_type: [], by_status: [] });
        setAcademicReport([]);
      }
    };
    load();
  }, []);

  const below75 = [];
  const totalAttendanceCount = attendanceReport.reduce((acc, x) => acc + Number(x.total || 0), 0);
  const presentCount = Number(attendanceReport.find((x) => x.status === 'present')?.total || 0);
  const avgAttendance = totalAttendanceCount ? Math.round((presentCount / totalAttendanceCount) * 100) : 0;
  const perfect = 0;

  const safetyResolved = Number(safetyReport.by_status?.find((x) => x.status === 'resolved')?.total || 0);
  const safetyUnresolved = Number(safetyReport.by_status?.find((x) => x.status === 'unresolved')?.total || 0);

  const subjectAvg = useMemo(
    () => academicReport.map((row) => ({ subject: row.exam_type__name, avg: Math.round(row.avg_percentage || 0) })),
    [academicReport]
  );

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Reports" subtitle="Attendance, engagement, safety and academics insights." />
        <div className="flex flex-wrap gap-2">{tabs.map((t) => <button key={t} onClick={() => setTab(t)} className={`px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>)}</div>

        {tab === 'Attendance Report' ? (
          <Card>
            <CardHeader title="Attendance Report" right={<Button variant="outline">Export PDF</Button>} />
            <CardBody className="space-y-4">
              <div className="grid md:grid-cols-3 gap-3">
                <Card><CardBody><p className="text-xs text-muted">Avg Attendance %</p><h4 className="text-xl">{avgAttendance}%</h4></CardBody></Card>
                <Card><CardBody><p className="text-xs text-muted">Below 75%</p><h4 className="text-xl">{below75.length}</h4></CardBody></Card>
                <Card><CardBody><p className="text-xs text-muted">Perfect Attendance</p><h4 className="text-xl">{perfect}</h4></CardBody></Card>
              </div>
              <ResponsiveContainer width="100%" height={260}><BarChart layout="vertical" data={attendanceReport.map((x) => ({ name: x.status, attendance: x.total }))}><XAxis type="number" stroke="#94a3b8" /><YAxis dataKey="name" type="category" width={120} stroke="#94a3b8" /><Tooltip /><Bar dataKey="attendance" fill="#6366f1" /></BarChart></ResponsiveContainer>
              <div className="p-3 rounded-lg border border-border bg-slate-900 text-sm text-muted">Red line threshold: 75%</div>
              <div className="space-y-2">{below75.map((s) => <div key={s.id} className="p-2 rounded bg-red-500/10 border border-red-500/20">{s.name} — {s.attendance}%</div>)}</div>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'Engagement Report' ? (
          <Card>
            <CardHeader title="Engagement Report" right={<div className="flex gap-2"><Button variant="outline">Week</Button><Button variant="outline">Month</Button><Button variant="outline">Export PDF</Button></div>} />
            <CardBody className="space-y-4">
              <ResponsiveContainer width="100%" height={240}><LineChart data={engagementReport.map((x) => ({ period: x.class_name, today: Math.round(x.avg_engagement || 0) }))}><XAxis dataKey="period" stroke="#94a3b8" /><YAxis domain={[0, 100]} stroke="#94a3b8" /><Tooltip /><Line dataKey="today" stroke="#6366f1" /></LineChart></ResponsiveContainer>
              <div className="grid grid-cols-6 gap-2">
                {engagementReport.map((r) => ['Mon','Tue','Wed','Thu','Fri'].map((d) => {
                  const val = Math.round(r.avg_engagement || 0);
                  return <div key={`${r.class_name}${d}`} className="p-2 rounded text-xs text-center" style={{ background: `rgba(99,102,241,${Math.max(0.15, val/100)})` }}>{r.class_name}-{d} {val}%</div>;
                }))}
              </div>
              <div className="grid md:grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">Best Period: Period 2 — avg 82%</div>
                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">Needs Attention: Period 5 — avg 34%</div>
              </div>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'Safety Report' ? (
          <Card>
            <CardHeader title="Safety Report" right={<Button variant="outline">Export PDF</Button>} />
            <CardBody className="space-y-4">
              <div className="grid md:grid-cols-4 gap-3">
                <Card><CardBody><p className="text-xs text-muted">Total Alerts</p><h4 className="text-xl">{safetyResolved + safetyUnresolved}</h4></CardBody></Card>
                <Card><CardBody><p className="text-xs text-muted">Resolved</p><h4 className="text-xl">{safetyResolved}</h4></CardBody></Card>
                <Card><CardBody><p className="text-xs text-muted">Unresolved</p><h4 className="text-xl">{safetyUnresolved}</h4></CardBody></Card>
                <Card><CardBody><p className="text-xs text-muted">Avg Response Time</p><h4 className="text-xl">6m</h4></CardBody></Card>
              </div>
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                <ResponsiveContainer width="100%" height={220}><PieChart><Pie data={[{name:'Resolved',value:safetyResolved},{name:'Unresolved',value:safetyUnresolved}]} dataKey="value" outerRadius={80}><Cell fill="#22c55e" /><Cell fill="#ef4444" /></Pie></PieChart></ResponsiveContainer>
                <ResponsiveContainer width="100%" height={220}><BarChart data={(safetyReport.by_type || []).map((x) => ({ loc: x.alert_type, count: x.total }))}><XAxis dataKey="loc" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Bar dataKey="count" fill="#6366f1" /></BarChart></ResponsiveContainer>
              </div>
              <div className="p-3 rounded-lg bg-slate-900 border border-border">Alert frequency heatmap by hour: 08-14 hrs concentrated.</div>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'Academic Report' ? (
          <Card>
            <CardHeader title="Academic Report" right={<div className="flex gap-2"><Select><option>10A</option><option>11A</option><option>12A</option></Select><Select><option>Quarterly</option></Select><Button variant="outline">Export PDF</Button></div>} />
            <CardBody className="space-y-4">
              <ResponsiveContainer width="100%" height={230}><BarChart data={subjectAvg}><XAxis dataKey="subject" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Bar dataKey="avg" fill="#6366f1" /></BarChart></ResponsiveContainer>
              <ResponsiveContainer width="100%" height={230}><LineChart data={subjectAvg.map((x) => ({ exam: x.subject, score: x.avg }))}><XAxis dataKey="exam" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Line dataKey="score" stroke="#22c55e" /></LineChart></ResponsiveContainer>
              <div className="grid xl:grid-cols-2 gap-3">
                <div className="p-3 rounded-lg border border-border bg-slate-900"><h4 className="mb-2">Top Exams by Avg %</h4>{subjectAvg.slice(0, 10).map((s,i)=><div key={s.subject} className="text-sm text-muted">#{i+1} {s.subject} ({s.avg}%)</div>)}</div>
                <div className="p-3 rounded-lg border border-border bg-slate-900"><h4 className="mb-2">Most Improved</h4><p className="text-sm text-muted">Naveen Kumar +12%</p><p className="text-sm text-muted">Shalini G +10%</p><Button variant="outline" className="mt-3 text-xs">Export individual marksheet</Button></div>
              </div>
            </CardBody>
          </Card>
        ) : null}
      </PageContainer>
    </AppShell>
  );
};
