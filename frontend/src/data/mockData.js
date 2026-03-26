// Mock data for API responses
export const mockDashboardData = {
  summaryCards: {
    totalStudentsPresent: 28,
    absentStudents: 2,
    averageEngagementScore: 72.5,
    activeParticipationCount: 15,
  },
  engagementTrend: [
    { time: '08:00', score: 65 },
    { time: '08:15', score: 68 },
    { time: '08:30', score: 72 },
    { time: '08:45', score: 70 },
    { time: '09:00', score: 75 },
    { time: '09:15', score: 78 },
    { time: '09:30', score: 76 },
    { time: '09:45', score: 80 },
  ],
  studentParticipation: [
    { name: 'Mathematics', value: 85 },
    { name: 'Science', value: 72 },
    { name: 'English', value: 68 },
    { name: 'History', value: 78 },
    { name: 'PE', value: 92 },
  ],
  attendanceDistribution: [
    { name: 'Present', value: 93, fill: '#10b981' },
    { name: 'Absent', value: 5, fill: '#ef4444' },
    { name: 'Late', value: 2, fill: '#f59e0b' },
  ],
};

export const mockAttendanceData = [
  {
    id: 1,
    studentName: 'Alice Johnson',
    studentId: 'STU001',
    status: 'Present',
    entryTime: '08:05',
    faceRecognitionStatus: 'Verified',
  },
  {
    id: 2,
    studentName: 'Bob Smith',
    studentId: 'STU002',
    status: 'Present',
    entryTime: '08:10',
    faceRecognitionStatus: 'Verified',
  },
  {
    id: 3,
    studentName: 'Charlie Davis',
    studentId: 'STU003',
    status: 'Absent',
    entryTime: '-',
    faceRecognitionStatus: 'Not Detected',
  },
  {
    id: 4,
    studentName: 'Diana Wilson',
    studentId: 'STU004',
    status: 'Present',
    entryTime: '08:15',
    faceRecognitionStatus: 'Verified',
  },
  {
    id: 5,
    studentName: 'Ethan Brown',
    studentId: 'STU005',
    status: 'Late',
    entryTime: '08:25',
    faceRecognitionStatus: 'Verified',
  },
  {
    id: 6,
    studentName: 'Fiona Garcia',
    studentId: 'STU006',
    status: 'Present',
    entryTime: '08:08',
    faceRecognitionStatus: 'Verified',
  },
];

export const mockEngagementData = {
  heatmapData: [
    { row: 'Row A', col1: 85, col2: 78, col3: 82, col4: 88, col5: 75 },
    { row: 'Row B', col1: 72, col2: 80, col3: 85, col4: 78, col5: 81 },
    { row: 'Row C', col1: 68, col2: 62, col3: 70, col4: 65, col5: 72 },
  ],
  studentEngagementScores: [
    { name: 'Alice Johnson', score: 95, status: 'High' },
    { name: 'Bob Smith', score: 87, status: 'High' },
    { name: 'Charlie Davis', score: 72, status: 'Medium' },
    { name: 'Diana Wilson', score: 65, status: 'Medium' },
    { name: 'Ethan Brown', score: 58, status: 'Low' },
    { name: 'Fiona Garcia', score: 78, status: 'High' },
  ],
  attentionPercentage: 73.5,
};

export const mockParticipationData = {
  participationList: [
    { id: 1, studentName: 'Alice Johnson', participationType: 'Hand Raise', timestamp: '09:15' },
    { id: 2, studentName: 'Bob Smith', participationType: 'Verbal Response', timestamp: '09:18' },
    { id: 3, studentName: 'Fiona Garcia', participationType: 'Hand Raise', timestamp: '09:22' },
    { id: 4, studentName: 'Diana Wilson', participationType: 'Question Asked', timestamp: '09:25' },
    { id: 5, studentName: 'Ethan Brown', participationType: 'Verbal Response', timestamp: '09:28' },
  ],
  leaderboard: [
    { rank: 1, name: 'Alice Johnson', points: 450 },
    { rank: 2, name: 'Fiona Garcia', points: 380 },
    { rank: 3, name: 'Bob Smith', points: 320 },
    { rank: 4, name: 'Diana Wilson', points: 280 },
    { rank: 5, name: 'Ethan Brown', points: 200 },
  ],
  participationTrend: [
    { time: '08:00', count: 2 },
    { time: '08:15', count: 5 },
    { time: '08:30', count: 7 },
    { time: '08:45', count: 6 },
    { time: '09:00', count: 8 },
    { time: '09:15', count: 10 },
    { time: '09:30', count: 9 },
  ],
};

export const mockAlerts = [
  {
    id: 1,
    type: 'warning',
    title: 'Low Classroom Engagement Detected',
    message: 'Engagement score has dropped below 55% in the last 5 minutes.',
    timestamp: '09:35',
  },
  {
    id: 2,
    type: 'info',
    title: 'High Participation Rate',
    message: 'Excellent participation with 65% of students actively engaged.',
    timestamp: '09:30',
  },
  {
    id: 3,
    type: 'danger',
    title: 'Student Inactivity Detected',
    message: 'Ethan Brown appears distracted for more than 10 minutes.',
    timestamp: '09:28',
  },
  {
    id: 4,
    type: 'success',
    title: 'Excellent Attendance',
    message: 'Class attendance is at 93%. Only 2 students absent.',
    timestamp: '09:15',
  },
];
