# EduSense AI Frontend - Setup Guide

## Quick Start (5 minutes)

### 1. Prerequisites Check
- ✅ Node.js installed (v14+)
- ✅ npm or yarn available
- ✅ Code editor (VS Code recommended)

### 2. Installation Steps

```bash
# Navigate to frontend directory
cd frontend

# Install all dependencies
npm install

# Start development server
npm run dev
```

The application opens at `http://localhost:3000` automatically.

### 3. Login
- **Email**: `teacher@edusense.ai`
- **Password**: `demo123`

---

## Project Setup Details

### Installation

```bash
# Step 1: Navigate to project
cd EduSense-AI/frontend

# Step 2: Install dependencies
npm install

# This installs:
# - React & React DOM
# - Vite (bundler & dev server)
# - Tailwind CSS
# - Recharts (for charts)
# - React Router (for navigation)
# - Axios (for API calls)
```

### Project Structure

```
frontend/
├── index.html                 # Entry HTML
├── src/
│   ├── App.jsx               # Main app component
│   ├── main.jsx              # React entry point
│   ├── index.css             # Global styles
│   ├── components/           # Reusable components
│   │   ├── common/           # Shared components
│   │   ├── layout/           # Layout components
│   │   └── ProtectedRoute.jsx
│   ├── pages/                # Page components
│   ├── context/              # React context
│   └── data/                 # Mock data
├── package.json              # Dependencies
├── vite.config.js            # Vite config
├── tailwind.config.js        # Tailwind config
└── README.md                 # Documentation
```

---

## Development

### Start Dev Server
```bash
npm run dev
```
- Automatic reload on file changes
- Hot Module Replacement (HMR)
- Opens in default browser
- Port: 3000

### Available Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server |
| `npm run build` | Create production build |
| `npm run preview` | Preview production build |

### Feature Development Workflow

1. **Create new page**:
   ```bash
   # Create in src/pages/MyPage.jsx
   # Import MainLayout
   # Add route in App.jsx
   ```

2. **Create new component**:
   ```bash
   # Create in src/components/
   # Export and import in pages
   ```

3. **Add styles**:
   ```html
   <!-- Use Tailwind CSS classes -->
   <div className="bg-blue-600 p-4 rounded-lg">Content</div>
   ```

---

## Tailwind CSS Guide

### Common Classes Used

```jsx
// Layout
<div className="flex items-center justify-between gap-4">

// Spacing
className="p-4 m-2 mb-8"

// Colors
className="bg-blue-600 text-white border border-gray-300"

// Responsive
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3"

// Effects
className="shadow-card hover:shadow-hover rounded-lg transition-all"
```

### Adding Custom Colors

Edit `tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: '#3b82f6',
      secondary: '#8b5cf6',
    }
  }
}
```

---

## API Integration

### Current Setup
- Using **mock data** from `src/data/mockData.js`
- No backend connection required for development
- Ready to switch to real APIs

### Switching to Real APIs

1. **Install axios** (already included):
```bash
npm install axios
```

2. **Create API service**:
```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE = process.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const getDashboardData = () => api.get('/dashboard');
export const getAttendanceData = () => api.get('/attendance');
export default api;
```

3. **Use in components**:
```javascript
import { getDashboardData } from '../services/api';

useEffect(() => {
  getDashboardData()
    .then(res => setData(res.data))
    .catch(err => console.error(err));
}, []);
```

### Expected API Responses

**GET /api/dashboard**
```json
{
  "summaryCards": {
    "totalStudentsPresent": 28,
    "absentStudents": 2,
    "averageEngagementScore": 72.5,
    "activeParticipationCount": 15
  },
  "engagementTrend": [...],
  "studentParticipation": [...]
}
```

---

## Charts & Data Visualization

### Using Recharts

```jsx
import {
  LineChart,
  BarChart,
  PieChart,
  line,
  ResponsiveContainer,
} from 'recharts';

<ResponsiveContainer width="100%" height={300}>
  <LineChart data={data}>
    <CartesianGrid />
    <XAxis dataKey="time" />
    <YAxis />
    <Tooltip />
    <Line type="monotone" dataKey="score" stroke="#3b82f6" />
  </LineChart>
</ResponsiveContainer>
```

