import React, { useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { useToast } from '../components/ui/ToastContext';

export const SettingsPage = () => {
  const tabs = ['School Details', 'User Management', 'Notification Settings', 'Camera Settings', 'AI Settings'];
  const [tab, setTab] = useState(tabs[0]);
  const { pushToast } = useToast();

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Settings" subtitle="Admin configuration for school, cameras, notifications and AI." />
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
          <Card className="xl:col-span-1">
            <CardBody className="space-y-2">
              {tabs.map((t) => <button key={t} onClick={() => setTab(t)} className={`w-full text-left px-3 py-2 rounded-lg text-sm ${tab === t ? 'bg-primary text-white' : 'bg-slate-800 text-muted'}`}>{t}</button>)}
            </CardBody>
          </Card>

          <Card className="xl:col-span-4">
            <CardHeader title={tab} />
            <CardBody className="space-y-3">
              {tab === 'School Details' ? (
                <>
                  <Input placeholder="School name" defaultValue="EduSense Higher Secondary School" />
                  <Input placeholder="Logo upload" type="file" />
                  <TextArea rows={3} placeholder="Address" defaultValue="Chennai, Tamil Nadu" />
                  <Select><option>CBSE</option><option>State</option><option>ICSE</option></Select>
                  <Input placeholder="Academic year" defaultValue="2026-2027" />
                  <Input placeholder="Classes (comma separated)" defaultValue="10A, 11A, 12A" />
                </>
              ) : null}

              {tab === 'User Management' ? (
                <>
                  <table className="w-full text-sm"><thead className="text-left text-muted"><tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead><tbody>
                    <tr className="border-t border-border"><td className="py-2">Admin</td><td>admin@edusense.ai</td><td>Admin</td><td><Badge tone="success">Active</Badge></td><td className="flex gap-2"><Button variant="outline" className="text-xs">Edit</Button><Button variant="danger" className="text-xs">Delete</Button><Button variant="warning" className="text-xs">Reset Password</Button></td></tr>
                    <tr className="border-t border-border"><td className="py-2">Class Teacher</td><td>teacher@edusense.ai</td><td>Teacher</td><td><Badge tone="success">Active</Badge></td><td className="flex gap-2"><Button variant="outline" className="text-xs">Edit</Button><Button variant="danger" className="text-xs">Delete</Button><Button variant="warning" className="text-xs">Reset Password</Button></td></tr>
                  </tbody></table>
                  <div className="grid md:grid-cols-2 gap-2 border border-border rounded-lg p-3 bg-slate-900"><Input placeholder="Name" /><Input placeholder="Email" type="email" /><Input placeholder="Password" type="password" /><Select><option>Admin</option><option>Teacher</option><option>Staff</option></Select><Button className="md:col-span-2">Add User</Button></div>
                </>
              ) : null}

              {tab === 'Notification Settings' ? (
                <>
                  <Input placeholder="Twilio Account SID" type="password" />
                  <Input placeholder="Twilio Auth Token" type="password" />
                  <Input placeholder="WhatsApp From Number" defaultValue="+919000000001" />
                  <Input placeholder="SMS From Number" defaultValue="+919000000002" />
                  <div className="grid md:grid-cols-2 gap-2 text-sm">
                    {['Absent Alert', 'Leave Approved', 'Leave Rejected', 'Result Report', 'Safety Alert', 'Weekly Summary'].map((x) => <label key={x} className="p-2 bg-slate-900 border border-border rounded-lg flex justify-between"><span>{x}</span><input type="checkbox" defaultChecked /></label>)}
                  </div>
                  <Button variant="warning" onClick={() => pushToast('Test notification sent', 'warning')}>Test Notification</Button>
                </>
              ) : null}

              {tab === 'Camera Settings' ? (
                <>
                  <Input placeholder="ESP32 CAM IP Address" defaultValue="192.168.1.50" />
                  <div className="grid md:grid-cols-3 gap-2"><Button variant="outline">Test ESP32 Connection</Button><Input placeholder="Webcam Index" defaultValue="0" /><Button variant="outline">Test Webcam</Button></div>
                  <Select><option>480p</option><option>720p</option><option>1080p</option></Select>
                  <div className="grid md:grid-cols-2 gap-2"><div className="h-28 rounded-lg border border-border bg-slate-700/40 grid place-items-center text-muted">ESP32 Preview</div><div className="h-28 rounded-lg border border-border bg-slate-700/40 grid place-items-center text-muted">Webcam Preview</div></div>
                </>
              ) : null}

              {tab === 'AI Settings' ? (
                <>
                  <Input placeholder="Groq API Key" type="password" />
                  <Select><option>llama-3.3-70b</option><option>mixtral-8x7b</option><option>gemma2-9b</option></Select>
                  <Select><option>English</option><option>Tamil</option><option>Hindi</option></Select>
                  <label className="text-sm text-muted">Face Recognition Threshold (0.6)</label>
                  <Input type="range" min="0.1" max="1" step="0.1" defaultValue="0.6" />
                  <label className="text-sm text-muted">Engagement Detection Sensitivity</label>
                  <Input type="range" min="1" max="10" defaultValue="6" />
                  <Button variant="outline">Test LLM</Button>
                </>
              ) : null}

              <Button variant="success" onClick={() => pushToast('Settings saved successfully', 'success')}>Save Settings</Button>
            </CardBody>
          </Card>
        </div>
      </PageContainer>
    </AppShell>
  );
};
