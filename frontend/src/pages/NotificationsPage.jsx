import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';
import { api } from '../lib/api';

const typeTone = { absent: 'danger', leave_approved: 'success', leave_rejected: 'warning', result_report: 'info', safety_alert: 'warning' };
const channelTone = { whatsapp: 'success', sms: 'default' };
const statusTone = { delivered: 'success', failed: 'danger', pending: 'warning', sent: 'info' };

export const NotificationsPage = () => {
  const [notificationsLog, setNotificationsLog] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [templateKey, setTemplateKey] = useState('absent');
  const [templateText, setTemplateText] = useState('');
  const [page, setPage] = useState(1);
  const { pushToast } = useToast();

  const loadData = async () => {
    try {
      const [logsData, templatesData] = await Promise.all([
        api.get('/notifications/'),
        api.get('/notifications/templates/'),
      ]);
      const logRows = Array.isArray(logsData) ? logsData : [];
      const templateRows = Array.isArray(templatesData) ? templatesData : [];
      setNotificationsLog(logRows);
      setTemplates(templateRows);
      if (templateRows.length) {
        const first = templateRows[0];
        setTemplateKey(first.template_type);
        setTemplateText(first.template_body || '');
      }
    } catch (error) {
      setNotificationsLog([]);
      setTemplates([]);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const rows = useMemo(() => notificationsLog.slice((page - 1) * 4, page * 4), [page]);

  const saveTemplate = async () => {
    const selected = templates.find((t) => t.template_type === templateKey);
    if (!selected) {
      return;
    }
    try {
      await api.put(`/notifications/templates/${selected.id}/`, {
        template_body: templateText,
      });
      pushToast('Template saved', 'success');
      loadData();
    } catch (error) {
      pushToast(error.message || 'Failed to save template', 'error');
    }
  };

  const resend = async (id) => {
    try {
      await api.post(`/notifications/${id}/resend/`, {});
      pushToast('Resent successfully', 'success');
      loadData();
    } catch (error) {
      pushToast(error.message || 'Resend failed', 'error');
    }
  };

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
                          <td className="py-2"><Badge tone={typeTone[n.notification_type] || 'default'}>{n.notification_type}</Badge></td>
                          <td>{n.student_name || '—'}</td><td>{n.parent_name}</td>
                          <td><Badge tone={channelTone[n.channel] || 'default'}>{n.channel}</Badge></td>
                          <td>{new Date(n.sent_at).toLocaleString()}</td>
                          <td><Badge tone={statusTone[n.status] || 'default'}>{n.status}</Badge></td>
                          <td>{n.status === 'failed' ? <Button variant="outline" className="text-xs" onClick={() => resend(n.id)}>Resend</Button> : '—'}</td>
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
                {templates.map((tpl) => (
                  <button
                    key={tpl.id}
                    onClick={() => { setTemplateKey(tpl.template_type); setTemplateText(tpl.template_body || ''); }}
                    className={`w-full text-left px-3 py-2 rounded-lg ${templateKey === tpl.template_type ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}
                  >
                    {tpl.template_type}
                  </button>
                ))}
                <TextArea value={templateText} onChange={(e) => setTemplateText(e.target.value)} rows={6} />
                <p className="text-xs text-muted">Variables: {'{student_name} {date} {class} {marks} {parent_name}'}</p>
                <div className="flex gap-2"><Button onClick={saveTemplate}>Save Template</Button><Button variant="outline" onClick={() => {
                  const selected = templates.find((t) => t.template_type === templateKey);
                  setTemplateText(selected?.template_body || '');
                }}>Reset</Button></div>
              </CardBody>
            </Card>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
};
