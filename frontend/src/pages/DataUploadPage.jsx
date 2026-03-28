import React, { useState, useMemo, useRef } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';
import { api } from '../lib/api';

const REQUIRED_COLUMNS = [
  'roll_number', 'name', 'class_name', 'date_of_birth', 
  'blood_group', 'address', 'father_name', 'mother_name', 
  'whatsapp_number', 'phone_number', 'email'
];

export const DataUploadPage = () => {
  const [file, setFile] = useState(null);
  const [csvHeaders, setCsvHeaders] = useState([]);
  const [csvRows, setCsvRows] = useState([]);
  const [mapping, setMapping] = useState({});
  const [mapped, setMapped] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [progress, setProgress] = useState(0);
  const [importResult, setImportResult] = useState(null);
  const fileInputRef = useRef(null);
  const { pushToast } = useToast();

  const downloadTemplate = () => {
    const csvContent = REQUIRED_COLUMNS.join(',') + '\n';
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.href = url;
    link.setAttribute('download', 'student_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleFileUpload = (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target.result;
      const lines = text.split(/\r?\n/).filter(line => line.trim());
      if (lines.length > 0) {
        const headers = lines[0].split(',').map(h => h.trim());
        setCsvHeaders(headers);
        const rows = lines.slice(1).map(line => line.split(',').map(c => c.trim()));
        setCsvRows(rows);
        
        const initialMapping = {};
        REQUIRED_COLUMNS.forEach(reqCol => {
          const match = headers.find(h => h.toLowerCase() === reqCol.toLowerCase() || h.toLowerCase().replace(/_/g, '') === reqCol.toLowerCase().replace(/_/g, ''));
          initialMapping[reqCol] = match || '';
        });
        setMapping(initialMapping);
        setMapped(false);
        setImportResult(null);
      }
    };
    reader.readAsText(selectedFile);
  };

  const handleMappingChange = (reqCol, csvCol) => {
    setMapping(prev => ({ ...prev, [reqCol]: csvCol }));
  };

  const previewData = useMemo(() => {
    if (!mapped) return [];
    return csvRows.map(row => {
      const mappedRow = {};
      REQUIRED_COLUMNS.forEach(reqCol => {
        const csvColName = mapping[reqCol];
        if (csvColName) {
          const colIndex = csvHeaders.indexOf(csvColName);
          mappedRow[reqCol] = colIndex !== -1 ? row[colIndex] : '';
        } else {
          mappedRow[reqCol] = '';
        }
      });
      const isValid = Boolean(mappedRow.name && mappedRow.roll_number && mappedRow.class_name);
      return { data: mappedRow, isValid };
    });
  }, [mapped, csvRows, csvHeaders, mapping]);

  const validCount = previewData.filter(r => r.isValid).length;
  const invalidCount = previewData.length - validCount;

  const doImport = async () => {
    if (validCount === 0) {
      pushToast('No valid rows to import', 'error');
      return;
    }
    
    setConfirming(true);
    setProgress(10);
    try {
      // Build final CSV string
      const headersRow = REQUIRED_COLUMNS.join(',');
      const bodyRows = previewData
        .filter(r => r.isValid)
        .map(r => REQUIRED_COLUMNS.map(col => `"${(r.data[col] || '').replace(/"/g, '""')}"`).join(','));
      
      const finalCsv = [headersRow, ...bodyRows].join('\n');
      const blob = new Blob([finalCsv], { type: 'text/csv' });
      const formData = new FormData();
      formData.append('file', blob, 'upload.csv');
      
      setProgress(50);
      const res = await api.post('/students/bulk-upload/', formData);
      setProgress(100);
      setImportResult({ success: true, message: `✅ ${res.created} students imported successfully` });
      pushToast(`${res.created} students imported`, 'success');
    } catch (error) {
      setProgress(100);
      setImportResult({ success: false, message: `❌ Import failed: ${error.message}` });
      pushToast(error.message || 'Import failed', 'error');
    }
  };

  const reset = () => {
    setFile(null);
    setCsvHeaders([]);
    setCsvRows([]);
    setMapped(false);
    setConfirming(false);
    setImportResult(null);
    setProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Data Upload" subtitle="Upload student master data via CSV with validation and import progress." />

        <Card>
          <CardHeader title="Step 1 — Download Template" right={file ? <Button variant="outline" onClick={reset}>Reset</Button> : null}/>
          <CardBody className="space-y-3">
            <Button onClick={downloadTemplate}>Download CSV Template</Button>
            <p className="text-sm text-muted">Required columns: {REQUIRED_COLUMNS.join(', ')}</p>
          </CardBody>
        </Card>

        {!file ? (
          <Card>
            <CardHeader title="Step 2 — Upload File" />
            <CardBody>
              <input type="file" accept=".csv" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />
              <button onClick={() => fileInputRef.current?.click()} className="w-full border border-dashed border-border rounded-xl p-8 bg-slate-900 text-muted hover:bg-slate-800 transition">
                ⤴ Drag and drop .csv or click to browse
                <div className="text-xs mt-2">Accepted: .csv only · Max size: 5MB</div>
              </button>
            </CardBody>
          </Card>
        ) : null}

        {file && !mapped ? (
          <Card>
            <CardHeader title="Step 3 — Column Mapper" />
            <CardBody className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {REQUIRED_COLUMNS.map((reqCol) => (
                  <div key={reqCol} className="flex items-center justify-between gap-3 bg-slate-900 p-2 rounded-lg border border-border">
                    <div className="text-sm text-muted font-medium w-1/2 break-words">{reqCol} {['name', 'roll_number', 'class_name'].includes(reqCol) ? <span className="text-red-400">*</span> : null}</div>
                    <Select className="w-1/2" value={mapping[reqCol]} onChange={(e) => handleMappingChange(reqCol, e.target.value)}>
                      <option value="">-- Ignore / Empty --</option>
                      {csvHeaders.map(h => <option key={h} value={h}>{h}</option>)}
                    </Select>
                  </div>
                ))}
              </div>
              <Button onClick={() => setMapped(true)}>Review Data & Continue</Button>
            </CardBody>
          </Card>
        ) : null}

        {mapped && !confirming ? (
          <Card>
            <CardHeader title="Step 4 — Preview Table" />
            <CardBody className="space-y-3">
              <div className="overflow-auto thin-scrollbar max-h-96">
                <table className="w-full text-sm min-w-[900px]">
                  <thead className="sticky top-0 bg-slate-800 z-10">
                    <tr className="text-left text-muted">                     
                      <th className="p-2">Name</th>
                      <th className="p-2">Roll</th>
                      <th className="p-2">Class</th>
                      <th className="p-2">DOB</th>
                      <th className="p-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                  {previewData.slice(0, 50).map((r, i) => (
                    <tr key={i} className="border-t border-border hover:bg-slate-800/60">
                      <td className="p-2">{r.data.name || '-'}</td>
                      <td className="p-2">{r.data.roll_number || '-'}</td>
                      <td className="p-2">{r.data.class_name || '-'}</td>
                      <td className="p-2">{r.data.date_of_birth || '-'}</td>
                      <td className="p-2">{r.isValid ? <Badge tone="success">Valid</Badge> : <Badge tone="danger">Missing Req</Badge>}</td>
                    </tr>
                  ))}
                  </tbody>
                </table>
              </div>
              {previewData.length > 50 && <p className="text-xs text-muted italic">Showing first 50 rows of {previewData.length} total.</p>}
              
              {invalidCount > 0 ? (
                <p className="text-sm text-danger">{invalidCount} rows are missing required fields (name, roll_number, class_name) and will be skipped.</p>
              ) : (
                <p className="text-sm text-success">All {validCount} rows are valid and ready to import.</p>
              )}
              
              <div className="flex gap-2 pt-2 border-t border-border">
                <Button variant="success" onClick={doImport} disabled={validCount === 0}>Confirm Import ({validCount})</Button>
                <Button variant="outline" onClick={() => setMapped(false)}>Back to Mapping</Button>
              </div>
            </CardBody>
          </Card>
        ) : null}

        {confirming ? (
          <Card>
            <CardHeader title="Import Progress" />
            <CardBody className="space-y-3">
              <div className="w-full h-2 rounded bg-slate-700 overflow-hidden">
                <div className="h-2 rounded bg-green-500 transition-all duration-300" style={{ width: `${progress}%` }} />
              </div>
              {!importResult ? (
                <p className="text-sm text-muted">Importing students, please wait...</p>
              ) : (
                <div className={`text-sm ${importResult.success ? 'text-green-400' : 'text-danger'}`}>
                  {importResult.message}
                </div>
              )}
              {importResult && (
                <Button variant="outline" onClick={reset} className="mt-2">Upload Another File</Button>
              )}
            </CardBody>
          </Card>
        ) : null}
      </PageContainer>
    </AppShell>
  );
};
