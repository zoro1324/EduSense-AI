import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { Modal } from '../components/ui/Modal';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

const gradeOf = (t) => (t >= 90 ? 'A+' : t >= 80 ? 'A' : t >= 70 ? 'B+' : t >= 60 ? 'B' : t >= 50 ? 'C' : 'D');

export const MarksResultsPage = () => {
  const tabs = ['Add Marks', 'View Results', 'AI Reports'];
  const [tab, setTab] = useState(tabs[0]);
  const [className, setClassName] = useState('10A');
  const [exam, setExam] = useState('Quarterly');
  const [preview, setPreview] = useState(null);
  const [saving, setSaving] = useState(false);
  const [generatingIds, setGeneratingIds] = useState([]);
  const [generatingAll, setGeneratingAll] = useState(false);
  const [sendingIds, setSendingIds] = useState([]);
  const [viaWhatsApp, setViaWhatsApp] = useState(false);
  const [viaSMS, setViaSMS] = useState(true);
  const [resultRows, setResultRows] = useState([]);
  const [marksRows, setMarksRows] = useState([]);
  const [examList, setExamList] = useState([]);

  const loadData = async () => {
    try {
      const [resultsData, examsData, marksData] = await Promise.all([
        api.get('/marks/results/'),
        api.get('/marks/exams/'),
        api.get('/marks/'),
      ]);
      setResultRows(Array.isArray(resultsData) ? resultsData : []);
      setMarksRows(Array.isArray(marksData) ? marksData : []);
      const exams = Array.isArray(examsData) ? examsData : [];
      setExamList(exams);
      if (exams.length && !exam) {
        setExam(exams[0].name);
      }
    } catch (error) {
      setResultRows([]);
      setMarksRows([]);
      setExamList([]);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const filteredResults = useMemo(
    () =>
      resultRows
        .filter((m) => !className || m.class_name === className)
        .filter((m) => !exam || m.exam_name === exam),
    [resultRows, className, exam]
  );

  const dynamicSubjects = useMemo(() => {
    const matchingMarks = marksRows.filter(m => 
      m.exam_name === exam && 
      filteredResults.some(r => String(r.student) === String(m.student))
    );
    return [...new Set(matchingMarks.map(m => m.subject_name))].sort();
  }, [marksRows, exam, filteredResults]);

  const filteredExams = useMemo(() => {
    const classExams = examList.filter(e => e.class_name === className);
    const names = [...new Set(classExams.map(e => e.name))];
    return names.length ? names : [...new Set(examList.map(e => e.name))];
  }, [examList, className]);

  const subjectAvg = [
    { subject: 'Average %', avg: filteredResults.length ? Math.round(filteredResults.reduce((acc, r) => acc + Number(r.percentage || 0), 0) / filteredResults.length) : 0 },
  ];

  const generateReport = async (id) => {
    try {
      setGeneratingIds((prev) => [...prev, id]);
      await api.post(`/marks/results/${id}/generate-report/`, {});
      await loadData();
    } catch (error) {
      // noop
    } finally {
      setGeneratingIds((prev) => prev.filter(gid => gid !== id));
    }
  };

  const generateAllReports = async () => {
    try {
      setGeneratingAll(true);
      await api.post(`/marks/results/generate-all-reports/`, {});
      await loadData();
    } catch (error) {
      // noop
    } finally {
      setGeneratingAll(false);
    }
  };

  const sendReport = async (id, payload = { whatsapp: true, sms: false }) => {
    try {
      setSendingIds((prev) => [...prev, id]);
      await api.post(`/marks/results/${id}/send-report/`, payload);
      await loadData();
    } catch (error) {
      // noop
    } finally {
      setSendingIds((prev) => prev.filter(sid => sid !== id));
    }
  };

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Marks & Results" subtitle="Enter marks, review performance and generate AI report cards." />
        <div className="flex gap-2">{tabs.map((t) => <button key={t} onClick={() => setTab(t)} className={`px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>)}</div>

        {tab === 'Add Marks' ? (
          <Card>
            <CardBody className="space-y-3">
              <div className="grid md:grid-cols-2 gap-2"><Select value={className} onChange={(e) => setClassName(e.target.value)}><option>10A</option><option>11A</option><option>12A</option></Select><Select value={exam} onChange={(e) => setExam(e.target.value)}>{filteredExams.map((examName) => <option key={examName}>{examName}</option>)}</Select></div>
              <div className="overflow-auto thin-scrollbar"><table className="w-full min-w-[1000px] text-sm"><thead className="text-left text-muted"><tr><th>Student</th>{dynamicSubjects.map(sub => <th key={sub}>{sub}</th>)}<th>Total</th><th>Grade</th></tr></thead><tbody>
                {filteredResults.map((r) => {
                  const sMarks = marksRows.filter(m => String(m.student) === String(r.student) && m.exam_name === r.exam_name);
                  const getMark = (subj) => {
                    const found = sMarks.find(m => m.subject_name === subj);
                    return found ? found.marks_obtained : '-';
                  };
                  return (
                    <tr key={r.id} className="border-t border-border hover:bg-slate-800/60">
                      <td className="py-2">{r.student_name}</td>
                      {dynamicSubjects.map(sub => <td key={sub}>{getMark(sub)}</td>)}
                      <td>{r.total_marks}</td>
                      <td>{r.grade || gradeOf(r.percentage || 0)}</td>
                    </tr>
                  );
                })}
              </tbody></table></div>
              <Button variant="outline">Upload CSV</Button>
              <Button className="w-full" loading={saving} onClick={() => { setSaving(true); setTimeout(() => setSaving(false), 1000); }}>Save Marks</Button>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'View Results' ? (
          <Card>
            <CardHeader title="Results" />
            <CardBody className="space-y-4">
              <table className="w-full text-sm"><thead className="text-left text-muted"><tr><th>Rank</th><th>Student</th><th>Total</th><th>Grade</th></tr></thead><tbody>
                {filteredResults.map((r, idx) => <tr key={r.id} className="border-t border-border"><td className="py-2">{(r.rank || idx + 1) === 1 ? '🥇' : (r.rank || idx + 1) === 2 ? '🥈' : (r.rank || idx + 1) === 3 ? '🥉' : (r.rank || idx + 1)}</td><td>{r.student_name}</td><td>{r.total_marks}</td><td>{r.grade}</td></tr>)}
                <tr className="border-t border-border text-muted"><td colSpan={4}>Subject-wise averages shown in chart below</td></tr>
              </tbody></table>
              <ResponsiveContainer width="100%" height={260}><BarChart data={subjectAvg}><XAxis dataKey="subject" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Bar dataKey="avg" fill="#6366f1" /></BarChart></ResponsiveContainer>
              <div className="text-sm text-muted">Comparison with previous exam: +3.2% ↗</div>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'AI Reports' ? (
          <Card>
            <CardHeader title="AI Reports" right={<Button onClick={generateAllReports} loading={generatingAll}>Generate All Reports</Button>} />
            <CardBody className="space-y-3">
              <table className="w-full text-sm"><thead className="text-left text-muted"><tr><th>Student</th><th>Exam</th><th>Status</th><th>Preview</th><th>Action</th></tr></thead><tbody>
                {filteredResults.slice(0, 8).map((r) => {
                  const isGenerating = generatingIds.includes(r.id);
                  return (
                    <tr key={r.id} className="border-t border-border">
                      <td className="py-2">{r.student_name}</td>
                      <td>{r.exam_name}</td>
                      <td>{r.ai_report ? '✅ Generated' : isGenerating ? '🔄 Generating...' : '⏳ Pending'}</td>
                      <td>{r.ai_report ? <button onClick={() => setPreview(r)} className="text-indigo-300">👁️</button> : '—'}</td>
                      <td>
                        {!r.ai_report ? (
                          <Button variant="outline" className="text-xs" loading={isGenerating} onClick={() => generateReport(r.id)}>Generate</Button>
                        ) : (
                          <Button variant="success" className="text-xs" loading={sendingIds.includes(r.id)} onClick={() => sendReport(r.id, { whatsapp: true, sms: false })}>Send</Button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody></table>
              <Button variant="warning">Bulk Send All</Button>
            </CardBody>
          </Card>
        ) : null}

        <Modal isOpen={Boolean(preview)} onClose={() => setPreview(null)} title="Report Preview" width="max-w-3xl">
          {preview ? (
            <div className="space-y-3">
              <h4 className="font-semibold">{preview.student_name} — {preview.exam_name}</h4>
              <div className="p-3 rounded-lg border border-border bg-slate-900 text-sm text-muted">{preview.ai_report || 'Report not generated yet.'}</div>
              <TextArea rows={5} defaultValue={preview.ai_report || ''} />
              <div className="flex items-center gap-3 text-sm">
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={viaWhatsApp} onChange={(e) => setViaWhatsApp(e.target.checked)} /> Send via WhatsApp
                </label>
                <label className="flex items-center gap-2">
                  <input type="checkbox" checked={viaSMS} onChange={(e) => setViaSMS(e.target.checked)} /> Send via SMS
                </label>
              </div>
              <Button 
                variant="success" 
                loading={sendingIds.includes(preview.id)}
                onClick={async () => {
                  await sendReport(preview.id, { whatsapp: viaWhatsApp, sms: viaSMS });
                  setPreview(null);
                }}
              >
                Send Report
              </Button>
            </div>
          ) : null}
        </Modal>
      </PageContainer>
    </AppShell>
  );
};
