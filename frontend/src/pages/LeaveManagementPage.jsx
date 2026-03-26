import React, { useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { attendanceRows, leaveRequests } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { Modal } from '../components/ui/Modal';
import { useToast } from '../components/ui/ToastContext';

export const LeaveManagementPage = () => {
  const tabs = ['Pending Requests', 'Leave History', 'Unexcused Absences'];
  const [tab, setTab] = useState(tabs[0]);
  const [approval, setApproval] = useState(null);
  const [rejecting, setRejecting] = useState(null);
  const { pushToast } = useToast();

  const unexcused = useMemo(() => attendanceRows.filter((s) => s.attendance < 75).slice(0, 6), []);

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Leave Management" subtitle="Approve leave requests and trigger parent notifications." />
        <div className="flex gap-2 flex-wrap">
          {tabs.map((t) => <button key={t} onClick={() => setTab(t)} className={`px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>)}
        </div>

        {tab === 'Pending Requests' ? (
          <Card>
            <CardBody className="space-y-3">
              <div className="grid md:grid-cols-3 gap-2"><Select><option>All Classes</option><option>10A</option><option>11A</option></Select><Input type="date" /><Input placeholder="Search" /></div>
              <div className="overflow-auto thin-scrollbar"><table className="w-full min-w-[900px] text-sm"><thead className="text-left text-muted"><tr><th>Student</th><th>Class</th><th>Date</th><th>Reason</th><th>Applied On</th><th>Action</th></tr></thead><tbody>
                {leaveRequests.map((r) => (
                  <tr key={r.id} className="border-t border-border hover:bg-slate-800/60"><td className="py-2">{r.student}</td><td>{r.className}</td><td>{r.date}</td><td>{r.reason}</td><td>{r.appliedOn}</td><td className="flex gap-2 py-2"><Button variant="success" className="text-xs px-2 py-1" onClick={() => setApproval(r)}>Approve</Button><Button variant="danger" className="text-xs px-2 py-1" onClick={() => setRejecting(r)}>Reject</Button></td></tr>
                ))}
              </tbody></table></div>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'Leave History' ? (
          <Card>
            <CardHeader title="Leave History" right={<Button variant="outline">Export CSV</Button>} />
            <CardBody>
              <table className="w-full text-sm"><thead className="text-left text-muted"><tr><th>Student</th><th>Class</th><th>Date</th><th>Reason</th><th>Status</th><th>Notified</th><th>Actions</th></tr></thead><tbody>
                {leaveRequests.map((r) => <tr key={r.id} className="border-t border-border hover:bg-slate-800/60"><td className="py-2">{r.student}</td><td>{r.className}</td><td>{r.date}</td><td>{r.reason}</td><td><Badge tone={r.status === 'Approved' ? 'success' : 'warning'}>{r.status}</Badge></td><td>{r.notified ? 'Yes' : 'No'}</td><td>View</td></tr>)}
              </tbody></table>
            </CardBody>
          </Card>
        ) : null}

        {tab === 'Unexcused Absences' ? (
          <Card>
            <CardHeader title="Unexcused Absences" right={<Button variant="warning" onClick={() => pushToast('Bulk notifications queued', 'warning')}>Bulk Notify All</Button>} />
            <CardBody>
              <table className="w-full text-sm"><thead className="text-left text-muted"><tr><th>Student</th><th>Class</th><th>Date</th><th>Notified</th><th>Action</th></tr></thead><tbody>
                {unexcused.map((s) => <tr key={s.id} className="border-t border-border hover:bg-slate-800/60"><td className="py-2">{s.name}</td><td>{s.className}</td><td>2026-03-26</td><td>No</td><td><Button variant="outline" className="text-xs" onClick={() => pushToast('Notification sent', 'success')}>Notify Now</Button></td></tr>)}
              </tbody></table>
            </CardBody>
          </Card>
        ) : null}

        <Modal isOpen={Boolean(approval)} onClose={() => setApproval(null)} title="Approve Leave">
          {approval ? (
            <div className="space-y-3 text-sm">
              <p>Send WhatsApp notification to parent?</p>
              <div className="p-3 rounded-lg bg-slate-900 border border-border">Dear Mr. Kumar, Your son Naveen Kumar (Class 12-A) leave has been approved for 27-Mar-2026. Reason: Fever.</div>
              <div className="flex gap-2"><Button onClick={() => { setApproval(null); pushToast('Leave approved and notification sent', 'success'); }}>Confirm Send</Button><Button variant="outline" onClick={() => { setApproval(null); pushToast('Leave approved', 'success'); }}>Send Later</Button></div>
            </div>
          ) : null}
        </Modal>

        <Modal isOpen={Boolean(rejecting)} onClose={() => setRejecting(null)} title="Reject Leave">
          <div className="space-y-3">
            <TextArea placeholder="Reason for rejection" rows={4} />
            <Button variant="danger" onClick={() => { setRejecting(null); pushToast('Rejected and parent notified', 'error'); }}>Reject + Notify</Button>
          </div>
        </Modal>
      </PageContainer>
    </AppShell>
  );
};
