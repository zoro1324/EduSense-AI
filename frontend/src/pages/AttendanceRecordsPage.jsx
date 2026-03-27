import React, { useEffect, useMemo, useState } from 'react';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select } from '../components/ui/UIPrimitives';
import { TableWrapper } from '../components/ui/Table';
import { api } from '../lib/api';

const pct = (row) => {
  const present = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6'].filter((k) => row[k]).length;
  return Math.round((present / 6) * 100);
};

export const AttendanceRecordsPage = () => {
  const [records, setRecords] = useState([]);
  const [query, setQuery] = useState('');
  const [className, setClassName] = useState('All');
  const [period, setPeriod] = useState('All');
  const [page, setPage] = useState(1);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await api.get('/attendance/');
        setRecords(Array.isArray(data) ? data : []);
      } catch (error) {
        setRecords([]);
      }
    };
    load();
  }, []);

  const attendanceRows = useMemo(() => {
    const grouped = new Map();
    records.forEach((row) => {
      const key = `${row.student}-${row.date}`;
      if (!grouped.has(key)) {
        grouped.set(key, {
          id: key,
          studentId: row.student,
          name: row.student_name,
          roll: String(row.student),
          className: 'N/A',
          p1: false,
          p2: false,
          p3: false,
          p4: false,
          p5: false,
          p6: false,
        });
      }
      const item = grouped.get(key);
      item[`p${row.period}`] = row.status === 'present';
    });
    return Array.from(grouped.values());
  }, [records]);

  const filtered = useMemo(() => {
    return attendanceRows.filter((r) => {
      const byQ = r.name.toLowerCase().includes(query.toLowerCase()) || r.roll.toLowerCase().includes(query.toLowerCase());
      const byClass = className === 'All' || r.className === className;
      const byPeriod = period === 'All' || r[`p${period}`] !== undefined;
      return byQ && byClass && byPeriod;
    });
  }, [attendanceRows, query, className, period]);

  const start = (page - 1) * 10;
  const rows = filtered.slice(start, start + 10);
  const pages = Math.max(1, Math.ceil(filtered.length / 10));

  return (
    <AppShell>
      <PageContainer>
        <PageTitle title="Attendance Records" subtitle="Filter, inspect and export attendance by class and period." />
        <Card>
          <CardBody className="grid grid-cols-1 md:grid-cols-6 gap-2">
            <Input type="date" />
            <Input type="date" />
            <Select value={className} onChange={(e) => setClassName(e.target.value)}><option>All</option><option>10A</option><option>11A</option><option>12A</option></Select>
            <Select value={period} onChange={(e) => setPeriod(e.target.value)}><option>All</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5</option><option value="6">6</option></Select>
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search" />
            <div className="flex gap-2"><Button variant="outline" className="flex-1">Export CSV</Button><Button variant="outline" className="flex-1">Export PDF</Button></div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Attendance Table" />
          <CardBody className="p-0">
            <TableWrapper
              columns={['Photo', 'Name', 'Roll', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'Total %']}
              rows={rows}
              renderRow={(row) => {
                const total = pct(row);
                const tone = total < 75 ? 'bg-red-500/10' : total <= 85 ? 'bg-yellow-500/10' : 'bg-green-500/10';
                const mark = (ok) => <span className={ok ? 'text-green-400' : 'text-red-400'}>{ok ? '✅' : '❌'}</span>;
                return (
                  <tr key={row.id} className={`border-b border-border hover:bg-slate-800/70 ${tone}`}>
                    <td className="px-3 py-2"><div className="w-8 h-8 rounded-full bg-primary/30 grid place-items-center text-xs">{row.name.split(' ').map((x) => x[0]).join('').slice(0,2)}</div></td>
                    <td className="px-3 py-2">{row.name}</td>
                    <td className="px-3 py-2">{row.roll}</td>
                    <td className="px-3 py-2">{mark(row.p1)}</td>
                    <td className="px-3 py-2">{mark(row.p2)}</td>
                    <td className="px-3 py-2">{mark(row.p3)}</td>
                    <td className="px-3 py-2">{mark(row.p4)}</td>
                    <td className="px-3 py-2">{mark(row.p5)}</td>
                    <td className="px-3 py-2">{mark(row.p6)}</td>
                    <td className="px-3 py-2"><Badge tone={total < 75 ? 'danger' : total <= 85 ? 'warning' : 'success'}>{total}%</Badge></td>
                  </tr>
                );
              }}
            />
          </CardBody>
          <div className="p-3 border-t border-border flex justify-end gap-2 text-sm">
            <Button variant="outline" disabled={page === 1} onClick={() => setPage((p) => p - 1)}>Prev</Button>
            <span className="px-2 py-2">{page}/{pages}</span>
            <Button variant="outline" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>Next</Button>
          </div>
        </Card>
      </PageContainer>
    </AppShell>
  );
};
