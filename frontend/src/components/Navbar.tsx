'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Navbar() {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  return (
    <nav style={{
      background: 'white',
      boxShadow: 'var(--shadow)',
      padding: '1rem 0',
      marginBottom: '2rem',
    }}>
      <div className="container" style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center' 
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <Link href="/dashboard" style={{ 
            fontSize: '1.5rem', 
            fontWeight: 'bold',
            textDecoration: 'none',
            color: 'var(--text-primary)',
          }}>
            ☁️ Cloud Cost Optimizer
          </Link>
          
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <Link href="/dashboard" style={{ textDecoration: 'none', color: 'var(--text-secondary)' }}>
              Dashboard
            </Link>
            <Link href="/dashboard/recommendations" style={{ textDecoration: 'none', color: 'var(--text-secondary)' }}>
              Recommendations
            </Link>
            <Link href="/dashboard/budget" style={{ textDecoration: 'none', color: 'var(--text-secondary)' }}>
              Budget
            </Link>
          </div>
        </div>

        <button onClick={handleLogout} className="btn btn-secondary">
          Logout
        </button>
      </div>
    </nav>
  );
}
