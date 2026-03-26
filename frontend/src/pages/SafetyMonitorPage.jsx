import React, { useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { safetyAlerts } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { Modal } from '../components/ui/Modal';
import { TableWrapper } from '../components/ui/Table';
import { useToast } from '../components/ui/ToastContext';

export const SafetyMonitorPage = () => {
  const [location, setLocation] = useState('Block A');
  const [snapshot, setSnapshot] = useState(null);
  const [alerts, setAlerts] = useState(safetyAlerts);
  const { pushToast } = useToast();

  const threat = 'Warning';
  const unresolved = useMemo(() => alerts.filter((a) => a.status === 'Unresolved'), [alerts]);

  const resolveAlert = (id) => {
    setAlerts((prev) => prev.map((a) => (a.id === id ? { ...a, status: 'Resolved' } : a)));
    pushToast('Alert resolved', 'success');
  };

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Safety Monitor" subtitle="Monitor high-risk patterns from CCTV and resolve incidents." />

        <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
          <div className="xl:col-span-3 space-y-3">
            <Select value={location} onChange={(e) => setLocation(e.target.value)}>
              <option>Block A</option><option>Block B</option><option>Corridor</option><option>Canteen</option>
            </Select>
            <Card>
              <CardBody>
                <div className="relative aspect-video border border-border rounded-xl bg-slate-700/40 grid place-items-center text-muted">
                  <div className="text-center"><div className="text-5xl">🛡️</div><p>Safety Feed</p></div>
                  <div className="absolute top-3 right-3"><Badge tone="warning">🟡 {threat}</Badge></div>
                </div>
              </CardBody>
            </Card>
          </div>

          <div className="xl:col-span-2 space-y-4">
            <Card>
              <CardHeader title="Live Alert Feed" />
              <CardBody className="space-y-2 max-h-[360px] overflow-auto thin-scrollbar">
                {alerts.map((a) => (
                  <div key={a.id} className={`p-3 rounded-lg border-l-4 ${a.level === 'Alert' ? 'border-red-500' : a.level === 'Warning' ? 'border-yellow-500' : 'border-green-500'} bg-slate-900 border border-border`}>
                    <div className="flex items-center justify-between">
                      <Badge tone={a.level === 'Alert' ? 'danger' : a.level === 'Warning' ? 'warning' : 'success'}>{a.level}</Badge>
                      <span className="text-xs text-muted">{a.timestamp}</span>
                    </div>
                    <p className="text-sm mt-2">{a.location}</p>
                    <div className="flex gap-2 mt-3 flex-wrap">
                      <Button variant="outline" className="text-xs px-2 py-1" onClick={() => setSnapshot(a)}>📸 View Snapshot</Button>
                      <Button variant="success" className="text-xs px-2 py-1" onClick={() => resolveAlert(a.id)}>Resolve</Button>
                      <Button variant="warning" className="text-xs px-2 py-1" onClick={() => pushToast('Alert sent to admin', 'warning')}>Send to Admin</Button>
                    </div>
                  </div>
                ))}
              </CardBody>
            </Card>

            <Card>
              <CardHeader title="Threat Levels" />
              <CardBody className="space-y-2 text-sm text-muted">
                <div>🟢 Normal — No unusual grouping</div>
                <div>🟡 Warning — Group of 4+ detected</div>
                <div>🔴 Alert — Isolated person surrounded</div>
              </CardBody>
            </Card>
          </div>
        </div>

        <Card>
          <CardHeader title="Alert History" right={<Button variant="outline">Export Report</Button>} />
          <CardBody className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
              <Input type="date" />
              <Select><option>All Locations</option><option>Block A</option><option>Block B</option><option>Corridor</option></Select>
              <Select><option>All Status</option><option>Resolved</option><option>Unresolved</option></Select>
              <Input placeholder="Search" />
            </div>
            <TableWrapper
              columns={['Time', 'Location', 'Snapshot', 'Threat Level', 'Status', 'Action']}
              rows={alerts}
              renderRow={(a) => (
                <tr key={a.id} className="border-b border-border hover:bg-slate-800/60">
                  <td className="px-3 py-2">{a.timestamp}</td>
                  <td className="px-3 py-2">{a.location}</td>
                  <td className="px-3 py-2"><Button variant="outline" className="text-xs px-2 py-1" onClick={() => setSnapshot(a)}>View</Button></td>
                  <td className="px-3 py-2"><Badge tone={a.level === 'Alert' ? 'danger' : a.level === 'Warning' ? 'warning' : 'success'}>{a.level}</Badge></td>
                  <td className="px-3 py-2"><Badge tone={a.status === 'Unresolved' ? 'danger' : 'success'}>{a.status}</Badge></td>
                  <td className="px-3 py-2 flex gap-2"><Button variant="success" className="text-xs px-2 py-1" onClick={() => resolveAlert(a.id)}>Resolve</Button><Button variant="outline" className="text-xs px-2 py-1" onClick={() => setSnapshot(a)}>View</Button></td>
                </tr>
              )}
            />
          </CardBody>
        </Card>

        <Modal isOpen={Boolean(snapshot)} onClose={() => setSnapshot(null)} title="Snapshot Preview">
          {snapshot ? (
            <div className="space-y-3">
              <div className="h-56 bg-slate-700/40 border border-border rounded-lg grid place-items-center text-muted">Image placeholder ({snapshot.snapshot})</div>
              <p className="text-sm text-muted">{snapshot.timestamp} · {snapshot.location}</p>
              <Badge tone={snapshot.level === 'Alert' ? 'danger' : snapshot.level === 'Warning' ? 'warning' : 'success'}>{snapshot.level}</Badge>
            </div>
          ) : null}
        </Modal>
      </PageContainer>
    </AppShell>
  );
};
