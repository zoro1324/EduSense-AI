import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Card, CardBody, CardHeader, PageContainer, PageTitle } from '../components/ui/UIPrimitives';
import { BarChart, Bar, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export const EngagementMonitorPage = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.get('/engagement/today/');
        setLogs(Array.isArray(data) ? data : []);
      } catch (error) {
        setLogs([]);
      }
    };
    load();
  }, []);

  const current = logs.length ? Math.round(logs[logs.length - 1].engagement_percent || 0) : 0;
  const engaged = logs.length ? logs[logs.length - 1].engaged_count || 0 : 0;
  const distracted = logs.length ? logs[logs.length - 1].distracted_count || 0 : 0;
  const status = current >= 70 ? 'High' : current >= 40 ? 'Medium' : 'Low';
  const periodEngagementToday = useMemo(() => {
    const map = new Map();
    logs.forEach((x) => {
      const key = `Period ${x.period}`;
      if (!map.has(key)) {
        map.set(key, []);
      }
      map.get(key).push(Number(x.engagement_percent || 0));
    });
    return Array.from(map.entries()).map(([period, values]) => {
      const today = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
      return { period, today, yesterday: today };
    });
  }, [logs]);
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
