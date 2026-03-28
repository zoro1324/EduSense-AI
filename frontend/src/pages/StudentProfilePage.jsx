import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { API_BASE_URL, api } from '../lib/api';

const TABS = ['Attendance History', 'Marks History', 'Leave History', 'AI Reports'];

const formatDate = (value) => {
  if (!value) {
    return 'N/A';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  return parsed.toLocaleDateString();
};

const formatDateTime = (value) => {
  if (!value) {
    return 'N/A';
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return String(value);
  }
  return parsed.toLocaleString();
};

export const StudentProfilePage = () => {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [marks, setMarks] = useState([]);
  const [results, setResults] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState('Attendance History');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');
      try {
        const [studentData, marksData, resultsData, leavesData, attendanceData] = await Promise.all([
          api.get(`/students/${id}/profile/`),
          api.get('/marks/'),
          api.get('/marks/results/'),
          api.get('/leaves/'),
          api.get('/attendance/'),
        ]);

        setStudent(studentData || null);
        setMarks((Array.isArray(marksData) ? marksData : []).filter((r) => String(r.student) === String(id)));
        setResults((Array.isArray(resultsData) ? resultsData : []).filter((r) => String(r.student) === String(id)));
        setLeaves((Array.isArray(leavesData) ? leavesData : []).filter((r) => String(r.student) === String(id)));
        setAttendance((Array.isArray(attendanceData) ? attendanceData : []).filter((r) => String(r.student) === String(id)));
      } catch (error) {
        setStudent(null);
        setMarks([]);
        setResults([]);
        setLeaves([]);
        setAttendance([]);
        setError(error.message || 'Unable to load student profile data');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const backendOrigin = useMemo(() => {
    try {
      const parsed = new URL(API_BASE_URL);
      return `${parsed.protocol}//${parsed.host}`;
    } catch (error) {
      return '';
    }
  }, []);

  const studentPhotoUrl = useMemo(() => {
    const raw = student?.photo;
    if (!raw || !backendOrigin) {
      return '';
    }
    if (/^https?:\/\//i.test(raw)) {
      return raw;
    }
    if (raw.startsWith('/')) {
      return `${backendOrigin}${raw}`;
    }
    if (raw.startsWith('media/')) {
      return `${backendOrigin}/${raw}`;
    }
    return `${backendOrigin}/media/${raw}`;
  }, [student, backendOrigin]);

  const attendanceHistory = useMemo(() => {
    return [...attendance].sort((a, b) => {
      const dateCompare = new Date(b.date).getTime() - new Date(a.date).getTime();
      if (dateCompare !== 0) {
        return dateCompare;
      }
      return Number(b.period || 0) - Number(a.period || 0);
    });
  }, [attendance]);

  const marksHistory = useMemo(() => {
    return [...marks].sort((a, b) => Number(b.id || 0) - Number(a.id || 0));
  }, [marks]);

  const resultsHistory = useMemo(() => {
    return [...results].sort((a, b) => Number(b.id || 0) - Number(a.id || 0));
  }, [results]);

  const leaveHistory = useMemo(() => {
    return [...leaves].sort((a, b) => new Date(b.applied_on).getTime() - new Date(a.applied_on).getTime());
  }, [leaves]);

  const aiReportsHistory = useMemo(() => {
    return resultsHistory
      .filter((item) => Boolean(item.ai_report || item.report_generated_at || item.report_sent_at || item.report_sent))
      .sort((a, b) => {
        const aTime = new Date(a.report_generated_at || a.report_sent_at || 0).getTime();
        const bTime = new Date(b.report_generated_at || b.report_sent_at || 0).getTime();
        return bTime - aTime;
      });
  }, [resultsHistory]);

  const attendancePercent = useMemo(() => {
    if (!attendanceHistory.length) {
      return 0;
    }
    const present = attendanceHistory.filter((x) => x.status === 'present').length;
    return Math.round((present / attendanceHistory.length) * 100);
  }, [attendanceHistory]);

  const approvedLeavesCount = useMemo(
    () => leaveHistory.filter((item) => item.status === 'approved').length,
    [leaveHistory]
  );

  const latestResult = resultsHistory[0] || null;
  const latestAttendance = attendanceHistory[0] || null;
  const latestLeave = leaveHistory[0] || null;
  const latestReport = aiReportsHistory[0] || null;

  const renderAttendanceHistory = () => {
    if (!attendanceHistory.length) {
      return <div className="text-sm text-muted">No attendance records found for this student.</div>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-muted">
              <th className="px-3 py-2 font-medium">Date</th>
              <th className="px-3 py-2 font-medium">Period</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Marked At</th>
              <th className="px-3 py-2 font-medium">Note</th>
            </tr>
          </thead>
          <tbody>
            {attendanceHistory.map((row) => (
              <tr key={row.id} className="border-b border-border/60">
                <td className="px-3 py-2">{formatDate(row.date)}</td>
                <td className="px-3 py-2">P{row.period}</td>
                <td className="px-3 py-2">
                  <Badge tone={row.status === 'present' ? 'success' : row.status === 'late' ? 'warning' : 'danger'}>
                    {String(row.status || 'unknown').toUpperCase()}
                  </Badge>
                </td>
                <td className="px-3 py-2 text-muted">{formatDateTime(row.marked_at)}</td>
                <td className="px-3 py-2 text-muted">{row.note || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderMarksHistory = () => {
    if (!marksHistory.length && !resultsHistory.length) {
      return <div className="text-sm text-muted">No marks or exam results found for this student.</div>;
    }

    return (
      <div className="space-y-4">
        {resultsHistory.length ? (
          <div className="overflow-x-auto">
            <p className="text-sm font-medium mb-2">Exam Results</p>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted">
                  <th className="px-3 py-2 font-medium">Exam</th>
                  <th className="px-3 py-2 font-medium">Total</th>
                  <th className="px-3 py-2 font-medium">Percentage</th>
                  <th className="px-3 py-2 font-medium">Grade</th>
                  <th className="px-3 py-2 font-medium">Rank</th>
                </tr>
              </thead>
              <tbody>
                {resultsHistory.map((row) => (
                  <tr key={row.id} className="border-b border-border/60">
                    <td className="px-3 py-2">{row.exam_name || 'N/A'}</td>
                    <td className="px-3 py-2">{row.total_marks ?? 0}/{row.max_total ?? 0}</td>
                    <td className="px-3 py-2">{Number(row.percentage || 0).toFixed(1)}%</td>
                    <td className="px-3 py-2">
                      <Badge tone={Number(row.percentage || 0) >= 75 ? 'success' : Number(row.percentage || 0) >= 50 ? 'warning' : 'danger'}>
                        {row.grade || 'N/A'}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">{row.rank ? `#${row.rank}` : 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}

        {marksHistory.length ? (
          <div className="overflow-x-auto">
            <p className="text-sm font-medium mb-2">Subject Marks</p>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted">
                  <th className="px-3 py-2 font-medium">Exam</th>
                  <th className="px-3 py-2 font-medium">Subject</th>
                  <th className="px-3 py-2 font-medium">Marks</th>
                  <th className="px-3 py-2 font-medium">Grade</th>
                </tr>
              </thead>
              <tbody>
                {marksHistory.map((row) => (
                  <tr key={row.id} className="border-b border-border/60">
                    <td className="px-3 py-2">{row.exam_name || 'N/A'}</td>
                    <td className="px-3 py-2">{row.subject_name || 'N/A'}</td>
                    <td className="px-3 py-2">{row.marks_obtained ?? 0}/{row.max_marks ?? 0}</td>
                    <td className="px-3 py-2">{row.grade || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    );
  };

  const renderLeaveHistory = () => {
    if (!leaveHistory.length) {
      return <div className="text-sm text-muted">No leave requests found for this student.</div>;
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-muted">
              <th className="px-3 py-2 font-medium">Start</th>
              <th className="px-3 py-2 font-medium">End</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Applied On</th>
              <th className="px-3 py-2 font-medium">Reason</th>
            </tr>
          </thead>
          <tbody>
            {leaveHistory.map((row) => (
              <tr key={row.id} className="border-b border-border/60">
                <td className="px-3 py-2">{formatDate(row.start_date)}</td>
                <td className="px-3 py-2">{formatDate(row.end_date)}</td>
                <td className="px-3 py-2">
                  <Badge tone={row.status === 'approved' ? 'success' : row.status === 'rejected' ? 'danger' : 'warning'}>
                    {String(row.status || 'pending').toUpperCase()}
                  </Badge>
                </td>
                <td className="px-3 py-2 text-muted">{formatDateTime(row.applied_on)}</td>
                <td className="px-3 py-2 text-muted">{row.reason || 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderAIReports = () => {
    if (!aiReportsHistory.length) {
      return <div className="text-sm text-muted">No AI reports generated yet for this student.</div>;
    }

    return (
      <div className="space-y-3">
        {aiReportsHistory.map((row) => (
          <div key={row.id} className="p-3 rounded-lg border border-border bg-slate-900 space-y-2">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-sm font-medium">{row.exam_name || 'Exam Result'}</p>
              <div className="flex items-center gap-2">
                <Badge tone={row.report_sent ? 'success' : 'warning'}>{row.report_sent ? 'Sent' : 'Not Sent'}</Badge>
                <span className="text-xs text-muted">Generated: {formatDateTime(row.report_generated_at)}</span>
              </div>
            </div>
            <p className="text-sm text-muted whitespace-pre-wrap">{row.ai_report || 'AI report text is not available for this result.'}</p>
            <p className="text-xs text-muted">Sent At: {formatDateTime(row.report_sent_at)}</p>
          </div>
        ))}
      </div>
    );
  };

  const renderTabPanel = () => {
    if (tab === 'Attendance History') {
      return renderAttendanceHistory();
    }
    if (tab === 'Marks History') {
      return renderMarksHistory();
    }
    if (tab === 'Leave History') {
      return renderLeaveHistory();
    }
    return renderAIReports();
  };

  if (loading) {
    return (
      <AppShell>
        <PageContainer>
          <p className="text-muted">Loading student profile...</p>
        </PageContainer>
      </AppShell>
    );
  }

  if (!student) {
    return (
      <AppShell>
        <PageContainer>
          <p className="text-muted">{error || 'Student profile is unavailable.'}</p>
        </PageContainer>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Student Profile" subtitle="Academic, attendance, leave and report history." />
        <Link to="/students" className="text-indigo-300 text-sm">← Back</Link>
        <Card>
          <CardBody>
            <div className="flex flex-wrap items-center gap-3">
              <div className="w-16 h-16 rounded-full bg-primary/30 overflow-hidden grid place-items-center text-2xl">
                {studentPhotoUrl ? (
                  <img src={studentPhotoUrl} alt={student.name} className="w-full h-full object-cover" />
                ) : (
                  student.name.split(' ').map((x) => x[0]).join('').slice(0, 2)
                )}
              </div>
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
          <Card><CardBody><p className="text-xs text-muted">Total Marks</p><h4 className="text-xl">{latestResult ? `${latestResult.total_marks}/${latestResult.max_total}` : 'N/A'}</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Rank</p><h4 className="text-xl">{latestResult?.rank ? `#${latestResult.rank}` : 'N/A'}</h4></CardBody></Card>
          <Card><CardBody><p className="text-xs text-muted">Leaves Taken</p><h4 className="text-xl">{approvedLeavesCount}</h4></CardBody></Card>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          <Card className="xl:col-span-2">
            <CardHeader title="Personal + Parent Details" />
            <CardBody className="text-sm text-muted space-y-1">
              <p>DOB: {formatDate(student.date_of_birth)}</p>
              <p>Blood Group: {student.blood_group}</p>
              <p>Address: {student.address}</p>
              <p>Father: {student.parent?.father_name || 'N/A'}</p>
              <p>Mother: {student.parent?.mother_name || 'N/A'}</p>
              <p>Phone: {student.parent?.phone_number || 'N/A'}</p>
              <p>Email: {student.parent?.email || 'N/A'}</p>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Registered Face" />
            <CardBody>
              {studentPhotoUrl ? (
                <img src={studentPhotoUrl} alt={`${student.name} face`} className="w-full aspect-square object-cover rounded-lg border border-border" />
              ) : (
                <div className="w-full aspect-square rounded-lg border border-border bg-slate-900 grid place-items-center text-muted text-sm">
                  No registered face image available
                </div>
              )}
              <div className="mt-3 text-xs text-muted">Face registration status: {student.face_registered ? 'Registered' : 'Pending'}</div>
            </CardBody>
          </Card>

          <Card>
            <CardHeader title="Recent Activity" />
            <CardBody className="text-sm text-muted space-y-2">
              <p>• Last attendance: {latestAttendance ? `${formatDate(latestAttendance.date)} P${latestAttendance.period}` : 'N/A'}</p>
              <p>• Last marks update: {latestResult?.exam_name || 'N/A'}</p>
              <p>• Last leave request: {latestLeave ? `${formatDate(latestLeave.start_date)} to ${formatDate(latestLeave.end_date)}` : 'N/A'}</p>
              <p>• Last AI report sent: {latestReport?.report_sent_at ? formatDateTime(latestReport.report_sent_at) : 'N/A'}</p>
            </CardBody>
          </Card>
        </div>

        <Card>
          <CardBody>
            <div className="flex flex-wrap gap-2 mb-3">
              {TABS.map((t) => (
                <button key={t} onClick={() => setTab(t)} className={`px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>
              ))}
            </div>
            <div className="p-4 rounded-lg bg-slate-900 border border-border text-sm text-muted">
              {renderTabPanel()}
            </div>
          </CardBody>
        </Card>
      </PageContainer>
    </AppShell>
  );
};
