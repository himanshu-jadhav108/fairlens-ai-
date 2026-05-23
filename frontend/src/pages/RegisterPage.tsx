import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../lib/firebase';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    try {
      await createUserWithEmailAndPassword(auth, email, password);
      navigate('/');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message || 'Failed to register');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 bg-background-surface p-8 rounded-xl card-border">
        <div>
          <div className="flex justify-center">
            <span className="text-5xl">👁️</span>
          </div>
          <h2 className="mt-6 text-center text-3xl font-display font-bold tracking-tight text-foreground">
            Create an account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleRegister}>
          {error && (
            <div className="bg-danger/10 border border-danger/20 text-danger px-4 py-2 rounded text-sm text-center">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email-address" className="sr-only">Email address</label>
              <input 
                id="email-address" 
                name="email" 
                type="email" 
                required 
                className="relative block w-full rounded-md border border-border bg-background-elevated py-2 text-foreground placeholder:text-foreground-muted focus:z-10 focus:ring-1 focus:ring-primary focus:outline-none sm:text-sm px-3 font-mono" 
                placeholder="Email address" 
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input 
                id="password" 
                name="password" 
                type="password" 
                required 
                className="relative block w-full rounded-md border border-border bg-background-elevated py-2 text-foreground placeholder:text-foreground-muted focus:z-10 focus:ring-1 focus:ring-primary focus:outline-none sm:text-sm px-3 font-mono" 
                placeholder="Password" 
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="confirm-password" className="sr-only">Confirm Password</label>
              <input 
                id="confirm-password" 
                name="confirm-password" 
                type="password" 
                required 
                className="relative block w-full rounded-md border border-border bg-background-elevated py-2 text-foreground placeholder:text-foreground-muted focus:z-10 focus:ring-1 focus:ring-primary focus:outline-none sm:text-sm px-3 font-mono" 
                placeholder="Confirm Password" 
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button 
              type="submit" 
              className="group relative flex w-full justify-center rounded-md bg-primary py-2 px-3 text-sm font-display font-bold text-primary-foreground hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background transition-opacity"
            >
              Sign up
            </button>
          </div>
        </form>
        <div className="text-center text-sm font-mono text-foreground-muted">
          <span>Already have an account? </span>
          <Link to="/login" className="font-bold text-primary hover:text-primary/80">Sign in</Link>
        </div>
      </div>
    </div>
  );
}
