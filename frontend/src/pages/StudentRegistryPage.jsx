import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { Badge, Button, Card, CardBody, CardHeader, Input, PageContainer, PageTitle, Select, TextArea } from '../components/ui/UIPrimitives';
import { Modal } from '../components/ui/Modal';
import { TableWrapper } from '../components/ui/Table';
import { useToast } from '../components/ui/ToastContext';
import { ImageUpload } from '../components/ui/ImageUpload';
import { api } from '../lib/api';

export const StudentRegistryPage = () => {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [classFilter, setClassFilter] = useState('All');
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [progress, setProgress] = useState('');
  const [photoFile, setPhotoFile] = useState(null);
  const [newStudent, setNewStudent] = useState({
    name: '',
    roll_number: '',
    class_name: '10A',
    date_of_birth: '',
    blood_group: 'O+',
    address: '',
    parent: {
      father_name: '',
      mother_name: '',
      whatsapp_number: '',
      phone_number: '',
      email: '',
    },
  });
  const { pushToast } = useToast();

  const loadStudents = async () => {
    try {
      const data = await api.get('/students/');
      setStudents(Array.isArray(data) ? data : []);
    } catch (error) {
      pushToast(error.message || 'Failed to load students', 'error');
    }
  };

  useEffect(() => {
    loadStudents();
  }, []);

  const filtered = useMemo(
    () =>
      students.filter(
        (s) =>
          (classFilter === 'All' || s.class_name === classFilter) &&
          (s.name.toLowerCase().includes(search.toLowerCase()) || s.roll_number.toLowerCase().includes(search.toLowerCase()))
      ),
    [students, classFilter, search]
  );

  const registerFace = async (studentId, imageFile = null) => {
    if (!studentId) {
      pushToast('Please select a student first', 'warning');
      return;
    }

    setProgress(imageFile ? 'Detecting face...' : 'Using saved student photo...');
    try {
      let payload = {};
      if (imageFile) {
        const formData = new FormData();
        formData.append('face_image', imageFile);
        payload = formData;
      }

      setTimeout(() => setProgress('Generating embeddings...'), 500);
      await api.post(`/students/${studentId}/register-face/`, payload);
      setProgress('✅ Registered');
      pushToast('Face registered successfully', 'success');
      loadStudents();
    } catch (error) {
      setProgress('❌ Registration failed');
      pushToast(error.message || 'Face registration failed', 'error');
    }
  };

  const saveStudent = async () => {
    try {
      setSaving(true);
      
      // Create FormData to handle file upload
      const formData = new FormData();
      
      // Add text fields
      formData.append('name', newStudent.name);
      formData.append('roll_number', newStudent.roll_number);
      formData.append('class_name', newStudent.class_name);
      formData.append('date_of_birth', newStudent.date_of_birth);
      formData.append('blood_group', newStudent.blood_group);
      formData.append('address', newStudent.address);
      
      // Add parent data
      formData.append('parent.father_name', newStudent.parent.father_name);
      formData.append('parent.mother_name', newStudent.parent.mother_name);
      formData.append('parent.whatsapp_number', newStudent.parent.whatsapp_number);
      formData.append('parent.phone_number', newStudent.parent.phone_number);
      formData.append('parent.email', newStudent.parent.email);
      
      // Add photo if selected
      if (photoFile) {
        formData.append('photo', photoFile);
      }
      
      await api.post('/students/', formData);
      pushToast('Student saved successfully', 'success');
      setOpen(false);
      setPhotoFile(null);
      setNewStudent({
        name: '',
        roll_number: '',
        class_name: '10A',
        date_of_birth: '',
        blood_group: 'O+',
        address: '',
        parent: {
          father_name: '',
          mother_name: '',
          whatsapp_number: '',
          phone_number: '',
          email: '',
        },
      });
      loadStudents();
    } catch (error) {
      pushToast(error.message || 'Failed to save student', 'error');
    } finally {
      setSaving(false);
    }
  };

  const deleteStudent = async (studentId) => {
    try {
      await api.delete(`/students/${studentId}/`);
      pushToast('Student deactivated', 'warning');
      loadStudents();
    } catch (error) {
      pushToast(error.message || 'Failed to delete student', 'error');
    }
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
                <tr key={s.student_id} className="border-b border-border hover:bg-slate-800/60">
                  <td className="px-3 py-2">
                    <div className="w-8 h-8 rounded-full bg-primary/30 grid place-items-center text-xs overflow-hidden">
                      {s.photo ? (
                        <img src={s.photo} alt={s.name} className="w-full h-full object-cover" />
                      ) : (
                        s.name.split(' ').map((x) => x[0]).join('').slice(0, 2)
                      )}
                    </div>
                  </td>
                  <td className="px-3 py-2">{s.name}</td>
                  <td className="px-3 py-2">{s.roll_number}</td>
                  <td className="px-3 py-2">{s.class_name}</td>
                  <td className="px-3 py-2">N/A</td>
                  <td className="px-3 py-2">{s.face_registered ? <Badge tone="success">Registered ✅</Badge> : <Badge tone="warning">Not Registered ⚠️</Badge>}</td>
                  <td className="px-3 py-2 flex gap-1">
                    <Link to={`/students/${s.student_id}`} className="px-2 py-1 text-xs rounded bg-slate-700">View Profile</Link>
                    <button className="px-2 py-1 text-xs rounded bg-slate-700" onClick={() => registerFace(s.student_id)}>Register Face</button>
                    <button className="px-2 py-1 text-xs rounded bg-red-500/30" onClick={() => deleteStudent(s.student_id)}>Delete</button>
                  </td>
                </tr>
              )}
            />
          </CardBody>
        </Card>

        <Modal isOpen={open} onClose={() => { setOpen(false); setPhotoFile(null); }} title="Register New Student" width="max-w-2xl">
          <div className="grid md:grid-cols-2 gap-3">
            <Input placeholder="Full Name" value={newStudent.name} onChange={(e) => setNewStudent((prev) => ({ ...prev, name: e.target.value }))} />
            <Input placeholder="Roll Number" value={newStudent.roll_number} onChange={(e) => setNewStudent((prev) => ({ ...prev, roll_number: e.target.value }))} />
            <Select value={newStudent.class_name} onChange={(e) => setNewStudent((prev) => ({ ...prev, class_name: e.target.value }))}><option>10A</option><option>11A</option><option>12A</option></Select>
            <Input type="date" value={newStudent.date_of_birth} onChange={(e) => setNewStudent((prev) => ({ ...prev, date_of_birth: e.target.value }))} />
            <Select value={newStudent.blood_group} onChange={(e) => setNewStudent((prev) => ({ ...prev, blood_group: e.target.value }))}><option>O+</option><option>A+</option><option>B+</option><option>AB+</option></Select>
            <TextArea placeholder="Address" className="md:col-span-2" rows={2} value={newStudent.address} onChange={(e) => setNewStudent((prev) => ({ ...prev, address: e.target.value }))} />
            <Input placeholder="Father Name" value={newStudent.parent.father_name} onChange={(e) => setNewStudent((prev) => ({ ...prev, parent: { ...prev.parent, father_name: e.target.value } }))} />
            <Input placeholder="Mother Name" value={newStudent.parent.mother_name} onChange={(e) => setNewStudent((prev) => ({ ...prev, parent: { ...prev.parent, mother_name: e.target.value } }))} />
            <Input placeholder="WhatsApp Number" value={newStudent.parent.whatsapp_number} onChange={(e) => setNewStudent((prev) => ({ ...prev, parent: { ...prev.parent, whatsapp_number: e.target.value, phone_number: e.target.value } }))} />
            <Input placeholder="Email" type="email" value={newStudent.parent.email} onChange={(e) => setNewStudent((prev) => ({ ...prev, parent: { ...prev.parent, email: e.target.value } }))} />
            <div className="md:col-span-2">
              <ImageUpload onImageSelect={setPhotoFile} />
            </div>
            <div className="md:col-span-2 flex gap-2">
              <Button onClick={() => registerFace(filtered[0]?.student_id)} disabled={!filtered[0]}>Register Face</Button>
              {progress ? <div className="text-sm text-muted self-center">{progress}</div> : null}
            </div>
            <Button variant="success" className="md:col-span-2" loading={saving} onClick={saveStudent}>Save Student</Button>
          </div>
        </Modal>
      </PageContainer>
    </AppShell>
  );
};
