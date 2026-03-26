import React, { useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { attendanceLast7Days, students } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle } from '../components/ui/UIPrimitives';

export const LiveAttendancePage = () => {
  const [streamOn, setStreamOn] = useState(true);
  const [search, setSearch] = useState('');

  const presentCount = attendanceLast7Days[attendanceLast7Days.length - 1].present;
  const list = useMemo(() => students.filter((s) => s.name.toLowerCase().includes(search.toLowerCase()) || s.roll.toLowerCase().includes(search.toLowerCase())), [search]);

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Live Attendance" subtitle="Real-time face recognition attendance from ESP32 CAM." />
        <div className="grid grid-cols-1 xl:grid-cols-5 gap-4">
          <div className="xl:col-span-3 space-y-4">
            <Card>
              <CardBody>
                <div className="aspect-video border border-border rounded-xl bg-slate-700/40 grid place-items-center text-muted">
                  <div className="text-center">
                    <div className="text-5xl">📷</div>
                    <p>ESP32 CAM Feed</p>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="p-3 rounded-lg bg-green-500/15 border border-green-500/40 text-green-200">✅ Naveen Kumar — Marked Present — 9:02 AM</div>
                  <div className="p-3 rounded-lg bg-red-500/15 border border-red-500/40 text-red-200">❌ Unknown Face Detected — Snapshot Saved</div>
                </div>
                <div className="mt-4 flex gap-2 items-center">
                  <Button onClick={() => setStreamOn((v) => !v)}>{streamOn ? 'Stop Stream' : 'Start Stream'}</Button>
                  <Badge tone={streamOn ? 'success' : 'danger'}>{streamOn ? '● Camera Online' : '● Camera Offline'}</Badge>
                </div>
              </CardBody>
            </Card>
          </div>

          <div className="xl:col-span-2">
            <Card className="h-full">
              <CardHeader title="Today's Attendance" right={<Badge tone="primary">{presentCount}/{students.length}</Badge>} />
              <CardBody className="space-y-3">
                <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search by name or roll" />
                <div className="max-h-[420px] overflow-auto thin-scrollbar space-y-2">
                  {list.map((s) => (
                    <div key={s.id} className="p-3 rounded-lg border border-border bg-slate-900 flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="w-8 h-8 rounded-full bg-primary/30 flex items-center justify-center text-xs">{s.name.split(' ').map((x) => x[0]).join('').slice(0, 2)}</div>
                        <div className="min-w-0">
                          <p className="text-sm truncate">{s.name}</p>
                          <p className="text-xs text-muted">{s.roll} · 09:{10 + s.id} AM</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge tone={s.id % 5 === 0 ? 'danger' : 'success'}>{s.id % 5 === 0 ? 'Absent' : 'Present'}</Badge>
                        <Button variant="outline" className="px-2 py-1 text-xs">Manual</Button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="text-xs text-muted border-t border-border pt-2">Present: {presentCount} | Absent: {students.length - presentCount} | Unknown: 1</div>
              </CardBody>
            </Card>
          </div>
        </div>
      </PageContainer>
    </AppShell>
  );
};
