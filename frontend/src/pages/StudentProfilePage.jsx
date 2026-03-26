import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { api } from '../lib/api';

export const StudentProfilePage = () => {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [results, setResults] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [tab, setTab] = useState('Attendance History');

  useEffect(() => {
    const load = async () => {
      try {
        const [studentData, resultsData, leavesData, attendanceData] = await Promise.all([
          api.get(`/students/${id}/profile/`),
          api.get('/marks/results/'),
          api.get('/leaves/'),
          api.get('/attendance/'),
        ]);
        setStudent(studentData || null);
        setResults((Array.isArray(resultsData) ? resultsData : []).filter((r) => String(r.student) === String(id)));
        setLeaves((Array.isArray(leavesData) ? leavesData : []).filter((r) => String(r.student) === String(id)));
        setAttendance((Array.isArray(attendanceData) ? attendanceData : []).filter((r) => String(r.student) === String(id)));
      } catch (error) {
        setStudent(null);
      }
    };
    load();
  }, [id]);

  const attendancePercent = useMemo(() => {
    if (!attendance.length) {
      return 0;
    }
    const present = attendance.filter((x) => x.status === 'present').length;
    return Math.round((present / attendance.length) * 100);
  }, [attendance]);

  const latestResult = results[0];

  if (!student) {
    return (
      <AppShell>
        <PageContainer>
          <p className="text-muted">Loading student profile...</p>
        </PageContainer>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <PageContainer>
        <Link to="/students" className="text-indigo-300 text-sm">← Back</Link>
        <Card>
          <CardBody>
            <div className="flex flex-wrap items-center gap-3">
              <div className="w-16 h-16 rounded-full bg-primary/30 grid place-items-center text-2xl">{student.name.split(' ').map((x) => x[0]).join('').slice(0,2)}</div>
              <div>
                <h2 className="text-xl font-semibold">{student.name}</h2>
                <p className="text-sm text-muted">{student.roll_number} · {student.class_name}</p>
              </div>
              <Badge tone={student.face_registered ? 'success' : 'warning'}>{student.face_registered ? 'Face Registered' : 'Face Pending'}</Badge>
            </div>
          </CardBody>
        </Card>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card><CardBody><p className="text-xs text-muted">Attendance %</p><h4 className="text-xl">{attendancePercent}%</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Total Marks</p><h4 className="text-xl">{latestResult?.total_marks ?? 0}</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Rank</p><h4 className="text-xl">#{latestResult?.rank ?? 'N/A'}</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Leaves Taken</p><h4 className="text-xl">{leaves.length}</h4></CardBody></Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <Card>
            <CardHeader title="Personal + Parent Details" />
            <CardBody className="text-sm text-muted space-y-1">
              <p>DOB: {student.date_of_birth}</p>
              <p>Blood Group: {student.blood_group}</p>
              <p>Address: {student.address}</p>
              <p>Father: {student.parent?.father_name || 'N/A'}</p>
              <p>Mother: {student.parent?.mother_name || 'N/A'}</p>
              <p>Phone: {student.parent?.phone_number || 'N/A'}</p>
              <p>Email: {student.parent?.email || 'N/A'}</p>
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardBody className="text-sm text-muted space-y-2">
              <p>• Last attendance: {attendance[0] ? `${attendance[0].date} P${attendance[0].period}` : 'N/A'}</p>
              <p>• Last marks added: {latestResult?.exam_name || 'N/A'}</p>
              <p>• Last leave: {leaves[0]?.start_date || 'N/A'}</p>
              <p>• Last AI report sent: {latestResult?.report_sent_at || 'N/A'}</p>
            </CardBody>
          </Card>
        </div>

        <Card>
          <CardBody>
            <div className="flex flex-wrap gap-2 mb-3">
              {['Attendance History', 'Marks History', 'Leave History', 'AI Reports'].map((t) => (
                <button key={t} onClick={() => setTab(t)} className={`px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>
              ))}
            </div>
            <div className="p-4 rounded-lg bg-slate-900 border border-border text-sm text-muted">{tab} data panel for {student.name}.</div>
          </CardBody>
        </Card>
      </PageContainer>
    </AppShell>
  );
};
