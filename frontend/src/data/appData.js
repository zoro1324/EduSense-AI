export const currentDateTime = () => new Date().toLocaleString('en-IN', {
  weekday: 'short',
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
});

export const students = [
  { id: 1, name: 'Naveen Kumar', roll: '10A01', className: '10A', attendance: 92, faceRegistered: true, dob: '2009-02-11', bloodGroup: 'O+', address: '12 Lake Road', father: 'Ramesh Kumar', mother: 'Latha R', parentPhone: '9876500011', parentEmail: 'ramesh@example.com', totalMarks: 452, rank: 3, leavesTaken: 2 },
  { id: 2, name: 'Ravi Prakash', roll: '10A02', className: '10A', attendance: 68, faceRegistered: true, dob: '2009-03-16', bloodGroup: 'B+', address: '44 Temple Street', father: 'Prakash R', mother: 'Kavitha P', parentPhone: '9876500012', parentEmail: 'prakash@example.com', totalMarks: 375, rank: 9, leavesTaken: 4 },
  { id: 3, name: 'Asha Devi', roll: '10A03', className: '10A', attendance: 88, faceRegistered: false, dob: '2009-07-02', bloodGroup: 'A+', address: '7 MG Colony', father: 'Sathish D', mother: 'Anitha D', parentPhone: '9876500013', parentEmail: 'asha.parent@example.com', totalMarks: 431, rank: 4, leavesTaken: 1 },
  { id: 4, name: 'Meena S', roll: '10A04', className: '10A', attendance: 74, faceRegistered: true, dob: '2009-10-21', bloodGroup: 'AB+', address: '101 Park Avenue', father: 'Suresh S', mother: 'Rani S', parentPhone: '9876500014', parentEmail: 'meena.parent@example.com', totalMarks: 342, rank: 11, leavesTaken: 6 },
  { id: 5, name: 'Harish V', roll: '10A05', className: '10A', attendance: 84, faceRegistered: true, dob: '2009-05-19', bloodGroup: 'O-', address: '17 Anna Nagar', father: 'Vinod H', mother: 'Geetha H', parentPhone: '9876500015', parentEmail: 'harish.parent@example.com', totalMarks: 398, rank: 8, leavesTaken: 2 },
  { id: 6, name: 'Sneha K', roll: '11A01', className: '11A', attendance: 95, faceRegistered: true, dob: '2008-11-13', bloodGroup: 'A-', address: '22 River View', father: 'Kiran K', mother: 'Priya K', parentPhone: '9876500016', parentEmail: 'sneha.parent@example.com', totalMarks: 468, rank: 2, leavesTaken: 1 },
  { id: 7, name: 'Arjun M', roll: '11A02', className: '11A', attendance: 86, faceRegistered: true, dob: '2008-01-28', bloodGroup: 'B-', address: '9 Lotus Lane', father: 'Murugan M', mother: 'Kala M', parentPhone: '9876500017', parentEmail: 'arjun.parent@example.com', totalMarks: 414, rank: 6, leavesTaken: 3 },
  { id: 8, name: 'Divya T', roll: '11A03', className: '11A', attendance: 72, faceRegistered: false, dob: '2008-06-15', bloodGroup: 'A+', address: '13 Market Road', father: 'Thiru T', mother: 'Selvi T', parentPhone: '9876500018', parentEmail: 'divya.parent@example.com', totalMarks: 355, rank: 10, leavesTaken: 5 },
  { id: 9, name: 'Karthik R', roll: '11A04', className: '11A', attendance: 90, faceRegistered: true, dob: '2008-08-08', bloodGroup: 'B+', address: '55 New Street', father: 'Raghu R', mother: 'Uma R', parentPhone: '9876500019', parentEmail: 'karthik.parent@example.com', totalMarks: 422, rank: 5, leavesTaken: 2 },
  { id: 10, name: 'Priya N', roll: '11A05', className: '11A', attendance: 77, faceRegistered: true, dob: '2008-12-03', bloodGroup: 'O+', address: '81 South End', father: 'Nagaraj N', mother: 'Lakshmi N', parentPhone: '9876500020', parentEmail: 'priya.parent@example.com', totalMarks: 386, rank: 7, leavesTaken: 3 },
  { id: 11, name: 'Vikram J', roll: '12A01', className: '12A', attendance: 98, faceRegistered: true, dob: '2007-02-17', bloodGroup: 'AB-', address: '4 School Road', father: 'Jagan J', mother: 'Nila J', parentPhone: '9876500021', parentEmail: 'vikram.parent@example.com', totalMarks: 479, rank: 1, leavesTaken: 0 },
  { id: 12, name: 'Farhan Ali', roll: '12A02', className: '12A', attendance: 83, faceRegistered: true, dob: '2007-04-05', bloodGroup: 'A+', address: '19 North Street', father: 'Ali F', mother: 'Sabiha F', parentPhone: '9876500022', parentEmail: 'farhan.parent@example.com', totalMarks: 401, rank: 8, leavesTaken: 2 },
  { id: 13, name: 'Lakshmi P', roll: '12A03', className: '12A', attendance: 70, faceRegistered: true, dob: '2007-09-12', bloodGroup: 'O+', address: '43 East Cross', father: 'Prabhu P', mother: 'Jaya P', parentPhone: '9876500023', parentEmail: 'lakshmi.parent@example.com', totalMarks: 340, rank: 12, leavesTaken: 6 },
  { id: 14, name: 'Yusuf Khan', roll: '12A04', className: '12A', attendance: 79, faceRegistered: false, dob: '2007-10-30', bloodGroup: 'B+', address: '66 Central Ave', father: 'Khan Y', mother: 'Razia Y', parentPhone: '9876500024', parentEmail: 'yusuf.parent@example.com', totalMarks: 368, rank: 10, leavesTaken: 4 },
  { id: 15, name: 'Shalini G', roll: '12A05', className: '12A', attendance: 87, faceRegistered: true, dob: '2007-01-09', bloodGroup: 'A-', address: '29 College Road', father: 'Gopi G', mother: 'Viji G', parentPhone: '9876500025', parentEmail: 'shalini.parent@example.com', totalMarks: 429, rank: 4, leavesTaken: 2 },
];

