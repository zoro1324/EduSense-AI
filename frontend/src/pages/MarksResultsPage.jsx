import React, { useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { quarterlyMarks } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { Modal } from '../components/ui/Modal';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const gradeOf = (t) => (t >= 90 ? 'A+' : t >= 80 ? 'A' : t >= 70 ? 'B+' : t >= 60 ? 'B' : t >= 50 ? 'C' : 'D');

export const MarksResultsPage = () => {
  const tabs = ['Add Marks', 'View Results', 'AI Reports'];
  const [tab, setTab] = useState(tabs[0]);
  const [className, setClassName] = useState('10A');
  const [exam, setExam] = useState('Quarterly');
  const [preview, setPreview] = useState(null);
  const [saving, setSaving] = useState(false);

  const rows = useMemo(() => quarterlyMarks.filter((m) => m.className === className), [className]);
  const resultRows = rows.map((r) => {
    const total = r.tamil + r.english + r.maths + r.science + r.social;
    const avg = Math.round(total / 5);
    return { ...r, total, grade: gradeOf(avg) };
  }).sort((a, b) => b.total - a.total).map((r, i) => ({ ...r, rank: i + 1 }));

  const subjectAvg = ['tamil', 'english', 'maths', 'science', 'social'].map((s) => ({ subject: s, avg: Math.round(resultRows.reduce((acc, r) => acc + r[s], 0) / resultRows.length) }));

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Marks & Results" subtitle="Enter marks, review performance and generate AI report cards." />
        <div className="flex gap-2">{tabs.map((t) => <button key={t} onClick={() => setTab(t)} className={`px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>)}</div>

        {tab === 'Add Marks' ? (
          <Card>
            <CardBody className="space-y-3">
              <div className="grid md:grid-cols-2 gap-2"><Select value={className} onChange={(e) => setClassName(e.target.value)}><option>10A</option><option>11A</option><option>12A</option></Select><Select value={exam} onChange={(e) => setExam(e.target.value)}><option>Unit Test 1</option><option>Unit Test 2</option><option>Quarterly</option><option>Half Yearly</option><option>Annual</option></Select></div>
              <div className="overflow-auto thin-scrollbar"><table className="w-full min-w-[1000px] text-sm"><thead className="text-left text-muted"><tr><th>Student</th><th>Tamil</th><th>English</th><th>Maths</th><th>Science</th><th>Social</th><th>Total</th><th>Grade</th></tr></thead><tbody>
                {resultRows.map((r) => <tr key={r.id} className="border-t border-border hover:bg-slate-800/60"><td className="py-2">{r.student}</td><td>{r.tamil}</td><td>{r.english}</td><td className={r.maths > 100 ? 'text-red-400' : ''}>{r.maths}</td><td>{r.science}</td><td>{r.social}</td><td>{r.total}</td><td>{r.grade}</td></tr>)}
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
                {resultRows.map((r) => <tr key={r.id} className="border-t border-border"><td className="py-2">{r.rank === 1 ? '🥇' : r.rank === 2 ? '🥈' : r.rank === 3 ? '🥉' : r.rank}</td><td>{r.student}</td><td>{r.total}</td><td>{r.grade}</td></tr>)}
                <tr className="border-t border-border text-muted"><td colSpan={4}>Subject-wise averages shown in chart below</td></tr>
              </tbody></table>
              <ResponsiveContainer width="100%" height={260}><BarChart data={subjectAvg}><XAxis dataKey="subject" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip /><Bar dataKey="avg" fill="#6366f1" /></BarChart></ResponsiveContainer>
              <div className="text-sm text-muted">Comparison with previous exam: +3.2% ↗</div>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'AI Reports' ? (
          <Card>
            <CardHeader title="AI Reports" right={<Button>Generate All Reports</Button>} />
            <CardBody className="space-y-3">
              <table className="w-full text-sm"><thead className="text-left text-muted"><tr><th>Student</th><th>Exam</th><th>Status</th><th>Preview</th><th>Action</th></tr></thead><tbody>
                {resultRows.slice(0, 8).map((r, i) => <tr key={r.id} className="border-t border-border"><td className="py-2">{r.student}</td><td>{exam}</td><td>{i % 3 === 0 ? '⏳ Pending' : '✅ Generated'}</td><td>{i % 3 === 0 ? '—' : <button onClick={() => setPreview(r)} className="text-indigo-300">👁️</button>}</td><td>{i % 3 === 0 ? <Button variant="outline" className="text-xs">Generate</Button> : <Button variant="success" className="text-xs">Send</Button>}</td></tr>)}
              </tbody></table>
              <div className="w-full h-2 rounded bg-slate-700"><div className="h-2 rounded bg-primary" style={{ width: '46%' }} /></div>
              <div className="text-xs text-muted">Generating report for Meena S...</div>
              <Button variant="warning">Bulk Send All</Button>
            </CardBody>
          </Card>
        ) : null}

        <Modal isOpen={Boolean(preview)} onClose={() => setPreview(null)} title="Report Preview" width="max-w-3xl">
          {preview ? (
            <div className="space-y-3">
              <h4 className="font-semibold">{preview.student} — {exam}</h4>
              <div className="p-3 rounded-lg border border-border bg-slate-900 text-sm text-muted">{preview.student} has shown consistent progress in language subjects, with stronger performance in Maths and Science. Recommend focused revision on Social and more practice tests before finals.</div>
              <TextArea rows={5} defaultValue="Editable report text..." />
              <div className="flex items-center gap-3 text-sm"><label className="flex items-center gap-2"><input type="checkbox" defaultChecked /> Send via WhatsApp</label><label className="flex items-center gap-2"><input type="checkbox" /> Send via SMS</label></div>
              <Button variant="success">Send Report</Button>
            </div>
          ) : null}
        </Modal>
      </PageContainer>
    </AppShell>
  );
};
