# EduSense AI Frontend - Project Overview

## 📋 Complete File Structure

```
EduSense-AI/
├── frontend/                              # Frontend Application Root
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Badge.jsx             # Status & Alert Badges Component
│   │   │   │   ├── Card.jsx              # Card & ChartCard Components
│   │   │   │   └── Icons.jsx             # SVG Icons Library
│   │   │   ├── layout/
│   │   │   │   ├── Header.jsx            # Top Navigation Bar with Notifications
│   │   │   │   ├── Sidebar.jsx           # Side Navigation with Menu Items
│   │   │   │   └── MainLayout.jsx        # Main Layout Wrapper Component
│   │   │   └── ProtectedRoute.jsx        # Route Protection Component
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx             # Login Page (email/password auth)
│   │   │   ├── DashboardPage.jsx         # Main Dashboard with Charts
│   │   │   ├── AttendancePage.jsx        # Attendance Tracking Table
│   │   │   ├── EngagementPage.jsx        # Engagement Analytics
│   │   │   ├── ParticipationPage.jsx     # Participation Insights
│   │   │   ├── AlertsPage.jsx            # Real-time Alerts Management
│   │   │   ├── SettingsPage.jsx          # User Settings & Preferences
│   │   │   └── NotFoundPage.jsx          # 404 Error Page
│   │   ├── context/
│   │   │   └── AuthContext.jsx           # Authentication State Management
│   │   ├── data/
│   │   │   └── mockData.js               # Mock API Response Data
│   │   ├── App.jsx                       # Main App Component & Routing
│   │   ├── main.jsx                      # React Entry Point
│   │   └── index.css                     # Global Tailwind Styles
│   ├── index.html                        # HTML Template
│   ├── package.json                      # npm Dependencies & Scripts
│   ├── vite.config.js                    # Vite Configuration
│   ├── tailwind.config.js                # Tailwind CSS Configuration
│   ├── postcss.config.js                 # PostCSS Configuration
│   ├── .gitignore                        # Git Ignore Rules
│   ├── .env.example                      # Environment Variables Template
│   ├── README.md                         # Main Documentation
│   ├── SETUP.md                          # Setup & Development Guide
│   └── PROJECT_OVERVIEW.md               # This File
```

---

## 🎯 Component Hierarchy

```
App.jsx
├── Router
├── AuthProvider
└── Routes
    ├── LoginPage (public)
    └── ProtectedRoute
        ├── DashboardPage
        │   └── MainLayout
        │       ├── Sidebar
        │       ├── Header
        │       └── Content
        │           ├── Card (x4)
        │           ├── ChartCard
        │           │   ├── LineChart
        │           │   ├── BarChart
        │           │   └── PieChart
        │           └── QuickStats
        ├── AttendancePage
        │   └── MainLayout
        │       └── AttendanceTable
        ├── EngagementPage
        │   └── MainLayout
        │       ├── AlertBanner
        │       ├── HeatmapVisualization
        │       └── StudentEngagementList
        ├── ParticipationPage
        │   └── MainLayout
        │       ├── TrendChart
        │       ├── Leaderboard
        │       └── RecentActivity
        ├── AlertsPage
        │   └── MainLayout
        │       └── AlertsList
        └── SettingsPage
            └── MainLayout
                ├── GeneralSettings
                ├── NotificationSettings
                └── ThresholdSettings
```

---

## 🔧 Key Features Implementation

### 1. Authentication System
- **File**: `src/context/AuthContext.jsx`
- **Features**: 
  - Mock login with email/password
  - User state management
  - Logout functionality
  - Session persistence ready
- **Demo Credentials**:
  - Email: `teacher@edusense.ai`
  - Password: `demo123`

### 2. Dashboard
- **File**: `src/pages/DashboardPage.jsx`
- **Components**:
  - Summary cards (4 KPIs)
  - Engagement trend chart
  - Student participation bar chart
  - Attendance distribution pie chart
  - Quick statistics cards
- **Data Source**: `mockDashboardData` from `mockData.js`

### 3. Attendance Monitoring
- **File**: `src/pages/AttendancePage.jsx`
- **Features**:
  - Real-time attendance table
  - Search by name/ID
  - Date filtering
  - Status badges (Present/Absent/Late)
  - Face recognition status
  - Pagination support

### 4. Engagement Analytics
- **File**: `src/pages/EngagementPage.jsx`
- **Features**:
  - Classroom engagement heatmap
  - Individual student scores
  - Attention percentage indicator
  - Low engagement alerts (<50%)
  - Progress visualizations
  - Color-coded engagement levels

### 5. Participation Insights
- **File**: `src/pages/ParticipationPage.jsx`
- **Features**:
  - Participation leaderboard
  - Trend graphs
  - Recent activity feed
  - Participation types (hand raise, verbal, questions)
  - Top participants ranking
  - Summary statistics

### 6. Alerts Management
- **File**: `src/pages/AlertsPage.jsx`
- **Features**:
  - Real-time alert feed
  - Alert type filtering (Critical, Warning, Success, Info)
  - Dismissible notifications
  - Action items for critical alerts
  - Alert summary counts

