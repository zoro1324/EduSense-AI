import React, { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { students } from '../data/appData';
import { Badge, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';

export const StudentProfilePage = () => {
  const { id } = useParams();
  const student = students.find((s) => String(s.id) === id) || students[0];
  const [tab, setTab] = useState('Attendance History');

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
                <p className="text-sm text-muted">{student.roll} · {student.className}</p>
              </div>
              <Badge tone={student.faceRegistered ? 'success' : 'warning'}>{student.faceRegistered ? 'Face Registered' : 'Face Pending'}</Badge>
            </div>
          </CardBody>
        </Card>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Card><CardBody><p className="text-xs text-muted">Attendance %</p><h4 className="text-xl">{student.attendance}%</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Total Marks</p><h4 className="text-xl">{student.totalMarks}</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Rank</p><h4 className="text-xl">#{student.rank}</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Leaves Taken</p><h4 className="text-xl">{student.leavesTaken}</h4></CardBody></Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <Card>
            <CardHeader title="Personal + Parent Details" />
            <CardBody className="text-sm text-muted space-y-1">
              <p>DOB: {student.dob}</p>
              <p>Blood Group: {student.bloodGroup}</p>
              <p>Address: {student.address}</p>
              <p>Father: {student.father}</p>
              <p>Mother: {student.mother}</p>
              <p>Phone: {student.parentPhone}</p>
              <p>Email: {student.parentEmail}</p>
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="Recent Activity" />
            <CardBody className="text-sm text-muted space-y-2">
              <p>• Last attendance: 26-Mar-2026 09:08 AM</p>
              <p>• Last marks added: Quarterly exam</p>
              <p>• Last leave: 02-Mar-2026</p>
              <p>• Last AI report sent: 21-Mar-2026</p>
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
