import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { students } from '../data/appData';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { Modal } from '../components/ui/Modal';
import { TableWrapper } from '../components/ui/Table';
import { useToast } from '../components/ui/ToastContext';

export const StudentRegistryPage = () => {
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('All');
  const [open, setOpen] = useState(false);
  const [progress, setProgress] = useState('');
  const { pushToast } = useToast();

  const filtered = useMemo(() => students.filter((s) => (classFilter === 'All' || s.className === classFilter) && (s.name.toLowerCase().includes(search.toLowerCase()) || s.roll.toLowerCase().includes(search.toLowerCase()))), [classFilter, search]);

  const registerFace = () => {
    setProgress('Detecting face...');
    setTimeout(() => setProgress('Generating embeddings...'), 700);
    setTimeout(() => setProgress('✅ Registered'), 1400);
  };

  return (
    <AppShell>
      <PageContainer>
        <div className="flex flex-wrap gap-2 justify-between items-center">
          <PageTitle title="Student Registry" subtitle="Manage student identity, profile and face registration." />
          <Badge tone="primary">Total: {students.length}</Badge>
        </div>
        <Card>
          <CardBody className="grid grid-cols-1 md:grid-cols-4 gap-2">
            <Input placeholder="Search student" value={search} onChange={(e) => setSearch(e.target.value)} />
            <Select value={classFilter} onChange={(e) => setClassFilter(e.target.value)}><option>All</option><option>10A</option><option>11A</option><option>12A</option></Select>
            <div />
            <Button onClick={() => setOpen(true)}>Add New Student</Button>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Students" />
          <CardBody className="p-0">
            <TableWrapper
              columns={['Photo', 'Name', 'Roll No', 'Class', 'Attendance %', 'Face Status', 'Actions']}
              rows={filtered}
              renderRow={(s) => (
                <tr key={s.id} className="border-b border-border hover:bg-slate-800/60">
                  <td className="px-3 py-2"><div className="w-8 h-8 rounded-full bg-primary/30 grid place-items-center text-xs">{s.name.split(' ').map((x) => x[0]).join('').slice(0,2)}</div></td>
                  <td className="px-3 py-2">{s.name}</td>
                  <td className="px-3 py-2">{s.roll}</td>
                  <td className="px-3 py-2">{s.className}</td>
                  <td className="px-3 py-2">{s.attendance}%</td>
                  <td className="px-3 py-2">{s.faceRegistered ? <Badge tone="success">Registered ✅</Badge> : <Badge tone="warning">Not Registered ⚠️</Badge>}</td>
                  <td className="px-3 py-2 flex gap-1">
                    <Link to={`/students/${s.id}`} className="px-2 py-1 text-xs rounded bg-slate-700">View Profile</Link>
                    <button className="px-2 py-1 text-xs rounded bg-slate-700">Edit</button>
                    <button className="px-2 py-1 text-xs rounded bg-red-500/30">Delete</button>
                  </td>
                </tr>
              )}
            />
          </CardBody>
        </Card>

        <Modal isOpen={open} onClose={() => setOpen(false)} title="Register New Student" width="max-w-2xl">
          <div className="grid md:grid-cols-2 gap-3">
            <Input placeholder="Full Name" />
            <Input placeholder="Roll Number" />
            <Select><option>10A</option><option>11A</option><option>12A</option></Select>
            <Input type="date" />
            <Select><option>O+</option><option>A+</option><option>B+</option><option>AB+</option></Select>
            <TextArea placeholder="Address" className="md:col-span-2" rows={2} />
            <Input placeholder="Father Name" />
            <Input placeholder="Mother Name" />
            <Input placeholder="WhatsApp Number" />
            <Input placeholder="Email" type="email" />
            <div className="md:col-span-2 p-3 rounded-lg border border-dashed border-border text-center bg-slate-900">Drag and drop image upload area</div>
            <div className="md:col-span-2 flex gap-2">
              <Button onClick={registerFace}>Register Face</Button>
              {progress ? <div className="text-sm text-muted self-center">{progress}</div> : null}
            </div>
            <Button variant="success" className="md:col-span-2" onClick={() => { setOpen(false); pushToast('Student saved successfully', 'success'); }}>Save Student</Button>
          </div>
        </Modal>
      </PageContainer>
    </AppShell>
  );
};