### 7. Settings
- **File**: `src/pages/SettingsPage.jsx`
- **Features**:
  - Email & push notifications
  - Engagement threshold slider
  - Attendance target settings
  - Participation goals
  - Theme selection
  - Application information

---

## 📊 Data Models

### Dashboard Data
```javascript
{
  summaryCards: {
    totalStudentsPresent: number,
    absentStudents: number,
    averageEngagementScore: number,
    activeParticipationCount: number
  },
  engagementTrend: [{time, score}],
  studentParticipation: [{name, value}],
  attendanceDistribution: [{name, value, fill}]
}
```

### Attendance Record
```javascript
{
  id: number,
  studentName: string,
  studentId: string,
  status: 'Present' | 'Absent' | 'Late',
  entryTime: string,
  faceRecognitionStatus: 'Verified' | 'Not Detected'
}
```

### Engagement Data
```javascript
{
  studentName: string,
  score: number (0-100),
  status: 'High' | 'Medium' | 'Low'
}
```

### Alert
```javascript
{
  id: number,
  type: 'danger' | 'warning' | 'success' | 'info',
  title: string,
  message: string,
  timestamp: string
}
```

---

## 🎨 Styling System

### Tailwind Classes Used
- **Layout**: `flex`, `grid`, `gap`, `p-*`, `m-*`
- **Colors**: `bg-{color}-{shade}`, `text-{color}-{shade}`
- **Borders**: `border`, `border-{color}`, `rounded-{size}`
- **Shadows**: `shadow-card`, `shadow-hover`, `shadow-lg`
- **Effects**: `transition`, `hover:`, `focus:`, `active:`
- **Responsive**: `md:`, `lg:`, `xl:` breakpoints

### Color Scheme
- **Primary**: Blue (#3b82f6)
- **Secondary**: Purple (#8b5cf6)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Danger**: Red (#ef4444)
- **Dark**: Gray (#1f2937)

---

## 📦 Dependencies

### Core
- **react** (18.2.0) - UI library
- **react-dom** (18.2.0) - React rendering
- **react-router-dom** (6.20.0) - Routing

### Styling
- **tailwindcss** (3.3.0) - CSS framework
- **postcss** (8.4.31) - CSS processing
- **autoprefixer** (10.4.16) - CSS vendor prefixes

### Charts & Visualization
- **recharts** (2.10.0) - Chart library

### HTTP
- **axios** (1.6.0) - API client

### Build Tools
- **vite** (5.0.0) - Build tool
- **@vitejs/plugin-react** (4.2.0) - React plugin

---

## 🚀 Getting Started (Quick Reference)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open browser to http://localhost:3000

# 5. Login with:
#    Email: teacher@edusense.ai
#    Password: demo123
```

---

## 🔌 API Endpoints (When Backend Ready)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/login` | User authentication |
| GET | `/api/dashboard` | Dashboard metrics |
| GET | `/api/attendance` | Attendance records |
| GET | `/api/engagement` | Engagement data |
| GET | `/api/participation` | Participation data |
| GET | `/api/alerts` | Alert list |
| PUT | `/api/settings` | Update user settings |

---

## 📱 Responsive Breakpoints

- **Mobile**: < 768px (single column)
- **Tablet**: 768px - 1024px (2 columns)
- **Desktop**: > 1024px (3+ columns)

---

## 🔐 Security Features

- Route protection via `ProtectedRoute` component
- Authentication context-based access control
- Mock JWT ready for real authentication
- Input validation on forms
- XSS protection via React (automatic escaping)

---

## ✨ Features Highlights

✅ Modern React with Hooks
✅ Responsive Design (Mobile, Tablet, Desktop)
✅ Real-time Data Visualization
✅ Authentication System
✅ Reusable Components
✅ Tailwind CSS Styling
✅ Mock Data Ready
✅ API Integration Ready
✅ Dark Mode Ready
✅ Accessibility Friendly

---

## 🎓 Learning Resources

Useful for understanding the codebase:
- React Hooks: https://react.dev/reference/react/hooks
- Tailwind CSS: https://tailwindcss.com/docs
- Vite: https://vitejs.dev/guide/
- React Router: https://reactrouter.com/en/main
- Recharts: https://recharts.org/en-US/guide

---

## 🐛 Known Limitations

- Data is mocked (no persistent storage)
- Authentication is simulated (no real validation)
- Charts are static (update with real API)
- No dark theme (ready to implement)
- No offline support (can be added)

---

## 🎯 Future Enhancements

1. **Backend Integration**: Connect real APIs
2. **Authentication**: JWT token management
3. **Export Features**: PDF/CSV reports
4. **Real-time Updates**: WebSocket integration
5. **Dark Theme**: Theme toggle
6. **Mobile App**: React Native version
7. **Analytics**: Usage tracking
8. **Student Portal**: Student-facing dashboard
9. **AI Insights**: ML-based recommendations
10. **Video Integration**: Live class streaming

---

## 📞 Support & Contribution

- **Issues**: Report on GitHub
- **Pull Requests**: Welcome for improvements
- **Documentation**: See README.md & SETUP.md
- **Questions**: Check the docs first

---

**Project Version**: 1.0.0
**Last Updated**: March 2024
**Status**: ✅ Ready for Development
