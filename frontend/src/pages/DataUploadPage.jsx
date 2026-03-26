import React, { useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';

export const DataUploadPage = () => {
  const [fileReady, setFileReady] = useState(false);
  const [mapped, setMapped] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [progress, setProgress] = useState(0);
  const { pushToast } = useToast();

  const doImport = () => {
    setConfirming(true);
    let step = 0;
    const timer = setInterval(() => {
      step += 12;
      setProgress(step);
      if (step >= 100) {
        clearInterval(timer);
        pushToast('✅ 58 students imported successfully', 'success');
      }
    }, 180);
  };

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Data Upload" subtitle="Upload student master data via CSV with validation and import progress." />

        <Card>
          <CardHeader title="Step 1 — Download Template" />
          <CardBody className="space-y-3">
            <Button>Download CSV Template</Button>
            <p className="text-sm text-muted">Required columns: name, roll_no, class, dob, blood_group, address, father_name, mother_name, parent_phone, parent_email</p>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Step 2 — Upload File" />
          <CardBody>
            <button onClick={() => setFileReady(true)} className="w-full border border-dashed border-border rounded-xl p-8 bg-slate-900 text-muted hover:bg-slate-800 transition">
              ⤴ Drag and drop .csv or click to browse
              <div className="text-xs mt-2">Accepted: .csv only · Max size: 5MB</div>
            </button>
          </CardBody>
        </Card>

        {fileReady ? (
          <Card>
            <CardHeader title="Step 3 — Column Mapper" />
            <CardBody className="space-y-2">
              {['name', 'roll_no', 'class', 'dob', 'blood_group'].map((col) => (
                <div key={col} className="grid grid-cols-2 gap-2 items-center">
                  <div className="text-sm text-muted">Your CSV: {col}</div>
                  <Select><option>{col}</option><option>Ignore</option></Select>
                </div>
              ))}
              <Button onClick={() => setMapped(true)}>Auto-detect & Continue</Button>
            </CardBody>
          </Card>
        ) : null}

        {mapped ? (
          <Card>
            <CardHeader title="Step 4 — Preview Table" />
            <CardBody className="space-y-3">
              <div className="overflow-auto thin-scrollbar">
                <table className="w-full text-sm min-w-[700px]"><thead><tr className="text-left text-muted"><th>Name</th><th>Roll</th><th>Class</th><th>DOB</th><th>Status</th></tr></thead><tbody>
                  {Array.from({ length: 10 }).map((_, i) => (
                    <tr key={i} className="border-t border-border"><td className="py-2">Student {i + 1}</td><td>{10 + i}</td><td>10A</td><td>2009-01-01</td><td>{i % 4 === 0 ? <Badge tone="danger">Error</Badge> : <Badge tone="success">Valid</Badge>}</td></tr>
                  ))}
                </tbody></table>
              </div>
              <p className="text-sm text-danger">3 rows have errors — fix before import</p>
              <div className="flex gap-2">
                <Button variant="success" onClick={doImport}>Confirm Import</Button>
                <Button variant="outline">Cancel</Button>
              </div>
            </CardBody>
          </Card>
        ) : null}

        {confirming ? (
          <Card>
            <CardHeader title="Import Progress" />
            <CardBody className="space-y-2">
              <div className="w-full h-2 rounded bg-slate-700"><div className="h-2 rounded bg-green-500" style={{ width: `${progress}%` }} /></div>
              <p className="text-sm text-muted">Importing student {Math.min(60, Math.round(progress * 0.6))} of 60...</p>
              {progress >= 100 ? <div className="text-sm text-green-300">✅ 58 students imported successfully · ❌ 2 failed — Download error report</div> : null}
            </CardBody>
          </Card>
        ) : null}
      </PageContainer>
    </AppShell>
  );
};
