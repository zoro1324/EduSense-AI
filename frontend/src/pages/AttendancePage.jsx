import React, { useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { ChartCard } from '../components/common/Card';
import { StatusBadge } from '../components/common/Badge';
import { IconSearch, IconCalendar } from '../components/common/Icons';
import { mockAttendanceData } from '../data/mockData';

export const AttendancePage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDate, setSelectedDate] = useState('');
  const [filteredData, setFilteredData] = useState(mockAttendanceData);

  const handleSearch = (value) => {
    setSearchTerm(value);
    filterData(value, selectedDate);
  };

  const handleDateFilter = (value) => {
    setSelectedDate(value);
    filterData(searchTerm, value);
  };

  const filterData = (search, date) => {
    let data = mockAttendanceData;

    if (search) {
      data = data.filter(
        (item) =>
          item.studentName.toLowerCase().includes(search.toLowerCase()) ||
          item.studentId.toLowerCase().includes(search.toLowerCase())
      );
    }

    if (date) {
      // In real app, filter by date
      // For now, just keep all records
    }

    setFilteredData(data);
  };

  const stats = {
    total: mockAttendanceData.length,
    present: mockAttendanceData.filter((d) => d.status === 'Present').length,
    absent: mockAttendanceData.filter((d) => d.status === 'Absent').length,
    late: mockAttendanceData.filter((d) => d.status === 'Late').length,
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Attendance Monitoring</h2>
          <p className="text-gray-600 mt-1">Real-time attendance captured from ESP32-CAM system</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg border border-blue-200 p-4 shadow-card">
            <p className="text-gray-600 text-sm">Total Students</p>
            <p className="text-2xl font-bold text-blue-600 mt-2">{stats.total}</p>
          </div>
          <div className="bg-white rounded-lg border border-green-200 p-4 shadow-card">
            <p className="text-gray-600 text-sm">Present</p>
            <p className="text-2xl font-bold text-green-600 mt-2">{stats.present}</p>
          </div>
          <div className="bg-white rounded-lg border border-red-200 p-4 shadow-card">
            <p className="text-gray-600 text-sm">Absent</p>
            <p className="text-2xl font-bold text-red-600 mt-2">{stats.absent}</p>
          </div>
          <div className="bg-white rounded-lg border border-yellow-200 p-4 shadow-card">
            <p className="text-gray-600 text-sm">Late</p>
            <p className="text-2xl font-bold text-yellow-600 mt-2">{stats.late}</p>
          </div>
        </div>

        {/* Filters */}
        <ChartCard title="Attendance Records" className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {/* Search Bar */}
            <div className="relative">
              <IconSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or ID..."
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition"
              />
            </div>

            {/* Date Filter */}
            <div className="relative">
              <IconCalendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => handleDateFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition"
              />
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Student Name</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Student ID</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Status</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Entry Time</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-700">Face Recognition</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((record) => (
                  <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-gray-900 font-medium">{record.studentName}</td>
                    <td className="px-4 py-3 text-gray-600 font-mono text-xs">{record.studentId}</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={record.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-600">{record.entryTime}</td>
                    <td className="px-4 py-3">
                      <StatusBadge status={record.faceRecognitionStatus} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {filteredData.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <p>No attendance records found matching your criteria.</p>
              </div>
            )}
          </div>

          {/* Table Footer */}
          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <p>Showing {filteredData.length} of {mockAttendanceData.length} records</p>
            <div className="flex gap-2">
              <button className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                ← Previous
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                Next →
              </button>
            </div>
          </div>
        </ChartCard>
      </div>
    </MainLayout>
  );
};
