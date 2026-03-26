import React, { useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { messageTemplates, notificationsLog } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';

const typeTone = { Absent: 'danger', Leave: 'warning', Result: 'info', Safety: 'warning' };
const channelTone = { WhatsApp: 'success', SMS: 'default' };
const statusTone = { Delivered: 'success', Failed: 'danger', Pending: 'warning' };

export const NotificationsPage = () => {
  const [templateKey, setTemplateKey] = useState('absent');
  const [templateText, setTemplateText] = useState(messageTemplates.absent);
  const [page, setPage] = useState(1);
  const { pushToast } = useToast();

  const rows = useMemo(() => notificationsLog.slice((page - 1) * 4, page * 4), [page]);

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Notifications" subtitle="Track outbound notifications and manage reusable templates." />

        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
          <div className="xl:col-span-8">
            <Card>
              <CardHeader title="Sent Notifications" />
              <CardBody className="space-y-3">
                <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                  <Select><option>All Types</option><option>Absent</option><option>Leave</option><option>Result</option></Select>
                  <Select><option>All Channels</option><option>WhatsApp</option><option>SMS</option></Select>
                  <Input type="date" />
                  <Select><option>All Status</option><option>Delivered</option><option>Failed</option><option>Pending</option></Select>
                  <Input placeholder="Search" />
                </div>
                <div className="overflow-auto thin-scrollbar">
                  <table className="w-full min-w-[900px] text-sm">
                    <thead className="text-left text-muted"><tr><th>Type</th><th>Student</th><th>Parent</th><th>Channel</th><th>Time</th><th>Status</th><th>Action</th></tr></thead>
                    <tbody>
                      {rows.map((n) => (
                        <tr key={n.id} className="border-t border-border hover:bg-slate-800/60">
                          <td className="py-2"><Badge tone={typeTone[n.type] || 'default'}>{n.type}</Badge></td>
                          <td>{n.student}</td><td>{n.parent}</td>
                          <td><Badge tone={channelTone[n.channel] || 'default'}>{n.channel}</Badge></td>
                          <td>{n.time}</td>
                          <td><Badge tone={statusTone[n.status] || 'default'}>{n.status}</Badge></td>
                          <td>{n.status === 'Failed' ? <Button variant="outline" className="text-xs" onClick={() => pushToast('Resent successfully', 'success')}>Resend</Button> : '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex justify-end gap-2"><Button variant="outline" disabled={page === 1} onClick={() => setPage((p) => p - 1)}>Prev</Button><Button variant="outline" disabled={page === 2} onClick={() => setPage((p) => p + 1)}>Next</Button></div>
              </CardBody>
            </Card>
          </div>

          <div className="xl:col-span-4">
            <Card>
              <CardHeader title="Message Templates" />
              <CardBody className="space-y-2">
                {Object.keys(messageTemplates).map((k) => (
                  <button
                    key={k}
                    onClick={() => { setTemplateKey(k); setTemplateText(messageTemplates[k]); }}
                    className={`w-full text-left px-3 py-2 rounded-lg ${templateKey === k ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}
                  >
                    {k}
                  </button>
                ))}
                <TextArea value={templateText} onChange={(e) => setTemplateText(e.target.value)} rows={6} />
                <p className="text-xs text-muted">Variables: {'{student_name} {date} {class} {marks} {parent_name}'}</p>
                <div className="flex gap-2"><Button onClick={() => pushToast('Template saved', 'success')}>Save Template</Button><Button variant="outline" onClick={() => setTemplateText(messageTemplates[templateKey])}>Reset</Button></div>
              </CardBody>
            </Card>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
};
