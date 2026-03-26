# EduSense AI - Frontend Dashboard

A modern, responsive React.js dashboard for **EduSense AI – IoT Based Classroom Engagement & Attendance Intelligence System**. This dashboard provides real-time classroom insights, attendance monitoring, engagement analytics, and participation tracking.

## 🎯 Features

### 📊 Dashboard
- **Real-time Summary Cards**: Total students present, absent count, average engagement score, active participation
- **Engagement Trend Chart**: Line chart showing engagement metrics over time
- **Participation Analytics**: Bar chart displaying student participation levels
- **Attendance Distribution**: Pie chart showing attendance status breakdown
- **Quick Statistics**: Class duration, attendance rate, response time, distraction events

### 👥 Attendance Monitoring
- **Real-time Attendance Table**: Track student attendance from ESP32-CAM system
- **Face Recognition Status**: Verify face detection results
- **Search & Filter**: Search by name/ID and filter by date
- **Status Badges**: Visual indicators (Present, Absent, Late)
- **Entry Time Tracking**: Real-time entry timestamps

### 📈 Engagement Analytics
- **Engagement Heatmap**: Classroom seating visualization with engagement scores
- **Student Engagement List**: Individual student engagement metrics
- **Attention Percentage Indicator**: Overall classroom attention rate
- **Low Engagement Alerts**: Automatic notifications when engagement drops below 50%
- **Visual Progress Indicators**: Easy-to-read engagement status

### 🎤 Participation Insights
- **Participation Leaderboard**: Ranked list of active participants
- **Participation Trends**: Line chart showing participation over time
- **Recent Activity Feed**: Real-time participation events
- **Participation Types**: Hand raises, verbal responses, questions asked
- **Quality Metrics**: Engagement scores and participation statistics

### 🚨 Alerts & Notifications
- **Real-time Alerts**: Low engagement, inactivity, attendance issues
- **Alert Filtering**: Filter by alert type (Critical, Warning, Success, Info)
- **Alert Summary**: Quick overview of all alert types
- **Action Items**: Responsive actions for critical alerts
- **Dismissible Notifications**: Clean up resolved alerts

### ⚙️ Settings
- **Notification Preferences**: Email and push notification controls
- **Alert Thresholds**: Customizable engagement, attendance, and participation targets
- **Theme Selection**: Light, dark, and auto theme options
- **System Information**: App version and build details

## 🛠️ Tech Stack

- **React.js 18** - UI framework with functional components and hooks
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing
- **Recharts** - Interactive charts and graphs
- **Axios** - HTTP client for API calls (when backend is ready)

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Badge.jsx          # Status and alert badges
│   │   │   ├── Card.jsx           # Reusable card components
│   │   │   └── Icons.jsx          # SVG icon library
│   │   ├── layout/
│   │   │   ├── Header.jsx         # Top navigation bar
│   │   │   ├── Sidebar.jsx        # Side navigation menu
│   │   │   └── MainLayout.jsx     # Main layout wrapper
│   │   └── ProtectedRoute.jsx     # Authentication guard
│   ├── pages/
│   │   ├── LoginPage.jsx          # Login interface
│   │   ├── DashboardPage.jsx      # Main dashboard
│   │   ├── AttendancePage.jsx     # Attendance monitoring
│   │   ├── EngagementPage.jsx     # Engagement analytics
│   │   ├── ParticipationPage.jsx  # Participation insights
│   │   ├── AlertsPage.jsx         # Alerts management
│   │   ├── SettingsPage.jsx       # User settings
│   │   └── NotFoundPage.jsx       # 404 page
│   ├── context/
│   │   └── AuthContext.jsx        # Authentication state
│   ├── data/
│   │   └── mockData.js            # Mock API responses
│   ├── App.jsx                    # Main app component
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Global styles
├── index.html                     # HTML template
├── package.json                   # Dependencies
├── tailwind.config.js             # Tailwind configuration
├── postcss.config.js              # PostCSS configuration
├── vite.config.js                 # Vite configuration
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. **Navigate to the frontend directory**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

### Development Server

Start the development server:
```bash
npm run dev
```

