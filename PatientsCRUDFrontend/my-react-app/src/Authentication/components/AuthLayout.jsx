// Authentication/components/AuthLayout.jsx
export const AuthLayout = ({ children }) => (
  <div className="min-h-screen bg-white flex items-center justify-center p-4 relative overflow-hidden font-sans">
    <div className="absolute top-[-10%] left-[-10%] w-[40vw] h-[40vw] bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
    <div className="absolute top-[20%] right-[-10%] w-[35vw] h-[35vw] bg-indigo-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
    <div className="absolute bottom-[-20%] left-[20%] w-[45vw] h-[45vw] bg-blue-50 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>

    <div className="w-full max-w-md bg-white/80 backdrop-blur-xl rounded-3xl shadow-[0_20px_50px_rgba(0,0,255,0.05)] border border-blue-50 p-8 relative z-10 transition-all duration-300 hover:shadow-[0_20px_60px_rgba(0,0,255,0.1)]">
      {children}
    </div>
  </div>
);