export const attendanceLast7Days = [
  { date: '2026-03-20', present: 26, absent: 4, unknown: 1 },
  { date: '2026-03-21', present: 27, absent: 3, unknown: 0 },
  { date: '2026-03-22', present: 24, absent: 6, unknown: 0 },
  { date: '2026-03-23', present: 28, absent: 2, unknown: 1 },
  { date: '2026-03-24', present: 29, absent: 1, unknown: 0 },
  { date: '2026-03-25', present: 25, absent: 5, unknown: 1 },
  { date: '2026-03-26', present: 28, absent: 2, unknown: 1 },
];

export const periodEngagementToday = [
  { period: 'Period 1', today: 84, yesterday: 78 },
  { period: 'Period 2', today: 82, yesterday: 76 },
  { period: 'Period 3', today: 71, yesterday: 69 },
  { period: 'Period 4', today: 68, yesterday: 74 },
  { period: 'Period 5', today: 34, yesterday: 57 },
  { period: 'Period 6', today: 61, yesterday: 65 },
];

export const safetyAlerts = [
  { id: 1, level: 'Alert', location: 'Block A', timestamp: '09:12 AM', status: 'Unresolved', snapshot: 'Snapshot-001' },
  { id: 2, level: 'Warning', location: 'Corridor', timestamp: '10:03 AM', status: 'Resolved', snapshot: 'Snapshot-002' },
  { id: 3, level: 'Normal', location: 'Canteen', timestamp: '10:20 AM', status: 'Resolved', snapshot: 'Snapshot-003' },
  { id: 4, level: 'Warning', location: 'Block B', timestamp: '11:10 AM', status: 'Resolved', snapshot: 'Snapshot-004' },
  { id: 5, level: 'Alert', location: 'Corridor', timestamp: '12:05 PM', status: 'Unresolved', snapshot: 'Snapshot-005' },
  { id: 6, level: 'Normal', location: 'Block A', timestamp: '01:17 PM', status: 'Resolved', snapshot: 'Snapshot-006' },
  { id: 7, level: 'Warning', location: 'Canteen', timestamp: '02:01 PM', status: 'Resolved', snapshot: 'Snapshot-007' },
];