The application will open automatically at `http://localhost:3000`

### Build for Production

Create optimized production build:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## 📖 Demo Credentials

Use these credentials to test the application:
- **Email**: `teacher@edusense.ai`
- **Password**: `demo123`

## 🔌 API Integration

The dashboard currently uses **mock data** stored in `src/data/mockData.js`. To connect to real backend APIs:

1. **Open `src/data/mockData.js`** and replace with actual API calls
2. **Use Axios** for HTTP requests (already installed):

```javascript
import axios from 'axios';

const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/api/dashboard');
    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};
```

3. **Expected API Endpoints**:
   - `GET /api/dashboard` - Dashboard metrics
   - `GET /api/attendance` - Attendance records
   - `GET /api/engagement` - Engagement data
   - `GET /api/participation` - Participation data
   - `GET /api/alerts` - Alert list
   - `POST /api/auth/login` - User authentication

## 🎨 Customization

### Colors & Theming
Edit `tailwind.config.js` to customize:
- Primary color scheme
- Button styles
- Shadow effects
- Spacing values

### Adding New Pages
1. Create a new file in `src/pages/`
2. Import `MainLayout` component
3. Add route in `src/App.jsx`
4. Add menu item in `src/components/layout/Sidebar.jsx`

### Component Reusability
- **Card Component**: Display summary metrics
- **Badge Component**: Status indicators
- **Icons Component**: SVG icon library
- **ChartCard Component**: Chart containers

## 📊 Charts & Visualizations

The dashboard uses **Recharts** for data visualization:
- Line Charts (Engagement trends, participation)
- Bar Charts (Student participation levels)
- Pie Charts (Attendance distribution)
- Progress Bars (Engagement indicators)
- Heatmaps (Classroom engagement visualization)

## 🔐 Authentication

The app includes a basic authentication context. Replace the mock login with real API:

```javascript
const login = async (email, password) => {
  const response = await axios.post('/api/auth/login', { email, password });
  setToken(response.data.token);
  setUser(response.data.user);
};
```

## 🌐 Responsive Design

The dashboard is fully responsive:
- **Mobile**: Stack layout with mobile-optimized sidebar
- **Tablet**: Adjusted grid layouts
- **Desktop**: Full sidebar + expanded content area

## 📱 Mobile Optimization

- Hamburger menu on small screens
- Touch-friendly button sizes
- Mobile-first CSS approach
- Responsive grid layouts

## 🐛 Troubleshooting

### Port 3000 already in use
```bash
npm run dev -- --port 3001
```

### Dependencies not installing
```bash
rm -rf node_modules package-lock.json
npm install
```

### Tailwind CSS not applied
```bash
npm install -D tailwindcss postcss autoprefixer
npm run dev
```

## 📦 Building & Deployment

### Build Output
The `npm run build` command generates optimized files in the `dist/` folder.

### Deploy to Services
- **Vercel**: Connect GitHub repository
- **Netlify**: Drag & drop `dist/` folder
- **Azure Static Web Apps**: Connect to repository
- **AWS S3 + CloudFront**: Upload `dist/` contents

## 🤝 Contributing

1. Create feature branches from `main`
2. Follow component structure conventions
3. Use Tailwind CSS for styling
4. Keep components reusable and well-documented

## 📝 Notes

- All data is currently **mocked** and resets on page refresh
- Backend APIs are not yet implemented (awaiting backend team)
- Authentication is simulated (no actual server validation)
- Build process is optimized for production (CSS purging, minification)

## 🔄 Next Steps

1. **Connect Backend APIs**: Replace mock data with real API calls
2. **Add Chart Animations**: Enhance Recharts with animations
3. **Implement Real Authentication**: Add JWT token management
4. **Add Export Features**: PDF/CSV export for reports
5. **Dark Theme**: Implement dark mode toggle
6. **Mobile App**: Convert to React Native for iOS/Android

## 📄 License

&copy; 2024 EduSense AI. All rights reserved.

## 📞 Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/zoro1324/EduSense-AI)
- Review the documentation
- Contact the development team

---

**Happy Coding! 🚀**