### Available Charts
- Line Charts - Trends over time
- Bar Charts - Comparisons
- Pie Charts - Distributions
- Area Charts - Progressive data
- Custom Heatmaps - Seating analysis

---

## Authentication

### Current Flow
1. User enters email & password
2. App validates (mock authentication)
3. Sets user state in AuthContext
4. Redirects to dashboard
5. ProtectedRoute guards other pages

### Adding Real Authentication

1. **Update LoginPage.jsx**:
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    const res = await axios.post('/api/auth/login', {
      email,
      password,
    });
    localStorage.setItem('token', res.data.token);
    login(email, res.data.user);
    navigate('/dashboard');
  } catch (error) {
    setError(error.response.data.message);
  }
};
```

2. **Store JWT token**:
```javascript
// AuthContext.jsx
useEffect(() => {
  const token = localStorage.getItem('token');
  if (token) {
    // Verify token validity
    setIsLoggedIn(true);
  }
}, []);
```

---

## Customization

### Change Logo/Title
Edit `src/components/layout/Header.jsx` and `Sidebar.jsx`:
```jsx
<h1 className="text-2xl font-bold text-blue-600">EduSense AI</h1>
```

### Add New Menu Items
Edit `src/components/layout/Sidebar.jsx`:
```jsx
const menuItems = [
  { icon: HomeIcon, label: 'Dashboard', path: '/dashboard' },
  // Add new item here
  { icon: YourIcon, label: 'New Page', path: '/new-page' },
];
```

### Modify Colors
Edit `tailwind.config.js`:
```javascript
colors: {
  primary: '#YourColor',
  success: '#YourColor',
  danger: '#YourColor',
}
```

---

## Deployment

### Build for Production
```bash
npm run build
```

Output files in `dist/` folder are production-ready.

### Deploy to Vercel
```bash
npm install -g vercel
vercel
```

### Deploy to Netlify
1. Connect GitHub repository
2. Build command: `npm run build`
3. Publish directory: `dist`

### Deploy to Azure Static Web Apps
```bash
az staticwebapp up --resource-group mygroup --name myapp
```

---

## Troubleshooting

### Issue: Dependencies missing
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Port 3000 in use
**Solution**:
```bash
npm run dev -- --port 3001
```

### Issue: Tailwind CSS not working
**Solution**:
```bash
npm install -D tailwindcss postcss autoprefixer
npm run dev
```

### Issue: Charts not displaying
**Solution**:
```bash
npm install recharts
npm run dev
```

---

## Performance Tips

1. **Lazy load pages**:
```javascript
const Dashboard = lazy(() => import('./pages/DashboardPage'));
```

2. **Optimize images**:
- Use PNG/WebP format
- Compress before adding
- Use SVG for icons

3. **Monitor bundle size**:
```bash
npm run build -- --visualize
```

4. **Enable caching**:
- Configure webpack cache
- Minimize re-renders with memo()

---

## Best Practices

✅ **Do**
- Use Tailwind CSS for styling
- Create reusable components
- Keep components small & focused
- Use React hooks (useState, useEffect)
- Add error handling in API calls

❌ **Don't**
- Use inline styles
- Create large monolithic components
- Skip error handling
- Hard-code values
- Forget responsive design

---

## Community & Support

- **Documentation**: See README.md in project root
- **Issues**: Report on GitHub
- **Contributing**: Create pull requests
- **Questions**: Check FAQ section

---

## Quick Reference

### npm Commands
```bash
npm install           # Install dependencies
npm run dev          # Start dev server
npm run build        # Production build
npm run preview      # Preview build
npm list            # Show dependencies
```

### File Locations
- Pages: `src/pages/`
- Components: `src/components/`
- Data: `src/data/`
- Styles: `src/index.css` + Tailwind
- Config: `tailwind.config.js`

### Useful Links
- [React Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Vite Docs](https://vitejs.dev)
- [Recharts](https://recharts.org)

---

**Last Updated**: March 2024
**Version**: 1.0.0