export const notificationsLog = [
  { id: 1, type: 'Absent', student: 'Ravi Prakash', parent: 'Prakash R', channel: 'WhatsApp', time: '09:45 AM', status: 'Delivered' },
  { id: 2, type: 'Leave', student: 'Meena S', parent: 'Suresh S', channel: 'SMS', time: '10:10 AM', status: 'Failed' },
  { id: 3, type: 'Result', student: 'Naveen Kumar', parent: 'Ramesh Kumar', channel: 'WhatsApp', time: '11:30 AM', status: 'Pending' },
  { id: 4, type: 'Safety', student: '—', parent: 'Admin', channel: 'SMS', time: '12:04 PM', status: 'Delivered' },
  { id: 5, type: 'Leave', student: 'Lakshmi P', parent: 'Prabhu P', channel: 'WhatsApp', time: '01:08 PM', status: 'Delivered' },
];

export const leaveRequests = [
  { id: 1, student: 'Naveen Kumar', className: '12A', date: '2026-03-27', reason: 'Fever', appliedOn: '2026-03-26', status: 'Pending', notified: false },
  { id: 2, student: 'Ravi Prakash', className: '10A', date: '2026-03-27', reason: 'Family event', appliedOn: '2026-03-25', status: 'Pending', notified: false },
  { id: 3, student: 'Divya T', className: '11A', date: '2026-03-28', reason: 'Doctor appointment', appliedOn: '2026-03-26', status: 'Approved', notified: true },
];

export const quarterlyMarks = students.map((s) => {
  const tamil = Math.floor(55 + Math.random() * 40);
  const english = Math.floor(55 + Math.random() * 40);
  const maths = Math.floor(55 + Math.random() * 40);
  const science = Math.floor(55 + Math.random() * 40);
  const social = Math.floor(55 + Math.random() * 40);
  return {
    id: s.id,
    student: s.name,
    className: s.className,
    exam: 'Quarterly',
    tamil,
    english,
    maths,
    science,
    social,
  };
});

export const messageTemplates = {
  absent: 'Dear {parent_name}, {student_name} from {class} is absent on {date}.',
  leaveApproved: 'Dear {parent_name}, leave for {student_name} on {date} has been approved.',
  leaveRejected: 'Dear {parent_name}, leave for {student_name} on {date} has been rejected.',
  result: 'Dear {parent_name}, result report for {student_name}: {marks}.',
  weeklySummary: 'Weekly attendance summary for {student_name} ({class}) is ready.',
  safety: 'Safety alert for {student_name} on {date}. Please contact school admin.',
};

export const reportHeatmap = [
  { period: 'P1', Mon: 78, Tue: 72, Wed: 80, Thu: 76, Fri: 74 },
  { period: 'P2', Mon: 82, Tue: 79, Wed: 85, Thu: 81, Fri: 83 },
  { period: 'P3', Mon: 68, Tue: 71, Wed: 66, Thu: 70, Fri: 69 },
  { period: 'P4', Mon: 74, Tue: 73, Wed: 77, Thu: 72, Fri: 75 },
  { period: 'P5', Mon: 35, Tue: 41, Wed: 38, Thu: 34, Fri: 39 },
  { period: 'P6', Mon: 63, Tue: 66, Wed: 64, Thu: 62, Fri: 65 },
];

export const attendanceRows = students.map((s) => ({
  ...s,
  p1: Math.random() > 0.2,
  p2: Math.random() > 0.2,
  p3: Math.random() > 0.2,
  p4: Math.random() > 0.2,
  p5: Math.random() > 0.2,
  p6: Math.random() > 0.2,
}));
