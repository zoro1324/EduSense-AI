import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Card, CardBody, CardHeader, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { BarChart, Bar, Cell, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { useAuth } from '../context/AuthContext';
import { api } from '../lib/api';

export const EngagementMonitorPage = () => {
  const { managedClasses, isPrincipal } = useAuth();
  const [logs, setLogs] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [selectedClass, setSelectedClass] = useState('');

  const availableClasses = useMemo(() => {
    if (isPrincipal) {
      const fromLogs = Array.from(new Set(logs.map((item) => item.class_name).filter(Boolean))).sort();
      return fromLogs;
    }
    return managedClasses;
  }, [isPrincipal, logs, managedClasses]);

  useEffect(() => {
    if (isPrincipal) {
      return;
    }
    if (!selectedClass && managedClasses.length > 0) {
      setSelectedClass(managedClasses[0]);
    }
    if (selectedClass && !managedClasses.includes(selectedClass) && managedClasses.length > 0) {
      setSelectedClass(managedClasses[0]);
    }
  }, [isPrincipal, managedClasses, selectedClass]);

  useEffect(() => {
    const load = async () => {
      if (!isPrincipal && managedClasses.length === 0) {
        setLogs([]);
        setLastUpdated(new Date());
        return;
      }

      try {
        const query = selectedClass ? `?class_name=${encodeURIComponent(selectedClass)}` : '';
        const data = await api.get(`/engagement/today/${query}`);
        setLogs(Array.isArray(data) ? data : []);
        setLastUpdated(new Date());
      } catch (error) {
        setLogs([]);
      }
    };

    load();

    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
  }, [isPrincipal, managedClasses, selectedClass]);

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
  const lastUpdatedLabel = lastUpdated ? lastUpdated.toLocaleTimeString() : 'Waiting for data';

  return (
    <AppShell>
      <PageContainer>
        <PageTitle
          title="Engagement Monitor"
          subtitle={isPrincipal ? 'Live class engagement and distraction trends.' : 'View engagement for classes you handle.'}
        />

        <Card>
          <CardBody className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="md:col-span-2">
              <p className="text-sm text-muted mb-1">{isPrincipal ? 'Filter by class' : 'Classes I go for'}</p>
              <Select value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)}>
                {isPrincipal ? <option value="">All Classes</option> : null}
                {availableClasses.map((className) => (
                  <option key={className} value={className}>
                    {className}
                  </option>
                ))}
              </Select>
            </div>
            <div className="flex items-end">
              <div className="text-xs text-muted">
                {selectedClass ? `Viewing: ${selectedClass}` : 'Viewing: All Classes'}
              </div>
            </div>
          </CardBody>
        </Card>

        {!isPrincipal && managedClasses.length === 0 ? (
          <Card>
            <CardBody>
              <div className="p-3 rounded-lg bg-yellow-500/20 border border-yellow-500/40 text-yellow-100 text-sm">
                No classes are assigned to you yet. Ask the principal to assign you via class in-charge or timetable faculty.
              </div>
            </CardBody>
          </Card>
        ) : null}

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
                <div className="text-xs text-muted">Last updated: {lastUpdatedLabel}</div>
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
