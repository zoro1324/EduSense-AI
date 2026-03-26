import React, { useMemo } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { periodEngagementToday } from '../data/appData';
import { Badge, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { BarChart, Bar, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export const EngagementMonitorPage = () => {
  const current = 22;
  const engaged = 19;
  const distracted = 9;
  const status = current >= 70 ? 'High' : current >= 40 ? 'Medium' : 'Low';
  const barData = periodEngagementToday.map((x) => ({ ...x, color: x.today >= 75 ? '#22c55e' : x.today >= 50 ? '#eab308' : '#ef4444' }));

  const statusTone = useMemo(() => (status === 'High' ? 'success' : status === 'Medium' ? 'warning' : 'danger'), [status]);

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Engagement Monitor" subtitle="Live class engagement and distraction trends." />
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
          <div className="xl:col-span-7">
            <Card>
              <CardBody>
                <div className="relative aspect-video border border-border rounded-xl bg-slate-700/40 grid place-items-center text-muted">
                  <div className="text-center">
                    <div className="text-5xl">📈</div>
                    <p>Classroom Feed</p>
                  </div>
                  <div className="absolute top-3 left-3 right-3 p-2 bg-slate-900/85 border border-border rounded-lg text-xs">
                    Engaged: {engaged} | Distracted: {distracted} | Total: {engaged + distracted}
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
          <div className="xl:col-span-5 space-y-4">
            <Card>
              <CardHeader title="Current Engagement" />
              <CardBody className="space-y-3">
                <div className="text-5xl font-semibold">{current}%</div>
                <Badge tone={statusTone}>{status}</Badge>
                <div className="text-sm text-muted">Engaged: {engaged}</div>
                <div className="text-sm text-muted">Distracted: {distracted}</div>
                <div className="text-xs text-muted">Last updated: 09:31 AM</div>
              </CardBody>
            </Card>
            {current < 30 ? (
              <Card>
                <CardBody>
                  <div className="p-3 rounded-lg bg-yellow-500/20 border border-yellow-500/40 text-yellow-100 text-sm">
                    ⚠️ Engagement critically low — 22% for 4 minutes
                  </div>
                </CardBody>
              </Card>
            ) : null}
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          <Card>
            <CardHeader title="Period Wise Engagement Today" />
            <CardBody>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={barData}>
                  <XAxis dataKey="period" stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} stroke="#94a3b8" />
                  <Tooltip />
                  <Bar dataKey="today">
                    {barData.map((e) => <Cell key={e.period} fill={e.color} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
          <Card>
            <CardHeader title="Today vs Yesterday" />
            <CardBody>
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={periodEngagementToday}>
                  <XAxis dataKey="period" stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} stroke="#94a3b8" />
                  <Tooltip />
                  <Line dataKey="today" stroke="#6366f1" strokeWidth={2} />
                  <Line dataKey="yesterday" stroke="#9ca3af" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardBody>
          </Card>
        </div>
      </PageContainer>
    </AppShell>
  );
};
